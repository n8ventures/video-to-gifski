from tkinter import filedialog, ttk, colorchooser, PhotoImage
import tkinter as tk
import customtkinter as ctk
from tkinterdnd2 import DND_FILES
from PIL import Image, ImageTk
import subprocess
import os
import shutil
import sys
import atexit
from CTkToolTip import CTkToolTip
import threading
import time
import math
import re
import glob

# splash screen module
from modules.rootTkSplashModule import (
    root,
    splash_screen,
    animate,
    DISABLED_FG,
    NORMAL_FG,
)

# ctk popups and settings
from modules.PopupModules import (
    create_popup,
    notavideo,
)

from modules.TkModules import (
    apply_emoji,
    make_non_resizable,
    center_window,
    Button,
    Label,
    Frame,
    Slider,
    animate_alpha,
)

# platform-specific modules
from modules.platformModules import (
    win,
    mac,
    bundle_path,
    icon,
    ffmpeg,
    gifski,
    openOutputFolder,
    temp_dir,
    config_dir,
    page_cache_dir,
)

# version info
if win:
    from __version__ import __version__
else:
    from __version__ import __versionMac__ as __version__

# info modules
from modules.infoModules import watermark_label

# data/binary module
from modules.dataBinaryModules import (
    get_filesize,
    get_video_data,
    video_extensions,
    alpha_formats,
    is_video_file,
    play_gif,
)

from modules.UpdaterModule import autoChecker

if win:
    from modules.argsModule import args

from modules.configModule import set_setting

print("Current version:", __version__)


def print_cmd(cmd, data=""):
    """
    Prints the gifski/ffmpeg command, but collapses a long run of frame
    PNGs into a compact "first .. last (N frames)" summary instead of
    dumping every single path inline — unreadable once a video has more
    than a handful of extracted frames.
    """
    frame_paths = [c for c in cmd if isinstance(c, str) and re.search(r"frames\d+\.png$", c)]
    if len(frame_paths) > 2:
        non_frame_parts = [c for c in cmd if c not in frame_paths]
        summary = (
            f"[{os.path.basename(frame_paths[0])} .. {os.path.basename(frame_paths[-1])} ({len(frame_paths)} frames)]"
        )
        print(non_frame_parts + [summary])
    else:
        print(f"{data}\n{cmd}")


global mode
video_data = None
running = False
after_id = None
loading_screen = None
_last_frame_extraction_key = None
_last_rendered_settings = None

# --- TEMP PATHS
temp_gif = os.path.join(temp_dir, "temp.gif")
preview_folder = os.path.join(temp_dir, "preview")


def Tooltip(widget, message, delay, **kwargs):
    # NOTE: Due to Tk9.0 i will be temporarily disable this until CustomTkinter finds a way to restore transparency.
    return
    BG_COLOR = "#1e1e1e" if ctk.get_appearance_mode() == "Light" else "#ede5da"
    FG_COLOR = "#ede5da" if ctk.get_appearance_mode() == "Light" else "#1e1e1e"
    CTkToolTip(
        widget=widget,
        message=message,
        delay=delay,
        bg_color=BG_COLOR,
        text_color=FG_COLOR,
        border_color=FG_COLOR,
        border_width=2,
        corner_radius=40,
        **kwargs,
    )


def _extraction_key():
    return (
        valid_files[current_video_index][1],
        fps.get(),
        scale_widget.get(),
        safeAlpha.get(),
    )


def remove_temp(path_to_clean, force=False):
    print(f"Removing temp at: {path_to_clean}")

    if force:
        shutil.rmtree(path_to_clean, ignore_errors=True)
        print("Temp force-removed successfully.")
    else:
        if os.path.exists(path_to_clean):
            try:
                shutil.rmtree(path_to_clean)
                print("Temp removed successfully.")
            except OSError as e:
                print(f"Error removing temp: {e}")
        else:
            print("Temp does not exist.")


# loading and preview functions
def loading(root, texthere="", filenum=0, filestotal=0):
    global loading_screen, load_text_label, progress_bar

    if loading_event.is_set():
        if not loading_screen:
            loading_screen = create_popup(root, "Converting...", 380, 150, 0)
            make_non_resizable(loading_screen)

            load_text_label = Label(
                loading_screen,
                text="Converting...\nPlease wait.",
                anchor="center",
                justify="center",
            )
            load_text_label.pack(pady=20)

            update_loading(texthere, filenum, filestotal)

            progress_bar = ctk.CTkProgressBar(loading_screen, mode="indeterminate")
            progress_bar.pack(fill=ctk.X, padx=10, pady=0)
            progress_bar.start()
            loading_screen.update_idletasks()
            print("starting loading popup")
    else:
        if loading_screen:
            progress_bar.stop()
            loading_screen.destroy()
            loading_screen = None
            print("loading popup dead")


def update_loading(texthere="", filenum=0, filestotal=0):
    max_length = 45
    if len(texthere) > max_length:
        part_len = (max_length - 3) // 2
        texthere = texthere[:part_len] + "..." + texthere[-part_len:]

    if filenum == 0 and filestotal == 0 or filestotal == 1:
        load_text_label.configure(text=f"{texthere}\n\nConverting...\nPlease wait.")
    else:
        load_text_label.configure(
            text=f"({filenum}/{filestotal} Files)\n{texthere}\n\nConverting...\nPlease wait.",
        )

    loading_screen.update_idletasks()


loading_event = threading.Event()


def loading_thread(root, texthere="", filenum=0, filestotal=0):
    loading_event.set()
    print("starting thread")
    loading(root, texthere, filenum, filestotal)


def loading_thread_switch(root, switch, texthere="", filenum=0, filestotal=0):
    if switch:
        threading.Thread(
            target=loading_thread,
            args=(root, texthere, filenum, filestotal),
            daemon=True,
        ).start()
        print("Thread Initialized.")
    else:
        print("killing loading popup")
        loading_event.clear()
        root.after(0, loading, root)


def stop_gif_animation(widget):
    global running, after_id
    running = False
    if after_id:
        widget.after_cancel(after_id)
        after_id = None


def load_gifpreview_frames():
    folder = preview_folder
    frame_files = sorted(
        [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".png")],
    )
    frames = []
    for frame_file in frame_files:
        img = Image.open(frame_file)
        img.load()
        frames.append(img)
    return frames


def animate_gif_preview(frames, widget, frame_num, loop, frame_duration):
    frame = frames[frame_num]
    global running, after_id
    if not running:
        return

    ctk_frame = ctk.CTkImage(light_image=frame, dark_image=frame, size=frame.size)
    widget.configure(image=ctk_frame)
    widget.image = ctk_frame

    frame_num = (frame_num + 1) % len(frames)
    if loop or frame_num != 0:
        after_id = widget.after(frame_duration, animate_gif_preview, frames, widget, frame_num, loop, frame_duration)


def start_gif_animation(widget, loop=True, fps=30, frames=None):
    global running
    running = True
    if frames is None:
        frames = load_gifpreview_frames()
    frame_duration = int(1000 // fps)
    animate_gif_preview(frames, widget, 0, loop, frame_duration)


# core process
def video_to_frames_seq(input_file, framerate, apply_scale=None, preview=False):
    global preview_height, preview_weight

    if preview == False:
        stop_gif_animation(preview_label)
        if os.path.exists(temp_dir) and os.listdir(temp_dir):
            shutil.rmtree(temp_dir)
    else:
        os.makedirs(preview_folder, exist_ok=True)

    os.makedirs(temp_dir, exist_ok=True)

    cmd = [
        ffmpeg,
        "-loglevel",
        "-8",
        "-i",
        input_file,
        "-vf",
    ]

    filtergraph = [f"fps={str(framerate)}"]

    if preview == False:
        should_scale = apply_scale if apply_scale is not None else (len(valid_files) == 1 and scale_widget.get() != 100)
        if should_scale:
            filtergraph.append(f"scale={scaled_width}:{scaled_height},setsar=1")
    else:
        aspect_ratio = scaled_width / scaled_height

        if scaled_width > scaled_height:  # Landscape
            max_width = 350
            target_width = min(scaled_width, max_width)
            target_height = int(target_width / aspect_ratio)
        else:  # Portrait or square
            max_height = 280
            target_height = min(scaled_height, max_height)
            target_width = int(target_height * aspect_ratio)

        preview_height = target_height
        preview_weight = target_width

        filtergraph.append(
            f"scale={target_width}:{target_height},setsar=1",
        )

    if safeAlpha.get():
        filtergraph.append("unpremultiply=inplace=1")

    cmd.append(",".join(filtergraph))

    if preview == False:
        cmd.append(os.path.join(temp_dir, "frames%04d.png"))
    else:
        cmd.append(os.path.join(preview_folder, "preview%04d.png"))

    if win:
        subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW)

    elif mac:
        subprocess.run(cmd)

    print_cmd(cmd, "### FFMPEG: ")


def vid_to_gif(
    fps,
    gifQuality,
    motionQuality,
    lossyQuality,
    output,
    data=None,
):
    global matte_var

    if hasattr(output, "name"):
        output_file = output.name
    elif isinstance(output, str):
        output_file = output

    if data is None:
        cmd = [
            gifski,
            "-q",
            "-r",
            str(int(fps)),
            "-Q",
            str(int(gifQuality)),
            "-W",
            str(scaled_width),
            "-H",
            str(scaled_height),
            "--repeat",
            "0",
        ]
    else:
        cmd = [
            gifski,
            "-q",
            "-r",
            str(int(fps)),
            "-Q",
            str(int(gifQuality)),
            "-W",
            str(data["width"]),
            "-H",
            str(data["height"]),
            "--repeat",
            "0",
        ]

    if extra_var.get():
        cmd.append("--extra")
    if fast_var.get():
        cmd.append("--fast")
    if motion_var.get():
        cmd.extend(["--motion-quality", str(int(motionQuality))])
    if lossy_var.get():
        cmd.extend(["--lossy-quality", str(int(lossyQuality))])
    if enableMatte.get():
        if matte_var is None:
            matte_var = "#FFFFFF"
            print("matte is not set. using default hex value #FFFFFF or white")

        cmd.extend(["--matte", matte_var])

    frame_pattern = os.path.join(temp_dir, "frames*.png")

    if win:
        if glob.glob(frame_pattern):
            cmd.extend(["-o", output_file])
            cmd.append(frame_pattern)

        subprocess.run(
            cmd,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

    elif mac:
        input_files = sorted(glob.glob(frame_pattern))
        if input_files:
            cmd.extend(["-o", output_file])
            cmd.extend(input_files)

        subprocess.run(cmd)

    print_cmd(cmd, "### GIFSKI: ")


def get_and_print_video_data(file_path):
    global video_data, valid_files, invalid_files, batch_video_data
    global _last_frame_extraction_key
    global advanced_mode, current_video_index

    _last_frame_extraction_key = None

    invalid_files = []
    valid_files = []
    batch_video_data = []

    per_video_settings.clear()
    page_preview_cache.clear()
    advanced_mode = False
    current_video_index = 0
    if os.path.exists(page_cache_dir):
        shutil.rmtree(page_cache_dir)

    if file_path == "":
        print("No video File dropped.")
        return

    print(f"Files: {file_path}")

    if isinstance(file_path, str):
        if file_path and is_video_file(file_path) and file_path == temp_gif:
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
                notavideo(invalid_files, [f[0] for f in valid_files])

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
    width_value = temp_data["width"]
    height_value = temp_data["height"]
    fps_value = round(eval(temp_data["r_frame_rate"]), 3)
    duration_value = temp_data["duration"]
    pix_fmt = temp_data["pix_fmt"]

    fps_int = round(fps_value)
    total_frames = int(float(duration_value) * fps_int)
    hours = total_frames // (3600 * fps_int)
    remaining_frames = total_frames % (3600 * fps_int)
    minutes = remaining_frames // (60 * fps_int)
    remaining_frames %= 60 * fps_int
    seconds = remaining_frames // fps_int
    frames = remaining_frames % fps_int
    timecode = f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}"

    debug_gif_window = create_popup(root, "Debugging GIF", 200, 200, 1)
    make_non_resizable(debug_gif_window)

    debug_gif_text = f"""
        Video width: {width_value}
        Video height: {height_value}
        Framerate: {fps_value}
        Duration: {duration_value}
        Frames: {total_frames}
        Timecode: {timecode}
        pixel format: {pix_fmt}"""

    debug_gif_label = Label(debug_gif_window, text=debug_gif_text, anchor="w")
    debug_gif_label.pack()

    close_button = Button(
        debug_gif_window,
        text="Close",
        command=debug_gif_window.destroy,
    )
    close_button.pack(pady=10)

    if not settings_window_open:
        open_settings_window()


def parse_video_data(video_data):
    global parsed_framerate

    width_value = video_data["width"]
    height_value = video_data["height"]
    fps_value = round(eval(video_data["r_frame_rate"]), 3)
    duration_value = video_data["duration"]
    pix_fmt = video_data["pix_fmt"]

    fps_int = round(fps_value)
    total_frames = int(float(duration_value) * fps_int)
    hours = total_frames // (3600 * fps_int)
    remaining_frames = total_frames % (3600 * fps_int)
    minutes = remaining_frames // (60 * fps_int)
    remaining_frames %= 60 * fps_int
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


def convert_and_save(
    fps,
    gif_quality,
    motion_quality,
    lossy_quality,
    input_file,
    mode,
):
    global output_file
    framerate = fps.get()
    gifQ = gif_quality.get()
    motionQ = motion_quality.get()
    lossyQ = lossy_quality.get()

    file = input_file[0][1]
    if mode == "final":
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
                initialdir=f"{os.path.dirname(input_file[0][1])}",
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
            remove_temp(temp_dir, True)
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
                            os.path.join(output_directory, f"{os.path.splitext(file_name)[0]}.gif")
                        )
                        if loading_screen:
                            update_loading(file_name, filenum, len(input_file))

                        if advanced_mode:
                            s = per_video_settings.get(file_name, _default_video_settings())
                            w = int(data["width"] * s["scale"] / 100)
                            h = int((w / data["width"]) * data["height"])
                            global scaled_width, scaled_height
                            scaled_width, scaled_height = w, h
                            video_to_frames_seq(full_path, s["fps"], apply_scale=(s["scale"] != 100))
                            vid_to_gif(
                                s["fps"], s["gif_quality"], s["motion_quality"], s["lossy_quality"], output, data
                            )
                        else:
                            video_to_frames_seq(full_path, framerate)
                            vid_to_gif(framerate, gifQ, motionQ, lossyQ, output, data)

                        remove_temp(temp_dir, True)

            loading_thread_switch(root, False)
            on_settings_window_close()
            try:
                openOutputFolder(output_directory, output)
            except OSError as e:
                print(f"Error: {e}")

    elif mode == "temp":
        output_file = temp_gif
        print(output_file)

        vid_to_gif(framerate, gifQ, motionQ, lossyQ, output_file)
        video_to_frames_seq(output_file, fps.get(), preview=True)
        loading_thread_switch(root, False)

        print("Conversion complete!")

    elif mode == "temp-final":
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

            shutil.copy2(temp_gif, output_file.name)
            print("Conversion complete!")
            stop_gif_animation(preview_label)
            remove_temp(temp_dir, True)
            on_settings_window_close()
            try:
                openOutputFolder(output_dir, output_full_path)
            except OSError as e:
                print(f"Error: {e}")

    elif mode == "advanced-save":
        filename = input_file[current_video_index][0]
        cached = page_preview_cache.get(filename)
        source_gif = cached["gif_path"] if cached else temp_gif
        file = input_file[current_video_index][1]
        output_file = filedialog.asksaveasfile(
            defaultextension=".gif",
            initialdir=f"{os.path.dirname(file)}",
            initialfile=f"{os.path.splitext(os.path.basename(file))[0]}.gif",
            filetypes=[("GIF files", "*.gif")],
        )

        if output_file:
            output_file.close()
            shutil.copy2(source_gif, output_file.name)
            output_full_path = os.path.abspath(output_file.name)
            output_dir = os.path.dirname(output_file.name)

            shutil.copy2(temp_gif, output_file.name)
            print(f"Saved '{os.path.basename(file)}' individually.")
            try:
                openOutputFolder(output_dir, output_full_path)
            except OSError as e:
                print(f"Error: {e}")


def apply_settings(mode):
    global fps, gif_quality_scale, scale_widget, extra_var, fast_var
    global motion_quality_scale, lossy_quality_scale, motion_var, lossy_var
    global scaled_width, scaled_height, safeAlpha

    fps_value = fps.get()
    extra_value = extra_var.get()
    fast_value = fast_var.get()
    motion_value = int(motion_var.get())
    lossy_value = int(lossy_var.get())
    gif_quality_value = int(gif_quality_scale.get())
    motion_quality = motion_quality_scale.get()
    lossy_quality = lossy_quality_scale.get()
    unpremultiply_value = safeAlpha.get()

    if len(valid_files) == 1:
        scale_value = scale_widget.get()
        width_value = video_data["width"]
        height_value = video_data["height"]

        if width_value and height_value:
            # Calculate the scaled width based on the slider value
            scaled_width = int(width_value * scale_value / 100)

            # Maintain the aspect ratio
            scaled_height = int((scaled_width / width_value) * height_value)

        print(f"-- SETTINGS APPLIED --\nFPS: {fps_value} - Scale: {scaled_width} x {scaled_height}")
        print("GIF Quality:", gif_quality_value)

        print("Motion Quality:", bool(motion_value))
        if bool(motion_value):
            print("Motion Quality Value:", int(motion_quality))

        print("Lossy Quality:", bool(lossy_value))
        if bool(lossy_value):
            print("Lossy Quality Value:", int(lossy_quality))

        print("Extra:", bool(extra_value))
        print("Fast:", bool(fast_value))
        print("unpremultiply:", bool(unpremultiply_value))

    file = valid_files
    convert_and_save(
        fps,
        gif_quality_scale,
        motion_quality_scale,
        lossy_quality_scale,
        file,
        mode,
    )


def choose_file():
    global file_path
    file_path = filedialog.askopenfilenames(
        title="Select Video File/s",
        filetypes=(
            ("Video files", "*" + " *".join(video_extensions)),
            ("All files", "*.*"),
        ),
    )
    get_and_print_video_data(file_path)


# pagination (batch mode)
per_video_settings = {}  # filename -> dict of that file's settings
current_video_index = 0
advanced_mode = False
page_preview_cache = {}


def _default_video_settings(fps_hint=30):
    return {
        "fps": fps_hint,
        "scale": 100,
        "gif_quality": 90,
        "motion_enabled": 0,
        "motion_quality": 100,
        "lossy_enabled": 0,
        "lossy_quality": 100,
        "extra": 0,
        "fast": 0,
        "unpremultiply": 0,
        "matte_enabled": 0,
        "matte_color": None,
    }


# settings window
settings_window_open = False


def on_settings_window_close():
    global settings_window_open
    settings_window_open = False
    settings_window.destroy()
    center_window(root, 425, 450)
    print("Settings Window is open?", settings_window_open)
    if mac:
        remove_temp(temp_dir)
        root.deiconify()


def open_settings_window():
    global settings_window_open, fps, scale_widget, extra_var, fast_var
    global settings_window, motion_var, lossy_var, safeAlpha, preview_label
    global gif_quality_scale, motion_quality_scale, lossy_quality_scale
    global enableMatte, matte_var

    if not settings_window_open:
        settings_window_open = True
        print("Settings Window is open?", settings_window_open)

    win_width = 950
    win_height = 520
    SIDE_PANE_WIDTH = round(win_height / 3)
    PREVIEW_PANE_WIDTH = win_width - (SIDE_PANE_WIDTH * 2)

    if len(valid_files) == 1:
        window_title = "User Settings"
        preview_label_text = "Click the Apply & Preview button\nto load a GIF Preview."
        export_label = "Quick Export"
        preview_label_pady = 5
    else:
        window_title = "User Settings: Batch Mode"
        preview_label_text = (
            "Multiple videos detected!\nAdjust the settings to apply\n" "the same configuration to all GIFs converted!"
        )
        export_label = "Export All"
        preview_label_pady = 20

    settings_window = ctk.CTkToplevel(root)
    settings_window.withdraw()
    center_window(settings_window, win_width, win_height)
    settings_window.title(window_title)
    if win:
        settings_window.iconbitmap(icon)
    watermark_label(settings_window)
    make_non_resizable(settings_window)

    # =================================================================
    # MAIN FRAME — Setup
    # =================================================================
    main_frame = Frame(settings_window, fg_color="transparent", border_width=0)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    main_frame.grid_columnconfigure(0, weight=0)  # required settings — fixed width
    main_frame.grid_columnconfigure(1, weight=1)  # preview — expands to fill space
    main_frame.grid_columnconfigure(2, weight=0)  # optional settings — fixed width
    main_frame.grid_rowconfigure(0, weight=1)

    required_frame = Frame(main_frame, border_width=0, width=SIDE_PANE_WIDTH, fg_color="transparent")
    preview_frame = Frame(main_frame, border_width=0, width=PREVIEW_PANE_WIDTH)
    optional_frame = Frame(main_frame, border_width=0, width=SIDE_PANE_WIDTH, fg_color="transparent")

    required_frame.grid(row=0, column=0, sticky="ns", padx=(0, 10))
    preview_frame.grid(row=0, column=1, sticky="nsew", padx=10)
    optional_frame.grid(row=0, column=2, sticky="ns", padx=(10, 0))

    # =================================================================
    # MIDDLE COLUMN — Preview
    # =================================================================
    preview_label = Label(
        preview_frame,
        text=preview_label_text,
        anchor="center",
        justify="center",
    )
    preview_label.pack(pady=preview_label_pady, fill="both", expand=True)

    fileSize_label = Label(preview_frame, text="", anchor="center")
    fileDimension_label = Label(preview_frame, text="", anchor="center")

    fileDimension_label.pack(pady=5, side=ctk.BOTTOM)
    fileSize_label.pack(pady=2, side=ctk.BOTTOM)

    playframe = Frame(preview_frame, fg_color="transparent", border_width=0)

    play_gif_button = Button(
        playframe,
        text="No GIF loaded",
        command=lambda: play_gif(temp_gif),
    )

    page_label = Label(preview_frame, text="")

    prev_chevron = ctk.CTkLabel(preview_frame, text="", cursor="hand2")
    apply_emoji(prev_chevron, "◀", px=20)
    next_chevron = ctk.CTkLabel(preview_frame, text="", cursor="hand2")
    apply_emoji(next_chevron, "▶", px=20)

    prev_chevron.bind("<Button-1>", lambda e: _navigate(-1))
    next_chevron.bind("<Button-1>", lambda e: _navigate(1))

    # =================================================================
    # LEFT COLUMN — Required settings + export/preview buttons
    # =================================================================
    required_label = Label(required_frame, text="Required Settings", font=("", 15, "bold"))
    required_label.pack(pady=(0, 5))

    separator1 = ttk.Separator(required_frame, orient="horizontal")
    separator1.pack(fill="x", pady=4)

    def attach_slider_value_label(parent, slider, format_fn, initial_value=None, disabled_text=None):
        var = ctk.StringVar()
        value = initial_value if initial_value is not None else slider.get()
        var.set(format_fn(value))

        label = Label(parent, textvariable=var)
        label.pack()

        def _update(value):
            var.set(format_fn(value))

        def set_disabled(is_disabled):
            if is_disabled and disabled_text is not None:
                var.set(disabled_text)
            else:
                var.set(format_fn(slider.get()))

        slider.configure(command=_update)
        return var, label, set_disabled, _update

    gif_quality_scale = Slider(
        required_frame,
        from_=1,
        to=100,
        width=220,
        height=20,
        number_of_steps=99,
    )
    gif_quality_scale.set(90)
    gif_quality_scale.pack(pady=(5, 0))
    gif_quality_var, gif_quality_value_label, _, gif_quality_update = attach_slider_value_label(
        required_frame,
        gif_quality_scale,
        lambda v: f"GIF Quality: {int(float(v))}",
    )
    Tooltip(gif_quality_value_label, message="Overall GIF Quality", delay=0.3)
    Tooltip(gif_quality_scale, message="Overall GIF Quality", delay=0.3)

    def update_checkbox_state(
        var,
        widget,
        other_var=None,
        other_widget=None,
        cmode=None,
        set_disabled_fn=None,  # new
    ):
        if cmode == "encode":
            if var.get() == 1:
                other_var.set(0)
                other_widget.configure(state="disabled")
            else:
                other_widget.configure(state="normal")
        elif cmode == "quality":
            if var.get() == 1:
                widget.configure(state="normal", **NORMAL_FG)
                if set_disabled_fn:
                    set_disabled_fn(False)
            else:
                widget.configure(state="disabled", **DISABLED_FG)
                if set_disabled_fn:
                    set_disabled_fn(True)
        elif cmode == "basic":
            if var.get() == 1:
                widget.configure(state="normal")
            else:
                widget.configure(state="disabled")
        elif cmode == "pack":
            if var.get() == 1:
                widget.pack(pady=5)
            else:
                widget.pack_forget()

    if len(valid_files) != 1:
        fps_limit = 30
    else:
        fps_limit = min(parsed_framerate, 50)

    fps = Slider(
        required_frame,
        from_=1,
        to=fps_limit,
        width=220,
        height=20,
        number_of_steps=fps_limit - 1,
    )
    fps.set(fps_limit)
    fps.pack(pady=(10, 0))
    fps_var, fps_value_label, _, fps_update = attach_slider_value_label(
        required_frame,
        fps,
        lambda v: f"FPS: {int(float(v))}",
    )

    def _current_source_dims():
        """Width/height of whichever file is on-screen right now — single file or current batch page."""
        if len(valid_files) == 1:
            return video_data["width"], video_data["height"]

        _, file_data = batch_video_data[current_video_index]
        return file_data["width"], file_data["height"]

    scale_widget = Slider(
        required_frame,
        from_=1,
        to=100,
        width=220,
        height=20,
        number_of_steps=198,
    )
    scale_widget = Slider(required_frame, from_=1, to=100, width=220, height=20, number_of_steps=198)
    scale_widget.set(100)
    scale_widget.pack(pady=(10, 0))
    scale_label_var = ctk.StringVar()

    def update_scale_label(value):
        global scaled_width, scaled_height
        width_value, height_value = _current_source_dims()
        if width_value and height_value:
            scaled_width = int(width_value * float(value) / 100)
            scaled_height = int((scaled_width / width_value) * height_value)
            scale_label_var.set(f"Scale: {value}%\n({scaled_width}x{scaled_height})")

    scale_widget.configure(command=lambda value: update_scale_label(value))
    update_scale_label(100)
    scale_label = Label(required_frame, textvariable=scale_label_var)
    scale_label.pack()

    if len(valid_files) != 1:
        scale_widget.pack_forget()
        scale_label.pack_forget()

    root.update_idletasks()

    # Export / Preview buttons — anchored to the bottom of the required column
    buttonsFrame = Frame(required_frame, fg_color="transparent", border_width=0)
    buttonsFrame.pack(pady=(20, 0), fill="x", side=ctk.BOTTOM)

    test_button = Button(
        buttonsFrame,
        text="",
        command=lambda: threading.Thread(target=preview_gif_window, daemon=True).start(),
    )
    apply_emoji(test_button, "▶️", text="Apply & Preview")

    test_button.pack(pady=5)

    settings_window.bind(
        "<space>",
        lambda event: threading.Thread(target=preview_gif_window, daemon=True).start(),
    )

    apply_button = Button(
        buttonsFrame,
        text="",
        command=lambda: threading.Thread(target=apply_settings, args=("final",), daemon=True).start(),
    )
    apply_emoji(apply_button, "📤", text=f"{export_label}")

    apply_button.pack(pady=5)

    save_current_button = Button(
        buttonsFrame,
        text="",
        command=lambda: threading.Thread(target=lambda: apply_settings("advanced-save"), daemon=True).start(),
    )
    apply_emoji(save_current_button, "💾", text="Save As...")
    save_current_button.configure(state="disabled")

    settings_window.bind(
        "<Control-s>",
        lambda event: threading.Thread(target=apply_settings, args=("final",), daemon=True).start(),
    )
    settings_window.bind(
        "<Command-s>",
        lambda event: threading.Thread(target=apply_settings, args=("final",), daemon=True).start(),
    )

    # =================================================================
    # RIGHT COLUMN — Optional settings
    # =================================================================
    optionalLabel = Label(optional_frame, text="Optional Settings", font=("", 15, "bold"))
    optionalLabel.pack(pady=(0, 5))

    sep_opt_top = ttk.Separator(optional_frame, orient="horizontal")
    sep_opt_top.pack(fill="x", pady=4)

    motion_var = ctk.IntVar()
    motion_quality_scale = Slider(
        optional_frame,
        from_=1,
        to=100,
        orientation=ctk.HORIZONTAL,
        number_of_steps=99,
        width=220,
        height=20,
    )
    motion_quality_scale.set(100)
    motion_quality_scale.pack(pady=(5, 0))
    motion_quality_scale.configure(state="disabled", **DISABLED_FG)
    motion_var_label_var, motion_value_label, motion_set_disabled, motion_update = attach_slider_value_label(
        optional_frame,
        motion_quality_scale,
        lambda v: f"Motion Quality: {int(float(v))}",
        disabled_text="Motion Quality: Disabled",
    )
    motion_quality_checkbutton = ctk.CTkCheckBox(
        optional_frame,
        text="Motion Quality",
        variable=motion_var,
        command=lambda: update_checkbox_state(
            motion_var, motion_quality_scale, cmode="quality", set_disabled_fn=motion_set_disabled
        ),
    )

    motion_set_disabled(True)

    motion_quality_checkbutton.pack(pady=5)
    Tooltip(
        motion_quality_checkbutton,
        message="Turn this on to fine-tune the Motion Quality (affects overall Quality.)",
        delay=0.3,
    )
    Tooltip(motion_quality_scale, message="Lower values reduce motion.", delay=0.3)

    lossy_var = ctk.IntVar()
    lossy_quality_scale = Slider(
        optional_frame,
        from_=1,
        to=100,
        orientation=ctk.HORIZONTAL,
        number_of_steps=99,
        width=220,
        height=20,
    )
    lossy_quality_scale.set(100)
    lossy_quality_scale.pack(pady=5)
    lossy_quality_scale.configure(state="disabled", **DISABLED_FG)
    lossy_var_label_var, lossy_value_label, lossy_set_disabled, lossy_update = attach_slider_value_label(
        optional_frame,
        lossy_quality_scale,
        lambda v: f"Lossy Quality: {int(float(v))}",
        disabled_text="Lossy Quality: Disabled",
    )
    lossy_set_disabled(True)

    lossy_quality_checkbutton = ctk.CTkCheckBox(
        optional_frame,
        text="Lossy Quality",
        variable=lossy_var,
        command=lambda: update_checkbox_state(
            lossy_var, lossy_quality_scale, cmode="quality", set_disabled_fn=lossy_set_disabled
        ),
    )

    lossy_quality_checkbutton.pack(pady=(2, 0))

    Tooltip(
        lossy_quality_scale,
        message="Turn this on to fine-tune the Lossy Quality (affects overall Quality.)",
        delay=0.3,
    )
    Tooltip(lossy_quality_checkbutton, message="Lower values introduce noise and streaks.", delay=0.3)

    sep_opt_mid = ttk.Separator(optional_frame, orient="horizontal")
    sep_opt_mid.pack(fill="x", pady=8)

    spacer = Label(optional_frame, text="Encode Quality", font=("", 15, "bold"))
    spacer.pack()

    checkboxFrame = Frame(optional_frame, fg_color="transparent", border_width=0)
    checkboxFrame.pack(pady=5, fill="x")

    extra_var = ctk.IntVar()
    extra_checkbox = ctk.CTkCheckBox(
        checkboxFrame,
        variable=extra_var,
        text="Extra Quality",
        command=lambda: update_checkbox_state(extra_var, extra_checkbox, fast_var, fast_checkbox, cmode="encode"),
    )
    extra_checkbox.pack(side=ctk.LEFT)
    Tooltip(extra_checkbox, message="Slower encoding, but 1% better quality.", delay=0.3)

    fast_var = ctk.IntVar()
    fast_checkbox = ctk.CTkCheckBox(
        checkboxFrame,
        variable=fast_var,
        text="Fast Quality",
        command=lambda: update_checkbox_state(fast_var, fast_checkbox, extra_var, extra_checkbox, cmode="encode"),
    )
    fast_checkbox.pack(side=ctk.RIGHT)
    Tooltip(fast_checkbox, message="Faster encoding, but 10% worse quality & larger file size.", delay=0.3)

    # unpremultiply / matte options
    alphaFrame = Frame(optional_frame, fg_color="transparent", border_width=0)
    sep_alpha = ttk.Separator(optional_frame, orient="horizontal")
    alphaLabel = Label(alphaFrame, text="Alpha Options", font=("", 15, "bold"))
    matteFrame = Frame(optional_frame, fg_color="transparent", border_width=1)
    matteSelectFrame = Frame(matteFrame, fg_color="transparent", border_width=0)

    safeAlpha = ctk.IntVar()
    unprenmult_checkbox = ctk.CTkCheckBox(alphaFrame, variable=safeAlpha, text="Unpremultiply")

    matte_var = None

    def pick_color():
        global matte_var
        color = colorchooser.askcolor()[1]
        if color:
            matte_var = color
            matte_box_preview.configure(fg_color=color)
            Tooltip(matte_box_preview, message=color, delay=0.3)

    enableMatte = ctk.IntVar()
    matte_checkbox = ctk.CTkCheckBox(
        matteFrame,
        text="Enable Matte",
        variable=enableMatte,
        command=lambda: update_checkbox_state(
            var=enableMatte,
            widget=matteSelectFrame,
            cmode="pack",
        ),
    )
    matte_button = Button(matteSelectFrame, text="", width=30, height=30, command=pick_color)
    apply_emoji(matte_button, "🎨")

    matte_box_preview = ctk.CTkLabel(
        matteSelectFrame,
        text="",
        width=30,
        height=20,
        fg_color="white",
        border_width=2,
        corner_radius=8,
    )

    if len(valid_files) != 1 or video_data["pix_fmt"] in alpha_formats:
        sep_alpha.pack(fill="x", pady=8)
        alphaFrame.pack(fill="x")
        alphaLabel.pack()
        unprenmult_checkbox.pack(pady=5)

        matteFrame.pack(fill="x", pady=5)
        matte_checkbox.pack(pady=5)

        matteSelectFrame.pack(pady=5)
        matteSelectFrame.pack_forget()

        matte_box_preview.pack(padx=5, pady=5, side=ctk.LEFT)

        matte_button.pack(padx=5, pady=5, side=ctk.RIGHT)

        Tooltip(
            unprenmult_checkbox,
            "It's like unmult but more precise.\nEnable this if your GIF has outlines.",
            delay=0.3,
        )
        Tooltip(matte_button, message="Click here to color-pick your desired matte.", delay=0.3)
        Tooltip(matte_checkbox, message="Enable this if you have semitransparent pixels.", delay=0.3)
        Tooltip(matte_box_preview, message="#FFFFFF", delay=0.3)

        root.update_idletasks()

    # =================================================================
    # Batch mode — hide what doesn't apply
    # (pack_forget() still works fine — these widgets are packed WITHIN
    # their column frame, the outer grid columns are untouched)
    # =================================================================

    # Pagination Functions
    def _capture_page_settings():
        return {
            "fps": fps.get(),
            "scale": scale_widget.get(),
            "gif_quality": gif_quality_scale.get(),
            "motion_enabled": motion_var.get(),
            "motion_quality": motion_quality_scale.get(),
            "lossy_enabled": lossy_var.get(),
            "lossy_quality": lossy_quality_scale.get(),
            "extra": extra_var.get(),
            "fast": fast_var.get(),
            "unpremultiply": safeAlpha.get(),
            "matte_enabled": enableMatte.get(),
            "matte_color": matte_var,
        }

    def _apply_page_settings(settings):
        global matte_var
        fps.set(settings["fps"])
        fps_update(settings["fps"])
        scale_widget.set(settings["scale"])
        update_scale_label(settings["scale"])
        gif_quality_scale.set(settings["gif_quality"])
        gif_quality_update(settings["gif_quality"])

        motion_var.set(settings["motion_enabled"])
        motion_quality_scale.set(settings["motion_quality"])
        update_checkbox_state(motion_var, motion_quality_scale, cmode="quality", set_disabled_fn=motion_set_disabled)

        lossy_var.set(settings["lossy_enabled"])
        lossy_quality_scale.set(settings["lossy_quality"])
        update_checkbox_state(lossy_var, lossy_quality_scale, cmode="quality", set_disabled_fn=lossy_set_disabled)

        extra_var.set(settings["extra"])
        fast_var.set(settings["fast"])
        safeAlpha.set(settings["unpremultiply"])
        enableMatte.set(settings["matte_enabled"])
        matte_var = settings["matte_color"]
        if matte_var:
            matte_box_preview.configure(fg_color=matte_var)
        update_checkbox_state(enableMatte, matte_button, cmode="basic")

    def _update_alpha_visibility(index):
        _, file_data = batch_video_data[index]
        needs_alpha = file_data["pix_fmt"] in alpha_formats

        if needs_alpha:
            sep_alpha.pack(fill="x", pady=8)
            alphaFrame.pack(fill="x")
            matteFrame.pack(fill="x")
        else:
            sep_alpha.pack_forget()
            alphaFrame.pack_forget()
            matteFrame.pack_forget()

    def _apply_current_page():
        if not advanced_mode:
            return
        filename = valid_files[current_video_index][0]
        per_video_settings[filename] = _capture_page_settings()
        page_preview_cache.pop(filename, None)  # stale — settings changed, old render no longer matches

        stop_gif_animation(preview_label)

        preview_label.configure(text="", image="")
        if mac:
            apply_emoji(preview_label, "✅", text="Settings applied.\nClick Load Preview to see it.")
        if win:
            preview_label.configure(text="Settings applied.\nClick Load Preview to see it.", image="")

        play_gif_button.configure(state="normal", text="", command=_load_preview_current_page)
        apply_emoji(play_gif_button, "▶️", text="Load Preview")
        save_current_button.configure(state="normal")
        fileSize_label.configure(text="")
        fileDimension_label.configure(text="")
        print(f"Applied settings for '{filename}'")

    def _load_preview_current_page():
        threading.Thread(target=preview_gif_window, daemon=True).start()

    def _save_as_current_page():
        def _do_save():
            filename = valid_files[current_video_index][0]
            current_settings = _capture_page_settings()
            if per_video_settings.get(filename) != current_settings:
                per_video_settings[filename] = current_settings
                page_preview_cache.pop(filename, None)

            if filename not in page_preview_cache:
                preview_gif_window()  # no render exists yet for these settings — do it now, like Quick Export

            apply_settings("advanced-save")

        threading.Thread(target=_do_save, daemon=True).start()

    def _export_all():
        def _do_export():
            if advanced_mode and valid_files:
                filename = valid_files[current_video_index][0]
                current_settings = _capture_page_settings()
                if per_video_settings.get(filename) != current_settings:
                    per_video_settings[filename] = current_settings
                    page_preview_cache.pop(filename, None)
            apply_settings("final")

        threading.Thread(target=_do_export, daemon=True).start()

    def _load_page(index):
        global current_video_index
        stop_gif_animation(preview_label)
        current_video_index = index
        filename, _ = valid_files[index]

        _, file_data = batch_video_data[index]
        try:
            native_fps = min(int(round(eval(file_data["r_frame_rate"]))), 50)
        except Exception:
            native_fps = 30

        fps.configure(to=native_fps, number_of_steps=native_fps)

        settings = per_video_settings.setdefault(filename, _default_video_settings(native_fps))
        _apply_page_settings(settings)
        _update_alpha_visibility(index)

        max_length = 45
        filename_text = filename
        if len(filename) > max_length:
            part_len = (max_length - 3) // 2
            filename_text = filename[:part_len] + "..." + filename[-part_len:]

        page_label.configure(text=f"{filename_text}  ({index + 1}/{len(valid_files)})")

        cached = page_preview_cache.get(filename)
        if cached:
            preview_label.configure(text="")
            fileSize_label.configure(text=cached["filesize_text"])
            fileDimension_label.configure(text=cached["dimensions_text"])
            play_gif_button.configure(state="normal", text="", command=lambda p=cached["gif_path"]: play_gif(p))
            apply_emoji(play_gif_button, "▶️", text="Play GIF on Full Size")
            start_gif_animation(preview_label, loop=True, fps=cached["fps"], frames=cached["frames"])
        else:
            preview_label.configure(text="Click Load Preview to see it.", image="")
            play_gif_button.configure(state="normal", text="", command=_load_preview_current_page)
            apply_emoji(play_gif_button, "▶️", text="Load Preview")
            fileSize_label.configure(text="")
            fileDimension_label.configure(text="")

    def _navigate(delta):
        if not advanced_mode or len(valid_files) <= 1:
            return
        _load_page((current_video_index + delta) % len(valid_files))

    if len(valid_files) != 1:
        settings_window.unbind("<space>")
        separator1.pack_forget()
        fileSize_label.pack_forget()
        fileDimension_label.pack_forget()
        playframe.pack_forget()
        play_gif_button.pack_forget()
        test_button.pack_forget()
        apply_button.pack_forget()
        apply_button.pack(side=ctk.TOP, pady=(20, 0))

        def _toggle_advanced():
            global advanced_mode
            advanced_mode = not advanced_mode
            if advanced_mode:
                uniform_settings = _capture_page_settings()
                for fname, _ in valid_files:
                    if fname not in per_video_settings:
                        file_data = next((d for f, d in batch_video_data if f == fname), None)
                        try:
                            native_fps = min(int(round(eval(file_data["r_frame_rate"]))), 50) if file_data else 30
                        except Exception:
                            native_fps = 30
                        seeded = dict(uniform_settings)
                        seeded["fps"] = native_fps
                        per_video_settings[fname] = seeded

                page_label.pack(pady=(2, 0))
                prev_chevron.place(relx=0.0, rely=0.5, anchor="w")
                next_chevron.place(relx=1.0, rely=0.5, anchor="e")

                fileSize_label.pack(pady=2, side=ctk.BOTTOM)
                fileDimension_label.pack(pady=2, side=ctk.BOTTOM)
                scale_widget.pack(pady=(10, 0))
                scale_label.pack()

                playframe.pack(pady=(10, 0))
                play_gif_button.pack(pady=3)

                advanced_button.pack_forget()
                advanced_button.pack(pady=(30, 0))
                advanced_button.configure(text="")
                apply_emoji(advanced_button, "🚀", text="Uniform Settings")

                apply_emoji(test_button, "✅", text="Apply")
                test_button.configure(command=_apply_current_page)
                apply_button.configure(command=_export_all)

                test_button.pack_forget()
                save_current_button.pack_forget()
                apply_button.pack_forget()
                test_button.pack(pady=5)
                save_current_button.pack(pady=5)
                apply_button.pack(pady=5)
                save_current_button.configure(state="normal")

                _load_page(0)

                settings_window.bind("<Left>", lambda e: _navigate(-1))
                settings_window.bind("<Right>", lambda e: _navigate(1))
                settings_window.bind("<space>", lambda e: _load_preview_current_page())

                if win:
                    settings_window.bind("<Control-s>", lambda e: _apply_current_page())
                    settings_window.bind("<Control-S>", lambda e: _save_as_current_page())
                    settings_window.bind("<Alt-s>", lambda e: _export_all())
                elif mac:
                    settings_window.bind("<Command-s>", lambda e: _apply_current_page())
                    settings_window.bind("<Command-S>", lambda e: _save_as_current_page())
                    settings_window.bind("<Control-s>", lambda e: _export_all())
            else:
                preview_label.configure(
                    text="Multiple videos detected!\nAdjust the settings to apply\n"
                    "the same configuration to all GIFs converted!"
                )
                page_label.pack_forget()
                prev_chevron.place_forget()
                next_chevron.place_forget()

                advanced_button.pack_forget()
                advanced_button.pack(pady=(15, 0))
                advanced_button.configure(text="")
                apply_emoji(advanced_button, "⚙️", text="Advanced Settings")

                fileSize_label.pack_forget()
                fileDimension_label.pack_forget()
                scale_widget.pack_forget()
                scale_label.pack_forget()

                stop_gif_animation(preview_label)
                preview_label.configure(text=preview_label_text, image="")
                playframe.pack_forget()
                play_gif_button.configure(state="disabled", text="No GIF loaded")

                test_button.pack_forget()
                save_current_button.pack_forget()
                apply_button.pack_forget()
                apply_button.pack(side=ctk.TOP, pady=(20, 0))
                apply_button.configure(
                    command=lambda: threading.Thread(target=apply_settings, args=("final",), daemon=True).start()
                )

                new_fps_value = min(fps.get(), 30)
                fps.configure(to=30, number_of_steps=30)
                fps.set(new_fps_value)
                fps_update(new_fps_value)

                settings_window.unbind("<Left>")
                settings_window.unbind("<Right>")
                settings_window.unbind("<space>")
                if win:
                    settings_window.unbind("<Control-s>")
                    settings_window.unbind("<Control-S>")
                    settings_window.unbind("<Alt-s>")
                elif mac:
                    settings_window.unbind("<Command-s>")
                    settings_window.unbind("<Command-S>")
                    settings_window.unbind("<Control-s>")

                settings_window.bind(
                    "<Control-s>",
                    lambda event: threading.Thread(target=apply_settings, args=("final",), daemon=True).start(),
                )
                settings_window.bind(
                    "<Command-s>",
                    lambda event: threading.Thread(target=apply_settings, args=("final",), daemon=True).start(),
                )

        advanced_button = Button(required_frame, text="", command=_toggle_advanced)
        advanced_button.pack(pady=(15, 0))
        apply_emoji(advanced_button, "⚙️", text="Advanced Settings")

        root.update_idletasks()

    def preview_gif_window():
        global _last_frame_extraction_key
        current_file = valid_files[current_video_index][1]
        loading_thread_switch(root, True, os.path.basename(current_file))

        stop_gif_animation(preview_label)

        current_key = _extraction_key()
        frames_exist = bool(glob.glob(os.path.join(temp_dir, "frames*.png")))

        if current_key != _last_frame_extraction_key or not frames_exist:
            video_to_frames_seq(current_file, fps.get(), apply_scale=(scale_widget.get() != 100))
            _last_frame_extraction_key = current_key
        else:
            print("Skipping ffmpeg re-extraction — FPS/Scale/Unpremultiply unchanged.")

        apply_settings("temp")

        playframe.pack(fill="x")

        play_gif_button.pack(pady=5, side=ctk.BOTTOM, expand=True)
        play_gif_button.configure(state="normal", text="")
        apply_emoji(play_gif_button, "▶️", text="Play GIF on Full Size")

        img = Image.open(output_file)
        imgW, imgH = img.size
        gcd = math.gcd(imgW, imgH)
        aspect_ratio_simplified = f"{imgW // gcd}:{imgH // gcd}"

        preview_label.configure(text="")

        frames = load_gifpreview_frames()
        start_gif_animation(preview_label, loop=True, fps=fps.get(), frames=frames)

        filesize = get_filesize(temp_gif)
        fileSize_text = f"GIF Size: {filesize}"
        fileDimension_text = f"Dimensions: {imgW}x{imgH} ({aspect_ratio_simplified})"
        fileSize_label.configure(text=fileSize_text)
        fileDimension_label.configure(text=fileDimension_text)

        if len(valid_files) == 1:
            global _last_rendered_settings
            _last_rendered_settings = _capture_page_settings()
            apply_button.configure(text="", command=lambda: threading.Thread(target=_save_as_solo, daemon=True).start())
            apply_emoji(apply_button, "💾", text="Save As...")
        else:
            save_current_button.configure(state="normal")

            filename = valid_files[current_video_index][0]
            per_video_settings[filename] = _capture_page_settings()

            cached_gif_path = os.path.join(page_cache_dir, f"{os.path.splitext(filename)[0]}.gif")
            os.makedirs(page_cache_dir, exist_ok=True)
            shutil.copy2(temp_gif, cached_gif_path)

            page_preview_cache[filename] = {
                "frames": frames,
                "fps": fps.get(),
                "filesize_text": fileSize_text,
                "dimensions_text": fileDimension_text,
                "gif_path": cached_gif_path,
            }

            play_gif_button.configure(command=lambda p=cached_gif_path: play_gif(p))

        settings_window.update_idletasks()

    def _save_as_solo():
        current_settings = _capture_page_settings()
        if current_settings != _last_rendered_settings:
            preview_gif_window()
        apply_settings("temp-final")

    def _resync_slider_visuals():
        gif_quality_scale.set(gif_quality_scale.get())
        fps.set(fps.get())
        scale_widget.set(scale_widget.get())
        motion_quality_scale.set(motion_quality_scale.get())
        lossy_quality_scale.set(lossy_quality_scale.get())

    settings_window.update_idletasks()
    _resync_slider_visuals()
    settings_window.update_idletasks()
    settings_window.deiconify()

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

animate(0, loop_switch)


# Create the main window
def show_main():
    def on_drop(event):
        global file_path
        print(f"File Path PASS I: {event.data}")
        file_path = re.findall(r"\{.*?\}|\S+", event.data)
        print(f"File Path PASS II: {file_path}")
        file_path = [re.sub(r"[{}]", "", file) for file in file_path]
        print(f"File Path PASS III: {file_path}")

        if win:
            threading.Thread(
                target=get_and_print_video_data,
                args=(file_path,),
            ).start()
        elif mac:
            get_and_print_video_data(file_path)

    geo_width = 425
    center_window(root, geo_width, 450)
    make_non_resizable(root)
    watermark_label(root)

    def _toggle_appearance():
        new_mode = "Light" if ctk.get_appearance_mode() == "Dark" else "Dark"

        def _swap_and_reveal():
            ctk.set_appearance_mode(new_mode)
            set_setting("appearance_mode", new_mode)
            theme_toggle_btn.configure(text="")
            apply_emoji(
                theme_toggle_btn,
                emoji_char="☀️" if new_mode == "Dark" else "🌑",
                px=15,
            )
            root.update_idletasks()
            animate_alpha(root, 1.0, duration_ms=250)

        animate_alpha(root, 0.0, duration_ms=150, on_complete=_swap_and_reveal)

    theme_toggle_btn = ctk.CTkButton(
        root,
        text="",
        width=32,
        height=32,
        corner_radius=6,
        font=("", 15),
        command=_toggle_appearance,
    )

    apply_emoji(
        theme_toggle_btn,
        emoji_char="☀️" if ctk.get_appearance_mode() == "Dark" else "🌑",
        px=15,
    )
    theme_toggle_btn.place(relx=1.0, x=-14, y=14, anchor="ne")

    spacer = Label(root, text="")
    spacer.pack(pady=10)

    # Create a button to choose a file
    choose_button = Button(root, text="Choose Video File/s", command=choose_file)
    choose_button.pack(pady=20)

    or_label = Label(root, text="Or")
    or_label.pack(pady=20)

    # Create a Canvas
    canvas = Frame(root, fg_color="transparent", border_width=0)
    canvas.pack(expand=True, fill="both")

    # Create a Label for the drop area
    drop_label = Label(canvas, text="Drag and Drop Video Files Here")
    drop_label.pack(pady=60)

    # Bind the drop event to the on_drop function
    def reg_dnd(widget):
        widget.drop_target_register(DND_FILES)
        widget.dnd_bind("<<Drop>>", on_drop)

    reg_dnd(drop_label)
    reg_dnd(canvas)
    reg_dnd(or_label)
    reg_dnd(root)

    print("Current working directory:", os.getcwd())
    print("Executable path:", sys.executable)

    # logo on drop event area
    platform = "MacOS" if mac else "Windows"
    DnDLogo = "icon-dev.png" if any(char.isalpha() for char in __version__) else "icon.png"
    if bundle_path:
        DnDLogo = os.path.join(bundle_path, "assets", "icons", platform, DnDLogo)
    else:
        DnDLogo = f"./buildandsign/icons/{platform}/{DnDLogo}"
    imgYPos = 225

    img_to_pil = Image.open(DnDLogo)
    image = ctk.CTkImage(
        light_image=img_to_pil,
        dark_image=img_to_pil,
        size=(150, 150) if win else (250, 250),
    )
    label = ctk.CTkLabel(canvas, text="", image=image)
    label.image = image
    label.place(x=geo_width / 2, y=imgYPos, anchor=ctk.CENTER)

    root.update_idletasks()
    splash_screen.destroy()
    root.deiconify()

    autoChecker(root)


def on_closing():
    remove_temp(temp_dir)
    remove_temp(page_cache_dir)
    print("Closing the application.")

    atexit.unregister(on_closing)  # Unregister the atexit callback
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)
atexit.register(on_closing)

splash_screen.after(3500, show_main)

root.mainloop()
