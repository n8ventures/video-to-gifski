from __version__ import __appname__, __updaterversion__, __updatername__
import tkinter as tk
from tkinter import ttk
import subprocess
import os
import json
import re
import sys
import atexit
import requests
from tqdm.tk import tqdm
import threading
import pywinctl as pwc

import argparse
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-E", "--Egg",action='store_true', help = "Egg, mi amor")
parser.add_argument('-v', '--version', action='version', version = __updaterversion__)
args = parser.parse_args()

app_exe = f'{__appname__}.exe'
icon = 'icoUpdater.ico'
if hasattr(sys, '_MEIPASS'):
    icon = os.path.join(sys._MEIPASS, icon)
    #  app_exe=os.path.join(sys._MEIPASS, app_exe)

def create_popup(root, title, width, height, switch):
    popup = tk.Toplevel(root)
    popup.title(title)
    popup.geometry(f"{width}x{height}")
    popup.iconbitmap(icon)
    # popup.overrideredirect(True)
    popup.attributes('-toolwindow', 1)
    center_window(popup, width, height)
    
    if switch == 1:
        popup.bind("<FocusOut>", lambda e: popup.destroy())

    popup.grab_set()
    
    return popup

def check_appVer():
    global appversion
    cmd = (app_exe, '-v')
    if os.path.exists(app_exe):
        result = subprocess.run(cmd, capture_output=True, text=True)

        appversion = result.stdout.strip()

    else:
        Missing_main()

def Missing_main():
    global appversion
    missing_app_menu = create_popup(root, 'Main App Missing!', 300,100, 1)
    make_non_resizable(missing_app_menu)

    txt_label = tk.Label(missing_app_menu, text='You don\'t have the main app!\nDownloading it for you now...')
    txt_label.pack(pady=20)

    appversion = 'N/A'

    updatenow()

def get_latest_release_version(repo_owner, repo_name):
    global api_url
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    response = requests.get(api_url)

    if response.status_code != 200:
        return '0.0.0'
    release_info = json.loads(response.text)
    return release_info.get('tag_name', '0.0.0')

def threadMeUp(thread):
    threading.Thread(target=thread).start()

def download_file(url, destination):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    with open(destination, 'wb') as file, tqdm(
        desc=destination,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
        miniters=1,
        ncols=80,
        position=0,
        leave=True,
        tk_parent=root,
    ) as bar:
        bar._tk_window.iconbitmap(icon)
        center_window(bar._tk_window, 460, 60)
        for data in response.iter_content(chunk_size=1024):
            file.write(data)
            bar.update(len(data))
    #bar.close() 
    check_for_updates_prompt.config(text='Update downloaded! Restarting...')
    bar._tk_window.destroy()
    return

# def parse_version(filename):
#     pattern = r'-(\d+\.\d+\.\d+)\.exe$'
#     match = re.search(pattern, filename)
#     if match:
#         return match.group(1)
#     else:
#         return None

def updatenow():
    # root.withdraw()
    windows = pwc.getWindowsWithTitle('N8\'s Video', condition=pwc.Re.CONTAINS, flags=pwc.Re.IGNORECASE)
    print(windows)
    for window in windows:
        if window.getAppName() == f'{__appname__}.exe':
            print(f'closing {window.getAppName()}')
            window.close()

    def updatenow_function():
        spacer=tk.Label(root, text='')
        spacer.pack()
        check_for_updates_prompt.config(text='Updating...')
        update_button.pack_forget()
        close_button_update.pack_forget()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        latest = latest_version

        for filename in os.listdir(current_dir):
            if filename.startswith(__appname__):
                os.remove(os.path.join(current_dir, filename))
                print(f"Removed: {filename}")
            

        latest_file = app_exe
        
        response = requests.get(api_url)
        release_data = response.json()
        
        for asset in release_data['assets']:
            if asset['name'] == latest_file:
                download_url = asset['browser_download_url']

                downloadUpdate = download_file(download_url, latest_file)
                threadMeUp(downloadUpdate)

            elif asset['name'] == f'{__appname__}-{latest_version}.exe':
                download_url = asset['browser_download_url']

                downloadUpdate = download_file(download_url, latest_file)
                threadMeUp(downloadUpdate)

        root.update_idletasks()

        subprocess.Popen([latest_file])
        root.quit()
        # root.destroy()
        return
    
    threadMeUp(updatenow_function)

def make_non_resizable(window):
    window.resizable(False, False)

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = width  
    window_height = height
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2  
    window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    
def on_closing():

    print("Closing the updater application.")
    
    atexit.unregister(on_closing)  # Unregister the atexit callback
    root.destroy()
    
# Create the main window
root = tk.Tk()
root.title(f"N8's V2GC Updater {__updaterversion__}")
geo_width = 425
center_window(root, geo_width, 300)
root.iconbitmap(icon)
make_non_resizable(root)

global check_for_updates_prompt, update_button, close_button_update, latest_version, checkupdates

check_appVer()

print("Current version:", appversion)

current_version = appversion
switch = 0
make_non_resizable(root)

image_path = 'ico3Updater.png'
if hasattr(sys, '_MEIPASS'):
    image_path = os.path.join(sys._MEIPASS, image_path)
else:
    image_path = '.\\buildandsign\\ico\\ico3Updater.png'
imgYPos = 270

image = tk.PhotoImage(file=image_path)
resized_image = image.subsample(2)
label = tk.Label(root, image=resized_image, bd=0)
label.image = resized_image
label.place(x=geo_width / 2, y=imgYPos, anchor=tk.CENTER)
spacer = tk.Label(root, text='')
spacer.pack(pady=5)
check_for_updates_prompt = tk.Label(root, text='Checking for updates...')
check_for_updates_prompt.pack(pady=10)

version_display = tk.Label(root, text=f'(Current Version: {appversion})', font=('Helvetica', 10, 'italic'))
version_display.pack(pady=10)

latest_version = get_latest_release_version("n8ventures", "v2g-con-personal")
latest_version_display = tk.Label(root, text='')
latest_version_display.pack()

buttonFrame = tk.Frame(root)
buttonFrame.pack()
close_button_update = ttk.Button(buttonFrame, text="Cancel", command=on_closing)
close_button_update.pack()

update_button = ttk.Button(buttonFrame, text="Sure!", command=updatenow)
update_button.pack_forget()


root.update_idletasks()

if current_version == latest_version:
    switch = 1
    # root.after(2000, check_for_updates_prompt.config(text='You have the latest version!'))
    check_for_updates_prompt.config(text='You have the latest version!')
    close_button_update.config(text='Close')
elif current_version >= latest_version:
    # root.after(2000, check_for_updates_prompt.config(text='looks like you\'re using an unreleased version. heh.'))
    check_for_updates_prompt.config(text='looks like you\'re using an unreleased version. heh.\nDo you still want to download the stable release version?')
    latest_version_display.config(text=f'Latest Version: {latest_version}', font=('Helvetica', 10, 'bold'))
    close_button_update.config(text='Close')

    latest_version_display.pack()
    update_button.pack(side=tk.LEFT, pady=10, padx= 70)
    close_button_update.pack(side=tk.RIGHT, pady=10, padx= 70)

elif latest_version == '0.0.0':
    check_for_updates_prompt.config(text=f"Internet connection unavailable.\nPlease try again later.")
    close_button_update.config(text='Close')
    close_button_update.pack()
else:
    # root.after(2000, check_for_updates_prompt.config(text=f"New version {latest_version} is available.\n\nDo you want to update?"))
    check_for_updates_prompt.config(text=f"New version {latest_version} is available.\n\nDo you want to update?")
    close_button_update.pack_forget()
    update_button.pack(side=tk.LEFT, pady=10, padx= 50)
    close_button_update.pack(side=tk.RIGHT, pady=10, padx= 50)

    # width = max(update_button.winfo_reqwidth(), close_button_update.winfo_reqwidth())
    # x_position = (checkupdates.winfo_width() - width) // 2
    # update_button.pack_configure(padx=(x_position - 5, 5))
    # close_button_update.pack_configure(padx=(5, x_position - 5))

    close_button_update.config(text='Maybe later')
root.update_idletasks()
root.protocol("WM_DELETE_WINDOW", on_closing)
atexit.register(on_closing)

root.mainloop()
