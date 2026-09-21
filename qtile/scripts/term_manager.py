#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

STATE_FILE = Path.home() / ".config" / "qtile" / "saved_terminals.json"

DEFAULT_LAYOUT = [
    {"workspace": "1", "class_instance": "qtile-term-ws1", "class_general": "qtile-term-ws1", "target": "1"},
    {"workspace": "2", "class_instance": "qtile-devterm-1", "class_general": "qtile-devterm", "target": "2"},
    {"workspace": "2", "class_instance": "qtile-devterm-2", "class_general": "qtile-devterm", "target": "3"},
    {"workspace": "4", "class_instance": "qtile-term-ws4", "class_general": "qtile-term-ws4", "target": "4"},
    {"workspace": "5", "class_instance": "qtile-term-ws5", "class_general": "qtile-term-ws5", "target": "5"},
]

# Map group names / labels to numeric workspace IDs
GROUP_MAP = {
    " 󰖟  ": "1",
    "   ": "2",
    "  ": "3",
    "   ": "4",
    "   ": "5",
}
REV_GROUP_MAP = {v: k for k, v in GROUP_MAP.items()}

def prune_dead_sessions():
    """Remove dead/unattached temporary grouped sessions (term-*) left over from crashes."""
    try:
        out = subprocess.check_output(
            ["tmux", "list-sessions", "-F", "#{session_name} #{session_attached}"],
            stderr=subprocess.DEVNULL,
            text=True
        )
        for line in out.strip().splitlines():
            parts = line.split()
            if len(parts) == 2:
                name, attached = parts[0], parts[1]
                if name.startswith("term-") and attached == "0":
                    subprocess.run(["tmux", "kill-session", "-t", name], stderr=subprocess.DEVNULL)
    except Exception:
        pass

def save():
    """Scan active Alacritty windows in Qtile and save a clean layout per workspace."""
    try:
        from libqtile.command.client import InteractiveCommandClient
        c = InteractiveCommandClient()
        windows = c.windows()
    except Exception as e:
        print(f"Could not connect to Qtile IPC: {e}", file=sys.stderr)
        return

    # Collect terminals grouped by workspace
    ws_terminals = {}

    for w in windows:
        classes = w.get("wm_class", [])
        if not any("alacritty" in cls.lower() or "qtile" in cls.lower() for cls in classes):
            continue

        group_name = w.get("group")
        ws = GROUP_MAP.get(group_name, "1")

        if ws not in ws_terminals:
            ws_terminals[ws] = []

        # Enforce reasonable caps: max 2 on WS2, max 1 on other workspaces
        max_allowed = 2 if ws == "2" else 1
        if len(ws_terminals[ws]) >= max_allowed:
            continue

        idx = len(ws_terminals[ws]) + 1
        if ws == "2":
            instance = f"qtile-devterm-{idx}"
            general = "qtile-devterm"
        else:
            instance = f"qtile-term-ws{ws}"
            general = f"qtile-term-ws{ws}"

        # Resolve target window from tmux if possible
        target = ws
        try:
            wid = w.get("id")
            xprop_out = subprocess.check_output(["xprop", "-id", str(wid), "_NET_WM_PID"], text=True)
            pid = xprop_out.strip().split("=")[-1].strip()
            if pid.isdigit():
                pstree = subprocess.check_output(["pstree", "-p", pid], text=True)
                m = re.search(r"tmux-smart-atta\((\d+)\)", pstree)
                if m:
                    atta_pid = m.group(1)
                    sess_out = subprocess.check_output(["tmux", "list-sessions", "-F", "#{session_name}"], text=True)
                    for s in sess_out.strip().splitlines():
                        if s.startswith(f"term-{atta_pid}-"):
                            win_idx = subprocess.check_output(
                                ["tmux", "display-message", "-p", "-t", s, "#{window_index}"],
                                text=True
                            ).strip()
                            if win_idx:
                                target = win_idx
                            break
        except Exception:
            pass

        ws_terminals[ws].append({
            "workspace": ws,
            "class_instance": instance,
            "class_general": general,
            "target": target,
        })

    # Flatten into list
    terminals = []
    for ws in sorted(ws_terminals.keys()):
        terminals.extend(ws_terminals[ws])

    if not terminals:
        return

    tmp_file = STATE_FILE.with_suffix(".tmp")
    try:
        with open(tmp_file, "w") as f:
            json.dump(terminals, f, indent=2)
        os.replace(tmp_file, STATE_FILE)
        print(f"Saved {len(terminals)} terminal viewports to {STATE_FILE}")
    except Exception as e:
        print(f"Failed to write state file: {e}", file=sys.stderr)

def restore():
    """Restore Alacritty terminals into their designated Qtile workspaces with strict deduplication."""
    # 1. Wait up to 3 seconds for tmux to initialize/resurrect
    for _ in range(30):
        if subprocess.run(["tmux", "has-session", "-t", "base"], stderr=subprocess.DEVNULL).returncode == 0:
            break
        time.sleep(0.1)

    # Ensure base session exists
    if subprocess.run(["tmux", "has-session", "-t", "base"], stderr=subprocess.DEVNULL).returncode != 0:
        subprocess.run(["tmux", "new-session", "-d", "-s", "base"], stderr=subprocess.DEVNULL)

    # 2. Prune old zombie grouped sessions
    prune_dead_sessions()

    # 3. Load layout
    layout = DEFAULT_LAYOUT
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                saved = json.load(f)
                if isinstance(saved, list) and len(saved) > 0:
                    layout = saved
        except Exception as e:
            print(f"Error loading {STATE_FILE}, using default: {e}", file=sys.stderr)

    # 4. Check which window classes are ALREADY active on the desktop via Qtile IPC
    existing_classes = set()
    try:
        from libqtile.command.client import InteractiveCommandClient
        c = InteractiveCommandClient()
        for w in c.windows():
            for cls in w.get("wm_class", []):
                existing_classes.add(cls)
    except Exception:
        pass

    # 5. Spawn each missing terminal
    for item in layout:
        instance = item.get("class_instance", "qtile-devterm")
        general = item.get("class_general", "qtile-devterm")
        target = str(item.get("target", "1"))

        # Skip if already open in Qtile
        if instance in existing_classes:
            print(f"Terminal {instance} already active in Qtile, skipping.")
            continue

        # Fallback check in process table
        check = subprocess.run(
            ["pgrep", "-f", f"alacritty.*{instance}"],
            stdout=subprocess.DEVNULL
        )
        if check.returncode == 0:
            print(f"Terminal {instance} already running in process table, skipping.")
            continue

        cmd = [
            "alacritty",
            "--class", f"{instance},{general}",
            "-e", "/home/cr/.local/bin/tmux-smart-attach", target
        ]
        print(f"Spawning {instance} (target window {target})...")
        subprocess.Popen(
            cmd,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        existing_classes.add(instance)
        time.sleep(0.25)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "save":
        save()
    elif len(sys.argv) > 1 and sys.argv[1] == "restore":
        restore()
    elif len(sys.argv) > 1 and sys.argv[1] == "prune":
        prune_dead_sessions()
    else:
        print("Usage: term_manager.py [save|restore|prune]")
