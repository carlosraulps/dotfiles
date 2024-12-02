
# Qtile keybindings

from libqtile.config import Key
from libqtile.lazy import lazy


mod = "mod4"

keys = [Key(key[0], key[1], *key[2:]) for key in [
    # ------------ Window Configs ------------

    # Switch between windows in current stack pane
    ([mod], "j", lazy.layout.down()),
    ([mod], "k", lazy.layout.up()),
    ([mod], "h", lazy.layout.left()),
    ([mod], "l", lazy.layout.right()),

    # Change window sizes (MonadTall)
    ([mod, "shift"], "l", lazy.layout.grow()),
    ([mod, "shift"], "h", lazy.layout.shrink()),

    # Toggle floating
    ([mod, "shift"], "f", lazy.window.toggle_floating()),

    # Move windows up or down in current stack
    ([mod, "shift"], "j", lazy.layout.shuffle_down()),
    ([mod, "shift"], "k", lazy.layout.shuffle_up()),

    # Toggle between different layouts as defined below
    ([mod], "Tab", lazy.next_layout()),
    ([mod, "shift"], "Tab", lazy.prev_layout()),

    # Kill window
    ([mod], "w", lazy.window.kill()),

    # Switch focus of monitors
    ([mod], "period", lazy.next_screen()),
    ([mod], "comma", lazy.prev_screen()),

    # Restart Qtile
    ([mod, "control"], "r", lazy.restart()),

    ([mod, "control"], "q", lazy.shutdown()),
    ([mod], "r", lazy.spawncmd()),

    # ------------ App Configs ------------

    # Menu
    ([mod], "m", lazy.spawn("rofi -show drun -theme .config/rofi/launchers/type-2/style-15.rasi")),

    
    ([mod, "shift"], "p", lazy.spawn(".config/rofi/powermenu/type-1/powermenu.sh")),

    # Window Nav
    ([mod, "shift"], "m", lazy.spawn("rofi -show")),

    # Browser
    ([mod], "b", lazy.spawn("brave")),

    # File Explorer
    ([mod], "r", lazy.spawn("alacritty -e ranger")),

    # Terminal
    ([mod], "Return", lazy.spawn("alacritty")),

    # Redshift
    #([mod], "r", lazy.spawn("redshift -O 2400")),
    #([mod, "shift"], "r", lazy.spawn("redshift -x")),

    # Screenshot
    ([mod], "s", lazy.spawn("flameshot gui")),
    #([mod, "shift"], "s", lazy.spawn("scrot -s")),

    # ------------ Hardware Configs ------------

    # Volume

    ([mod], "F2", lazy.spawn("amixer set Master 5%-")),
    ([mod], "F3", lazy.spawn("amixer set Master 5%+")),
    ([mod], "F1", lazy.spawn("amixer set Master toggle")),

    # Brightness
    ([mod], "F6", lazy.spawn("brightnessctl set 5%+")),
    ([mod], "F5", lazy.spawn("brightnessctl set 5%-")),

]]
