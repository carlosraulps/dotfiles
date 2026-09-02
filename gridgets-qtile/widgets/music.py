import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from engine.mpris import mpris_engine

WAVE_FRAMES = [
    " ▃▅▇▆▅▃ ",
    "▂▅▇█▇▅▃ ",
    "▃▆█▇▅▃▂ ",
    "▅▇▆▅▃▂ ▂",
    "▇▆▅▃▂ ▂▃",
    "▆▅▃▂ ▂▃▅",
    "▅▃▂ ▂▃▅▆",
    "▃▂ ▂▃▅▆▇",
    "▂ ▂▃▅▆▇█",
    " ▂▃▅▆▇▆▅",
]

class MusicWidget(Gtk.Box):
    def __init__(self, config):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.config = config
        self.get_style_context().add_class('gridget-card')
        self.get_style_context().add_class('gridget-music')

        self.wave_index = 0
        self.is_playing = False

        # Header Row: [󰝚 Player Name] -------- [Animated Wave ▃▅▇▅▃]
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header_box.set_hexpand(True)

        self.player_lbl = Gtk.Label()
        self.player_lbl.set_halign(Gtk.Align.START)
        self.player_lbl.set_hexpand(True)
        self.player_lbl.get_style_context().add_class('widget-title')
        self.player_lbl.set_markup("<b>󰝚 Media Player</b>")
        header_box.pack_start(self.player_lbl, True, True, 0)

        self.wave_lbl = Gtk.Label()
        self.wave_lbl.set_halign(Gtk.Align.END)
        self.wave_lbl.get_style_context().add_class('music-wave')
        self.wave_lbl.set_markup("<span color='#5c6370'>  ▂ ▂  </span>")
        header_box.pack_end(self.wave_lbl, False, False, 0)

        self.pack_start(header_box, False, False, 0)

        # Track Info (Title & Artist)
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        info_box.set_valign(Gtk.Align.CENTER)

        self.title_lbl = Gtk.Label()
        self.title_lbl.set_halign(Gtk.Align.START)
        self.title_lbl.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
        self.title_lbl.get_style_context().add_class('music-title')
        self.title_lbl.set_markup("<b>No Media Playing</b>")

        self.artist_lbl = Gtk.Label()
        self.artist_lbl.set_halign(Gtk.Align.START)
        self.artist_lbl.set_ellipsize(3)
        self.artist_lbl.get_style_context().add_class('music-artist')
        self.artist_lbl.set_markup("<span alpha='75%'>Idle</span>")

        info_box.pack_start(self.title_lbl, False, False, 0)
        info_box.pack_start(self.artist_lbl, False, False, 0)
        self.pack_start(info_box, True, True, 0)

        # Controls Row
        ctrl_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        ctrl_row.set_halign(Gtk.Align.CENTER)

        self.prev_btn = Gtk.Button(label="⏮")
        self.prev_btn.get_style_context().add_class('media-btn')
        self.prev_btn.set_tooltip_text("Previous Track")
        self.prev_btn.connect('clicked', lambda _: mpris_engine.previous())

        self.play_btn = Gtk.Button(label="▶")
        self.play_btn.get_style_context().add_class('media-btn')
        self.play_btn.get_style_context().add_class('media-btn-primary')
        self.play_btn.set_tooltip_text("Play / Pause")
        self.play_btn.connect('clicked', lambda _: mpris_engine.play_pause())

        self.next_btn = Gtk.Button(label="⏭")
        self.next_btn.get_style_context().add_class('media-btn')
        self.next_btn.set_tooltip_text("Next Track")
        self.next_btn.connect('clicked', lambda _: mpris_engine.next())

        ctrl_row.pack_start(self.prev_btn, False, False, 0)
        ctrl_row.pack_start(self.play_btn, False, False, 0)
        ctrl_row.pack_start(self.next_btn, False, False, 0)
        self.pack_start(ctrl_row, False, False, 0)

        # Periodic Polling & Wave Animation
        self.update_media()
        GLib.timeout_add(1000, self.update_media)
        GLib.timeout_add(140, self.animate_wave)

    def animate_wave(self):
        if self.is_playing:
            self.wave_index = (self.wave_index + 1) % len(WAVE_FRAMES)
            wave_text = WAVE_FRAMES[self.wave_index]
            self.wave_lbl.set_markup(f"<span color='#61afef' font_weight='bold'>{wave_text}</span>")
        else:
            self.wave_lbl.set_markup("<span color='#5c6370'>  ▂ ▂  </span>")
        return True

    def update_media(self):
        info = mpris_engine.poll()
        player_name = info.get('player_name', '')
        self.is_playing = info.get('is_playing', False)

        icon = "󰓇 " if "spotify" in player_name.lower() else (" " if "youtube" in player_name.lower() or "brave" in player_name.lower() else "󰝚 ")
        if player_name:
            self.player_lbl.set_markup(f"<b>{icon}{GLib.markup_escape_text(player_name)}</b>")
        else:
            self.player_lbl.set_markup("<b>󰝚 Media Player</b>")

        title = info.get('title', 'No Media Playing')
        artist = info.get('artist', 'Idle')

        self.title_lbl.set_markup(f"<b>{GLib.markup_escape_text(title)}</b>")
        self.artist_lbl.set_markup(f"<span alpha='75%'>{GLib.markup_escape_text(artist)}</span>")

        if self.is_playing:
            self.play_btn.set_label("⏸")
            self.play_btn.get_style_context().add_class('media-playing')
        else:
            self.play_btn.set_label("▶")
            self.play_btn.get_style_context().remove_class('media-playing')

        return True
