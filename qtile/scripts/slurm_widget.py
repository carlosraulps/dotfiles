#!/usr/bin/env python3
"""
Multi-Cluster Slurm Queue Monitor Widget for Qtile Bar
Displays live active RUNNING jobs across Arch, Carbono, and Iskay clusters.
"""

import os
import json
import time
import subprocess
import shutil

STATE_FILE = "/home/cr/simulations/server-notification/data/multi_cluster_jobs.json"
SQUEUE_PATH = shutil.which("squeue") or "/usr/bin/squeue"


def get_local_running_jobs():
    """Queries local Slurm for running jobs on Arch."""
    if not os.path.exists(SQUEUE_PATH):
        return []
    try:
        res = subprocess.run(
            [SQUEUE_PATH, "-h", "-t", "R", "-o", "%i|%j|%M|%N"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=1.0
        )
        if res.returncode == 0 and res.stdout.strip():
            jobs = []
            for line in res.stdout.strip().splitlines():
                parts = line.strip().split("|")
                if len(parts) >= 2:
                    jobs.append({
                        "id": parts[0],
                        "name": parts[1],
                        "time": parts[2] if len(parts) > 2 else "",
                        "node": parts[3] if len(parts) > 3 else "",
                        "cluster": "arch"
                    })
            return jobs
    except Exception:
        pass
    return []


def get_carbono_running_jobs():
    """Queries Carbono directly if state file is missing or empty."""
    try:
        res = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=1", "carbono", "squeue -u carlos.primo -h -t R -o '%i|%j|%u|%M|%N|%P'"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=2.0
        )
        if res.returncode == 0 and res.stdout.strip():
            jobs = []
            for line in res.stdout.strip().splitlines():
                parts = line.strip().split("|")
                if len(parts) >= 2:
                    jobs.append({
                        "id": parts[0],
                        "name": parts[1],
                        "user": parts[2] if len(parts) > 2 else "carlos.primo",
                        "time": parts[3] if len(parts) > 3 else "",
                        "node": parts[4] if len(parts) > 4 else "",
                        "partition": parts[5] if len(parts) > 5 else "",
                        "cluster": "carbono",
                        "state": "RUNNING"
                    })
            return jobs
    except Exception:
        pass
    return []


def get_huk_running_jobs():
    """Queries Huk directly if persistent ControlMaster socket is active."""
    ssh_dir = os.path.expanduser("~/.ssh")
    sock_found = False
    try:
        for fname in os.listdir(ssh_dir):
            if fname.startswith("cm-") and ("huk" in fname or "192.168.16.100" in fname):
                sock_found = True
                break
    except Exception:
        pass

    if not sock_found:
        return []

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
            jobs = []
            for line in res.stdout.strip().splitlines():
                parts = line.strip().split("|")
                if len(parts) >= 2:
                    jobs.append({
                        "id": parts[0],
                        "name": parts[1],
                        "user": parts[2] if len(parts) > 2 else "carlos",
                        "time": parts[3] if len(parts) > 3 else "",
                        "node": parts[4] if len(parts) > 4 else "huk",
                        "partition": parts[5] if len(parts) > 5 else "batch",
                        "cluster": "huk",
                        "state": "RUNNING"
                    })
            return jobs
    except Exception:
        pass
    return []


def get_multi_cluster_data():
    """Reads multi-cluster telemetry file or falls back to direct check."""
    data = {
        "arch": [],
        "carbono": [],
        "iskay": [],
        "huk": []
    }

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

    # Always ensure local Arch jobs are fresh from local squeue
    local_arch = get_local_running_jobs()
    if local_arch or not data["arch"]:
        data["arch"] = local_arch

    # Direct Carbono check fallback if empty in state
    if not data["carbono"]:
        direct_carb = get_carbono_running_jobs()
        if direct_carb:
            data["carbono"] = direct_carb

    # Direct Huk check fallback if empty in state
    if not data["huk"]:
        direct_huk = get_huk_running_jobs()
        if direct_huk:
            data["huk"] = direct_huk

    return data


def get_running_jobs_text():
    """Returns compact Pango markup for Qtile bar showing running jobs across clusters."""
    try:
        data = get_multi_cluster_data()
        arch_jobs = data.get("arch", [])
        carb_jobs = data.get("carbono", [])
        iskay_jobs = data.get("iskay", [])
        huk_jobs = data.get("huk", [])

        arch_count = len(arch_jobs)
        carb_count = len(carb_jobs)
        iskay_count = len(iskay_jobs)
        huk_count = len(huk_jobs)
        total = arch_count + carb_count + iskay_count + huk_count

        if total == 0:
            return "<span foreground='#6272a4'>0 Running</span>"

        parts = []

        # Arch (Local)
        if arch_count > 0:
            name = arch_jobs[0].get("name", "job")
            if len(name) > 10:
                name = name[:8] + ".."
            if arch_count == 1:
                parts.append(f"<span foreground='#50fa7b'><b>Arch: 1</b></span> <span foreground='#cfd8e6'>({name})</span>")
            else:
                parts.append(f"<span foreground='#50fa7b'><b>Arch: {arch_count}R</b></span>")
        else:
            parts.append("<span foreground='#6272a4'>Arch: 0</span>")

        # Carbono
        if carb_count > 0:
            name = carb_jobs[0].get("name", "job")
            if len(name) > 10:
                name = name[:8] + ".."
            if carb_count == 1:
                parts.append(f"<span foreground='#ffb86c'><b>Carb: 1</b></span> <span foreground='#cfd8e6'>({name})</span>")
            else:
                parts.append(f"<span foreground='#ffb86c'><b>Carb: {carb_count}R</b></span>")
        else:
            parts.append("<span foreground='#6272a4'>Carb: 0</span>")

        # Iskay
        if iskay_count > 0:
            name = iskay_jobs[0].get("name", "job")
            if len(name) > 10:
                name = name[:8] + ".."
            if iskay_count == 1:
                parts.append(f"<span foreground='#bd93f9'><b>Iskay: 1</b></span> <span foreground='#cfd8e6'>({name})</span>")
            else:
                parts.append(f"<span foreground='#bd93f9'><b>Iskay: {iskay_count}R</b></span>")
        else:
            parts.append("<span foreground='#6272a4'>Iskay: 0</span>")

        # Huk
        if huk_count > 0:
            name = huk_jobs[0].get("name", "job")
            if len(name) > 10:
                name = name[:8] + ".."
            if huk_count == 1:
                parts.append(f"<span foreground='#8be9fd'><b>Huk: 1</b></span> <span foreground='#cfd8e6'>({name})</span>")
            else:
                parts.append(f"<span foreground='#8be9fd'><b>Huk: {huk_count}R</b></span>")
        else:
            parts.append("<span foreground='#6272a4'>Huk: 0</span>")

        # If only one cluster is active, show it highlighted alongside the idle counts
        return " <span foreground='#44475a'>|</span> ".join(parts)

    except Exception as e:
        return f"<span foreground='#ff5555'>Slurm Err: {str(e)[:15]}</span>"


if __name__ == "__main__":
    print(get_running_jobs_text())
