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
from PIL import Image
import shutil
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
script_directory = os.path.dirname(os.path.realpath(__file__))
    
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
        ('.\\\\splash\\\\splash.gif','.'),
        ('.\\\\splash\\\\splashEE.gif','.'),
        ('.\\\\buildandsign\\\\ico\\\\amor.png', '.'),
        ('.\\\\buildandsign\\\\ico\\\\ico3.png', '.'),
        ('.\\\\buildandsign\\\\ico\\\\motionteamph.png', '.'),
        ('{site_packages_path}\\\\tkinterdnd2', 'tkinterdnd2'),
        ('{site_packages_path}\\\\requests', 'requests'), 
        ('{site_packages_path}\\\\PIL', 'PIL'),
        ('{site_packages_path}\\\\pywinctl', 'pywinctl'),
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
        version='__mainVersion.rc',
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
        ('.\\\\buildandsign\\\\ico\\\\ico3Updater.png', '.'),
        ('{site_packages_path}\\\\tkinterdnd2', 'tkinterdnd2'),
        ('{site_packages_path}\\\\requests', 'requests'), 
        ('{site_packages_path}\\\\tqdm', 'tqdm'),
        ('{site_packages_path}\\\\pywinctl', 'pywinctl'), 
        
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
        version='__updaterVersion.rc',
        )'''
    a = textwrap.dedent(a)
    b = textwrap.dedent(b)
    c = textwrap.dedent(c) 
    with open('updater.spec', 'w') as spec_file:
        spec_file.write(a.__str__())
        spec_file.write(b.__str__())
        spec_file.write(c.__str__())

def genMainRC():
    version = __version__.split('.')
    a = f'''
    # UTF-8
    # Please refer to __version__.py
    # For more details about fixed file info 'ffi' see:
    # http://msdn.microsoft.com/en-us/library/ms646997.aspx
    VSVersionInfo(
      ffi=FixedFileInfo(
        # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
        # Set not needed items to zero 0.
        filevers=({version[0]}, {version[1]}, {version[2]}, 0),
        prodvers=({version[0]}, {version[1]}, {version[2]}, 0),
        # Contains a bitmask that specifies the valid bits 'flags'r
        mask=0x3f,
        # Contains a bitmask that specifies the Boolean attributes of the file.
        flags=0x0,
        # The operating system for which this file was designed.
        # 0x4 - NT and there is no need to change it.
        OS=0x4,
        # The general type of file.
        # 0x1 - the file is an application.
        fileType=0x1,
        # The function of the file.
        # 0x0 - the function is not defined for this fileType
        subtype=0x0,
        # Creation date and time stamp.
        date=(0, 0)
        ),
      kids=[
        StringFileInfo(
          [
          StringTable(
            '040904e4',
            [StringStruct('CompanyName', 'N8VENTURES'),
            StringStruct('FileDescription', 'N8\\'s Video to GIF Converter'),
            StringStruct('FileVersion', '{__version__}'),
            StringStruct('InternalName', '{__appname__}'),
            StringStruct('LegalCopyright', '© 2024 N8VENTURES. All rights reserved.'),
            StringStruct('OriginalFilename', '{__appname__}.exe'),
            StringStruct('ProductName', 'N8\\'s Video to GIF Converter'),
            StringStruct('ProductVersion', '{__version__}')])
          ]), 
        VarFileInfo([VarStruct('Translation', [1033, 1252])])
      ]
    )
    '''
    a = textwrap.dedent(a)
    with open('__mainVersion.rc', 'w', encoding='utf-8') as rc_file:
        rc_file.write(a.__str__())

def genUpdaterRC():
    version = __updaterversion__.split('.')
    a = f'''
    # UTF-8
    # Please refer to __version__.py
    # For more details about fixed file info 'ffi' see:
    # http://msdn.microsoft.com/en-us/library/ms646997.aspx
    VSVersionInfo(
      ffi=FixedFileInfo(
        # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
        # Set not needed items to zero 0.
        filevers=({version[0]}, {version[1]}, {version[2]}, 0),
        prodvers=({version[0]}, {version[1]}, {version[2]}, 0),
        # Contains a bitmask that specifies the valid bits 'flags'r
        mask=0x3f,
        # Contains a bitmask that specifies the Boolean attributes of the file.
        flags=0x0,
        # The operating system for which this file was designed.
        # 0x4 - NT and there is no need to change it.
        OS=0x4,
        # The general type of file.
        # 0x1 - the file is an application.
        fileType=0x1,
        # The function of the file.
        # 0x0 - the function is not defined for this fileType
        subtype=0x0,
        # Creation date and time stamp.
        date=(0, 0)
        ),
      kids=[
        StringFileInfo(
          [
          StringTable(
            '040904e4',
            [StringStruct('CompanyName', 'N8VENTURES'),
            StringStruct('FileDescription', 'N8\\'s Video to GIF Converter'),
            StringStruct('FileVersion', '{__updaterversion__}'),
            StringStruct('InternalName', '{__updatername__}'),
            StringStruct('LegalCopyright', '© 2024 N8VENTURES. All rights reserved.'),
            StringStruct('OriginalFilename', '{__updatername__}.exe'),
            StringStruct('ProductName', 'N8\\'s Video to GIF Converter'),
            StringStruct('ProductVersion', '{__updaterversion__}')])
          ]), 
        VarFileInfo([VarStruct('Translation', [1033, 1252])])
      ]
    )
    '''
    a = textwrap.dedent(a)
    with open('__updaterVersion.rc', 'w', encoding='utf-8') as rc_file:
        rc_file.write(a.__str__())

def buildAndSign():
    build_main = 'pyinstaller ./main.spec'
    build_updater = 'pyinstaller ./updater.spec'

    printColor(Color.CYAN, 'Building main.exe...')
    subprocess.run(build_main, shell=True)
    printColor(Color.GREEN, 'main.exe Built!')

    printColor(Color.CYAN, 'Building updater.exe...')
    subprocess.run(build_updater, shell=True)
    printColor(Color.GREEN, 'updater.exe Built!')

    # Sign the executable using signtool
    where_command= 'where /R "C:\\Program Files (x86)" signtool.*'
    where_result = subprocess.run(where_command,capture_output=True, shell=True)
    output_str = where_result.stdout.decode('utf-8')
    output_lines = output_str.split('\r\n')

    if os.path.exists("C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.19041.0\\x64\\"):
        os.chdir("C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.19041.0\\x64\\")
        signtool_exe = 'signtool.exe'
    else:
        signtool_exe = output_lines[0]

    def cert_pass():
        while True:
            response = input(f'{Color.YELLOW}Enter certificate password: {Color.END}')
            if response:
                return response
            else:
                print("No input. Please enter the password: ")

    # Construct the sign_command
    try:
        password = cert_pass()
        main_sign_command = f'{signtool_exe} sign /f "{script_directory}\\buildandsign\\certificate.pfx" /p {password} /tr http://timestamp.digicert.com /td sha256 /v "{script_directory}\\dist\\main.exe"'
        printColor(Color.CYAN, 'Signing main.exe...')
        subprocess.run(main_sign_command, shell=True)
        printColor(Color.GREEN, 'main.exe signed!')

        Updater_sign_command = f'{signtool_exe} sign /f "{script_directory}\\buildandsign\\certificate.pfx" /p {password} /tr http://timestamp.digicert.com /td sha256 /v "{script_directory}\\dist\\Updater.exe"'
        printColor(Color.CYAN, 'Signing updater.exe...')
        subprocess.run(Updater_sign_command, shell=True)
        printColor(Color.GREEN, 'updater.exe signed!')

    except Exception as e:
        print("An error occurred while signing:", e)


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

    if response.status_code != 200:
        return '0.0.0'
    release_info = json.loads(response.text)
    return release_info.get('tag_name', '0.0.0')

def ffmpeg_GyanDev():
    gyan_api = 'https://www.gyan.dev/ffmpeg/builds/git-version'
    response = requests.get(gyan_api)
    if response.status_code != 200:
        return '0.0.0'
    release_info = response
    return release_info.text
    
def yes_no_prompt(prompt):
    while True:
        response = input(f"{prompt} (y/n): ").strip().lower()
        if response in ["yes", "y"]:
            return True
        elif response in ["no", "n"]:
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
                return version[1]
            print("Version not found.")
            return None
        else:
            print(f"Error: {result.stderr}")
            return None

    print('Current FFmpeg version: ', get_ffmpeg_version())

    def get_gifski_version():
        cmd = [gifski, '--version']
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            version_info = result.stdout
            version = re.search(r'(\d+(\.\d+)+)', version_info)
            if version:
                return version[1]
            print("Version not found.")
            return None
        else:
            print(f"Error: {result.stderr}")
            return None

    print('Current Gifski version: ', get_gifski_version())

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

icoFolder = '.\\buildandsign\\ico\\'

def pngtoico(png):
    def resize_image(image_path, output_path, size):
        with Image.open(image_path) as img:
            resized_img = img.resize(size)
            resized_img.save(output_path)
            
    mainDir = '.\\'

    image = png
    sizes = [(16, 16), (32, 32), (48, 48), (128, 128), (256, 256)]

    resize_folder = "resize"
    os.makedirs(resize_folder, exist_ok=True)

    for size in sizes:
        output_path = os.path.join(resize_folder, f"resized_{size[0]}x{size[1]}.png")
        resize_image(image, output_path, size)

    resized_images = [os.path.join(resize_folder, f"resized_{size[0]}x{size[1]}.png") for size in sizes]
    print(resized_images)
    
    if png == f'{icoFolder}ico2.png':
        output_ico = f'{mainDir}EE\\ico.ico'
    elif png == f'{icoFolder}icobeta.png':
        output_ico = f'{mainDir}EE\\icoDev.ico'
        
    elif png == f'{icoFolder}ico3.png':
        output_ico = f'{mainDir}ico.ico'
    elif png == f'{icoFolder}ico3beta.png':
        output_ico = f'{mainDir}icoDev.ico'
    elif png == f'{icoFolder}ico3Updater.png':
        output_ico = f'{mainDir}icoUpdater.ico'
        
    else:
        output_ico = f'{mainDir}{os.path.splitext(os.path.basename(png))[0]}.ico'
        print(output_ico)
    
    cmd = ["magick"] + resized_images + ['-type','TrueColorAlpha', output_ico]
    subprocess.run(cmd, check=True)
    shutil.rmtree('resize')

parser.add_argument("-T", "--Test",action='store_true', help = "test modules.")
parser.add_argument("-B", "--build",action='store_true', help = "build the app.")
parser.add_argument("-c", "--console",action='store_true', help = 'Enable console window. (for testing purposes. Please don\'t use the argument for final export.)')
parser.add_argument("-U","--Update", action ='store_true', help ='Checks updates on binaries and will ask you to update.')
parser.add_argument("-i","--icon", action ='store_true', help ='Updates and generates .ico files for the executables.')
parser.add_argument('-v', '--version', action='version', help='Checks all the version the app uses including the app and updater itself.',
                    version = textwrap.dedent(f"""\
                    App Proper: {__version__}
                    Updater version: {__updaterversion__}
                    FFMPEG: {__ffmpegversion__}
                    Gifski: {__gifskiversion__}
                    """))

args = parser.parse_args()

if args.Test:
    printColor(Color.CYAN, 'Generating mainVersion.rc...')
    genMainRC()
    printColor(Color.GREEN, 'mainVersion.rc Generated!')

    printColor(Color.CYAN, 'Generating updaterVersion.rc...')
    genUpdaterRC()
    printColor(Color.GREEN, 'UpdaterVersion.rc Generated!')

if args.console:
    console = 'True'
    if not args.build:
        printColor(Color.YELLOW, 'You can\'t use this arguement alone. Use it with \'-b\'.(DevTool.py -c -b)')

ffmpegRepo = ffmpeg_GyanDev()
gifskiRepo = get_latest_release_version('ImageOptim', 'gifski')
ffmpeg_dir = '.\\buildandsign\\bin\\full\\'
gifski_dir = f'.\\buildandsign\\bin\\'

if args.build:
    print('############ V E R I F Y I N G ############')

    if not os.path.exists(f'{gifski_dir}gifski.exe'):
        latest_file = f'gifski-{gifskiRepo}'
        gifski_exe = 'gifski.exe'

        printColor(Color.YELLOW, 'gifski.exe NOT FOUND!')
        printColor(Color.CYAN, 'downloading gifski.exe...')
        if gifskiRepo == '0.0.0':
            printColor(Color.RED,'Request timed out. Please try again later.')
            print('Exiting Build process.')
            sys.exit()
        else:
            download_file(f'https://gif.ski/gifski-{gifskiRepo}.zip', f'{gifski_dir}\\{latest_file}.zip')
            printColor(Color.GREEN, 'Gifski Download complete!')

            printColor(Color.CYAN, f'Extracting {latest_file}.zip...')
            subprocess.run(f'C:\\Program Files\\7-Zip\\7z.exe e {gifski_dir}\\{latest_file}.zip -o{gifski_dir} win\\{gifski_exe}')
            printColor(Color.GREEN, 'Latest Gifski binaries extracted!')
            os.remove(os.path.join(gifski_dir, f'{latest_file}.zip'))
    else:
        printColor(Color.GREEN, 'gifski.exe Found!')

    required_ffbins = ['ffmpeg.exe', 'ffplay.exe', 'ffprobe.exe']
    if not all(os.path.exists(os.path.join(ffmpeg_dir, bin)) for bin in required_ffbins):
        latest_file_full = f'ffmpeg-{ffmpegRepo}-full_build'

        if ffmpegRepo == '0.0.0':
            printColor(Color.RED,'Request timed out. Please try again later.')
            print('Exiting Build process.')
            sys.exit()
        else:
            download_file('https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z', os.path.join(ffmpeg_dir, f'{latest_file_full}.7z'))
            printColor(Color.GREEN, 'FFMPEG Download complete!')

            printColor(Color.CYAN, f'Extracting {latest_file_full}.7z...')
            subprocess.run(f'C:\\Program Files\\7-Zip\\7z.exe e {ffmpeg_dir}\\{latest_file_full}.7z -o{ffmpeg_dir} {latest_file_full}\\bin\\*')
            printColor(Color.GREEN, 'Latest FFmpeg binaries extracted!')
            os.remove(os.path.join(ffmpeg_dir, f'{latest_file_full}.7z'))
    else:
        for bin in required_ffbins:
            printColor(Color.GREEN, f'{bin} Found!')

    printColor(Color.CYAN, 'Updating local versions...')
    check_and_update_local()
    printColor(Color.GREEN, 'Versions up to date!')

    printColor(Color.CYAN, 'Checking icons and files...')

    if not os.path.exists('ico.ico'):
        printColor(Color.YELLOW, 'ico.ico NOT FOUND!')
        printColor(Color.CYAN, 'building ico.ico...')
        pngtoico(f'{icoFolder}ico3.png')
        printColor(Color.GREEN, 'ico.ico Ready!')
    else:
        printColor(Color.GREEN, 'ico.ico Found!')

    if not os.path.exists('icoUpdater.ico'):
        printColor(Color.YELLOW, 'ico.ico NOT FOUND!')
        printColor(Color.CYAN, 'building icoUpdater.ico...')
        pngtoico(f'{icoFolder}ico3Updater.png')
        printColor(Color.GREEN, 'icoUpdater.ico Ready!')
    else:
        printColor(Color.GREEN, 'icoUpdater.ico Found!')


    print('############ S P E C  F I L E S ############')
    printColor(Color.CYAN, 'Generating main.spec...')
    genMainSpec(ff, console)
    printColor(Color.GREEN, 'main.spec generated!')

    printColor(Color.CYAN, 'Generating updater.spec...')
    genUpdaterSpec()
    printColor(Color.GREEN, 'updater.spec generated!')

    print('############ V E R S I O N  R C  F I L E S ############')
    printColor(Color.CYAN, 'Generating mainVersion.rc...')
    genMainRC()
    printColor(Color.GREEN, 'mainVersion.rc Generated!')

    printColor(Color.CYAN, 'Generating updaterVersion.rc...')
    genUpdaterRC()
    printColor(Color.GREEN, 'UpdaterVersion.rc Generated!')

    print('############ B U I L D  &  S I G N ############')
    buildAndSign()


if args.Update:

    
    currentFFmpeg = __ffmpegversion__
    currentGifski = __gifskiversion__

    # sevenZip = 'C:\\Program Files\\7-Zip\\7z.exe'
    # if not os.exists(sevenZip):
    #     sevenZip = '.\\buildandsign\\bins\\7z.exe'

    #     if not os.exists(sevenZip):
    #         print('Download and install: 7zip!')

    print('Checking FFmpeg version...')
    if currentFFmpeg == ffmpegRepo:
        printColor(Color.CYAN, 'FFmpeg does not require an update at the moment.')
    elif ffmpegRepo == '0.0.0':
        printColor(Color.RED,'Request timed out. Please try again later.')
    else:
        printColor(Color.GREEN, f"New version of FFmpeg \'{ffmpegRepo}\' is available.")
        if user_agrees := yes_no_prompt(
            f"{Color.YELLOW}Do you want to download the FFmpeg update?{Color.END}"
        ):
            print("Downloading FFmpeg...")
            # latest_file_essentials = f'ffmpeg-{ffmpegRepo}-essentials_build.7z'
            latest_file_full = f'ffmpeg-{ffmpegRepo}-full_build'
            # download_file('https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z', latest_file_essentials)
            download_file('https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z', os.path.join(ffmpeg_dir, f'{latest_file_full}.7z'))
            printColor(Color.GREEN, 'FFmpeg Download complete!')


            ffmpeg_list = ['ffmpeg.exe', 'ffplay.exe', 'ffprobe.exe']
            if all(os.path.exists(os.path.join(ffmpeg_dir, exe)) for exe in ffmpeg_list):
                for exe in ffmpeg_list:
                    printColor(Color.YELLOW, f'Removing {exe}...')
                    os.remove(os.path.join(ffmpeg_dir, exe))
                printColor(Color.GREEN, 'Old FFmpeg binaries removed!')
            else:
                printColor(Color.CYAN, 'Old FFmpeg binaries not found!')

            printColor(Color.CYAN, f'Extracting {latest_file_full}.7z...')
            subprocess.run(f'C:\\Program Files\\7-Zip\\7z.exe e {ffmpeg_dir}\\{latest_file_full}.7z -o{ffmpeg_dir} {latest_file_full}\\bin\\*')
            printColor(Color.GREEN, 'Latest FFmpeg binaries extracted!')
            os.remove(os.path.join(ffmpeg_dir, f'{latest_file_full}.7z'))

        else:
            print("Skipping FFmpeg update...")

    print('Checking Gifski version...')
    if currentGifski == gifskiRepo:
        printColor(Color.CYAN,'Gifski does not require an update at the moment.')
    elif gifskiRepo == '0.0.0':
        printColor(Color.RED,'Request timed out. Please try again later.')
    else:
        printColor(Color.GREEN, f"New version of Gifski \'{gifskiRepo}\' is available.")
        if user_agrees := yes_no_prompt(
            f"{Color.YELLOW}Do you want to download the Gifski update?{Color.END}"
        ):
            latest_file = f'gifski-{gifskiRepo}'
            download_file(f'https://gif.ski/gifski-{gifskiRepo}.zip', f'{gifski_dir}\\{latest_file}.zip')
            printColor(Color.GREEN, 'Gifski Download complete!')
            gifski_exe = 'gifski.exe'
            if os.path.exists(f'{gifski_dir}\\{gifski_exe}'):
                printColor(Color.YELLOW, f'Removing {gifski_exe}...')
                os.remove(os.path.join(gifski_dir, gifski_exe))
                printColor(Color.GREEN, 'Old Gifski binary removed!')
            printColor(Color.CYAN, 'Old gifski binary not found!')

            printColor(Color.CYAN, f'Extracting {latest_file}.zip...')
            subprocess.run(f'C:\\Program Files\\7-Zip\\7z.exe e {gifski_dir}\\{latest_file}.zip -o{gifski_dir} win\\{gifski_exe}')
            printColor(Color.GREEN, 'Latest Gifski binary extracted!')
            os.remove(os.path.join(gifski_dir, f'{latest_file}.zip'))

        else:
            print("Skipping Gifski update...")

    check_and_update_local()

if args.icon:
    if shutil.which('magick') is None:
        print('Install ImageMagick please: https://imagemagick.org/script/download.php')
    else:
        # pngtoico(f'{icoFolder}ico2.png')
        # pngtoico(f'{icoFolder}icobeta.png')
        # pngtoico(f'{icoFolder}icoUpdater.png')
        pngtoico(f'{icoFolder}ico3Updater.png')
        pngtoico(f'{icoFolder}ico3.png')
        pngtoico(f'{icoFolder}ico3beta.png')

