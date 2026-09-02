#!/usr/bin/python3
import sys
import os
import signal
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib

from grid import DesktopGridCanvas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
CSS_PATH = os.path.join(BASE_DIR, 'style.css')

class GridgetsDesktopWindow(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("Gridgets Desktop")
        self.set_wmclass("gridgets", "Gridgets")
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_below(True)

        # X11 desktop layer window type hint
        self.set_type_hint(Gdk.WindowTypeHint.DESKTOP)

        # Enable RGBA transparency
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        self.set_app_paintable(True)

        self.get_style_context().add_class('gridgets-window')

        # Load Stylesheet
        self.load_css()

        # Canvas
        self.canvas = DesktopGridCanvas(CONFIG_PATH)
        self.add(self.canvas)

        # Position to cover full screen
        self.update_geometry()

        self.connect('delete-event', Gtk.main_quit)

    def load_css(self):
        if os.path.exists(CSS_PATH):
            css_provider = Gtk.CssProvider()
            css_provider.load_from_path(CSS_PATH)
            screen = Gdk.Screen.get_default()
            Gtk.StyleContext.add_provider_for_screen(
                screen,
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def update_geometry(self):
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor() or display.get_monitor(0)
        if monitor:
            geom = monitor.get_geometry()
            width = geom.width
            height = geom.height
        else:
            screen = Gdk.Screen.get_default()
            width = screen.get_width()
            height = screen.get_height()

        self.set_default_size(width, height)
        self.move(0, 0)
        self.canvas.rebuild_grid(width, height)

def main():
    # Handle SIGINT cleanly
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = GridgetsDesktopWindow()
    app.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()
