
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
    ([mod, "shift"], "r", lazy.spawncmd()),

    # ------------ App Configs ------------

    # Menu (Rofi Spotlight Launcher)
    ([mod], "space", lazy.spawn("rofi -show drun -theme ~/.config/rofi/themes/spotlight-dark.rasi")),
    ([mod], "m", lazy.spawn("rofi -show drun -theme ~/.config/rofi/themes/spotlight-dark.rasi")),

    # Spotlight File Search (Win+F) & Calculator (Win+C)
    ([mod], "f", lazy.spawn("rofi -show finder -theme ~/.config/rofi/themes/spotlight-dark.rasi")),
    ([mod], "c", lazy.spawn("bash -c '~/.config/rofi/scripts/spotlight-calc.sh'")),

    # Window Switcher (Alt+Tab & Super+Shift+M)
    (["mod1"], "Tab", lazy.spawn("rofi -show window -theme ~/.config/rofi/themes/spotlight-dark.rasi")),
    ([mod, "shift"], "m", lazy.spawn("rofi -show window -theme ~/.config/rofi/themes/spotlight-dark.rasi")),

    # Power Menu
    ([mod, "shift"], "p", lazy.spawn("bash -c '~/.config/rofi/powermenu/type-1/powermenu.sh'")),

    # Pomodoro Productivity Menu Popup (Win+P)
    ([mod], "p", lazy.spawn("/home/cr/temporary/dotfiles/qtile/scripts/pomodoro.py menu")),

    # Wi-Fi Menu Applet
    ([mod, "shift"], "w", lazy.spawn("bash -c '~/.config/rofi/applets/bin/wifi.sh'")),

    # Quicklinks Applet
    ([mod], "e", lazy.spawn("bash -c '~/.config/rofi/applets/bin/quicklinks.sh'")),

    # Apple-Style Look Up Dictionary (Win+D or Ctrl+Alt+D)
    ([mod], "d", lazy.spawn("/home/cr/.local/bin/apple-lookup")),
    (["mod1", "control"], "d", lazy.spawn("/home/cr/.local/bin/apple-lookup")),

    # Browser (Brave)
    ([mod], "b", lazy.spawn("brave")),

    # File Explorer (Ranger)
    ([mod], "r", lazy.spawn("alacritty -e ranger")),

    # Terminal (Alacritty with Smart Tmux - Workspace-Aware & Protected)
    ([mod], "Return", lazy.spawn("/home/cr/.config/qtile/scripts/spawn_term.sh")),

    # Instant Undo: Restore Last Closed Terminal (Accidental Close Guard)
    ([mod], "u", lazy.spawn("/home/cr/.config/qtile/scripts/undo_close_term.sh")),

    # Terminal Archive & History Menu (Rofi Search across 7-day preserved sessions)
    ([mod, "shift"], "u", lazy.spawn("/home/cr/.config/qtile/scripts/term_archive_menu.py")),
    ([mod, "shift"], "t", lazy.spawn("/home/cr/.config/qtile/scripts/term_archive_menu.py")),

    # Fallback Pure Terminal (without Tmux)
    ([mod, "shift"], "Return", lazy.spawn("alacritty")),

    # Gridgets Desktop Widgets Toggle / Restart
    ([mod, "shift"], "g", lazy.spawn("/home/cr/temporary/dotfiles/gridgets-qtile/run.sh --bg")),

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
