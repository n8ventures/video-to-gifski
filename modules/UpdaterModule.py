import requests
import json
import customtkinter as ctk

from modules.platformModules import win, mac, icon
from modules.TkModules import make_non_resizable, open_link, center_window
from packaging.version import parse as parse_version, InvalidVersion

if win:
    from __version__ import __version__
elif mac:
    from __version__ import __versionMac__ as __version__

global release, prerelease, n8_repo


def _fetch_releases():
    global release, prerelease
    try:
        release = get_latest_release_version(want_prerelease=False)
        prerelease = get_latest_release_version(want_prerelease=True)
    except Exception:
        release = {"tag_name": "0.0.0", "has_dmg_zip": False, "has_exe": False, "html_url": ""}
        prerelease = {"tag_name": "0.0.0", "has_dmg_zip": False, "has_exe": False, "html_url": ""}


release = {"tag_name": "0.0.0", "has_dmg_zip": False, "has_exe": False, "html_url": ""}
prerelease = {"tag_name": "0.0.0", "has_dmg_zip": False, "has_exe": False, "html_url": ""}
n8_repo = "https://api.github.com/repos/n8ventures/video-to-gifski/releases"


def create_popup(root, title, width, height, switch, lift=0):
    popup = ctk.CTkToplevel(root)
    center_window(popup, width, height)
    popup.title(title)

    if win:
        popup.iconbitmap(icon)

    # popup.overrideredirect(True)
    if win:
        popup.attributes("-toolwindow", 1)
    elif mac:
        popup.attributes("-type", "utility")

    if switch == 1:
        popup.bind("<FocusOut>", lambda e: popup.after(200, popup.destroy))
    if lift == 1:
        popup.lift()

    popup.grab_set()
    return popup


def safe_parse_version(v):
    """
    Wraps packaging.version.parse with a fallback for tags that don't
    parse as valid versions at all (e.g. a malformed or unexpected tag
    format) — returns version "0.0.0" rather than crashing the caller.
    """
    try:
        return parse_version(v.lstrip("v"))
    except InvalidVersion:
        return parse_version("0.0.0")


def get_latest_release_version(want_prerelease=False):
    try:
        response = requests.get(n8_repo)
        response.raise_for_status()
    except Exception:
        return {"tag_name": "0.0.0", "has_dmg_zip": False, "has_exe": False, "html_url": ""}

    releases = json.loads(response.text)

    if not releases:
        return {"tag_name": "0.0.0", "has_dmg_zip": False, "has_exe": False, "html_url": ""}

    for release in releases:
        if release.get("prerelease", False) == want_prerelease:
            tag_name = release.get("tag_name", "0.0.0")
            assets = release.get("assets", [])
            has_dmg_zip = any(
                asset["name"].lower().endswith(".zip") and "macos" in asset["name"].lower() for asset in assets
            )
            has_exe = any(asset["name"].endswith(".exe") for asset in assets)
            html_url = release.get("html_url", "")
            return {"tag_name": tag_name, "has_dmg_zip": has_dmg_zip, "has_exe": has_exe, "html_url": html_url}

    return {"tag_name": "0.0.0", "has_dmg_zip": False, "has_exe": False, "html_url": ""}


def CheckUpdates(root):
    global release, prerelease
    _fetch_releases()
    has_prerelease_latest = prerelease["tag_name"] != "0.0.0" and (
        prerelease["has_exe"] if win else prerelease["has_dmg_zip"]
    )
    has_release_latest = release["has_exe"] if win else release["has_dmg_zip"]

    print(f"Pre-release: {has_prerelease_latest}\nRelease: {has_release_latest}")
    print(f"compare: {__version__ in prerelease['tag_name']}")
    print("\n-- DEBUG DATA --\n\n")
    print("RELEASE: ", release)
    print("\n\n")
    print("PRE-RELEASE: ", prerelease)
    print("\n\n")

    geo_width = 300
    geo_len = 270
    updatemenu = create_popup(root, "Checking for Updates...", geo_width, geo_len, 0)
    make_non_resizable(updatemenu)

    msglabel = ctk.CTkLabel(updatemenu, text="")
    msglabel.pack(pady=10)

    version_display = ctk.CTkLabel(
        updatemenu, text=f"(Current Version: {__version__})", font=("Helvetica", 14, "italic")
    )
    version_display.pack(pady=2)
    latest_version_display = ctk.CTkLabel(updatemenu, text="Checking for updates...")
    latest_version_display.pack()
    ask_label = ctk.CTkLabel(updatemenu, text="Would you like to update?\n")

    buttonsFrame = ctk.CTkFrame(updatemenu)
    buttonsFrame.pack(side=ctk.BOTTOM, pady=10)

    if win:
        updatemenu.attributes("-topmost", True)

    update_button = ctk.CTkButton(buttonsFrame, text="Yes")
    close_button = ctk.CTkButton(buttonsFrame, text="Close", command=updatemenu.destroy)
    close_button.pack(side=ctk.RIGHT, padx=5)

    def update_btn_cmd(callback):
        updatemenu.destroy()
        callback()

    if has_beta:
        print("PASS -1A: HAS BETA")
        if has_prerelease_latest:
            print("PASS 0-A: HAS PRE RELEASE")
            update_button.configure(command=lambda: update_btn_cmd(lambda: open_link(prerelease["html_url"])))

            current_version_parts = __version__.split("-")
            current_version = current_version_parts[0]
            current_tag = current_version_parts[1] if len(current_version_parts) > 1 else ""

            prerelease_parts = prerelease["tag_name"].split("-")
            prerelease_version = prerelease_parts[0]
            prerelease_tag = prerelease_parts[2] if len(prerelease_parts) > 2 else ""

            current_version = safe_parse_version(current_version)
            prerelease_version = safe_parse_version(prerelease_version)

            if current_version >= prerelease_version:
                print("PASS 1-A: CURRENT IS HIGHER OR EQUAL VS ONLINE")
                if current_tag.lower() >= prerelease_tag.lower() and current_version >= prerelease_version:
                    print("PASS 1-2-A: BETA IS HIGHER OR EQUAL VS ONLINE")
                    latest_version_display.configure(text="You're up to date!")
                elif current_tag.lower() < prerelease_tag.lower() and current_version <= prerelease_version:
                    print("PASS 1-2-B: BETA IS OUTDATED VS ONLINE")
                    msglabel.configure(text="A new beta patch is available!")
                    latest_version_display.configure(
                        text=f'Latest Version: {prerelease["tag_name"]}', font=("Helvetica", 14, "bold")
                    )
                    ask_label.pack(pady=10)
                    update_button.pack(side=ctk.LEFT)
                    close_button.configure(text="Cancel")
            elif current_version < prerelease_version:
                print("PASS 1-B: CURRENT IS LESS THAN ONLINE")
                msglabel.configure(text="A new update is available!")
                latest_version_display.configure(
                    text=f'Latest Version: {prerelease["tag_name"]}', font=("Helvetica", 14, "bold")
                )
                ask_label.pack(pady=10)
                update_button.pack(side=ctk.LEFT)
                close_button.configure(text="Cancel")
            else:
                print("PASS 1-C: NO NEW UPDATE")
                msglabel.configure(text="No new pre-release available.")
                latest_version_display.configure(text="You're up to date!")
                close_button.configure(text="Close")
        elif release["tag_name"] == "0.0.0" or prerelease["tag_name"] == "0.0.0":
            print("PASS 0-B: INTERNET ERROR BETA")
            latest_version_display.configure(text="Connection error, Please try again later.")

    elif has_release_latest:
        print("PASS -1B: HAS RELEASE")
        update_button.configure(command=lambda: update_btn_cmd(lambda: open_link(release["html_url"])))
        current_version_parts = __version__.split("-")
        current_version = current_version_parts[0]
        release_version = release["tag_name"]

        current_version = safe_parse_version(current_version)
        release_version = safe_parse_version(release_version)

        if current_version >= release_version:
            print("PASS 0-A: STABLE IS HIGHER OR EQUAL VS ONLINE")
            latest_version_display.configure(text="You're up to date!")
        elif current_version < release_version:
            print("PASS 0-B: STABLE IS OUTDATED VS ONLINE")
            msglabel.configure(text="A new update is available!")
            latest_version_display.configure(
                text=f'Latest Version: {release["tag_name"]}', font=("Helvetica", 14, "bold")
            )
            ask_label.pack(pady=10)
            update_button.pack(side=ctk.LEFT)
            close_button.configure(text="Cancel")
        else:
            print("PASS 0-C: NO NEW UPDATE")
            msglabel.configure(text="No new update available.")
            latest_version_display.configure(text="You're up to date!")
            close_button.configure(text="Close")

    elif release["tag_name"] == "0.0.0" or prerelease["tag_name"] == "0.0.0":
        print("PASS -1C: INTERNET ERROR")
        latest_version_display.configure(
            text="Connection error, Please try again later.", font=("Helvetica", 14, "bold")
        )
    else:
        msglabel.configure(text="No new release available.")
        latest_version_display.configure(text="You're up to date!")


has_beta = any(char.isalpha() for char in __version__)
print(f"Has Beta? {has_beta}")


def autoChecker(root):
    _fetch_releases()
    has_prerelease_latest = prerelease["tag_name"] != "0.0.0" and (
        prerelease["has_exe"] if win else prerelease["has_dmg_zip"]
    )
    has_release_latest = release["has_exe"] if win else release["has_dmg_zip"]  # ← was missing

    if has_beta:
        if has_prerelease_latest:
            current_version_parts = __version__.split("-")
            current_version = safe_parse_version(current_version_parts[0])
            current_tag = current_version_parts[1] if len(current_version_parts) > 1 else ""

            prerelease_parts = prerelease["tag_name"].split("-")
            prerelease_version = safe_parse_version(prerelease_parts[0])
            prerelease_tag = prerelease_parts[2] if len(prerelease_parts) > 2 else ""

            if current_version < prerelease_version or (
                current_version <= prerelease_version and current_tag.lower() < prerelease_tag.lower()
            ):
                root.after(0, lambda: CheckUpdates(root))
    elif has_release_latest:
        current_version = safe_parse_version(__version__.split("-")[0])
        release_version = safe_parse_version(release["tag_name"])
        if current_version < release_version:
            root.after(0, lambda: CheckUpdates(root))
