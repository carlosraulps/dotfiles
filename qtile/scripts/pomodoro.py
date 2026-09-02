#!/usr/bin/env python3
"""
Advanced Pomodoro & Productivity Timer Suite for Qtile
Features:
- Rofi Spotlight Popup Controller (Deep Study, Break, Sprint, Custom)
- Pango Markup live status for Qtile Bar
- Resilient timestamp calculations (immune to sleep/freeze drift)
- Desktop notifications via notify-send + audio chime via canberra-gtk-play
- Daily session tracking & stats
"""

import os
import sys
import time
import json
import subprocess

CACHE_DIR = os.path.expanduser("~/.cache")
STATE_FILE = os.path.join(CACHE_DIR, "qtile_pomodoro.json")
THEME_FILE = os.path.expanduser("~/.config/rofi/themes/spotlight-dark.rasi")

# OneDark Color Palette
COLOR_STUDY = "#98c379"    # Green
COLOR_BREAK = "#e5c07b"    # Yellow/Amber
COLOR_PAUSED = "#e06c75"   # Red
COLOR_IDLE = "#5c6370"     # Dim Grey
COLOR_ACCENT = "#61afef"   # Cyan/Blue


def get_default_state():
    return {
        "status": "idle",             # "running", "paused", "idle"
        "mode_type": "none",          # "study", "break", "none"
        "mode_name": "Idle",
        "total_seconds": 0,
        "target_timestamp": 0,
        "remaining_seconds": 0,
        "completed_today": 0,
        "last_date": time.strftime("%Y-%m-%d"),
        "notified": False,
    }


def load_state():
    os.makedirs(CACHE_DIR, exist_ok=True)
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                state = json.load(f)
                # Reset counter if date changed
                today = time.strftime("%Y-%m-%d")
                if state.get("last_date") != today:
                    state["completed_today"] = 0
                    state["last_date"] = today
                return state
        except Exception:
            pass
    return get_default_state()


def save_state(state):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def send_notification(title, message, urgency="normal"):
    try:
        subprocess.Popen([
            "notify-send",
            "-u", urgency,
            "-a", "Pomodoro Timer",
            "-i", "alarm",
            title,
            message
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

    try:
        # Play subtle audio alert
        subprocess.Popen(["canberra-gtk-play", "-i", "complete"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def update_and_get_remaining(state):
    if state["status"] == "running":
        remaining = int(state["target_timestamp"] - time.time())
        if remaining <= 0:
            # Timer finished!
            if not state.get("notified", False):
                state["notified"] = True
                if state["mode_type"] == "study":
                    state["completed_today"] = state.get("completed_today", 0) + 1
                    send_notification(
                        "🧠 Study Session Complete!",
                        f"Great work! Completed session: {state['mode_name']}.\nTime for a well-deserved break! (Total today: {state['completed_today']})",
                        urgency="critical"
                    )
                else:
                    send_notification(
                        "☕ Break Time Ended!",
                        f"Break finished ({state['mode_name']}). Ready to refocus?",
                        urgency="normal"
                    )
            state["status"] = "idle"
            state["remaining_seconds"] = 0
            save_state(state)
            return 0
        state["remaining_seconds"] = remaining
        return remaining
    elif state["status"] == "paused":
        return state.get("remaining_seconds", 0)
    return 0


def format_time(seconds):
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"


def get_bar_text():
    state = load_state()
    remaining = update_and_get_remaining(state)

    if state["status"] == "running":
        time_str = format_time(remaining)
        if state["mode_type"] == "study":
            return f'<span foreground="{COLOR_STUDY}">󱎫 {time_str}</span>'
        else:
            return f'<span foreground="{COLOR_BREAK}">󰏤 {time_str}</span>'
    elif state["status"] == "paused":
        time_str = format_time(state.get("remaining_seconds", 0))
        return f'<span foreground="{COLOR_PAUSED}">󰏥 {time_str}</span>'
    else:
        completed = state.get("completed_today", 0)
        badge = f" ({completed})" if completed > 0 else ""
        return f'<span foreground="{COLOR_IDLE}">25m{badge}</span>'


def start_timer(minutes, mode_type, mode_name):
    state = load_state()
    seconds = int(minutes * 60)
    state["status"] = "running"
    state["mode_type"] = mode_type
    state["mode_name"] = mode_name
    state["total_seconds"] = seconds
    state["target_timestamp"] = time.time() + seconds
    state["remaining_seconds"] = seconds
    state["notified"] = False
    save_state(state)

    send_notification(
        f"⏱️ Started: {mode_name}",
        f"Timer set for {minutes} minutes. Stay in the zone!"
    )


def toggle_pause():
    state = load_state()
    if state["status"] == "running":
        remaining = int(state["target_timestamp"] - time.time())
        if remaining > 0:
            state["status"] = "paused"
            state["remaining_seconds"] = remaining
            save_state(state)
            send_notification("⏸️ Timer Paused", f"Paused at {format_time(remaining)} remaining.")
    elif state["status"] == "paused":
        remaining = state.get("remaining_seconds", 0)
        if remaining > 0:
            state["status"] = "running"
            state["target_timestamp"] = time.time() + remaining
            save_state(state)
            send_notification("▶️ Timer Resumed", f"Resuming {state['mode_name']} ({format_time(remaining)} left).")


def reset_timer():
    state = load_state()
    state["status"] = "idle"
    state["remaining_seconds"] = 0
    state["target_timestamp"] = 0
    save_state(state)
    send_notification("⏹️ Pomodoro Reset", "Timer cancelled and reset to idle.")


def prompt_custom_timer():
    cmd = [
        "rofi",
        "-dmenu",
        "-p", "⏱️ Enter Minutes:",
        "-lines", "0",
    ]
    if os.path.exists(THEME_FILE):
        cmd.extend(["-theme", THEME_FILE])

    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        out, _ = proc.communicate(input="")
        val = out.strip()
        if val.isdigit():
            mins = int(val)
            if mins > 0:
                start_timer(mins, "study", f"Custom ({mins}m)")
    except Exception:
        pass


def open_rofi_menu():
    state = load_state()
    remaining = update_and_get_remaining(state)
    completed = state.get("completed_today", 0)

    # Active status header
    if state["status"] == "running":
        status_line = f"🟢 ACTIVE: {state['mode_name']} ({format_time(remaining)} left)"
        pause_action = "⏸️  Pause Active Timer"
    elif state["status"] == "paused":
        status_line = f"🟡 PAUSED: {state['mode_name']} ({format_time(state['remaining_seconds'])} left)"
        pause_action = "▶️  Resume Active Timer"
    else:
        status_line = "⚪ IDLE: Ready to start a session"
        pause_action = "▶️  Start Default (25 min Focus)"

    options = [
        f"📊 {status_line}",
        "🧠 45 min — Deep Study & Research",
        "🍅 25 min — Classic Pomodoro Session",
        "⚡ 50 min — Ultra Flow Sprint",
        "☕ 15 min — Rest & Coffee Break",
        "🧘 5 min — Quick Eye & Posture Break",
        "󰔛 Custom Timer... (Enter any minutes)",
        pause_action,
        "⏹️  Reset / Cancel Current Timer",
        f"🏆 Score: {completed} Sessions Completed Today",
    ]

    menu_text = "\n".join(options)
    cmd = [
        "rofi",
        "-dmenu",
        "-i",
        "-p", "🍅 Pomodoro Menu",
        "-lines", str(len(options)),
    ]
    if os.path.exists(THEME_FILE):
        cmd.extend(["-theme", THEME_FILE])

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    selected, _ = proc.communicate(input=menu_text)
    choice = selected.strip()

    if not choice:
        return

    if "45 min" in choice:
        start_timer(45, "study", "Deep Study (45m)")
    elif "25 min" in choice:
        start_timer(25, "study", "Classic Pomodoro (25m)")
    elif "50 min" in choice:
        start_timer(50, "study", "Ultra Sprint (50m)")
    elif "15 min" in choice:
        start_timer(15, "break", "Coffee Break (15m)")
    elif "5 min" in choice:
        start_timer(5, "break", "Quick Stretch (5m)")
    elif "Custom Timer" in choice:
        prompt_custom_timer()
    elif "Pause" in choice or "Resume" in choice:
        toggle_pause()
    elif "Start Default" in choice:
        start_timer(25, "study", "Classic Pomodoro (25m)")
    elif "Reset" in choice:
        reset_timer()


def main():
    if len(sys.argv) < 2 or sys.argv[1] == "status":
        print(get_bar_text())
    elif sys.argv[1] == "menu":
        open_rofi_menu()
    elif sys.argv[1] == "toggle":
        toggle_pause()
    elif sys.argv[1] == "reset":
        reset_timer()
    elif sys.argv[1] == "start":
        if len(sys.argv) >= 4:
            mins = float(sys.argv[2])
            mtype = sys.argv[3]
            mname = sys.argv[4] if len(sys.argv) >= 5 else f"{mins}m"
            start_timer(mins, mtype, mname)


if __name__ == "__main__":
    main()
