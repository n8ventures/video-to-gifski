import tkinter as tk
from tkinter import ttk, PhotoImage
import emoji

from __version__ import __version__
from modules.platformModules import icon, win, mac
from modules.TkModules import make_non_resizable, center_window, Button

def notavideo(invalid_file, valid_file):
    from modules.rootTkSplashModule import root
    longest_invalid_length = max((len(file) for file in invalid_file if len(file) > 50), default=0)
    longest_valid_length = max((len(file) for file in valid_file if len(file) > 50), default=0)
    largest_length = max(longest_invalid_length, longest_valid_length)

    weight = (largest_length * 3) + 400
    height = (((len(invalid_file)+len(valid_file))*16)+150)
    
    if len(valid_file) != 0:
        height = height + 25
        
    print(f'{weight} x {height}')
    notavideo = create_popup(root, "Not A Video!", weight, height, 1, 1)
    make_non_resizable(notavideo)
    if win:
        notavideo.attributes("-topmost", True) 

    invalid_files_list = emoji.emojize(":cross_mark: ") + emoji.emojize("\n:cross_mark: ").join(invalid_file)
    button_text = 'Close'
    
    if len(valid_file) != 0:
        valid_files_list = emoji.emojize(":check_mark_button: ") + emoji.emojize("\n:check_mark_button: ").join(valid_file)
        valid_text = f"The following files will be processed:\n\n{valid_files_list}"
        button_text = 'Continue'
    else:
        valid_text = 'Please select valid video files!'

    errortext = (
        "The following files are not video files:\n\n"
        f"{invalid_files_list}\n\n"
        f"{valid_text}"
    )

    display_text_label = ttk.Label(notavideo, text=errortext,  anchor="center", justify="center")
    display_text_label.pack(pady=10)

    close_button = Button(notavideo, text=button_text, command=notavideo.destroy)
    close_button.pack(pady=10) 

def create_popup(root, title, width, height, switch, lift = 0):
    popup = tk.Toplevel(root)
    popup.title(title)
    popup.geometry(f"{width}x{height}")

    if win:
        popup.iconbitmap(icon)

    # popup.overrideredirect(True)
    if win:
        popup.attributes('-toolwindow', 1)
    elif mac:
        popup.attributes('-type', 'utility')

    center_window(popup, width, height)

    if switch == 1:
        popup.bind("<FocusOut>", lambda e: popup.destroy())
    if lift == 1:
        popup.lift()

    popup.grab_set()
    return popup




