import tkinter as tk
from tkinter import filedialog
import subprocess
import os
import json

# def convert_to_gif(input_file, output_file, fps, scale):
#     cmd = [
#         "ffmpeg",
#         "-i", input_file,
#         "-vf", f"fps={fps},scale={scale}:-1:flags=lanczos",
#         "-c:v", "gif",
#         output_file
#     ]
#     subprocess.run(cmd)

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

def video_to_frames_seq():
    cmd = [ 
        "gifski"
        ]
    subprocess.run(cmd)

def choose_file():
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

# Create the main window
root = tk.Tk()
root.title("Video to GIF Converter")

# Create a button to choose a file
choose_button = tk.Button(root, text="Choose Video File", command=choose_file)
choose_button.pack(pady=30)

# Create a slider for FPS
fps_label = tk.Label(root, text="Frames Per Second:")
fps_label.pack()
fps = tk.Scale(root, from_=30, to=1, orient=tk.HORIZONTAL)
fps.pack()

# Create a slider for scale
scale_label = tk.Label(root, text="Scale:")
scale_label.pack()
scale = tk.Scale(root, from_=100, to=800, orient=tk.HORIZONTAL)
scale.pack()

# Start the Tkinter event loop
root.mainloop()