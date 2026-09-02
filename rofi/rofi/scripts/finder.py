#!/usr/bin/env python3
"""
macOS Spotlight-style File Finder & Search for Rofi
Fast recursive search across user home folders with rich icons and non-blocking opening via xdg-open / ranger.
"""

import os
import sys
import subprocess

HOME = os.path.expanduser("~")

EXT_ICONS = {
    # Images
    ".png": " ", ".jpg": " ", ".jpeg": " ", ".webp": " ", ".gif": " ", ".svg": " ", ".bmp": " ", ".ico": " ",
    # Documents & PDFs
    ".pdf": " ", ".doc": " ", ".docx": " ", ".odt": " ", ".rtf": " ", ".txt": " ", ".md": " ", ".csv": " ", ".xlsx": " ", ".xls": " ",
    # Code & Configs
    ".py": "󰌠 ", ".sh": " ", ".bash": " ", ".zsh": " ", ".fish": " ",
    ".c": " ", ".cpp": " ", ".h": " ", ".hpp": " ", ".rs": " ", ".go": " ",
    ".js": " ", ".ts": " ", ".html": " ", ".css": " ", ".json": " ", ".yaml": " ", ".yml": " ",
    ".toml": " ", ".rasi": " ", ".conf": " ", ".ini": " ", ".lua": " ", ".vim": " ",
    # Archives
    ".zip": " ", ".tar": " ", ".gz": " ", ".xz": " ", ".bz2": " ", ".zst": " ", ".7z": " ", ".rar": " ",
    # Media
    ".mp3": "󰎆 ", ".flac": "󰎆 ", ".wav": "󰎆 ", ".ogg": "󰎆 ", ".m4a": "󰎆 ",
    ".mp4": "󰕧 ", ".mkv": "󰕧 ", ".webm": "󰕧 ", ".mov": "󰕧 ", ".avi": "󰕧 ",
}


def get_icon(path, is_dir=False):
    if is_dir:
        return " "
    ext = os.path.splitext(path)[1].lower()
    return EXT_ICONS.get(ext, "󰈔 ")


def scan_files():
    search_roots = [
        os.path.join(HOME, "Downloads"),
        os.path.join(HOME, "Documents"),
        os.path.join(HOME, "Pictures"),
        os.path.join(HOME, "Desktop"),
        os.path.join(HOME, "temporary"),
        os.path.join(HOME, ".config"),
    ]
    seen = set()
    exclude_dirs = {".git", ".cache", "node_modules", ".local", "__pycache__", ".npm", ".cargo", ".rustup", "brain", ".system_generated"}

    for root_dir in search_roots:
        if not os.path.isdir(root_dir):
            continue
        for current_root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith(".")]
            depth = current_root[len(HOME):].count(os.sep)
            if depth > 4:
                continue

            for d in dirs:
                full_path = os.path.join(current_root, d)
                if full_path not in seen:
                    seen.add(full_path)
                    rel_path = full_path.replace(HOME, "~")
                    print(f"  {d}/  \0info\x1f{full_path}\x1fmeta\x1f{d} {rel_path}")

            for f in files:
                if f.startswith("."):
                    continue
                full_path = os.path.join(current_root, f)
                if full_path not in seen:
                    seen.add(full_path)
                    icon = get_icon(f, is_dir=False)
                    rel_path = full_path.replace(HOME, "~")
                    print(f"{icon} {f}  \0info\x1f{full_path}\x1fmeta\x1f{f} {rel_path}")

            if len(seen) > 2500:
                return


def open_target(target):
    target = target.strip()
    if not target:
        return
    # Extract path if it was passed with info
    target_path = os.environ.get("ROFI_INFO", "")
    if not target_path or not os.path.exists(target_path):
        target_path = target
        for icon in EXT_ICONS.values():
            if target_path.startswith(icon):
                target_path = target_path[len(icon):].strip()
        if target_path.startswith(" "):
            target_path = target_path[2:].strip()
        if "  " in target_path:
            target_path = target_path.split("  ")[0].strip()
        target_path = os.path.expanduser(target_path)

    if not os.path.exists(target_path):
        return

    if os.path.isdir(target_path):
        subprocess.Popen(
            ["alacritty", "-e", "ranger", target_path],
            start_new_session=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    else:
        subprocess.Popen(
            ["xdg-open", target_path],
            start_new_session=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1].strip():
            open_target(sys.argv[1])
        else:
            scan_files()
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(0)
