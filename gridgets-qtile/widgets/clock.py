import datetime
from zoneinfo import ZoneInfo
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

class ClockWidget(Gtk.Box):
    def __init__(self, config):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.config = config
        self.use_24h = config.get('use_24h', True)
        self.tz_name = config.get('timezone', 'America/Sao_Paulo')
        try:
            self.tz = ZoneInfo(self.tz_name)
        except Exception:
            self.tz = None

        self.get_style_context().add_class('gridget-card')
        self.get_style_context().add_class('gridget-clock')

        # Inner container for center alignment
        inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        inner.set_valign(Gtk.Align.CENTER)
        inner.set_halign(Gtk.Align.CENTER)

        # Time Label
        self.time_label = Gtk.Label()
        self.time_label.get_style_context().add_class('clock-time')

        # Date Label
        self.date_label = Gtk.Label()
        self.date_label.get_style_context().add_class('clock-date')

        inner.pack_start(self.time_label, True, True, 0)
        inner.pack_start(self.date_label, False, False, 0)
        self.pack_start(inner, True, True, 0)

        self.update_time()
        GLib.timeout_add_seconds(1, self.update_time)

    def update_time(self):
        now = datetime.datetime.now(self.tz) if self.tz else datetime.datetime.now()
        if self.use_24h:
            time_str = now.strftime('%H:%M')
        else:
            time_str = now.strftime('%I:%M %p')
        date_str = now.strftime('%A, %b %d')

        self.time_label.set_markup(f"<span font_weight='bold'>{time_str}</span>")
        self.date_label.set_markup(f"<span alpha='75%'>{date_str}</span>")
        return True
