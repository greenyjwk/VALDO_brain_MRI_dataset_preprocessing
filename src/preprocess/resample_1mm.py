# import os
# import sys
# import numpy as np
# import SimpleITK as sitk

# def resample_image(image, new_spacing=[1.0, 1.0, 1.0]):
#     """
#     Resample an image to a given voxel spacing.

#     Parameters:
#         image (SimpleITK.Image): The input NIfTI image.
#         new_spacing (list): The desired voxel spacing (default: 1mm x 1mm x 1mm).

#     Returns:
#         SimpleITK.Image: The resampled image.
#     """
#     resample = sitk.ResampleImageFilter()
    
#     # Get original spacing and size
#     original_spacing = np.array(image.GetSpacing())
#     original_size = np.array(image.GetSize())
    
#     print("original_spacing: ", original_spacing)
#     print("original_size: ", original_size)

#     # Compute new size to preserve field of view (FOV)
#     new_size = np.round(original_size * (original_spacing / np.array(new_spacing))).astype(int).tolist()
#     print("new_size: ", new_size)
    
#     # Configure resampling parameters
#     resample.SetOutputSpacing(new_spacing)
#     resample.SetSize(new_size)
#     resample.SetOutputOrigin(image.GetOrigin())
#     resample.SetOutputDirection(image.GetDirection())
#     resample.SetInterpolator(sitk.sitkLinear)  # Linear interpolation (can use BSpline for smoother results)

#     return resample.Execute(image)

# def resample_nifti_in_directory(input_root, output_root):
#     """
#     Iterates through each subdirectory in `input_root`, finds three NIfTI files, and resamples them.

#     Parameters:
#         input_root (str): Path to the input directory containing subdirectories with NIfTI files.
#         output_root (str): Path to the output directory where resampled files will be saved.
#     """
#     if not os.path.exists(output_root):
#         os.makedirs(output_root)

#     subdirectories = [d for d in os.listdir(input_root) if os.path.isdir(os.path.join(input_root, d))]

#     for subdir in subdirectories:
#         input_subdir_path = os.path.join(input_root, subdir)
#         print("mrn: ", input_subdir_path)
#         output_subdir_path = os.path.join(output_root, subdir)

#         if not os.path.exists(output_subdir_path):
#             os.makedirs(output_subdir_path)

#         # Find all .nii or .nii.gz files
#         nifti_files = [f for f in os.listdir(input_subdir_path) if f.endswith('.nii') or f.endswith('.nii.gz')]
        
#         if len(nifti_files) != 4:
#             print(f"Skipping {subdir} (expected 3 NIfTI files, found {len(nifti_files)})")
#             continue

#         for nifti_file in nifti_files:
#             input_file_path = os.path.join(input_subdir_path, nifti_file)
#             output_file_path = os.path.join(output_subdir_path, nifti_file)

#             # Read the NIfTI image
#             image = sitk.ReadImage(input_file_path)

#             # Resample to 1mm x 1mm x 1mm
#             resampled_image = resample_image(image)

#             # Save the resampled image
#             sitk.WriteImage(resampled_image, output_file_path)

#         print(f"Resampled images saved in {output_subdir_path}")

# # Example usage:
# input_root_path = "/mnt/storage/cmb_segmentation_dataset/Task2"  # Change this to your actual input directory
# output_root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_1mm"  # Output directory where resampled images will be stored

# resample_nifti_in_directory(input_root_path, output_root_path)

import os
import sys
import numpy as np
import SimpleITK as sitk

def resample_image(image, new_spacing=[1.0, 1.0, 1.0], is_mask=False):
    """
    Resample an image to a given voxel spacing.

    Parameters:
        image (SimpleITK.Image): The input NIfTI image.
        new_spacing (list): The desired voxel spacing (default: 1mm x 1mm x 1mm).
        is_mask (bool): Whether the image is a binary mask (default: False).

    Returns:
        SimpleITK.Image: The resampled image.
    """
    resample = sitk.ResampleImageFilter()
    
    # Get original spacing and size
    original_spacing = np.array(image.GetSpacing())
    original_size = np.array(image.GetSize())
    
    print("original_spacing: ", original_spacing)
    print("original_size: ", original_size)

    # Compute new size to preserve field of view (FOV)
    new_size = np.round(original_size * (original_spacing / np.array(new_spacing))).astype(int).tolist()
    print("new_size: ", new_size)
    
    # Configure resampling parameters
    resample.SetOutputSpacing(new_spacing)
    resample.SetSize(new_size)
    resample.SetOutputOrigin(image.GetOrigin())
    resample.SetOutputDirection(image.GetDirection())
    
    # Use nearest neighbor interpolation for masks to preserve binary values
    if is_mask:
        resample.SetInterpolator(sitk.sitkNearestNeighbor)
    else:
        resample.SetInterpolator(sitk.sitkLinear)  # Linear interpolation for regular images

    return resample.Execute(image)

def resample_nifti_in_directory(input_root, output_root):
    """
    Iterates through each subdirectory in `input_root`, finds NIfTI files, and resamples them.

    Parameters:
        input_root (str): Path to the input directory containing subdirectories with NIfTI files.
        output_root (str): Path to the output directory where resampled files will be saved.
    """
    if not os.path.exists(output_root):
        os.makedirs(output_root)

    subdirectories = [d for d in os.listdir(input_root) if os.path.isdir(os.path.join(input_root, d))]

    for subdir in subdirectories:
        input_subdir_path = os.path.join(input_root, subdir)
        print("Processing subject:", subdir)
        output_subdir_path = os.path.join(output_root, subdir)

        if not os.path.exists(output_subdir_path):
            os.makedirs(output_subdir_path)

        # Find all .nii or .nii.gz files
        nifti_files = [f for f in os.listdir(input_subdir_path) if f.endswith('.nii') or f.endswith('.nii.gz')]

        for nifti_file in nifti_files:
            input_file_path = os.path.join(input_subdir_path, nifti_file)
            output_file_path = os.path.join(output_subdir_path, nifti_file)

            # Check if the file is a mask based on filename
            is_mask = '_CMB' in nifti_file

            # Read the NIfTI image
            image = sitk.ReadImage(input_file_path)

            # Resample to 1mm x 1mm x 1mm
            resampled_image = resample_image(image, is_mask=is_mask)

            # Save the resampled image
            sitk.WriteImage(resampled_image, output_file_path)
            print(f"Processed {nifti_file} {'(mask)' if is_mask else '(image)'}")

        print(f"Resampled images saved in {output_subdir_path}")

# Example usage:
if __name__ == "__main__":
    input_root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/bias_field_correction"
    output_root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/bias_field_correction_resampled_1mm"
    resample_nifti_in_directory(input_root_path, output_root_path)