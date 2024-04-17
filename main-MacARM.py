from __version__ import __versionMac__ as __version__, __appname__, __ffmpegversion_Mac__ as __ffmpegversion__, __gifskiversion__
import tkinter as tk
from tkinter import filedialog, ttk, PhotoImage
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


def is_running_from_bundle():
    # Check if the application is running from a bundled executable
    if getattr(sys, 'frozen', False):
        # For py2app bundles, use sys.executable to get the bundle path
        if hasattr(sys, '_MEIPASS'):
            return sys._MEIPASS
        else:
            current_dir = os.path.dirname(sys.executable)
            parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
            return os.path.join(parent_dir, "Resources")

    return False

# Example usage:
if is_running_from_bundle():
    print("Running from a bundled application")
else:
    print("Running from source")

import argparse
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-E", "--Egg",action='store_true', help = "Egg, mi amor")
parser.add_argument('-v', '--version', action='version', version = __version__)
parser.add_argument('-D', '--debug', action='store_true', help=f'Debug mode. use cmd \' {__appname__}.exe | MORE\'. But, you already knew that, don\'t cha?')
parser.add_argument('-ct', '--checkthreads', action='store_true', help='Checks threads. (Will not work without [-D])')
args = parser.parse_args()

debug = ''

if args.debug:
    debug = '(Debug Mode)'
    if args.checkthreads:
        def list_current_threads():
            while True:
                print("-" * 20)
                print("Current threads:")
                for thread in threading.enumerate():
                    print(thread.name)
                print("-" * 20)
                time.sleep(3)

        threading.Thread(name='thread checker', target=list_current_threads, daemon=True).start()
if args.Egg:
    debug = '(Egg me up)'
print("Current version:", __version__)



video_data = None
global mode

# for windows executables, basically makes this readable inside an exe    
ffprobe = 'ffprobe'
ffplay = 'ffplay'
gifski = 'gifski'
ffmpeg = 'ffmpeg'
bundle_path = is_running_from_bundle()
if bundle_path:
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

def create_popup(root, title, width, height, switch):
    popup = tk.Toplevel(root)
    popup.title(title)
    popup.geometry(f"{width}x{height}")
    popup.iconphoto(True, icon)
    # popup.overrideredirect(True)
    popup.attributes('-type', 'utility')
    center_window(popup, width, height)
    
    if switch == 1:
        popup.bind("<FocusOut>", lambda e: popup.destroy())

    popup.grab_set()
    
    return popup

def loading():
    if loading_event.is_set():
        global loading_screen
        loading_screen = create_popup(root, "Converting...", 350, 120, 0)
        make_non_resizable(loading_screen)
        
        load_text_label = tk.Label(loading_screen, text='Converting...\nPlease wait.')
        load_text_label.pack(pady=20)

        progress_bar = ttk.Progressbar(loading_screen, mode='indeterminate')
        progress_bar.pack(fill=tk.X, padx=10, pady=0)
        progress_bar.start()
        root.update_idletasks()
        print('starting loading popup')
    else:
        loading_screen.destroy()
        print('loading popup dead')
        
loading_event = threading.Event()

def loading_thread():
    loading_event.set()
    print('starting thread')
    loading()

def loading_thread_switch(switch):
    if switch == True:
        threading.Thread(target=loading_thread, daemon=True).start()
    if switch == False:
        print('killing loading popup')
        loading_event.clear()
        loading()

# if Updater not found, download on github.
def get_latest_release_version():
    global n8_gif_repo

    n8_gif_repo = "https://api.github.com/repos/n8ventures/v2g-con-personal/releases/latest"
    response = requests.get(n8_gif_repo)
    if response.status_code != 200:
        return '0.0.0'
    release_info = json.loads(response.text)
    return release_info.get('tag_name', '0.0.0')

# def downloadUpdater():
#     global latest_release_version

#     response = requests.get(n8_gif_repo)
#     if response.status_code == 200:
#         return downloadUpdaterUpdate(response)
#     print("Failed to retrieve updater information. Please check your internet connection.")
#     return 'ERR_NO_CONNECTION'



# def downloadUpdaterUpdate(response):
#     release_data = response.json()
#     latest_release_version = get_latest_release_version()
#     if latest_release_version == '0.0.0':
#         return 'ERR_NO_CONNECTION'
#     latest_file = f'{__updatername__}.exe'

#     for asset in release_data['assets']:
#         if asset['name'] == latest_file:
#             download_url = asset['browser_download_url']
#             updaterURL = requests.get(download_url)

#             with open(latest_file, 'wb') as file:
#                 file.write(updaterURL.content)
#                 return 'UPDR_DONE'
#     print('File not found!')
#     return 'ERR_NOT_FOUND'

# def UPDATER_POPUP(title, msg):
#     win_height = 250 if os.path.exists(f"{__updatername__}.exe") else 140
#     updaterMenu = create_popup(root, title, 400, win_height, 1)
#     make_non_resizable(updaterMenu)

#     txt_msg = msg

#     if os.path.exists(f"{__updatername__}.exe"):
#         NR_label1= tk.Label(updaterMenu, text='New release detected!', font=('Helvetica', 10, 'bold'))
#         NR_label2= tk.Label(updaterMenu, text=f'Updating {__updatername__}.exe...', font=('Helvetica', 10, 'italic'))
#         NR_label1.pack(pady=10)
#         NR_label2.pack(pady=10)

#     txt_label = tk.Label(updaterMenu, text=txt_msg)
#     txt_label.pack(pady=10)

#     close_button = ttk.Button(updaterMenu, text="Close", command=updaterMenu.destroy)

#     close_button.pack(pady=10)

#     root.update_idletasks()

#     if downloadUpdater() == 'UPDR_DONE':
#         updaterMenu.destroy()

# def execute_download_updater():
#     UPDATER_POPUP('Downloading updater...', '\nDownloading the uploader!\nYou may still use the program freely!\nWe\'ll run the updater once the download has been finished!')
#     update_result = downloadUpdater()
#     if update_result == 'ERR_NO_CONNECTION':
#         UPDATER_POPUP('Updater Download Failed!', '\nERROR: Download Failed!\nPlease check your internet connection and try again later!')
#     elif update_result == 'ERR_NOT_FOUND':
#         UPDATER_POPUP('Updater Download Failed!', '\nERROR: Download Failed!\nFile not found!')
#     elif update_result == 'UPDR_DONE':
#         time.sleep(3)
#         subprocess.Popen(f'{__updatername__}.exe')

def CheckUpdates():
    print('Disabled. lol')
    # get_latest_release_version()
    
    # if not os.path.exists(f"{__updatername__}.exe"):
    #     print('updater not found')
    #     execute_download_updater()
    # else:
    #     print('Updater exists!')
    #     if __version__ < get_latest_release_version():
    #         print('New release! Downloading updated updater. (yeah I know...)')
    #         execute_download_updater()
    #     else:
    #         print('opening updater')
    #         subprocess.Popen(f'{__updatername__}.exe')

def about():
    geo_width = 370
    geo_len = 300

    if args.Egg:
        geo_width = 370
        geo_len= 410

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
    if args.Egg:
        egg_about(aboutmenu, geo_width, geo_len)

    close_button = ttk.Button(aboutmenu, text="Close", command=aboutmenu.destroy)
    close_button.pack(pady=10)


def egg_about(aboutmenu, geo_width, geo_len):
    mograph = 'motionteamph.png'
    mograph = (
        os.path.join(bundle_path, mograph)
        if bundle_path
        else './buildandsign/ico/motionteamph.png'
    )
    image = tk.PhotoImage(file=mograph)
    label = tk.Label(aboutmenu, image=image, bd=0)
    label.image = image
    label.place(x=geo_width / 2, y=geo_len - 60, anchor=tk.CENTER)
    Hovertip(label, "BetMGM Manila Motions Team 2024")


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
    # about_menu.add_command(label="Check for Updates", command=CheckUpdates)
    menu_bar.add_cascade(label="Help", menu=about_menu)
    
    parent_window.config(menu=menu_bar)
    
    frame = tk.Frame(parent_window)
    frame.pack(side=tk.BOTTOM, fill=tk.X)

    separator_wm = ttk.Separator(frame, orient="horizontal")
    separator_wm.pack(side=tk.TOP, fill=tk.X)
    
    watermark_label = tk.Label(frame, text="by N8VENTURES", fg="gray")
    watermark_label.pack(side=tk.LEFT, anchor=tk.SW)
    
    version_label = tk.Label(frame, text=f"version: {__version__} {debug}", fg="gray")
    version_label.pack(side=tk.RIGHT, anchor=tk.SE)
    
    root.config(menu=menu_bar)

def make_non_resizable(window):
    window.resizable(False, False)

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = width  
    window_height = height
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
    'rgba', 'abgr', 'argb', 'bgra', 'yuva420p', 'yuva422p', 'yuva444p',
    'rgba64be', 'rgba64le', 'bgra64be', 'bgra64le',
    'yuva422p9be', 'yuva422p9le', 'yuva444p9be', 'yuva444p9le',
    'yuva420p10be', 'yuva420p10le', 'yuva422p10be', 'yuva422p10le',
    'yuva444p10be', 'yuva444p10le', 'yuva420p16be', 'yuva420p16le',
    'yuva422p16be', 'yuva422p16le', 'yuva444p16be', 'yuva444p16le'
]

def video_to_frames_seq(input_file, framerate):
    temp_folder = 'temp'

    if os.path.exists(temp_folder) and os.listdir(temp_folder):
        shutil.rmtree(temp_folder)

    os.makedirs(temp_folder, exist_ok=True)

    cmd = [
        ffmpeg,
        "-loglevel", "-8",
        '-i', input_file,
        "-vf",
    ]

    filtergraph = [f'fps={str(framerate)}']

    if scale_widget.get() != 100:
        filtergraph.append(f'scale={scaled_width}:{scaled_height},setsar=1')

    if safeAlpha.get():
        filtergraph.append('unpremultiply=inplace=1')

    cmd.append(','.join(filtergraph))
    cmd.append(os.path.join(temp_folder, 'frames%04d.png'))
    # subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(cmd)
    if args.debug:
        print(cmd)
    
def vid_to_gif(fps, gifQuality, motionQuality, lossyQuality, output):

    if hasattr(output, 'name'):
        output_file = output.name
    elif isinstance(output, str):
        output_file = output

    cmd = [
        gifski,
        "-q",
        "-r", str(int(fps)),
        "-Q", str(gifQuality),
        "-W", str(scaled_width),
        "-H", str(scaled_height),
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
        
    # Find all matching files in the temp directory
    input_files = glob.glob("temp/frames*.png")

    # Check if any files are found
    if input_files:
        # Extend the command with the found file paths
        cmd.extend(["-o", output_file])
        cmd.extend(input_files)

        # Execute the command
        subprocess.run(cmd)
    else:
        print("No input files found.")
    if args.debug:
        print(cmd)


def get_and_print_video_data(file_path):
    global video_data
    if file_path != 'temp/temp.gif':
        print(f"File: {file_path}")

    if file_path and is_video_file(file_path) and file_path != 'temp/temp.gif':
        if video_data := get_video_data(file_path):
            parse_video_data(video_data)
    elif file_path and is_video_file(file_path) and file_path == 'temp/temp.gif':
        if temp_data := get_video_data(file_path):
            parse_temp_data(temp_data)
    elif file_path == '':
        print('No video File dropped.')

    else:
        notavideo()

def notavideo():
    notavideo = create_popup(root, "Not a video!", 400, 100, 1)
    make_non_resizable(notavideo)

    errortext = (
        "Not a video! Please select a video file!"
    )

    about_label = tk.Label(notavideo, text=errortext, justify=tk.LEFT)
    about_label.pack(pady=10)

    close_button = ttk.Button(notavideo, text="Close", command=notavideo.destroy)
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

    close_button = ttk.Button(debug_gif_window, text="Close", command=debug_gif_window.destroy)
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
    folder_name = os.path.basename(path)
    if platform.system() == 'Windows':
        open_folders = subprocess.check_output('tasklist /v /fi "imagename eq explorer.exe"', shell=True).decode('utf-8')
        return folder_name in open_folders
    elif platform.system() == 'Darwin':  # macOS
        # Use AppleScript to check if Finder window is open with the specified folder
        script = f'''
            tell application "System Events"
                set openWindows to name of every window of application process "Finder"
            end tell
            if "{folder_name}" is in openWindows then
                return true
            else
                return false
            end if
        '''
        open_windows = subprocess.check_output(['osascript', '-e', script]).decode('utf-8').strip()
        return open_windows == 'true'
    else:
        raise OSError("Unsupported operating system")

def convert_and_save(fps, gif_quality, motion_quality, lossy_quality, input_file, mode):
    global output_file
    framerate = fps.get()
    gifQ = gif_quality.get()
    motionQ= motion_quality.get()
    lossyQ = lossy_quality.get()

    def openOutputFolder(path, path2):
        print('checking if window is open...')
        if not is_folder_open(path):
            print('window not found, opening window.')
            if platform.system() == 'Windows':
                subprocess.run(fr'explorer /select,"{path2}"')
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', '-R', path2])
        else:
            print('window found!')
            if platform.system() == 'Windows':
                windows = pwc.getWindowsWithTitle(os.path.basename(path))
                if windows:
                    win = windows[0]
                    if win.minimize():
                        win.restore(True)
                    win.activate(True)
                else:
                    print('Window not found with specified title.')
            elif platform.system() == 'Darwin':  # macOS
                # macOS does not support window manipulation like Windows, so just reveal the file in Finder
                subprocess.run(['open', '-R', path2])

    if mode == 'final':
        output_file = filedialog.asksaveasfile(
            defaultextension=".gif",
            initialfile=f"{os.path.splitext(os.path.basename(input_file))[0]}.gif",
            filetypes=[("GIF files", "*.gif")],
        )
        if output_file:
            output_file.close()
            output_folder = os.path.abspath(output_file.name)
            output_dir = os.path.dirname(output_file.name)

            loading_thread_switch(True)
            video_to_frames_seq(input_file, framerate)
            vid_to_gif(framerate, gifQ, motionQ, lossyQ, output_file)
            loading_thread_switch(False)

            print("Conversion complete!")
            shutil.rmtree('temp')
            on_settings_window_close()
            openOutputFolder(output_dir, output_folder)
            # open_finish_window()

    elif mode == 'temp':
            output_file = 'temp/temp.gif'
            print(output_file)

            loading_thread_switch(True)
            vid_to_gif(framerate, gifQ, motionQ, lossyQ, output_file)
            loading_thread_switch(False)

            print("Conversion complete!")


    elif mode == 'temp-final':
        output_file = filedialog.asksaveasfile(
            defaultextension=".gif",
            initialfile=f"{os.path.splitext(os.path.basename(input_file))[0]}.gif",
            filetypes=[("GIF files", "*.gif")],
        )

        if output_file:
            output_file.close()
            output_folder = os.path.abspath(output_file.name)
            output_dir = os.path.dirname(output_file.name)

            shutil.copy2('temp/temp.gif', output_file.name)
            print("Conversion complete!")
            shutil.rmtree('temp')
            on_settings_window_close()
            openOutputFolder(output_dir, output_folder)


def apply_settings(mode):
    global fps, gif_quality_scale, scale_widget, extra_var, fast_var, motion_quality_scale, lossy_quality_scale, motion_var, lossy_var, scaled_width, scaled_height, safeAlpha

    fps_value = fps.get()
    scale_value = scale_widget.get()
    extra_value = extra_var.get()
    fast_value = fast_var.get()
    motion_value = motion_var.get()
    lossy_value = lossy_var.get()
    gif_quality_value = gif_quality_scale.get()
    motion_quality= motion_quality_scale.get()
    lossy_quality =lossy_quality_scale.get()
    width_value = video_data['width']
    height_value = video_data['height']
    unpremultiply_value = safeAlpha.get()
        

    if width_value and height_value:
        # Calculate the scaled width based on the slider value
        scaled_width = int(width_value * scale_value / 100)

        # Maintain the aspect ratio
        scaled_height = int((scaled_width / width_value) * height_value)

    print(f"Settings applied - FPS: {fps_value}, Scale: {scaled_width} x {scaled_height}")
    print("GIF Quality:", gif_quality_value)
    
    print("Motion Quality On:", motion_value)
    if motion_value:
        print("Motion Quality:", motion_quality)
    
    print("Lossy Quality On:", lossy_value)
    if lossy_value:
        print("Lossy Quality:", lossy_quality)
    
    print("Extra:", extra_value)
    print("Fast:", fast_value)
    print('unpremultiply:', unpremultiply_value)
    
    convert_and_save(fps, gif_quality_scale, motion_quality_scale, lossy_quality_scale, file_path, mode)

def choose_file():
    global file_path
    file_path = filedialog.askopenfilename(
        title="Select Video File",
        filetypes=(("Video files", "*" + " *".join(video_extensions)), ("All files", "*.*"))
    )
    get_and_print_video_data(file_path)

settings_window_open = False

def on_settings_window_close():
    global settings_window_open
    settings_window_open = False
    settings_window.destroy()
    print(settings_window_open)
    
## let's impliment the hover for info for less GUI clutter.    
def open_settings_window(): 
    global settings_window_open, fps, gif_quality_scale, scale_widget, extra_var, fast_var, settings_window, motion_quality_scale, lossy_quality_scale, motion_var, lossy_var, safeAlpha
    
    if not settings_window_open:
        settings_window_open = True
        print(settings_window_open)
    
    settings_window = tk.Toplevel(root)
    settings_window.title("User Settings")
    center_window(settings_window, 350, 720)
    settings_window.iconphoto(True, icon)
    watermark_label(settings_window)
    make_non_resizable(settings_window)

    preview_label = tk.Label(settings_window, text='Click the Preview button to, well... Preview the GIF.')
    preview_label.pack(pady=5)
    
    fileSize_label =tk.Label(settings_window, text = '')
    fileDimension_label = tk.Label(settings_window, text='')
    fileSize_label.pack()
    fileDimension_label.pack(pady=5)
    
    playframe = tk.Frame(settings_window)
    playframe.pack()
    play_gif_button = Button(playframe, text='Play GIF', command=lambda: play_gif('temp/temp.gif'))
    play_gif_button.pack(pady=10)
    play_gif_button.config(state="disabled")
    
    if args.debug:
        play_gif_button.pack(side=tk.LEFT, pady=10)
        debug_gif_button = Button(playframe, text='Debug GIF', command=lambda: get_and_print_video_data('temp/temp.gif'))
        debug_gif_button.pack(side=tk.RIGHT, pady=10)
        debug_gif_button.config(state="disabled")

    separator1 = ttk.Separator(settings_window, orient="horizontal")
    separator1.pack(fill="x", padx=20, pady=4)
    
    gif_quality_label = tk.Label(settings_window, text="GIF Quality:")
    gif_quality_label.pack()
    gif_quality_scale = tk.Scale(settings_window, from_=100, to=1, orient=tk.HORIZONTAL, resolution=1, length=300)
    gif_quality_scale.set(90)
    gif_quality_scale.pack()
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
    
    motion_var = tk.IntVar()
    motion_quality_label = tk.Checkbutton(settings_window, text="Motion Quality:", variable=motion_var, command=lambda: update_checkbox_state(motion_var, motion_quality_scale, cmode = 'quality'))
    motion_quality_label.pack()
    motion_quality_scale = tk.Scale(settings_window, from_=100, to=1,orient=tk.HORIZONTAL, resolution=1, length=300, sliderrelief='flat')
    motion_quality_scale.set(100)
    motion_quality_scale.pack()
    motion_quality_scale['state'] = 'disabled'
    Hovertip(motion_quality_label, "Turn this on to fine-tune the Motion Quality (affects overall Quality.)", hover_delay=500)
    Hovertip(motion_quality_scale, "Lower values reduce motion.", hover_delay=500)
    # separator3 = ttk.Separator(settings_window, orient="horizontal")
    # separator3.pack(fill="x", padx=20, pady=2)
    lossy_var = tk.IntVar()
    lossy_quality_label = tk.Checkbutton(settings_window, text="Lossy Quality:", variable=lossy_var, command=lambda: update_checkbox_state(lossy_var, lossy_quality_scale, cmode = 'quality'))
    lossy_quality_label.pack()
    lossy_quality_scale = tk.Scale(settings_window, from_=100, to=1, orient=tk.HORIZONTAL, resolution=1, length=300, sliderrelief='flat')
    lossy_quality_scale.set(100)
    lossy_quality_scale.pack()
    lossy_quality_scale['state'] = 'disabled'
    Hovertip(lossy_quality_scale, "Turn this on to fine-tune the Lossy Quality (affects overall Quality.)", hover_delay=500)
    Hovertip(lossy_quality_label, "Lower values introduce noise and streaks.", hover_delay=500)
    # separator4 = ttk.Separator(settings_window, orient="horizontal")
    # separator4.pack(fill="x", padx=20, pady=2)

    fps_label = tk.Label(settings_window, text="Frames Per Second:")
    fps_label.pack()
    
    fps_limit = min(parsed_framerate, 30)
    
    fps = tk.Scale(settings_window, from_=1, to=fps_limit, orient=tk.HORIZONTAL, resolution=1, length=300)
    fps.set(30)
    fps.pack()

    # separator5 = ttk.Separator(settings_window, orient="horizontal")
    # separator5.pack(fill="x", padx=20, pady=4)

    scale_label_0 = tk.Label(settings_window, text="Scale:")
    scale_label_0.pack()
    scale_widget = tk.Scale(settings_window, from_=25, to=100, orient=tk.HORIZONTAL, length=300)
    scale_widget.set(100)
    scale_widget.pack()    
    scale_label_var = tk.StringVar()
    scale_widget.config(command=lambda value: update_scale_label(value))
    scale_label_var.set(f"{video_data['width']}x{video_data['height']} - Scale: {scale_widget.get()}%")
    scale_label = tk.Label(settings_window, textvariable=scale_label_var)
    scale_label.pack()
    
    separator6 = ttk.Separator(settings_window, orient="horizontal")
    separator6.pack(fill="x", padx=20, pady=2)
    
    spacer = tk.Label(settings_window, text="Encode Quality:")
    spacer.pack(pady=5)
    
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
    
    safeAlpha = tk.IntVar()
    unprenmult_checkbox = tk.Checkbutton(alphaFrame, variable=safeAlpha, text="Unpremultiply")
    if video_data['pix_fmt'] in alpha_formats:
        separator2.pack(fill="x", padx=20, pady=2)
        
        alphaFrame.pack()
        alphaLabel.pack()
        unprenmult_checkbox.pack(pady=5)
        
        Hovertip(unprenmult_checkbox, "It\'s like unmult but more precise.\nEnable this if your GIF has outlines.", hover_delay=500)
        root.update_idletasks()
    
    buttonsFrame = tk.Frame(settings_window)
    buttonsFrame.pack(pady=10)
    
    apply_button = Button(buttonsFrame, text="Quick Export", command=lambda: threading.Thread(target=apply_settings, args=('final', ), daemon=True).start())
    apply_button.pack(side=tk.LEFT, padx=5)
    
    test_button = Button(buttonsFrame, text="Apply & Preview", command=lambda: threading.Thread(target=preview_gif_window, daemon=True).start())
    test_button.pack(side=tk.RIGHT, padx=5)
    
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
    
    def preview_gif_window():
        play_gif_button.config(state="normal")
        if args.debug:
            debug_gif_button.config(state="normal")
            
        loading_thread_switch(True)
        video_to_frames_seq(file_path, fps.get())
        loading_thread_switch(False)
        
        apply_settings('temp')
        
        img = Image.open(output_file)
        aspect_ratio = img.width / img.height
        imgW, imgH = img.size
        gcd = math.gcd(imgW, imgH)
        aspect_ratio_simplified = f'{imgW // gcd}:{imgH // gcd}'
        
        if img.width > img.height:  # Landscape
            target_width = min(img.width, 450)
            target_height = int(target_width / aspect_ratio)
        else:  # Portrait or square
            target_height = min(img.height, 300)
            target_width = int(target_height * aspect_ratio)
        
        img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(img)
        center_window(settings_window, 480, 970)
        settings_window.update_idletasks()

        preview_label.config(text="")
        preview_label.img = tk_img
        preview_label.config(image=tk_img)
        
        apply_button.config(text='Save As...', command=lambda: apply_settings('temp-final'))
        
        filesize = get_filesize('temp/temp.gif')
        fileSize_label.config(text=f'GIF Size: {filesize}')
        fileDimension_label.config(text=f'Dimensions: {imgW}x{imgH} ({aspect_ratio_simplified})')
        
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

    root.withdraw()
    settings_window.grab_set()
    settings_window.wait_window(settings_window)
    if os.path.exists('temp'):
        shutil.rmtree('temp') 
        print("temp removed successfully.")
    else:
        print("temp does not exist.")
    root.deiconify()


# Create the main window
root = TkinterDnD.Tk()
if any(char.isalpha() for char in __version__):
    if bundle_path:
        icon =  PhotoImage(file=os.path.join(bundle_path, 'ico3beta.png'))
    else:
        icon =  PhotoImage(file='./buildandsign/ico/ico3beta.png')
else:
    if bundle_path:
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
if args.Egg:
    splash_geo_x = 400
    splash_geo_y = 400
center_window(splash_screen, splash_geo_x, splash_geo_y)




gif_path = 'splash.gif'
if bundle_path:
    gif_path = os.path.join(bundle_path, gif_path)
else:
    gif_path = './/splash//splash.gif'

if args.Egg:
    gif_path = 'splashEE.gif'
    if bundle_path:
        gif_path = os.path.join(bundle_path, gif_path)
    else:
        gif_path = './/splash//splashEE.gif'

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

loop_switch = bool(args.Egg)
animate(0, loop_switch)

def show_main():    
    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        
    def drag_enter(event):
        drop_label.config
        label.config

    def drag_leave(event):
        drop_label.config
        label.config
        
    def on_drop(event):
        global file_path
        drop_label.config
        label.config
        file_path = event.data.strip('{}')
        threading.Thread(target=get_and_print_video_data, args=(file_path, )).start()
    
    if any(char.isalpha() for char in __version__):
        root.title(f"N8's Video to GIF Converter Early Access {__version__}")
        
    else:
        root.title(f"N8's Video to GIF Converter {__version__}")

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

    # Create a Canvas with a grey broken-line border - doesnt work lol
    canvas = tk.Canvas(root, bd=2, relief="ridge")
    canvas.pack(expand=True, fill="both")

    # Create a Label for the drop area
    drop_label = tk.Label(canvas, text="Drag and Drop Video Files Here", padx=20, pady=20)
    drop_label.pack(expand=True, fill="both")

    # Bind the drop event to the on_drop function
    drop_label.bind("<Enter>", drag_enter)
    drop_label.bind("<Leave>", drag_leave)
    drop_label.drop_target_register(DND_FILES)
    drop_label.dnd_bind('<<Drop>>', on_drop)
    canvas.bind("<Enter>", drag_enter)
    canvas.bind("<Leave>", drag_leave)
    canvas.dnd_bind('<<Drop>>', on_drop)
    canvas.drop_target_register(DND_FILES)

    print("Current working directory:", os.getcwd())
    print("Executable path:", sys.executable)

    # logo on drop event area
    DnDLogo = 'ico3.png' 
    if bundle_path:
        DnDLogo = os.path.join(bundle_path, DnDLogo)
    else:
        DnDLogo = './buildandsign/ico/ico3.png'
    imgYPos = 225


    if args.Egg:
        DnDLogo = 'amor.png' 
        if bundle_path:
            DnDLogo = os.path.join(bundle_path, DnDLogo)
        else:
            DnDLogo = './buildandsign/ico/amor.png'
        
        imgYPos = 200

    image = tk.PhotoImage(file=DnDLogo)
    resized_image = image.subsample(2)
    label = tk.Label(canvas, image=resized_image, bd=0)
    label.image = resized_image
    label.place(x=geo_width / 2, y=imgYPos, anchor=tk.CENTER)
    
    splash_screen.destroy()
    root.deiconify()

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

