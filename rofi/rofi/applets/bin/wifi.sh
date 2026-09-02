#!/usr/bin/env bash

## Rofi WiFi Applet (using nmcli)

# Theme
theme="$HOME/.config/rofi/applets/type-1/style-1.rasi"
[ -f "$theme" ] || theme="$HOME/.config/rofi/launchers/type-2/style-15.rasi"

# Notify
notify() {
    if command -v dunstify >/dev/null 2>&1; then
        dunstify -u normal -i network-wireless "Wi-Fi" "$1"
    fi
}

# Check Wi-Fi state
wifi_state=$(nmcli -fields WIFI g | sed 1d | tr -d '[:space:]')

if [ "$wifi_state" =~ "enabled" ] || [ "$wifi_state" = "enabled" ]; then
    toggle="󰖪  Disable Wi-Fi"
else
    toggle="󰖩  Enable Wi-Fi"
fi

# List Wi-Fi networks
scan_wifi() {
    nmcli --fields "IN-USE,SSID,BARS,SECURITY" device wifi list --rescan yes | \
    sed 1d | \
    sed 's/^/*/g' | \
    awk -F'  +' '{
        in_use = ($1 ~ /\*/) ? "󰄲 " : "  ";
        ssid = $2;
        bars = $3;
        sec = ($4 != "--" && $4 != "") ? "" : "";
        if (ssid != "" && ssid != "--") {
            printf "%s %s  %s  %s\n", in_use, bars, sec, ssid;
        }
    }' | uniq
}

# Run Rofi Menu
chosen=$(echo -e "$toggle\n$(scan_wifi)" | rofi -dmenu -p "󰖩 Wi-Fi" -theme "$theme")

[ -z "$chosen" ] && exit 0

if [ "$chosen" = "$toggle" ]; then
    if [ "$wifi_state" = "enabled" ]; then
        nmcli radio wifi off
        notify "Wi-Fi Disabled"
    else
        nmcli radio wifi on
        notify "Wi-Fi Enabled"
    fi
    exit 0
fi

# Extract SSID
selected_ssid=$(echo "$chosen" | awk '{print $4}' | sed 's/^[ \t]*//;s/[ \t]*$//')
[ -z "$selected_ssid" ] && selected_ssid=$(echo "$chosen" | sed 's/^.*  //')

# Check if connection already exists
if nmcli connection show "$selected_ssid" >/dev/null 2>&1; then
    notify "Connecting to $selected_ssid..."
    if nmcli connection up "$selected_ssid"; then
        notify "Connected to $selected_ssid"
    else
        notify "Failed to connect to $selected_ssid"
    fi
else
    # Prompt password if secured
    if echo "$chosen" | grep -q ""; then
        password=$(rofi -dmenu -password -p "Password for $selected_ssid" -theme "$theme")
        [ -z "$password" ] && exit 0
        notify "Connecting to $selected_ssid..."
        if nmcli device wifi connect "$selected_ssid" password "$password"; then
            notify "Connected to $selected_ssid"
        else
            notify "Failed to connect to $selected_ssid"
        fi
    else
        notify "Connecting to $selected_ssid..."
        if nmcli device wifi connect "$selected_ssid"; then
            notify "Connected to $selected_ssid"
        else
            notify "Failed to connect to $selected_ssid"
        fi
    fi
fi
