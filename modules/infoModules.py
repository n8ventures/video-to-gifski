import tkinter as ttk
import os
from idlelib.tooltip import Hovertip
import sys

from modules.platformModules import win, mac
from modules.PopupModules import create_popup
from modules.TkModules import make_non_resizable, Button, clickable_link_labels, Label, Frame
from modules.argsModule import args
from modules.rootTkSplashModule import root, ctk

from __version__ import __gifskiversion__, __author__

if win:
    from __version__ import __version__, __ffmpegversion__
elif mac:
    from __version__ import __versionMac__ as __version__, __ffmpegversion_Mac__ as __ffmpegversion__


def about():
    geo_width = 370
    geo_len = 300

    aboutmenu = create_popup(root, "About Me!", geo_width, geo_len, 1)
    make_non_resizable(aboutmenu)

    gifski_text = f"- Gifski (https://gif.ski/)\nVersion: {__gifskiversion__}"
    ffmpeg_text = "- FFmpeg (https://ffmpeg.org/)"

    if win:
        ffmpeg_text += "\nby gyan.dev"
    elif mac:
        ffmpeg_text += "\nby martin-riedl.de"

    ffmpeg_text += f"\nVersion: {__ffmpegversion__}"

    copyright_text = (
        "This program is distributed under the MIT License.\n" "Copyright (c) 2024-2025 John Nathaniel Calvara"
    )
    credits_text = "\nCredits:\n" f"{gifski_text}\n\n" f"{ffmpeg_text}"

    credits_label = Label(aboutmenu, text=credits_text, anchor="center", justify="center")
    credits_label.pack(pady=10)

    copyright_label = Label(aboutmenu, text=copyright_text, anchor="center", justify="center")
    copyright_label.pack(pady=5)

    clickable_link_labels(aboutmenu, "nate@n8ventures.dev", "mailto:nate@n8ventures.dev")
    clickable_link_labels(
        aboutmenu,
        "https://github.com/n8ventures",
        "https://github.com/n8ventures",
    )

    if win:
        aboutmenu.attributes("-topmost", True)

    close_button = Button(aboutmenu, text="Close", command=aboutmenu.destroy)
    close_button.pack(pady=10)


def watermark_label(parent, debug=""):
    version = __version__
    frame = ctk.CTkFrame(parent, bg_color="transparent", border_width=0)
    frame.pack(side=ctk.BOTTOM, fill=ctk.X)

    ctk.CTkLabel(
        frame,
        text=f" by {__author__}",
        text_color="gray",
    ).pack(side=ctk.LEFT, padx=5)

    ctk.CTkLabel(
        frame,
        text=f"version: {version} {debug}",
        text_color="gray",
    ).pack(side=ctk.RIGHT, padx=5)
