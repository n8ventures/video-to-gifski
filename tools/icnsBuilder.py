import shutil
import subprocess
import os
from PIL import Image


def pngtoicns(png, output_dir="./assets/icons/mac/"):
    # Prepare paths
    iconset = f"{os.path.splitext(os.path.split(png)[1])[0]}.iconset"

    iconset_dir = os.path.join(output_dir, iconset)
    sizes = [(16, 16), (32, 32), (32, 32), (64, 64), (128, 128), (256, 256), (256, 256), (512, 512), (512, 512)]
    output_files = [
        "icon_16x16.png",
        "icon_16x16@2x.png",
        "icon_32x32.png",
        "icon_32x32@2x.png",
        "icon_128x128.png",
        "icon_128x128@2x.png",
        "icon_256x256.png",
        "icon_256x256@2x.png",
        "icon_512x512.png",
    ]

    os.makedirs(iconset_dir, exist_ok=True)

    for (width, height), output_file in zip(sizes, output_files):
        command = ["sips", "-z", str(width), str(height), png, "--out", os.path.join(iconset_dir, output_file)]
        subprocess.run(command, check=True)

    shutil.copy(png, os.path.join(iconset_dir, "icon_512x512@2x.png"))
    iconutil_command = ["iconutil", "-c", "icns", iconset_dir]
    subprocess.run(iconutil_command, check=True)

    shutil.rmtree(iconset_dir)


def pngtoico(png, output_dir="./assets/icons/win/"):
    if shutil.which("magick") is None:
        print("Install ImageMagick please: https://imagemagick.org/script/download.php")
        return

    def resize_image(image_path, output_path, size):
        with Image.open(image_path) as img:
            resized_img = img.resize(size)
            resized_img.save(output_path)

    image = png
    sizes = [(16, 16), (32, 32), (48, 48), (128, 128), (256, 256)]

    resize_folder = "resize"
    os.makedirs(resize_folder, exist_ok=True)

    for size in sizes:
        output_path = os.path.join(resize_folder, f"resized_{size[0]}x{size[1]}.png")
        resize_image(image, output_path, size)

    resized_images = [os.path.join(resize_folder, f"resized_{size[0]}x{size[1]}.png") for size in sizes]
    print(resized_images)

    cmd = (
        ["magick"]
        + resized_images
        + ["-type", "TrueColorAlpha", f"{output_dir}{os.path.splitext(os.path.basename(png))[0]}.ico"]
    )
    subprocess.run(cmd, check=True)
    shutil.rmtree("resize")


if __name__ == "__main__":
    pngtoicns("./assets/icons/mac/icon.png")
    pngtoicns("./assets/icons/mac/icoDMG.png")
