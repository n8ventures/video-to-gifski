# Video to Gifski
Convert videos and export them into GIFs using Gifski.

# Releases
Stable release is available on Windows (x64) & MacOSX (Apple Silicon/ARM).

Download and check the latest release [here](https://github.com/n8ventures/video-to-gifski/releases/latest).

or just directly download here without worry:

[OSX (ARM/Apple Silicon)](https://github.com/n8ventures/video-to-gifski/releases/latest/download/MacOS.-.N8.Video.To.Gifski.dmg)

[Windows](https://github.com/n8ventures/video-to-gifski/releases/latest/download/N8sVideoToGifski.exe)

## ⚠️ IMPORTANT for MacOS
<details>
<summary>Click to expand troubleshooting instructions</summary>

  <img src="https://github.com/n8ventures/video-to-gifski/blob/main/docs/misc/macOS_dmgWarning.png" alt="macOS DMG Warning" width="250">

   If you encounter anything like:

   _"N8's Video To Gifski.app is damaged and can’t be opened"_

   _"N8's Video To Gifski.app cannot be opened because the developer cannot be verified"_

   _""N8's Video To Gifski" can't be opened because Apple cannot check it for malicious software."_

   _""MacOS.-.N8.Video.To.Gifski.dmg" Not Opened."_ 

   Just copy this code, and then paste and run this on your Terminal:

   ### For The .DMG file:
   (Assuming you've downloaded it on your Downloads Folder)
   
   `sudo xattr -dr com.apple.quarantine ~/Downloads/MacOS.-.N8.Video.To.Gifski.dmg`
   
   or
   
   `sudo xattr -dr com.apple.quarantine ~/Downloads/MacOS\.-\.N8.Video.To.Gifski.dmg`

   ### For The Application:
   `sudo xattr -dr com.apple.quarantine "~/Applications/N8's Video To Gifski.app"`

   ### Alternatively,

   right-click or ⌃(CTRL)+Click the .app/.dmg and click 'Open', a pop-up will appear, then click 'Open' again.

   __More info here: https://support.apple.com/en-ph/guide/mac-help/mchleab3a043/mac__

</details>

<div align="center">
<h1>How To Use</h1>

### 1. Open up the program, either choose the "Choose File" Button, or drag the video on the window!

![Main Menu](docs/howto/1.png)

Since Version 4.0.0, you can batch-process multiple videos at once!

![Batch Mode](docs/tag-4-0-0//MacOS_DragDrop.gif)

### 2. Choose your compression options
I'd like to point out that enabling/checking Motion Quality and/or Lossy Quality affects the overall quality.

![Settings Menu](docs/howto/2.png)

Also, you'll also have this option pop up if it detects videos with alpha channels.

![Preunmultiply Filter](docs/howto/2b.png)

### 3. Preview the GIF
Click on the `Apply & Preview` button, to apply the settings you adjusted and a preview GIF should show along with the GIF Size and Dimensions.

![Settings Menu with Preview](docs/howto/3.gif)

If you don't like the current settings, you can always adjust it.

### 4. Save the GIF
Now just click the `Save As` button, and you're good to go.

![Save As Button](docs/howto/4a.png)

But, let's backtrack a bit, remember on the first time the program opens the GIF, you see the `Quick Export` button? It's there if you just want something converted quick and done.

First instance of opening the video:

![Quick Export Button](docs/howto/4b.png)

</div>

## Licenses

This software is distributed under the terms of the [MIT License](LICENSE).

Third-party components used in this software may have their own licenses. 
Please refer to the following for more information:

- [FFmpeg License](https://ffmpeg.org/legal.html)
- [GIFSKI License](https://gif.ski/license.html)
