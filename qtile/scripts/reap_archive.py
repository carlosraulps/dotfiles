#!/usr/bin/env python3
# ==============================================================================
#  reap_archive.py — Safe 7-Day Inactivity Reaper for Terminal Archive
# ==============================================================================

import os
import subprocess
import time

MAX_IDLE_SECONDS = 7 * 86400  # 7 days
MAX_IDLE_WINDOWS = 20         # Cap idle windows to prevent memory bloat

def reap():
    try:
        out = subprocess.check_output(
            ["tmux", "list-windows", "-t", "archive", "-F", "#{window_id}|#{window_activity}|#{pane_pid}"],
            stderr=subprocess.DEVNULL,
            text=True
        )
    except Exception:
        return

    now = int(time.time())
    idle_windows = []

    for line in out.strip().splitlines():
        if not line:
            continue
        parts = line.split("|")
        if len(parts) != 3:
            continue
        wid, activity_str, pid = parts
        
        # Check active child process: NEVER reap if computing / running jobs!
        has_children = False
        if pid and pid.isdigit():
            res = subprocess.run(["pgrep", "-P", pid], stdout=subprocess.DEVNULL)
            if res.returncode == 0:
                has_children = True

        if has_children:
            continue

        try:
            activity = int(activity_str)
        except ValueError:
            activity = now

        idle_age = now - activity
        idle_windows.append((wid, idle_age))

    # Sort idle windows by age (oldest first)
    idle_windows.sort(key=lambda x: x[1], reverse=True)

    reaped_count = 0
    for idx, (wid, idle_age) in enumerate(idle_windows):
        # Reap if older than 7 days, or if exceeding max pool cap
        if idle_age > MAX_IDLE_SECONDS or idx >= MAX_IDLE_WINDOWS:
            subprocess.run(["tmux", "kill-window", "-t", f"archive:{wid}"], stderr=subprocess.DEVNULL)
            reaped_count += 1

    if reaped_count > 0:
        print(f"Reaped {reaped_count} expired idle windows from archive.")

if __name__ == "__main__":
    reap()
