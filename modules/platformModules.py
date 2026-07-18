import os
import sys
import platform
import subprocess
import tkinter as tk
import tempfile

# Check the platform
current_platform = platform.system()

win = current_platform == "Windows"
mac = current_platform == "Darwin"

from __version__ import __appname__, __internal_app_name__


def is_running_from_bundle():
    # Check if the application is running from a bundled executable
    if getattr(sys, "frozen", False):
        if win:
            if hasattr(sys, "_MEIPASS"):
                return sys._MEIPASS
        if mac:
            current_dir = os.path.dirname(sys.executable)
            parent_dir = os.path.abspath(
                os.path.join(
                    current_dir,
                    os.pardir,
                )
            )
            return os.path.join(parent_dir, "Resources")

    return False


if win:
    from __version__ import __version__
elif mac:
    from __version__ import __versionMac__ as __version__

# cache this once — is_running_from_bundle() was being called twice before
bundle_path = is_running_from_bundle()

if bundle_path:
    print("Running from a bundled application (.app/.exe)")
else:
    print("Running from source (.py)")

print("Current app version:", __version__)

print("Current working directory:", os.getcwd())
print("Executable path:", sys.executable)
print("TclVersion: ", tk.TclVersion)
print("TkVersion: ", tk.TkVersion)

# Binary file names for each platform
platform_binaries = {
    "Windows": {
        "ffprobe": "ffprobe.exe",
        "ffplay": "ffplay.exe",
        "gifski": "gifski.exe",
        "ffmpeg": "ffmpeg.exe",
    },
    "Darwin": {
        "ffprobe": "ffprobe",
        "ffplay": "ffplay",
        "gifski": "gifski",
        "ffmpeg": "ffmpeg",
    },
}

# Default binaries based on the platform
binaries = platform_binaries.get(current_platform, {})

icon = None
iconUpdater = None

platform_folder = "MacOS" if mac else "Windows"

is_dev_build = any(char.isalpha() for char in __version__)

if is_dev_build:
    if win:
        icon = (
            os.path.join(
                bundle_path or "",
                "assets",
                "icons",
                "icoDev.ico",
            )
            if bundle_path
            else "./buildandsign/icons/Windows/icoDev.ico"
        )
    elif mac:
        icon = (
            os.path.join(
                bundle_path or "",
                "icon-dev.png",
            )
            if bundle_path
            else "./buildandsign/icons/MacOS/icon-dev.png"
        )
else:
    if win:
        icon = (
            os.path.join(
                bundle_path or "",
                "assets",
                "icons",
                platform_folder,
                "ico.ico",
            )
            if bundle_path
            else "ico.ico"
        )
    elif mac:
        icon = (
            os.path.join(
                bundle_path or "",
                "assets",
                "icons",
                platform_folder,
                "icon.png",
            )
            if bundle_path
            else "./buildandsign/icons/MacOS/icon.png"
        )


if bundle_path:
    log_dir = os.path.expanduser(f"~/Library/Application Support/{__appname__}/Logs")
    temp_dir = os.path.join(tempfile.gettempdir(), __appname__)
    binaries = {
        key: os.path.join(
            bundle_path,
            "bin",
            platform_folder,
            value,
        )
        for key, value in binaries.items()
    }
else:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    temp_dir = os.path.join(base_dir, "temp")
    log_dir = os.path.join(base_dir, "logs")

    if win:
        icon = os.path.join("./buildandsign/icons/Windows/", os.path.basename(icon))
    elif mac:
        MacOSbin = "./buildandsign/bin/macOS"
        binaries = {
            key: os.path.join(
                MacOSbin,
                value,
            )
            for key, value in binaries.items()
        }

os.makedirs(temp_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)

ffprobe = binaries.get("ffprobe")
ffplay = binaries.get("ffplay")
gifski = binaries.get("gifski")
ffmpeg = binaries.get("ffmpeg")


# opening windows
def is_folder_open(path):
    if win:
        open_folders = subprocess.check_output(
            'tasklist /v /fi "imagename eq explorer.exe"',
            shell=True,
        ).decode("utf-8")
        folder_name = os.path.basename(path)

        return folder_name in open_folders
    elif mac:
        folder_name = os.path.basename(path)
        # AppleScript to check Finder windows
        script = """
            tell application "System Events"
                set openWindows to name of every window of application process "Finder"
            end tell
            return openWindows
        """

        try:
            open_windows = (
                subprocess.check_output(
                    [
                        "osascript",
                        "-e",
                        script,
                    ]
                )
                .decode("utf-8")
                .strip()
                .split(", ")
            )
            # Check if folder name is in the list of open windows
            return folder_name in open_windows
        except subprocess.CalledProcessError as e:
            print(f"Error checking Finder windows: {e}")
            return False


def openOutputFolder(path, path2):
    # NOTE: no longer does `global win` + reassigns win to a Window object.
    # `win` is your Windows/macOS platform flag used everywhere else in the
    # app — overwriting it here corrupted every later `if win:` check for
    # the rest of the process's life once a matching window was found.
    if win:
        import pywinctl as pwc  # type: ignore

        print("checking if window is open...")
        if not is_folder_open(path):
            print("window not found, opening window.")
            subprocess.run(rf'explorer /select,"{path2}"')
        else:
            print("window found!")
            print("Window path: ", path)

            windows = pwc.getWindowsWithTitle(os.path.basename(path))
            if windows:
                matched_window = windows[0]
                if matched_window.minimize():
                    matched_window.restore(True)
                matched_window.activate(True)
            else:
                print("Window not found with specified title.")
                print("Opening window: ", path2)
                subprocess.run(rf'explorer /select,"{path2}"')
    elif mac:
        print("Checking if folder is open...")
        if not is_folder_open(path):
            print("Folder not found in Finder. Opening folder...")
        else:
            print("Folder is already open in Finder.")

        # Reveal the file or folder in Finder
        try:
            subprocess.run(["open", "-R", path2], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error opening folder in Finder: {e}")
