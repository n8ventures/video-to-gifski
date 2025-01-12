from tkinter import ttk
import tkinter as tk
import os
from idlelib.tooltip import Hovertip
import sys
import emoji

from modules.platformModules import win, mac
from modules.PopupModules import create_popup
from modules.TkModules import make_non_resizable, Button, clickable_link_labels
from modules.argsModule import args
from modules.rootTkSplashModule import root
from modules.UpdaterModule import CheckUpdates

from __version__ import __gifskiversion__, __author__
if win:
    from __version__ import __version__, __ffmpegversion__
elif mac:
    from __version__ import __versionMac__ as __version__, __ffmpegversion_Mac__ as __ffmpegversion__

def about():
    geo_width = 370
    geo_len = 300

    if args is not None and args.Egg:
        geo_width = 370
        geo_len= 410

    aboutmenu = create_popup(root, "About Us!", geo_width, geo_len, 1)
    make_non_resizable(aboutmenu)

    gifski_text = f"- Gifski (https://gif.ski/)\nVersion: {__gifskiversion__}"
    ffmpeg_text = f"- FFmpeg (https://ffmpeg.org/)\nVersion: {__ffmpegversion__}"
    copyright_text = (
    "This program is distributed under the MIT License.\n"
    "Copyright (c) 2024-2025 John Nathaniel Calvara"
    )
    credits_text = (
        "\nCredits:\n"
        f"{gifski_text}\n\n"
        f"{ffmpeg_text}"
    )

    credits_label = ttk.Label(aboutmenu, text=credits_text, anchor="center", justify="center")
    credits_label.pack(pady=10)

    copyright_label = ttk.Label(aboutmenu, text=copyright_text,  anchor="center", justify="center")
    copyright_label.pack(pady=5)

    clickable_link_labels(
        aboutmenu, 
        "nate@n8ventures.dev", 
        "mailto:nate@n8ventures.dev"
    )
    clickable_link_labels(
        aboutmenu,
        "https://github.com/n8ventures",
        "https://github.com/n8ventures",
    )
    if args is not None and args.Egg:
        egg_about(aboutmenu, geo_width, geo_len)

    close_button = Button(aboutmenu, text="Close", command=aboutmenu.destroy)
    close_button.pack(pady=10)


def egg_about(aboutmenu, geo_width, geo_len):
    mograph = 'motionteamph.png'
    mograph = (
        os.path.join(sys._MEIPASS, mograph)
        if hasattr(sys, '_MEIPASS')
        else '.\\buildandsign\\ico\\motionteamph.png'
    )
    image = tk.PhotoImage(file=mograph)
    label = tk.Label(aboutmenu, image=image, bd=0)
    label.image = image
    label.place(x=geo_width / 2, y=geo_len - 60, anchor=tk.CENTER)
    Hovertip(label, "BetMGM Manila Motions Team 2024")

def watermark_label(parent_window, debug = ''):
    menu_bar = tk.Menu(root)
    
    about_menu = tk.Menu(menu_bar, tearoff=0)

    from modules.rootTkSplashModule import sv_ttk, darkdetect
    is_dark = True if darkdetect.theme() else False

    def toggle_theme():
        global is_dark
        if sv_ttk.get_theme() == "dark":
            sv_ttk.use_light_theme()
            is_dark = False
        elif sv_ttk.get_theme() == "light":
            sv_ttk.use_dark_theme()
            is_dark = True
            
        theme_label = emoji.emojize(f"{':crescent_moon:' if is_dark else ':sun_with_face:'} - Toggle Theme")
        about_menu.delete(0)
        about_menu.insert_command(0, label=theme_label, command=toggle_theme)

    about_menu.add_command(label=emoji.emojize(f"{':crescent_moon:' if is_dark else ':sun_with_face:'} - Toggle Theme"), command=toggle_theme)
    about_menu.add_separator()
    
    about_menu.add_command(label="About Me", command=about)
    about_menu.add_command(label="Check for Updates", command=CheckUpdates)
    menu_bar.add_cascade(label="Help", menu=about_menu)
    
    parent_window.config(menu=menu_bar)
    
    frame = ttk.Frame(parent_window)
    frame.pack(side=tk.BOTTOM, fill=tk.X)

    separator_wm = ttk.Separator(frame, orient="horizontal")
    separator_wm.pack(side=tk.TOP, fill=tk.X)
    
    watermark_label = ttk.Label(frame, text=f" by {__author__}", style='WM.TLabel')
    watermark_label.pack(side=tk.LEFT, anchor=tk.SW)
    
    version_label = ttk.Label(frame, text=f"version: {__version__} {debug}", style='WM.TLabel')
    version_label.pack(side=tk.RIGHT, anchor=tk.SE)
    
    if mac:
        root.config(menu=menu_bar)