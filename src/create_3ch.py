import nibabel as nib
import numpy as np
import os
import glob
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description="Create 3-channel NIfTI images")
    parser.add_argument('--root_path', type=str, required=False, default="/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_bias_field_correction")
    parser.add_argument('--output_dir', type=str, required=False, default="/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_stacked_temp")
    parser.add_argument('--dataset', type=str, choices=['mayo', 'valdo'], default='mayo', required=False)
    parser.add_argument('--config_path', type=str, required=False, default="/media/Datacenter_storage/Ji/VALDO_brain_MRI_dataset_preprocessing/configs/config.json")
    args = parser.parse_args()

    root_path = args.root_path
    output_dir = args.output_dir
    dataset = args.dataset
    config_path = args.config_path
    
    # config file
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    for uid in os.listdir(root_path):
        subdir_path = os.path.join(root_path, uid)
        
        # creating subdirectory in output directory
        if not os.path.exists(os.path.join(output_dir, uid)):
            os.mkdir(os.path.join(output_dir, uid))

        if dataset == 'mayo':
            nii1 = glob.glob(os.path.join(subdir_path, f"{config['mayo_stack_order'][0]}*.nii.gz"))
            nii2 = glob.glob(os.path.join(subdir_path, f"{config['mayo_stack_order'][1]}*.nii.gz"))
            nii3 = glob.glob(os.path.join(subdir_path, f"{config['mayo_stack_order'][2]}*.nii.gz"))
        elif dataset == 'valdo':
            nii1 = glob.glob(os.path.join(subdir_path, f"{config['valdo_stack_order'][0]}*.nii.gz"))
            nii2 = glob.glob(os.path.join(subdir_path, f"{config['valdo_stack_order'][1]}*.nii.gz"))
            nii3 = glob.glob(os.path.join(subdir_path, f"{config['valdo_stack_order'][2]}*.nii.gz"))

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
        combined_nii = nib.Nifti1Image(combined_data, affine=nii1.affine)

        # Save the combined image
        output_file = os.path.join(output_dir, uid, f"{uid}.nii.gz")
        nib.save(combined_nii, output_file)

if __name__ == "__main__":
    main()