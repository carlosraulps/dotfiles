
import os
import subprocess
from libqtile.config import Screen
from libqtile import bar
from libqtile.log_utils import logger
from .widgets import primary_widgets, secondary_widgets


WALLPAPER = os.path.expanduser("~/Downloads/Caricature Coastal View.png")
if not os.path.exists(WALLPAPER):
    WALLPAPER = os.path.expanduser("~/.config/qtile/wallpapers/Caricature Coastal View.png")
if not os.path.exists(WALLPAPER):
    WALLPAPER = os.path.expanduser("~/.config/qtile/mojave-dark.png")


def status_bar(widgets):
    return bar.Bar(widgets, 24, opacity=0.92)


screens = [Screen(top=status_bar(primary_widgets), wallpaper=WALLPAPER, wallpaper_mode='fill')]

xrandr = "xrandr | grep -w 'connected' | cut -d ' ' -f 2 | wc -l"

command = subprocess.run(
    xrandr,
    shell=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

if command.returncode != 0:
    error = command.stderr.decode("UTF-8")
    logger.error(f"Failed counting monitors using {xrandr}:\n{error}")
    connected_monitors = 1
else:
    connected_monitors = int(command.stdout.decode("UTF-8"))

if connected_monitors > 1:
    for _ in range(1, connected_monitors):
        screens.append(Screen(top=status_bar(secondary_widgets), wallpaper=WALLPAPER, wallpaper_mode='fill'))
