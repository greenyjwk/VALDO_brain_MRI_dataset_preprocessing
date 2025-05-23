# import os
# import sys

# root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_epd_gt_box_GAN_cmbOnly_2class_csf"
# images_dir = f"{root_path}/images/train"
# labels_dir = f"{root_path}/labels/train"

# for label_file in os.listdir(labels_dir):
#     print(label_file)
#     label_path = os.path.join(labels_dir, label_file)
#     image_file = label_file.replace('.txt', '.png')
#     image_path = os.path.join(images_dir, image_file)
#     print(f"Deleted: {image_path}")
#     os.remove(image_file)            
            
# print("Cleanup complete.")

# '''
# It removes png files that don't have cmb patches.
# It is usually used from the train dataset.
# '''


import os
import sys

root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_epd_gt_box_GAN_cmbOnly_2class_csf"
images_dir = f"{root_path}/images/train"
labels_dir = f"{root_path}/labels/train"

label_basenames = {os.path.splitext(f)[0] for f in os.listdir(labels_dir) if f.endswith('.txt')}

for image_file in os.listdir(images_dir):
    if image_file.endswith('.png'):
        base = os.path.splitext(image_file)[0]
        if base not in label_basenames:
            image_path = os.path.join(images_dir, image_file)
            print(f"Deleted: {image_path}")
            os.remove(image_path)

print("Cleanup complete.")

'''
It removes png files that don't have matching label files.
It is usually used from the train dataset.
'''