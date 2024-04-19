from setuptools import setup
from __version__ import __versionMac__

if any(char.isalpha() for char in __versionMac__):
    icon = 'icoDev.icns'
else:
    icon = 'ico.icns'

APP = ['main-MacARM.py']
OPTIONS = {
    'iconfile': icon, 
    'packages':[
        'PIL', 
        'tkinterdnd2', 
        'urllib3', 
        'packaging', 
        'requests', 
        'pywinctl', 
        'tkmacosx',
        'colour',
        'charset_normalizer',
        'colorama',
        'tk',
        'tqdm',
        'typing_extensions',
        'wand',
        ],
    'includes':[
        'requests',
        'tkinter',
        'os',
        'json',
        'shutil',
        'sys',
        'atexit',
        'threading',
        'time',
        'math',
        'glob',
        'platform',
        ],
    'frameworks':[
        '/opt/homebrew/Cellar/tcl-tk/8.6.14/lib/libtk8.6.dylib',
        '/opt/homebrew/Cellar/tcl-tk/8.6.14/lib/libtcl8.6.dylib',
    ],
    'plist': {
        'NSHumanReadableCopyright': 
            'Copyright © 2024 John Nathaniel Calvara. This software is licensed under the MIT License.',
        'CFBundleIdentifier':
            "dev.n8ventures.N8\'sVideoToGIFConverter(Beta)",
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
        'ico.icns',
        'icoDev.icns',
        './splash/splash.gif',
        './splash/splashEE.gif',
        './buildandsign/ico/amor.png',
        './buildandsign/ico/ico3.png',
        './buildandsign/ico/ico3beta.png',
        './buildandsign/ico/motionteamph.png',
        ]),
     ('../lib', ['/opt/homebrew/Cellar/tcl-tk/8.6.14/lib/']),
        ]
setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    name='N8\'s Video To GIF Converter (Beta)',
    version= __versionMac__,
    description='convert videos to gif using FFMPEG and Gifski.',
    author='John Nathaniel Calvara',
    author_email='nate@n8ventures.dev',
    url='https://github.com/n8ventures/video-to-gifski',
)
