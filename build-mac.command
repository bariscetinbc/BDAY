#!/bin/sh
# Double-click this file on a Mac to build the application.
cd "$(dirname "$0")" || exit 1
echo "Installing the packaging tool (first time only)…"
python3 -m pip install --upgrade pyinstaller || exit 1
echo "Checking the calculations…"
python3 selftest.py || exit 1
echo "Building the Mac application…"
pyinstaller --noconfirm --clean bday_macos.spec || exit 1
echo
echo "Done. Your application is: dist/BDAY.app"
echo "You can move it to your Applications folder and double-click it."
