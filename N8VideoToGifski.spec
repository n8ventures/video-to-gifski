# -*- mode: python ; coding: utf-8 -*-
import os
import subprocess

from PyInstaller.utils.hooks import (
    collect_all,
    collect_data_files,
    collect_submodules,
    copy_metadata,
    collect_dynamic_libs,
)
from importlib.metadata import PackageNotFoundError
from modules.platformModules import mac, win
from __version__ import __versionMac__ as __version__
from __version__ import __author__, __appname__, __internal_app_name__

block_cipher = None


def safe_copy_metadata(package_name):
    try:
        return copy_metadata(package_name)
    except PackageNotFoundError:
        return []


datas = [
    ("build_count.json", "."),
    ("buildandsign/splash/splash.gif", "assets/splash"),
    ("buildandsign/themes/Marcel.json", "assets/themes"),
]
binaries = []
hiddenimports = []

# Include python-docx package data (templates) used for the "Save As DOCX" export
datas += safe_copy_metadata("pillow")
datas += safe_copy_metadata("packaging")
datas += safe_copy_metadata("scipy")
datas += safe_copy_metadata("emoji")
datas += safe_copy_metadata("tqdm")

datas += collect_data_files("certifi")
datas += collect_data_files("customtkinter")
datas += collect_data_files("tkinterdnd2")
datas += collect_data_files("CTkToolTip")


# ffmpeg/ffprobe — fetched once at build time (ffmpeg.martin-riedl.de, arm64)
# into bin/Silicon/, bundled here as `binaries` rather than `datas` so
# PyInstaller preserves the executable bit and treats them as Mach-O
# binaries (picked up by your codesigning step in devtools.py, same as any
# other binary in the bundle). No more static_ffmpeg / runtime download.

if mac:
    binaries += [
        ("buildandsign/bin/MacOS/ffmpeg", "bin/MacOS"),
        ("buildandsign/bin/MacOS/ffprobe", "bin/MacOS"),
        ("buildandsign/bin/MacOS/gifski", "bin/MacOS"),
        ("buildandsign/bin/MacOS/ffplay", "bin/MacOS"),
    ]
    datas += [
        ("buildandsign/icons/MacOS/icon.icns", "assets/icons/MacOS"),
        ("buildandsign/icons/MacOS/icon.png", "assets/icons/MacOS"),
    ]
    icon = "buildandsign/icons/MacOS/icon.icns"
if win:
    binaries += [
        ("buildandsign/bin/Windows/ffmpeg.exe", "bin/Windows"),
        ("buildandsign/bin/Windows/ffprobe.exe", "bin/Windows"),
        ("buildandsign/bin/Windows/gifski.exe", "bin/Windows"),
        ("buildandsign/bin/Windows/ffplay.exe", "bin/Windows"),
    ]
    datas += [
        ("buildandsign/icons/Windows/icon.ico", "assets/icons/Windows"),
        ("buildandsign/icons/Windows/icon.png", "assets/icons/Windows"),
    ]
    icon = "buildandsign/icons/Windows/icon.ico"

a = Analysis(  # type: ignore
    ["main.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=["./hooks"],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)  # type: ignore

exe = EXE(  # type: ignore
    pyz,
    a.scripts,
    a.binaries if win else [],
    a.datas if win else [],
    exclude_binaries=not win,
    name=f"{__appname__}",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,  # signing handled post-build by devtools.py
    entitlements_file=None,  # avoids --timestamp failures with Apple Dev certs
    icon=icon,
    version=None if mac else "main.rc",
)

if mac:
    coll = COLLECT(  # type: ignore
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=False,
        upx_exclude=[],
        name=f"{__appname__}",
    )

    app = BUNDLE(  # type: ignore
        coll,
        name=f"{__appname__}.app",
        icon=icon,
        bundle_identifier=f"{__internal_app_name__}",
        version=os.environ.get("BUILD_VERSION", __version__),
        info_plist={
            "CFBundleDisplayName": f"{__appname__}",
            "CFBundleShortVersionString": os.environ.get("BUILD_VERSION", __version__),
            "NSHighResolutionCapable": True,
            "NSRequiresAquaSystemAppearance": False,  # respects dark/light mode
            "LSMinimumSystemVersion": "13.0",
            # for when you add AppleScript later:
            "NSAppleEventsUsageDescription": f"{__appname__} uses AppleScript to open Finder windows.",
        },
    )
