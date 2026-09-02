import random
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

QUOTES = [
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("Talk is cheap. Show me the code.", "Linus Torvalds"),
    ("Simplicity is prerequisite for reliability.", "Edsger W. Dijkstra"),
    ("Make it work, make it right, make it fast.", "Kent Beck"),
    ("Code is like humor. When you have to explain it, it’s bad.", "Cory House"),
    ("First, solve the problem. Then, write the code.", "John Johnson"),
    ("Premature optimization is the root of all evil.", "Donald Knuth"),
    ("Clean code always looks like it was written by someone who cares.", "Robert C. Martin"),
    ("Programs must be written for people to read, and only incidentally for machines to execute.", "Harold Abelson"),
    ("The best error message is the one that never shows up.", "Thomas Fuchs"),
    ("The secret of getting ahead is getting started.", "Mark Twain"),
]

class QuotesWidget(Gtk.Box):
    def __init__(self, config):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.config = config
        self.get_style_context().add_class('gridget-card')
        self.get_style_context().add_class('gridget-quotes')

        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        title = Gtk.Label()
        title.set_halign(Gtk.Align.START)
        title.get_style_context().add_class('widget-title')
        title.set_markup("<b>💡 Daily Quote</b>")
        header.pack_start(title, True, True, 0)
        self.pack_start(header, False, False, 0)

        # Body
        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        body.set_valign(Gtk.Align.CENTER)

        self.quote_lbl = Gtk.Label()
        self.quote_lbl.set_line_wrap(True)
        self.quote_lbl.set_halign(Gtk.Align.START)
        self.quote_lbl.get_style_context().add_class('quote-text')

        self.author_lbl = Gtk.Label()
        self.author_lbl.set_halign(Gtk.Align.END)
        self.author_lbl.get_style_context().add_class('quote-author')

        body.pack_start(self.quote_lbl, True, True, 0)
        body.pack_start(self.author_lbl, False, False, 0)
        self.pack_start(body, True, True, 0)

        self.cycle_quote()
        # Change quote every 4 hours
        GLib.timeout_add_seconds(14400, self.cycle_quote)

    def cycle_quote(self):
        quote, author = random.choice(QUOTES)
        self.quote_lbl.set_markup(f"<i>\"{quote}\"</i>")
        self.author_lbl.set_markup(f"<span alpha='70%'>— {author}</span>")
        return True
