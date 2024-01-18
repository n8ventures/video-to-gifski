import os
import subprocess

# PyInstaller build command
build_command = f'pyinstaller --onefile --add-binary="C:\\Paths\\ffmpeg.exe;." --add-binary="C:\\Paths\\ffprobe.exe;." --add-binary="C:\\Users\\John.Calvara\\.cargo\\bin\\gifski.exe;." --noconsole main.py'
subprocess.run(build_command, shell=True)

# Sign the executable using signtool
os.chdir("C:\\Program Files (x86)\\Windows Kits\\10\\App Certification Kit")

# Construct the sign_command
sign_command = 'signtool.exe sign /f "D:\\personal\\repo\\v2g\\vid-to-gif-converter\\buildandsign\\n8cert.pfx" /p n8123 /t http://timestamp.digicert.com /v "D:\\personal\\repo\\v2g\\vid-to-gif-converter\\dist\\main.exe"'
subprocess.run(sign_command, shell=True)