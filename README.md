# 🚀 Arch Linux Dotfiles — macOS Aesthetic & Power Workstation

An aesthetic, keyboard-driven, high-performance desktop environment built on **Arch Linux**, **Qtile**, **Rofi Spotlight**, and **OneDark** palette. Features a custom macOS-inspired top bar, glassmorphic desktop widgets with an animated rhythm wave visualizer, non-blocking asynchronous tools, and complete dark mode integration.

---

## 📸 Overview & Highlights

* **Window Manager**: [Qtile](https://qtile.org/) (Python 3.14+ compatible, zero-overlap macOS bar, instant workspace switching).
* **Application Launcher**: **Rofi Spotlight Edition** (Squared geometry, high contrast OneDark palette, 0-latency).
* **Scientific Calculator**: Built into Spotlight (`Win + C`) with CODATA physical constants (`hbar`, `kb`, `c`, `G`, `eV`, `me`, etc.) and non-blocking clipboard copy.
* **File Finder**: Instant file search bound to `Win + F`.
* **Desktop Widgets**: Custom **Gridgets** suite (Clock, São Paulo Live Weather, System RAM/CPU, and MPRIS Media Player with live dancing audio equalizer bars & Spotatui / Spotify / YouTube prioritization).
* **Terminal**: [Alacritty](https://alacritty.org/) with OneDark theme, UbuntuMono Nerd Font, and Alt+Y / Alt+P clipboard binds.
* **Editor**: [LazyVim](https://www.lazyvim.org/) with OneDark Pro (`onedark_dark`).
* **Document Viewer**: [Zathura](https://pwmt.org/projects/zathura/) configured in Recolor Dark Mode with OneDark, Catppuccin, Dracula, Nord, and TokyoNight themes.
* **Typing Test**: [ttyper](https://github.com/max-niederman/ttyper) centered in an automated floating window with OneDark styling.
* **Lock Screen**: Aesthetic frosted-blur lock screen with automatic 1080p dynamic resolution scaling.
* **Compositor**: [Picom](https://github.com/yshui/picom) v13 with native 32-bit ARGB transparency, hardware double-buffering, and zero-flicker VSync.

---

## ⌨️ Keybindings Cheatsheet

### 🌟 Launchers & Spotlight Tools
| Shortcut | Action |
| :--- | :--- |
| `Win + Space` / `Win + M` | **Spotlight Application Launcher** (Rofi Drun) |
| `Win + C` | **Spotlight Scientific Calculator** (Physical constants + math) |
| `Win + F` | **Spotlight File Finder** (Instant recursive file search) |
| `Alt + Tab` / `Win + Shift + M` | **Window Switcher** (Fuzzy search open windows) |
| `Win + Shift + P` | **Power Menu** (Lock, Suspend, Logout, Reboot, Shutdown) |
| `Win + Shift + W` | **Wi-Fi Network Menu** |
| `Win + E` | **Quicklinks Applet** |

### 🪟 Window & Workspace Management
| Shortcut | Action |
| :--- | :--- |
| `Win + Return` | Open Terminal (Alacritty) |
| `Win + B` | Open Browser (Brave) |
| `Win + R` | Open File Manager (Ranger) |
| `Win + 1 .. 5` | Switch to Workspace 1–5 (Instant, deterministic) |
| `Win + Shift + 1 .. 5` | Move Active Window to Workspace 1–5 |
| `Win + H / J / K / L` | Move Window Focus (Vim-style navigation) |
| `Win + Shift + H / J / K / L` | Shuffle / Move Windows in Layout |
| `Win + Tab` | Cycle Layouts (`Max`, `MonadTall`, `MonadWide`, `RatioTile`) |
| `Win + W` | Close Focused Window |
| `Win + Control + R` | Restart Qtile Live |
| `Win + Shift + G` | Toggle / Reload Gridgets Desktop Widgets |
| `Win + S` | Interactive Screenshot (Flameshot) |

---

## 📂 Repository Structure

```text
.
├── alacritty/               # Terminal emulator configuration & OneDark themes
├── applications/            # Custom .desktop launchers (PDF Arranger Dark, Ttyper Floating)
├── bin/                     # Standalone helper scripts (ttyper-float)
├── electron-flags/          # Hardware stability flags for Antigravity IDE & Brave
├── feh/                     # Wallpaper and image viewer keybindings
├── fish/                    # Fish shell configurations
├── gridgets-qtile/          # Desktop widgets engine (Clock, Weather, System, Music)
│   ├── engine/              # Smart D-Bus MPRIS media listener with player priority
│   ├── widgets/             # UI widgets with animated audio rhythm wave
│   ├── config.json          # Grid coordinates and styling geometry
│   └── style.css            # Glassmorphic Nord/OneDark stylesheet
├── nvim/                    # Neovim / LazyVim configuration & OneDark Pro colorscheme
├── picom/                   # Picom v13 compositor config (VSync, GLX/XRender, Opacity)
├── qtile/                   # Qtile Window Manager configuration
│   ├── autostart.sh         # Background daemon startup script
│   ├── config.py            # Main entry point with non-blocking hooks
│   ├── scripts/             # Lock screen (frosted blur full-screen script)
│   ├── settings/            # Modular settings (keys, groups, layouts, widgets, screens)
│   └── wallpapers/          # High-resolution wallpapers & pre-rendered lock screens
├── ranger/                  # Terminal file manager configuration & devicons
├── rofi/                    # Rofi Spotlight suite, applets, and powermenu
│   └── rofi/
│       ├── scripts/         # Non-blocking calc.py, finder.py, spotlight-calc.sh
│       └── themes/          # spotlight-dark.rasi (Squared OneDark Edition)
├── systemd/                 # User systemd units (rclone Google Drive mount)
├── ttyper/                  # TTY typing test config with OneDark colors & English 200
└── zathura/                 # Zathura minimal PDF viewer with Dark Mode & themes
```

---

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/c4rlosr4ul/dotfiles.git ~/temporary/dotfiles
cd ~/temporary/dotfiles
```

### 2. Symlink Configurations to `~/.config`
```bash
# Core window manager and terminal
ln -sf $(pwd)/qtile ~/.config/qtile
ln -sf $(pwd)/alacritty ~/.config/alacritty
ln -sf $(pwd)/rofi/rofi ~/.config/rofi
ln -sf $(pwd)/picom ~/.config/picom

# Editors & Tools
ln -sf $(pwd)/nvim ~/.config/nvim
ln -sf $(pwd)/zathura ~/.config/zathura
ln -sf $(pwd)/ranger ~/.config/ranger
ln -sf $(pwd)/ttyper ~/.config/ttyper

# Electron Stability Flags (Prevents SIGTRAP on NVIDIA/Nouveau)
cp $(pwd)/electron-flags/* ~/.config/

# Custom Binaries & Desktop Entries
mkdir -p ~/.local/bin ~/.local/share/applications
cp $(pwd)/bin/* ~/.local/bin/
cp $(pwd)/applications/* ~/.local/share/applications/
update-desktop-database ~/.local/share/applications/
```

### 3. Recommended Packages (Arch Linux)
```bash
# Core Environment
sudo pacman -S qtile alacritty rofi picom feh dunst flameshot i3lock imagemagick brightnessctl alsa-utils

# Python & D-Bus Dependencies for Gridgets & Qtile
sudo pacman -S python-gobject gtk3 libnotify python-dbus

# Typing & Tools
sudo pacman -S ttyper zathura zathura-pdf-mupdf ranger
```

---

## 🎨 Theming Details

* **Colorscheme**: **OneDark Pro**
  * Background: `#1e222a` / `#282c34`
  * Foreground: `#abb2bf`
  * Accent Blue: `#61afef`
  * Accent Green: `#98c379`
  * Accent Red: `#e06c75`
  * Accent Yellow: `#e5c07b`
  * Accent Purple: `#c678dd`
* **Typography**: `UbuntuMono Nerd Font` & `Poppins`

---

## 🔒 License
Licensed under the [MIT License](LICENSE).
