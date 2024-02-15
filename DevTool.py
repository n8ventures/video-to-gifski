import textwrap
import argparse
import os
import sys
import subprocess
import requests
import json
from tqdm import tqdm
import re
from __version__ import __version__,__ffmpegversion__, __gifskiversion__, __updaterversion__, __appname__, __updatername__

class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def printColor(COLOR, string):
    print(COLOR + string + Color.END)

note = '''\
    Hi, this has been created by N8 because he forgets shit. He\'s now made it availabe to create a full version of the program.
    Anyways, here\'s all the need-to-know when exporting it into an .exe.

    Note: this only covers creating full versions of the program. But I do have plans to check internal updates using this script.
    '''

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,description=textwrap.dedent(note))

console = 'False'
ff = 'full'

python_directory = sys.prefix
site_packages_path = os.path.join(python_directory, 'lib', 'site-packages') 
site_packages_path = site_packages_path.replace('\\', '\\\\')
    
def genMainSpec(ff, console):

    if any(char.isalpha() for char in __version__):
        icon = 'icoDev.ico'
    else:
        icon = 'ico.ico'

    a = f'''\
    # -*- mode: python ; coding: utf-8 -*-
    from PyInstaller.utils.hooks import collect_data_files
    
    excludes = ['test.py', 'updater.py', 'DevTool.py']
    
    datas = [ 
        ('ico.ico', '.'),
        ('icoDev.ico', '.'),
        ('.\\\\buildandsign\\\\ico\\\\amor.png', '.'),
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
        hiddenimports=['tkinterdnd2', 'tkinter', 'PIL', 'requests'],
        hookspath=[],
        hooksconfig={},
        runtime_hooks=[],
        excludes=excludes,
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
    a = f'''\
    # -*- mode: python ; coding: utf-8 -*-
    from PyInstaller.utils.hooks import collect_data_files
    
    excludes = ['test.py', 'updater.py', 'DevTool.py']
    
    datas = [ 
        ('icoUpdater.ico', '.'),
        ('.\\\\buildandsign\\\\ico\\\\n8.png', '.'),
        ('{site_packages_path}\\\\tkinterdnd2', 'tkinterdnd2'),
        ('{site_packages_path}\\\\requests', 'requests'), 
        ('{site_packages_path}\\\\tqdm', 'tqdm'), 
        
    ]
    datas += collect_data_files('pyinstaller_hooks_contrib.collect')

    a = Analysis( # type: ignore
        ['updater.py'],
        pathex=[],
        binaries=[],\n'''
    b ='''\
        datas=datas,
        hiddenimports=['tkinterdnd2', 'tkinter', 'tqdm'],
        hookspath=[],
        hooksconfig={},
        runtime_hooks=[],
        excludes=excludes,
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
        name='updater',
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
        icon=['icoUpdater.ico'],
        )'''
    a = textwrap.dedent(a)
    b = textwrap.dedent(b)
    c = textwrap.dedent(c) 
    with open('updater.spec', 'w') as spec_file:
        spec_file.write(a.__str__())
        spec_file.write(b.__str__())
        spec_file.write(c.__str__())

def buildAndSign():
    build_main = 'pyinstaller ./main.spec'
    build_updater = 'pyinstaller ./updater.spec'
    printColor(Color.GREEN, 'Building main.exe...')
    subprocess.run(build_main, shell=True)
    printColor(Color.GREEN, 'Building updater.exe...')
    subprocess.run(build_updater, shell=True)

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
    main_sign_command = f'{signtool_exe} sign /f "{script_directory}\\buildandsign\\n8cert.pfx" /p n8123 /t http://timestamp.digicert.com /v "{script_directory}\\dist\\main.exe"'
    printColor(Color.GREEN, 'Signing main.exe...')
    subprocess.run(main_sign_command, shell=True)
    
    main_sign_command = f'{signtool_exe} sign /f "{script_directory}\\buildandsign\\n8cert.pfx" /p n8123 /t http://timestamp.digicert.com /v "{script_directory}\\dist\\Updater.exe"'
    printColor(Color.GREEN, 'Signing updater.exe...')
    subprocess.run(main_sign_command, shell=True)


    # rename newly built main.exe
    os.chdir(script_directory)
    os.chdir('./dist')

    old_main = 'main.exe'
    old_updater = 'updater.exe'
    new_main = f'{__appname__}.exe'
    new_updater = f'{__updatername__}.exe'

    if os.path.exists(new_main):
        os.remove(new_main)
        printColor(Color.YELLOW, f'\nremoved {new_main}!') 
    if os.path.exists(new_updater):
        os.remove(new_updater)
        printColor(Color.YELLOW, f'\nremoved {new_updater}!') 

    # Rename the file after signing
    os.rename(old_main, new_main)
    printColor(Color.GREEN, f'\n{__appname__} EXE Build version {__version__} DONE!')
    os.rename(old_updater, new_updater)
    printColor(Color.GREEN, f'\n{__updatername__} EXE Build version {__updaterversion__} DONE!')

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

def check_and_update_local():
    ffmpeg = '.\\buildandsign\\bin\\full\\ffmpeg.exe'
    gifski= '.\\buildandsign\\bin\\gifski.exe'
    
    def get_ffmpeg_version():
        cmd = [ffmpeg, '-version']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
                version_info = result.stdout
                version = re.search(r'ffmpeg version (\d{4}-\d{2}-\d{2}-git-\w+)', version_info)
                if version:
                    return version.group(1)
                else:
                    print("Version not found.")
                    return None
        else:
            print(f"Error: {result.stderr}")
            return None
    # print(get_ffmpeg_version())
    
    def get_gifski_version():
        cmd = [gifski, '--version']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
                version_info = result.stdout
                version = re.search(r'(\d+(\.\d+)+)', version_info)
                if version:
                    return version.group(1)
                else:
                    print("Version not found.")
                    return None
        else:
            print(f"Error: {result.stderr}")
            return None
    # print(get_gifski_version())

    def update__version__():
        with open('__version__.py', 'r') as file:
            lines = file.readlines()
        for i, line in enumerate(lines):
            if '__ffmpegversion__' in line:
                lines[i] = f'__ffmpegversion__ = \'{get_ffmpeg_version()}\'\n'
            if '__gifskiversion__' in line:
                lines[i] = f'__gifskiversion__= \'{get_gifski_version()}\''
                break
        with open('__version__.py', 'w') as file:
            file.writelines(lines)
    
    update__version__()
    print('Checking and updating local versions on __version__.py...')
parser.add_argument("-f", "--full",action='store_true', help = "export the app.")
parser.add_argument("-c", "--console",action='store_true', help = 'Enable console window. (for testing purposes. Please don\'t use the argument for final export.)')
parser.add_argument("-U","--Update", action ='store_true', help ='[Checks updates on binaries and will ask you to update.')
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
    if not args.full:
        printColor(Color.YELLOW, 'You can\'t use this arguement alone. Use it with \'-f\'.(ex. DevTool.py -c -f)')

if args.full:
    check_and_update_local()
    genMainSpec(ff, console)
    genUpdaterSpec()
    buildAndSign()

if args.Update:
    ffmpegRepo = ffmpeg_GyanDev()
    gifskiRepo = get_latest_release_version('ImageOptim', 'gifski')
    
    check_and_update_local()
    
    currentFFmpeg = __ffmpegversion__
    currentGifski = __gifskiversion__
    
    print('Checking FFmpeg version...')
    if currentFFmpeg == ffmpegRepo:
        printColor(Color.CYAN, 'FFmpeg does not require an update at the moment.')
    elif ffmpegRepo == '0.0.0':
        printColor(Color.RED,'Request timed out. Please try again later.')
    else:
        printColor(Color.GREEN, f"New version of FFmpeg \'{ffmpegRepo}\' is available.")
        user_agrees = yes_no_prompt("Do you want to download the update?")
        if user_agrees:
            print("Downloading FFmpeg...")
            # latest_file_essentials = f'ffmpeg-{ffmpegRepo}-essentials.7z'
            latest_file_full = f'ffmpeg-{ffmpegRepo}-full.7z'
            # download_file('https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z', latest_file_essentials)
            download_file('https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z', latest_file_full)
            printColor(Color.GREEN, 'Download complete! Please extract them in \'.\\bin\'')
        else:
            print("Skipping FFmpeg update...")
    
    print('Checking Gifski version...')
    if currentGifski == gifskiRepo:
        printColor(Color.CYAN,'Gifski does not require an update at the moment.')
    elif gifskiRepo == '0.0.0':
        printColor(Color.RED,'Request timed out. Please try again later.')
    else:
        printColor(Color.GREEN, f"New version of Gifski \'{gifskiRepo}\' is available.")
        user_agrees = yes_no_prompt("Do you want to download the update?")
        if user_agrees:
            latest_file = f'gifski-{gifskiRepo}.zip'
            download_file(f'https://gif.ski/gifski-{gifskiRepo}.zip', latest_file)
            printColor(Color.GREEN, 'Download complete! Please extract them in \'.\\bin\'')
        else:
            print("Skipping Gifski update...")

