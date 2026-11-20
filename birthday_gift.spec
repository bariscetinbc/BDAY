# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller recipe: one self-contained Windows executable."""

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
    hiddenimports=["gift_logic", "gift_app_tk"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "numpy", "pandas", "PyQt5", "PySide2", "PySide6"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="DogumGunuHediyesi",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
