#!/bin/bash
# Gridgets Desktop Launcher for Qtile

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

export NO_AT_BRIDGE=1
export DISPLAY="${DISPLAY:-:0}"
export XAUTHORITY="${XAUTHORITY:-$HOME/.Xauthority}"

# Use system python with PyGObject (GTK3) support
PYTHON_BIN="/usr/bin/python3"
if [ ! -x "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

PIDFILE="/tmp/gridgets-qtile.pid"
LOGFILE="/tmp/gridgets-qtile.log"

# Kill existing instance if running
if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    kill -9 "$PID" 2>/dev/null
    rm -f "$PIDFILE"
fi
pkill -f "$DIR/main.py" 2>/dev/null
sleep 0.3

# Run daemon in background or foreground
if [ "$1" = "--bg" ] || [ "$1" = "-b" ]; then
    nohup "$PYTHON_BIN" "$DIR/main.py" < /dev/null > "$LOGFILE" 2>&1 &
    PID=$!
    echo $PID > "$PIDFILE"
    disown $PID
    echo "Gridgets Desktop started in background (PID: $PID)."
else
    exec "$PYTHON_BIN" "$DIR/main.py"
fi

