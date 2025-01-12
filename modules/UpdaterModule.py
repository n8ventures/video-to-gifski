import requests
import json
import os
import subprocess
import tkinter as tk
from tkinter import ttk

from modules.platformModules import win, mac
from modules.PopupModules import create_popup
from modules.TkModules import make_non_resizable, Button, open_link
from modules.argsModule import args

if win:
    from __version__ import __version__
elif mac:
    from __version__ import(
        __versionMac__ as __version__
)

global release, prerelease, n8_gif_repo

def get_latest_release_version(pr=False, filter_keywords=None, require_dmg=False):
    n8_gif_repo = "https://api.github.com/repos/n8ventures/video-to-gifski/releases"
    try:
        response = requests.get(n8_gif_repo)
        response.raise_for_status()  
    except:
        return {
            'tag_name': '0.0.0',
            'has_dmg': False,
            'has_exe': False,
            'html_url': ''
        }
    
    releases = json.loads(response.text)
    
    if not releases:
        return {
            'tag_name': '0.0.0',
            'has_dmg': False,
            'has_exe': False,
            'html_url': ''
        }
    
    for release in releases:
        if pr or not release.get('prerelease', False):
            tag_name = release.get('tag_name', '0.0.0')
            assets = release.get('assets', [])
            has_dmg = any(asset['name'].endswith('.dmg') for asset in assets)
            has_exe = any(asset['name'].endswith('.exe') for asset in assets)
            html_url = release.get('html_url', '')

            if (filter_keywords is None or all(keyword.lower() in tag_name.lower() for keyword in filter_keywords)) and (not require_dmg or has_dmg):
                return {
                    'tag_name': tag_name,
                    'has_dmg': has_dmg,
                    'has_exe': has_exe,
                    'html_url': html_url
                }
    
    return {
        'tag_name': '0.0.0',
        'has_dmg': False,
        'has_exe': False,
        'html_url': ''
    }

def CheckUpdates():
    from modules.rootTkSplashModule import root
    global release, prerelease
    if release['tag_name'] == '0.0.0' or prerelease['tag_name'] == '0.0.0':
        try:
            release = get_latest_release_version(pr=False)
            prerelease = get_latest_release_version(pr=True, filter_keywords=['osx', 'beta'])
        except:
            release = {
                'tag_name': '0.0.0',
                'has_dmg': False,
                'has_exe': False,
                'html_url': ''
            }
            prerelease = {
                'tag_name': '0.0.0',
                'has_dmg': False,
                'has_exe': False,
                'html_url': ''
            }
    has_prerelease_latest = 'beta' in prerelease['tag_name'].lower() and prerelease['has_dmg']
    has_release_latest = release['has_dmg']
    print(f'Pre-release: {has_prerelease_latest}\nRelease: {has_release_latest}')
    print(f'compare: {__version__ in prerelease['tag_name']}')
    print('\n-- DEBUG DATA --\n\n')
    print('RELEASE: ', release)
    print('\n\n')
    print('PRE-RELEASE: ', prerelease)
    print('\n\n')
    

    geo_width = 300
    geo_len = 190
    updatemenu = create_popup(root, "Checking for Updates...", geo_width, geo_len, 0)
    make_non_resizable(updatemenu)

    msglabel = tk.Label(updatemenu, text='')
    msglabel.pack(pady=10)

    version_display = tk.Label(updatemenu, text=f'(Current Version: {__version__})', font=('Helvetica', 14, 'italic'))
    version_display.pack(pady=2)
    latest_version_display = tk.Label(updatemenu, text ='Checking for updates...')
    latest_version_display.pack()
    ask_label = tk.Label(updatemenu, text='Would you like to update?\n')
    
    buttonsFrame = ttk.Frame(updatemenu)
    buttonsFrame.pack(side=tk.BOTTOM, pady=10)
    
    update_button = Button(buttonsFrame, text='Yes')
    close_button = Button(buttonsFrame, text="Close", command=updatemenu.destroy)
    close_button.pack(side=tk.RIGHT, padx=5)
    
    def update_btn_cmd(callback):
        updatemenu.destroy()
        callback()
    
    if has_beta:
        print('PASS -1A: HAS BETA')
        if has_prerelease_latest:
            print('PASS 0-A: HAS PRE RELEASE')
            update_button.config(command=lambda: update_btn_cmd(lambda: open_link(prerelease['html_url'])))
            
            current_version_parts = __version__.split('-')
            current_version = current_version_parts[0]
            current_tag = current_version_parts[1] if len(current_version_parts) > 1 else ''

            prerelease_parts = prerelease['tag_name'].split('-')
            prerelease_version = prerelease_parts[0]
            prerelease_tag = prerelease_parts[2] if len(prerelease_parts) > 2 else ''

            if current_version >= prerelease_version:
                print('PASS 1-A: CURRENT IS HIGHER OR EQUAL VS ONLINE')
                if current_tag.lower() >= prerelease_tag.lower() and current_version >= prerelease_version:
                    print('PASS 1-2-A: BETA IS HIGHER OR EQUAL VS ONLINE')
                    latest_version_display.config(text="You're up to date!")
                elif current_tag.lower() < prerelease_tag.lower() and current_version <= prerelease_version:
                    print('PASS 1-2-B: BETA IS OUTDATED VS ONLINE')
                    msglabel.config(text='A new beta patch is available!')
                    latest_version_display.config(text=f'Latest Version: {prerelease["tag_name"]}', font=('Helvetica', 14, 'bold'))
                    ask_label.pack(pady=10)
                    update_button.pack(side=tk.LEFT)
                    close_button.config(text='Cancel')
            elif current_version < prerelease_version:
                print('PASS 1-B: CURRENT IS LESS THAN ONLINE')
                msglabel.config(text='A new update is available!')
                latest_version_display.config(text=f'Latest Version: {prerelease["tag_name"]}', font=('Helvetica', 14, 'bold'))
                ask_label.pack(pady=10)
                update_button.pack(side=tk.LEFT)
                close_button.config(text='Cancel')
            else:
                print('PASS 1-C: NO NEW UPDATE')
                msglabel.config(text="No new pre-release available.")
                latest_version_display.config(text="You're up to date!")
                close_button.config(text='Close')
        elif release['tag_name'] == '0.0.0' or prerelease['tag_name'] == '0.0.0':
            print('PASS 0-B: INTERNET ERROR BETA')
            latest_version_display.config(text='Connection error, Please try again later.')

    elif has_release_latest:
        print('PASS -1B: HAS RELEASE')
        update_button.config(command=lambda: update_btn_cmd(lambda: open_link(release['html_url'])))
        current_version_parts = __version__.split('-')
        current_version = current_version_parts[0]
        release_version = release['tag_name']

        if current_version >= release_version:
            print('PASS 0-A: STABLE IS HIGHER OR EQUAL VS ONLINE')
            latest_version_display.config(text="You're up to date!")
        elif current_version < release_version:
            print('PASS 0-B: STABLE IS OUTDATED VS ONLINE')
            msglabel.config(text='A new update is available!')
            latest_version_display.config(text=f'Latest Version: {release["tag_name"]}', font=('Helvetica', 14, 'bold'))
            ask_label.pack(pady=10)
            update_button.pack(side=tk.LEFT)
            close_button.config(text='Cancel')
        else:
            print('PASS 0-C: NO NEW UPDATE')
            msglabel.config(text="No new update available.")
            latest_version_display.config(text="You're up to date!")
            close_button.config(text='Close')

    elif release['tag_name'] == '0.0.0' or prerelease['tag_name'] == '0.0.0':
        print('PASS -1C: INTERNET ERROR')
        latest_version_display.config(text='Connection error, Please try again later.', font=('Helvetica', 14, 'bold'))
    else:
        msglabel.config(text="No new release available.")
        latest_version_display.config(text="You're up to date!")

has_beta = ('beta' or 'alpha') in __version__.lower()
print(f'Has Beta? {has_beta}')

try:
    release = get_latest_release_version(pr=False)
    prerelease = get_latest_release_version(pr=True, filter_keywords=['osx', 'beta'])
except:
    release = {
        'tag_name': '0.0.0',
        'has_dmg': False,
        'has_exe': False,
        'html_url': ''
    }
    prerelease = {
        'tag_name': '0.0.0',
        'has_dmg': False,
        'has_exe': False,
        'html_url': ''
    }

    print('\n-- DEBUG DATA --\n')
    print('RELEASE: ', release)
    print('PRE-RELEASE: ', prerelease)
    print('\n')
    
def autoChecker():
    has_prerelease_latest = 'beta' in prerelease['tag_name'].lower() and prerelease['has_dmg']
    has_release_latest = release['has_dmg']

    if has_beta:
        print('PASS -1A: HAS BETA')
        if has_prerelease_latest:
            print('PASS 0-A: HAS PRE RELEASE')
            current_version_parts = __version__.split('-')
            current_version = current_version_parts[0]
            current_tag = current_version_parts[1] if len(current_version_parts) > 1 else ''

            prerelease_parts = prerelease['tag_name'].split('-')
            prerelease_version = prerelease_parts[0]
            prerelease_tag = prerelease_parts[2] if len(prerelease_parts) > 2 else ''

            if current_version >= prerelease_version:
                print('AC - PASS 1-A: CURRENT IS HIGHER OR EQUAL VS ONLINE')
                if current_tag.lower() >= prerelease_tag.lower() and current_version >= prerelease_version:
                    print('AC - PASS 1-2-A: BETA IS HIGHER OR EQUAL VS ONLINE')
                elif current_tag.lower() < prerelease_tag.lower() and current_version <= prerelease_version:
                    print('AC - PASS 1-2-B: BETA IS OUTDATED VS ONLINE')
                    return CheckUpdates()
            else:
                print('AC - PASS 1-B: CURRENT IS LESS THAN ONLINE')
                return CheckUpdates()
        elif release['tag_name'] == '0.0.0' or prerelease['tag_name'] == '0.0.0':
            print('AC - PASS 0-B: INTERNET ERROR BETA')

    elif has_release_latest:
        print('AC - PASS -1B: HAS RELEASE')
        current_version_parts = __version__.split('-')
        current_version = current_version_parts[0]
        release_version = release['tag_name']
        
        

        if current_version >= release_version:
            print('AC - PASS 0-A: STABLE IS HIGHER OR EQUAL VS ONLINE')
        else:
            print('AC - PASS 0-B: STABLE IS OUTDATED VS ONLINE')
            return CheckUpdates()
    elif release['tag_name'] == '0.0.0' or prerelease['tag_name'] == '0.0.0':
        print('AC - PASS -1C: INTERNET ERROR')