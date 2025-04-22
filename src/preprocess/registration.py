import sys
import shutil
import os
import ants
import json
import re
import numpy as np

def registration_runner(reference_seq, input_root_path, output_root_path, config):
    print("Mayo Registration")
    reference_seq = re.sub(r'\s+', '_', reference_seq)

    if not os.path.exists(output_root_path):
        os.mkdir(output_root_path)
    
    subfolders = os.listdir(input_root_path)

    for uid in subfolders:
        print(uid)
        if uid == ".DS_Store":
            continue

        # Find the file that starts with reference_seq
        reference_file = None
        moving_files = []
        for file in os.listdir(os.path.join(input_root_path, uid)):
            if file.startswith(reference_seq):
                reference_file = file
            else:
                moving_files.append(file)

        if reference_file is None or len(moving_files) < 2:
            print(f"Files not found for subdir: {uid}")
            continue

        reference_path = os.path.join(input_root_path, uid, reference_file)
        # reference_path = fixed
        moving1 = os.path.join(input_root_path, uid, moving_files[0])
        moving2 = os.path.join(input_root_path, uid, moving_files[1])
        
        print("refrence_path ", reference_path)
        print("moving1 ", moving1)
        print("moving2 ", moving2)
    
        fixed = ants.image_read(reference_path)
        moving1 = ants.image_read(moving1)
        moving2 = ants.image_read(moving2)

        moving1 = ants.from_numpy(np.flip(moving1.numpy(), axis=0), spacing=moving1.spacing)
        moving2 = ants.from_numpy(np.flip(moving2.numpy(), axis=0), spacing=moving2.spacing)           

        moving1 = ants.from_numpy(np.flip(moving1.numpy(), axis=0), spacing=moving1.spacing)
        moving2 = ants.from_numpy(np.flip(moving2.numpy(), axis=0), spacing=moving2.spacing) 

        if config["dataset"] == 'mayo':
            if fixed.shape[3] > 1:
                fixed = fixed[:,:,:,config['mayo_TE_frame']]  # Selecting 3rd TE
                print(fixed.shape)

        # creating subdirectory from output directory
        if not os.path.exists(os.path.join(output_root_path, uid)):
            os.mkdir(os.path.join(output_root_path, uid))

        try:
            # registration for T1
            # “SyN”: Symmetric normalization: Affine + deformable transformation, with mutual information as optimization metric.
            registration_T1 = ants.registration(fixed=fixed, moving=moving1, type_of_transform=config["registration_type"])
            aligned_volume_T1 = registration_T1['warpedmovout']   # Since the moving image is warped to the fixed image space
            ants.image_write(aligned_volume_T1, os.path.join(output_root_path, uid, moving_files[0]))

            # registration for T2
            registration_T2 = ants.registration(fixed=fixed, moving=moving2, type_of_transform=config["registration_type"])
            aligned_volume_T2 = registration_T2['warpedmovout'] # Since the moving image is warped to the fixed image space
            ants.image_write(aligned_volume_T2, os.path.join(output_root_path, uid, moving_files[1]))
            
            # copy and paste T2S to the output directory
            shutil.copy(reference_path, os.path.join(output_root_path, uid, reference_file))
        except RuntimeError as e:
            print(f"Registration for T2 failed for {uid} with error: {e}")
            continue
        
def main():
    config_path = '/media/Datacenter_storage/Ji/VALDO_brain_MRI_dataset_preprocessing/configs/config.json'
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    reference_seq = "T2S"
    # output_root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_registered"
    output_root_path = "/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_registered_temp"
    registration_runner(reference_seq, output_root_path)
    
if __name__ == "__main__":
    main()