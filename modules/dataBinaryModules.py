import os
import subprocess
import json
from modules.platformModules import win, mac, ffprobe, ffplay

alpha_formats = [
    # RGB with alpha
    'rgba', 'abgr', 'argb', 'bgra', 
    
    # 64-bit RGB with alpha
    'rgba64be', 'rgba64le', 'bgra64be', 'bgra64le',
    
    # 32-bit RGBA
    'rgba32be', 'rgba32le',
    
    # YUV with alpha
    'yuva420p', 'yuva422p', 'yuva444p',
    
    # YUV with alpha at various bit depths
    'yuva420p9be', 'yuva420p9le',
    'yuva422p9be', 'yuva422p9le',
    'yuva444p9be', 'yuva444p9le',
    
    'yuva420p10be', 'yuva420p10le',
    'yuva422p10be', 'yuva422p10le',
    'yuva444p10be', 'yuva444p10le',
    
    'yuva420p12be', 'yuva420p12le',
    'yuva444p12le',
    
    'yuva420p16be', 'yuva420p16le',
    'yuva422p16be', 'yuva422p16le',
    'yuva444p16be', 'yuva444p16le',

    
    # Other formats
    'ya8',  # 8-bit grayscale with alpha
    'ya16be', 'ya16le',  # 16-bit grayscale with alpha
    
    # 64-bit YUV with alpha
    'ayuv64le', 'ayuv64be',
    
    # 32-bit float RGBA
    'rgbaf32be', 'rgbaf32le'
]

video_extensions = [
    # Common video formats
    '.mp4', '.m4v', '.mpeg', '.mpg', '.mp2', '.mpv', '.m4p', '.mpe', 
    '.avi', '.mov', '.qt', '.vob',  '.mkv',

    # High definition and other video formats
    '.m2ts', '.mts', '.m2v', '.ts', '.webm', '.wmv', '.yuv', 

    # Flash and streaming video formats
    '.flv', '.f4v', '.asf', '.rm', '.rmvb', '.nsv', '.roq', 

    # Animated image/video formats
    '.gif', '.gifv', '.mng', 

    # Less common video formats
    '.3g2', '.3gp', '.amv', '.drc', '.mpx', 

    # Open formats
    '.ogg', '.ogv', 

    # Professional video formats
    '.mxf', 

    # Additional formats
    '.svi'
]

def is_video_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    return file_extension.lower() in video_extensions

def get_filesize(file_path):
    size_bytes = os.path.getsize(file_path)
    size_mb = round(size_bytes / (1024 * 1024), 2)
    size_kb = round(size_bytes / 1024, 2)
    return f'{size_mb} MB ({size_kb} KB)'

#ffprobe
def get_video_data(input_file):
    cmd = [
        ffprobe,
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,duration,pix_fmt",
        "-of", "json",
        input_file
    ]

    if win:
        result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    elif mac:
        result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        # Parse the JSON output
        video_info = json.loads(result.stdout)
        return video_info['streams'][0]  # Assuming there is only one video stream
    else:
        # Handle error
        print(f"Error: {result.stderr}")
        return None

#ffplay
def play_gif(file_path):
    cmd = [
    ffplay,
    "-window_title", "Playing GIF Preview",
    "-loglevel", "-8",
    "-loop", "0",
    file_path
]
    if win:
        subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
    elif mac:
        subprocess.run(cmd)
