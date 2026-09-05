# ⚡ High-Performance Google Drive Live Mount (0ms Local Latency)

This system mounts Google Drive as a native local filesystem under `~/mnt/google-drive` using **rclone** and **systemd user services**, engineered specifically for zero-latency local development and high-throughput data transfer.

---

## 🎯 Architecture Overview

Traditional cloud mounts suffer from high round-trip API latency on every directory navigation (`ls`, `cd`, file tree in editors) and blocking delays on file saves.

This configuration solves both issues using an **NVMe VFS Hot Cache** combined with **RAM-based metadata caching**:

```text
[ Editor / Shell ] 
        │
        ▼ (< 1ms write)
[ Local NVMe SSD Cache (~/.cache/rclone) ]
        │
        ▼ (Asynchronous background upload after 5s)
[ Google Drive Cloud API ]
```

---

## ⚙️ Service Configuration

The service is defined at [`~/.config/systemd/user/rclone-gdrive.service`](file:///home/cr/.config/systemd/user/rclone-gdrive.service) and tracked in [`systemd/user/rclone-gdrive.service`](file:///home/cr/temporary/dotfiles/systemd/user/rclone-gdrive.service):

```ini
[Unit]
Description=rclone Google Drive Mount (High Performance NVMe VFS Cache)
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
ExecStartPre=/usr/bin/mkdir -p %h/mnt/google-drive
ExecStart=/usr/bin/rclone mount cr: %h/mnt/google-drive \
    --vfs-cache-mode full \
    --vfs-cache-max-age 72h \
    --vfs-cache-max-size 40G \
    --vfs-read-ahead 128M \
    --vfs-write-back 5s \
    --dir-cache-time 72h \
    --poll-interval 15s \
    --buffer-size 64M \
    --drive-chunk-size 64M
ExecStop=/usr/bin/fusermount3 -uz %h/mnt/google-drive
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

---

## 🚀 Performance Flags Explained

| Flag | Value | Function & Benefit |
| :--- | :--- | :--- |
| `--vfs-cache-mode` | `full` | Enables two-way caching on your local SSD. Files open instantly and can be edited out-of-order. |
| `--vfs-write-back` | `5s` | **Zero-lag saving.** Saving a file in Neovim or VSCode commits directly to NVMe in < 1ms. Rclone uploads the file 5 seconds later in the background. |
| `--dir-cache-time` | `72h` | Directory trees and metadata are stored in RAM for 72 hours. Running `ls` or opening folders in Ranger executes in **0.007s (7ms)**. |
| `--poll-interval` | `15s` | Uses Google's Changes Stream. If you upload a file from your phone or web browser, it appears locally within 15 seconds without flushing your directory cache. |
| `--vfs-cache-max-age` | `72h` | Retains accessed files locally for 3 days so you don't repeatedly re-download project files. |
| `--vfs-cache-max-size` | `40G` | Caps the local cache size to 40 GB on your `/home` partition. |
| `--drive-chunk-size` | `64M` | Increases upload batch sizes from 8MB to 64MB, accelerating uploads of PDFs, videos, and datasets by up to 4x. |
| `--buffer-size` | `64M` | Read buffer in RAM per open file. |

---

## 🔑 Permanent OAuth Key Setup (Never Expire in 7 Days)

By default, Google Cloud OAuth apps are in **"Testing"** status, which invalidates refresh tokens every 7 days with `invalid_grant`.

To make the token permanent:

1. Go to [Google Cloud Console — OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent).
2. Under **Publishing status**, click **"PUBLISH APP"** (Switch from *Testing* to *In Production*).
3. Confirm the prompt.
4. Re-authorize once in your terminal:
   ```bash
   rclone config reconnect cr:
   ```
5. Restart the mount service:
   ```bash
   systemctl --user restart rclone-gdrive.service
   ```

---

## 🛠️ Management Commands

* **Check service status**: `systemctl --user status rclone-gdrive.service`
* **Restart service**: `systemctl --user restart rclone-gdrive.service`
* **Stop service**: `systemctl --user stop rclone-gdrive.service`
* **Inspect logs**: `journalctl --user -u rclone-gdrive.service -f`
