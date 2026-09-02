import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from engine.system import system_engine

class SystemWidget(Gtk.Box):
    def __init__(self, config):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.config = config
        self.get_style_context().add_class('gridget-card')
        self.get_style_context().add_class('gridget-system')

        # Title
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        title_lbl = Gtk.Label()
        title_lbl.set_halign(Gtk.Align.START)
        title_lbl.get_style_context().add_class('widget-title')
        title_lbl.set_markup("<b>System Monitor</b>")
        title_box.pack_start(title_lbl, True, True, 0)
        self.pack_start(title_box, False, False, 0)

        # CPU Row
        cpu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        cpu_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        cpu_title = Gtk.Label(label="CPU")
        cpu_title.set_halign(Gtk.Align.START)
        self.cpu_val_lbl = Gtk.Label(label="0%")
        self.cpu_val_lbl.set_halign(Gtk.Align.END)
        cpu_header.pack_start(cpu_title, True, True, 0)
        cpu_header.pack_end(self.cpu_val_lbl, False, False, 0)

        self.cpu_bar = Gtk.ProgressBar()
        self.cpu_bar.set_fraction(0.0)
        self.cpu_bar.get_style_context().add_class('meter-cpu')

        cpu_box.pack_start(cpu_header, False, False, 0)
        cpu_box.pack_start(self.cpu_bar, False, False, 0)
        self.pack_start(cpu_box, False, False, 0)

        # RAM Row
        ram_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        ram_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        ram_title = Gtk.Label(label="RAM")
        ram_title.set_halign(Gtk.Align.START)
        self.ram_val_lbl = Gtk.Label(label="0M")
        self.ram_val_lbl.set_halign(Gtk.Align.END)
        ram_header.pack_start(ram_title, True, True, 0)
        ram_header.pack_end(self.ram_val_lbl, False, False, 0)

        self.ram_bar = Gtk.ProgressBar()
        self.ram_bar.set_fraction(0.0)
        self.ram_bar.get_style_context().add_class('meter-ram')

        ram_box.pack_start(ram_header, False, False, 0)
        ram_box.pack_start(self.ram_bar, False, False, 0)
        self.pack_start(ram_box, False, False, 0)

        # Net Row
        net_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.net_down_lbl = Gtk.Label()
        self.net_down_lbl.set_halign(Gtk.Align.START)
        self.net_down_lbl.get_style_context().add_class('stat-subtext')
        self.net_down_lbl.set_markup(" 0.0 KB/s")

        self.net_up_lbl = Gtk.Label()
        self.net_up_lbl.set_halign(Gtk.Align.END)
        self.net_up_lbl.get_style_context().add_class('stat-subtext')
        self.net_up_lbl.set_markup(" 0.0 KB/s")

        net_box.pack_start(self.net_down_lbl, True, True, 0)
        net_box.pack_end(self.net_up_lbl, False, False, 0)
        self.pack_start(net_box, False, False, 0)

        self.update_stats()
        GLib.timeout_add_seconds(2, self.update_stats)

    def update_stats(self):
        data = system_engine.poll()
        cpu_pct = data['cpu_percent']
        self.cpu_val_lbl.set_text(f"{cpu_pct:.1f}%")
        self.cpu_bar.set_fraction(cpu_pct / 100.0)

        ram_used = data['ram_used_mb']
        ram_total = data['ram_total_mb']
        ram_pct = data['ram_percent']
        self.ram_val_lbl.set_text(f"{ram_used}M / {ram_total}M")
        self.ram_bar.set_fraction(ram_pct / 100.0)

        down = data['download_kbps']
        up = data['upload_kbps']
        down_str = f"{down / 1024.0:.1f} MB/s" if down >= 1024 else f"{down:.0f} KB/s"
        up_str = f"{up / 1024.0:.1f} MB/s" if up >= 1024 else f"{up:.0f} KB/s"
        self.net_down_lbl.set_markup(f" {down_str}")
        self.net_up_lbl.set_markup(f" {up_str}")
        return True
