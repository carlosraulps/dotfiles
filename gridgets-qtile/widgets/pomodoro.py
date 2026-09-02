import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

WORK_TIME = 25 * 60
BREAK_TIME = 5 * 60

class PomodoroWidget(Gtk.Box):
    def __init__(self, config):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.config = config
        self.get_style_context().add_class('gridget-card')
        self.get_style_context().add_class('gridget-pomodoro')

        self.time_left = WORK_TIME
        self.is_running = False
        self.is_break = False
        self.timer_id = None

        # Title
        self.title_lbl = Gtk.Label()
        self.title_lbl.set_halign(Gtk.Align.START)
        self.title_lbl.get_style_context().add_class('widget-title')
        self.title_lbl.set_markup("<b>🍅 Focus Session</b>")
        self.pack_start(self.title_lbl, False, False, 0)

        # Timer Display
        inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        inner.set_valign(Gtk.Align.CENTER)
        inner.set_halign(Gtk.Align.CENTER)

        self.timer_lbl = Gtk.Label()
        self.timer_lbl.get_style_context().add_class('pomodoro-timer')
        self.update_timer_label()
        inner.pack_start(self.timer_lbl, True, True, 0)

        self.pack_start(inner, True, True, 0)

        # Controls Row
        ctrl_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        ctrl_row.set_halign(Gtk.Align.CENTER)

        self.toggle_btn = Gtk.Button(label="Start")
        self.toggle_btn.get_style_context().add_class('pomodoro-btn')
        self.toggle_btn.connect('clicked', self.on_toggle)

        self.reset_btn = Gtk.Button(label="Reset")
        self.reset_btn.get_style_context().add_class('pomodoro-btn')
        self.reset_btn.connect('clicked', self.on_reset)

        ctrl_row.pack_start(self.toggle_btn, False, False, 0)
        ctrl_row.pack_start(self.reset_btn, False, False, 0)
        self.pack_start(ctrl_row, False, False, 0)

    def update_timer_label(self):
        mins = self.time_left // 60
        secs = self.time_left % 60
        self.timer_lbl.set_markup(f"<span font_weight='bold'>{mins:02d}:{secs:02d}</span>")

    def on_toggle(self, _):
        if self.is_running:
            self.is_running = False
            self.toggle_btn.set_label("Start")
            if self.timer_id:
                GLib.source_remove(self.timer_id)
                self.timer_id = None
        else:
            self.is_running = True
            self.toggle_btn.set_label("Pause")
            self.timer_id = GLib.timeout_add_seconds(1, self.tick)

    def on_reset(self, _):
        if self.timer_id:
            GLib.source_remove(self.timer_id)
            self.timer_id = None
        self.is_running = False
        self.is_break = False
        self.time_left = WORK_TIME
        self.toggle_btn.set_label("Start")
        self.title_lbl.set_markup("<b>🍅 Focus Session</b>")
        self.update_timer_label()

    def tick(self):
        if not self.is_running:
            return False

        if self.time_left > 0:
            self.time_left -= 1
            self.update_timer_label()
            return True
        else:
            # Switch mode
            self.is_break = not self.is_break
            if self.is_break:
                self.time_left = BREAK_TIME
                self.title_lbl.set_markup("<b>☕ Short Break</b>")
            else:
                self.time_left = WORK_TIME
                self.title_lbl.set_markup("<b>🍅 Focus Session</b>")
            self.update_timer_label()
            return True
