import os
import json
import subprocess
import shutil
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

STATE_FILE = "/home/cr/simulations/server-notification/data/multi_cluster_jobs.json"
SQUEUE_PATH = shutil.which("squeue") or "/usr/bin/squeue"


class SlurmWidget(Gtk.Box):
    """
    Desktop Widget displaying active RUNNING Slurm jobs across Arch, Carbono, and Iskay.
    Replaces the media player widget card while keeping media code intact in background.
    """

    def __init__(self, config):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.config = config
        self.get_style_context().add_class('gridget-card')
        self.get_style_context().add_class('gridget-slurm')

        # 1. Header: [󰒋 Slurm Queue] -------- [Badge: 1 Running]
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header_box.set_hexpand(True)

        self.title_lbl = Gtk.Label()
        self.title_lbl.set_halign(Gtk.Align.START)
        self.title_lbl.set_hexpand(True)
        self.title_lbl.get_style_context().add_class('widget-title')
        self.title_lbl.set_markup("<b>󰒋 Slurm Watch Queue</b>")
        header_box.pack_start(self.title_lbl, True, True, 0)

        self.badge_lbl = Gtk.Label()
        self.badge_lbl.set_halign(Gtk.Align.END)
        self.badge_lbl.get_style_context().add_class('slurm-badge')
        self.badge_lbl.set_markup("<span>0 Running</span>")
        header_box.pack_end(self.badge_lbl, False, False, 0)

        self.pack_start(header_box, False, False, 0)

        # 2. Scrollable container for job cards
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_shadow_type(Gtk.ShadowType.NONE)
        scroller.set_overlay_scrolling(True)
        scroller.set_propagate_natural_height(False)
        scroller.set_min_content_height(70)

        self.jobs_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.jobs_container.set_valign(Gtk.Align.START)
        scroller.add(self.jobs_container)
        self.pack_start(scroller, True, True, 2)

        # 3. Quick Action Buttons Row: [󰒋 Watch] [📋 Viewer] [🔄 Refresh]
        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        btn_row.set_halign(Gtk.Align.CENTER)
        btn_row.set_valign(Gtk.Align.END)
        btn_row.set_margin_top(4)
        btn_row.set_margin_bottom(2)

        watch_btn = Gtk.Button()
        watch_lbl = Gtk.Label()
        watch_lbl.set_markup("<span color='#88c0d0' weight='bold'>󰒋 Watch</span>")
        watch_btn.add(watch_lbl)
        watch_btn.get_style_context().add_class('slurm-btn')
        watch_btn.set_tooltip_text("Open live terminal watch squeue")
        watch_btn.connect('clicked', lambda _: subprocess.Popen("alacritty -e watch -n 1 squeue", shell=True))

        viewer_btn = Gtk.Button()
        viewer_lbl = Gtk.Label()
        viewer_lbl.set_markup("<span color='#88c0d0' weight='bold'>📋 Multi-Cluster</span>")
        viewer_btn.add(viewer_lbl)
        viewer_btn.get_style_context().add_class('slurm-btn')
        viewer_btn.set_tooltip_text("Open interactive Multi-Cluster Slurm Monitor")
        viewer_btn.connect(
            'clicked',
            lambda _: subprocess.Popen(
                "alacritty -e /home/cr/.config/qtile/scripts/slurm_multicluster_viewer.py",
                shell=True
            )
        )

        refresh_btn = Gtk.Button()
        refresh_lbl = Gtk.Label()
        refresh_lbl.set_markup("<span color='#88c0d0' weight='bold'>🔄</span>")
        refresh_btn.add(refresh_lbl)
        refresh_btn.get_style_context().add_class('slurm-btn')
        refresh_btn.set_tooltip_text("Refresh queue state")
        refresh_btn.connect('clicked', lambda _: self.update_jobs())

        btn_row.pack_start(watch_btn, False, False, 0)
        btn_row.pack_start(viewer_btn, False, False, 0)
        btn_row.pack_start(refresh_btn, False, False, 0)
        self.pack_start(btn_row, False, False, 2)

        # Initial populate and periodic loop (every 2 seconds)
        self.update_jobs()
        GLib.timeout_add_seconds(2, self.update_jobs)

    def get_running_data(self):
        """Fetches multi-cluster running jobs data."""
        data = {"arch": [], "carbono": [], "iskay": [], "huk": []}
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    raw = json.load(f)
                    clusters = raw.get("clusters", {})
                    for c in ["arch", "carbono", "iskay", "huk"]:
                        if c in clusters:
                            data[c] = clusters[c]
            except Exception:
                pass

        # Always check local Arch squeue as real-time ground truth
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
                                "time": p[3] if len(p) > 3 else "",
                                "node": p[4] if len(p) > 4 else "carlos",
                                "partition": p[5] if len(p) > 5 else "batch",
                                "cluster": "arch",
                                "state": "RUNNING"
                            })
                    data["arch"] = arch_jobs
            except Exception:
                pass

        # Fallback to direct Carbono check if empty in state
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
                                "time": p[3] if len(p) > 3 else "",
                                "node": p[4] if len(p) > 4 else "n02",
                                "partition": p[5] if len(p) > 5 else "fulereno",
                                "cluster": "carbono",
                                "state": "RUNNING"
                            })
                    data["carbono"] = carb_jobs
            except Exception:
                pass

        # Fallback to direct Huk check if empty in state and ControlMaster socket is active
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
                                    "time": p[3] if len(p) > 3 else "",
                                    "node": p[4] if len(p) > 4 else "huk",
                                    "partition": p[5] if len(p) > 5 else "batch",
                                    "cluster": "huk",
                                    "state": "RUNNING"
                                })
                        data["huk"] = huk_jobs
                except Exception:
                    pass

        return data

    def update_jobs(self):
        """Re-renders running jobs in the widget container."""
        # Clear existing entries
        for child in self.jobs_container.get_children():
            self.jobs_container.remove(child)
            child.destroy()

        data = self.get_running_data()
        arch_jobs = data.get("arch", [])
        carb_jobs = data.get("carbono", [])
        iskay_jobs = data.get("iskay", [])
        huk_jobs = data.get("huk", [])

        total = len(arch_jobs) + len(carb_jobs) + len(iskay_jobs) + len(huk_jobs)

        # Update Badge
        if total > 0:
            self.badge_lbl.get_style_context().remove_class('slurm-badge-idle')
            self.badge_lbl.get_style_context().add_class('slurm-badge')
            self.badge_lbl.set_markup(f"<b>{total} Running</b>")
        else:
            self.badge_lbl.get_style_context().remove_class('slurm-badge')
            self.badge_lbl.get_style_context().add_class('slurm-badge-idle')
            self.badge_lbl.set_markup("<span alpha='65%'>0 Running</span>")

        # Cluster configs: (Display Name, Jobs List, Accent Color)
        clusters = [
            ("Arch Workstation", arch_jobs, "#a3be8c"),
            ("Carbono Cluster", carb_jobs, "#ebcb8b"),
            ("Iskay Cluster", iskay_jobs, "#b48ead"),
            ("Huk Cluster", huk_jobs, "#88c0d0"),
        ]

        has_any_jobs = False

        for c_title, j_list, color in clusters:
            if not j_list:
                continue

            has_any_jobs = True
            # Cluster Section Title
            hdr = Gtk.Label()
            hdr.set_halign(Gtk.Align.START)
            hdr.get_style_context().add_class('slurm-cluster-hdr')
            hdr.set_markup(f"<span color='{color}'>● <b>{c_title}</b> ({len(j_list)})</span>")
            self.jobs_container.pack_start(hdr, False, False, 2)

            for j in j_list:
                box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
                box.get_style_context().add_class('slurm-job-box')

                # Title row: [ #161 H_Sn ] --- [ 9:25:30 ]
                top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                lbl_name = Gtk.Label()
                lbl_name.set_halign(Gtk.Align.START)
                lbl_name.set_ellipsize(3)
                lbl_name.get_style_context().add_class('slurm-job-title')
                lbl_name.set_markup(f"<b>#{j.get('id', '')}</b>  <span color='#88c0d0'>{j.get('name', 'job')}</span>")

                lbl_time = Gtk.Label()
                lbl_time.set_halign(Gtk.Align.END)
                lbl_time.get_style_context().add_class('slurm-job-sub')
                lbl_time.set_markup(f"<span color='#d8dee9'>⏱ {j.get('time', 'running')}</span>")

                top_row.pack_start(lbl_name, True, True, 0)
                top_row.pack_end(lbl_time, False, False, 0)
                box.pack_start(top_row, False, False, 0)

                # Sub row: Node carlos | user cr | part batch
                node_str = j.get('node', 'N/A')
                part_str = j.get('partition', 'batch')
                user_str = j.get('user', '')
                sub_text = f"🖥 {node_str}  ·  📂 {part_str}"
                if user_str:
                    sub_text += f"  ·  👤 {user_str}"

                sub_lbl = Gtk.Label()
                sub_lbl.set_halign(Gtk.Align.START)
                sub_lbl.get_style_context().add_class('slurm-job-sub')
                sub_lbl.set_markup(f"<span alpha='75%'>{sub_text}</span>")
                box.pack_start(sub_lbl, False, False, 0)

                self.jobs_container.pack_start(box, False, False, 1)

        # If no jobs running anywhere
        if not has_any_jobs:
            idle_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            idle_box.set_valign(Gtk.Align.CENTER)
            idle_box.set_vexpand(True)

            idle_title = Gtk.Label()
            idle_title.set_markup("<span color='#81a1c1'><b>All Slurm Queues Idle</b></span>")

            idle_desc = Gtk.Label()
            idle_desc.set_markup(
                "<span size='small' alpha='60%'>No active running jobs on Arch, Carbono, Iskay, or Huk.\nClick Watch to monitor upcoming submissions.</span>"
            )
            idle_desc.set_justify(Gtk.Justification.CENTER)

            idle_box.pack_start(idle_title, False, False, 0)
            idle_box.pack_start(idle_desc, False, False, 0)
            self.jobs_container.pack_start(idle_box, True, True, 10)
        else:
            # Show summary of other idle clusters
            idle_clusters = [c_title.split()[0] for c_title, j_list, _ in clusters if not j_list]
            if idle_clusters:
                idle_status_lbl = Gtk.Label()
                idle_status_lbl.set_halign(Gtk.Align.START)
                idle_summary = " · ".join([f"{c}: 0" for c in idle_clusters])
                idle_status_lbl.set_markup(f"<span size='small' alpha='50%'>Idle: {idle_summary}</span>")
                self.jobs_container.pack_start(idle_status_lbl, False, False, 2)

        self.jobs_container.show_all()
        return True
