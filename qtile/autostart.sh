#!/bin/sh

# Sycs google drive

rclone mount cr: ~/mnt/google-drive --vfs-cache-mode full &

nohup systemd-inhibit --what=idle:sleep sleep infinity &

# Export XDG data dirs for Rofi and GUI apps
export XDG_DATA_DIRS="/usr/local/share:/usr/share:$HOME/.local/share${XDG_DATA_DIRS:+:$XDG_DATA_DIRS}"

# Launch Gridgets Desktop widgets
/home/cr/temporary/dotfiles/gridgets-qtile/run.sh --bg &

# Notification daemon
command -v dunst >/dev/null 2>&1 && dunst &

# Screenshot daemon
command -v flameshot >/dev/null 2>&1 && flameshot &

# Wallpaper (Caricature Coastal View)
if command -v feh >/dev/null 2>&1; then
  WALLPAPER="/home/cr/Downloads/Caricature Coastal View.png"
  [ -f "$WALLPAPER" ] || WALLPAPER="/home/cr/.config/qtile/wallpapers/Caricature Coastal View.png"
  [ -f "$WALLPAPER" ] || WALLPAPER="/home/cr/.config/qtile/mojave-dark.png"
  feh --bg-fill "$WALLPAPER" &
fi

# X11 Compositor (Eliminates window tearing & white workspace flashes)
command -v picom >/dev/null 2>&1 && picom -b &
