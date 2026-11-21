#!/usr/bin/env python3
"""Build the ready-to-run Linux download for BDAY.

Run `python3 build_linux.py` on a Linux machine with PyInstaller installed.
If a one-file executable has already been built by PyInstaller, pass it with
`python3 build_linux.py --binary /path/to/BDAY` to package it without rebuilding.
"""

from __future__ import annotations

import argparse
import io
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOWNLOADS = ROOT / "downloads" / "Linux"
ARCHIVE = DOWNLOADS / "BDAY-Linux.tar.gz"

README = """BDAY for Linux
==============

This folder contains a self-contained Linux program. It does not need Python
or a web browser to be installed.

How to run
----------

1. Extract BDAY-Linux.tar.gz (right click -> Extract Here, or:
   tar -xzf BDAY-Linux.tar.gz).
2. Open the BDAY-Linux folder.
3. Double-click the file named BDAY. If your desktop asks, choose
   "Run" / "Allow launching". If double-clicking does nothing, open a terminal
   in this folder and type: ./BDAY

The window has fields for date, name, amount, currency and IBAN. It looks up
the exchange rate for the chosen date and prepares the Turkish birthday gift
message. If you have a personal TCMB EVDS key you can enter it in the window;
otherwise a public exchange-rate service is used. You can also type the rate
yourself when you are offline.

Settings (language, theme, currency and saved key) are kept in ~/.bday.json.

Requires a 64-bit Linux desktop (x86_64) with GTK 3 available. On Debian or
Ubuntu, if the window does not open, install GTK 3 with:
  sudo apt install libgtk-3-0

BDAY-Linux
"""


def _add_readable(tar: tarfile.TarFile, name: str, text: str) -> None:
    data = text.encode("utf-8")
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mode = 0o644
    info.mtime = 0
    tar.addfile(info, io.BytesIO(data))


def _make_archive(binary: Path) -> None:
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="bday-linux-") as temp:
        stage = Path(temp) / "BDAY-Linux"
        stage.mkdir()
        target = stage / "BDAY"
        shutil.copy2(binary, target)
        target.chmod(0o755)
        (stage / "OKUMA-BENI.txt").write_text(README, encoding="utf-8")
        (stage / "README.txt").write_text(README, encoding="utf-8")
        with tarfile.open(ARCHIVE, "w:gz") as tar:
            tar.add(stage, arcname="BDAY-Linux")
    print(f"Created {ARCHIVE} ({ARCHIVE.stat().st_size / 1024 / 1024:.1f} MB)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, help="an existing PyInstaller BDAY executable")
    args = parser.parse_args()

    if args.binary:
        binary = args.binary.resolve()
        if not binary.is_file():
            print(f"No such file: {binary}", file=sys.stderr)
            return 1
    else:
        if shutil.which("pyinstaller") is None:
            print("PyInstaller is not installed. Install it with: pip install pyinstaller", file=sys.stderr)
            return 1
        with tempfile.TemporaryDirectory(prefix="bday-build-") as temp:
            out = Path(temp) / "out"
            work = Path(temp) / "work"
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "PyInstaller",
                    "--noconfirm",
                    "--clean",
                    "--distpath",
                    str(out),
                    "--workpath",
                    str(work),
                    str(ROOT / "bday_linux.spec"),
                ],
                cwd=ROOT,
                check=True,
            )
            binary = out / "BDAY"
            if not binary.is_file():
                print("PyInstaller did not produce a BDAY executable.", file=sys.stderr)
                return 1
            _make_archive(binary)
            return 0
    _make_archive(binary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
