#!/usr/bin/env python3
"""Single entry point for the birthday gift desktop app on every platform.

Linux uses the existing GTK window. Windows and macOS use the Tk window that
ships with the standard Python installer. If neither toolkit can start, the
built-in offline page opens in the default browser so the tool is still usable.
"""

from __future__ import annotations

import importlib
import os
import platform
import sys
import webbrowser
from pathlib import Path


def _resource(name: str) -> Path:
    """Find a bundled file both when running from source and from PyInstaller."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    candidate = base / name
    if candidate.exists():
        return candidate
    return Path(__file__).resolve().parent / name


def main() -> None:
    system = platform.system()
    has_display = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    if system == "Linux":
        modules = ["gift_app"] if has_display else []
    else:
        modules = ["gift_app_tk", "gift_app"]

    for module_name in modules:
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:  # missing toolkit or display: try the next one
            print(f"{module_name} could not start: {exc}", file=sys.stderr)
            continue
        try:
            module.main()
        except Exception as exc:
            print(f"{module_name} failed: {exc}", file=sys.stderr)
            continue
        return

    page = _resource("index.html")
    if page.exists():
        print("Opening the local gift page in your browser…")
        webbrowser.open(page.resolve().as_uri())
    else:
        print("No desktop toolkit is available. Please open index.html in a browser.", file=sys.stderr)


if __name__ == "__main__":
    main()
