from __version__ import __version__, __appname__, __ffmpegversion__, __gifskiversion__, __updatername__, __updaterversion__
import tkinter as tk
from tkinter import filedialog, ttk
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

import argparse
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('-v', '--version', action='version', version = __version__)
args = parser.parse_args()

print("Current version:", __version__)

video_data = None
global mode



# for windows executables, basically makes this readable inside an exe
if any(char.isalpha() for char in __version__):
    icon = 'icoDev.ico'
else:
    icon = 'ico.ico'
    
ffprobe = 'ffprobe.exe'
ffplay = 'ffplay.exe'
gifski = 'gifski.exe'
ffmpeg = 'ffmpeg.exe'
if hasattr(sys, '_MEIPASS'):
    icon = os.path.join(sys._MEIPASS, icon)
    ffprobe = os.path.join(sys._MEIPASS, ffprobe)
    ffplay = os.path.join(sys._MEIPASS, ffplay)
    gifski = os.path.join(sys._MEIPASS, gifski)
    ffmpeg = os.path.join(sys._MEIPASS, ffmpeg)

def create_popup(root, title, width, height, switch):
    popup = tk.Toplevel(root)
    popup.title(title)
    popup.geometry(f"{width}x{height}")
    popup.iconbitmap(icon)
    # popup.overrideredirect(True)
    popup.attributes('-toolwindow', 1)
    center_window(popup, width, height)
    
    if switch == 1:
        popup.bind("<FocusOut>", lambda e: popup.destroy())

    popup.grab_set()
    
    return popup

# IDK HOW BUT PLEASE WHAT THE FUCK
def loading(mode):
    global loading_screen
    def load_start():

        loading_screen = create_popup(root, "Converting...", 350, 120, 0)
        make_non_resizable(loading_screen)
        
        load_text_label = tk.Label(loading_screen, text='Converting...\nPlease wait.')
        load_text_label.pack(pady=20)

        progress_bar = ttk.Progressbar(loading_screen, mode='indeterminate')
        progress_bar.pack(fill=tk.X, padx=10, pady=0)
        progress_bar.start()

    def load_stop():
        loading_screen.destroy()

    if mode == 1:
        load_start()
    elif mode == 0:
        load_stop()

def run_loading():
    threading.Thread(target=loading, args=(1,),  daemon=True).start()

# if Updater not found, download on github.
def get_latest_release_version():
    global n8_gif_repo

    n8_gif_repo = "https://api.github.com/repos/n8ventures/v2g-con-personal/releases/latest"
    response = requests.get(n8_gif_repo)
    if response.status_code == 200:
        release_info = json.loads(response.text)
        return release_info.get('tag_name', '0.0.0')
    else:
        return '0.0.0'

def downloadUpdater():
    global latest_release_version

    response = requests.get(n8_gif_repo)
    if response.status_code == 200:
        release_data = response.json()
        latest_release_version = get_latest_release_version()
        if latest_release_version == '0.0.0':
            return 'ERR_NO_CONNECTION'
        else:
            latest_file = f'{__updatername__}.exe'
            
            for asset in release_data['assets']:
                
                if asset['name'] == latest_file:
                    download_url = asset['browser_download_url']
                    updaterURL = requests.get(download_url)

                    with open(latest_file, 'wb') as file:
                        file.write(updaterURL.content)
                        return 'UPDR_DONE'
            else:
                print('File not found!')
                return 'ERR_NOT_FOUND'
    else:
        print("Failed to retrieve updater information. Please check your internet connection.")
        return 'ERR_NO_CONNECTION'


def UPDATER_POPUP(title, msg):
    updaterMenu = create_popup(root, title, 400, 120, 1)
    make_non_resizable(updaterMenu)
    
    txt_msg = msg
    
    txt_label = tk.Label(updaterMenu, text=txt_msg)
    txt_label.pack()
    
    close_button = ttk.Button(updaterMenu, text="Close", command=updaterMenu.destroy)
    
    close_button.pack(pady=10)
    
    root.update()

def updaterExists():
    get_latest_release_version()
    if not os.path.exists(f"{__updatername__}.exe"):
        downloadUpdater()
        print('latest release:', latest_release_version)


# threading.Thread(target=updaterExists).start()
updaterExists()

def CheckUpdates():
    
    def execute_download_updater():
        UPDATER_POPUP('Downloading updater...', '\nDownloading the uploader!\nYou may still use the program freely!\nWe\'ll run the updater once the download has been finished!')
        update_result = downloadUpdater()
        if update_result == 'ERR_NO_CONNECTION':
            UPDATER_POPUP('Updater Download Failed!', '\nERROR: Download Failed!\nPlease check your internet connection and try again later!')
        elif update_result == 'ERR_NOT_FOUND':
            UPDATER_POPUP('Updater Download Failed!', '\nERROR: Download Failed!\nFile not found!')
        elif update_result == 'UPDR_DONE':
            subprocess.Popen(f'{__updatername__}.exe')
            
    if not os.path.exists(f"{__updatername__}.exe"):
        print('updater not found')
        execute_download_updater()
    else:
        if __version__ < get_latest_release_version():
            print('downloading updater')
            execute_download_updater()
        else:
            print('opening updater')
            subprocess.Popen(f'{__updatername__}.exe')

def about():
    geo_width = 370
    geo_len= 420
    aboutmenu = create_popup(root, "About Us!", geo_width, geo_len, 1)
    make_non_resizable(aboutmenu)

    gifski_text = f"- Gifski (https://gif.ski/)\nVersion: {__gifskiversion__}"
    ffmpeg_text = f"- FFmpeg (https://ffmpeg.org/)\nVersion: {__ffmpegversion__}"
    about_text = (
        "\nThis program is built for personal use only.\n\n"
        "Credits:\n\n"
        f"{gifski_text}\n\n"
        f"{ffmpeg_text}\n"
    )

    about_label = tk.Label(aboutmenu, text=about_text, justify=tk.LEFT)
    about_label.pack(pady=10)

    mailto_label = tk.Label(aboutmenu, text="nate@n8ventures.dev", fg="blue", cursor="hand2")
    mailto_label.pack()
    mailto_label.bind("<Button-1>", lambda e: open_link("mailto:nate@n8ventures.dev"))

    github_label = tk.Label(aboutmenu, text="https://github.com/n8ventures", fg="blue", cursor="hand2")
    github_label.pack(pady=5)
    github_label.bind("<Button-1>", lambda e: open_link("https://github.com/n8ventures"))

    close_button = ttk.Button(aboutmenu, text="Close", command=aboutmenu.destroy)
    close_button.pack(pady=10)
    
    image_path = 'motionteamph.png' 
    if hasattr(sys, '_MEIPASS'):
        image_path = os.path.join(sys._MEIPASS, image_path)
    else:
        image_path = '.\\buildandsign\\ico\\motionteamph.png' 

    image = tk.PhotoImage(file=image_path)
    label = tk.Label(aboutmenu, image=image, bd=0)
    label.image = image
    label.place(x=geo_width / 2, y=geo_len - 60, anchor=tk.CENTER)
    Hovertip(label, "BetMGM Manila Motions Team 2024")

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
    frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=2)

    separator_wm = ttk.Separator(frame, orient="horizontal")
    separator_wm.pack(side=tk.BOTTOM, fill=tk.Y, padx=10)
    
    watermark_label = tk.Label(frame, text="by N8VENTURES (github.com/n8ventures)", fg="gray")
    watermark_label.pack(side=tk.LEFT, anchor=tk.SW, padx=2)
    
    version_label = tk.Label(frame, text=f"version: {__version__}", fg="gray")
    version_label.pack(side=tk.RIGHT, anchor=tk.SE, padx=2)

def make_non_resizable(window):
    window.resizable(False, False)

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = width  
    window_height = height
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2  
    window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position-30}")

def get_filesize(file_path):
    size_bytes = os.path.getsize(file_path)
    size_mb = round(size_bytes / (1024 * 1024), 2)
    size_kb = round(size_bytes / 1024, 2)
    return f'{size_mb} MB ({size_kb} KB)'

def get_video_data(input_file):
    cmd = [
        ffprobe,
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,duration,pix_fmt",
        "-of", "json",
        input_file
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    
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
    
    filtergraph = []
    
    filtergraph.append(f'fps={str(framerate)}')
    
    if scale_widget.get() != 100:
        filtergraph.append(f'scale={scaled_width}:{scaled_height},setsar=1')
    
    if video_data['pix_fmt'] in alpha_formats:
        filtergraph.append('unpremultiply=inplace=1')

    cmd.append(','.join(filtergraph))
    cmd.append(os.path.join(temp_folder, 'frames%04d.png'))
    # subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
    
def vid_to_gif(fps, gifQuality, motionQuality, lossyQuality, output):

    if hasattr(output, 'name'):
        output_file = output.name
    elif isinstance(output, str):
        output_file = output

    cmd = [
        gifski,
        "-q",
        "-r", str(fps),
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
        
    cmd.extend(["-o", output_file, "temp/frames*.png"])

    # subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW)

def get_and_print_video_data(file_path):
    global video_data
    print(f"File dropped: {file_path}")
    
    if file_path and is_video_file(file_path):
        video_data = get_video_data(file_path)
        
        if video_data:
            width_value = video_data['width']
            height_value = video_data['height']
            fps_value = round(eval(video_data['r_frame_rate']), 3)
            duration_value = video_data['duration']
            pix_fmt = video_data['pix_fmt']
            print("Video width:", width_value)
            print("Video height:", height_value)
            print("Frame rate:", fps_value)
            print("Duration:", duration_value)
            print("pixel format:", pix_fmt)
        
            if not settings_window_open:
                open_settings_window()
    else:
        notavideo = create_popup(root, "NOT A VIDEO FILE!", 400, 100, 1)
        make_non_resizable(notavideo)

        errortext = (
            "Not a video! Please select a video file!"
        )

        about_label = tk.Label(notavideo, text=errortext, justify=tk.LEFT)
        about_label.pack(pady=10)

        close_button = ttk.Button(notavideo, text="Close", command=notavideo.destroy)
        close_button.pack(pady=10)
                
def is_video_file(file_path):
    # might need this later for the file dialog on importing it...
    global video_extensions
    _, file_extension = os.path.splitext(file_path)
    video_extensions = [
    '.3g2', '.3gp', '.amv', '.asf', '.avi', '.drc', '.f4v', '.flv', '.gif', '.gifv', '.m2ts', 
    '.m2v', '.m4p', '.m4v', '.mkv', '.mng', '.mov', '.mp2', '.mp4', '.mpe', '.mpeg', '.mpg', 
    '.mpv', '.mts', '.mxf', '.nsv', '.ogg', '.ogv', '.qt', '.rm', '.rmvb', '.roq', '.svi', 
    '.ts', '.vob', '.webm', '.wmv', '.yuv'
    ]

    return file_extension.lower() in video_extensions

def is_folder_open(path):
    open_folders = subprocess.check_output('tasklist /v /fi "imagename eq explorer.exe"', shell=True).decode('utf-8')
    folder_name = os.path.basename(path)
    return folder_name in open_folders

def convert_and_save(fps, gif_quality, motion_quality, lossy_quality, input_file, mode):
    global output_file
    framerate = fps.get()
    gifQ = gif_quality.get()
    motionQ= motion_quality.get()
    lossyQ = lossy_quality.get()

    def openOutputFolder(path):
        print('checking if window is open...')
        if not is_folder_open(path):
            print('window not found, opening window.')
            subprocess.run(fr'explorer /select,"{path}"')
        else:
            print('window found!')
            windows = pwc.getWindowsWithTitle(os.path.basename(path))
            if windows:
                windows[0].activate(True)
            else:
                print('Window not found with specified title.')
    
    if mode == 'final':
        output_file = filedialog.asksaveasfile(
            defaultextension=".gif",
        initialfile=os.path.splitext(os.path.basename(input_file))[0] + ".gif",
        filetypes=[("GIF files", "*.gif")]
        )
        if output_file:
            output_file.close()
            output_folder = os.path.abspath(output_file.name)
            output_dir = os.path.dirname(output_file.name)
            
            video_to_frames_seq(input_file, framerate)
            vid_to_gif(framerate, gifQ, motionQ, lossyQ, output_file)
            
            print("Conversion complete!")
            shutil.rmtree('temp')
            on_settings_window_close()
            openOutputFolder(output_dir)
            # open_finish_window()
            
    elif mode == 'temp':
            output_file = 'temp.gif'
            print(output_file)
            # run_loading()
            vid_to_gif(framerate, gifQ, motionQ, lossyQ, output_file)
            # loading(0)
            print("Conversion complete!")
            
            
    elif mode == 'temp-final':
        output_file = filedialog.asksaveasfile(
        defaultextension=".gif",
        initialfile=os.path.splitext(os.path.basename(input_file))[0] + ".gif",
        filetypes=[("GIF files", "*.gif")]
        )
        
        if output_file:
            output_file.close()
            output_folder = os.path.abspath(output_file.name)
            output_dir = os.path.dirname(output_file.name)
            
            shutil.copy2('temp.gif', output_file.name)
            print("Conversion complete!")
            shutil.rmtree('temp')
            on_settings_window_close()
            openOutputFolder(output_dir)


def apply_settings(mode):
    global fps, gif_quality_scale, scale_widget, extra_var, fast_var, motion_quality_scale, lossy_quality_scale, motion_var, lossy_var
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
    
    convert_and_save(fps, gif_quality_scale, motion_quality_scale, lossy_quality_scale, file_path, mode)

def choose_file():
    global file_path
    file_path = filedialog.askopenfilename(
        title="Select Video File",
        filetypes=(("Video files", "*.mp4;*.avi;*.mkv;*.mov"), ("All files", "*.*"))
    )
    get_and_print_video_data(file_path)

# Unused (Might need to figure this one out sooner or later...)
def open_finish_window():
    global finish_window
    finish_window = tk.Toplevel(root)
    finish_window.title("Done!")
    center_window(finish_window, 300, 300)
    finish_window.iconbitmap(icon)
    watermark_label(finish_window)
    make_non_resizable(finish_window)

    finish_close_label = tk.Label(finish_window, text="Conversion Complete!")
    finish_close_label.pack()

    finish_close_button = tk.Button(finish_window, text="Close", command=lambda: finish_window.destroy())
    finish_close_button.pack(pady=30)

    # Disable the root window
    root.withdraw()

    # Make the finish_window modal (only interactable) and wait for it to be closed
    finish_window.grab_set()
    finish_window.wait_window(finish_window)

    # Re-enable the root window when finish_window is closed
    root.deiconify()

settings_window_open = False

def on_settings_window_close():
    global settings_window_open
    settings_window_open = False
    settings_window.destroy()
    print(settings_window_open)

def on_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
    
## let's impliment the hover for info for less GUI clutter.    
def open_settings_window(): 
    global settings_window_open, fps, gif_quality_scale, scale_widget, extra_var, fast_var, settings_window, motion_quality_scale, lossy_quality_scale, motion_var, lossy_var
    
    if not settings_window_open:
        settings_window_open = True
        print(settings_window_open)
    
    settings_window = tk.Toplevel(root)
    settings_window.title("User Settings")
    center_window(settings_window, 350, 800)
    settings_window.iconbitmap(icon)
    watermark_label(settings_window)
    make_non_resizable(settings_window)

    preview_label = tk.Label(settings_window, text='Click the Preview button to, well... Preview the GIF.')
    preview_label.pack(pady=5)
    
    fileSize_label =tk.Label(settings_window, text = '')
    fileSize_label.pack(pady=5)
    
    play_gif_button = tk.Button(settings_window, text='Play GIF', command=lambda: play_gif('temp.gif'))
    play_gif_button.pack(pady=10)
    play_gif_button.config(state="disabled")
    
    separator1 = ttk.Separator(settings_window, orient="horizontal")
    separator1.pack(fill="x", padx=20, pady=4)
    
    gif_quality_label = tk.Label(settings_window, text="GIF Quality:")
    gif_quality_label.pack()
    gif_quality_scale = tk.Scale(settings_window, from_=100, to=1, orient=tk.HORIZONTAL, resolution=1, length=300)
    gif_quality_scale.set(90)
    gif_quality_scale.pack()
    Hovertip(gif_quality_label, "Overall GIF Quality", hover_delay=500)
    Hovertip(gif_quality_scale, "Overall GIF Quality", hover_delay=500)
    
    # separator2 = ttk.Separator(settings_window, orient="horizontal")
    # separator2.pack(fill="x", padx=20, pady=2)
    
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
    Hovertip(motion_quality_label, "Lower values reduce motion.", hover_delay=500)
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
    Hovertip(lossy_quality_scale, "Lower values introduce noise and streaks.", hover_delay=500)
    Hovertip(lossy_quality_label, "Lower values introduce noise and streaks.", hover_delay=500)
    # separator4 = ttk.Separator(settings_window, orient="horizontal")
    # separator4.pack(fill="x", padx=20, pady=2)

    fps_label = tk.Label(settings_window, text="Frames Per Second:")
    fps_label.pack()
    fps = tk.Scale(settings_window, from_=1, to=30, orient=tk.HORIZONTAL, resolution=1, length=300)
    fps.set(30)
    fps.pack()

    # separator5 = ttk.Separator(settings_window, orient="horizontal")
    # separator5.pack(fill="x", padx=20, pady=4)

    scale_label_0 = tk.Label(settings_window, text="Scale:")
    scale_label_0.pack()
    scale_widget = tk.Scale(settings_window, from_=25, to=100, orient=tk.HORIZONTAL, resolution=5, length=200)
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

    extra_var = tk.IntVar()
    extra_checkbox = tk.Checkbutton(settings_window, variable=extra_var, text="Extra", command=lambda: update_checkbox_state(extra_var, extra_checkbox, fast_var, fast_checkbox,  cmode = 'encode'))
    extra_checkbox.pack()
    Hovertip(extra_checkbox, "Extra - slower encoding, but 1% better quality.", hover_delay=500)
    fast_var = tk.IntVar()
    fast_checkbox = tk.Checkbutton(settings_window, variable=fast_var, text="Fast", command=lambda: update_checkbox_state(fast_var, fast_checkbox, extra_var, extra_checkbox,  cmode = 'encode'))
    fast_checkbox.pack()
    Hovertip(fast_checkbox, "Fast - faster encoding, but 10% worse quality & larger file size.", hover_delay=500)
    apply_button = tk.Button(settings_window, text="Convert!", width=10, command=lambda: apply_settings(mode='final'))
    apply_button.pack(side=tk.LEFT, pady=5)
    
    test_button = tk.Button(settings_window, text="Test/Preview", width=24, command=lambda: preview_gif_window())
    test_button.pack(side=tk.RIGHT, pady=5)
    
    width = max(apply_button.winfo_reqwidth(), test_button.winfo_reqwidth())
    x_position = (settings_window.winfo_width() - width) // 2
    apply_button.pack_configure(padx=(x_position - 5, 5))
    test_button.pack_configure(padx=(5, x_position - 5))
    
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
        # global preview_gif_window
        # preview_gif_window = tk.Toplevel(root)
        # preview_gif_window.title("Check the gif")
        # preview_gif_window.geometry("500x500")
        # preview_gif_window.iconbitmap(icon)
        # watermark_label(preview_gif_window)
        play_gif_button.config(state="normal")
        
        video_to_frames_seq(file_path, fps.get())
        
        apply_settings(mode='temp')
        
        img = Image.open(output_file)
        aspect_ratio = img.width / img.height
        
        if img.width > img.height:  # Landscape
            target_width = min(img.width, 450)
            target_height = int(target_width / aspect_ratio)
        else:  # Portrait or square
            target_height = min(img.height, 300)
            target_width = int(target_height * aspect_ratio)
        
        img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(img)
        center_window(settings_window, 480, 950)
        settings_window.update_idletasks()

        preview_label.config(text="")
        preview_label.img = tk_img
        preview_label.config(image=tk_img)
        
        apply_button.config(text='Save', command=lambda: apply_settings(mode='temp-final'))
        
        filesize = get_filesize('temp.gif')
        fileSize_label.config(text=f'GIF Size: {filesize}')
        
        
    settings_window.protocol("WM_DELETE_WINDOW", lambda: on_settings_window_close())
    
        
    def play_gif(file_path):
        cmd = [
        ffplay,
        "-loglevel", "-8",
        "-loop", "0",
        file_path
    ]

        subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW)

    root.withdraw()
    settings_window.grab_set()
    settings_window.wait_window(settings_window)
    if os.path.exists('temp'):
        shutil.rmtree('temp')
        os.remove('temp.gif')
        print("temp removed successfully.")
    else:
        print("temp does not exist.")
    root.deiconify()

    
def drag_enter(event):
    drop_label.config(bg="lightgray")
    label.config(bg="lightgray")

def drag_leave(event):
    drop_label.config(bg="white")
    label.config (bg="white")
def on_drop(event):
    global file_path
    drop_label.config(bg="white")
    label.config (bg="white")
    file_path = event.data.strip('{}')
    get_and_print_video_data(file_path)
    
# Create the main window
root = TkinterDnD.Tk()

if any(char.isalpha() for char in __version__):
    root.title(f"N8's Video to GIF Converter Early Access {__version__}")
    
else:
    root.title(f"N8's Video to GIF Converter {__version__}")

geo_width= 425
center_window(root, geo_width, 450)
root.iconbitmap(icon)
make_non_resizable(root)
watermark_label(root)

spacer = tk.Label(root, text="")
spacer.pack(pady=10)

# Create a button to choose a file
choose_button = tk.Button(root, text="Choose Video File", command=choose_file)
choose_button.pack(pady=20)

or_label = tk.Label(root, text="Or")
or_label.pack(pady=20)

# Create a Canvas with a grey broken-line border - doesnt work lol
canvas = tk.Canvas(root, bd=2, relief="ridge")
canvas.pack(expand=True, fill="both")

# Create a Label for the drop area
drop_label = tk.Label(canvas, text="Drag and Drop Video Files Here", padx=20, pady=20, bg="white")
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
image_path = 'amor.png' 
if hasattr(sys, '_MEIPASS'):
    image_path = os.path.join(sys._MEIPASS, image_path)
else:
    image_path = '.\\buildandsign\\ico\\amor.png' 

image = tk.PhotoImage(file=image_path)
resized_image = image.subsample(2)
label = tk.Label(canvas, image=resized_image, bd=0, bg="white")
label.image = resized_image
label.place(x=geo_width / 2, y=200, anchor=tk.CENTER)
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

root.mainloop()