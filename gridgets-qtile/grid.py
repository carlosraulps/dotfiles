import os
import json
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

from widgets.clock import ClockWidget
from widgets.weather import WeatherWidget
from widgets.system import SystemWidget
from widgets.music import MusicWidget
from widgets.notes import NotesWidget
from widgets.pomodoro import PomodoroWidget
from widgets.quotes import QuotesWidget
from widgets.command import CommandWidget
from widgets.slurm import SlurmWidget

WIDGET_REGISTRY = {
    'clock': ClockWidget,
    'time': ClockWidget,
    'weather': WeatherWidget,
    'system': SystemWidget,
    'cpu-ram': SystemWidget,
    'music': MusicWidget,
    'notes': NotesWidget,
    'pomodoro': PomodoroWidget,
    'quotes': QuotesWidget,
    'command': CommandWidget,
    'slurm': SlurmWidget,
    'squeue': SlurmWidget,
}

class DesktopGridCanvas(Gtk.Fixed):
    def __init__(self, config_path):
        super().__init__()
        self.config_path = config_path
        self.config = {}
        self.widget_instances = []
        self.set_has_window(True)

        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {'global': {}, 'widgets': []}

    def rebuild_grid(self, screen_width, screen_height):
        # Clear existing children
        for child in self.get_children():
            self.remove(child)
            child.destroy()
        self.widget_instances.clear()

        glob = self.config.get('global', {})
        cols = glob.get('columns', 28)
        rows = glob.get('rows', 16)
        gap = glob.get('gap', 6)
        margin = glob.get('margin', 10)
        top_offset = glob.get('top_offset', 28)

        # Calculate cell geometry matching Gridgets
        available_width = screen_width - (margin * 2) - (gap * (cols - 1))
        cell_size = max(1, available_width // cols)
        step = cell_size + gap

        # Render active widgets
        for w_data in self.config.get('widgets', []):
            w_type = w_data.get('type')
            cls = WIDGET_REGISTRY.get(w_type)
            if not cls:
                continue

            col = w_data.get('col', w_data.get('x', 0))
            row = w_data.get('row', w_data.get('y', 0))
            w_cols = w_data.get('width', 2)
            w_rows = w_data.get('height', 2)

            pixel_x = margin + (col * step)
            pixel_y = top_offset + margin + (row * step)
            pixel_width = (w_cols * cell_size) + ((w_cols - 1) * gap)
            pixel_height = (w_rows * cell_size) + ((w_rows - 1) * gap)

            try:
                instance = cls(w_data)
                instance.set_size_request(pixel_width, pixel_height)
                self.put(instance, pixel_x, pixel_y)
                self.widget_instances.append(instance)
            except Exception as e:
                print(f"[DesktopGrid] Error creating {w_type}: {e}")

        self.show_all()
