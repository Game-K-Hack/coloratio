# PyInstaller spec - Coloratio
# Build : pyinstaller build.spec
# Sortie : dist/Coloratio.exe (one-file)

# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

hidden = []
hidden += collect_submodules("PIL")
hidden += [
    "PyQt5.QtCore",
    "PyQt5.QtGui",
    "PyQt5.QtWidgets",
    "numpy",
]

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    datas=[("logo.ico", "."), ("logo.png", ".")],
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # On retire les modules Qt inutiles pour alleger le binaire
        "PyQt5.QtNetwork",
        "PyQt5.QtQml",
        "PyQt5.QtQuick",
        "PyQt5.QtWebEngine",
        "PyQt5.QtWebEngineCore",
        "PyQt5.QtWebEngineWidgets",
        "PyQt5.QtMultimedia",
        "PyQt5.QtMultimediaWidgets",
        "PyQt5.QtBluetooth",
        "PyQt5.QtSerialPort",
        "PyQt5.QtSql",
        "PyQt5.QtTest",
        "PyQt5.QtDesigner",
        "PyQt5.QtHelp",
        "PyQt5.QtSvg",
        "PyQt5.QtXml",
        "PyQt5.Qsci",
        # Backends matplotlib/scipy au cas ou Pillow les tirerait
        "matplotlib",
        "scipy",
        "tkinter",
        "test",
        "unittest",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="Coloratio",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[
        "vcruntime140.dll",
        "python3.dll",
        "Qt5Core.dll",
        "Qt5Gui.dll",
        "Qt5Widgets.dll",
    ],
    runtime_tmpdir=None,
    console=False,            # GUI : pas de console
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="logo.ico",
)
