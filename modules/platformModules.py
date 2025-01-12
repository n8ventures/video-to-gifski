import os
import sys
import platform
import subprocess
from tkinter import PhotoImage
import tkinter as tk

# Check the platform
current_platform = platform.system()

win = current_platform == "Windows"
mac = current_platform == "Darwin"

def is_running_from_bundle():
    # Check if the application is running from a bundled executable
    if getattr(sys, 'frozen', False):
        if win:
            if hasattr(sys, '_MEIPASS'):
                return sys._MEIPASS
        if mac:
            current_dir = os.path.dirname(sys.executable)
            parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
            return os.path.join(parent_dir, "Resources")

    return False

if win:
    from __version__ import __version__
elif mac:
    from __version__ import __versionMac__ as __version__

if is_running_from_bundle():
    print("Running from a bundled application (.app/.exe)")
else:
    print("Running from source (.py)")

print("Current app version:", __version__)

print("Current working directory:", os.getcwd())
print("Executable path:", sys.executable)
print('TclVersion: ', tk.TclVersion)
print('TkVersion: ', tk.TkVersion)

# Binary file names for each platform
platform_binaries = {
    "Windows": {
        "ffprobe": "ffprobe.exe",
        "ffplay": "ffplay.exe",
        "gifski": "gifski.exe",
        "ffmpeg": "ffmpeg.exe"
    },
    "Darwin": {
        "ffprobe": "ffprobe",
        "ffplay": "ffplay",
        "gifski": "gifski",
        "ffmpeg": "ffmpeg"
    }
}

# Default binaries based on the platform
binaries = platform_binaries.get(current_platform, {})

# Handle bundle paths for binaries and icon
bundle_path = is_running_from_bundle()

icon = None
iconUpdater = None

if any(char.isalpha() for char in __version__):
    if win:
        icon = os.path.join(bundle_path or '', 'icoDev.ico') if bundle_path else './icons/win/icoDev.ico'
    elif mac:
        icon = PhotoImage(file=os.path.join(bundle_path or '', 'ico3beta.png') if bundle_path else './buildandsign/ico/ico3beta.png')
else:
    if win:
        icon = os.path.join(bundle_path or '', 'ico.ico') if bundle_path else 'ico.ico'
    elif mac:
        icon = PhotoImage(file=os.path.join(bundle_path or '', 'ico3.png') if bundle_path else './buildandsign/ico/ico3.png')

if bundle_path:
    binaries = {
        key: os.path.join(bundle_path, value)
        for key, value in binaries.items()
    }
    if win:
        iconUpdater = os.path.join(bundle_path, 'icoUpdater.ico')
        icon = os.path.join(bundle_path, icon)
else:
    if win:
        icon_path = './icons/win/'
        iconUpdater = os.path.join(icon_path, 'icoUpdater.ico')
        icon = os.path.join(icon_path, icon)
    elif mac:
        MacOSbin = './buildandsign/bin/macOS'
        binaries = {
    key: os.path.join(MacOSbin, value)
    for key, value in binaries.items()
}

ffprobe = binaries.get("ffprobe")
ffplay = binaries.get("ffplay")
gifski = binaries.get("gifski")
ffmpeg = binaries.get("ffmpeg")

# opening windows
def is_folder_open(path):
    if win:
        open_folders = subprocess.check_output('tasklist /v /fi "imagename eq explorer.exe"', shell=True).decode('utf-8')
        folder_name = os.path.basename(path)

        return folder_name in open_folders
    elif mac:
        folder_name = os.path.basename(path)
        # AppleScript to check Finder windows
        script = '''
            tell application "System Events"
                set openWindows to name of every window of application process "Finder"
            end tell
            return openWindows
        '''

        try:
            open_windows = subprocess.check_output(['osascript', '-e', script]).decode('utf-8').strip().split(", ")
            # Check if folder name is in the list of open windows
            return folder_name in open_windows
        except subprocess.CalledProcessError as e:
            print(f"Error checking Finder windows: {e}")
            return False

def openOutputFolder(path, path2):
    global win, mac
    if win:
        import pywinctl as pwc

        print('checking if window is open...')
        if not is_folder_open(path):
            print('window not found, opening window.')
            subprocess.run(fr'explorer /select,"{path2}"')
        else:
            print('window found!')
            print('Window path: ',path)

            windows = pwc.getWindowsWithTitle(os.path.basename(path))
            if windows:
                win = windows[0]
                if win.minimize():
                    win.restore(True)
                win.activate(True)

            else:
                print('Window not found with specified title.')
                print('Opening window: ', path2)
                subprocess.run(fr'explorer /select,"{path2}"')
    elif mac:
        print('Checking if folder is open...')
        if not is_folder_open(path):
            print('Folder not found in Finder. Opening folder...')
        else:
            print('Folder is already open in Finder.')

        # Reveal the file or folder in Finder
        try:
            subprocess.run(['open', '-R', path2], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error opening folder in Finder: {e}")