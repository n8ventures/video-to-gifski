import tkinter as ttk
import os
from idlelib.tooltip import Hovertip
import sys

from modules.platformModules import win, mac

from modules.rootTkSplashModule import root, ctk

from __version__ import __author__

if win:
    from __version__ import __version__
elif mac:
    from __version__ import __versionMac__ as __version__


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
