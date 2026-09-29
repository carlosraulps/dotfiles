#!/usr/bin/env python3
"""
Interactive Multi-Cluster Slurm Watcher for Terminal / Alacritty
Monitors active RUNNING and QUEUED/PENDING jobs across Arch, Carbono, Iskay, and Huk in real-time.
"""

import os
import sys
import time
import json
import curses
import subprocess
import shutil
import datetime

STATE_FILE = "/home/cr/simulations/server-notification/data/multi_cluster_jobs.json"
SQUEUE_PATH = shutil.which("squeue") or "/usr/bin/squeue"


def compute_queued_time(submit_str):
    """Calculates human-readable elapsed queue time from submission timestamp."""
    if not submit_str or submit_str in ("N/A", "Unknown", "None", ""):
        return "-"
    try:
        clean_str = submit_str.replace("T", " ")
        dt = datetime.datetime.fromisoformat(clean_str)
        diff = datetime.datetime.now() - dt
        secs = max(0, int(diff.total_seconds()))
        d = secs // 86400
        h = (secs % 86400) // 3600
        m = (secs % 3600) // 60
        s = secs % 60
        if d > 0:
            return f"{d}d {h:02d}h"
        elif h > 0:
            return f"{h}h {m:02d}m"
        elif m > 0:
            return f"{m}m {s:02d}s"
        else:
            return f"{s}s"
    except Exception:
        return submit_str[:8]


def format_est_start(start_str):
    """Formats estimated start time cleanly (e.g. HH:MM:SS or +1d HH:MM)."""
    if not start_str or start_str in ("N/A", "None", "Unknown", ""):
        return "N/A"
    try:
        clean_str = start_str.replace("T", " ")
        dt = datetime.datetime.fromisoformat(clean_str)
        now = datetime.datetime.now()
        if dt.date() == now.date():
            return dt.strftime("%H:%M:%S")
        elif dt.date() == (now + datetime.timedelta(days=1)).date():
            return "+1d " + dt.strftime("%H:%M")
        else:
            return dt.strftime("%b %d %H:%M")
    except Exception:
        return start_str[:12]


def get_data():
    """Retrieves both RUNNING and PENDING jobs across monitored clusters."""
    running_data = {"arch": [], "carbono": [], "iskay": [], "huk": []}
    pending_data = {"arch": [], "carbono": [], "iskay": [], "huk": []}

    # 1. State cache from background notification daemon (bot.service)
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                raw = json.load(f)
                clusters = raw.get("clusters", {})
                for c in ["arch", "carbono", "iskay", "huk"]:
                    if c in clusters:
                        running_data[c] = clusters[c]
                pending_clusters = raw.get("pending_clusters", {})
                for c in ["arch", "carbono", "iskay", "huk"]:
                    if c in pending_clusters:
                        pending_data[c] = pending_clusters[c]
        except Exception:
            pass

    # 2. Augment local Arch (real-time authority <5ms)
    if os.path.exists(SQUEUE_PATH):
        try:
            res = subprocess.run(
                [SQUEUE_PATH, "-h", "-o", "%i|%j|%u|%T|%M|%l|%N|%P|%r|%V|%S"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=0.8
            )
            if res.returncode == 0 and res.stdout.strip():
                arch_running = []
                arch_pending = []
                for line in res.stdout.strip().splitlines():
                    p = line.strip().split("|")
                    if len(p) >= 8:
                        entry = {
                            "id": p[0],
                            "name": p[1],
                            "user": p[2],
                            "state": p[3],
                            "time": p[4],
                            "limit": p[5],
                            "node": p[6],
                            "partition": p[7],
                            "reason": p[8] if len(p) > 8 else "None",
                            "submit_time": p[9] if len(p) > 9 else "",
                            "start_time": p[10] if len(p) > 10 else "",
                            "cluster": "arch"
                        }
                        if entry["state"] == "RUNNING":
                            arch_running.append(entry)
                        elif entry["state"] == "PENDING":
                            arch_pending.append(entry)
                running_data["arch"] = arch_running
                pending_data["arch"] = arch_pending
        except Exception:
            pass

    # 3. Direct Carbono check fallback if state file was empty
    if not running_data["carbono"] and not pending_data["carbono"]:
        try:
            res = subprocess.run(
                ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=1", "carbono", "squeue -u carlos.primo -h -o '%i|%j|%u|%T|%M|%l|%N|%P|%r|%V|%S'"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=2.0
            )
            if res.returncode == 0 and res.stdout.strip():
                carb_running = []
                carb_pending = []
                for line in res.stdout.strip().splitlines():
                    p = line.strip().split("|")
                    if len(p) >= 8:
                        entry = {
                            "id": p[0],
                            "name": p[1],
                            "user": p[2],
                            "state": p[3],
                            "time": p[4],
                            "limit": p[5],
                            "node": p[6],
                            "partition": p[7],
                            "reason": p[8] if len(p) > 8 else "None",
                            "submit_time": p[9] if len(p) > 9 else "",
                            "start_time": p[10] if len(p) > 10 else "",
                            "cluster": "carbono"
                        }
                        if entry["state"] == "RUNNING":
                            carb_running.append(entry)
                        elif entry["state"] == "PENDING":
                            carb_pending.append(entry)
                running_data["carbono"] = carb_running
                pending_data["carbono"] = carb_pending
        except Exception:
            pass

    # 4. Direct Huk check fallback if state file was empty and ControlMaster socket is active
    if not running_data["huk"] and not pending_data["huk"]:
        ssh_dir = os.path.expanduser("~/.ssh")
        sock_found = False
        try:
            for fname in os.listdir(ssh_dir):
                if fname.startswith("cm-") and ("huk" in fname or "192.168.16.100" in fname):
                    sock_found = True
                    break
        except Exception:
            pass

        if sock_found:
            try:
                res = subprocess.run(
                    ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=1", "huk", "squeue -u carlos -h -o '%i|%j|%u|%T|%M|%l|%N|%P|%r|%V|%S'"],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=2.0
                )
                if res.returncode == 0 and res.stdout.strip():
                    huk_running = []
                    huk_pending = []
                    for line in res.stdout.strip().splitlines():
                        p = line.strip().split("|")
                        if len(p) >= 8:
                            entry = {
                                "id": p[0],
                                "name": p[1],
                                "user": p[2],
                                "state": p[3],
                                "time": p[4],
                                "limit": p[5],
                                "node": p[6],
                                "partition": p[7],
                                "reason": p[8] if len(p) > 8 else "None",
                                "submit_time": p[9] if len(p) > 9 else "",
                                "start_time": p[10] if len(p) > 10 else "",
                                "cluster": "huk"
                            }
                            if entry["state"] == "RUNNING":
                                huk_running.append(entry)
                            elif entry["state"] == "PENDING":
                                huk_pending.append(entry)
                    running_data["huk"] = huk_running
                    pending_data["huk"] = huk_pending
            except Exception:
                pass

    return running_data, pending_data


def draw_ui(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(1000)

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)   # Arch
    curses.init_pair(2, curses.COLOR_YELLOW, -1)  # Carbono
    curses.init_pair(3, curses.COLOR_MAGENTA, -1) # Iskay
    curses.init_pair(4, curses.COLOR_CYAN, -1)    # Headers & Accents
    curses.init_pair(5, curses.COLOR_WHITE, -1)   # Regular text
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_CYAN) # Inverted Top Banner
    curses.init_pair(7, curses.COLOR_BLUE, -1)    # Huk

    while True:
        try:
            key = stdscr.getch()
            if key in [ord('q'), ord('Q'), 27]: # q or ESC
                break

            stdscr.erase()
            h, w = stdscr.getmaxyx()
            now_str = time.strftime("%Y-%m-%d %H:%M:%S")

            # Header Banner
            title = f" 󰒋 Multi-Cluster Slurm Monitor · Active Running & Queued Jobs ({now_str}) "
            stdscr.attron(curses.color_pair(6) | curses.A_BOLD)
            stdscr.addstr(0, 0, title.ljust(w - 1)[:w - 1])
            stdscr.attroff(curses.color_pair(6) | curses.A_BOLD)

            running_data, pending_data = get_data()
            row = 2

            # Counts
            arch_r = len(running_data.get("arch", []))
            carb_r = len(running_data.get("carbono", []))
            iskay_r = len(running_data.get("iskay", []))
            huk_r = len(running_data.get("huk", []))
            total_r = arch_r + carb_r + iskay_r + huk_r

            arch_p = len(pending_data.get("arch", []))
            carb_p = len(pending_data.get("carbono", []))
            iskay_p = len(pending_data.get("iskay", []))
            huk_p = len(pending_data.get("huk", []))
            total_p = arch_p + carb_p + iskay_p + huk_p

            # Summary Bar
            summary_str = (
                f"Running ({total_r}): Arch: {arch_r}  Carb: {carb_r}  Iskay: {iskay_r}  Huk: {huk_r}   │   "
                f"Queued ({total_p}): Arch: {arch_p}  Carb: {carb_p}  Iskay: {iskay_p}  Huk: {huk_p}"
            )
            if row < h - 1:
                stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
                stdscr.addstr(row, 2, summary_str[:w - 4])
                stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
            row += 2

            # ----------------------------------------------------
            # 1. RUNNING JOBS TABLE
            # ----------------------------------------------------
            cluster_configs_running = [
                ("ARCH", running_data.get("arch", []), 1),
                ("CARBONO", running_data.get("carbono", []), 2),
                ("ISKAY", running_data.get("iskay", []), 3),
                ("HUK", running_data.get("huk", []), 7),
            ]

            if row < h - 4:
                stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
                stdscr.addstr(row, 2, f"▶ ACTIVE RUNNING JOBS ({total_r})")
                stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
                row += 1

            if row < h - 4:
                hdr_r = f"{'CLUSTER':<10} {'JOBID':<10} {'NAME':<18} {'USER':<14} {'NODE':<10} {'PARTITION':<11} {'ELAPSED':<11} {'STATE':<10}"
                stdscr.attron(curses.color_pair(4) | curses.A_UNDERLINE)
                stdscr.addstr(row, 2, hdr_r[:w - 4])
                stdscr.attroff(curses.color_pair(4) | curses.A_UNDERLINE)
                row += 1

            rendered_running = False
            for cname, jobs, color_id in cluster_configs_running:
                for j in jobs:
                    if row >= h - 5:
                        break
                    rendered_running = True
                    jid = str(j.get("id", "-"))
                    name = str(j.get("name", "-"))[:16]
                    user = str(j.get("user", "-"))[:13]
                    node = str(j.get("node", "-"))[:10]
                    part = str(j.get("partition", "-"))[:10]
                    elapsed = str(j.get("time", "-"))[:10]
                    state = str(j.get("state", "RUNNING"))[:9]

                    line = f"{cname:<10} {jid:<10} {name:<18} {user:<14} {node:<10} {part:<11} {elapsed:<11} {state:<10}"
                    stdscr.attron(curses.color_pair(color_id))
                    stdscr.addstr(row, 2, line[:w - 4])
                    stdscr.attroff(curses.color_pair(color_id))
                    row += 1

            if not rendered_running and row < h - 4:
                stdscr.attron(curses.color_pair(5))
                stdscr.addstr(row, 4, "🟢 No active running jobs detected on monitored clusters.")
                stdscr.attroff(curses.color_pair(5))
                row += 1

            row += 1 # Space between tables

            # ----------------------------------------------------
            # 2. QUEUED / PENDING JOBS TABLE
            # ----------------------------------------------------
            cluster_configs_pending = [
                ("ARCH", pending_data.get("arch", []), 1),
                ("CARBONO", pending_data.get("carbono", []), 2),
                ("ISKAY", pending_data.get("iskay", []), 3),
                ("HUK", pending_data.get("huk", []), 7),
            ]

            if row < h - 3:
                stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
                stdscr.addstr(row, 2, f"▶ QUEUED / PENDING JOBS ({total_p} Waiting in Queue)")
                stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
                row += 1

            if row < h - 3:
                hdr_p = f"{'CLUSTER':<10} {'JOBID':<10} {'NAME':<18} {'USER':<14} {'PARTITION':<11} {'QUEUED':<10} {'TIME_LIMIT':<11} {'REASON':<24} {'EST_START':<12}"
                stdscr.attron(curses.color_pair(4) | curses.A_UNDERLINE)
                stdscr.addstr(row, 2, hdr_p[:w - 4])
                stdscr.attroff(curses.color_pair(4) | curses.A_UNDERLINE)
                row += 1

            rendered_pending = False
            for cname, jobs, color_id in cluster_configs_pending:
                for j in jobs:
                    if row >= h - 2:
                        break
                    rendered_pending = True
                    jid = str(j.get("id", "-"))
                    name = str(j.get("name", "-"))[:16]
                    user = str(j.get("user", "-"))[:13]
                    part = str(j.get("partition", "-"))[:10]
                    queued = compute_queued_time(j.get("submit_time", ""))[:9]
                    limit = str(j.get("limit", "-"))[:10]
                    reason = str(j.get("reason", "Pending"))[:23]
                    est_start = format_est_start(j.get("start_time", ""))[:12]

                    line = f"{cname:<10} {jid:<10} {name:<18} {user:<14} {part:<11} {queued:<10} {limit:<11} {reason:<24} {est_start:<12}"
                    stdscr.attron(curses.color_pair(color_id))
                    stdscr.addstr(row, 2, line[:w - 4])
                    stdscr.attroff(curses.color_pair(color_id))
                    row += 1

            if not rendered_pending and row < h - 2:
                stdscr.attron(curses.color_pair(5))
                stdscr.addstr(row, 4, "🟢 No queued jobs waiting in queue across monitored clusters.")
                stdscr.attroff(curses.color_pair(5))
                row += 1

            # ----------------------------------------------------
            # Footer
            # ----------------------------------------------------
            footer = " [q] Quit  |  [r] Refresh  |  Auto-refreshes live every 1s  |  Showing RUNNING & QUEUED jobs "
            if h > 1:
                stdscr.attron(curses.color_pair(4))
                stdscr.addstr(h - 1, 0, footer.ljust(w - 1)[:w - 1])
                stdscr.attroff(curses.color_pair(4))

            stdscr.refresh()
        except Exception:
            pass


def main():
    try:
        curses.wrapper(draw_ui)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
