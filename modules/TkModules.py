import customtkinter as ctk
from modules.platformModules import win, mac
from PIL import Image, ImageDraw, ImageFont, ImageTk

# Use CustomTkinter widgets as the primary building blocks
Button = ctk.CTkButton
Label = ctk.CTkLabel
Frame = ctk.CTkFrame
Slider = ctk.CTkSlider


def make_non_resizable(window):
    window.resizable(False, False)


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = width
    window_height = height
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position-35}")
    window.update_idletasks()


def clickable_link_labels(window, text, link):
    mailto_label = Label(window, text=text, cursor="hand2")
    mailto_label.pack()
    mailto_label.bind("<Button-1>", lambda e: open_link(link))


def open_link(url):
    import webbrowser

    webbrowser.open(url)


# EMOJI IMAGES
def emoji_img(text, size=13):
    VALID_EMOJI_SIZES = [20, 32, 40, 48, 64, 96, 160]

    def closest_size(size):
        return min(VALID_EMOJI_SIZES, key=lambda x: abs(x - size))

    px = int(round(size * 72 / 96))
    if win:
        font = ImageFont.truetype("seguiemj.ttf", px)
    elif mac:
        px = closest_size(px)
        font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", px)

    canvas = px * 4
    img = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.text(
        (canvas // 2, canvas // 2),
        text,
        font=font,
        embedded_color=True,
        anchor="mm",
    )

    bbox = img.getbbox()
    img = img.crop(bbox if bbox else (0, 0, px, px))

    return ctk.CTkImage(
        light_image=img,
        dark_image=img,
        size=img.size,
    )


def apply_emoji(widget, emoji_char, text="", px=13, compound="left"):
    """
    Makes an emoji render correctly on both platforms:
    - macOS: Tk's font fallback already renders color emoji fine, so the
      emoji just goes straight into the widget's text.
    - Windows: Tk won't render color emoji from a font at all, so we
      render it to an image via emoji_img() and set it as `image=`,
      with `text=` holding just the label text.
    The image ref is stashed on the widget itself (widget.image = ...) —
    same pattern you're already using for the title icon at line 373 —
    so Tk doesn't garbage-collect it once this function returns.
    """
    if mac:
        widget.configure(text=f"{emoji_char} {text}".strip())
        return

    img = emoji_img(emoji_char, size=px)
    widget.configure(text=text, image=img, compound=compound)
    widget.image = img


_fade_after_id = None  # tracks the in-flight animation so re-toggling mid-fade doesn't stack callbacks

import tkinter as tk


def animate_alpha(root, target, duration_ms, on_complete=None, steps=15):
    """
    Smoothly steps `root`'s alpha toward `target` over `duration_ms`.
    Cancels any fade already in progress before starting a new one, so
    rapid re-toggling can't stack conflicting animations.
    """
    global _fade_after_id
    if _fade_after_id is not None:
        try:
            root.after_cancel(_fade_after_id)
        except tk.TclError:
            pass
        _fade_after_id = None

    try:
        start = root.attributes("-alpha")
    except tk.TclError:
        start = 1.0

    step_delay = max(1, duration_ms // steps)

    def _step(i=0):
        global _fade_after_id
        try:
            progress = i / steps
            alpha = start + (target - start) * progress
            root.attributes("-alpha", alpha)
        except tk.TclError:
            return  # window destroyed mid-animation — bail quietly

        if i < steps:
            _fade_after_id = root.after(step_delay, lambda: _step(i + 1))
        else:
            _fade_after_id = None
            if on_complete:
                on_complete()

    _step()
