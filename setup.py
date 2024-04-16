from setuptools import setup
from __version__ import __versionMac__

if any(char.isalpha() for char in __versionMac__):
    icon = 'icoDev.icns'
else:
    icon = 'ico.icns'

APP = ['main-MacARM.py']
OPTIONS = {
     'iconfile': icon, 
     'packages':['PIL', 'tkinterdnd2', 'urllib3', 'packaging', 'requests', 'pywinctl'],
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
