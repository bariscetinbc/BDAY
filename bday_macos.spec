# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller recipe: a double-clickable macOS .app."""

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
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="BDAY",
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

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="BDAY",
)

app = BUNDLE(
    coll,
    name="BDAY.app",
    icon=None,
    bundle_identifier="com.bday.app",
    info_plist={
        "NSHighResolutionCapable": True,
        "CFBundleDisplayName": "BDAY",
        "LSMinimumSystemVersion": "10.13.0",
    },
)
