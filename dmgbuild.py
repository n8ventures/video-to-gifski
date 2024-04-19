import os.path
#
# Example settings file for dmgbuild
#

# Use like this: 
#  dmgbuild -s dmgbuild.py -D filesystem='APFS' "N8's Video To Gifski (Beta)" "N8's Video To Gifski (Beta).dmg"

# You can actually use this file for your own application (not just TextEdit)
# by doing e.g.
#
#   dmgbuild -s settings.py -D app=/path/to/My.app "My Application" MyApp.dmg

# .. Useful stuff ..............................................................

application =  defines.get('app',"./dist/N8's Video To GIF Converter (Beta).app") # type: ignore
appname = os.path.basename(application)

# .. Basics ....................................................................

# Uncomment to override the output filename
filename = "N8's Video To Gifski (Beta).dmg"

# Uncomment to override the output volume name
volume_name = "N8's Video To Gifski (Beta)"

# Volume format (see hdiutil create -help)
format = defines.get("format", "UDRO")  # type: ignore # noqa: F821

# Compression level (if relevant)
# compression_level = 9

# Volume size
size = defines.get("size", None) # type: ignore

# Files to include
files = [application]

# Symlinks to create
symlinks = {"Applications": "/Applications"}

# Files to hide
# hide = [ 'Secret.data' ]

# Files to hide the extension of
# hide_extension = [ 'README.rst' ]

# Volume icon
#
# You can either define icon, in which case that icon file will be copied to the
# image, *or* you can define badge_icon, in which case the icon file you specify
# will be used to badge the system's Removable Disk icon. Badge icons require
# pyobjc-framework-Quartz.
#
icon = './buildandsign/dmg/icoDMG.icns'

# Where to put the icons
icon_locations = {appname: (120, 170), "Applications": (440, 170)}

# .. Window configuration ......................................................

# Background
#
# This is a STRING containing any of the following:
#
#    #3344ff          - web-style RGB color
#    #34f             - web-style RGB color, short form (#34f == #3344ff)
#    rgb(1,0,0)       - RGB color, each value is between 0 and 1
#    hsl(120,1,.5)    - HSL (hue saturation lightness) color
#    hwb(300,0,0)     - HWB (hue whiteness blackness) color
#    cmyk(0,1,0,0)    - CMYK color
#    goldenrod        - X11/SVG named color
#    builtin-arrow    - A simple built-in background with a blue arrow
#    /foo/bar/baz.png - The path to an image file
#
# The hue component in hsl() and hwb() may include a unit; it defaults to
# degrees ('deg'), but also supports radians ('rad') and gradians ('grad'
# or 'gon').
#
# Other color components may be expressed either in the range 0 to 1, or
# as percentages (e.g. 60% is equivalent to 0.6).
background = "./buildandsign/dmg/DMG_BG.png"

show_status_bar = False
show_tab_view = False
show_toolbar = False
show_pathbar = False
show_sidebar = False
sidebar_width = 180

# Window position in ((x, y), (w, h)) format
window_rect = ((500, 500), (560, 400))

# Select the default view; must be one of
#
#    'icon-view'
#    'list-view'
#    'column-view'
#    'coverflow'
#
default_view = "icon-view"

# General view configuration
show_icon_preview = False

# Set these to True to force inclusion of icon/list view settings (otherwise
# we only include settings for the default view)
include_icon_view_settings = "auto"
include_list_view_settings = "auto"

# .. Icon view configuration ...................................................

arrange_by = None
grid_offset = (0, 0)
grid_spacing = 100
scroll_position = (0, 0)
label_pos = "bottom"  # or 'right'
text_size = 12
icon_size = 72

# .. List view configuration ...................................................

# Column names are as follows:
#
#   name
#   date-modified
#   date-created
#   date-added
#   date-last-opened
#   size
#   kind
#   label
#   version
#   comments
#
list_icon_size = 16
list_text_size = 12
list_scroll_position = (0, 0)
list_sort_by = "name"
list_use_relative_dates = True
list_calculate_all_sizes = (False,)
list_columns = ("name", "date-modified", "size", "kind", "date-added")
list_column_widths = {
    "name": 300,
    "date-modified": 181,
    "date-created": 181,
    "date-added": 181,
    "date-last-opened": 181,
    "size": 97,
    "kind": 115,
    "label": 100,
    "version": 75,
    "comments": 300,
}
list_column_sort_directions = {
    "name": "ascending",
    "date-modified": "descending",
    "date-created": "descending",
    "date-added": "descending",
    "date-last-opened": "descending",
    "size": "descending",
    "kind": "ascending",
    "label": "ascending",
    "version": "ascending",
    "comments": "ascending",
}

# .. License configuration .....................................................

# # Text in the license configuration is stored in the resources, which means
# # it gets stored in a legacy Mac encoding according to the language.  dmgbuild
# # will *try* to convert Unicode strings to the appropriate encoding, *but*
# # you should be aware that Python doesn't support all of the necessary encodings;
# # in many cases you will need to encode the text yourself and use byte strings
# # instead here.

# # Recognized language names are:
# #
# #    da_DK, de_AT, de_CH, de_DE, en_AU, en_GB, en_IE, en_SG, en_US, es_ES,
# #    fi_FI, fr_BE, fr_FR, fr_CA, fr_CH, it_IT, ja_JP, ko_KR, nb_NO, nl_BE,
# #    nl_NL, pt_BR, pt_PT, ru_RU, sv_SE, zh_CN, zh_TW,

# license = {
#     "default-language": "en_US",
#     "licenses": {
#         # For each language, the text of the license.  This can be plain text,
#         # RTF (in which case it must start "{\rtf1"), or a path to a file
#         # containing the license text.  If you're using RTF,
#         # watch out for Python escaping (or read it from a file).
#         "en_GB": b"""{\\rtf1\\ansi\\ansicpg1252\\cocoartf1504\\cocoasubrtf820
#  {\\fonttbl\\f0\\fnil\\fcharset0 Helvetica-Bold;\\f1\\fnil\\fcharset0 Helvetica;}
#  {\\colortbl;\\red255\\green255\\blue255;\\red0\\green0\\blue0;}
#  {\\*\\expandedcolortbl;;\\cssrgb\\c0\\c0\\c0;}
#  \\paperw11905\\paperh16837\\margl1133\\margr1133\\margb1133\\margt1133
#  \\deftab720
#  \\pard\\pardeftab720\\sa160\\partightenfactor0

#  \\f0\\b\\fs60 \\cf2 \\expnd0\\expndtw0\\kerning0
#  \\up0 \\nosupersub \\ulnone \\outl0\\strokewidth0 \\strokec2 Test License\\
#  \\pard\\pardeftab720\\sa160\\partightenfactor0

#  \\fs36 \\cf2 \\strokec2 What is this?\\
#  \\pard\\pardeftab720\\sa160\\partightenfactor0

#  \\f1\\b0\\fs22 \\cf2 \\strokec2 This is the English license. It says what you are allowed to do with this software.\\
#  \\
#  }""",
#         "de_DE": "Ich bin ein Berliner. Bielefeld gibt's doch gar nicht.",
#     },
#     "buttons": {
#         # For each language, text for the buttons on the licensing window.
#         #
#         # Default buttons and text are built-in for the following languages:
#         #
#         #   da_DK: Danish
#         #   de_DE: German
#         #   en_AU: English (Australian)
#         #   en_GB: English (UK)
#         #   en_NZ: English (New Zealand)
#         #   en_US: English (US)
#         #   es_ES: Spanish
#         #   fr_CA: French (Canadian)
#         #   fr_FR: French
#         #   it_IT: Italian
#         #   ja_JP: Japanese
#         #   nb_NO: Norsk
#         #   nl_BE: Flemish
#         #   nl_NL: Dutch
#         #   pt_BR: Brazilian Portuguese
#         #   pt_PT: Portugese
#         #   sv_SE: Swedish
#         #   zh_CN: Simplified Chinese
#         #   zh_TW: Traditional Chinese
#         #
#         # You don't need to specify them for those languages; if you fail to
#         # specify them for some other language, English will be used instead.
#         "en_US": (
#             b"English",
#             b"Agree!",
#             b"Disagree!",
#             b"Print!",
#             b"Save!",
#             b'Do you agree or not? Press "Agree" or "Disagree".',
#         ),
#     },
# }