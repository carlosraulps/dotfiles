#!/bin/sh
# ==============================================================================
#  Qtile Autostart & Workspace Layout Automation (Singleton Lock Protected)
# ==============================================================================

# Prevent concurrent duplicate execution of autostart.sh
LOCKFILE="/tmp/qtile_autostart.lock"
if [ -e "$LOCKFILE" ] && kill -0 "$(cat "$LOCKFILE" 2>/dev/null)" 2>/dev/null; then
    exit 0
fi
echo $$ > "$LOCKFILE"
trap 'rm -f "$LOCKFILE"' EXIT INT TERM

# Sync Google Drive (if not already mounted via systemd)
if ! mountpoint -q ~/mnt/google-drive 2>/dev/null; then
    rclone mount cr: ~/mnt/google-drive --vfs-cache-mode full &
fi

# Inhibit systemd idle sleep during heavy computing sessions
pgrep -f "systemd-inhibit --what=idle:sleep" >/dev/null || nohup systemd-inhibit --what=idle:sleep sleep infinity &

# Export XDG data dirs for Rofi and GUI apps
export XDG_DATA_DIRS="/usr/local/share:/usr/share:$HOME/.local/share${XDG_DATA_DIRS:+:$XDG_DATA_DIRS}"

# Launch Gridgets Desktop widgets
/home/cr/temporary/dotfiles/gridgets-qtile/run.sh --bg &

# Notification daemon
pgrep -x dunst >/dev/null || dunst &

# Screenshot daemon
pgrep -x flameshot >/dev/null || flameshot &

# Apple Look Up Selection Daemon ('📖 Look Up' floating pill)
pgrep -f "apple-lookup --daemon" >/dev/null || /home/cr/.local/bin/apple-lookup --daemon &

# Wallpaper (Caricature Coastal View)
if command -v feh >/dev/null 2>&1; then
    WALLPAPER="/home/cr/Downloads/Caricature Coastal View.png"
    [ -f "$WALLPAPER" ] || WALLPAPER="/home/cr/.config/qtile/wallpapers/Caricature Coastal View.png"
    [ -f "$WALLPAPER" ] || WALLPAPER="/home/cr/.config/qtile/mojave-dark.png"
    feh --bg-fill "$WALLPAPER" &
fi

# X11 Compositor (Eliminates window tearing & white workspace flashes)
pgrep -x picom >/dev/null || picom -b &

# ==============================================================================
#  Workstation App Layout Automation
# ==============================================================================

# Workspace 3 (Win+3): Launch Antigravity IDE AND Antigravity App (Both strictly in Max layout)
if ! pgrep -f "antigravity-ide" >/dev/null 2>&1; then
    antigravity-ide &
fi

if ! pgrep -f "/opt/antigravity/antigravity" >/dev/null 2>&1; then
    /usr/local/bin/antigravity &
fi

# Workspace 2 (Win+2): Launch Brave
if ! pgrep -x "brave" >/dev/null 2>&1; then
    brave &
fi

# ==============================================================================
#  Alacritty + Tmux Resilient Workspace Restoration
# ==============================================================================
# Automatically restore Alacritty viewports to their designated Qtile workspaces
# (Guaranteed singleton protection, no duplicate terminals, zero syntax errors)
python3 /home/cr/.config/qtile/scripts/term_manager.py restore &

# Prune dead/idle archived terminals older than 7 days
python3 /home/cr/.config/qtile/scripts/reap_archive.py &
