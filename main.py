import tkinter as tk
from tkinter import filedialog, ttk, colorchooser, PhotoImage
from tkinterdnd2 import DND_FILES
from PIL import Image, ImageTk
import subprocess
import os
import shutil
import sys
import atexit
from idlelib.tooltip import Hovertip
import threading
import time
import math
import re
import glob

# version info
from __version__ import __version__

# splash screen module
from modules.rootTkSplashModule import (
    root,
    splash_screen,
    animate
)
# tk popups and settings
from modules.PopupModules import (
    create_popup, 
    notavideo,
    )

from modules.TkModules import (
    make_non_resizable, center_window,
    Button, widget_color,
    )
# platform-specific modules 
from modules.platformModules import (
    win, mac,
    bundle_path,
    icon, 
    ffmpeg, gifski, 
    openOutputFolder
    )

# info modules
from modules.infoModules import watermark_label

# data/binary module
from modules.dataBinaryModules import (
    get_filesize, get_video_data, 
    video_extensions, alpha_formats,
    is_video_file,
    play_gif,
    )

from modules.UpdaterModule import autoChecker


if win:
    from modules.argsModule import args

debug = ''

if win and args.debug:
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
if win and args.Egg:
    debug = '(Egg me up)'
print("Current version:", __version__)


global mode
video_data = None
running = False
after_id = None
loading_screen = None

def remove_temp(force = False):
    print('Removing temp...')
    if force:
        shutil.rmtree('temp') 
        print("temp force-removed successfully.")
    else:
        if os.path.exists('temp'):
            shutil.rmtree('temp') 
            print("temp removed successfully.")
        else:
            print("temp does not exist.")

def loading(root, texthere='', filenum=0, filestotal=0):
    global loading_screen, load_text_label

    if loading_event.is_set():
        if not loading_screen: 
            loading_screen = create_popup(root, "Converting...", 380, 150, 0)
            make_non_resizable(loading_screen)
            
            load_text_label = ttk.Label(loading_screen, text='Converting...\nPlease wait.', anchor="center", justify="center")
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

def loading_thread(root, texthere='', filenum=0, filestotal=0):
    loading_event.set()
    print('starting thread')
    loading(root, texthere, filenum, filestotal)

def loading_thread_switch(root, switch, texthere='', filenum=0, filestotal=0):
    if switch:
        threading.Thread(target=loading_thread, args=(root, texthere, filenum, filestotal), daemon=True).start()
        print('Thread Initialized.')
    else:
        print('killing loading popup')
        loading_event.clear()
        root.after(0, loading(root))


def stop_gif_animation(widget):
    global running, after_id
    running = False
    if after_id:
        widget.after_cancel(after_id)
        after_id = None

def load_gifpreview_frames():
    folder = 'temp/preview'
    frame_files = sorted([os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.png')])
    return [Image.open(frame_file) for frame_file in frame_files]

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
            max_width=350
            target_width = min(scaled_width , max_width)
            target_height = int(target_width / aspect_ratio)
        else:  # Portrait or square
            max_height=280
            target_height = min(scaled_height, max_height)
            target_width = int(target_height * aspect_ratio)

        preview_height = target_height
        preview_weight = target_width
        
        filtergraph.append(f'scale={target_width}:{target_height},setsar=1')

    if safeAlpha.get():
        filtergraph.append('unpremultiply=inplace=1')

    cmd.append(','.join(filtergraph))

    if preview == False:
        cmd.append(os.path.join(temp_folder, 'frames%04d.png'))
    else:
        cmd.append(os.path.join(preview_folder, 'preview%04d.png'))
    
    if win:
        # subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
        if args.debug:
            print(cmd)

    elif mac:
        subprocess.run(cmd)

def vid_to_gif(fps, gifQuality, motionQuality, lossyQuality, output, data=None):
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
            "-W", str(data['width']),
            "-H", str(data['height']),
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
        cmd.extend(["-o", output_file])
        cmd.extend(input_files)

    if win:
        # subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
        if args.debug:
            print(cmd)
    elif mac:
        subprocess.run(cmd)

def get_and_print_video_data(file_path):
    global video_data, valid_files, invalid_files, batch_video_data
    invalid_files = []
    valid_files = []
    batch_video_data = []

    if file_path == '':
        print('No video File dropped.')
        return

    print(f"Files: {file_path}")

    if isinstance(file_path, str):
        if file_path and is_video_file(file_path) and file_path == 'temp/temp.gif':
            if temp_data := get_video_data(file_path):
                parse_temp_data(temp_data)
    else:
        for file in file_path:
            if not is_video_file(file):
                print(f'File "{file}" is not a supported video file.')
                invalid_files.append(os.path.basename(file))
                continue

            valid_files.append((os.path.basename(file), file))
    
        def invalid_check():
            if invalid_files:
                notavideo(invalid_files,[f[0] for f in valid_files])

        if win:
            invalid_check()

        if valid_files and not settings_window_open:
            if len(valid_files) == 1:
                if video_data := get_video_data(valid_files[0][1]):
                    parse_video_data(video_data)
            else:
                for filename, full_path in valid_files:  
                    if batch_data := get_video_data(full_path):
                        batch_video_data.append((filename, batch_data))
                
                open_settings_window()

        if mac:
            invalid_check()

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

    debug_gif_label = ttk.Label(debug_gif_window, text=debug_gif_text, anchor="w")
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


def convert_and_save(fps, gif_quality, motion_quality, lossy_quality, input_file, mode):
    global output_file
    framerate = fps.get()
    gifQ = gif_quality.get()
    motionQ= motion_quality.get()
    lossyQ = lossy_quality.get()

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

            loading_thread_switch(root, True, os.path.basename(file))

            video_to_frames_seq(file, framerate)
            vid_to_gif(framerate, gifQ, motionQ, lossyQ, output_file)
            
            print("SINGLE FINAL: ", loading_screen)
            
            loading_thread_switch(root, False)

            print("Conversion complete!")
            remove_temp(True)
            on_settings_window_close()
            try:
                openOutputFolder(output_dir, output_full_path)
            except OSError as e:
                print(f"Error: {e}")

        elif output_directory:
            loading_thread_switch(root, True, input_file[0][0], 1, len(input_file))

            for filenum, (file_name, full_path) in enumerate(input_file, start=1):
                for file_name2, data in batch_video_data:
                    if file_name == file_name2:
                        output = os.path.normpath(
                            os.path.join(
                                output_directory, f"{os.path.splitext(file_name)[0]}.gif"
                                )
                            )
                        
                        if loading_screen:
                            update_loading(file_name, filenum, len(input_file))
                        
                        video_to_frames_seq(full_path, framerate)
                        vid_to_gif(framerate, gifQ, motionQ, lossyQ, output, data)
                        remove_temp(True)
            
            loading_thread_switch(root, False)
            on_settings_window_close()
            try:
                openOutputFolder(output_directory, output)
            except OSError as e:
                print(f"Error: {e}")

    elif mode == 'temp':
            output_file = 'temp/temp.gif'
            print(output_file)

            vid_to_gif(framerate, gifQ, motionQ, lossyQ, output_file)
            video_to_frames_seq(output_file, fps.get(), preview=True)
            loading_thread_switch(root, False)

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
            remove_temp(True)
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
    center_window(root, 425, 450)
    print('Settings Window is open?', settings_window_open)
    if mac:
        remove_temp()
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
        preview_label_text = 'Click the Apply & Preview button\nto load a GIF Preview.'
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
    center_window(settings_window, 350, win_height)
    settings_window.title(window_title)
    if win:
        settings_window.iconbitmap(icon)
    watermark_label(settings_window, debug)
    make_non_resizable(settings_window)

    preview_label = ttk.Label(settings_window, text = preview_label_text, anchor="center", justify="center")
    preview_label.pack(pady=preview_label_pady)
    
    fileSize_label = ttk.Label(settings_window, text = '', anchor="center")
    fileDimension_label = ttk.Label(settings_window, text='', anchor="center")
    fileSize_label.pack()
    fileDimension_label.pack(pady=5)
    
    playframe = ttk.Frame(settings_window)
    playframe.pack()
    play_gif_button = Button(playframe, text='No GIF loaded', command=lambda: play_gif('temp/temp.gif'))
    play_gif_button.pack(pady=10)
    play_gif_button.config(state="disabled")
    
    if win and args.debug and len(valid_files) == 1:
        play_gif_button.pack(side=tk.LEFT, pady=10)
        debug_gif_button = Button(playframe, text='Debug GIF', command=lambda: get_and_print_video_data('temp/temp.gif'))
        debug_gif_button.pack(side=tk.RIGHT, pady=10)
        debug_gif_button.config(state="disabled")

    separator1 = ttk.Separator(settings_window, orient="horizontal")
    separator1.pack(fill="x", padx=20, pady=4)
    
    gif_quality_scale = tk.Scale(settings_window, from_=1, to=100, orient=tk.HORIZONTAL, resolution=1, length=300, troughcolor=widget_color[0])
    gif_quality_scale.set(90)
    gif_quality_scale.pack()
    gif_quality_label = ttk.Label(settings_window, text="GIF Quality")
    gif_quality_label.pack()
    Hovertip(gif_quality_label, "Overall GIF Quality", hover_delay=500)
    Hovertip(gif_quality_scale, "Overall GIF Quality", hover_delay=500)
    
    def update_checkbox_state(var, widget, other_var=None, other_widget=None, cmode=None, color = False):
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
                if color:
                    widget.config(troughcolor=widget_color[1])
                else:
                    widget.config(troughcolor=widget_color[0])
            else:
                widget['state'] = 'disabled'
                widget['takefocus'] = False
                widget['sliderrelief'] = 'flat'
                if color:
                    widget.config(troughcolor=widget_color[3])
                else:
                    widget.config(troughcolor=widget_color[2])

        elif cmode == 'basic':
            if var.get() == 1:
                widget['state'] = 'normal'
            else:
                widget['state'] = 'disabled'

    if len(valid_files) != 1:
        fps_limit = 30
    else:
        fps_limit = min(parsed_framerate, 30)
    
    fps = tk.Scale(settings_window, from_=1, to=fps_limit, orient=tk.HORIZONTAL, resolution=1, length=300, fg=widget_color[1], troughcolor=widget_color[1])
    fps.set(fps_limit)
    fps.pack()
    fps_label = ttk.Label(settings_window, text="Frames Per Second", style="Alt.TLabel")
    fps_label.pack()

    if len(valid_files) == 1:
        scale_widget = tk.Scale(settings_window, from_=1, to=100, orient=tk.HORIZONTAL, resolution=0.5, length=300, troughcolor=widget_color[0])
        scale_widget.set(100)
        scale_widget.pack()    
        scale_label_var = tk.StringVar()
        scale_widget.config(command=lambda value: update_scale_label(value))
        scale_label_var.set(f"{video_data['width']}x{video_data['height']} - Scale: {scale_widget.get()}%")
        scale_label = ttk.Label(settings_window, textvariable=scale_label_var)
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
    
    optionalFrame = ttk.Frame(settings_window)
    optionalFrame.pack()
    optionalLabel = ttk.Label(optionalFrame, text="Optional Settings:")
    optionalLabel.pack()
    
    motion_var = tk.IntVar()
    motion_quality_scale = tk.Scale(optionalFrame, from_=1, to=100,orient=tk.HORIZONTAL, resolution=1, length=300, sliderrelief='flat', fg=widget_color[1], troughcolor=widget_color[3])
    motion_quality_scale.set(100)
    motion_quality_scale.pack()
    motion_quality_scale['state'] = 'disabled'
    motion_quality_checkbutton = ttk.Checkbutton(optionalFrame, text="Motion Quality", variable=motion_var, command=lambda: update_checkbox_state(motion_var, motion_quality_scale, cmode = 'quality', color = True), style="Alt.TCheckbutton")
    motion_quality_checkbutton.pack()
    Hovertip(motion_quality_checkbutton, "Turn this on to fine-tune the Motion Quality (affects overall Quality.)", hover_delay=500)
    Hovertip(motion_quality_scale, "Lower values reduce motion.", hover_delay=500)

    lossy_var = tk.IntVar()
    lossy_quality_scale = tk.Scale(optionalFrame, from_=1, to=100, orient=tk.HORIZONTAL, resolution=1, length=300, sliderrelief='flat', troughcolor=widget_color[2])
    lossy_quality_scale.set(100)
    lossy_quality_scale.pack()
    lossy_quality_scale['state'] = 'disabled'
    lossy_quality_checkbutton = ttk.Checkbutton(optionalFrame, text="Lossy Quality", variable=lossy_var, command=lambda: update_checkbox_state(lossy_var, lossy_quality_scale, cmode = 'quality'))
    lossy_quality_checkbutton.pack()
    Hovertip(lossy_quality_scale, "Turn this on to fine-tune the Lossy Quality (affects overall Quality.)", hover_delay=500)
    Hovertip(lossy_quality_checkbutton, "Lower values introduce noise and streaks.", hover_delay=500)

    separator6 = ttk.Separator(settings_window, orient="horizontal")
    separator6.pack(fill="x", padx=20, pady=2)
    
    spacer = ttk.Label(settings_window, text="Encode Quality:")
    spacer.pack()
    
    checkboxFrame = ttk.Frame(settings_window)
    checkboxFrame.pack(pady=5)
    
    extra_var = tk.IntVar()
    extra_checkbox =ttk.Checkbutton(checkboxFrame, variable=extra_var, text="Extra Quality", command=lambda: update_checkbox_state(extra_var, extra_checkbox, fast_var, fast_checkbox,  cmode = 'encode'))
    extra_checkbox.pack(side=tk.LEFT)
    Hovertip(extra_checkbox, "Slower encoding, but 1% better quality.", hover_delay=500)
    
    fast_var = tk.IntVar()
    fast_checkbox = ttk.Checkbutton(checkboxFrame, variable=fast_var, text="Fast Quality", command=lambda: update_checkbox_state(fast_var, fast_checkbox, extra_var, extra_checkbox,  cmode = 'encode'))
    fast_checkbox.pack(side=tk.RIGHT)
    Hovertip(fast_checkbox, "Faster encoding, but 10% worse quality & larger file size.", hover_delay=500)
    
    # iunpremultiply option
    alphaFrame = ttk.Frame(settings_window)
    separator2 = ttk.Separator(settings_window, orient="horizontal")
    alphaLabel = ttk.Label(alphaFrame, text='Alpha Options:')
    matteFrame = ttk.Frame(settings_window)
    separator3 = ttk.Separator(settings_window, orient="horizontal")
    
    safeAlpha = tk.IntVar()
    unprenmult_checkbox = ttk.Checkbutton(alphaFrame, variable=safeAlpha, text="Unpremultiply")
    
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
    matte_checkbox = ttk.Checkbutton(matteFrame, variable=enableMatte, command=lambda: update_checkbox_state(enableMatte, matte_button, cmode = 'basic'))
    matte_button = Button(matteFrame, text="Choose Matte", command=pick_color)
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

    # Export and Preview Buttons
    buttonsFrame = ttk.Frame(settings_window)
    buttonsFrame.pack(pady=10)
    
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
        loading_thread_switch(root, True, os.path.basename(valid_files[0][1]))
        video_to_frames_seq(valid_files[0][1], fps.get())
        
        apply_settings('temp')
        
        play_gif_button.config(state="normal", text='Play GIF on Full Size')
        if win and args.debug:
                debug_gif_button.config(state="normal")
        
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
    root.withdraw()

    if not invalid_files:
        if mac:
            settings_window.grab_set()
            settings_window.wait_visibility()
        elif win:
            settings_window.grab_set()

    if win:
        settings_window.wait_window(settings_window)
        root.deiconify()

loop_switch = False
if win:
    loop_switch = bool(args.Egg)

animate(0, loop_switch)
# Create the main window
def show_main():    
    def on_drop(event):
        global file_path
        print(f'File Path PASS I: {event.data}')
        file_path = re.findall(r'\{.*?\}|\S+', event.data)
        print(f'File Path PASS II: {file_path}')
        file_path = [re.sub(r'[{}]', '', file) for file in file_path]
        print(f'File Path PASS III: {file_path}')

        if win:
            threading.Thread(target=get_and_print_video_data, args=(file_path, )).start()
        elif mac:
            get_and_print_video_data(file_path)

    if any(char.isalpha() for char in __version__):
        root.title("N8's Video to Gifski (Beta)")
    else:
        root.title("N8's Video to Gifski")

    geo_width= 425
    center_window(root, geo_width, 450)
    make_non_resizable(root)
    watermark_label(root, debug)

    spacer = ttk.Label(root, text="")
    spacer.pack(pady=10)

    # Create a button to choose a file
    choose_button = Button(root, text="Choose Video File", command=choose_file)
    choose_button.pack(pady=20)

    or_label = ttk.Label(root, text="Or")
    or_label.pack(pady=20)

    # Create a Canvas
    canvas = ttk.Frame(root)
    canvas.pack(expand=True, fill="both")

    # Create a Label for the drop area
    drop_label = ttk.Label(canvas, text="Drag and Drop Video Files Here")
    drop_label.pack(pady = 60)

    # Bind the drop event to the on_drop function
    def reg_dnd(widget):
        widget.drop_target_register(DND_FILES)
        widget.dnd_bind('<<Drop>>', on_drop)

    reg_dnd(drop_label)
    reg_dnd(canvas)
    reg_dnd(or_label)
    reg_dnd(root)

    print("Current working directory:", os.getcwd())
    print("Executable path:", sys.executable)

    # logo on drop event area
    DnDLogo = 'ico3.png'
    if bundle_path:
        DnDLogo = os.path.join(bundle_path, DnDLogo)
    else:
        DnDLogo = './buildandsign/ico/ico3.png'
    imgYPos = 225


    if win and args.Egg:
        DnDLogo = 'amor.png' 
        if hasattr(sys, '_MEIPASS'):
            DnDLogo = os.path.join(sys._MEIPASS, DnDLogo)
        else:
            DnDLogo = './buildandsign/ico/amor.png'

        imgYPos = 200

    image = tk.PhotoImage(file=DnDLogo)
    resized_image = image.subsample(2)
    label = tk.Label(canvas, image=resized_image, bd=0)
    label.image = resized_image
    label.place(x=geo_width / 2, y=imgYPos, anchor=tk.CENTER)

    root.update_idletasks()
    splash_screen.destroy()
    root.deiconify()

    threading.Thread(target=autoChecker, daemon=True).start()    

def on_closing():
    remove_temp()
    print("Closing the application.")
    
    atexit.unregister(on_closing)  # Unregister the atexit callback
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
atexit.register(on_closing)

splash_screen.after(3500, show_main)

root.mainloop()