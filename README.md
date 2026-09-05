# 🚀 Arch Linux Dotfiles — macOS Aesthetic & Power Workstation

An aesthetic, keyboard-driven, high-performance desktop environment built on **Arch Linux**, **Qtile**, **Rofi Spotlight**, and **OneDark** palette. Features a custom macOS-inspired top bar, zero-mirroring persistent terminals, a full Pomodoro productivity suite, glassmorphic desktop widgets with an animated audio visualizer, NVMe-accelerated Google Drive integration, and complete dark mode ergonomics.

---

## 📸 Overview & Highlights

* **Window Manager**: [Qtile](https://qtile.org/) (Python 3.14+ compatible, zero-overlap top bar, instant workspace switching).
* **Terminal & Multiplexer**: [Alacritty](https://alacritty.org/) with [Tmux](https://github.com/tmux/tmux):
  * **Dynamic Auto-Renaming**: Status tabs automatically track the active foreground command (`spotatui`, `btop`, `nvim`, `ranger`, `agy`, `fish`).
  * **Zero Mirroring**: Every `Win + Enter` terminal window gets an independent prompt while sharing the global active terminal list across the top.
  * **Clean Shutdown**: Closing a window (`Win + W` or `exit`) immediately removes that window from Tmux so ghost tabs never accumulate.
  * **Auto-Save**: Background session persistence (`tmux-continuum` / `tmux-resurrect`) saves state every 5 minutes.
* **Productivity Suite**:
  * **Spotlight Pomodoro**: One-click presets for 45m deep study, 15m break, 25m classic, and custom timers via `Win + P` or top bar click.
  * **Live Pango Indicators**: Real-time countdown on the status bar (Vibrant Green for study, Warm Amber for break, Soft Red for paused, Dim Grey for idle).
* **Cloud Storage**:
  * **NVMe Google Drive Live Mount**: Full VFS caching (`rclone`) on local NVMe SSD with 5s asynchronous write-back for **0ms editing latency** in Neovim/VSCode and 7ms RAM directory browsing.
* **Application Launcher**: **Rofi Spotlight Edition** (Clean squared geometry, low-eyestrain OneDark palette, 0-latency).
* **Scientific Calculator**: Built into Spotlight (`Win + C`) with CODATA physical constants (`hbar`, `kb`, `c`, `G`, `eV`, `me`, etc.) and clipboard copy.
* **File Finder**: Instant recursive file search bound to `Win + F`.
* **Desktop Widgets**: Custom **Gridgets** suite (Clock, São Paulo Live Weather, System RAM/CPU, and MPRIS Media Player with live dancing audio equalizer bars).
* **Editor**: [LazyVim](https://www.lazyvim.org/) with OneDark Pro (`onedark_dark`).
* **Document Viewer**: [Zathura](https://pwmt.org/projects/zathura/) configured in Recolor Dark Mode with OneDark, Catppuccin, Dracula, Nord, and TokyoNight themes.
* **Compositor**: [Picom](https://github.com/yshui/picom) v13 with native 32-bit ARGB transparency, hardware double-buffering, and zero-flicker VSync.

---

## ⌨️ Keybindings Cheatsheet

### 🌟 Launchers & Productivity Tools
| Shortcut | Action |
| :--- | :--- |
| `Win + Space` / `Win + M` | **Spotlight Application Launcher** (Rofi Drun) |
| `Win + C` | **Spotlight Scientific Calculator** (Physical constants + math) |
| `Win + F` | **Spotlight File Finder** (Instant recursive file search) |
| `Alt + Tab` / `Win + Shift + M` | **Window Switcher** (Fuzzy search open windows) |
| `Win + P` | **Pomodoro Productivity Menu** (Popup presets: 45m study, 15m break, custom) |
| `Win + Shift + P` | **Power Menu** (Lock, Suspend, Logout, Reboot, Shutdown) |
| `Win + Shift + W` | **Wi-Fi Network Menu** |
| `Win + E` | **Quicklinks Applet** |

### 🪟 Window & Workspace Management
| Shortcut | Action |
| :--- | :--- |
| `Win + Return` | **Open Terminal** (Always fresh, zero-mirroring, auto-renamed) |
| `Win + Shift + Return` | **Open Persistent Workstation** (Direct attach to `base` session) |
| `Win + B` | Open Browser (Brave) |
| `Win + R` | Open File Manager (Ranger) |
| `Win + 1 .. 5` | Switch to Workspace 1–5 (Instant, deterministic) |
| `Win + Shift + 1 .. 5` | Move Active Window to Workspace 1–5 |
| `Win + H / J / K / L` | Move Window Focus (Vim-style navigation) |
| `Win + Shift + H / J / K / L` | Shuffle / Move Windows in Layout |
| `Win + Tab` | Cycle Layouts (`Max`, `MonadTall`, `MonadWide`, `RatioTile`) |
| `Win + W` | Close Focused Window (Cleanly kills X11 window + Tmux tab) |
| `Win + Control + R` | Restart Qtile Live |
| `Win + Shift + G` | Toggle / Reload Gridgets Desktop Widgets |
| `Win + S` | Interactive Screenshot (Flameshot) |

### 📟 Subterminal Splits & Tmux Controls
| Shortcut | Action |
| :--- | :--- |
| `Ctrl + b \|` | Split Window Vertically (New subterminal on the right) |
| `Ctrl + b -` | Split Window Horizontally (New subterminal below) |
| `Ctrl + b h / j / k / l` | Navigate between split subterminals |
| `Ctrl + b d` | Detach session (keeps tasks running in background) |
| `Mouse Click` | Focus split pane or click tabs in the top bar |

---

## 🖥️ Workstation Workspace Layout

Qtile is configured with deterministic workspace routing on startup and live reload:

* **Workspace 1 (` 󰖟 `)**: General Web & Research.
* **Workspace 2 (`  `)**: Development Master Suite. Auto-starts **Brave** as master on the left and **2 Alacritty terminals** stacked vertically on the right in `MonadTall` layout.
* **Workspace 3 (`  `)**: Antigravity AI Suite. Strictly locked to **`Max` layout**. Automatically routes both **Antigravity IDE** and the standalone **Antigravity app** full-screen (`Win + Tab` or `Win + J / K` toggles between them).
* **Workspace 4 (`  `)**: Notes, Writing & PDF Reading (Zathura / Obsidian).
* **Workspace 5 (`  `)**: Media, Spotify & Monitoring (Spotatui, Btop).

---

## 🍅 Pomodoro Productivity Suite

The custom Pomodoro controller ([`qtile/scripts/pomodoro.py`](file:///home/cr/temporary/dotfiles/qtile/scripts/pomodoro.py)) integrates directly with the top bar and Rofi:

* **Interactive Menu (`Win + P` or Left-Click bar)**:
  * 🧠 **45 min — Deep Study & Research**: Dedicated long-focus block.
  * ☕ **15 min — Rest & Coffee Break**: Restorative break paired with deep study.
  * 🍅 **25 min — Classic Pomodoro**: Standard focus sprint.
  * ⚡ **50 min — Ultra Flow Sprint**: Extended high-intensity coding session.
  * 🧘 **5 min — Quick Eye & Posture Break**: Fast micro-break.
  * 󰔛 **Custom Timer...**: Type any duration in minutes (e.g. `30`, `90`).
  * ⏸️ / ▶️ **Smart Pause & Resume**: Freezes the exact second remaining.
  * ⏹️ **Reset / Cancel**: Clears the active session.
  * 🏆 **Today's Score**: Tracks completed focus sessions for the day.
* **Top Bar Indicators**:
  * Study: `<span foreground="#98c379">󰄉 󱎫 MM:SS</span>` (OneDark Green)
  * Break: `<span foreground="#e5c07b">󰄉 󰏤 MM:SS</span>` (OneDark Amber)
  * Paused: `<span foreground="#e06c75">󰄉 󰏥 MM:SS</span>` (OneDark Red)
  * Idle: `<span foreground="#5c6370">󰄉 25m</span>` (Dim Slate)
* **Mouse Callbacks**:
  * **Left-Click**: Open Rofi preset menu.
  * **Middle-Click**: Instant pause / resume toggle.
  * **Right-Click**: Instant reset.

---

## ⚡ High-Performance Google Drive Mount

Configured via user systemd service ([`systemd/user/rclone-gdrive.service`](file:///home/cr/temporary/dotfiles/systemd/user/rclone-gdrive.service)) delivering local SSD speeds:

* **Instant Saves (`--vfs-write-back 5s`)**: File saves in Neovim/VSCode write to your local NVMe SSD in **< 1ms**. Rclone syncs changes to Google Drive 5s later in the background with zero editing latency.
* **7ms Directory Browsing (`--dir-cache-time 72h`)**: Caches directory tree metadata in RAM for instant folder navigation in Ranger or file pickers.
* **Live Push Sync (`--poll-interval 15s`)**: Listens to Google's Changes Stream. Remote edits from other devices appear locally within 15 seconds.
* **40 GB NVMe Hot Cache (`--vfs-cache-max-size 40G`)**: Files accessed in the last 3 days load at 3,500 MB/s directly from SSD.
* **Permanent OAuth Key**: Published in Google Cloud Console (*In Production*) for infinite-lifetime tokens that never expire after 7 days.

---

## 🛡️ Storage Architecture & Safety Safeguards

To prevent the 50 GB root partition (`/`) from running out of disk space:

1. **Virtual Machine Storage Pool**:
   * Libvirt's default pool (`/var/lib/libvirt/images`) is permanently deactivated.
   * All VM disk images (`.qcow2`) are stored in `/home/cr/vmachines/` where **700+ GB of free space** is available.
2. **Automated Pacman Cache Pruning**:
   * Enabled `paccache.timer` via `pacman-contrib` to automatically prune old package versions weekly, capping package cache to ~1 GB.
3. **Journal Log Cap**:
   * Capped `systemd-journald` size to `200M` in `/etc/systemd/journald.conf.d/size-limit.conf`.
4. **Coredump Storage**:
   * Disabled multi-gigabyte memory dumps on app crashes via `/etc/systemd/coredump.conf.d/disable.conf`.

---

## 📂 Repository Structure

```text
.
├── alacritty/               # Terminal emulator configuration & OneDark themes
├── applications/            # Custom .desktop launchers (PDF Arranger Dark, Ttyper Floating)
├── bin/                     # Standalone helper scripts (tmux-smart-attach, ttyper-float)
├── electron-flags/          # Hardware stability flags for Antigravity IDE & Brave
├── feh/                     # Wallpaper and image viewer keybindings
├── fish/                    # Fish shell configurations
├── gridgets-qtile/          # Desktop widgets engine (Clock, Weather, System, Music)
├── nvim/                    # Neovim / LazyVim configuration & OneDark Pro colorscheme
├── picom/                   # Picom v13 compositor config (VSync, GLX, 32-bit ARGB)
├── qtile/                   # Qtile Window Manager configuration
│   ├── autostart.sh         # Daemon startup with singleton mutex lockfile
│   ├── config.py            # Main entry point with single startup hook
│   ├── scripts/             # Pomodoro controller (pomodoro.py) & frosted lock screen
│   ├── settings/            # Modular settings (keys, groups, layouts, widgets, screens)
│   └── themes/              # mac-arch, darker, and onedark JSON palettes
├── ranger/                  # Terminal file manager configuration & devicons
├── rofi/                    # Rofi Spotlight suite, applets, and powermenu
│   └── rofi/
│       ├── scripts/         # Non-blocking calc.py, finder.py, spotlight-calc.sh
│       └── themes/          # spotlight-dark.rasi (Muted OneDark & Slate Edition)
├── systemd/                 # User systemd units (NVMe-optimized rclone Google Drive mount)
├── tmux/                    # Tmux config (dynamic auto-renaming, OneDark bar, 5m autosave)
├── ttyper/                  # TTY typing test config with OneDark colors & English 200
└── zathura/                 # Zathura minimal PDF viewer with Dark Mode & themes
```

---

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/carlosraulps/dotfiles.git ~/temporary/dotfiles
cd ~/temporary/dotfiles
```

### 2. Symlink Configurations to `~/.config`
```bash
# Core window manager, terminal, and multiplexer
ln -sf $(pwd)/qtile ~/.config/qtile
ln -sf $(pwd)/alacritty ~/.config/alacritty
ln -sf $(pwd)/tmux/.tmux.conf ~/.tmux.conf
ln -sf $(pwd)/rofi/rofi ~/.config/rofi
ln -sf $(pwd)/picom ~/.config/picom

# Editors & Tools
ln -sf $(pwd)/nvim ~/.config/nvim
ln -sf $(pwd)/zathura ~/.config/zathura
ln -sf $(pwd)/ranger ~/.config/ranger
ln -sf $(pwd)/ttyper ~/.config/ttyper

# Systemd User Services
mkdir -p ~/.config/systemd/user
ln -sf $(pwd)/systemd/user/rclone-gdrive.service ~/.config/systemd/user/rclone-gdrive.service
systemctl --user daemon-reload
systemctl --user enable --now rclone-gdrive.service

# Electron Stability Flags (Prevents GPU/Nouveau hangs)
cp $(pwd)/electron-flags/* ~/.config/

# Custom Binaries & Desktop Entries
mkdir -p ~/.local/bin ~/.local/share/applications
cp $(pwd)/bin/* ~/.local/bin/
chmod +x ~/.local/bin/*
cp $(pwd)/applications/* ~/.local/share/applications/
update-desktop-database ~/.local/share/applications/
```

### 3. Recommended Packages (Arch Linux)
```bash
# Core Environment & Window Manager
sudo pacman -S qtile alacritty tmux rofi picom feh dunst flameshot i3lock imagemagick brightnessctl alsa-utils libnotify

# Python & D-Bus Dependencies for Gridgets & Qtile
sudo pacman -S python-gobject gtk3 python-dbus pacman-contrib

# Typing & Tools
sudo pacman -S ttyper zathura zathura-pdf-mupdf ranger rclone
```

---

## 🎨 Theming Details

* **Colorscheme**: **OneDark Pro & Nord Slate**
  * Background: `#1e222a` / `#242b38`
  * Elevated Surface: `#2c3240` / `#323b4c`
  * Foreground: `#e2e6ed` / `#abb2bf`
  * Muted: `#5c6370` / `#7f848e`
  * Accent Blue: `#61afef` (Soft OneDark Sky Blue)
  * Accent Green: `#98c379`
  * Accent Amber: `#e5c07b`
  * Accent Coral: `#e06c75`
* **Typography**: `UbuntuMono Nerd Font` & `Poppins`

---

## 🔒 License
Licensed under the [MIT License](LICENSE).
