import os
from PIL import Image
import numpy as np

def main(masks_dir):    
    for file in os.listdir(masks_dir):
        mask_path = os.path.join(masks_dir, file)
        mask = Image.open(mask_path)
        mask = np.array(mask)
        mask = mask // 255
        mask = Image.fromarray(mask.astype(np.uint8))
        mask.save(mask_path)

if __name__ == "__main__":
    task = "train"
    root_path = "/media/Datacenter_storage/Ji/valdo_dataset/valdo_gan"
    masks_dir = f"{root_path}/masks/{task}"
    main(masks_dir)