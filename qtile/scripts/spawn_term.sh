#!/bin/bash
# ==============================================================================
#  spawn_term.sh — Workspace-Aware Alacritty Launcher for Qtile
# ==============================================================================

# Get currently active workspace group name from Qtile IPC
CURR_WS=$(python3 -c "from libqtile.command.client import InteractiveCommandClient; c = InteractiveCommandClient(); print(c.group.info()['name'])" 2>/dev/null)

case "$CURR_WS" in
    *"󰖟"*) CLASS="qtile-term-ws1" ;;
    *""*) CLASS="qtile-devterm" ;;
    *""*) CLASS="qtile-term-ws3" ;;
    *""*) CLASS="qtile-term-ws4" ;;
    *""*) CLASS="qtile-term-ws5" ;;
    *)     CLASS="Alacritty" ;;
esac

# Launch Alacritty with workspace-bound class and optional target window
alacritty --class "$CLASS,$CLASS" -e /home/cr/.local/bin/tmux-smart-attach "$@" &
