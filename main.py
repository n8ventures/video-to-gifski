from __version__ import __version__
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
import subprocess
import os
import json
import shutil
import sys

print("Current version:", __version__)

video_data = None

icon = 'ico.ico'
ffprobe = 'ffprobe.exe'
gifski = 'gifski.exe'
ffmpeg = 'ffmpeg.exe'
if hasattr(sys, '_MEIPASS'):
    icon = os.path.join(sys._MEIPASS, icon)
    ffprobe = os.path.join(sys._MEIPASS, ffprobe)
    gifski = os.path.join(sys._MEIPASS, gifski)
    ffmpeg = os.path.join(sys._MEIPASS, ffmpeg)

def convert_and_save(fps, gif_quality, input_file):
    output_file = filedialog.asksaveasfile(
        defaultextension=".gif",
    initialfile=os.path.splitext(os.path.basename(input_file))[0] + ".gif",
    filetypes=[("GIF files", "*.gif")]
    )
    framerate = fps.get()
    gifQ = gif_quality.get()
    if output_file:
        video_to_frames_seq(input_file)
        vid_to_gif(framerate, gifQ, output_file)
        print("Conversion complete!")
        shutil.rmtree('temp')
        settings_window.destroy()
        # open_finish_window()

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

def video_to_frames_seq(input_file):
    os.makedirs('temp', exist_ok=True)
    cmd = [ 
       ffmpeg, 
        "-i", input_file
        ]
    
    if scale_widget.get() != 100:
        cmd.extend([
            "-vf", f"scale={scaled_width}:{scaled_height},setsar=1" 
        ])
        
    cmd.append("temp/frames%04d.png")
    
    subprocess.run(cmd)

def vid_to_gif(framerate, gifQuality, output):
    cmd = [
        gifski,
        "-r", str(framerate),
        "-Q", str(gifQuality),
        ]

    if extra_var.get():
        cmd.append("--extra")
    if fast_var.get():
        cmd.append("--fast")

    cmd.extend(["-o", output.name, "temp/frames*.png"])

    subprocess.run(cmd)
    
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
            
            open_settings_window()

def choose_file():
    global file_path
    file_path = filedialog.askopenfilename()
    get_and_print_video_data(file_path)

def open_finish_window():
    global finish_window
    finish_window = tk.Toplevel(root)
    finish_window.title("Done!")
    finish_window.geometry("300x300")
    finish_window.iconbitmap(icon)
    
    watermark_label = tk.Label(finish_window, text="by N8VENTURES (github.com/n8ventures)", fg="gray")
    watermark_label.pack(side=tk.BOTTOM, anchor=tk.SW, padx=10, pady=10)

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

def open_settings_window(): 
    global fps, gif_quality_scale, scale_widget, extra_var, fast_var, settings_window
    settings_window = tk.Toplevel(root)
    settings_window.title("User Settings")
    settings_window.geometry("350x400")
    settings_window.iconbitmap(icon)
    watermark_label = tk.Label(settings_window, text="by N8VENTURES (github.com/n8ventures)", fg="gray")
    watermark_label.pack(side=tk.BOTTOM, anchor=tk.SW, padx=10, pady=10)

    gif_quality_label = tk.Label(settings_window, text="GIF Quality:")
    gif_quality_label.pack(pady=10)
    gif_quality_scale = tk.Scale(settings_window, from_=100, to=1, orient=tk.HORIZONTAL, resolution=1, length=300)
    gif_quality_scale.set(90)
    gif_quality_scale.pack()

    fps_label = tk.Label(settings_window, text="Frames Per Second:")
    fps_label.pack()
    fps = tk.Scale(settings_window, from_=30, to=1, orient=tk.HORIZONTAL, resolution=1, length=300)
    fps.set(30)
    fps.pack()

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
    
    spacer = tk.Label(settings_window, text="")
    spacer.pack(pady=10)

    def update_checkbox_state(var, checkbox, other_var, other_checkbox):
        if var.get() == 1:
            other_var.set(0)
            other_checkbox['state'] = 'disabled'
        else:
            other_checkbox['state'] = 'normal'

    extra_var = tk.IntVar()
    extra_checkbox = tk.Checkbutton(settings_window, text="Extra", variable=extra_var, command=lambda: update_checkbox_state(extra_var, extra_checkbox, fast_var, fast_checkbox))
    extra_checkbox.pack()

    fast_var = tk.IntVar()
    fast_checkbox = tk.Checkbutton(settings_window, text="Fast", variable=fast_var, command=lambda: update_checkbox_state(fast_var, fast_checkbox, extra_var, extra_checkbox))
    fast_checkbox.pack()

    apply_button = tk.Button(settings_window, text="Convert!", command=lambda: apply_settings())
    apply_button.pack(pady=10)
    
    root.withdraw()
    settings_window.grab_set()
    settings_window.wait_window(settings_window)
    root.deiconify()



def apply_settings():
    global fps, gif_quality_scale, scale_widget, extra_var, fast_var
    fps_value = fps.get()
    scale_value = scale_widget.get()
    extra_value = extra_var.get()
    fast_value = fast_var.get()
    gif_quality_value = gif_quality_scale.get()
    width_value = video_data['width']
    height_value = video_data['height']

    if width_value and height_value:
        # Calculate the scaled width based on the slider value
        scaled_width = int(width_value * scale_value / 100)

        # Maintain the aspect ratio
        scaled_height = int((scaled_width / width_value) * height_value)

    print(f"Settings applied - FPS: {fps_value}, Scale: {scaled_width} x {scaled_height}")
    print("GIF Quality:", gif_quality_value)
    print("Extra:", extra_value)
    print("Fast:", fast_value)
    
    convert_and_save(fps, gif_quality_scale, file_path)
    
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
root.geometry("350x400")
root.iconbitmap(icon)

# Create a button to choose a file
choose_button = tk.Button(root, text="Choose Video File", command=choose_file)
choose_button.pack(pady=20)

or_label = tk.Label(root, text="Or")
or_label.pack(pady=20)

# Create a Canvas with a grey broken-line border
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

print("Current working directory:", os.getcwd())
print("Executable path:", sys.executable)

image_path = 'ico.png' 
if hasattr(sys, '_MEIPASS'):
    image_path = os.path.join(sys._MEIPASS, image_path)
else:
    image_path = '.\\buildandsign\\ico\\ico.png' 

image = tk.PhotoImage(file=image_path)
label = tk.Label(canvas, image=image, bd=0, bg="white")
label.image = image
label.place(x=175, y=200, anchor=tk.CENTER) 

watermark_label = tk.Label(root, text="by N8VENTURES (github.com/n8ventures)", fg="gray")
watermark_label.pack(side=tk.BOTTOM, anchor=tk.SW, padx=10, pady=10)

root.mainloop()