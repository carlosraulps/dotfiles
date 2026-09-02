import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib
from engine.weather import weather_engine

class WeatherWidget(Gtk.EventBox):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.city = config.get('city', 'São Paulo')
        self.use_fahrenheit = config.get('use_fahrenheit', False)

        # Main Box inside EventBox
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.box.get_style_context().add_class('gridget-card')
        self.box.get_style_context().add_class('gridget-weather')
        self.add(self.box)

        # Header: City + Refresh Hint
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.city_label = Gtk.Label()
        self.city_label.set_halign(Gtk.Align.START)
        self.city_label.get_style_context().add_class('weather-city')
        self.city_label.set_markup(f"<b>{GLib.markup_escape_text(self.city)}</b>")
        header_box.pack_start(self.city_label, True, True, 0)

        self.status_icon = Gtk.Label()
        self.status_icon.set_halign(Gtk.Align.END)
        self.status_icon.get_style_context().add_class('stat-subtext')
        self.status_icon.set_markup("<span alpha='50%'>↻</span>")
        header_box.pack_end(self.status_icon, False, False, 0)
        self.box.pack_start(header_box, False, False, 0)

        # Main Row: Icon + Temp
        main_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        main_row.set_valign(Gtk.Align.CENTER)

        self.icon_image = Gtk.Image()
        self.temp_label = Gtk.Label()
        self.temp_label.get_style_context().add_class('weather-temp')
        self.temp_label.set_text("--°")

        main_row.pack_start(self.icon_image, False, False, 0)
        main_row.pack_start(self.temp_label, False, False, 0)
        self.box.pack_start(main_row, True, True, 0)

        # Bottom Row: Condition + High/Low
        bottom_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.cond_label = Gtk.Label()
        self.cond_label.set_halign(Gtk.Align.START)
        self.cond_label.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
        self.cond_label.get_style_context().add_class('weather-condition')
        self.cond_label.set_text("Loading...")

        self.highlow_label = Gtk.Label()
        self.highlow_label.set_halign(Gtk.Align.END)
        self.highlow_label.get_style_context().add_class('weather-highlow')
        self.highlow_label.set_text("H:-- L:--")

        bottom_row.pack_start(self.cond_label, True, True, 0)
        bottom_row.pack_end(self.highlow_label, False, False, 0)
        self.box.pack_start(bottom_row, False, False, 0)

        # Click event to refresh on demand
        self.set_above_child(True)
        self.connect('button-press-event', self.on_card_clicked)

        weather_engine.add_listener(self.on_weather_update)
        self.refresh_weather()

        # Refresh every 30 minutes
        GLib.timeout_add_seconds(1800, self.refresh_weather)

    def on_card_clicked(self, widget, event):
        if event.button == 1:  # Left click
            self.cond_label.set_text("Refreshing...")
            self.status_icon.set_markup("<span alpha='90%'>↻</span>")
            self.refresh_weather()
            return True
        return False

    def refresh_weather(self):
        weather_engine.fetch_async(self.city, self.use_fahrenheit, on_complete=self.on_fetch_complete)
        return True

    def on_fetch_complete(self):
        self.status_icon.set_markup("<span alpha='50%'>↻</span>")
        return False

    def on_weather_update(self, data):
        if not data:
            return

        city_name = data.get('city', self.city)
        temp_str = data.get('temperature', '--°')
        cond_str = data.get('condition', '')
        high_str = data.get('high', '--°')
        low_str = data.get('low', '--°')

        self.city_label.set_markup(f"<b>{GLib.markup_escape_text(city_name)}</b>")
        self.temp_label.set_text(temp_str)
        self.cond_label.set_text(cond_str)
        self.highlow_label.set_markup(f"<span alpha='75%'>H:{high_str} L:{low_str}</span>")

        icon_path = data.get('icon_path')
        if icon_path and os.path.exists(icon_path):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_path, 36, 36, True)
                self.icon_image.set_from_pixbuf(pixbuf)
            except Exception:
                pass

