# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

excludes = ['test.py', 'updater.py', 'DevTool.py']

datas = [ 
    ('ico.ico', '.'),
    ('icoDev.ico', '.'),
    ('.\\buildandsign\\ico\\amor.png', '.'),
    ('.\\buildandsign\\ico\\motionteamph.png', '.'),
    ('C:\\Python312\\lib\\site-packages\\tkinterdnd2', 'tkinterdnd2'),
    ('C:\\Python312\\lib\\site-packages\\requests', 'requests'), 
    ('C:\\Python312\\lib\\site-packages\\PIL', 'PIL')
]
datas += collect_data_files('pyinstaller_hooks_contrib.collect')

a = Analysis( # type: ignore
    ['main.py'],
    pathex=[],
    binaries=[
        ('.\\buildandsign\\bin\\full\\ffplay.exe', '.'),
        ('.\\buildandsign\\bin\\full\\ffmpeg.exe', '.'),
        ('.\\buildandsign\\bin\\full\\ffprobe.exe', '.'),
        ('.\\buildandsign\\bin\\gifski.exe', '.'),
    ],
    datas=datas,
    hiddenimports=['tkinterdnd2', 'tkinter', 'PIL', 'requests'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
)



pyz = PYZ(a.pure) # type: ignore

exe = EXE( # type: ignore
pyz,
a.scripts,
a.binaries,
a.datas,
[],
name='main',
debug=False,
bootloader_ignore_signals=False,
strip=False,
upx=True,
upx_exclude=[],
runtime_tmpdir=None,
console=False,
disable_windowed_traceback=False,
argv_emulation=False,
target_arch=None,
codesign_identity=None,
entitlements_file=None,
icon=['ico.ico'],
)