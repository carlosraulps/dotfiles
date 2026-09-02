import os
import urllib.parse
from gi.repository import Gio, GLib

class MprisEngine:
    def __init__(self):
        self.bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self.cached_info = {
            'player_name': '',
            'title': 'No Media Playing',
            'artist': 'Idle',
            'album': '',
            'status': 'Stopped',
            'art_url': '',
            'is_playing': False,
        }

    def get_active_player_bus_name(self):
        """
        Scans all MPRIS media players and prioritizes any player that is
        actively PLAYING (e.g. Brave YouTube, Spotify, MPV, VLC) over idle or paused ones.
        """
        try:
            proxy = Gio.DBusProxy.new_sync(
                self.bus,
                Gio.DBusProxyFlags.NONE,
                None,
                "org.freedesktop.DBus",
                "/org/freedesktop/DBus",
                "org.freedesktop.DBus",
                None
            )
            result = proxy.call_sync("ListNames", None, Gio.DBusCallFlags.NONE, -1, None)
            names = result.unpack()[0]
            mpris_players = [n for n in names if n.startswith("org.mpris.MediaPlayer2.")]
            if not mpris_players:
                return None

            playing_players = []
            paused_players = []

            for p in mpris_players:
                try:
                    props_proxy = Gio.DBusProxy.new_sync(
                        self.bus,
                        Gio.DBusProxyFlags.NONE,
                        None,
                        p,
                        "/org/mpris/MediaPlayer2",
                        "org.freedesktop.DBus.Properties",
                        None
                    )
                    status_var = props_proxy.call_sync(
                        "Get",
                        GLib.Variant("(ss)", ("org.mpris.MediaPlayer2.Player", "PlaybackStatus")),
                        Gio.DBusCallFlags.NONE, 200, None
                    )
                    status = status_var.unpack()[0] if status_var else "Stopped"
                    if status == "Playing":
                        playing_players.append(p)
                    elif status == "Paused":
                        paused_players.append(p)
                except Exception:
                    pass

            # 1. Prioritize ANY player actively PLAYING (Spotatui top priority)
            if playing_players:
                for p in playing_players:
                    if 'spotatui' in p.lower():
                        return p
                for p in playing_players:
                    if 'spotify' in p.lower():
                        return p
                for p in playing_players:
                    p_lower = p.lower()
                    if 'brave' in p_lower or 'chrome' in p_lower or 'firefox' in p_lower:
                        return p
                return playing_players[0]

            # 2. If nothing is actively playing, return paused spotatui / spotify first
            if paused_players:
                for p in paused_players:
                    if 'spotatui' in p.lower():
                        return p
                for p in paused_players:
                    if 'spotify' in p.lower():
                        return p
                for p in paused_players:
                    p_lower = p.lower()
                    if 'brave' in p_lower or 'chrome' in p_lower:
                        return p
                return paused_players[0]

            # 3. Fallback: check if spotatui is registered
            for p in mpris_players:
                if 'spotatui' in p.lower():
                    return p
            return mpris_players[0]
        except Exception:
            pass
        return None

    def poll(self):
        bus_name = self.get_active_player_bus_name()
        if not bus_name:
            self.cached_info = {
                'player_name': '',
                'title': 'No Media Playing',
                'artist': 'Idle',
                'album': '',
                'status': 'Stopped',
                'art_url': '',
                'is_playing': False,
            }
            return self.cached_info

        try:
            props_proxy = Gio.DBusProxy.new_sync(
                self.bus,
                Gio.DBusProxyFlags.NONE,
                None,
                bus_name,
                "/org/mpris/MediaPlayer2",
                "org.freedesktop.DBus.Properties",
                None
            )

            status_var = props_proxy.call_sync(
                "Get",
                GLib.Variant("(ss)", ("org.mpris.MediaPlayer2.Player", "PlaybackStatus")),
                Gio.DBusCallFlags.NONE, 250, None
            )
            status = status_var.unpack()[0] if status_var else "Stopped"

            meta_var = props_proxy.call_sync(
                "Get",
                GLib.Variant("(ss)", ("org.mpris.MediaPlayer2.Player", "Metadata")),
                Gio.DBusCallFlags.NONE, 250, None
            )
            metadata = meta_var.unpack()[0] if meta_var else {}

            title = metadata.get('xesam:title', 'Unknown Track')
            if isinstance(title, GLib.Variant):
                title = title.unpack()

            artists = metadata.get('xesam:artist', ['Unknown Artist'])
            if isinstance(artists, GLib.Variant):
                artists = artists.unpack()
            artist = ", ".join(artists) if isinstance(artists, list) else str(artists)

            album = metadata.get('xesam:album', '')
            if isinstance(album, GLib.Variant):
                album = album.unpack()

            art_url = metadata.get('mpris:artUrl', '')
            if isinstance(art_url, GLib.Variant):
                art_url = art_url.unpack()

            raw_name = bus_name.replace('org.mpris.MediaPlayer2.', '')
            name_lower = raw_name.lower()
            if 'brave' in name_lower or 'chromium' in name_lower:
                player_name = "Brave (YouTube)"
            elif 'spotify' in name_lower:
                player_name = "Spotify"
            elif 'spotatui' in name_lower:
                player_name = "Spotify"
            elif 'firefox' in name_lower:
                player_name = "Firefox"
            elif 'mpv' in name_lower:
                player_name = "MPV"
            elif 'vlc' in name_lower:
                player_name = "VLC"
            else:
                player_name = raw_name.split('.')[0].capitalize()

            self.cached_info = {
                'bus_name': bus_name,
                'player_name': player_name,
                'title': str(title) if title else 'No Media Playing',
                'artist': str(artist) if artist else 'Idle',
                'album': str(album),
                'status': str(status),
                'art_url': str(art_url),
                'is_playing': (status == 'Playing'),
            }
        except Exception:
            pass

        return self.cached_info

    def play_pause(self):
        bus_name = self.get_active_player_bus_name()
        if not bus_name:
            return
        try:
            player_proxy = Gio.DBusProxy.new_sync(
                self.bus,
                Gio.DBusProxyFlags.NONE,
                None,
                bus_name,
                "/org/mpris/MediaPlayer2",
                "org.mpris.MediaPlayer2.Player",
                None
            )
            player_proxy.call_sync("PlayPause", None, Gio.DBusCallFlags.NONE, -1, None)
        except Exception:
            pass

    def next(self):
        bus_name = self.get_active_player_bus_name()
        if not bus_name:
            return
        try:
            player_proxy = Gio.DBusProxy.new_sync(
                self.bus,
                Gio.DBusProxyFlags.NONE,
                None,
                bus_name,
                "/org/mpris/MediaPlayer2",
                "org.mpris.MediaPlayer2.Player",
                None
            )
            player_proxy.call_sync("Next", None, Gio.DBusCallFlags.NONE, -1, None)
        except Exception:
            pass

    def previous(self):
        bus_name = self.get_active_player_bus_name()
        if not bus_name:
            return
        try:
            player_proxy = Gio.DBusProxy.new_sync(
                self.bus,
                Gio.DBusProxyFlags.NONE,
                None,
                bus_name,
                "/org/mpris/MediaPlayer2",
                "org.mpris.MediaPlayer2.Player",
                None
            )
            player_proxy.call_sync("Previous", None, Gio.DBusCallFlags.NONE, -1, None)
        except Exception:
            pass

mpris_engine = MprisEngine()
