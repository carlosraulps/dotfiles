# Qtile workspaces configuration
from types import FunctionType  # type: ignore
from libqtile.config import Key, Group, Match
from libqtile.lazy import lazy
from libqtile import layout
from .keys import mod, keys
from .theme import colors

layout_conf = {
    'border_focus': colors['focus'][0],
    'border_width': 3,
    'margin': 2
}

groups = [
    # Workspace 1 (General / Web)
    Group(" 󰖟  ", layout="monadtall"),

    # Workspace 2 (Win+2: Brave on Left + 2 Terminals on Right in MonadTall)
    Group(
        "   ",
        layout="monadtall",
        layouts=[layout.MonadTall(**layout_conf), layout.Max()],
        matches=[
            Match(wm_class="Brave-browser"),
            Match(wm_class="brave-browser"),
            Match(wm_class="qtile-devterm"),
        ]
    ),

    # Workspace 3 (Win+3: Antigravity IDE strictly in MAX - not monadtall, not nothing!)
    Group(
        "  ",
        layout="max",
        layouts=[layout.Max()],
        matches=[
            Match(wm_class="antigravity-ide"),
            Match(wm_class="antigravity"),
            Match(wm_class="Antigravity"),
            Match(wm_class="Antigravity-ide"),
        ]
    ),

    # Workspace 4 (Work / Notes)
    Group("   ", layout="monadtall"),

    # Workspace 5 (Media / Discord / Zoom)
    Group("   ", layout="monadtall"),
]

for i, group in enumerate(groups):
    actual_key = str(i + 1)
    keys.extend([
        # Switch to workspace N
        Key([mod], actual_key, lazy.group[group.name].toscreen(toggle=False)),
        # Send window to workspace N
        Key([mod, "shift"], actual_key, lazy.window.togroup(group.name))
    ])
