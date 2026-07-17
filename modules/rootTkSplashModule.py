from tkinterdnd2 import TkinterDnD
from PIL import Image, ImageSequence
from tkinter import PhotoImage
import os
import subprocess
import json

from modules.TkModules import center_window
from modules.platformModules import win, mac, bundle_path, icon, gifski, ffmpeg
from modules.argsModule import args


import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_ALL


class CTk(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)


def set_args(argument=None):
    if argument is None:
        return False
    global args
    args = argument
    return True


_THEME_PATH = "buildandsign/themes/Marcel.json" if not bundle_path else os.path.join(bundle_path, "themes/Marcel.json")

with open(_THEME_PATH) as f:
    theme = json.load(f)

slider_theme = theme["CTkSlider"]
NORMAL_FG = {
    "progress_color": tuple(slider_theme["progress_color"]),
    "button_color": tuple(slider_theme["button_color"]),
}
DISABLED_FG = {
    "progress_color": tuple(theme["CTkButton"]["text_color_disabled"]),
    "button_color": tuple(theme["CTkButton"]["text_color_disabled"]),
}
ALT_FRAME_FG = {
    "fg_color": tuple(theme["CTk"]["fg_color"][::-1]),
}
ALT_TEXT_COLOR = {
    "text_color": tuple(theme["CTkLabel"]["text_color"][::-1]),
}
button_theme = theme["CTkButton"]
ALT_BUTTON_COLOR = {
    "fg_color": tuple(button_theme["fg_color"][::-1]),
    "hover_color": tuple(button_theme["hover_color"][::-1]),
    "border_color": tuple(button_theme["border_color"][::-1]),
    "text_color": tuple(button_theme["text_color"][::-1]),
    "text_color_disabled": tuple(button_theme["text_color_disabled"][::-1]),
}


ctk.set_appearance_mode("System")
ctk.set_default_color_theme(_THEME_PATH)

root = CTk()
root.withdraw()

gifski_ver = None
ffmpeg_ver = None
try:
    if gifski:
        gifski_ver = subprocess.run([str(gifski), "--version"], capture_output=True, text=True)
except Exception:
    gifski_ver = None

try:
    if ffmpeg:
        ffmpeg_ver = subprocess.run([str(ffmpeg), "-version"], capture_output=True, text=True)
except Exception:
    ffmpeg_ver = None

gifski_output = gifski_ver.stdout or gifski_ver.stderr
ffmpeg_output = ffmpeg_ver.stdout or ffmpeg_ver.stderr
print("Gifski Version:", gifski_output.strip())
print("ffmpeg Version:", ffmpeg_output.splitlines()[0].strip())

print("TCL Library:", root.tk.exprstring("$tcl_library"))
print("Tk Library:", root.tk.exprstring("$tk_library"))

if win:
    root.iconbitmap(icon)
elif mac:
    root.iconphoto(True, PhotoImage(file=icon))


# print(style.theme_names())  # List all themes
# print(style.layout("TLabel"))  # Display layout for 'TLabel'

splash_screen = ctk.CTkToplevel(root)
splash_screen.overrideredirect(True)
splash_screen.attributes("-topmost", True)  # Keep the window on top
if win:
    splash_screen.attributes("-transparentcolor", "white")
elif mac:
    # NOTE: since tk9.0, transparency is broken.
    splash_screen.attributes("-transparent", "true")
splash_screen.config(background="#000")

splash_geo_x = 350
splash_geo_y = 550

center_window(splash_screen, splash_geo_x, splash_geo_y)

gif_path = "splash.gif"
if bundle_path:
    gif_path = os.path.join(bundle_path, gif_path)
else:
    gif_path = ".//splash//splash.gif"

gif_img = Image.open(gif_path)
gif_frames_rgba = [frame.convert("RGBA") for frame in ImageSequence.Iterator(gif_img)]

splash_label = ctk.CTkLabel(splash_screen, text="")
splash_label.pack()


def animate(frame_num, loop):
    frame = gif_frames_rgba[frame_num]
    # photo = ImageTk.PhotoImage(frame)
    photo = ctk.CTkImage(light_image=frame, dark_image=frame, size=(splash_geo_x, splash_geo_y))
    splash_label.configure(image=photo)
    splash_label.image = photo

    if loop:
        frame_num = (frame_num + 1) % len(gif_frames_rgba)
        splash_screen.after(25, animate, frame_num, True)
    elif frame_num < len(gif_frames_rgba) - 1:
        frame_num += 1
        splash_screen.after(25, animate, frame_num, False)
