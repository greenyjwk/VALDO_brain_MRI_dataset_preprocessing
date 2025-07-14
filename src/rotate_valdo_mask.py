import os
import cv2

def process_dataset(masks_dir, output_masks_dir):
    os.makedirs(output_masks_dir, exist_ok=True)
    for filename in os.listdir(masks_dir):
        if filename.endswith((".jpg", ".png")):
            mask_path = os.path.join(masks_dir, filename)
            output_mask_path = os.path.join(output_masks_dir, filename)
            mask = cv2.imread(mask_path)
            if mask is None:
                print(f"Failed to read mask: {mask_path}")
                continue
            else:
                print(f"{filename} is a valid mask file.")
            rotated_mask = cv2.rotate(mask, cv2.ROTATE_90_COUNTERCLOCKWISE)
            cv2.imwrite(output_mask_path, rotated_mask)
            
if __name__ == "__main__":
    task = "val"
    root_path = "/media/Datacenter_storage/Ji/valdo_dataset/valdo_gan"
    masks_dir = f"{root_path}/masks/{task}"
    output_masks_dir = f"{root_path}/masks/{task}"
    process_dataset(masks_dir, output_masks_dir)