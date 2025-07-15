import textwrap
import argparse
import os
import sys
import subprocess
import requests
import json
from tqdm import tqdm
import re
from __version__ import (
    __version__,
    __ffmpegversion__, 
    __gifskiversion__, 
    __appname__)
from PIL import Image
import shutil

from modules.platformModules import win, mac
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
        icon = '.\\\\icons\\\\win\\\\icoDev.ico'
    else:
        icon = '.\\\\icons\\\\win\\\\ico.ico'

    a = f'''\
    # -*- mode: python ; coding: utf-8 -*-
    from PyInstaller.utils.hooks import collect_data_files
    
    excludes = ['test.py', 'DevTool.py']
    
    datas = [ 
        ('.\\\\icons\\\\win\\\\icoDev.ico', '.'),
        ('.\\\\icons\\\\win\\\\ico.ico', '.'),
        ('.\\\\splash\\\\splash.gif','.'),
        ('.\\\\splash\\\\splashEE.gif','.'),
        ('.\\\\buildandsign\\\\ico\\\\amor.png', '.'),
        ('.\\\\buildandsign\\\\ico\\\\ico3.png', '.'),
        ('.\\\\buildandsign\\\\ico\\\\motionteamph.png', '.'),
        ('{site_packages_path}\\\\tkinterdnd2', 'tkinterdnd2'),
        ('{site_packages_path}\\\\emoji','emoji'),
        ('{site_packages_path}\\\\sv_ttk','sv_ttk')
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
        hiddenimports=[],
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
        debug={console},
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
            StringStruct('FileDescription', 'N8\\'s Video to Gifski'),
            StringStruct('FileVersion', '{__version__}'),
            StringStruct('InternalName', 'N8\\'s Video To Gifski'),
            StringStruct('LegalCopyright','Copyright © 2024-2025 John Nathaniel Calvara. Licensed under the MIT License.'),
            StringStruct('OriginalFilename', 'N8\\'s Video To Gifski.exe'),
            StringStruct('ProductName', 'N8\\'s Video to Gifski'),
            StringStruct('ProductVersion', '{__version__}')])
          ]), 
        VarFileInfo([VarStruct('Translation', [1033, 1252])])
      ]
    )
    '''
    a = textwrap.dedent(a)
    with open('__mainVersion.rc', 'w', encoding='utf-8') as rc_file:
        rc_file.write(a.__str__())

def buildAndSign():
    def cert_pass():
        while True:
            if win:
                response = input(f'{Color.YELLOW}Enter certificate password: {Color.END}')
            elif mac:
                response = input(f'{Color.YELLOW}Enter identity: {Color.END}')
            if response:
                return response
            else:
                print("No input. Please enter the password: ")
    if win:
        build_main = 'pyinstaller ./main.spec'

        printColor(Color.CYAN, 'Building main.exe...')
        subprocess.run(build_main, shell=True)
        printColor(Color.GREEN, 'main.exe Built!')

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

        # Construct the sign_command
        try:
            password = cert_pass()
            main_sign_command = f'{signtool_exe} sign /f "{script_directory}\\buildandsign\\certificate.pfx" /p {password} /tr http://timestamp.digicert.com /td sha256 /v "{script_directory}\\dist\\main.exe"'
            printColor(Color.CYAN, 'Signing main.exe...')
            subprocess.run(main_sign_command, shell=True)
            printColor(Color.GREEN, 'main.exe signed!')

        except Exception as e:
            print("An error occurred while signing:", e)


        # rename newly built main.exe
        os.chdir(script_directory)
        os.chdir('./dist')

        old_main = 'main.exe'
        new_main = f'{__appname__.replace("'", "").replace(" ", "")}.exe'

        if os.path.exists(new_main):
            os.remove(new_main)
            printColor(Color.YELLOW, f'\nremoved {new_main}!')

        # Rename the file after signing
        os.rename(old_main, new_main)
    elif mac:
        # Remove build and dist folders
        printColor(Color.YELLOW, 'Building removing "build" folder...')
        subprocess.run(['rm', '-rf', 'build', 'dist', 'N8\'s Video To Gifski.dmg'], check=True)
        printColor(Color.GREEN, '"build" folder removed!')
        # Create App using py2app
        printColor(Color.CYAN, 'Building main.app...')
        subprocess.run(['python', 'mac_py2app_setup.py', 'py2app'], check=True)
        printColor(Color.GREEN, 'main.app Built!')
        
        # Sign The .app
        printColor(Color.CYAN, 'signing the .app...')
        apple_dev = cert_pass()
        build_app_path = os.path.abspath(r"./dist/N8's Video To Gifski.app")
        subprocess.run([
            'codesign', '--sign', apple_dev, '--deep', '--force', '--timestamp', build_app_path
        ], check=True)
        printColor(Color.GREEN, '.app Signed!')

        # Create DMG for distribution
        printColor(Color.CYAN, 'Building DMG for distribution...')
        subprocess.run([
            'dmgbuild', 
            '-s', 'dmgbuild.py', 
            '-D', 'filesystem="UDZO"', 
            "N8's Video To Gifski",
            "N8's Video To Gifski.dmg"
        ], check=True)
        printColor(Color.GREEN, 'DMG Built!')
        
        # Sign the DMG
        printColor(Color.CYAN, 'signing the .dmg...')
        apple_dev = apple_dev
        dmg_path = os.path.abspath(r"./N8's Video To Gifski.dmg")
        subprocess.run([
            'codesign', '--sign', apple_dev, '--deep', '--force', '--timestamp', dmg_path
        ], check=True)
        printColor(Color.GREEN, '.dmg Signed!')
        
        # Rename DMG
        printColor(Color.CYAN, 'renaming the .dmg...')
        new_dmg_path = os.path.abspath(r"./MacOS - N8 Video To Gifski.dmg")
        os.rename(dmg_path, new_dmg_path)
        printColor(Color.GREEN, '.dmg renamed!')

    printColor(Color.GREEN, f'\n{__appname__} Build version {__version__} DONE!')

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

base_dir = os.path.abspath(os.path.dirname(__file__)) 

def check_and_update_local():
    if win:
        ffmpeg = '.\\buildandsign\\bin\\full\\ffmpeg.exe'
        gifski= '.\\buildandsign\\bin\\gifski.exe'
    elif mac:
        MacOS_bin_dir = os.path.join(base_dir, 'buildandsign', 'bin', 'MacOS')
        ffmpeg = os.path.join(MacOS_bin_dir, 'ffmpeg')
        gifski = os.path.join(MacOS_bin_dir, 'gifski')

    def get_ffmpeg_version():
        cmd = [ffmpeg, '-version']
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            version_info = result.stdout
            if win:
                version = re.search(r'ffmpeg version (\d{4}-\d{2}-\d{2}-git-\w+)', version_info)
            elif mac:
                version = re.search(r'ffmpeg version (\S+)', version_info)
            
            if version:
                if win:
                    return version[1]
                elif mac:
                    clean_version = version.group(1).split('-')[0] 
                    clean_version += '-' 
                    clean_version +=  version.group(1).split('-')[1] 
                    clean_version += '-'
                    clean_version +=  version.group(1).split('-')[2]
                    return clean_version 

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
            if win:
                if '__ffmpegversion__' in line:
                    lines[i] = f'__ffmpegversion__ = \'{get_ffmpeg_version()}\'\n'
                if '__gifskiversion__' in line:
                    lines[i] = f'__gifskiversion__= \'{get_gifski_version()}\'\n'
                    break
            elif mac:
                if '__ffmpegversion_Mac__' in line:
                    lines[i] = f'__ffmpegversion_Mac__ = \'{get_ffmpeg_version()}\'\n'
                if '__gifskiversion_Mac__' in line:
                    lines[i] = f'__gifskiversion_Mac__= \'{get_gifski_version()}\''
                    break
        with open('__version__.py', 'w') as file:
            file.writelines(lines)

    update__version__()
    print('Checking and updating local versions on __version__.py...')

if win:
    icoFolder = os.path.join(base_dir, 'buildandsign', 'ico')
    iconsProdFolder = os.path.join(base_dir, 'icons', 'win')
if mac:
    icoFolder = os.path.join(base_dir, 'buildandsign', 'ico', 'MacOS')
    iconsProdFolder = os.path.join(base_dir, 'icons', 'mac')

def pngtoico(png):
    # Prepare paths
    mainDir = iconsProdFolder
    output_dir = iconsProdFolder
    iconset = f"{os.path.splitext(os.path.split(png)[1])[0]}.iconset"

    # Easter Egg and Dev Icons
    if png == os.path.join(icoFolder, 'ico2.png'):
        output_ico = os.path.join(mainDir, 'Easter', 'ico.ico')
        iconset = os.path.join('Easter', 'ico.iconset')
    elif png == os.path.join(icoFolder, 'icobeta.png'):
        output_ico = os.path.join(mainDir, 'icoDev.ico')
        iconset = os.path.join('Easter', 'icoDev.iconset')
    # Icons Proper
    elif png == os.path.join(icoFolder, 'ico3.png'):
        output_ico = os.path.join(mainDir, 'ico.ico')
        iconset = 'ico.iconset'
    elif png == os.path.join(icoFolder, 'ico3beta.png'):
        output_ico = os.path.join(mainDir, 'icoDev.ico')
        iconset = 'icoDev.iconset'
    elif png == os.path.join(icoFolder, 'ico3Updater.png'):
        output_ico = os.path.join(mainDir, 'icoUpdater.ico')
    # Any Icons
    else:
        output_ico = os.path.join(mainDir, f'{os.path.splitext(os.path.basename(png))[0]}.ico')
    
    if win:
        def resize_image(image_path, output_path, size):
            with Image.open(image_path) as img:
                resized_img = img.resize(size)
                resized_img.save(output_path)      

        image = png
        sizes = [(16, 16), (32, 32), (48, 48), (128, 128), (256, 256)]

        resize_folder = "resize"
        os.makedirs(resize_folder, exist_ok=True)

        for size in sizes:
            output_path = os.path.join(resize_folder, f"resized_{size[0]}x{size[1]}.png")
            resize_image(image, output_path, size)

        resized_images = [os.path.join(resize_folder, f"resized_{size[0]}x{size[1]}.png") for size in sizes]
        print(resized_images)
        
        cmd = ["magick"] + resized_images + ['-type','TrueColorAlpha', output_ico]
        subprocess.run(cmd, check=True)
        shutil.rmtree('resize')

    elif mac:
        iconset_dir = os.path.join(output_dir, iconset)
        sizes = [
        (16, 16), (32, 32), (32, 32), (64, 64), (128, 128),
        (256, 256), (256, 256), (512, 512), (512, 512)
        ]
        output_files = [
        "icon_16x16.png", "icon_16x16@2x.png", "icon_32x32.png", "icon_32x32@2x.png",
        "icon_128x128.png", "icon_128x128@2x.png", "icon_256x256.png", "icon_256x256@2x.png",
        "icon_512x512.png"
        ]
        
        os.makedirs(iconset_dir, exist_ok=True)

        for (width, height), output_file in zip(sizes, output_files):
            command = ['sips', '-z', str(width), str(height), png, '--out', os.path.join(iconset_dir, output_file)]
            subprocess.run(command, check=True)
            
        shutil.copy(png, os.path.join(iconset_dir, "icon_512x512@2x.png"))
        iconutil_command = ['iconutil', '-c', 'icns', iconset_dir]
        subprocess.run(iconutil_command, check=True)

        shutil.rmtree(iconset_dir)

parser.add_argument("-T", "--Test",action='store_true', help = "test modules on Windows. Test Signatures on MacOS")
parser.add_argument("-B", "--build",action='store_true', help = "build the app.")
parser.add_argument("-c", "--console",action='store_true', help = 'Enable console window. (for testing purposes. Please don\'t use the argument for final export.)')
parser.add_argument("-U","--Update", action ='store_true', help ='Checks updates on binaries and will ask you to update.')
parser.add_argument("-i","--icon", action ='store_true', help ='Updates and generates .ico files for the executables.')
parser.add_argument('-v', '--version', action='version', help='Checks all the version the apps',
                    version = textwrap.dedent(f"""\
                    App Proper: {__version__}
                    FFMPEG: {__ffmpegversion__}
                    Gifski: {__gifskiversion__}
                    """))

args = parser.parse_args()

if args.Test:
    if win:
        printColor(Color.CYAN, 'Generating mainVersion.rc...')
        genMainRC()
        printColor(Color.GREEN, 'mainVersion.rc Generated!')
    if mac:
        def sign_and_test(path):
            """
            Test the signing and validity of a .app or .dmg file.
            """
            codesign = 'codesign'
            spctl = 'spctl'

            # Determine if path is .app or .dmg
            is_app = path.endswith('.app')
            is_dmg = path.endswith('.dmg')

            steps = []
            
            steps.append("Verifying with CodeSign (Deep & Strict)")
            steps.append("Displaying CodeSign Info")
            if is_app:
                steps.append("Verifying Executable in .app")
            if is_app:
                steps.append("Checking with Gatekeeper")
            
            try:
                print(f"\n--- Testing Signature for: {path} ---")

                # Loop through each step dynamically
                for i, step in enumerate(steps, start=1):
                    printColor(Color.CYAN, f"\n[{i}/{len(steps)}] {step}...")

                    if step == "Verifying with CodeSign (Deep & Strict)":
                        try:
                            result = subprocess.run([codesign, '--deep', '--strict', path], capture_output=True, text=True, check=True)
                            print(result.stdout)  # Print the successful output, if any
                        except subprocess.CalledProcessError as e:
                            if '':
                                printColor(Color.YELLOW, 'Output is blank. I think we\'re good!')

                    elif step == "Displaying CodeSign Info":
                        subprocess.run([codesign, '--display', '--verbose=4', path], check=True)

                    elif step == "Verifying Executable in .app" and is_app:
                        app_exec_path = os.path.join(path, 'Contents/MacOS/N8\'s Video To Gifski')
                        subprocess.run([codesign, '--verify', '--verbose=4', app_exec_path], check=True)

                    elif step == "Checking with Gatekeeper" and is_app:
                        try:
                            spctl_result = subprocess.run([spctl, '--assess', '--type', 'execute', '--verbose=4', path],  capture_output=True, text=True, check=True)
                            print(spctl_result.stdout)
                        except subprocess.CalledProcessError as e:
                            if re.search(r"rejected", spctl_result.stdout):
                                printColor(Color.YELLOW, f"⚠️ Gatekeeper rejected the app: {path} (but continuing anyway)...")
                            else:
                                print(spctl_result.stdout)

                printColor(Color.GREEN, f"\n✅ All tests passed for: {path}")
            except subprocess.CalledProcessError as e:
                if "rejected":
                    pass
                printColor(Color.RED, f"\n❌ Error while testing {path}:\n{e}")
            except Exception as e:
                printColor(Color.RED, f"\n❌ Unexpected error: {str(e)}")
        
        printColor(Color.CYAN, 'Checking App for Signatures...')
        build_app_path = os.path.abspath(r"./dist/N8's Video To Gifski.app")
        sign_and_test(build_app_path)
        printColor(Color.CYAN, 'App Signature Checked!')

        printColor(Color.CYAN, 'Checking DMG for Signatures...')
        dmg_path = os.path.abspath(r"./N8's Video To Gifski.dmg")
        sign_and_test(dmg_path)
        printColor(Color.CYAN, 'DMG Signature Checked!')

if args.console:
    console = 'True'
    if not args.build:
        printColor(Color.YELLOW, 'You can\'t use this arguement alone. Use it with \'-b\'.(DevTool.py -c -b)')

ffmpegRepo = ffmpeg_GyanDev()
gifskiRepo = get_latest_release_version('ImageOptim', 'gifski')
ffmpeg_dir = '.\\buildandsign\\bin\\full\\'
gifski_dir = f'.\\buildandsign\\bin\\'
MacOS_bin_dir = f'./buildandsign/bin/MacOS/'
    
if args.build:
    print('############ V E R I F Y I N G ############')

    if win:
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

    elif mac:
        if not os.path.exists(f'{MacOS_bin_dir}gifski'):
            latest_file = f'gifski-{gifskiRepo}'
            gifski = 'gifski'
            printColor(Color.RED, 'gifski.exe NOT FOUND!')
            
            print('Exiting Build process.')
            sys.exit()
        else:
            printColor(Color.GREEN, 'gifski.exe Found!')

        required_ffbins = ['ffmpeg', 'ffplay', 'ffprobe']
        if not all(os.path.exists(os.path.join(MacOS_bin_dir, bin)) for bin in required_ffbins):
            printColor(Color.RED,f'{bin} not found!')
            print('Exiting Build process.')
            sys.exit()
        else:
            for bin in required_ffbins:
                printColor(Color.GREEN, f'{bin} Found!')

    printColor(Color.CYAN, 'Updating local versions...')
    check_and_update_local()
    printColor(Color.GREEN, 'Versions up to date!')

    printColor(Color.CYAN, 'Checking icons and files...')

    icon_file = 'ico.ico'
    if mac:
        icon_file = 'ico.icns'
    
    if not os.path.exists(f'{iconsProdFolder}/{icon_file}'):
        printColor(Color.YELLOW, f'{icon_file} NOT FOUND!')
        printColor(Color.CYAN, f'building {icon_file}...')
        pngtoico(f'{icoFolder}/ico3.png')
        printColor(Color.GREEN, f'{icon_file} Ready!')
    else:
        printColor(Color.GREEN, f'{icon_file} Found!')
    
    if mac:
        if not os.path.exists(f'{iconsProdFolder}/icoDMG.icns'):
            printColor(Color.YELLOW, f'icoDMG.icns NOT FOUND!')
            printColor(Color.CYAN, f'building icoDMG.icns...')
            pngtoico(os.path.abspath('./buildandsign/dmg/icoDMG.png'))
            printColor(Color.GREEN, f'icoDMG.icns Ready!')
        else:
            printColor(Color.GREEN, f'icoDMG.icns Found!')

    if win:
        print('############ S P E C  F I L E S ############')
        printColor(Color.CYAN, 'Generating main.spec...')
        genMainSpec(ff, console)
        printColor(Color.GREEN, 'main.spec generated!')

        print('############ V E R S I O N  R C  F I L E S ############')
        printColor(Color.CYAN, 'Generating mainVersion.rc...')
        genMainRC()
        printColor(Color.GREEN, 'mainVersion.rc Generated!')

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
        pngtoico(f'{icoFolder}/ico3Updater.png')
        pngtoico(f'{icoFolder}/ico3.png')
        pngtoico(f'{icoFolder}/ico3beta.png')

