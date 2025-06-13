import os
import glob
from PIL import Image
from tqdm import tqdm  # for progress bar

def convert_to_single_channel(directory):
    image_files = glob.glob(os.path.join(directory, '*.png'))
    for img_path in tqdm(image_files, desc="Converting images"):
        try:
            with Image.open(img_path) as img:
                if img.mode != 'RGB':
                    img.convert('RGB')
                r, g, b = img.split()
                b.save(img_path)
        except Exception as e:
            print(f"Error processing {img_path}: {str(e)}")
    print(f"Successfully processed {len(image_files)} images")

if __name__ == "__main__":
    task = "val"
    convert_to_single_channel(f'/media/Datacenter_storage/Ji/valdo_dataset/valdo_t2s_cmbOnly_GAN/images/{task}')