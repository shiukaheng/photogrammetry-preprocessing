# 📸 Photogrammetry pre-processing
This is a convenience script to pre-process images from a photogrammetry session. What it does:
- You dump in any images, either RAW or JPEG in the `/source` folder
- All RAW images will be converted to TIF using `dcraw` and `exiftool`, preserving EXIF data. Converted images (or copied, if image is JPEG), will be in the `/converted` folder
- Human masks are generated to remove presumably moving subjects (this script is designed for photogrammetry in public spaces), results of which will be in the `/masks` folder

## How to use
This script utilizes Docker to make sure it runs everywhere, because of the fuss of installing `dcraw`, `exiftool` and getting `pytorch` running.

Right now it can easily be used using any IDE supporting devcontainers, but in the near future it will be modified so it can run easily using regular Docker.

Once you are inside the container, simply run "~/process.sh" and the images would be processed.
