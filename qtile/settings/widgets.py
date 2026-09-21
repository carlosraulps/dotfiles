import os
import sys
from libqtile import widget
from libqtile.lazy import lazy
from .theme import colors

SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
import pomodoro
import slurm_widget

# Active network interface detection (Ethernet priority)
def get_active_net_interface():
    for iface in ['enp38s0', 'eth0', 'enp0s3', 'wlan0']:
        if os.path.exists(f'/sys/class/net/{iface}/operstate'):
            try:
                with open(f'/sys/class/net/{iface}/operstate') as f:
                    if f.read().strip() == 'up':
                        return iface
            except Exception:
                pass
    return 'enp38s0'

ACTIVE_IFACE = get_active_net_interface()

def base(fg='text', bg='dark'): 
    return {
        'foreground': colors[fg],
        'background': colors[bg]
    }

def separator():
    return widget.Sep(**base(), linewidth=0, padding=4)

def bar_divider():
    return widget.Sep(
        background=colors['dark'],
        foreground=colors['grey'],
        linewidth=1,
        padding=10
    )

def icon(fg='text', bg='dark', fontsize=16, text="?", mouse_callbacks=None):
    kwargs = base(fg, bg)
    if mouse_callbacks:
        kwargs['mouse_callbacks'] = mouse_callbacks
    return widget.TextBox(
        **kwargs,
        fontsize=fontsize,
        text=text,
        padding=2
    )

def powerline(fg="light", bg="dark"):
    return widget.TextBox(
        **base(fg, bg),
        text="",  # Icon: nf-oct-triangle_left
        fontsize=34,
        padding=0
    )

def media_player_widget():
    """
    Spotify, YouTube & Browser MPRIS2 Media Player Widget.
    Preserved in background per configuration (uncomment in primary_widgets to display).
    """
    return widget.Mpris2(
        name="media_player",
        objname=None,
        display_metadata=["xesam:title", "xesam:artist"],
        scroll_chars=None,
        stop_pause_text="⏸ Paused",
        format="󰎈 {xesam:artist} - {xesam:title}",
        paused_text="󰏤 {xesam:title}",
        playing_text="󰐊 {xesam:title}",
        **base(bg="dark", fg="color2"),
        padding=4,
    )

def workspaces(): 
    return [
        icon(
            fg='focus',
            bg='dark',
            fontsize=18,
            text='  ',
            mouse_callbacks={'Button1': lazy.spawn("bash -c '~/.config/rofi/powermenu/type-1/powermenu.sh'")}
        ),  # Arch / Apple System Menu (Reboot, Shutdown, Logout, Lock)
        separator(),
        widget.GroupBox(
            **base(fg='light'),
            font='UbuntuMono Nerd Font',
            fontsize=17,
            margin_y=3,
            margin_x=0,
            padding_y=8,
            padding_x=6,
            borderwidth=1,
            active=colors['active'],
            inactive=colors['inactive'],
            rounded=False,
            highlight_method='block',
            urgent_alert_method='block',
            urgent_border=colors['urgent'],
            this_current_screen_border=colors['focus'],
            this_screen_border=colors['grey'],
            other_current_screen_border=colors['dark'],
            other_screen_border=colors['dark'],
            disable_drag=True
        ),
        separator(),
        widget.WindowName(**base(fg='focus'), fontsize=13, padding=6),
        separator(),
    ]

# MacBook / macOS Top Bar (Zero Overlap & São Paulo Timezone)
primary_widgets = [
    *workspaces(),

    # Layout Indicator
    widget.CurrentLayout(**base(bg='dark'), mode='icon', scale=0.65),
    widget.CurrentLayout(**base(bg='dark'), padding=4),
    bar_divider(),

    # Pacman / System Updates
    icon(bg="dark", fg="color2", fontsize=15, text=' '),
    widget.CheckUpdates(
        background=colors['dark'],
        colour_have_updates=colors['color2'],
        colour_no_updates=colors['text'],
        no_update_string='0',
        display_format='{updates}',
        update_interval=1800,
        custom_command='checkupdates',
        padding=2,
    ),
    bar_divider(),

    # Ethernet / Wi-Fi Network Indicator & Live Bandwidth (Clickable -> Wi-Fi Menu)
    icon(
        bg="dark",
        fg="focus",
        fontsize=16,
        text='󰈀 ',
        mouse_callbacks={'Button1': lazy.spawn("bash -c '~/.config/rofi/applets/bin/wifi.sh'")}
    ),
    widget.Net(
        **base(bg='dark'),
        interface=ACTIVE_IFACE,
        format='{down:.1f}M ↓↑ {up:.1f}M',
        prefix='M',
        padding=2
    ),
    bar_divider(),

    # CPU & RAM & Storage Monitors
    icon(bg="dark", fg="color1", fontsize=16, text=' '),
    widget.CPU(
        **base(bg='dark'),
        format='{load_percent:.0f}%',
        padding=2
    ),
    separator(),
    icon(bg="dark", fg="color3", fontsize=15, text=' '),
    widget.Memory(
        **base(bg='dark'),
        format='{MemUsed:.0f}M',
        padding=2
    ),
    separator(),
    icon(
        bg="dark",
        fg="color4",
        fontsize=15,
        text='󰋊 ',
        mouse_callbacks={'Button1': lazy.spawn("alacritty -e df -h")}
    ),
    widget.DF(
        **base(bg='dark'),
        partition='/home',
        visible_on_warn=False,
        format='{uf:.0f}G',
        measure='G',
        update_interval=30,
        padding=2,
        mouse_callbacks={'Button1': lazy.spawn("alacritty -e df -h")}
    ),
    bar_divider(),

    # Desktop Workstation Power (AC Direct Power)
    icon(bg="dark", fg="color2", fontsize=16, text='󰚥 '),
    widget.TextBox(
        **base(bg='dark'),
        text='100% AC',
        padding=2
    ),
    bar_divider(),

    # Pomodoro Productivity Suite (Left Click: Rofi Menu, Middle Click: Pause/Play, Right Click: Reset)
    icon(
        bg="dark",
        fg="color3",
        fontsize=15,
        text='󰄉 ',
        mouse_callbacks={
            'Button1': lazy.spawn("/home/cr/temporary/dotfiles/qtile/scripts/pomodoro.py menu"),
            'Button2': lazy.spawn("/home/cr/temporary/dotfiles/qtile/scripts/pomodoro.py toggle"),
            'Button3': lazy.spawn("/home/cr/temporary/dotfiles/qtile/scripts/pomodoro.py reset"),
        }
    ),
    widget.GenPollText(
        background=colors['dark'],
        update_interval=1,
        func=pomodoro.get_bar_text,
        markup=True,
        padding=3,
        mouse_callbacks={
            'Button1': lazy.spawn("/home/cr/temporary/dotfiles/qtile/scripts/pomodoro.py menu"),
            'Button2': lazy.spawn("/home/cr/temporary/dotfiles/qtile/scripts/pomodoro.py toggle"),
            'Button3': lazy.spawn("/home/cr/temporary/dotfiles/qtile/scripts/pomodoro.py reset"),
        }
    ),
    bar_divider(),

    # Slurm Workstation Running Jobs Monitor (Watches local active running jobs; Click -> Terminal Watch)
    icon(
        bg="dark",
        fg="color2",
        fontsize=15,
        text='󰒋 ',
        mouse_callbacks={
            'Button1': lazy.spawn("alacritty -e /home/cr/.config/qtile/scripts/slurm_multicluster_viewer.py"),
            'Button3': lazy.spawn("alacritty -e squeue"),
        }
    ),
    widget.GenPollText(
        background=colors['dark'],
        update_interval=2,
        func=slurm_widget.get_running_jobs_text,
        markup=True,
        padding=3,
        mouse_callbacks={
            'Button1': lazy.spawn("alacritty -e /home/cr/.config/qtile/scripts/slurm_multicluster_viewer.py"),
            'Button3': lazy.spawn("alacritty -e squeue"),
        }
    ),
    bar_divider(),

    # Media Player Widget (Spotify / YouTube / MPRIS2) - [Preserved in code in background, inactive]
    # media_player_widget(),
    # bar_divider(),

    # Spotlight Search Icon (Clickable -> Rofi Launcher)
    icon(
        bg="dark",
        fg="text",
        fontsize=14,
        text=' ',
        mouse_callbacks={'Button1': lazy.spawn("rofi -show drun -theme ~/.config/rofi/themes/spotlight-dark.rasi")}
    ),
    separator(),

    # Control Center Icon (Clickable -> Quicklinks Applet)
    icon(
        bg="dark",
        fg="text",
        fontsize=16,
        text='󰍜 ',
        mouse_callbacks={'Button1': lazy.spawn("bash -c '~/.config/rofi/applets/bin/quicklinks.sh'")}
    ),
    separator(),

    # macOS Date & Time Pill (São Paulo, BR: America/Sao_Paulo)
    powerline('color1', 'dark'),
    icon(bg="color1", fg="dark", fontsize=15, text='  '),
    widget.Clock(
        timezone='America/Sao_Paulo',
        foreground=colors['dark'],
        background=colors['color1'],
        format='%a %d %b  %H:%M ',
        padding=4,
    ),

    # System Tray
    widget.Systray(background=colors['dark'], padding=6),
]

secondary_widgets = [
    *workspaces(),
    separator(),
    powerline('color1', 'dark'),
    widget.CurrentLayout(**base(bg='color1'), mode='icon', scale=0.65),
    widget.CurrentLayout(**base(bg='color1'), padding=4),
    powerline('color2', 'color1'),
    widget.Clock(
        timezone='America/Sao_Paulo',
        **base(bg='color2'),
        format='%a %d %b  %H:%M '
    ),
    powerline('dark', 'color2'),
]

widget_defaults = {
    'font': 'UbuntuMono Nerd Font',
    'fontsize': 13,
    'padding': 1,
}
extension_defaults = widget_defaults.copy()
