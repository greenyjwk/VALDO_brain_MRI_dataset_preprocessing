import nibabel as nib
import numpy as np
import os
import sys
import glob
import json
import argparse
import re

def main():
    parser = argparse.ArgumentParser(description="Create 3-channel NIfTI images")
    parser.add_argument('--dataset', type=str, choices=['mayo', 'valdo'], default='valdo', required=False)
    
    # Mayo
    # parser.add_argument('--src_path', type=str, required=False, default="/brain_mri_valdo_mayo/mayo_bias_field_correction_resampled")
    # parser.add_argument('--output_path', type=str, required=False, default="/brain_mri_valdo_mayo/mayo_stacked_resampled")
    # parser.add_argument('--config_path', type=str, required=False, default="/VALDO_brain_MRI_dataset_preprocessing/configs/config.json")

    # Valdo
    parser.add_argument('--src_path', type=str, required=False, default="/brain_mri_valdo_mayo/valdo_resample_ALFA_bias_field_correction")
    parser.add_argument('--output_path', type=str, required=False, default="/brain_mri_valdo_mayo/valdo_resample_ALFA_stacked_T2S_only")
    parser.add_argument('--config_path', type=str, required=False, default="/VALDO_brain_MRI_dataset_preprocessing/configs/config.json")

    args = parser.parse_args()
    dataset = args.dataset
    
    if dataset == 'mayo':
        root = "/media/Datacenter_storage/Ji"
        src_path = root + args.src_path
        output_dir = root + args.output_path
        config_path = root + args.config_path
    elif dataset == "valdo":
        root = "/mnt/storage/ji"
        src_path = root + args.src_path
        output_dir = root + args.output_path
        config_path = root + args.config_path
    
    # config file
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for uid in os.listdir(src_path):
        subdir_path = os.path.join(src_path, uid)
        
        # creating subdirectory in output directory
        if not os.path.exists(os.path.join(output_dir, uid)):
            os.mkdir(os.path.join(output_dir, uid))

        if dataset == 'mayo':
            nii1 = glob.glob(os.path.join(subdir_path, f"{config['mayo_stack_order'][0]}*.nii.gz"))
            nii2 = glob.glob(os.path.join(subdir_path, f"{config['mayo_stack_order'][1]}*.nii.gz"))
            nii3 = glob.glob(os.path.join(subdir_path, f"{config['mayo_stack_order'][2]}*.nii.gz"))
        elif dataset == 'valdo':
            nii1 = glob.glob(os.path.join(subdir_path, f"*{config['valdo_stack_order'][0]}.nii.gz"))
            nii2 = glob.glob(os.path.join(subdir_path, f"*{config['valdo_stack_order'][1]}.nii.gz"))
            nii3 = glob.glob(os.path.join(subdir_path, f"*{config['valdo_stack_order'][2]}.nii.gz"))
            
            print(nii1)
            print(nii2)
            print(nii3)

        if not nii1 or not nii2 or not nii3:
            print(f"Files not found for subdir: {uid}")
            continue

        nii1 = nib.load(nii1[0])
        nii2 = nib.load(nii2[0])
        nii3 = nib.load(nii3[0])

        # Extract data arrays
        data1 = nii1.get_fdata()
        data2 = nii2.get_fdata()
        data3 = nii3.get_fdata()

        # Stack the arrays along a new 4th dimension (channel dimension)
        combined_data = np.stack([data1, data2, data3], axis=-1)

        # Create a new NIfTI image
        combined_nii = nib.Nifti1Image(combined_data, affine=nii3.affine)

        # Save the combined image
        output_file = os.path.join(output_dir, uid, f"{uid}.nii.gz")
        nib.save(combined_nii, output_file)

if __name__ == "__main__":
    main()