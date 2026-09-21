#!/usr/bin/env python3
# ==============================================================================
#  term_archive_menu.py — Rofi Search & Restore for Archived Terminals
# ==============================================================================

import os
import subprocess
import sys

ROFI_THEME = os.path.expanduser("~/.config/rofi/themes/spotlight-dark.rasi")

def get_archived_windows():
    try:
        out = subprocess.check_output(
            ["tmux", "list-windows", "-t", "archive", "-F", "#{window_id}|#{window_name}|#{pane_current_command}|#{pane_current_path}|#{pane_pid}"],
            stderr=subprocess.DEVNULL,
            text=True
        )
    except Exception:
        return []

    windows = []
    for line in out.strip().splitlines():
        if not line:
            continue
        parts = line.split("|")
        if len(parts) != 5:
            continue
        wid, name, cmd, cwd, pid = parts
        cwd_short = cwd.replace(os.path.expanduser("~"), "~")
        
        # Check active child process
        status = "idle"
        if pid and pid.isdigit():
            res = subprocess.run(["pgrep", "-P", pid, "-a"], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                first_child = res.stdout.strip().splitlines()[0]
                proc_name = first_child.split(" ", 1)[-1][:35]
                status = f"RUNNING: {proc_name}"

        label = f"[{cmd}]  {cwd_short}  ({status})"
        windows.append((wid, label))
    return windows

def main():
    windows = get_archived_windows()
    if not windows:
        subprocess.run(["notify-send", "-a", "Tmux Archive", "Terminal Archive", "No archived terminal sessions found."])
        return

    # Build menu items
    menu_items = [f"{wid}  │  {label}" for wid, label in windows]
    input_text = "\n".join(menu_items)

    rofi_cmd = ["rofi", "-dmenu", "-i", "-p", "Archived Terminals"]
    if os.path.exists(ROFI_THEME):
        rofi_cmd.extend(["-theme", ROFI_THEME])

    proc = subprocess.Popen(rofi_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    selected, _ = proc.communicate(input=input_text)

    if not selected or not selected.strip():
        return

    selected_wid = selected.split("│")[0].strip()
    if not selected_wid.startswith("@"):
        return

    # Move window from archive back to base
    subprocess.run(["tmux", "move-window", "-s", f"archive:{selected_wid}", "-t", "base:"], stderr=subprocess.DEVNULL)

    # Spawn terminal on current workspace attached to restored window
    spawn_script = os.path.expanduser("~/.config/qtile/scripts/spawn_term.sh")
    subprocess.Popen([spawn_script, selected_wid])

if __name__ == "__main__":
    main()
