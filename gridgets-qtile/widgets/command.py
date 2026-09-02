import subprocess
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class CommandWidget(Gtk.Box):
    def __init__(self, config):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.config = config
        self.cmd = config.get('command', 'echo "Hello"')
        self.label = config.get('label', 'Quick Action')

        self.get_style_context().add_class('gridget-card')
        self.get_style_context().add_class('gridget-command')

        btn = Gtk.Button()
        btn.get_style_context().add_class('command-btn')
        btn_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        btn_box.set_valign(Gtk.Align.CENTER)
        btn_box.set_halign(Gtk.Align.CENTER)

        icon_lbl = Gtk.Label()
        icon_lbl.set_markup("<span font_size='22000'>⚡</span>")
        text_lbl = Gtk.Label()
        text_lbl.set_markup(f"<b>{self.label}</b>")

        btn_box.pack_start(icon_lbl, False, False, 0)
        btn_box.pack_start(text_lbl, False, False, 0)
        btn.add(btn_box)

        btn.connect('clicked', self.on_execute)
        self.pack_start(btn, True, True, 0)

    def on_execute(self, _):
        try:
            subprocess.Popen(self.cmd, shell=True)
        except Exception as e:
            print(f"[CommandWidget] Exec failed: {e}")
