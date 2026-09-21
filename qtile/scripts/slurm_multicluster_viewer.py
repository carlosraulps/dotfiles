#!/usr/bin/env python3
"""
Interactive Multi-Cluster Slurm Watcher for Terminal / Alacritty
Monitors active RUNNING jobs across Arch, Carbono, and Iskay in real-time.
"""

import os
import sys
import time
import json
import curses
import subprocess
import shutil

STATE_FILE = "/home/cr/simulations/server-notification/data/multi_cluster_jobs.json"
SQUEUE_PATH = shutil.which("squeue") or "/usr/bin/squeue"


def get_data():
    data = {"arch": [], "carbono": [], "iskay": [], "huk": []}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                raw = json.load(f)
                clusters = raw.get("clusters", {})
                for c in ["arch", "carbono", "iskay", "huk"]:
                    if c in clusters:
                        data[c] = clusters[c]
        except Exception:
            pass

    # Augment local Arch
    if os.path.exists(SQUEUE_PATH):
        try:
            res = subprocess.run(
                [SQUEUE_PATH, "-h", "-t", "R", "-o", "%i|%j|%u|%M|%N|%P"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=1.0
            )
            if res.returncode == 0 and res.stdout.strip():
                arch_jobs = []
                for line in res.stdout.strip().splitlines():
                    p = line.strip().split("|")
                    if len(p) >= 2:
                        arch_jobs.append({
                            "id": p[0],
                            "name": p[1],
                            "user": p[2] if len(p) > 2 else "cr",
                            "time": p[3] if len(p) > 3 else "0:00",
                            "node": p[4] if len(p) > 4 else "local",
                            "partition": p[5] if len(p) > 5 else "batch",
                            "cluster": "arch",
                            "state": "RUNNING"
                        })
                data["arch"] = arch_jobs
        except Exception:
            pass

    # Direct Carbono check fallback if empty in state
    if not data["carbono"]:
        try:
            res = subprocess.run(
                ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=1", "carbono", "squeue -u carlos.primo -h -t R -o '%i|%j|%u|%M|%N|%P'"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=2.0
            )
            if res.returncode == 0 and res.stdout.strip():
                carb_jobs = []
                for line in res.stdout.strip().splitlines():
                    p = line.strip().split("|")
                    if len(p) >= 2:
                        carb_jobs.append({
                            "id": p[0],
                            "name": p[1],
                            "user": p[2] if len(p) > 2 else "carlos.primo",
                            "time": p[3] if len(p) > 3 else "0:00",
                            "node": p[4] if len(p) > 4 else "n02",
                            "partition": p[5] if len(p) > 5 else "fulereno",
                            "cluster": "carbono",
                            "state": "RUNNING"
                        })
                data["carbono"] = carb_jobs
        except Exception:
            pass

    # Direct Huk check fallback if empty in state and ControlMaster socket is active
    if not data["huk"]:
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
                    ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=1", "huk", "squeue -u carlos -h -t R -o '%i|%j|%u|%M|%N|%P'"],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=2.0
                )
                if res.returncode == 0 and res.stdout.strip():
                    huk_jobs = []
                    for line in res.stdout.strip().splitlines():
                        p = line.strip().split("|")
                        if len(p) >= 2:
                            huk_jobs.append({
                                "id": p[0],
                                "name": p[1],
                                "user": p[2] if len(p) > 2 else "carlos",
                                "time": p[3] if len(p) > 3 else "0:00",
                                "node": p[4] if len(p) > 4 else "huk",
                                "partition": p[5] if len(p) > 5 else "batch",
                                "cluster": "huk",
                                "state": "RUNNING"
                            })
                    data["huk"] = huk_jobs
            except Exception:
                pass

    return data


def draw_ui(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(1000)

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)   # Arch / Running
    curses.init_pair(2, curses.COLOR_YELLOW, -1)  # Carbono
    curses.init_pair(3, curses.COLOR_MAGENTA, -1) # Iskay
    curses.init_pair(4, curses.COLOR_CYAN, -1)    # Headers
    curses.init_pair(5, curses.COLOR_WHITE, -1)   # Regular text
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_CYAN) # Inverted header
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
            title = f" 󰒋 Multi-Cluster Slurm Monitor · Watch Active Running Jobs ({now_str}) "
            stdscr.attron(curses.color_pair(6) | curses.A_BOLD)
            stdscr.addstr(0, 0, title.ljust(w - 1)[:w - 1])
            stdscr.attroff(curses.color_pair(6) | curses.A_BOLD)

            data = get_data()
            row = 2

            # Summary Bar
            arch_cnt = len(data.get("arch", []))
            carb_cnt = len(data.get("carbono", []))
            iskay_cnt = len(data.get("iskay", []))
            huk_cnt = len(data.get("huk", []))
            total_cnt = arch_cnt + carb_cnt + iskay_cnt + huk_cnt

            stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
            stdscr.addstr(row, 2, f"Total Running Jobs: {total_cnt}   │   Arch: {arch_cnt}   Carbono: {carb_cnt}   Iskay: {iskay_cnt}   Huk: {huk_cnt}")
            stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
            row += 2

            # Table Header
            hdr = f"{'CLUSTER':<10} {'JOBID':<10} {'NAME':<18} {'USER':<12} {'NODE':<12} {'PARTITION':<12} {'ELAPSED':<12} {'STATE':<10}"
            stdscr.attron(curses.color_pair(4) | curses.A_UNDERLINE)
            stdscr.addstr(row, 2, hdr[:w - 4])
            stdscr.attroff(curses.color_pair(4) | curses.A_UNDERLINE)
            row += 1

            # Job rows
            cluster_configs = [
                ("ARCH", data.get("arch", []), 1),
                ("CARBONO", data.get("carbono", []), 2),
                ("ISKAY", data.get("iskay", []), 3),
                ("HUK", data.get("huk", []), 7),
            ]

            rendered_any = False
            for cname, jobs, color_id in cluster_configs:
                for j in jobs:
                    if row >= h - 2:
                        break
                    rendered_any = True
                    jid = str(j.get("id", "-"))
                    name = str(j.get("name", "-"))[:16]
                    user = str(j.get("user", "-"))[:10]
                    node = str(j.get("node", "-"))[:10]
                    part = str(j.get("partition", "-"))[:10]
                    elapsed = str(j.get("time", "-"))[:10]
                    state = str(j.get("state", "RUNNING"))[:9]

                    line = f"{cname:<10} {jid:<10} {name:<18} {user:<12} {node:<12} {part:<12} {elapsed:<12} {state:<10}"
                    stdscr.attron(curses.color_pair(color_id))
                    stdscr.addstr(row, 2, line[:w - 4])
                    stdscr.attroff(curses.color_pair(color_id))
                    row += 1

            if not rendered_any:
                stdscr.attron(curses.color_pair(5))
                stdscr.addstr(row + 1, 4, "🟢 No active running jobs detected on monitored clusters.")
                stdscr.attroff(curses.color_pair(5))

            # Footer
            footer = " [q] Quit  |  Auto-refreshes every 1s  |  Showing RUNNING jobs only "
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
