import textwrap
from __version__ import __version__
def generateSpec():
    a = '''\
    # -*- mode: python ; coding: utf-8 -*-
    from PyInstaller.utils.hooks import collect_data_files
    
    datas = [
        ('C:\\\\python312\\\\lib\\\\site-packages\\\\tkinterdnd2', 'tkinterdnd2'), 
        ('ico.ico', '.'),
        ('icoDev.ico', '.'),
        ('.\\\\buildandsign\\\\ico\\\\ico.png', '.'),
        ('C:\\\\python312\\\\lib\\\\site-packages\\\\requests', 'requests'), 
        ('.\\\\buildandsign\\\\ico\\\\motionteamph.png', '.')
    ]
    datas += collect_data_files('pyinstaller_hooks_contrib.collect')

    a = Analysis( # type: ignore
        ['main.py'],
        pathex=[],
        binaries=[
            ('.\\\\buildandsign\\\\bin\\\\ffplay.exe', '.'),
            ('.\\\\buildandsign\\\\bin\\\\ffmpeg.exe', '.'),
            ('.\\\\buildandsign\\\\bin\\\\ffprobe.exe', '.'),
            ('.\\\\buildandsign\\\\bin\\\\gifski.exe', '.'),
        ],
        datas=datas,
        hiddenimports=['tkinterdnd2', 'tkinter', 'PIL'],
        hookspath=[],
        hooksconfig={},
        runtime_hooks=[],
        excludes=[],
        noarchive=False,
    )\n\n

    pyz = PYZ(a.pure) # type: ignore\n\n'''

    if any(char.isalpha() for char in __version__):
        icon = 'icoDev.ico'
    else:
        icon = 'ico.ico'
    
    b = f'''\
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
        icon=['{icon}'],
        )'''
    a = textwrap.dedent(a)
    b = textwrap.dedent(b)
    with open('main.spec', 'w') as spec_file:
        spec_file.write(a.__str__())
        spec_file.write(b.__str__())
        
if __name__ == '__main__':
    generateSpec()