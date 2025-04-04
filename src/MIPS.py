import os
import json
import cv2
import sys
import numpy as np
import nibabel as nib

def generate_json(vol_dir_path):
    print(vol_dir_path)
    uid_max_depth = dict()
    for vol in os.listdir(vol_dir_path):
        path = os.path.join(vol_dir_path, vol, vol + ".nii.gz")
        img = nib.load(path)
        img = img.get_fdata()
        max_depth = img.shape[2] -1

        uid_max_depth[vol] = max_depth
        print(uid_max_depth)
    print(uid_max_depth)
        
    json_output_path = "/mnt/storage/ji/uid_max_depth.json"  # Specify the output JSON file path
    with open(json_output_path, 'w') as json_file:
        json.dump(uid_max_depth, json_file, indent=4)  # Convert dict to JSON and save it


def load_json(json_file_path):
    # Path to the JSON file
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)  # Load the JSON content into a Python dictionary

    img_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_epd_gt_box_t2s/images/train"
    output_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_epd_gt_box_t2s/images/train_mean_pixel"
    os.makedirs(output_path, exist_ok=True)  # Create the output folder if it doesn't exist

    for img in os.listdir(img_path):
        uid_key = img.split('_')[0]
        uid_value = int(img.split('_')[-1].split('.')[0])
        
        # Get the slice numbers for the current slice and its neighbors
        slice_numbers = [uid_value - 1, uid_value, uid_value + 1]

        # Load the corresponding slices and calculate mean pixel intensity
        slices = []
        skip_outer_loop = False
        for slice_num in slice_numbers:
            slice_filename = f"{uid_key}_slice_{slice_num:03d}.png"
            slice_path = os.path.join(img_path, slice_filename)
            if os.path.exists(slice_path):
                img_data = cv2.imread(slice_path, cv2.IMREAD_GRAYSCALE)  # Load as grayscale
                slices.append(img_data)
            else:
                print(f"Slice {slice_filename} not found.")
                skip_outer_loop = True
                break
        if skip_outer_loop:
            continue

        if slices:
            # Stack the slices and calculate the mean pixel intensity for each pixel location
            stacked_slices = np.stack(slices, axis=0)  # Shape: (3, height, width)
            mean_pixel_intensity = np.mean(stacked_slices, axis=0).astype(np.uint8)  # Shape: (height, width)
            print("mean_pixel_intensity.shape  ", mean_pixel_intensity.shape)
            sys.exit()
            # Save the mean pixel intensity image
            
            output_file_path = os.path.join(output_path, img)
            cv2.imwrite(output_file_path, mean_pixel_intensity)
            print(f"Saved mean pixel intensity image to {output_file_path}")
        else:
            print(f"No valid slices found for {img}.")


if __name__ == "__main__":
    vol_dir_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_stacked"
    # generate_json(vol_dir_path)
    load_json("/mnt/storage/ji/uid_max_depth.json")