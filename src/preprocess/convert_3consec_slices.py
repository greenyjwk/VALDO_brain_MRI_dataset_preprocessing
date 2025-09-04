import nibabel as nib
import numpy as np
import os
import sys

out_path_root = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/3_consec_slices_TEMP"
root_dir = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/bias_field_correction_resampled"


for uid in os.listdir(root_dir):
    if not os.path.exists(os.path.join(out_path_root, uid)):
        os.makedirs(os.path.join(out_path_root, uid))
        print("Created:", out_path_root)
    else:
        print("Already exists:", out_path_root)
    nii_path = os.path.join(root_dir, uid, f"{uid}_space-T2S_desc-masked_T2S.nii.gz")

    # Load NIfTI
    nii = nib.load(nii_path)
    data = nii.get_fdata()   # shape: (255, 255, 39)
    print("Original shape:", data.shape)
    # Initialize new array: (H, W, D-2, 3)
    H, W, D = data.shape
    stacked = np.zeros((H, W, D-2, 3), dtype=data.dtype)
    print(stacked.shape)
    

    # Fill with adjacent slices
    for i in range(1, D-1):   # skip first and last slice
        stacked[:, :, i-1, 0] = data[:, :, i-1]  # previous slice
        stacked[:, :, i-1, 1] = data[:, :, i]    # current slice
        stacked[:, :, i-1, 2] = data[:, :, i+1]  # next slice

    print("New shape:", stacked.shape)  # (255, 255, 37, 3)

    # Save as new NIfTI
    new_img = nib.Nifti1Image(stacked, nii.affine, nii.header)
    out_path = os.path.join(out_path_root, f"{uid}", f"{uid}.nii.gz")
    nib.save(new_img, out_path)



for uid in os.listdir(root_dir):
    mask_path = os.path.join(root_dir, uid, f"{uid}_space-T2S_CMB.nii.gz")

    # Load NIfTI
    mask = nib.load(mask_path)
    mask = mask.get_fdata()   # shape: (255, 255, 39)
    
    H, W, D = mask.shape
    mask_new = np.zeros((H, W, D-2), dtype=data.dtype)
    print(mask.shape)

    # Fill with adjacent slices
    for i in range(1, D-1):   # skip first and last slice
        mask_new[:, :, i-1] = mask[:, :, i]    # current slice

    print("New shape:", mask_new.shape)  # (255, 255, 37, 3)

    # Save as new NIfTI
    mask_new = nib.Nifti1Image(mask_new, nii.affine, nii.header)
    out_path = os.path.join(out_path_root, f"{uid}", f"{uid}_space-T2S_CMB.nii.gz")
    nib.save(mask_new, out_path)