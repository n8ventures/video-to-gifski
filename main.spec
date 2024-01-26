    # -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas = [
    ('C:\\\\python312\\\\lib\\\\site-packages\\\\tkinterdnd2', 'tkinterdnd2'), 
    ('ico.ico', '.'), 
    ('.\\\\buildandsign\\\\ico\\\\ico.png', '.')
    ]
datas += collect_data_files('pyinstaller_hooks_contrib.collect')


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[
        ('.\\buildandsign\\bin\\ffplay.exe', '.'),
        ('.\\buildandsign\\bin\\ffmpeg.exe', '.'),
        ('.\\buildandsign\\bin\\ffprobe.exe', '.'),
        ('.\\buildandsign\\bin\\gifski.exe', '.'),
        
        ],
    datas=datas,
    hiddenimports=['tkinterdnd2', 'tkinter', 'PIL'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    
)
pyz = PYZ(a.pure)

exe = EXE(
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
