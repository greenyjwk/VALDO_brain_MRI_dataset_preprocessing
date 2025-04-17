import os
import json
import cv2
import numpy as np
import nibabel as nib

def generate_json(vol_dir_path):
    uid_max_depth = dict()
    for vol in os.listdir(vol_dir_path):
        path = os.path.join(vol_dir_path, vol, vol + ".nii.gz")
        img = nib.load(path)
        img = img.get_fdata()
        max_depth = img.shape[2] -1
        uid_max_depth[vol] = max_depth
    json_output_path = "/mnt/storage/ji/uid_max_depth.json"  # Specify the output JSON file path
    with open(json_output_path, 'w') as json_file:
        json.dump(uid_max_depth, json_file, indent=4)  # Convert dict to JSON and save it

def load_json(json_file_path, vol_dir_path):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)  # Load the JSON content into a Python dictionary
    img_path = f"{vol_dir_path}/images/train"
    output_path = f"{vol_dir_path}/images/train"
    # output_path = "TEMP2/images/train"
    os.makedirs(output_path, exist_ok=True)  # Create the output folder if it doesn't exist

    for img in os.listdir(img_path):
        uid_key = img.split('_')[0]
        uid_value = int(img.split('_')[-1].split('.')[0])
        slice_numbers = [uid_value - 1, uid_value, uid_value + 1]
        slices = []
        skip_outer_loop = False
        for slice_num in slice_numbers:
            slice_filename = f"{uid_key}_slice_{slice_num:03d}.png"
            slice_path = os.path.join(img_path, slice_filename)
            if os.path.exists(slice_path):
                img_data = cv2.imread(slice_path, cv2.IMREAD_GRAYSCALE)
                slices.append(img_data)
            else:
                skip_outer_loop = True
                break
        if skip_outer_loop:
            continue

        if slices:
            # print(slices)
            stacked_slices = np.stack(slices, axis=-1)
            output_file_path = os.path.join(output_path, img)
            cv2.imwrite(output_file_path, stacked_slices)
        else:
            print(f"No valid slices found for {img}.")

if __name__ == "__main__":
    vol_dir_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_epd_gt_box_t2s_GAN_3slices"
    load_json("/mnt/storage/ji/uid_max_depth.json", vol_dir_path)