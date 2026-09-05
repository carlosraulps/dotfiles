# 📟 Terminal & Multiplexer Architecture (Zero Mirroring & Clean Exit)

This document details the multi-terminal architecture combining **Alacritty**, **Tmux**, and **Qtile** to provide session persistence, zero-mirroring independence, real-time command tracking, and automatic zombie window cleanup.

---

## 🎯 The Challenges Solved

Traditional tiling window manager setups struggle when pairing terminal windows with Tmux:

1. **Mirroring Trap**: Attaching multiple terminal windows to the same Tmux session causes every window to mirror the exact same view.
2. **Ghost Window Accumulation**: Closing an X11 terminal window (`Win + W`) only detaches the Tmux client, leaving orphaned shells running in the background (`1:fish`, `2:fish` ... `12:fish`).
3. **Reboot Clutter**: Tools like `tmux-continuum` save all those dead background windows and restore a dozen useless tabs upon reboot.
4. **Static Window Names**: Hardcoding names (`-n "term"`) disables Tmux's automatic renaming, hiding what command is actually running.

---

## 🏗️ The Solution Architecture (`tmux-smart-attach`)

Implemented in [`bin/tmux-smart-attach`](file:///home/cr/temporary/dotfiles/bin/tmux-smart-attach) and linked to `~/.local/bin/tmux-smart-attach`:

```text
[ Win + Return ]
       │
       ▼
1. Always spawn a fresh window in the 'base' session
       │
       ▼
2. Create an independent grouped session (term-PID) viewing that window
       │
       ▼
3. Enable 'automatic-rename on' & 'allow-rename off' (tracks foreground command)
       │
       ▼
4. Trap EXIT / SIGHUP / SIGTERM:
   When Win + W kills the window -> immediately 'tmux kill-window'
```

---

## 🌟 Key Features & Behaviors

### 1. Zero Mirroring
Every press of **`Win + Return`** creates an independent window in the shared session. Each terminal window on your desktop can run different commands without mirroring or hijacking any other window.

### 2. Unified Active Terminal Bar
Every terminal displays the real-time status bar across the top:
```text
1:fish   2:btop   3:spotatui   4:nvim
```
You can see all active tools currently running across all workspaces.

### 3. Dynamic Program Renaming
Configured in [`tmux/.tmux.conf`](file:///home/cr/temporary/dotfiles/tmux/.tmux.conf):
```tmux
set -g renumber-windows on
set -g automatic-rename on
setw -g automatic-rename on
set -g allow-rename off
set -g automatic-rename-format "#{?pane_in_mode,[tmux],#{pane_current_command}}"
```
* Running `spotatui` renames the tab to `spotatui`.
* Running `btop` renames the tab to `btop`.
* Running `nvim` renames the tab to `nvim`.
* Exiting the program smoothly reverts the tab back to `fish`.

### 4. Instant Clean Shutdown on `Win + W`
In `tmux-smart-attach`:
```bash
cleanup() {
    TOTAL_WINS=$(tmux list-windows -t base 2>/dev/null | wc -l)
    if [ "$TOTAL_WINS" -gt 1 ]; then
        tmux kill-window -t "$WIN_ID" 2>/dev/null
    fi
    tmux kill-session -t "$SESS_NAME" 2>/dev/null
}
trap cleanup EXIT SIGHUP SIGINT SIGTERM
```
When you press `Win + W`, the script's exit trap fires, killing that specific window in Tmux. It instantly disappears from the top bar across all remaining terminals.

### 5. Background Crash Protection
`tmux-continuum` saves active sessions every 5 minutes to `~/.local/share/tmux/resurrect/`. Because closed windows are destroyed upon exit, only **truly active** sessions are saved and restored on reboot.

---

## ⌨️ Common Terminal Keybindings

| Shortcut | Description |
| :--- | :--- |
| `Win + Return` | Open fresh terminal window |
| `Win + Shift + Return` | Direct attach to master `base` session |
| `Win + W` | Close active terminal (kills window in Tmux) |
| `Ctrl + b \|` | Split pane vertically |
| `Ctrl + b -` | Split pane horizontally |
| `Ctrl + b h / j / k / l` | Navigate split panes |
| `Ctrl + b d` | Detach session (keeps running in background) |
| `Mouse Click` | Focus pane or click window tab in the top bar |
