import cv2
import os
import glob
from PIL import Image
from tqdm import tqdm  # for progress bar

def convert_to_single_channel(directory):
    image_files = glob.glob(os.path.join(directory, '*.png'))

    for img_path in tqdm(image_files, desc="Converting images"):
        try:
            # Read image
            with Image.open(img_path) as img:
                if img.mode != 'RGB':
                    img.convert('RGB')
                r, g, b = img.split()
                b.save(img_path)
        except Exception as e:
            print(f"Error processing {img_path}: {str(e)}")
    print(f"Successfully processed {len(image_files)} images")

# Use the function
convert_to_single_channel('/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_ESRGAN_T2S_only/images/val')