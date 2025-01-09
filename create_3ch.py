import nibabel as nib
import numpy as np
import shutil
import os
import ants

root_path = "/mnt/storage/ji/VALDO_preprocessing/bias-field-correction"
output_dir = "/mnt/storage/ji/VALDO_preprocessing/final"

if not os.path.exists(output_dir):
    os.mkdir(output_dir)

for subdir in os.listdir(root_path):
    print(subdir)
    T1 = os.path.join(root_path, subdir, subdir + "_space-T2S_desc-masked_T1.nii.gz")
    T2 = os.path.join(root_path, subdir, subdir + "_space-T2S_desc-masked_T2.nii.gz")
    T2S = os.path.join(root_path, subdir, subdir + "_space-T2S_desc-masked_T2S.nii.gz")
   
    # creating subdirecty in output directory
    if not os.path.exists(os.path.join(output_dir, subdir)):
        os.mkdir(os.path.join(output_dir, subdir))

    # Load the three NIfTI files
    nii1 = nib.load(T1)
    nii2 = nib.load(T2)
    nii3 = nib.load(T2S)

    # Extract data arrays
    data1 = nii1.get_fdata()
    data2 = nii2.get_fdata()
    data3 = nii3.get_fdata()

    # Ensure all arrays have the same shape
    if not (data1.shape == data2.shape == data3.shape):
        raise ValueError("The NIfTI files must have the same dimensions.")

    # Stack the arrays along a new 4th dimension (channel dimension)
    combined_data = np.stack([data1, data2, data3], axis=-1)

    # Create a new NIfTI image
    combined_nii = nib.Nifti1Image(combined_data, affine=nii1.affine)

    # Save the combined image
    output_file = os.path.join(output_dir, subdir, subdir + ".nii.gz")
    nib.save(combined_nii, output_file)

    print(f"Combined NIfTI file saved as {output_file}")
