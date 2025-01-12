from setuptools import setup
from __version__ import __versionMac__, __appname__

if any(char.isalpha() for char in __versionMac__):
    icon = './icons/mac/icoDev.icns'
    app_name = f'{__appname__} (Beta)'
else:
    icon = './icons/mac/ico.icns'
    app_name = __appname__

APP = ['main.py']
OPTIONS = {
    'iconfile': icon, 
    'packages':[
        'PIL',
        'tkinter',
        'tkinterdnd2',
        'subprocess', 
        'json',
        'urllib3', 
        'packaging', 
        'requests', 
        'pywinctl', 
        'tkmacosx',
        'colour',
        'charset_normalizer',
        'colorama',
        'tk',
        'typing_extensions',
        'glob',
        'encodings',
        ],
    'includes':[
        'requests',
        'subprocess',
        'sys',
        'atexit',
        'tkinter',
        'os',
        'json',
        'shutil',
        'threading',
        'time',
        'math',
        'glob',
        'platform',
        ],
    'excludes':[
        'PyInstaller'
    ],
    'frameworks':[
        '/opt/homebrew/Cellar/tcl-tk@8/8.6.15/lib/libtk8.6.dylib',
        '/opt/homebrew/Cellar/tcl-tk@8/8.6.15/lib/libtcl8.6.dylib',
    ],
    'plist': {
        'NSHumanReadableCopyright': 
            'Copyright © 2024-2025 John Nathaniel Calvara. This software is licensed under the MIT License.',
        'CFBundleIdentifier':
            "dev.n8ventures.N8VideoToGifski",
        'NSAppleScriptEnabled':
            True,
        'CFBundleGetInfoString':
            'Convert Video To GIF with FFmpeg and Gifski.',
        }
}
DATA_FILES=[   
    ('.', [
        './buildandsign/bin/macOS/ffplay', 
        './buildandsign/bin/macOS/ffprobe', 
        './buildandsign/bin/macOS/ffmpeg',
        './buildandsign/bin/macOS/gifski',
        './icons/mac/ico.icns',
        './icons/mac/icoDev.icns',
        './splash/splash.gif',
        './splash/splashEE.gif',
        './buildandsign/ico/amor.png',
        './buildandsign/ico/ico3.png',
        './buildandsign/ico/ico3beta.png',
        './buildandsign/ico/motionteamph.png',
        ]),
     ('../lib', ['/opt/homebrew/Cellar/tcl-tk@8/8.6.15/lib/']),
        ]
setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    name=app_name,
    version= __versionMac__,
    description='convert videos to gif using FFMPEG and Gifski.',
    author='John Nathaniel Calvara',
    author_email='nate@n8ventures.dev',
    url='https://github.com/n8ventures/video-to-gifski',
)
