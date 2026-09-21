
from libqtile import hook

from types import FunctionType # type: ignore

from settings.keys import mod, keys
from settings.groups import groups
from settings.layouts import layouts, floating_layout
from settings.widgets import widget_defaults, extension_defaults
from settings.screens import screens
from settings.mouse import mouse
from settings.path import qtile_path


from os import path
import subprocess


@hook.subscribe.startup
def autostart():
    # Runs once on boot and once on any live restart
    subprocess.Popen([path.join(qtile_path, 'autostart.sh')])

import threading

_save_timer = None

def debounced_save():
    global _save_timer
    _save_timer = None
    term_mgr = path.join(qtile_path, 'scripts', 'term_manager.py')
    if path.exists(term_mgr):
        subprocess.Popen(['python3', term_mgr, 'save'])

def schedule_save(delay=1.5):
    global _save_timer
    if _save_timer is not None:
        _save_timer.cancel()
    _save_timer = threading.Timer(delay, debounced_save)
    _save_timer.daemon = True
    _save_timer.start()

@hook.subscribe.client_managed
def on_client_managed(client):
    schedule_save(1.5)

@hook.subscribe.client_killed
def on_client_killed(client):
    schedule_save(0.5)

@hook.subscribe.shutdown
def on_shutdown():
    term_mgr = path.join(qtile_path, 'scripts', 'term_manager.py')
    if path.exists(term_mgr):
        subprocess.run(['python3', term_mgr, 'save'], timeout=2)

main = None
dgroups_key_binder = None
dgroups_app_rules: list = []
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
auto_fullscreen = True
focus_on_window_activation = 'urgent'
wmname = 'LG3D'

