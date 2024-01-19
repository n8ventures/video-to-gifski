import os
import subprocess
from __version__ import __version__, __appname__

# PyInstaller build command
# build_command = f'pyinstaller --onefile --add-binary=".\\buildandsign\\bin\\ffmpeg.exe;." --add-binary=".\\buildandsign\\bin\\ffprobe.exe;." --add-binary=".\\buildandsign\\bin\\gifski.exe;." --hidden-import=tkinterdnd2.TkinterDnD --hidden-import=tkinter --collect-data pyinstaller_hooks_contrib.collect --add-data "C:\\python312\\lib\\site-packages\\tkinterdnd2;tkinterdnd2" --add-data ".\\ico.ico;." --noconsole --icon=".\\ico.ico" main.py'
build_command = 'pyinstaller ./main.spec'
subprocess.run(build_command, shell=True)

# Sign the executable using signtool
where_command= 'where /R "C:\\Program Files (x86)" signtool.*'
where_result = subprocess.run(where_command,capture_output=True, shell=True)
output_str = where_result.stdout.decode('utf-8')
output_lines = output_str.split('\r\n')

if os.path.exists("C:\\Program Files (x86)\\Windows Kits\\10\\App Certification Kit"):
    os.chdir("C:\\Program Files (x86)\\Windows Kits\\10\\App Certification Kit")
    signtool_exe = 'signtool.exe'
else:
    signtool_exe = output_lines[0]

script_directory = os.path.dirname(os.path.realpath(__file__))
# Construct the sign_command
sign_command = f'{signtool_exe} sign /f "{script_directory}\\buildandsign\\n8cert.pfx" /p n8123 /t http://timestamp.digicert.com /v "{script_directory}\\dist\\main.exe"'
subprocess.run(sign_command, shell=True)

# rename newly built main.exe
# go back to repo directory

os.chdir(script_directory)
os.chdir('./dist')

# Assuming 'old_name.exe' is the original file name
old_name = 'main.exe'
new_name = f'{__appname__}-{__version__}.exe'

if os.path.exists(new_name):
    os.remove(new_name)
    print(f'\nremoved {new_name}!') 

# Rename the file after signing
os.rename(old_name, new_name)
print(f'\nEXE Build version {__version__} DONE!')