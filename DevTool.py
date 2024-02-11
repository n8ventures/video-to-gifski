import textwrap
import argparse
import os
import sys
import subprocess
import requests
import json
from tqdm import tqdm
import time
from __version__ import __version__,__ffmpegversion__, __gifskiversion__, __updaterversion__, __appname__

note = '''\
    Hi, this has been created by N8 because he forgets shit. He\'s now made it availabe to create a \"lite\" and full version of the program.
    Anyways, here\'s all the need-to-know when exporting it into an .exe.

    Note: this only covers creating lite and/or full versions of the program. But I do have plans to check internal updates using this script.
    '''

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,description=textwrap.dedent(note))

console = 'False'
ff = 'full'
lite = ''

def genMainSpec(ff, console):
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
        ('ico.ico', '.'),
        ('icoDev.ico', '.'),
        ('.\\\\buildandsign\\\\ico\\\\ico.png', '.'),
        ('.\\\\buildandsign\\\\ico\\\\motionteamph.png', '.'),
        ('{site_packages_path}\\\\tkinterdnd2', 'tkinterdnd2'),
        ('{site_packages_path}\\\\requests', 'requests'), 
        ('{site_packages_path}\\\\PIL', 'PIL')
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

def genUpdaterSpec():
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
        ('ico.ico', '.'),
        ('icoDev.ico', '.'),
        ('.\\\\buildandsign\\\\ico\\\\ico.png', '.'),
        ('.\\\\buildandsign\\\\ico\\\\motionteamph.png', '.'),
        ('{site_packages_path}\\\\requests', 'requests'), 
        ('{site_packages_path}\\\\tqdm', 'tqdm'), 
        
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
    with open('updater.spec', 'w') as spec_file:
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

def get_latest_release_version(repo_owner, repo_name):
    global api_url
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        release_info = json.loads(response.text)
        return release_info.get('tag_name', '0.0.0')
    else:
        return '0.0.0'

def ffmpeg_GyanDev():
    gyan_api = 'https://www.gyan.dev/ffmpeg/builds/git-version'
    response = requests.get(gyan_api)
    if response.status_code == 200:
        release_info = response
        return release_info.text
    else:
        return '0.0.0'
    
def yes_no_prompt(prompt):
    while True:
        response = input(prompt + " (y/n): ").strip().lower()
        if response == "yes" or response == "y":
            return True
        elif response == "no" or response == "n":
            return False
        else:
            print("Please enter 'yes' or 'no'.")

def download_file(url, destination):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    with open(destination, 'wb') as file, tqdm(
            desc=f"Downloading {destination}",
            total=total_size,  
            unit='B',  
            unit_scale=True,  
            unit_divisor=1024,  
            miniters=1, 
            colour='green', 
            ) as progress_bar:
        for chunk in response.iter_content(chunk_size=1024):
            file.write(chunk)
            progress_bar.update(len(chunk))

parser.add_argument("-f", "--full",action='store_true', help = "export the FULL version of the app.")
parser.add_argument("-l", "--lite", action='store_true', help = "export the LITE version of the app.")
parser.add_argument("-c", "--console",action='store_true', help = 'Enable console window. (for testing purposes. Please don\'t use the argument for final export.)')

parser.add_argument("-U","--Update", action ='store_true', help ='[WIP] Checks updates on binaries and will ask you to update.')

parser.add_argument('-v', '--version', action='version', help='checks all the version the app uses including the app and updater itself.',
                    version = textwrap.dedent(f"""\
                    App Proper: {__version__}
                    Updater version: {__updaterversion__}
                    FFMPEG: {__ffmpegversion__}
                    Gifski: {__gifskiversion__}
                    """))
args = parser.parse_args()


if args.console:
    console = 'True'
    if not args.full and not args.lite:
        print('You can\'t use this arguement alone. Use it with \'-f\' or with \'-l\'')
if args.full:
    genMainSpec(ff, console)
    buildAndSign()

if args.lite:
    ff = 'lite'
    lite = '_lite'
    genMainSpec(ff, console)
    buildAndSign()

if args.Update:
    #print('Not Developed Yet.')
    ffmpegRepo = ffmpeg_GyanDev()
    gifskiRepo = get_latest_release_version('ImageOptim', 'gifski')
    currentFFmpeg = __ffmpegversion__
    currentGifski = __gifskiversion__
    
    print('Checking FFmpeg version...')
    if currentFFmpeg == ffmpegRepo:
        print('FFmpeg does not require an update at the moment.')
    elif ffmpegRepo == '0.0.0':
        print('Internet connection unavailable. Please try again later.')
    else:
        print(f"New version of FFmpeg \'{ffmpegRepo}\' is available.")
        user_agrees = yes_no_prompt("Do you want to download the update?")
        if user_agrees:
            print("Downloading FFmpeg...")
            latest_file_essentials = f'ffmpeg-{ffmpegRepo}-essentials.7z'
            latest_file_full = f'ffmpeg-{ffmpegRepo}-full.7z'
            download_file('https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z', latest_file_essentials)
            download_file('https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z', latest_file_full)
        else:
            print("Skipping FFmpeg update...")
    
    print('Checking Gifski version...')
    if currentGifski == gifskiRepo:
        print('FFmpeg does not require an update at the moment.')
    elif gifskiRepo == '0.0.0':
        print('Internet connection unavailable. Please try again later.')
    else:
        print(f"New version of Gifski \'{gifskiRepo}\' is available.")
        user_agrees = yes_no_prompt("Do you want to download the update?")
        if user_agrees:
            latest_file = f'gifski-{gifskiRepo}.zip'
            download_file(f'https://gif.ski/gifski-{gifskiRepo}.zip', latest_file)
            print('Download complete! Please extract them in \'.\\bin\'')
        else:
            print("Skipping Gifski update...")

