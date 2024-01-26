from __version__ import __version__
import tkinter as tk
from tkinter import filedialog, ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageTk, ImageSequence
import subprocess
import os
import json
import shutil
import sys
import tempfile
import atexit

print("Current version:", __version__)

video_data = None
global mode

# for windows executables, basically makes this readable inside an exe
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

def watermark_label(parent_window):
    watermark_label = tk.Label(parent_window, text="by N8VENTURES (github.com/n8ventures)", fg="gray")
    watermark_label.pack(side=tk.BOTTOM, anchor=tk.SW, padx=10, pady=10)
    
    separator_wm = ttk.Separator(parent_window, orient="horizontal")
    separator_wm.pack(side=tk.BOTTOM,fill="x", padx=10, pady=10)

def make_non_resizable(window):
    window.resizable(False, False)

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = width  
    window_height = height
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2  
    window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

def get_filesize(file_path):
    size_bytes = os.path.getsize(file_path)
    size_mb = round(size_bytes / (1024 * 1024), 2)
    return f'{size_mb} MB'

# # Example usage:
# file_path = "path/to/your/file.txt"
# file_size = get_filesize(file_path)
# print(f"The size of the file is: {file_size}")

def get_video_data(input_file):
    cmd = [
        ffprobe,
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,duration",
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

def video_to_frames_seq(input_file, framerate):
    temp_folder = 'temp'
    
    if os.path.exists(temp_folder) and os.listdir(temp_folder):
        shutil.rmtree(temp_folder)
        
    os.makedirs(temp_folder, exist_ok=True)

    cmd = [
        'ffmpeg',
        '-i', input_file,
        "-vf", f"fps={str(framerate)}",
    ]

    if scale_widget.get() != 100:
        cmd.extend([
            f'scale={scaled_width}:{scaled_height},setsar=1'
        ])

    cmd.append(os.path.join(temp_folder, 'frames%04d.png'))

    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def vid_to_gif(fps, gifQuality, motionQuality, lossyQuality, output):

    if hasattr(output, 'name'):
        output_file = output.name
    elif isinstance(output, str):
        output_file = output

    cmd = [
        gifski,
        "-r", str(fps),
        "-Q", str(gifQuality),
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

    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
def get_and_print_video_data(file_path):
    global video_data
    print(f"File dropped: {file_path}")
    
    if file_path:
        video_data = get_video_data(file_path)
        if video_data:
            width_value = video_data['width']
            height_value = video_data['height']
            fps_value = round(eval(video_data['r_frame_rate']), 3)
            duration_value = video_data['duration']
            print("Video width:", width_value)
            print("Video height:", height_value)
            print("Frame rate:", fps_value)
            print("Duration:", duration_value)
        
            if not settings_window_open:
                open_settings_window()

def convert_and_save(fps, gif_quality, motion_quality, lossy_quality, input_file, mode):
    global output_file
    framerate = fps.get()
    gifQ = gif_quality.get()
    motionQ= motion_quality.get()
    lossyQ = lossy_quality.get()
    
    if mode == 'final':
        output_file = filedialog.asksaveasfile(
            defaultextension=".gif",
        initialfile=os.path.splitext(os.path.basename(input_file))[0] + ".gif",
        filetypes=[("GIF files", "*.gif")]
        )
        if output_file:
            output_folder = os.path.abspath(output_file.name)
            print (output_folder)
            
            video_to_frames_seq(input_file, framerate)
            vid_to_gif(framerate, gifQ, motionQ, lossyQ, output_file)
            print("Conversion complete!")
            shutil.rmtree('temp')
            on_settings_window_close()
            subprocess.run(fr'explorer /select,"{output_folder}"')
            # open_finish_window()
            
    elif mode == 'temp':
        # with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as temp_file:
        #     output_file = temp_file.name
            output_file = 'temp.gif'
            print(tempfile)
            print(output_file)
            
            vid_to_gif(framerate, gifQ, motionQ, lossyQ, output_file)
            print("Conversion complete!")
    elif mode == 'temp-final':
        output_file = filedialog.asksaveasfile(
        defaultextension=".gif",
        initialfile=os.path.splitext(os.path.basename(input_file))[0] + ".gif",
        filetypes=[("GIF files", "*.gif")]
        )
        
        if output_file:
            output_folder = os.path.abspath(output_file.name)
            
            shutil.copy('temp.gif', output_file.name)
            print("Conversion complete!")
            shutil.rmtree('temp')
            on_settings_window_close()
            subprocess.run(fr'explorer /select,"{output_folder}"')


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
    motion_quality_scale = tk.Scale(settings_window, from_=100, to=1, orient=tk.HORIZONTAL, resolution=1, length=300, sliderrelief='flat')
    motion_quality_scale.set(100)
    motion_quality_scale.pack()
    motion_quality_scale['state'] = 'disabled'
    # separator3 = ttk.Separator(settings_window, orient="horizontal")
    # separator3.pack(fill="x", padx=20, pady=2)
    lossy_var = tk.IntVar()
    lossy_quality_label = tk.Checkbutton(settings_window, text="Lossy Quality:", variable=lossy_var, command=lambda: update_checkbox_state(lossy_var, lossy_quality_scale, cmode = 'quality'))
    lossy_quality_label.pack()
    lossy_quality_scale = tk.Scale(settings_window, from_=100, to=1, orient=tk.HORIZONTAL, resolution=1, length=300, sliderrelief='flat')
    lossy_quality_scale.set(100)
    lossy_quality_scale.pack()
    lossy_quality_scale['state'] = 'disabled'
    # separator4 = ttk.Separator(settings_window, orient="horizontal")
    # separator4.pack(fill="x", padx=20, pady=2)

    fps_label = tk.Label(settings_window, text="Frames Per Second:")
    fps_label.pack()
    fps = tk.Scale(settings_window, label='test', from_=30, to=1, orient=tk.HORIZONTAL, resolution=3, length=300)
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
    extra_checkbox = tk.Checkbutton(settings_window, text="Extra - maximizes quality export but slower encoding.", variable=extra_var, command=lambda: update_checkbox_state(extra_var, extra_checkbox, fast_var, fast_checkbox,  cmode = 'encode'))
    extra_checkbox.pack()

    fast_var = tk.IntVar()
    fast_checkbox = tk.Checkbutton(settings_window, text="Fast - does faster enocding but quality is poorer.", variable=fast_var, command=lambda: update_checkbox_state(fast_var, fast_checkbox, extra_var, extra_checkbox,  cmode = 'encode'))
    fast_checkbox.pack()

    apply_button = tk.Button(settings_window, text="Convert!",width=10, command=lambda: apply_settings(mode='final'))
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
        
        target_width = 450
        img = Image.open(output_file)
        aspect_ratio = img.width / img.height
        target_height = int(target_width / aspect_ratio)
        
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
        "-loop", "0",
        file_path
    ]

        result = subprocess.run(cmd)


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
root.title(f"Video to GIF Converter {__version__}")
center_window(root, 350, 450)
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
image_path = 'ico.png' 
if hasattr(sys, '_MEIPASS'):
    image_path = os.path.join(sys._MEIPASS, image_path)
else:
    image_path = '.\\buildandsign\\ico\\ico.png' 

image = tk.PhotoImage(file=image_path)
label = tk.Label(canvas, image=image, bd=0, bg="white")
label.image = image
label.place(x=175, y=200, anchor=tk.CENTER) 

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