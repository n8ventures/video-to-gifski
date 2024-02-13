from wand.image import Image
import os
import shutil
def resize_image(image_path, output_path, size):
    with Image(filename=image_path) as img:
        img.resize(size[0], size[1])
        img.save(filename=output_path)

mainDir = '..\\..\\'

def main(png):
    image = png
    sizes = [(16, 16), (32, 32), (48, 48), (128, 128), (256, 256)]

    # Create a 'resize' folder if it doesn't exist
    import os
    resize_folder = "resize"
    os.makedirs(resize_folder, exist_ok=True)

    # Resize the image to each size
    for size in sizes:
        output_path = os.path.join(resize_folder, f"resized_{size[0]}x{size[1]}.png")
        resize_image(image, output_path, size)

    # Combine the resized images into a single ICO file
    resized_images = [os.path.join(resize_folder, f"resized_{size[0]}x{size[1]}.png") for size in sizes]
    print(resized_images)
    if png == 'ico2.png':
        output_ico = f'{mainDir}ico.ico'
        print()
    elif png == 'icobeta.png':
        output_ico = f'{mainDir}icoDev.ico'
    else:
        output_ico = f'{mainDir}{png[:png.rfind('.')]}.ico'
        
    cmd = ["magick", "convert"] + resized_images + ["-colors", "256", output_ico]
    import subprocess
    subprocess.run(cmd, check=True)
    shutil.rmtree('resize')
    
if __name__ == "__main__":
    main('ico2.png')
    main('icobeta.png')
    main('icoUpdater.png')