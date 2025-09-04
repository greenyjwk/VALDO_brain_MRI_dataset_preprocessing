import os
import sys
import shutil
import numpy as np
import SimpleITK as sitk

def resample_image(image, new_spacing=[0.5, 0.5, 3.0], is_mask=False):
    resample = sitk.ResampleImageFilter()
    
    # Get original spacing and size
    original_spacing = np.array(image.GetSpacing())
    original_size = np.array(image.GetSize())
    
    print("original_spacing: ", original_spacing)
    print("original_size: ", original_size)
    new_spacing[-1] = original_spacing[-1]
    print("new_spacing: ", new_spacing)
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
    if not os.path.exists(output_root):
        os.makedirs(output_root)

    subdirectories = [d for d in os.listdir(input_root) if os.path.isdir(os.path.join(input_root, d))]
    
    for subdir in subdirectories:
        input_subdir_path = os.path.join(input_root, subdir)
        output_subdir_path = os.path.join(output_root, subdir)
        if not os.path.exists(output_subdir_path):
            os.makedirs(output_subdir_path)
            
        if subdir.startswith("sub-3"):
            # Find all .nii or .nii.gz files
            nifti_files = [f for f in os.listdir(input_subdir_path) if f.endswith('.nii') or f.endswith('.nii.gz')]

            for nifti_file in nifti_files:
                input_file_path = os.path.join(input_subdir_path, nifti_file)
                output_file_path = os.path.join(output_subdir_path, nifti_file)

                # Check if the file is a mask based on filename
                is_mask = '_CMB' in nifti_file

                # Read the NIfTI image
                image = sitk.ReadImage(input_file_path)

                # Resample to 0.5mm x 0.5mm x 3mm 
                # z-axis doesn't change
                new_spacing = [0.5, 0.5, 3.0]
                resampled_image = resample_image(image, new_spacing, is_mask=is_mask)

                # Save the resampled image
                sitk.WriteImage(resampled_image, output_file_path)
                print(f"Processed {nifti_file} {'(mask)' if is_mask else '(image)'}")
                print()
                print()
            print(f"Resampled images saved in {output_subdir_path}")
        else:
            # print(input_subdir_path)
            print(output_subdir_path)
            if os.path.exists(output_subdir_path):
                shutil.rmtree(output_subdir_path)
            shutil.copytree(input_subdir_path, output_subdir_path)

# Example usage:
if __name__ == "__main__":
    input_root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/bias_field_correction"
    output_root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/bias_field_correction_resampled"
    resample_nifti_in_directory(input_root_path, output_root_path)