# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller recipe: one self-contained Linux executable (GTK 3 window)."""

page_files = [
    ("src/index.html", "."),
    ("src/styles.css", "."),
    ("src/app.js", "."),
]

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=page_files,
    hiddenimports=["gift_logic", "gift_app", "gi"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "numpy", "pandas", "PyQt5", "PySide2", "PySide6"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="BDAY",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
)
