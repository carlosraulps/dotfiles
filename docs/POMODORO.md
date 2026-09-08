# 🍅 Pomodoro Productivity Suite (Spotlight Edition)

A high-productivity focus timer built directly into **Qtile** and **Rofi Spotlight**, offering preset study cycles, dynamic Pango color markup, drift-proof UNIX time calculations, audio chime notifications, and daily score tracking.

---

## 🎯 Features

* **Interactive Rofi Spotlight Popup**: Accessible via **`Win + P`** or **Left-Click** on the top bar indicator.
* **Auto-Completion Pop-up Modal**: The moment a session or break expires, an interactive Spotlight modal appears automatically in the center of the screen, offering instant 1-click transitions (e.g. `Enter` to start recommended 15m break).
* **OneDark Dunst Notifications**: Tailored Dunst theme matching Qtile and Rofi geometry with high-contrast banners and application icon support.
* **Flashing Top Bar Completion Alert**: If you look away, the top bar widget flashes an alternating high-visibility completion banner (`🎉 00:00 DONE! TAKE A BREAK`) until acknowledged or clicked.
* **Audible Alarm Chimes**: Plays crisp system alarm sounds (`alarm-clock-elapsed.oga` / `complete.oga`) via `paplay` when sessions end.
* **One-Click Presets**:
  * 🧠 **45 min — Deep Study & Research**: Long-focus block for intensive programming and literature reading.
  * ☕ **15 min — Rest & Coffee Break**: Restorative break paired with deep study blocks.
  * 🍅 **25 min — Classic Pomodoro**: The traditional 25m sprint.
  * ⚡ **50 min — Ultra Flow Sprint**: Extended high-intensity coding session.
  * 🧘 **5 min — Quick Eye & Posture Break**: Micro-break to stretch and hydrate.
  * 󰔛 **Custom Timer...**: Interactive minutes prompt for custom durations.
  * ⏸️ / ▶️ **Smart Pause & Resume**: Freezes the exact second remaining and resumes seamlessly.
  * ⏹️ **Reset / Cancel**: Clears the active session and returns to idle.
  * 🏆 **Today's Score**: Tracks completed focus sessions for the day.
* **Dynamic OneDark Top Bar Indicator**:
  * **Study Session**: `<span foreground="#98c379">󰄉 󱎫 MM:SS</span>` (OneDark Green)
  * **Break Period**: `<span foreground="#e5c07b">󰄉 󰏤 MM:SS</span>` (Warm Amber)
  * **Paused**: `<span foreground="#e06c75">󰄉 󰏥 MM:SS</span>` (Coral Red)
  * **Session Finished**: `<span background="#e5c07b" foreground="#1e222a"><b> 🎉 00:00 DONE! TAKE A BREAK </b></span>` (Flashing Alert)
  * **Idle**: `<span foreground="#5c6370">󰄉 25m</span>` (Dim Slate)
* **Drift-Proof Architecture**: Uses absolute UNIX epoch timestamps (`time.time()`). System freezes, sleep mode, or terminal lag will **never** desync the countdown.

---

## 🖱️ Controls & Shortcuts

| Action | How to Trigger |
| :--- | :--- |
| **Open Preset Menu** | **`Win + P`** or **Left-Click** the timer on the top bar |
| **Quick Toggle (Pause / Resume)** | **Middle-Click** (scroll wheel click) directly on the timer |
| **Quick Reset** | **Right-Click** directly on the timer |

---

## 📂 Source Code

* Controller Script: [`qtile/scripts/pomodoro.py`](file:///home/cr/temporary/dotfiles/qtile/scripts/pomodoro.py)
* Qtile Widget Integration: [`qtile/settings/widgets.py`](file:///home/cr/temporary/dotfiles/qtile/settings/widgets.py#L164-L190)
* Hotkey Binding: [`qtile/settings/keys.py`](file:///home/cr/temporary/dotfiles/qtile/settings/keys.py#L55)
