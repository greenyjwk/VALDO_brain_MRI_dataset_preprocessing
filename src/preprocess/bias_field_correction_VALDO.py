import sys
import os
import numpy as np
from pathlib import Path
import ants  # This is antspyx

def bias_field_correction(src_path, dst_path):
    print("N4ITK on: ", src_path)
    try:
        # Load the NIfTI file with ANTsPy
        img = ants.image_read(str(src_path))
        print(f"Image shape: {img.shape}")
        
        # Check if it's 4D and extract the 3rd channel (index 2)
        if len(img.shape) == 4:
            print("4D image detected, extracting 3rd channel (index 2)")
            # Extract 3rd channel - ANTsPy uses 0-based indexing
            img_3rd = ants.slice_image(img, axis=3, idx=2)
            print(f"Extracted 3rd channel shape: {img_3rd.shape}")
            
            # Apply N4 bias field correction
            corrected_img = ants.n4_bias_field_correction(
                img_3rd,
                convergence={'iters': [100, 100, 60, 40], 'tol': 1e-4},
                shrink_factor=3,
                spline_param=300
            )
        else:
            print(f"Image is not 4D (shape: {img.shape}), applying bias correction directly")
            # Apply N4 bias field correction directly
            corrected_img = ants.n4_bias_field_correction(
                img,
                convergence={'iters': [100, 100, 60, 40], 'tol': 1e-4},
                shrink_factor=3,
                spline_param=300
            )
        
        # Save the corrected image
        ants.image_write(corrected_img, str(dst_path))
        print(f"Successfully processed: {dst_path}")
        
    except Exception as e:
        print(f"\tFailed on: {src_path}, Error: {e}")
    return

# Rest of your functions remain the same...
def bias_field_correction_runner(root_path, output_root_path, target_sequence):
    if not os.path.exists(output_root_path):
        os.makedirs(output_root_path, exist_ok=True)
    
    for uid in os.listdir(root_path):
        if uid == ".DS_Store":
            continue

        output_uid_path = os.path.join(output_root_path, uid)
        if not os.path.exists(output_uid_path):
            os.makedirs(output_uid_path, exist_ok=True)
        uid_path = os.path.join(root_path, uid)
                
        for file in os.listdir(uid_path):
            if file.endswith(f'{target_sequence}.nii.gz'):
                file_path = os.path.join(uid_path, file)
                output_file_path = os.path.join(output_uid_path, file)
                print("file_path: ", file_path)
                print("output_file_path: ", output_file_path)
                bias_field_correction(file_path, output_file_path)
            else:
                print(f"Skipping file: {file}")
        print()

def main():
    target_sequence = "T2"
    root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/skull_stripped"
    output_root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/bias_field_correction"
    
    bias_field_correction_runner(root_path, output_root_path, target_sequence)
    
if __name__ == "__main__":
    main()