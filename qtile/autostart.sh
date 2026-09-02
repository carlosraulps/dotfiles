#!/bin/sh
# ==============================================================================
#  Qtile Autostart & Workspace Layout Automation
# ==============================================================================

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

# Workspace 3 (Win+3): Launch Antigravity IDE strictly in Max layout
if ! pgrep -f "antigravity-ide" >/dev/null 2>&1; then
    antigravity-ide &
fi

# Workspace 2 (Win+2): Launch Brave on Left + 2 Terminals on Right in MonadTall
if ! pgrep -x "brave" >/dev/null 2>&1; then
    brave &
    sleep 0.6
    alacritty --class qtile-devterm,qtile-devterm -e /home/cr/.local/bin/tmux-smart-attach &
    sleep 0.3
    alacritty --class qtile-devterm,qtile-devterm -e /home/cr/.local/bin/tmux-smart-attach &
fi
