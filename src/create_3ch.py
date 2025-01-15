import nibabel as nib
import numpy as np
import os
import glob

# VALDO
# root_path = "/mnt/storage/Ji/brain_mri_valdo_mayo/bias-field-correction"
# output_dir = "/mnt/storage/ji/VALDO_preprocessing/final"

# Mayo
root_path = "/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/bias-field-correction"
output_dir = "/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_stacked"



if not os.path.exists(output_dir):
    os.mkdir(output_dir)

for uid in os.listdir(root_path):
    print(uid)
    subdir_path = os.path.join(root_path, uid)
    
    # Search for NIfTI files in the subdirectory
    nifti_files = glob.glob(os.path.join(subdir_path, "*.nii.gz"))
    
    if len(nifti_files) != 3:
        print(f"Expected 3 NIfTI files in {subdir_path}, but found {len(nifti_files)}")
        continue

    # Sort the files to ensure consistent order (optional)
    nifti_files.sort()

    # creating subdirectory in output directory
    if not os.path.exists(os.path.join(output_dir, uid)):
        os.mkdir(os.path.join(output_dir, uid))

    # Load the three NIfTI files
    nii1 = nib.load(nifti_files[0])
    nii2 = nib.load(nifti_files[1])
    nii3 = nib.load(nifti_files[2])

    # Extract data arrays
    data1 = nii1.get_fdata()
    data2 = nii2.get_fdata()
    data3 = nii3.get_fdata()

    # Stack the arrays along a new 4th dimension (channel dimension)
    combined_data = np.stack([data1, data2, data3], axis=-1)

    # Create a new NIfTI image
    combined_nii = nib.Nifti1Image(combined_data, affine=nii1.affine)

    # Save the combined image
    mrn = nifti_files.split('_')[-1]
    output_file = os.path.join(output_dir, uid, uid + '_' + mrn)
    nib.save(combined_nii, output_file)