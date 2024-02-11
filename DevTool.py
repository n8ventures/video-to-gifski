import textwrap
import argparse
import os
import sys
import subprocess
from __version__ import __version__, __ffmpegfullversion__, __ffmpegliteversion__, __gifskiversion__, __updaterversion__, __appname__

note = '''\
    Hi, this has been created by N8 because he forgets shit. He\'s now made it availabe to create a \"lite\" and full version of the program.
    Anyways, here\'s all the need-to-know when exporting it into an .exe.

    Note: this only covers creating lite and/or full versions of the program. But I do have plans to check internal updates using this script.
    '''

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,description=textwrap.dedent(note))

console = 'False'
ff = 'full'
lite = ''

def generateSpec(ff, console):
    python_directory = sys.prefix
    site_packages_path = os.path.join(python_directory, 'lib', 'site-packages') 
    site_packages_path = site_packages_path.replace('\\', '\\\\')
    if any(char.isalpha() for char in __version__):
        icon = 'icoDev.ico'
    else:
        icon = 'ico.ico'

    a = f'''\
    # -*- mode: python ; coding: utf-8 -*-
    from PyInstaller.utils.hooks import collect_data_files
    
    datas = [
        ('{site_packages_path}\\\\tkinterdnd2', 'tkinterdnd2'), 
        ('ico.ico', '.'),
        ('icoDev.ico', '.'),
        ('.\\\\buildandsign\\\\ico\\\\ico.png', '.'),
        ('{site_packages_path}\\\\requests', 'requests'), 
        ('.\\\\buildandsign\\\\ico\\\\motionteamph.png', '.')
    ]
    datas += collect_data_files('pyinstaller_hooks_contrib.collect')

    a = Analysis( # type: ignore
        ['main.py'],
        pathex=[],
        binaries=[
            ('.\\\\buildandsign\\\\bin\\\\{ff}\\\\ffplay.exe', '.'),
            ('.\\\\buildandsign\\\\bin\\\\{ff}\\\\ffmpeg.exe', '.'),
            ('.\\\\buildandsign\\\\bin\\\\{ff}\\\\ffprobe.exe', '.'),
            ('.\\\\buildandsign\\\\bin\\\\gifski.exe', '.'),
        ],\n'''
    b ='''\
        datas=datas,
        hiddenimports=['tkinterdnd2', 'tkinter', 'PIL'],
        hookspath=[],
        hooksconfig={},
        runtime_hooks=[],
        excludes=[],
        noarchive=False,
    )\n\n

    pyz = PYZ(a.pure) # type: ignore\n\n'''

    c = f'''\
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
        console={console},
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=['{icon}'],
        )'''
    a = textwrap.dedent(a)
    b = textwrap.dedent(b)
    c = textwrap.dedent(c) 
    with open('main.spec', 'w') as spec_file:
        spec_file.write(a.__str__())
        spec_file.write(b.__str__())
        spec_file.write(c.__str__())
    
def buildAndSign():
    build_command = 'pyinstaller ./main.spec'
    subprocess.run(build_command, shell=True)

    # Sign the executable using signtool
    where_command= 'where /R "C:\\Program Files (x86)" signtool.*'
    where_result = subprocess.run(where_command,capture_output=True, shell=True)
    output_str = where_result.stdout.decode('utf-8')
    output_lines = output_str.split('\r\n')

    if os.path.exists("C:\\Program Files (x86)\\Windows Kits\\10\\App Certification Kit"):
        os.chdir("C:\\Program Files (x86)\\Windows Kits\\10\\App Certification Kit")
        signtool_exe = 'signtool.exe'
    else:
        signtool_exe = output_lines[0]

    script_directory = os.path.dirname(os.path.realpath(__file__))
    # Construct the sign_command
    sign_command = f'{signtool_exe} sign /f "{script_directory}\\buildandsign\\n8cert.pfx" /p n8123 /t http://timestamp.digicert.com /v "{script_directory}\\dist\\main.exe"'
    subprocess.run(sign_command, shell=True)

    # rename newly built main.exe
    os.chdir(script_directory)
    os.chdir('./dist')

    old_name = 'main.exe'
    new_name = f'{__appname__}-{__version__}{lite}.exe'

    if os.path.exists(new_name):
        os.remove(new_name)
        print(f'\nremoved {new_name}!') 

    # Rename the file after signing
    os.rename(old_name, new_name)
    print(f'\nEXE Build version {__version__} DONE!')

parser.add_argument("-f", "--full",action='store_true', help = "export the FULL version of the app.")
parser.add_argument("-l", "--lite", action='store_true', help = "export the LITE version of the app.")
parser.add_argument("-c", "--console",action='store_true', help = 'Enable console window. (for testing purposes. Please don\'t use the argument for final export.)')

parser.add_argument("-U","--Update", action ='store_true', help ='[WIP] Checks updates on binaries and will ask you to update.')

parser.add_argument('-v', '--version', action='version', help='checks all the version the app uses including the app and updater itself.',
                    version = textwrap.dedent(f"""\
                    App Proper: {__version__}
                    Updater version: {__updaterversion__}
                    FFMPEG (full): {__ffmpegfullversion__}
                    FFMPEG (lite): { __ffmpegliteversion__}
                    Gifski: {__gifskiversion__}
                    """))
args = parser.parse_args()

if args.console:
    console = 'True'
    if not args.full and not args.lite:
        print('You can\'t use this arguement alone. Use it with \'-f\' or with \'-l\'')
if args.full:
    generateSpec(ff, console)
    buildAndSign()

if args.lite:
    ff = 'lite'
    lite = '_lite'
    generateSpec(ff, console)
    buildAndSign()

if args.Update:
    print('Not Developed Yet.')

if __name__ == '__main__':
    parser.print_help()