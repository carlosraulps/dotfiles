#!/usr/bin/env bash
# ==============================================================================
#  Aesthetic Blurred Lock Screen for Qtile & Arch Linux (Full Screen Fill)
# ==============================================================================

WALLPAPER_DIR="$HOME/.config/qtile/wallpapers"
BLURRED_BG="$WALLPAPER_DIR/lock_blurred.png"
DEFAULT_BG="$WALLPAPER_DIR/Caricature Coastal View.png"

# If betterlockscreen is installed, use its advanced cached blur engine
if command -v betterlockscreen >/dev/null 2>&1; then
    betterlockscreen -l dimblur
    exit 0
fi

# Detect primary screen resolution (e.g. 1920x1080)
SCREEN_RES=$(xrandr --current 2>/dev/null | grep -E '\*' | head -n1 | awk '{print $1}')
SCREEN_RES="${SCREEN_RES:-1920x1080}"

# Ensure blurred wallpaper is scaled to exact screen resolution
if [ ! -f "$BLURRED_BG" ] && [ -f "$DEFAULT_BG" ]; then
    magick "$DEFAULT_BG" -resize "${SCREEN_RES}^" -gravity center -extent "$SCREEN_RES" -filter Gaussian -blur 0x14 -brightness-contrast -12x0 "$BLURRED_BG" 2>/dev/null
fi

# Lock screen using i3lock with full-screen blurred wallpaper
if [ -f "$BLURRED_BG" ]; then
    i3lock -i "$BLURRED_BG" --nofork
elif command -v i3lock >/dev/null 2>&1; then
    i3lock -c 16171d
elif command -v loginctl >/dev/null 2>&1; then
    loginctl lock-session
fi
