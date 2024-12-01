from libqtile import widget
from .theme import colors
from libqtile.widget import battery, cpu
import psutil

# Get the icons at https://www.nerdfonts.com/cheat-sheet (you need a Nerd Font)

def base(fg='text', bg='dark'): 
    return {
        'foreground': colors[fg],
        'background': colors[bg]
    }


def separator():
    return widget.Sep(**base(), linewidth=0, padding=5)


def icon(fg='text', bg='dark', fontsize=18, text="?"):
    return widget.TextBox(
        **base(fg, bg),
        fontsize=fontsize,
        text=text,
        padding=3
    )


def powerline(fg="light", bg="dark"):
    return widget.TextBox(
        **base(fg, bg),
        text="", # Icon: nf-oct-triangle_left
        fontsize=37,
        padding=-12 #Nice significa que se reducirá el espacio alrededor del widget "TextBox" en 12 pixels.
    )


def workspaces(): 
    return [
        separator(),
        widget.GroupBox(
            **base(fg='light'),
            font='UbuntuMono Nerd Font',
            fontsize=19,
            margin_y=3,
            margin_x=0,
            padding_y=8,
            padding_x=5,
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
        widget.WindowName(**base(fg='focus'), fontsize=14, padding=5),
        separator(),
    ]

def battery_widget():
    return [
        powerline('color4', 'dark'),

        icon(bg='color4', text=''), # Icon: nf-fa-battery_3

        widget.Battery(
            **base(bg='color4'),
            battery='BAT0',
            format='{percent:2.0%}'
        ),

        icon(bg='color4', text=''), # Icon: nf-fa-battery_4

        widget.Battery(
            **base(bg='color4'),
            battery='BAT1',
            format='{percent:2.0%}'
        ),

        powerline('dark', 'color4'),
    ]

def storage():
    return [
        powerline('color2', 'dark'),

        icon(bg='color2', text='󱩵'), # Icon: nf-fa-hdd-o

        widget.DF(
            **base(bg='color2'),
            format=' {f}{m}',
            visible_on_warn=False,
            partition='/'
        ),

        powerline('dark', 'color2'),
    ]

def cpu_ram():
    return [
        powerline('color1', 'dark'),

        icon(bg='color1', text=''), # Icon: nf-fa-cogs

        widget.CPU(
            **base(bg='color1'),
            format='CPU {freq_current}GHz {load_percent}%'
        ),

        icon(bg='color1', text=''), # Icon: nf-fa-memory

        widget.Memory(
            **base(bg='color1'),
            format='{MemUsed}M/{MemTotal}M'
        ),

        powerline('dark', 'color1'),
    ]

primary_widgets = [
    *workspaces(),

    separator(),

    powerline('dark', 'dark'),

    widget.CurrentLayoutIcon(**base(bg='dark'), scale=0.65),

    widget.CurrentLayout(**base(bg='dark'), padding=5),

    powerline('dark', 'dark'),

    icon(bg="dark", text='|   '), # Icon: nf-fa-download
    
    widget.CheckUpdates(
        background=colors['dark'],
        colour_have_updates=colors['text'],
        colour_no_updates=colors['text'],
        no_update_string='0',
        display_format='{updates}',
        update_interval=1800,
        custom_command='checkupdates',
    ),

    powerline('dark', 'dark'),

    icon(bg="dark", text='|   '),  # Icon: nf-fa-feed
    
    widget.Net(**base(bg='dark'), interface='wlp4s0'),

    #######
    powerline('dark', 'dark'),

    icon(bg="dark", fontsize=16, text='|  󰁺 '), # Icon: nf-fa-battery-full

    widget.Battery(
        background=colors['dark'],
        battery=0,
        format='{percent:2.0%}'
    ),

    icon(bg="dark", fontsize=16, text='+'), # Icon: nf-fa-battery-full
    widget.Battery(
        background=colors['dark'],
        battery=1,
        format='{percent:2.0%}',
        update_interval=10,
    ),
    #######
    powerline('dark', 'dark'),
    
    icon(bg="dark", fontsize=17, text=' |  󰍛 '), # Icon: nf-mdi-memory

    widget.Memory(**base(bg='dark'), format='{MemUsed:.0f}M'),

    powerline('dark', 'dark'),

    icon(bg="color1", fg="dark", fontsize=17, text='  '), # Icon: nf-mdi-calendar_clock

    widget.Clock(
    foreground=colors['dark'],  # Color del texto
    background=colors['color1'],  # Fondo
    format='%d/%m/%Y - %H:%M ',
    padding=5,
),
    #powerline('dark', 'color1'),

    widget.Systray(background=colors['dark'], padding=5),
]

secondary_widgets = [
    *workspaces(),

    separator(),

    powerline('color1', 'dark'),

    widget.CurrentLayoutIcon(**base(bg='color1'), scale=0.65),

    widget.CurrentLayout(**base(bg='color1'), padding=5),

    powerline('color2', 'color1'),

    widget.Clock(**base(bg='color2'), format='%d/%m/%Y - %H:%M '),

    powerline('dark', 'color2'),
]

widget_defaults = {
    'font': 'Ubuntu Nerd Font Bold',
    'fontsize': 14,
    'padding': 1,
}
extension_defaults = widget_defaults.copy()
