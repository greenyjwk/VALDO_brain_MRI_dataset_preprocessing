import os
import subprocess
import nibabel as nib
import numpy as np

def skull_stripped_runner(root_path, output_root_path):
    os.makedirs(output_root_path, exist_ok=True)

    for uid in os.listdir(root_path):
        if uid == ".DS_Store":
            continue
        
        user_output_dir = os.path.join(output_root_path, uid)
        os.makedirs(user_output_dir, exist_ok=True)
        
        for file in os.listdir(os.path.join(root_path, uid)):
            if not file.endswith('.nii.gz'):
                continue

            file_path = os.path.join(root_path, uid, file)
            output_file_path = os.path.join(user_output_dir, file)
            temp_output = output_file_path.replace('.nii.gz', '_temp.nii.gz')
            
            # Run skull stripping
            command = ['mri_synthstrip', '-i', file_path, '-o', temp_output]
            try:
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                
                # Load original and stripped images
                orig_img = nib.load(file_path)
                stripped_img = nib.load(temp_output)
                
                # Create mask from stripped image
                mask = (stripped_img.get_fdata() > 0).astype(float)
                print(np.unique(mask))
                # Apply mask to original image
                final_data = orig_img.get_fdata() * mask
                
                # Save with original intensities
                final_nii = nib.Nifti1Image(final_data, orig_img.affine, orig_img.header)
                nib.save(final_nii, output_file_path)
                
                print(f"Processed: {file}")
                
            except subprocess.CalledProcessError as e:
                print(f"Error processing {file}: {e.stderr}")
            finally:
                if os.path.exists(temp_output):
                    os.remove(temp_output)

def main():
    root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_registered"
    output_root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_skull_stripped"
    skull_stripped_runner(root_path, output_root_path)

if __name__ == "__main__":
    main()
    
'''
Please run the following commands in the terminal

FREESURFER_HOME=/mnt/storage/ji/freesurfer
source $FREESURFER_HOME/SetUpFreeSurfer.sh
or
FREESURFER_HOME=/media/Datacenter_storage/Ji/freesurfer
source $FREESURFER_HOME/SetUpFreeSurfer.sh
'''