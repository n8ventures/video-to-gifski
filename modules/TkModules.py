from modules.platformModules import win, mac

# if win:
#     from tkinter import ttk
#     Button = ttk.Button
# elif mac:
#     from tkmacosx import Button
#     Button = Button

from tkinter import ttk
Button = ttk.Button

widget_color = [
    # 0 = Default
    "#323232", 
    # 1 = Colored
    "#7d7dff",
    # 2 = Default Greyed Out
    "#c8c8c8", 
    # 3 = Colored Greyed Out
    "#8383a6"
    ]

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

def clickable_link_labels(aboutmenu, text, link):
    mailto_label = ttk.Label(aboutmenu, text=text, style="Alt.TLabel", cursor="hand2")
    mailto_label.pack()
    mailto_label.bind("<Button-1>", lambda e: open_link(link))

def open_link(url):
    import webbrowser
    webbrowser.open(url)




