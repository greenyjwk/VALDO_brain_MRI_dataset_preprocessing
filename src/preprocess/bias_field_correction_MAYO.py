# import os
# from pathlib import Path
# from nipype.interfaces.ants.segmentation import N4BiasFieldCorrection

# def unwarp_bias_field_correction(arg, **kwarg):
#     return bias_field_correction(*arg, **kwarg)

# def bias_field_correction(src_path, dst_path):
#     print("N4ITK on: ", src_path)
#     try:
#         n4 = N4BiasFieldCorrection()
#         n4.inputs.input_image = str(src_path)
#         n4.inputs.output_image = str(dst_path)
#         n4.inputs.dimension = 3
#         n4.inputs.n_iterations = [100, 100, 60, 40]
#         n4.inputs.shrink_factor = 3
#         n4.inputs.convergence_threshold = 1e-4
#         n4.inputs.bspline_fitting_distance = 300
#         n4.run()
#     except RuntimeError:
#         print("\tFailed on: ", src_path)
#     return

# def bias_field_correction_runner(root_path, output_root_path):
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
#             bias_field_correction(file_path, output_file_path)

# def main():
#     # root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_skull_stripped"
#     # output_root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_bias_field_correction"
    
#     root_path = "/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_skull_stripped_resampled_0325"
#     output_root_path = "/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_bias_field_correction_resampled_0325_t2s"

#     bias_field_correction_runner(root_path, output_root_path)
    
# if __name__ == "__main__":
#     main()


# import sys
# import os
# import nibabel as nib
# import numpy as np
# from pathlib import Path
# import ants  # This is antspyx
# from nipype.interfaces.ants.segmentation import N4BiasFieldCorrection

# def unwarp_bias_field_correction(arg, **kwarg):
#     return bias_field_correction(*arg, **kwarg)

# def bias_field_correction(src_path, dst_path):
#     print("N4ITK on: ", src_path)
#     try:
#         # Load the NIfTI file
#         img = nib.load(src_path)
#         img_data = img.get_fdata()
#         print(img_data.shape)
        
#         # Check if it's 4D and extract the 3rd channel (index 2)
#         if len(img_data.shape) == 4:
#             # Extract 3rd channel (index 2)
#             img_data_3TE_channel = img_data[:, :, :, 2]
            
#             # Create new NIfTI image with only the 3rd channel
#             new_img = nib.Nifti1Image(img_data_3TE_channel, img.affine, img.header)
            
#             # Create temporary file for the extracted channel
#             temp_path = str(dst_path).replace('.nii.gz', '_temp_3rd_channel.nii.gz')
#             nib.save(new_img, temp_path)
#             print(f"Saved temporary 3rd channel to: {temp_path}")
            
#             # Apply N4 bias field correction to the extracted channel
#             n4 = N4BiasFieldCorrection()
#             n4.inputs.input_image = temp_path
#             n4.inputs.output_image = str(dst_path)
#             n4.inputs.dimension = 3
#             n4.inputs.n_iterations = [100, 100, 60, 40]
#             n4.inputs.shrink_factor = 3
#             n4.inputs.convergence_threshold = 1e-4
#             n4.inputs.bspline_fitting_distance = 300
#             n4.run()
            
#             # Clean up temporary file
#             if os.path.exists(temp_path):
#                 os.remove(temp_path)
#                 print(f"Removed temporary file: {temp_path}")
            
#         else:
#             print(f"Image is not 4D (shape: {img_data.shape}), applying bias correction directly")
#             # If not 4D, apply bias correction directly
#             print(src_path)
#             print(dst_path)
#             # sys.exit()
#             n4 = N4BiasFieldCorrection()
#             n4.inputs.input_image = str(src_path)
#             n4.inputs.output_image = str(dst_path)
#             n4.inputs.dimension = 3
#             n4.inputs.n_iterations = [100, 100, 60, 40]
#             n4.inputs.shrink_factor = 3
#             n4.inputs.convergence_threshold = 1e-4
#             n4.inputs.bspline_fitting_distance = 300
#             n4.run()
            
#         print(f"Successfully processed: {dst_path}")
            
#     except Exception as e:
#         print(f"\tFailed on: {src_path}, Error: {e}")
#     return

# def bias_field_correction_runner(root_path, output_root_path, target_sequence):
#     if not os.path.exists(output_root_path):
#         os.makedirs(output_root_path, exist_ok=True)
    
#     for uid in os.listdir(root_path):
#         if uid == ".DS_Store":
#             continue

#         output_uid_path = os.path.join(output_root_path, uid)
#         if not os.path.exists(output_uid_path):
#             os.makedirs(output_uid_path, exist_ok=True)
#         uid_path = os.path.join(root_path, uid)
                
#         for file in os.listdir(uid_path):
#             if file.startswith(target_sequence) and file.endswith('.nii.gz'):
#                 print(f"Processing file: {file}")
#                 uid = file.split('_')[-1].split('.')[0]
#                 file_path = os.path.join(uid_path, file)
#                 output_file_path = os.path.join(output_uid_path, f"{target_sequence}_{uid}.nii.gz")
#                 bias_field_correction(file_path, output_file_path)
#             else:
#                 print(f"  Skipping file: {file}")

# def main():
#     # target_sequence = "Axial_3TE_T2_STAR"
#     target_sequence = "3D_SAG_T1_MPRAGE_1MM"
#     root_path = "/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_skull_stripped_resampled_0325"
#     output_root_path = f"/media/Datacenter_storage/PublicDatasets/MAYO_cerebral_microbleeds/mayo_bias_field_correction"
#     bias_field_correction_runner(root_path, output_root_path, target_sequence)
    
# if __name__ == "__main__":
#     main()



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
            if file.startswith(target_sequence) and file.endswith('.nii.gz'):
                print(f"Processing file: {file}")
                uid_from_file = file.split('_')[-1].split('.')[0]
                file_path = os.path.join(uid_path, file)
                output_file_path = os.path.join(output_uid_path, f"{target_sequence}_{uid_from_file}.nii.gz")
                bias_field_correction(file_path, output_file_path)
            else:
                print(f"  Skipping file: {file}")

        print()
        print()

def main():
    target_sequence = "Axial_3TE_T2_STAR"
    root_path = "/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_skull_stripped_resampled_0325"
    output_root_path = "/media/Datacenter_storage/PublicDatasets/MAYO_cerebral_microbleeds/mayo_bias_field_correction"
    
    bias_field_correction_runner(root_path, output_root_path, target_sequence)
    
if __name__ == "__main__":
    main()