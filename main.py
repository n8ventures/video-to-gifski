from __version__ import __version__
import tkinter as tk
from tkinter import filedialog
import subprocess
import os
import json
import shutil

# def convert_to_gif(input_file, output_file, fps, scale):
#     cmd = [
#         "ffmpeg",
#         "-i", input_file,
#         "-vf", f"fps={fps},scale={scale}:-1:flags=lanczos",
#         "-c:v", "gif",
#         output_file
#     ]
#     subprocess.run(cmd)
print("Current version:", __version__)

video_data = None

def convert_and_save(fps, gif_quality, input_file):
    output_file = filedialog.asksaveasfile(
        defaultextension=".gif",
    initialfile=os.path.splitext(os.path.basename(input_file))[0] + ".gif",
    filetypes=[("GIF files", "*.gif")]
    )
    framerate = fps.get()
    gifQ = gif_quality.get()
    video_to_frames_seq(input_file)
    vid_to_gif(framerate, gifQ, output_file)
    print("Conversion complete!")
    shutil.rmtree('temp')
    
def get_video_data(input_file):
    cmd = [
        "ffprobe",
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
        "ffmpeg", 
        "-i", input_file,
        "temp/frames%04d.png",
        ]
    subprocess.run(cmd)

def vid_to_gif(framerate, gifQuality, output):
    cmd = [
        "gifski",
        "-r", str(framerate),
        "-Q", str(gifQuality),
        ]

    if extra_var.get():
        cmd.append("--extra")
    if fast_var.get():
        cmd.append("--fast")

    cmd.extend(["-o", output.name, "temp/frames*.png"])

    subprocess.run(cmd)

def choose_file():
    global video_data
    global file_path
    file_path = filedialog.askopenfilename()
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

def open_settings_window():
    global fps, gif_quality_scale, scale_widget, extra_var, fast_var
    settings_window = tk.Toplevel(root)
    settings_window.title("User Settings")

    gif_quality_label = tk.Label(settings_window, text="GIF Quality:")
    gif_quality_label.pack()
    gif_quality_scale = tk.Scale(settings_window, from_=100, to=1, orient=tk.HORIZONTAL)
    gif_quality_scale.pack()

    fps_label = tk.Label(settings_window, text="Frames Per Second:")
    fps_label.pack()
    fps = tk.Scale(settings_window, from_=30, to=1, orient=tk.HORIZONTAL)
    fps.pack()

    scale_label = tk.Label(settings_window, text="Scale:")
    scale_label.pack()
    scale_widget = tk.Scale(settings_window, from_=50, to=200, orient=tk.HORIZONTAL)
    scale_widget.pack()

    scale_entry = tk.Entry(settings_window)
    scale_entry.pack()

    extra_var = tk.IntVar()
    extra_checkbox = tk.Checkbutton(settings_window, text="Extra", variable=extra_var)
    extra_checkbox.pack()

    fast_var = tk.IntVar()
    fast_checkbox = tk.Checkbutton(settings_window, text="Fast", variable=fast_var)
    fast_checkbox.pack()

    apply_button = tk.Button(settings_window, text="Apply", command=lambda: apply_settings())
    apply_button.pack(pady=10)

    def on_scale_change(_):
        scale_value = scale_widget.get()
        scale_entry.delete(0, tk.END)
        scale_entry.insert(0, str(scale_value))

    scale_widget.bind("<B1-Motion>", on_scale_change)
    
def apply_settings():
    global fps, gif_quality_scale, scale_widget, extra_var, fast_var
    fps_value = fps.get()
    scale_value = 100
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
    

# def open_save_window():
#     save_window = tk.Toplevel(root)
#     save_window.title("Save Output")

#     # Create an entry widget to get the output file path
#     output_entry = tk.Entry(save_window)
#     output_entry.pack(pady=10)

#     # Create a "Save" button to initiate the conversion and save the output file
#     save_button = tk.Button(save_window, text="Save", command=lambda: convert_and_save(output_entry.get()))
#     save_button.pack(pady=10)

# Create the main window
root = tk.Tk()
root.title(f"Video to GIF Converter {__version__}")
root.geometry("350x200")

# Create a button to choose a file
choose_button = tk.Button(root, text="Choose Video File", command=choose_file)
choose_button.pack(pady=30)

# Create a button to open the user settings window
settings_button = tk.Button(root, text="Open Settings", command=open_settings_window)
settings_button.pack(pady=10)

watermark_label = tk.Label(root, text="by N8VENTURES (github.com/n8ventures)", fg="gray")
watermark_label.pack(side=tk.BOTTOM, anchor=tk.SW, padx=10, pady=10)
# Create a button to open the save window
# save_button = tk.Button(root, text="Save Output", command=open_save_window)
# save_button.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()