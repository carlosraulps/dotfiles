import os
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, GdkPixbuf, GLib
from engine.weather import weather_engine


class WeatherLocationRow(Gtk.Box):
    """A card row displaying weather, temperature, condition, and local time for a single city."""

    def __init__(self, city_id, default_name, default_region, accent_color="#88c0d0"):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.city_id = city_id
        self.accent_color = accent_color
        self.get_style_context().add_class('weather-loc-card')

        # Top line: [📍 City (Region)] ---------------- [16:45]
        top_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.title_lbl = Gtk.Label()
        self.title_lbl.set_halign(Gtk.Align.START)
        self.title_lbl.get_style_context().add_class('weather-loc-title')
        self.title_lbl.set_markup(f"<span color='{accent_color}'>●</span> <b>{default_name}</b> <span alpha='65%'>({default_region})</span>")
        top_box.pack_start(self.title_lbl, True, True, 0)

        self.time_lbl = Gtk.Label()
        self.time_lbl.set_halign(Gtk.Align.END)
        self.time_lbl.get_style_context().add_class('weather-loc-time')
        self.time_lbl.set_markup("<span alpha='60%'>--:--</span>")
        top_box.pack_end(self.time_lbl, False, False, 0)
        self.pack_start(top_box, False, False, 0)

        # Main Info Row: [Icon + Temp] ------------- [Condition + High/Low]
        info_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        info_row.set_valign(Gtk.Align.CENTER)

        # Left cluster: Weather Icon + Big Temp
        left_cluster = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.icon_img = Gtk.Image()
        left_cluster.pack_start(self.icon_img, False, False, 0)

        self.temp_lbl = Gtk.Label()
        self.temp_lbl.set_halign(Gtk.Align.START)
        self.temp_lbl.get_style_context().add_class('weather-loc-temp')
        self.temp_lbl.set_text("--°")
        left_cluster.pack_start(self.temp_lbl, False, False, 0)
        info_row.pack_start(left_cluster, False, False, 0)

        # Right cluster: Condition + H/L
        right_cluster = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        right_cluster.set_valign(Gtk.Align.CENTER)

        self.cond_lbl = Gtk.Label()
        self.cond_lbl.set_halign(Gtk.Align.END)
        self.cond_lbl.set_ellipsize(3)
        self.cond_lbl.get_style_context().add_class('weather-loc-cond')
        self.cond_lbl.set_text("Loading...")

        self.hl_lbl = Gtk.Label()
        self.hl_lbl.set_halign(Gtk.Align.END)
        self.hl_lbl.get_style_context().add_class('weather-loc-hl')
        self.hl_lbl.set_text("H:-- L:--")

        right_cluster.pack_start(self.cond_lbl, False, False, 0)
        right_cluster.pack_start(self.hl_lbl, False, False, 0)
        info_row.pack_end(right_cluster, True, True, 0)

        self.pack_start(info_row, True, True, 0)

    def update(self, data):
        """Updates row with weather data."""
        if not data:
            return

        city_name = data.get('city', 'City')
        region = data.get('region', '')
        time_str = data.get('time', '--:--')
        temp_str = data.get('temperature', '--°')
        cond_str = data.get('condition', 'Unknown')
        high_str = data.get('high', '--°')
        low_str = data.get('low', '--°')
        icon_path = data.get('icon_path')

        self.title_lbl.set_markup(
            f"<span color='{self.accent_color}'>●</span> <b>{city_name}</b> <span alpha='65%'>({region})</span>"
        )
        self.time_lbl.set_markup(f"<span alpha='65%'>🕒 {time_str}</span>")
        self.temp_lbl.set_text(temp_str)
        self.cond_lbl.set_text(cond_str)
        self.hl_lbl.set_markup(f"<span alpha='75%'>H:{high_str}  L:{low_str}</span>")

        if icon_path and os.path.exists(icon_path):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_path, 28, 28, True)
                self.icon_img.set_from_pixbuf(pixbuf)
            except Exception:
                pass


class WeatherWidget(Gtk.EventBox):
    """
    Dual-City Weather Widget for Gridgets Desktop.
    Displays live real-time conditions for both:
    1. Santo André (ABC Paulista / São Paulo) - Carbono Cluster home
    2. Lima, Peru - Iskay / Bastião Cluster home
    """

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.use_fahrenheit = config.get('use_fahrenheit', False)

        # Container
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.box.get_style_context().add_class('gridget-card')
        self.box.get_style_context().add_class('gridget-weather')
        self.add(self.box)

        # 1. Header: [🌤 Weather Overview] ----------- [↻ Refresh]
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.header_title = Gtk.Label()
        self.header_title.set_halign(Gtk.Align.START)
        self.header_title.get_style_context().add_class('widget-title')
        self.header_title.set_markup("<b>🌤 Weather Overview</b>")
        header_box.pack_start(self.header_title, True, True, 0)

        self.status_icon = Gtk.Label()
        self.status_icon.set_halign(Gtk.Align.END)
        self.status_icon.get_style_context().add_class('stat-subtext')
        self.status_icon.set_markup("<span alpha='50%'>↻</span>")
        header_box.pack_end(self.status_icon, False, False, 0)
        self.box.pack_start(header_box, False, False, 0)

        # 2. Location Row 1: Santo André (SP)
        self.row_sp = WeatherLocationRow(
            city_id="santo_andre",
            default_name="Santo André",
            default_region="SP",
            accent_color="#88c0d0"
        )
        self.box.pack_start(self.row_sp, True, True, 1)

        # 3. Location Row 2: Lima (Peru)
        self.row_lima = WeatherLocationRow(
            city_id="lima",
            default_name="Lima",
            default_region="Peru",
            accent_color="#b48ead"
        )
        self.box.pack_start(self.row_lima, True, True, 1)

        # Click event to refresh on demand
        self.set_above_child(True)
        self.connect('button-press-event', self.on_card_clicked)

        weather_engine.add_listener(self.on_weather_update)
        self.refresh_weather()

        # Refresh every 2 seconds as requested
        GLib.timeout_add_seconds(2, self.refresh_weather)

    def on_card_clicked(self, widget, event):
        if event.button == 1:  # Left click
            self.status_icon.set_markup("<span alpha='90%'>↻</span>")
            self.row_sp.cond_lbl.set_text("Refreshing...")
            self.row_lima.cond_lbl.set_text("Refreshing...")
            weather_engine.fetch_async(use_fahrenheit=self.use_fahrenheit, on_complete=self.on_fetch_complete, force=True)
            return True
        return False

    def refresh_weather(self):
        weather_engine.fetch_async(use_fahrenheit=self.use_fahrenheit, on_complete=self.on_fetch_complete)
        return True

    def on_fetch_complete(self):
        self.status_icon.set_markup("<span alpha='50%'>↻</span>")
        return False

    def on_weather_update(self, data):
        if not data:
            return

        locations = data.get('locations', [])
        for loc in locations:
            cid = loc.get('id')
            if cid == 'santo_andre':
                self.row_sp.update(loc)
            elif cid == 'lima':
                self.row_lima.update(loc)
