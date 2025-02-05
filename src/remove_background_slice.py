import os

images_dir = "/mnt/storage/ji/brain_mri_valdo_mayo/YOLO_valdo_stacked_1mm_png_pm2_0205__temp/images/val"
labels_dir = "/mnt/storage/ji/brain_mri_valdo_mayo/YOLO_valdo_stacked_1mm_png_pm2_0205__temp/labels/val"
masks_dir = "/mnt/storage/ji/brain_mri_valdo_mayo/YOLO_valdo_stacked_1mm_png_pm2_0205__temp/masks/val"

for label_file in os.listdir(labels_dir):
    label_path = os.path.join(labels_dir, label_file)

    # Check if the label file is empty or contains only whitespace
    with open(label_path, 'r') as file:
        content = file.read().strip()
        if not content:
            image_file = label_file.replace('.txt', '.png')
            image_path = os.path.join(images_dir, image_file)
            mask_path = image_path.replace('images', 'masks')
            os.remove(label_path)
            os.remove(image_path)
            os.remove(mask_path)
            print(f"Deleted: {label_path} and {image_path} and {mask_path}")

print("Cleanup complete.")

'''
It removes png files that don't have cmb patches. 
It is usually used from the train dataset.
'''