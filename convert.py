import os
import shutil
from multiprocessing import Pool, cpu_count
from functools import partial
from tqdm import tqdm

# Define the source and destination directories
source_dir = './source'
dest_dir = './converted'

# Ensure the destination directory exists
if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

# List of raw formats (you can add more if required)
raw_formats = ['.arw', '.cr2', '.nef', '.dng', '.raf']

def process_file(file):
    # Fetch the file's full path
    full_path = os.path.join(source_dir, file)

    # Check if it's an actual file
    if os.path.isfile(full_path):
        # Split the filename to fetch the extension
        name, ext = os.path.splitext(file)

        # Convert extensions to lowercase for comparison
        ext = ext.lower()

        # Check if the file is a raw image
        if ext in raw_formats:
            # Convert using dcraw and save it as a TIFF in the destination directory
            os.system(f'dcraw -c -T {full_path} > {os.path.join(dest_dir, name + ext + ".tif")}')
            # Use exiftool to copy metadata from original raw to the new TIFF
            os.system(f'exiftool -TagsFromFile {full_path} {os.path.join(dest_dir, name + ext + ".tif")} -overwrite_original > /dev/null')

        # Check if the file is a JPG or JPEG image
        elif ext in ['.jpg', '.jpeg']:
            # Copy the JPG/JPEG file to the destination directory
            shutil.copy2(full_path, os.path.join(dest_dir, file))

# Create a pool of worker processes
with Pool(cpu_count()) as p:
    list(tqdm(p.imap(process_file, os.listdir(source_dir)), total=len(os.listdir(source_dir)), desc="Converting files", ncols=100))

# Done!
print("Conversion and copy process completed!")
