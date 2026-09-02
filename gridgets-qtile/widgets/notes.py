import os
import json
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

NOTES_FILE = os.path.expanduser('~/.local/share/gridgets/notes-qtile.json')

class NotesWidget(Gtk.Box):
    def __init__(self, config):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.config = config
        self.get_style_context().add_class('gridget-card')
        self.get_style_context().add_class('gridget-notes')

        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        title = Gtk.Label()
        title.set_halign(Gtk.Align.START)
        title.get_style_context().add_class('widget-title')
        title.set_markup("<b>📝 Quick Notes</b>")
        header.pack_start(title, True, True, 0)
        self.pack_start(header, False, False, 0)

        # Scrolled Text View
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.text_view = Gtk.TextView()
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.text_view.get_style_context().add_class('notes-textview')

        self.buffer = self.text_view.get_buffer()
        self.buffer.connect('changed', self.on_text_changed)

        scrolled.add(self.text_view)
        self.pack_start(scrolled, True, True, 0)

        self.load_note()

    def load_note(self):
        default_text = "• Quick Task 1\n• Quick Task 2\n\nEdit your notes here."
        if os.path.exists(NOTES_FILE):
            try:
                with open(NOTES_FILE, 'r') as f:
                    data = json.load(f)
                    self.buffer.set_text(data.get('notes', default_text))
                    return
            except Exception:
                pass
        self.buffer.set_text(default_text)

    def on_text_changed(self, buffer):
        start, end = buffer.get_bounds()
        text = buffer.get_text(start, end, True)
        os.makedirs(os.path.dirname(NOTES_FILE), exist_ok=True)
        try:
            with open(NOTES_FILE, 'w') as f:
                json.dump({'notes': text}, f)
        except Exception:
            pass
