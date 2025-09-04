'''
It reduces the background slices so that background slices are same number as cmb patches.
'''
import os
import sys

removal_count = 0
root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/csf_png_for_biomedparse_cmbonly"
images_dir = f"{root_path}/images/train"
labels_dir = f"{root_path}/labels/train"
masks_dir = f"{root_path}/masks/train"

for label_file in os.listdir(labels_dir):
    label_path = os.path.join(labels_dir, label_file)
    with open(label_path, 'r') as file:
        content = file.read().strip()
        print(content[0])
        if not content or content[0]=='1':
            image_file = label_file.replace('.txt', '.png')
            image_path = os.path.join(images_dir, image_file)
            os.remove(label_path)
            os.remove(image_path)
            print(f"Deleted: {label_path} and {image_path}")
            removal_count += 1

    # if len(os.listdir(images_dir)) <= 800:
    #     break

print("Cleanup complete.")