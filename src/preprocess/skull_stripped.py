# import os
# import subprocess

# def skull_stripped_runner(root_path, output_root_path):
#     '''
#     Please run the following commands in the terminal

#     FREESURFER_HOME=/mnt/storage/ji/freesurfer
#     source $FREESURFER_HOME/SetUpFreeSurfer.sh
#     or
#     FREESURFER_HOME=/media/Datacenter_storage/Ji/freesurfer
#     source $FREESURFER_HOME/SetUpFreeSurfer.sh
#     '''

#     if not os.path.exists(output_root_path):
#         os.mkdir(output_root_path)
    
#     for uid in os.listdir(root_path):
#         if uid == ".DS_Store":
#             continue

#         if not os.path.exists(os.path.join(output_root_path, uid)):
#                 os.mkdir(os.path.join(output_root_path, uid))

#         for file in os.listdir(os.path.join(root_path, uid)):
#             file_path = os.path.join(os.path.join(root_path, uid), file)
#             output_file_path = os.path.join(output_root_path, uid, file)
#             command = ['mri_synthstrip', '-i', file_path, '-o', output_file_path, '--norm-img', '0']
#             try:
#                 result = subprocess.run(command, check=True, capture_output=True, text=True)
#                 print("Output:", result.stdout)
#             except subprocess.CalledProcessError as e:
#                 print("Error:", e.stderr)
            
# def main():
#     root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_registered"
#     output_root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_skull_stripped"
#     skull_stripped_runner(root_path, output_root_path)
    
# if __name__ == "__main__":
#     main()



import os
import subprocess
import nibabel as nib
import numpy as np

def skull_stripped_runner(root_path, output_root_path):
    if not os.path.exists(output_root_path):
        os.mkdir(output_root_path)

    for uid in os.listdir(root_path):
        if uid == ".DS_Store":
            continue
            
        if not os.path.exists(os.path.join(output_root_path, uid)):
            os.mkdir(os.path.join(output_root_path, uid))
            
        for file in os.listdir(os.path.join(root_path, uid)):
            file_path = os.path.join(os.path.join(root_path, uid), file)
            output_file_path = os.path.join(output_root_path, uid, file)
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
                
                # Apply mask to original image
                final_data = orig_img.get_fdata() * mask
                
                # Save with original intensities
                final_nii = nib.Nifti1Image(final_data, orig_img.affine, orig_img.header)
                nib.save(final_nii, output_file_path)
                
                # Clean up temp file
                os.remove(temp_output)
                
                print(f"Processed: {file}")
                
            except subprocess.CalledProcessError as e:
                print("Error:", e.stderr)

def main():
    root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_registered"
    output_root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_skull_stripped"
    skull_stripped_runner(root_path, output_root_path)

if __name__ == "__main__":
    main()