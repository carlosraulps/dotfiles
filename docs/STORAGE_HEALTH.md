# 🛡️ Storage Architecture & Root Partition Safeguards

This document outlines the disk partition architecture, storage pools, and automated maintenance safeguards designed to prevent the 50 GB root partition (`/`) from running out of disk space.

---

## 📊 Partition Layout

On this system, storage is allocated across LVM volumes on a 1 TB NVMe SSD:

| Mount Point | Volume | Capacity | Ideal Role |
| :--- | :--- | :--- | :--- |
| `/` (Root) | `/dev/mapper/ArchinstallVg-root` | **50 GB** | Base OS, system libraries, core pacman packages |
| `/home` | `/dev/mapper/ArchinstallVg-home` | **880 GB** | User files, VMs, ISOs, datasets, project caches, Docker |

---

## 🛑 What Caused the Historic "No Space Left On Device" Error

By default, Virt-Manager / Libvirt creates a storage pool at `/var/lib/libvirt/images` (located on `/`).

When a 65 GB Windows 11 virtual machine (`win11.qcow2`) was created in that default pool, it quickly allocated 20+ GB during setup. Because the entire root partition was only 50 GB, root hit **100% full (0 bytes free)**. QEMU immediately paused the VM with `"Disk I/O error: No space left on device"`.

---

## 🚀 The Permanent Solutions Applied

### 1. Relocated Virtual Machines to `/home/cr/vmachines/`
* Moved all `.qcow2` images and `.iso` files to `/home/cr/vmachines/` (700+ GB available).
* Reconfigured libvirt domain XMLs to point to the new path.
* Assigned ownership to `libvirt-qemu:kvm`.
* **Permanently deactivated** the `/var` storage pool in libvirt so all future VMs default to `/home/cr/vmachines/`.

### 2. Automated Weekly Pacman Cache Pruning
Arch Linux preserves every downloaded package version in `/var/cache/pacman/pkg/` by default, which can balloon to 15–20 GB.

We enabled `paccache.timer`:
```bash
sudo pacman -S pacman-contrib --noconfirm
sudo systemctl enable --now paccache.timer
```
* **Benefit**: Automatically runs weekly, keeping only the 2 most recent package versions for downgrade safety and deleting older ones. Caches are kept under ~1 GB.

### 3. Systemd Journal Size Cap
Capped `/var/log/journal/` at 200 MB via `/etc/systemd/journald.conf.d/size-limit.conf`:
```ini
[Journal]
SystemMaxUse=200M
SystemMaxFileSize=50M
```

### 4. Disabled Memory Core Dumps
Disabled multi-gigabyte memory dumps on app crashes via `/etc/systemd/coredump.conf.d/disable.conf`:
```ini
[Coredump]
Storage=none
```

---

## 💡 Best Practices for Future Applications

* **Flatpaks**: Always install with `--user` (`flatpak install --user <app>`). Installs to `~/.local/share/flatpak` on `/home`.
* **Containers (Docker/Podman)**: Configure Docker data-root to `/home/docker` or use rootless Podman.
* **Large Datasets / Models**: Always store in `/home/cr/`.
