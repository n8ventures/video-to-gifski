from tkinterdnd2 import TkinterDnD
from PIL import Image, ImageTk, ImageSequence
from tkinter import ttk, PhotoImage
import tkinter as tk
import os
import sys
import sv_ttk
import darkdetect
import subprocess

from modules.TkModules import center_window, widget_color
from modules.platformModules import win, mac, bundle_path, icon, gifski, ffmpeg
from modules.argsModule import args

def set_args(argument = None):
    if argument is None:
        return False
    global args
    args = argument
    return True

root = TkinterDnD.Tk()
root.withdraw()

gifski_ver = subprocess.run(
    [gifski, "--version"],
    capture_output=True,   
    text=True
)

ffmpeg_ver = subprocess.run(
    [ffmpeg, "-version"],
    capture_output=True,   
    text=True
)

gifski_output = gifski_ver.stdout or gifski_ver.stderr
ffmpeg_output = ffmpeg_ver.stdout or ffmpeg_ver.stderr
print("Gifski Version:", gifski_output.strip())
print("ffmpeg Version:", ffmpeg_output.splitlines()[0].strip())

print('TCL Library:', root.tk.exprstring('$tcl_library'))
print('Tk Library:',root.tk.exprstring('$tk_library'))

if win:
    root.iconbitmap(icon)
elif mac:
    root.iconphoto(True, PhotoImage(file=icon))

sv_ttk.set_theme(darkdetect.theme())
print('sv_ttk.get_theme(): ', sv_ttk.get_theme())

if win:
    import pywinstyles
    def apply_theme_to_titlebar():
        version = sys.getwindowsversion()
        print ('sys.getwindowsversion(): ', version)

        if version.major == 10 and version.build >= 22000:
            # Set the title bar color to the background color on Windows 11 for better appearance
            pywinstyles.change_header_color(root, "#1c1c1c" if sv_ttk.get_theme() == "dark" else "#fafafa")
        elif version.major == 10:
            pywinstyles.apply_style(root, "dark" if sv_ttk.get_theme() == "dark" else "normal")


            # A hacky way to update the title bar's color on Windows 10 (it doesn't update instantly like on Windows 11)
            root.wm_attributes("-alpha", 0.99)
            root.wm_attributes("-alpha", 1)

    apply_theme_to_titlebar()

style = ttk.Style()
style.configure("Alt.TLabel", foreground=widget_color[1])
style.configure("WM.TLabel", foreground='gray')
style.configure(
    "AltBox.TLabel",
    background="white", 
    relief="solid",      
    borderwidth=1,       
)
style.configure("Alt.TCheckbutton", foreground=widget_color[1])

# print(style.theme_names())  # List all themes
# print(style.layout("TLabel"))  # Display layout for 'TLabel'

splash_screen = tk.Toplevel(root)
splash_screen.overrideredirect(1) 
splash_screen.attributes('-topmost', True)  # Keep the window on top
if win: 
    splash_screen.attributes("-transparentcolor", "white")
elif mac:
    splash_screen.attributes("-transparent", "true")
splash_geo_x = 350
splash_geo_y = 550
if args is not None and args.Egg:
    splash_geo_x = 400
    splash_geo_y = 400
center_window(splash_screen, splash_geo_x, splash_geo_y)

gif_path = 'splash.gif'
if bundle_path:
    gif_path = os.path.join(bundle_path, gif_path)
else:
    gif_path = './/splash//splash.gif'

if args is not None and args.Egg:
    gif_path = 'splashEE.gif'
    if bundle_path:
        gif_path = os.path.join(bundle_path, gif_path)
    else:
        gif_path = './/splash//splashEE.gif'

gif_img = Image.open(gif_path)
gif_frames_rgba = [frame.convert("RGBA") for frame in ImageSequence.Iterator(gif_img)]

splash_label = tk.Label(splash_screen, bg='white')
splash_label.pack()

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