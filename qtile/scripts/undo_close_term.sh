#!/bin/bash
# ==============================================================================
#  undo_close_term.sh — Instant Undo for Accidental Terminal Closure
# ==============================================================================

LAST_FILE="$HOME/.config/qtile/last_closed_window.txt"
TARGET_WIN=""

if [ -f "$LAST_FILE" ]; then
    CANDIDATE=$(cat "$LAST_FILE" 2>/dev/null | tr -d '[:space:]')
    if [ -n "$CANDIDATE" ] && tmux list-windows -t archive -F "#{window_id}" 2>/dev/null | grep -qx "$CANDIDATE"; then
        TARGET_WIN="$CANDIDATE"
    fi
fi

# Fallback: Pick latest window in archive
if [ -z "$TARGET_WIN" ]; then
    TARGET_WIN=$(tmux list-windows -t archive -F "#{window_id}" 2>/dev/null | tail -n 1)
fi

# If a window was found in archive, restore it to base and launch
if [ -n "$TARGET_WIN" ]; then
    rm -f "$LAST_FILE"
    tmux move-window -s "archive:$TARGET_WIN" -t "base:" 2>/dev/null
    /home/cr/.config/qtile/scripts/spawn_term.sh "$TARGET_WIN"
else
    /home/cr/.config/qtile/scripts/spawn_term.sh
fi
