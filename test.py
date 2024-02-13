import subprocess
import json


cmd = ('.\\dist\\n8-vid-to-gif-2.1.0.exe')
result = subprocess.run(cmd, capture_output=True, text=True)
print(result)
print('####################')
print(result.stdout)
print('###############')

# def get_video_data(input_file):
#     cmd = [
#         "ffprobe",
#         "-v", "error",
#         "-select_streams", "v:0",
#         "-show_entries", "stream=width,height,r_frame_rate,duration",
#         "-of", "json",
#         input_file
#     ]

#     result = subprocess.run(cmd, capture_output=True, text=True)
    
#     if result.returncode == 0:
#         # Parse the JSON output
#         video_info = json.loads(result.stdout)
#         return video_info['streams'][0]  # Assuming there is only one video stream
#     else:
#         # Handle error
#         print(f"Error: {result.stderr}")
#         return None

# # Example usage
# input_file_path = "D:\ENTAIN\BetMGM\Sports/2022\BTL_1104073\Output\BTL_1104073 PC_Rich Push Image - 1038x600.mov"
# video_data = get_video_data(input_file_path)

# if video_data:
#     print("Video width:", video_data['width'])
#     print("Video height:", video_data['height'])
#     print("Frame rate:", round(eval(video_data['r_frame_rate']), 3))
#     print("Duration:", video_data['duration'])

# import tkinter as tk
# from tkinter import filedialog
# import subprocess
# import os

# def convert_to_gif(input_file, output_file, fps, scale):
#     cmd = [
#         "ffmpeg",
#         "-i", input_file,
#         "-vf", f"fps={fps},scale={scale}:-1:flags=lanczos",
#         "-c:v", "gif",
#         output_file
#     ]
#     subprocess.run(cmd)

# def choose_file():
#     file_path = filedialog.askopenfilename()
#     if file_path:
#         output_file = os.path.splitext(os.path.basename(file_path))[0] + ".gif"
#         fps_value = fps.get()
#         scale_value = scale.get()
#         convert_to_gif(file_path, output_file, fps_value, scale_value)
#         tk.messagebox.showinfo("Conversion Complete", f"File converted to {output_file}")

# # Create the main window
# root = tk.Tk()
# root.title("Video to GIF Converter")

# # Create a button to choose a file
# choose_button = tk.Button(root, text="Choose Video File", command=choose_file)
# choose_button.pack(pady=20)

# # Create a slider for FPS
# fps_label = tk.Label(root, text="Frames Per Second:")
# fps_label.pack()
# fps = tk.Scale(root, from_=1, to=30, orient=tk.HORIZONTAL)
# fps.pack()

# # Create a slider for scale
# scale_label = tk.Label(root, text="Scale:")
# scale_label.pack()
# scale = tk.Scale(root, from_=100, to=800, orient=tk.HORIZONTAL)
# scale.pack()

# # Start the Tkinter event loop
# root.mainloop()