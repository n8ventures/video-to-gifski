from __version__ import __versionMac__ as __version__, __appname__, __ffmpegversion_Mac__ as __ffmpegversion__, __gifskiversion__, __author__
import tkinter as tk
from tkinter import filedialog, ttk, PhotoImage, colorchooser
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageTk, ImageSequence
import subprocess
import os
import json
import shutil
import sys
import atexit
from idlelib.tooltip import Hovertip
import requests
import threading
import pywinctl as pwc
import time
import math
from tkmacosx import Button
import glob
import platform
import re


def is_running_from_bundle():
    # Check if the application is running from a bundled executable
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            return sys._MEIPASS
        current_dir = os.path.dirname(sys.executable)
        parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
        return os.path.join(parent_dir, "Resources")

    return False

# Example usage:
if is_running_from_bundle():
    print("Running from a bundled application (.app)")
else:
    print("Running from source (.py)")

print("Current app version:", __version__)

print("Current working directory:", os.getcwd())
print("Executable path:", sys.executable)
print('TclVersion: ', tk.TclVersion)
print('TkVersion: ', tk.TkVersion)


video_data = None
global mode

# for windows executables, basically makes this readable inside an exe    
ffprobe = 'ffprobe'
ffplay = 'ffplay'
gifski = 'gifski'
ffmpeg = 'ffmpeg'
if bundle_path := is_running_from_bundle():
    ffprobe = os.path.join(bundle_path, ffprobe)
    ffplay = os.path.join(bundle_path, ffplay)
    gifski = os.path.join(bundle_path, gifski)
    ffmpeg = os.path.join(bundle_path, ffmpeg)
else:
    MacOSbin = './buildandsign/bin/macOS'
    ffprobe = os.path.join(MacOSbin, ffprobe)
    ffplay = os.path.join(MacOSbin, ffplay)
    gifski = os.path.join(MacOSbin, gifski)
    ffmpeg = os.path.join(MacOSbin, ffmpeg)

def create_popup(root, title, width, height, switch, lift = 0):
    popup = tk.Toplevel(root)
    popup.title(title)
    popup.geometry(f"{width}x{height}")
    popup.iconphoto(True, icon)
    # popup.overrideredirect(True)
    popup.attributes('-type', 'utility')
    center_window(popup, width, height)
    
    if switch == 1:
        popup.bind("<FocusOut>", lambda e: popup.destroy())
    if lift == 1:
        popup.lift()

    popup.grab_set()
    
    return popup

loading_screen = None

def loading(texthere='', filenum=0, filestotal=0):
    global loading_screen, load_text_label

    if loading_event.is_set():
        if not loading_screen: 
            loading_screen = create_popup(root, "Converting...", 380, 150, 0)
            make_non_resizable(loading_screen)
            
            load_text_label = tk.Label(loading_screen, text='Converting...\nPlease wait.')
            load_text_label.pack(pady=20)

            update_loading(texthere, filenum, filestotal)

            progress_bar = ttk.Progressbar(loading_screen, mode='indeterminate')
            progress_bar.pack(fill=tk.X, padx=10, pady=0)
            progress_bar.start()
            loading_screen.update_idletasks()
            print('starting loading popup')
    else:
        if loading_screen:  
            loading_screen.destroy()
            loading_screen = None 
            print('loading popup dead')

def update_loading(texthere='', filenum=0, filestotal=0):
    if filenum == 0 and filestotal == 0 or filestotal == 1:
        load_text_label.config(text=f'{texthere}\n\nConverting...\nPlease wait.')
    else:
        load_text_label.config(text=f'({filenum}/{filestotal} Files)\n{texthere}\n\nConverting...\nPlease wait.')
    
    loading_screen.update_idletasks()

loading_event = threading.Event()

def loading_thread(texthere='', filenum=0, filestotal=0):
    loading_event.set()
    print('starting thread')
    loading(texthere, filenum, filestotal)

def loading_thread_switch(switch, texthere='', filenum=0, filestotal=0):
    if switch:
        threading.Thread(target=loading_thread, args=(texthere, filenum, filestotal), daemon=True).start()
        print('Thread Initialized.')
    else:
        print('killing loading popup')
        loading_event.clear()
        root.after(0, loading)

# check updates

def get_latest_release_version(pr=False, filter_keywords=None, require_dmg=False):
    n8_gif_repo = "https://api.github.com/repos/n8ventures/video-to-gifski/releases"
    try:
        response = requests.get(n8_gif_repo)
        response.raise_for_status()  
    except:
        return {
            'tag_name': '0.0.0',
            'has_dmg': False,
            'has_exe': False,
            'html_url': ''
        }
    
    releases = json.loads(response.text)
    
    if not releases:
        return {
            'tag_name': '0.0.0',
            'has_dmg': False,
            'has_exe': False,
            'html_url': ''
        }
    
    for release in releases:
        if pr or not release.get('prerelease', False):
            tag_name = release.get('tag_name', '0.0.0')
            assets = release.get('assets', [])
            has_dmg = any(asset['name'].endswith('.dmg') for asset in assets)
            has_exe = any(asset['name'].endswith('.exe') for asset in assets)
            html_url = release.get('html_url', '')

            if (filter_keywords is None or all(keyword.lower() in tag_name.lower() for keyword in filter_keywords)) and (not require_dmg or has_dmg):
                return {
                    'tag_name': tag_name,
                    'has_dmg': has_dmg,
                    'has_exe': has_exe,
                    'html_url': html_url
                }
    
    return {
        'tag_name': '0.0.0',
        'has_dmg': False,
        'has_exe': False,
        'html_url': ''
    }


has_beta = 'beta' in __version__.lower()
print(f'Has Beta? {has_beta}')

global release, prerelease
try:
    release = get_latest_release_version(pr=False)
    prerelease = get_latest_release_version(pr=True, filter_keywords=['osx', 'beta'])
except:
    release = {
        'tag_name': '0.0.0',
        'has_dmg': False,
        'has_exe': False,
        'html_url': ''
    }
    prerelease = {
        'tag_name': '0.0.0',
        'has_dmg': False,
        'has_exe': False,
        'html_url': ''
    }

print('\n-- DEBUG DATA --\n')
print('RELEASE: ', release)
print('PRE-RELEASE: ', prerelease)
print('\n')

def CheckUpdates():
    global release, prerelease
    if release['tag_name'] == '0.0.0' or prerelease['tag_name'] == '0.0.0':
        try:
            release = get_latest_release_version(pr=False)
            prerelease = get_latest_release_version(pr=True, filter_keywords=['osx', 'beta'])
        except:
            release = {
                'tag_name': '0.0.0',
                'has_dmg': False,
                'has_exe': False,
                'html_url': ''
            }
            prerelease = {
                'tag_name': '0.0.0',
                'has_dmg': False,
                'has_exe': False,
                'html_url': ''
            }
    has_prerelease_latest = 'beta' in prerelease['tag_name'].lower() and prerelease['has_dmg']
    has_release_latest = release['has_dmg']
    print(f'Pre-release: {has_prerelease_latest}\nRelease: {has_release_latest}')
    print(f'compare: {__version__ in prerelease['tag_name']}')
    print('\n-- DEBUG DATA --\n\n')
    print('RELEASE: ', release)
    print('\n\n')
    print('PRE-RELEASE: ', prerelease)
    print('\n\n')
    

    geo_width = 300
    geo_len = 180
    updatemenu = create_popup(root, "Checking for Updates...", geo_width, geo_len, 0)
    make_non_resizable(updatemenu)

    msglabel = tk.Label(updatemenu, text='')
    msglabel.pack(pady=10)

    version_display = tk.Label(updatemenu, text=f'(Current Version: {__version__})', font=('Helvetica', 14, 'italic'))
    version_display.pack(pady=2)
    latest_version_display = tk.Label(updatemenu, text ='Checking for updates...')
    latest_version_display.pack()
    ask_label = tk.Label(updatemenu, text='Would you like to update?\n')
    
    buttonsFrame = tk.Frame(updatemenu)
    buttonsFrame.pack(side=tk.BOTTOM, pady=10)
    
    update_button = Button(buttonsFrame, text='Yes')
    close_button = Button(buttonsFrame, text="Close", command=updatemenu.destroy)
    close_button.pack(side=tk.RIGHT, padx=5)
    
    def update_btn_cmd(callback):
        updatemenu.destroy()
        callback()
    
    if has_beta:
        print('PASS -1A: HAS BETA')
        if has_prerelease_latest:
            print('PASS 0-A: HAS PRE RELEASE')
            update_button.config(command=lambda: update_btn_cmd(lambda: open_link(prerelease['html_url'])))
            
            current_version_parts = __version__.split('-')
            current_version = current_version_parts[0]
            current_tag = current_version_parts[1] if len(current_version_parts) > 1 else ''

            prerelease_parts = prerelease['tag_name'].split('-')
            prerelease_version = prerelease_parts[0]
            prerelease_tag = prerelease_parts[2] if len(prerelease_parts) > 2 else ''

            if current_version >= prerelease_version:
                print('PASS 1-A: CURRENT IS HIGHER OR EQUAL VS ONLINE')
                if current_tag.lower() >= prerelease_tag.lower() and current_version >= prerelease_version:
                    print('PASS 1-2-A: BETA IS HIGHER OR EQUAL VS ONLINE')
                    latest_version_display.config(text="You're up to date!")
                elif current_tag.lower() < prerelease_tag.lower() and current_version <= prerelease_version:
                    print('PASS 1-2-B: BETA IS OUTDATED VS ONLINE')
                    msglabel.config(text='A new beta patch is available!')
                    latest_version_display.config(text=f'Latest Version: {prerelease["tag_name"]}', font=('Helvetica', 14, 'bold'))
                    ask_label.pack(pady=10)
                    update_button.pack(side=tk.LEFT)
                    close_button.config(text='Cancel')
            elif current_version < prerelease_version:
                print('PASS 1-B: CURRENT IS LESS THAN ONLINE')
                msglabel.config(text='A new update is available!')
                latest_version_display.config(text=f'Latest Version: {prerelease["tag_name"]}', font=('Helvetica', 14, 'bold'))
                ask_label.pack(pady=10)
                update_button.pack(side=tk.LEFT)
                close_button.config(text='Cancel')
            else:
                print('PASS 1-C: NO NEW UPDATE')
                msglabel.config(text="No new pre-release available.")
                latest_version_display.config(text="You're up to date!")
                close_button.config(text='Close')
        elif release['tag_name'] == '0.0.0' or prerelease['tag_name'] == '0.0.0':
            print('PASS 0-B: INTERNET ERROR BETA')
            latest_version_display.config(text='Connection error, Please try again later.')

    elif has_release_latest:
        print('PASS -1B: HAS RELEASE')
        update_button.config(command=lambda: update_btn_cmd(lambda: open_link(release['html_url'])))
        current_version_parts = __version__.split('-')
        current_version = current_version_parts[0]
        release_version = release['tag_name']

        if current_version >= release_version:
            print('PASS 0-A: STABLE IS HIGHER OR EQUAL VS ONLINE')
            latest_version_display.config(text="You're up to date!")
        elif current_version < release_version:
            print('PASS 0-B: STABLE IS OUTDATED VS ONLINE')
            msglabel.config(text='A new update is available!')
            latest_version_display.config(text=f'Latest Version: {release["tag_name"]}', font=('Helvetica', 14, 'bold'))
            ask_label.pack(pady=10)
            update_button.pack(side=tk.LEFT)
            close_button.config(text='Cancel')
        else:
            print('PASS 0-C: NO NEW UPDATE')
            msglabel.config(text="No new update available.")
            latest_version_display.config(text="You're up to date!")
            close_button.config(text='Close')

    elif release['tag_name'] == '0.0.0' or prerelease['tag_name'] == '0.0.0':
        print('PASS -1C: INTERNET ERROR')
        latest_version_display.config(text='Connection error, Please try again later.', font=('Helvetica', 14, 'bold'))
    else:
        msglabel.config(text="No new release available.")
        latest_version_display.config(text="You're up to date!")

def autoChecker():
    has_prerelease_latest = 'beta' in prerelease['tag_name'].lower() and prerelease['has_dmg']
    has_release_latest = release['has_dmg']

    if has_beta:
        print('PASS -1A: HAS BETA')
        if has_prerelease_latest:
            print('PASS 0-A: HAS PRE RELEASE')
            current_version_parts = __version__.split('-')
            current_version = current_version_parts[0]
            current_tag = current_version_parts[1] if len(current_version_parts) > 1 else ''

            prerelease_parts = prerelease['tag_name'].split('-')
            prerelease_version = prerelease_parts[0]
            prerelease_tag = prerelease_parts[2] if len(prerelease_parts) > 2 else ''

            if current_version >= prerelease_version:
                print('AC - PASS 1-A: CURRENT IS HIGHER OR EQUAL VS ONLINE')
                if current_tag.lower() >= prerelease_tag.lower() and current_version >= prerelease_version:
                    print('AC - PASS 1-2-A: BETA IS HIGHER OR EQUAL VS ONLINE')
                elif current_tag.lower() < prerelease_tag.lower() and current_version <= prerelease_version:
                    print('AC - PASS 1-2-B: BETA IS OUTDATED VS ONLINE')
                    return CheckUpdates()
            else:
                print('AC - PASS 1-B: CURRENT IS LESS THAN ONLINE')
                return CheckUpdates()
        elif release['tag_name'] == '0.0.0' or prerelease['tag_name'] == '0.0.0':
            print('AC - PASS 0-B: INTERNET ERROR BETA')

    elif has_release_latest:
        print('AC - PASS -1B: HAS RELEASE')
        current_version_parts = __version__.split('-')
        current_version = current_version_parts[0]
        release_version = release['tag_name']
        
        

        if current_version >= release_version:
            print('AC - PASS 0-A: STABLE IS HIGHER OR EQUAL VS ONLINE')
        else:
            print('AC - PASS 0-B: STABLE IS OUTDATED VS ONLINE')
            return CheckUpdates()
    elif release['tag_name'] == '0.0.0' or prerelease['tag_name'] == '0.0.0':
        print('AC - PASS -1C: INTERNET ERROR')

def about():
    geo_width = 370
    geo_len = 300

    aboutmenu = create_popup(root, "About Us!", geo_width, geo_len, 1)
    make_non_resizable(aboutmenu)

    gifski_text = f"- Gifski (https://gif.ski/)\nVersion: {__gifskiversion__}"
    ffmpeg_text = f"- FFmpeg (https://ffmpeg.org/)\nVersion: {__ffmpegversion__}"
    copyright_text = (
    "This program is distributed under the MIT License.\n"
    "Copyright (c) 2024 John Nathaniel Calvara"
    )
    credits_text = (
        "\nCredits:\n"
        f"{gifski_text}\n\n"
        f"{ffmpeg_text}"
    )

    credits_label = tk.Label(aboutmenu, text=credits_text, justify=tk.LEFT)
    credits_label.pack(pady=10)

    copyright_label = tk.Label(aboutmenu, text=copyright_text, justify=tk.CENTER)
    copyright_label.pack(pady=5)

    clickable_link_labels(
        aboutmenu, "nate@n8ventures.dev", "mailto:nate@n8ventures.dev"
    )
    clickable_link_labels(
        aboutmenu,
        "https://github.com/n8ventures",
        "https://github.com/n8ventures",
    )

    close_button = Button(aboutmenu, text="Close", command=aboutmenu.destroy)
    close_button.pack(pady=10)


def clickable_link_labels(aboutmenu, text, link):
    mailto_label = tk.Label(aboutmenu, text=text, fg="blue", cursor="hand2")
    mailto_label.pack()
    mailto_label.bind("<Button-1>", lambda e: open_link(link))

def open_link(url):
    import webbrowser
    webbrowser.open(url)

def watermark_label(parent_window):
    
    menu_bar = tk.Menu(root)
    
    about_menu = tk.Menu (menu_bar, tearoff=0)
    about_menu.add_command(label="About Us", command=about)
    about_menu.add_command(label="Check for Updates", command=CheckUpdates)
    menu_bar.add_cascade(label="Help", menu=about_menu)
    
    parent_window.config(menu=menu_bar)
    
    frame = tk.Frame(parent_window)
    frame.pack(side=tk.BOTTOM, fill=tk.X)

    separator_wm = ttk.Separator(frame, orient="horizontal")
    separator_wm.pack(side=tk.TOP, fill=tk.X)
    
    watermark_label = tk.Label(frame, text=f"by {__author__}", fg="gray")
    watermark_label.pack(side=tk.LEFT, anchor=tk.SW)
    
    version_label = tk.Label(frame, text=f"version: {__version__}", fg="gray")
    version_label.pack(side=tk.RIGHT, anchor=tk.SE)
    
    root.config(menu=menu_bar)

def make_non_resizable(window):
    window.resizable(False, False)

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = width  
    window_height = height
    window.update_idletasks()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2  
    window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position-35}")

def get_filesize(file_path):
    size_bytes = os.path.getsize(file_path)
    size_mb = round(size_bytes / (1024 * 1024), 2)
    size_kb = round(size_bytes / 1024, 2)
    return f'{size_mb} MB ({size_kb} KB)'

def get_video_data(input_file):
    cmd = [ffprobe,
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,duration,pix_fmt",
        "-of", "json",
        input_file
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        # Parse the JSON output
        video_info = json.loads(result.stdout)
        return video_info['streams'][0]  # Assuming there is only one video stream
    else:
        # Handle error
        print(f"Error: {result.stderr}")
        return None

alpha_formats = [
    # RGB with alpha
    'rgba', 'abgr', 'argb', 'bgra', 
    
    # 64-bit RGB with alpha
    'rgba64be', 'rgba64le', 'bgra64be', 'bgra64le',
    
    # 32-bit RGBA
    'rgba32be', 'rgba32le',
    
    # YUV with alpha
    'yuva420p', 'yuva422p', 'yuva444p',
    
    # YUV with alpha at various bit depths
    'yuva420p9be', 'yuva420p9le',
    'yuva422p9be', 'yuva422p9le',
    'yuva444p9be', 'yuva444p9le',
    
    'yuva420p10be', 'yuva420p10le',
    'yuva422p10be', 'yuva422p10le',
    'yuva444p10be', 'yuva444p10le',
    
    'yuva420p12be', 'yuva420p12le',
    'yuva444p12le',
    
    'yuva420p16be', 'yuva420p16le',
    'yuva422p16be', 'yuva422p16le',
    'yuva444p16be', 'yuva444p16le',

    
    # Other formats
    'ya8',  # 8-bit grayscale with alpha
    'ya16be', 'ya16le',  # 16-bit grayscale with alpha
    
    # 64-bit YUV with alpha
    'ayuv64le', 'ayuv64be',
    
    # 32-bit float RGBA
    'rgbaf32be', 'rgbaf32le'
]

running = False
after_id = None

def stop_gif_animation(widget):
    global running, after_id
    running = False
    if after_id:
        widget.after_cancel(after_id)
        after_id = None

def video_to_frames_seq(input_file, framerate, preview = False):
    global preview_height, preview_weight
    
    temp_folder = 'temp'
    preview_folder = 'temp/preview'

    if preview == False:
        stop_gif_animation(preview_label)
        if os.path.exists(temp_folder) and os.listdir(temp_folder):
            shutil.rmtree(temp_folder)
    else:
            os.makedirs(preview_folder, exist_ok=True)

    os.makedirs(temp_folder, exist_ok=True)


    cmd = [
        ffmpeg,
        "-loglevel", "-8",
        '-i', input_file,
        "-vf",
    ]

    filtergraph = [f'fps={str(framerate)}']

    if preview == False:
        if len(valid_files) == 1 and scale_widget.get() != 100:
            filtergraph.append(f'scale={scaled_width}:{scaled_height},setsar=1')
    else:
        aspect_ratio = scaled_width / scaled_height

        if scaled_width > scaled_height:  # Landscape
            max_width= 350
            target_width = min(scaled_width , max_width)
            target_height = int(target_width / aspect_ratio)
        else:  # Portrait or square
            max_height=300
            target_height = min(scaled_height, max_height)
            target_width = int(target_height * aspect_ratio)
        
        preview_height = target_height
        preview_weight = target_width

        filtergraph.append(f'scale={target_width}:{target_height},setsar=1')
        print('0000000000---- H:', target_height, 'x W:',target_width)
    if safeAlpha.get():
        filtergraph.append('unpremultiply=inplace=1')

    cmd.append(','.join(filtergraph))

    if preview == False:
        cmd.append(os.path.join(temp_folder, 'frames%04d.png'))
    else:
        cmd.append(os.path.join(preview_folder, 'preview%04d.png'))
    subprocess.run(cmd)

def load_gifpreview_frames():
    folder = 'temp/preview'
    frame_files = sorted([os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.png')])
    return [Image.open(frame_file) for frame_file in frame_files]

def vid_to_gif(fps, gifQuality, motionQuality, lossyQuality, output):
    global matte_var  

    if hasattr(output, 'name'):
        output_file = output.name
    elif isinstance(output, str):
        output_file = output

    if len(valid_files) == 1:
        cmd = [
            gifski,
            "-q",
            "-r", str(int(fps)),
            "-Q", str(gifQuality),
            "-W", str(scaled_width),
            "-H", str(scaled_height),
            "--repeat", "0",
            ]
    else:
        cmd = [
            gifski,
            "-q",
            "-r", str(int(fps)),
            "-Q", str(gifQuality),
            "--repeat", "0",
            ]

    if extra_var.get():
        cmd.append("--extra")
    if fast_var.get():
        cmd.append("--fast")
    if motion_var.get():
        cmd.extend(["--motion-quality", str(motionQuality)])
    if lossy_var.get():
        cmd.extend(["--lossy-quality", str(lossyQuality)])
    if enableMatte.get():
        if matte_var is None:
            matte_var = '#FFFFFF'
            print('matte is not set. using default hex value #FFFFFF or white')
        
        cmd.extend(["--matte", matte_var])

    if input_files := glob.glob("temp/frames*.png"):
        # Extend the command with the found file paths
        cmd.extend(["-o", output_file])
        cmd.extend(input_files)
        # Execute the command
        subprocess.run(cmd)
    else:
        print("No input files found.")


def get_and_print_video_data(file_path):
    global video_data, valid_files
    invalid_files = []
    valid_files = []

    if file_path == '':
        print('No video File dropped.')
        return

    print(f"Files: {file_path}")
    
    for file in file_path:
        if not is_video_file(file):
            print(f'File "{file}" is not a supported video file.')
            invalid_files.append(os.path.basename(file))
            continue

        valid_files.append((os.path.basename(file), file))

    if valid_files and not settings_window_open:
        if len(valid_files) == 1:
            if video_data := get_video_data(valid_files[0][1]):
                parse_video_data(video_data)
        else:
            open_settings_window()
    
    if invalid_files:
        notavideo(invalid_files,[f[0] for f in valid_files])

def notavideo(invalid_file, valid_file):
    longest_invalid_length = max((len(file) for file in invalid_file if len(file) > 50), default=0)
    longest_valid_length = max((len(file) for file in valid_file if len(file) > 50), default=0)
    largest_length = max(longest_invalid_length, longest_valid_length)

    weight = (largest_length * 3) + 400
    height = (((len(invalid_file)+len(valid_file))*16)+150)
    
    if len(valid_file) != 0:
        height = height + 25
        
    print(f'{weight} x {height}')
    notavideo = create_popup(root, "Not A Video!", weight, height, 1, 1)
    make_non_resizable(notavideo)

    invalid_files_list = "❌ " + "\n❌ ".join(invalid_file)
    button_text = 'Close'
    
    if len(valid_file) != 0:
        valid_files_list = "✅ " + "\n✅ ".join(valid_file)
        valid_text = f"The following files will be processed:\n\n{valid_files_list}"
        button_text = 'Continue'
    else:
        valid_text = 'Please select valid video files!'

    errortext = (
        "The following files are not video files:\n\n"
        f"{invalid_files_list}\n\n"
        f"{valid_text}"
    )

    about_label = tk.Label(notavideo, text=errortext, justify=tk.LEFT)
    about_label.pack(pady=10)

    close_button = Button(notavideo, text=button_text, command=notavideo.destroy)
    close_button.pack(pady=10) 

def parse_temp_data(temp_data):
    width_value = temp_data['width']
    height_value = temp_data['height']
    fps_value = round(eval(temp_data['r_frame_rate']), 3)
    duration_value = temp_data['duration']
    pix_fmt = temp_data['pix_fmt']

    fps_int = round(fps_value)
    total_frames = int(float(duration_value) *fps_int)
    hours = total_frames // (3600 * fps_int)
    remaining_frames = total_frames % (3600 * fps_int)
    minutes = remaining_frames // (60 * fps_int)
    remaining_frames %= (60 * fps_int)
    seconds = remaining_frames // fps_int
    frames = remaining_frames % fps_int
    timecode = f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}"

    debug_gif_window = create_popup(root, 'Debugging GIF', 200, 200, 1)
    make_non_resizable(debug_gif_window)

    debug_gif_text= f'''
        Video width: {width_value}
        Video height: {height_value}
        Framerate: {fps_value}
        Duration: {duration_value}
        Frames: {total_frames}
        Timecode: {timecode}
        pixel format: {pix_fmt}'''

    debug_gif_label = tk.Label(debug_gif_window, text=debug_gif_text, justify=tk.LEFT)
    debug_gif_label.pack()

    close_button = Button(debug_gif_window, text="Close", command=debug_gif_window.destroy)
    close_button.pack(pady=10)

    if not settings_window_open:
        open_settings_window()


def parse_video_data(video_data):
    global parsed_framerate
    
    width_value = video_data['width']
    height_value = video_data['height']
    fps_value = round(eval(video_data['r_frame_rate']), 3)
    duration_value = video_data['duration']
    pix_fmt = video_data['pix_fmt']

    fps_int = round(fps_value)
    total_frames = int(float(duration_value) *fps_int)
    hours = total_frames // (3600 * fps_int)
    remaining_frames = total_frames % (3600 * fps_int)
    minutes = remaining_frames // (60 * fps_int)
    remaining_frames %= (60 * fps_int)
    seconds = remaining_frames // fps_int
    frames = remaining_frames % fps_int
    timecode = f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}"
    
    parsed_framerate = int(round(fps_value))

    print("Video width:", width_value)
    print("Video height:", height_value)
    print("Frame rate:", fps_value)
    print("Duration:", duration_value)
    print("Frames:", total_frames)
    print(f"Timecode: {timecode}")
    print("pixel format:", pix_fmt)

    if not settings_window_open:
        open_settings_window()
        
video_extensions = [
'.3g2', '.3gp', '.amv', '.asf', '.avi', '.drc', '.f4v', '.flv', '.gif', '.gifv', '.m2ts', 
'.m2v', '.m4p', '.m4v', '.mkv', '.mng', '.mov', '.mp2', '.mp4', '.mpe', '.mpeg', '.mpg', 
'.mpv', '.mts', '.mxf', '.nsv', '.ogg', '.ogv', '.qt', '.rm', '.rmvb', '.roq', '.svi', 
'.ts', '.vob', '.webm', '.wmv', '.yuv'
]

def is_video_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    return file_extension.lower() in video_extensions


def is_folder_open(path):
    """
    Checks if the folder is currently open in Finder (macOS only).
    """
    if platform.system() != 'Darwin':  # Ensure this only runs on macOS
        raise OSError("is_folder_open is only supported on macOS.")

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

def convert_and_save(fps, gif_quality, motion_quality, lossy_quality, input_file, mode):
    global output_file
    framerate = fps.get()
    gifQ = gif_quality.get()
    motionQ= motion_quality.get()
    lossyQ = lossy_quality.get()

    def openOutputFolder(path, path2):
        """
        Opens the specified folder or reveals a file in Finder (macOS only).
        """
        if platform.system() != 'Darwin':  # Ensure this only runs on macOS
            raise OSError("open_output_folder is only supported on macOS.")

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

    file = input_file[0][1]

    if mode == 'final':
        output_file = None
        output_directory = None
        
        if len(input_file) == 1:
            output_file = filedialog.asksaveasfile(
                defaultextension=".gif",
                initialdir=f"{os.path.dirname(file)}",
                initialfile=f"{os.path.splitext(os.path.basename(file))[0]}.gif",
                filetypes=[("GIF files", "*.gif")],
            )
        else:
            output_directory = filedialog.askdirectory(
                title="Select your Directory to Save GIF Files",
                initialdir=f"{os.path.dirname(input_file[0][1])}"
                )

        if output_file:
            output_file.close()
            output_full_path = os.path.abspath(output_file.name)
            output_dir = os.path.dirname(output_file.name)

            loading_thread_switch(True, os.path.basename(file))

            video_to_frames_seq(file, framerate)
            vid_to_gif(framerate, gifQ, motionQ, lossyQ, output_file)
            loading_thread_switch(False)

            print("Conversion complete!")
            shutil.rmtree('temp')
            on_settings_window_close()
            try:
                openOutputFolder(output_dir, output_full_path)
            except OSError as e:
                print(f"Error: {e}")

        elif output_directory:
            loading_thread_switch(True, input_file[0][0], 1, len(input_file))

            for filenum, (file_name, full_path) in enumerate(input_file, start=1):
                output = os.path.join(output_directory, f"{os.path.splitext(file_name)[0]}.gif")
                
                if loading_screen:
                    update_loading(file_name, filenum, len(input_file))
                
                video_to_frames_seq(full_path, framerate)
                vid_to_gif(framerate, gifQ, motionQ, lossyQ, output)
                shutil.rmtree('temp')
            
            loading_thread_switch(False)
            print("Conversions complete!")
            on_settings_window_close()
            
            try:
                openOutputFolder(output_directory, output)
            except OSError as e:
                print(f"Error: {e}")

    elif mode == 'temp':
            output_file = 'temp/temp.gif'
            print(output_file)

            loading_thread_switch(True, os.path.basename(file))
            vid_to_gif(framerate, gifQ, motionQ, lossyQ, output_file)
            video_to_frames_seq(output_file, fps.get(), preview=True)
            loading_thread_switch(False)

            print("Conversion complete!")


    elif mode == 'temp-final':
        output_file = filedialog.asksaveasfile(
            defaultextension=".gif",
            initialdir=f"{os.path.dirname(file)}",
            initialfile=f"{os.path.splitext(os.path.basename(file))[0]}.gif",
            filetypes=[("GIF files", "*.gif")],
        )

        if output_file:
            output_file.close()
            output_full_path = os.path.abspath(output_file.name)
            output_dir = os.path.dirname(output_file.name)

            shutil.copy2('temp/temp.gif', output_file.name)
            print("Conversion complete!")
            stop_gif_animation(preview_label)
            shutil.rmtree('temp')
            on_settings_window_close()
            try:
                openOutputFolder(output_dir, output_full_path)
            except OSError as e:
                print(f"Error: {e}")


def apply_settings(mode):
    global fps, gif_quality_scale, scale_widget, extra_var, fast_var, motion_quality_scale, lossy_quality_scale, motion_var, lossy_var, scaled_width, scaled_height, safeAlpha

    fps_value = fps.get()
    extra_value = extra_var.get()
    fast_value = fast_var.get()
    motion_value = motion_var.get()
    lossy_value = lossy_var.get()
    gif_quality_value = gif_quality_scale.get()
    motion_quality= motion_quality_scale.get()
    lossy_quality =lossy_quality_scale.get()
    unpremultiply_value = safeAlpha.get()
    
    if len(valid_files) == 1:
        scale_value = scale_widget.get()
        width_value = video_data['width']
        height_value = video_data['height']
        
        if width_value and height_value:
            # Calculate the scaled width based on the slider value
            scaled_width = int(width_value * scale_value / 100)

            # Maintain the aspect ratio
            scaled_height = int((scaled_width / width_value) * height_value)
        
        print(f"-- SETTINGS APPLIED --\nFPS: {fps_value} - Scale: {scaled_width} x {scaled_height}")
        print("GIF Quality:", gif_quality_value)
        
        print("Motion Quality", motion_value)
        if motion_value:
            print("Motion Quality Value:", motion_quality)
        
        print("Lossy Quality", lossy_value)
        if lossy_value:
            print("Lossy Quality Value:", lossy_quality)
        
        print("Extra:", extra_value)
        print("Fast:", fast_value)
        print('unpremultiply:', unpremultiply_value)

    file = valid_files
    convert_and_save(fps, gif_quality_scale, motion_quality_scale, lossy_quality_scale, file, mode)

def choose_file():
    global file_path
    file_path = filedialog.askopenfilenames(
        title="Select Video File",
        filetypes=(("Video files", "*" + " *".join(video_extensions)), ("All files", "*.*"))
    )
    get_and_print_video_data(file_path)

settings_window_open = False

def on_settings_window_close():
    global settings_window_open
    settings_window_open = False
    settings_window.destroy()
    print('Settings Window is open?', settings_window_open)
    root.deiconify()
    

def open_settings_window(): 
    global settings_window_open, fps, scale_widget, extra_var, fast_var, settings_window, motion_var, lossy_var, safeAlpha, preview_label
    global gif_quality_scale, motion_quality_scale, lossy_quality_scale
    global enableMatte, matte_var
    
    if not settings_window_open:
        settings_window_open = True
        print('Settings Window is open?', settings_window_open)

    win_height = 650
    if len(valid_files) == 1:
        window_title = 'User Settings'
        preview_label_text = 'Click the Apply & Preview button to load a GIF Preview.'
        export_label = 'Quick Export'
        preview_label_pady = 5
        if video_data['pix_fmt'] in alpha_formats:
            win_height += 100
    else:
        window_title = 'User Settings: Batch Mode'
        preview_label_text = 'Multiple videos detected!\nAdjust the settings to apply\nthe same configuration to all GIFs converted!'
        export_label = 'Export'
        preview_label_pady = 20
        win_height -= 25
    
    settings_window = tk.Toplevel(root)
    settings_window.title(window_title)
    center_window(settings_window, 350, win_height)
    settings_window.iconphoto(True, icon)
    watermark_label(settings_window)
    make_non_resizable(settings_window)

    preview_label = tk.Label(settings_window, text = preview_label_text)
    preview_label.pack(pady=preview_label_pady)
    
    fileSize_label =tk.Label(settings_window, text = '')
    fileDimension_label = tk.Label(settings_window, text='')
    fileSize_label.pack()
    fileDimension_label.pack(pady=5)
    
    playframe = tk.Frame(settings_window)
    playframe.pack()
    play_gif_button = Button(playframe, text='No GIF loaded', command=lambda: play_gif('temp/temp.gif'))
    play_gif_button.pack(pady=10)
    play_gif_button.config(state="disabled")
    
    separator1 = ttk.Separator(settings_window, orient="horizontal")
    separator1.pack(fill="x", padx=20, pady=4)
    
    gif_quality_scale = tk.Scale(settings_window, from_=1, to=100, orient=tk.HORIZONTAL, resolution=1, length=300)
    gif_quality_scale.set(90)
    gif_quality_scale.pack()
    gif_quality_label = tk.Label(settings_window, text="GIF Quality")
    gif_quality_label.pack()
    Hovertip(gif_quality_label, "Overall GIF Quality", hover_delay=500)
    Hovertip(gif_quality_scale, "Overall GIF Quality", hover_delay=500)
    
    def update_checkbox_state(var, widget, other_var=None, other_widget=None, cmode=None):
        if cmode == 'encode':
            if var.get() == 1:
                other_var.set(0)
                other_widget['state'] = 'disabled'
            else:
                other_widget['state'] = 'normal'
        
        elif cmode == 'quality':
            if var.get() == 1:
                widget['state'] = 'normal'
                widget['takefocus'] = True
                widget['sliderrelief'] = 'raised'
            else:
                widget['state'] = 'disabled'
                widget['takefocus'] = False
                widget['sliderrelief'] = 'flat'

        elif cmode == 'basic':
            if var.get() == 1:
                widget['state'] = 'normal'
            else:
                widget['state'] = 'disabled'

    if len(valid_files) != 1:
        fps_limit = 30
    else:
        fps_limit = min(parsed_framerate, 30)
    
    fps = tk.Scale(settings_window, from_=1, to=fps_limit, orient=tk.HORIZONTAL, resolution=1, length=300, fg="#7d7dff", troughcolor="#7d7dff")
    fps.set(fps_limit)
    fps.pack()
    fps_label = tk.Label(settings_window, text="Frames Per Second", fg="#7d7dff")
    fps_label.pack()

    # separator5 = ttk.Separator(settings_window, orient="horizontal")
    # separator5.pack(fill="x", padx=20, pady=4)

    if len(valid_files) == 1:
        scale_widget = tk.Scale(settings_window, from_=1, to=100, orient=tk.HORIZONTAL, resolution=0.5, length=300)
        scale_widget.set(100)
        scale_widget.pack()    
        scale_label_var = tk.StringVar()
        scale_widget.config(command=lambda value: update_scale_label(value))
        scale_label_var.set(f"{video_data['width']}x{video_data['height']} - Scale: {scale_widget.get()}%")
        scale_label = tk.Label(settings_window, textvariable=scale_label_var)
        scale_label.pack()
        
        def update_scale_label(value):
            global scaled_width, scaled_height
            
            width_value = video_data['width']
            height_value = video_data['height']

            if width_value and height_value:
                # Calculate the scaled width based on the slider value
                scaled_width = int(width_value * float(value) / 100)

                # Maintain the aspect ratio
                scaled_height = int((scaled_width / width_value) * height_value)

                # Update the label text with the current size and percentage
                scale_label_var.set(f"{scaled_width}x{scaled_height} - Scale: {value}%")

        scale_widget.bind("<B1-Motion>", lambda event: update_scale_label(scale_widget.get()))
        root.update_idletasks()
    
    separator3 = ttk.Separator(settings_window, orient="horizontal")
    separator3.pack(fill="x", padx=20, pady=2)
    
    optionalFrame = tk.Frame(settings_window)
    optionalFrame.pack()
    optionalLabel = tk.Label(optionalFrame, text="Optional Settings:")
    optionalLabel.pack()
    
    motion_var = tk.IntVar()
    motion_quality_scale = tk.Scale(optionalFrame, from_=1, to=100,orient=tk.HORIZONTAL, resolution=1, length=300, sliderrelief='flat', fg="#7d7dff", troughcolor="#7d7dff")
    motion_quality_scale.set(100)
    motion_quality_scale.pack()
    motion_quality_scale['state'] = 'disabled'
    motion_quality_checkbutton = tk.Checkbutton(optionalFrame, text="Motion Quality", variable=motion_var, command=lambda: update_checkbox_state(motion_var, motion_quality_scale, cmode = 'quality'))
    motion_quality_checkbutton.pack()
    Hovertip(motion_quality_checkbutton, "Turn this on to fine-tune the Motion Quality (affects overall Quality.)", hover_delay=500)
    Hovertip(motion_quality_scale, "Lower values reduce motion.", hover_delay=500)

    lossy_var = tk.IntVar()
    lossy_quality_scale = tk.Scale(optionalFrame, from_=1, to=100, orient=tk.HORIZONTAL, resolution=1, length=300, sliderrelief='flat')
    lossy_quality_scale.set(100)
    lossy_quality_scale.pack()
    lossy_quality_scale['state'] = 'disabled'
    lossy_quality_checkbutton = tk.Checkbutton(optionalFrame, text="Lossy Quality", variable=lossy_var, command=lambda: update_checkbox_state(lossy_var, lossy_quality_scale, cmode = 'quality'))
    lossy_quality_checkbutton.pack()
    Hovertip(lossy_quality_scale, "Turn this on to fine-tune the Lossy Quality (affects overall Quality.)", hover_delay=500)
    Hovertip(lossy_quality_checkbutton, "Lower values introduce noise and streaks.", hover_delay=500)
    # separator4 = ttk.Separator(settings_window, orient="horizontal")
    # separator4.pack(fill="x", padx=20, pady=2)
    
    separator6 = ttk.Separator(settings_window, orient="horizontal")
    separator6.pack(fill="x", padx=20, pady=2)
    
    spacer = tk.Label(settings_window, text="Encode Quality:")
    spacer.pack()
    
    checkboxFrame = tk.Frame(settings_window)
    checkboxFrame.pack(pady=5)
    
    extra_var = tk.IntVar()
    extra_checkbox = tk.Checkbutton(checkboxFrame, variable=extra_var, text="Extra Quality", command=lambda: update_checkbox_state(extra_var, extra_checkbox, fast_var, fast_checkbox,  cmode = 'encode'))
    extra_checkbox.pack(side=tk.LEFT)
    Hovertip(extra_checkbox, "Slower encoding, but 1% better quality.", hover_delay=500)
    
    fast_var = tk.IntVar()
    fast_checkbox = tk.Checkbutton(checkboxFrame, variable=fast_var, text="Fast Quality", command=lambda: update_checkbox_state(fast_var, fast_checkbox, extra_var, extra_checkbox,  cmode = 'encode'))
    fast_checkbox.pack(side=tk.RIGHT)
    Hovertip(fast_checkbox, "Faster encoding, but 10% worse quality & larger file size.", hover_delay=500)
    
    # insert unpremultiply option here
    
    alphaFrame = tk.Frame(settings_window)
    separator2 = ttk.Separator(settings_window, orient="horizontal")
    alphaLabel = tk.Label(alphaFrame, text='Alpha Options:')
    matteFrame = tk.Frame(settings_window)
    separator3 = ttk.Separator(settings_window, orient="horizontal")
    
    safeAlpha = tk.IntVar()
    unprenmult_checkbox = tk.Checkbutton(alphaFrame, variable=safeAlpha, text="Unpremultiply")
    
    matte_var = None
    def pick_color():
        global matte_var
        color = colorchooser.askcolor()[1]  # Ask the user to choose a color and get the hex code
        print(color)
        if color:
            matte_var = color
            matte_box_preview.config(bg=color)
            Hovertip(matte_box_preview, color, hover_delay=500)
    
    enableMatte = tk.IntVar()
    matte_checkbox = tk.Checkbutton(matteFrame, variable=enableMatte, command=lambda: update_checkbox_state(enableMatte, matte_button, cmode = 'basic'))
    matte_button = tk.Button(matteFrame, text="Choose Matte", command=pick_color)
    matte_box_preview = tk.Label(matteFrame, width=2, height=1, bg="white", relief="solid")
    
    if len(valid_files) != 1 or video_data['pix_fmt'] in alpha_formats:
        separator2.pack(fill="x", padx=20, pady=2)
        
        alphaFrame.pack()
        alphaLabel.pack()
        unprenmult_checkbox.pack(pady=5)
        matteFrame.pack()
        separator3.pack(fill="x", padx=20, pady=2)
        matte_checkbox.pack(pady=5, side=tk.LEFT)
        matte_box_preview.pack(pady=5,side=tk.LEFT)
        matte_button.pack(pady=5, side=tk.RIGHT)
        matte_button['state'] = 'disabled'
        
        Hovertip(unprenmult_checkbox, "It\'s like unmult but more precise.\nEnable this if your GIF has outlines.", hover_delay=500)
        Hovertip(matte_button, "Click here to color-pick your desired matte.", hover_delay=500)
        Hovertip(matte_checkbox, "Enable this if you have semitransparent pixels.", hover_delay=500)
        Hovertip(matte_box_preview, '#FFFFFF', hover_delay=500)
        root.update_idletasks()
    
    buttonsFrame = tk.Frame(settings_window)
    buttonsFrame.pack(side=tk.BOTTOM, pady=20)
    
    apply_button = Button(buttonsFrame, text=export_label, command=lambda: threading.Thread(target=apply_settings, args=('final', ), daemon=True).start())
    apply_button.pack(side=tk.LEFT, padx=5)
    
    test_button = Button(buttonsFrame, text="Apply & Preview", command=lambda: threading.Thread(target=preview_gif_window, daemon=True).start())
    test_button.pack(side=tk.RIGHT, padx=5)
    
    if len(valid_files) != 1:
        separator1.pack_forget()
        # preview_label.pack_forget()
        fileSize_label.pack_forget()
        fileDimension_label.pack_forget()
        playframe.pack_forget()
        play_gif_button.pack_forget()
        test_button.pack_forget()
        apply_button.pack_forget()
        apply_button.pack(side=tk.TOP)
        
        root.update_idletasks()
    
    def preview_gif_window():
        loading_thread_switch(True)
        video_to_frames_seq(file_path[0], fps.get())
        loading_thread_switch(False)
        
        apply_settings('temp')
        
        play_gif_button.config(state="normal", text='Play GIF on Full Size')
        
        img = Image.open(output_file)
        imgW, imgH = img.size
        gcd = math.gcd(imgW, imgH)
        aspect_ratio_simplified = f'{imgW // gcd}:{imgH // gcd}'
        height =  650
        height += preview_height
        
        if video_data['pix_fmt'] in alpha_formats:
            height += 100
        
        center_window(settings_window, 380, height)

        preview_label.config(text="")
        
        # Animate GIF preview Window
        def animate_gif_preview(frames, widget, frame_num, loop, frame_duration):
            frame = frames[frame_num]
            global running, after_id
            if not running:
                return
            photo = ImageTk.PhotoImage(frame)
            widget.config(image=photo)
            widget.image = photo
            
            frame_num = (frame_num + 1) % len(frames)
            if loop or frame_num != 0:
                after_id = widget.after(frame_duration, animate_gif_preview, frames, widget, frame_num, loop, frame_duration)
                
        def start_gif_animation(widget, loop=True, fps=30):
            global running
            running = True
            
            frames = load_gifpreview_frames()
            frame_duration = 1000 // fps  # Duration per frame in milliseconds
            animate_gif_preview(frames, widget, 0, loop, frame_duration)
            
        start_gif_animation(preview_label, loop=True, fps=fps.get())
        
        apply_button.config(text='Save As...', command=lambda: apply_settings('temp-final'))
        
        filesize = get_filesize('temp/temp.gif')
        fileSize_label.config(text=f'GIF Size: {filesize}')
        fileDimension_label.config(text=f'Dimensions: {imgW}x{imgH} ({aspect_ratio_simplified})')
        settings_window.update_idletasks()
        
    settings_window.protocol("WM_DELETE_WINDOW", lambda: on_settings_window_close())
    
        
    def play_gif(file_path):
        cmd = [
        ffplay,
        "-window_title", "Playing GIF Preview",
        "-loglevel", "-8",
        "-loop", "0",
        file_path
    ]

        subprocess.run(cmd)

    def on_settings_close():
        if os.path.exists('temp'):
            shutil.rmtree('temp') 
            print("temp removed successfully.")
        else:
            print("temp does not exist.")
        settings_window.destroy()
        on_settings_window_close()

    root.withdraw()
    settings_window.grab_set()
    settings_window.wait_visibility()
    settings_window.protocol("WM_DELETE_WINDOW", on_settings_close) 


# Create the main window
root = TkinterDnD.Tk()
print('TCL Library:', root.tk.exprstring('$tcl_library'))
print('Tk Library:',root.tk.exprstring('$tk_library'))

if any(char.isalpha() for char in __version__):
    icon = (
        PhotoImage(file=os.path.join(bundle_path, 'ico3beta.png'))
        if bundle_path
        else PhotoImage(file='./buildandsign/ico/ico3beta.png')
    )
elif bundle_path:
    icon =  PhotoImage(file=os.path.join(bundle_path, 'ico3.png'))
else:
    icon = PhotoImage(file='./buildandsign/ico/ico3.png')
root.withdraw()

splash_screen = tk.Toplevel(root)
splash_screen.overrideredirect(1)
splash_screen.attributes('-topmost', True)  # Keep the window on top
splash_screen.attributes("-transparent", "true")
splash_geo_x = 350
splash_geo_y = 550
center_window(splash_screen, splash_geo_x, splash_geo_y)




gif_path = 'splash.gif'
if bundle_path:
    gif_path = os.path.join(bundle_path, gif_path)
else:
    gif_path = './/splash//splash.gif'


gif_img = Image.open(gif_path)
gif_frames_rgba = [frame.convert("RGBA") for frame in ImageSequence.Iterator(gif_img)]

splash_label = tk.Label(splash_screen, bg='white')
splash_label.pack()

# Function to animate GIF frames
def animate(frame_num, loop):
    frame = gif_frames_rgba[frame_num]
    photo = ImageTk.PhotoImage(frame)
    splash_label.config(image=photo, bg='white')
    splash_label.image = photo
    
    if loop:
        frame_num = (frame_num + 1) % len(gif_frames_rgba)
        splash_screen.after(25, animate, frame_num, True)
    elif frame_num < len(gif_frames_rgba) - 1:
        frame_num += 1
        splash_screen.after(25, animate, frame_num, False)


animate(0, False)

def show_main():    
    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def on_drop(event):
        global file_path
        print(f'File Path PASS I: {event.data}')
        file_path = re.findall(r'\{.*?\}|\S+', event.data)
        print(f'File Path PASS II: {file_path}')
        file_path = [re.sub(r'[{}]', '', file) for file in file_path]
        print(f'File Path PASS III: {file_path}')

        get_and_print_video_data(file_path)

    if any(char.isalpha() for char in __version__):
        root.title("N8's Video to Gifski (Beta)")

    else:
        root.title("N8's Video to Gifski")

    geo_width= 425
    center_window(root, geo_width, 450)
    root.iconphoto(True, icon)
    make_non_resizable(root)
    watermark_label(root)

    spacer = tk.Label(root, text="")
    spacer.pack(pady=10)

    # Create a button to choose a file
    choose_button = Button(root, text="Choose Video File", command=choose_file)
    choose_button.pack(pady=20)

    or_label = tk.Label(root, text="Or")
    or_label.pack(pady=20)

    # Create a Canvas
    canvas = tk.Canvas(root, relief="ridge")
    canvas.pack(expand=True, fill="both")

    # Create a Label for the drop area
    drop_label = tk.Label(canvas, text="Drag and Drop Video Files Here")
    drop_label.pack(pady = 60)

    # Bind the drop event to the on_drop function
    def reg_dnd(widget):
        widget.drop_target_register(DND_FILES)
        widget.dnd_bind('<<Drop>>', on_drop)

    reg_dnd(drop_label)
    reg_dnd(canvas)
    reg_dnd(or_label)
    reg_dnd(root)

    # logo on drop event area
    DnDLogo = 'ico3.png'
    if bundle_path:
        DnDLogo = os.path.join(bundle_path, DnDLogo)
    else:
        DnDLogo = './buildandsign/ico/ico3.png'
    imgYPos = 225

    image = tk.PhotoImage(file=DnDLogo)
    resized_image = image.subsample(2)
    label = tk.Label(canvas, image=resized_image, bd=0)
    label.image = resized_image
    label.place(x=geo_width / 2, y=imgYPos, anchor=tk.CENTER)

    splash_screen.destroy()
    root.deiconify()
    threading.Thread(target=autoChecker(), daemon=True).start()    

def on_closing():
    if os.path.exists('temp'):
        shutil.rmtree('temp')
        print("temp removed successfully.")
    else:
        print("temp does not exist.")
        
    print("Closing the application.")
    
    atexit.unregister(on_closing)  # Unregister the atexit callback
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
atexit.register(on_closing)

# threading.Thread(target=show_main).start()
splash_screen.after(3500, show_main)

root.mainloop()