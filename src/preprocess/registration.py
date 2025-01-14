import shutil
import os
import ants
import re

def registration_runner(reference_seq, input_root_path, output_root_path, config):
    
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

        fixed = os.path.join(input_root_path, uid, reference_file)
        reference_path = fixed
        moving1 = os.path.join(input_root_path, uid, moving_files[0])
        moving2 = os.path.join(input_root_path, uid, moving_files[1])
    
        fixed = ants.image_read(fixed)
        moving1 = ants.image_read(moving1)
        moving2 = ants.image_read(moving2)

        if fixed.shape[3] > 1:
            fixed = fixed[:,:,:,config['mayo_TE_frame']]  # Selecting 3rd TE
            print(fixed.shape)

        # creating subdirectory from output directory
        if not os.path.exists(os.path.join(output_root_path, uid)):
            os.mkdir(os.path.join(output_root_path, uid))

        # registration for T1
        registration_1 = ants.registration(fixed=fixed, moving=moving1, type_of_transform="SyN")
        aligned_volume_1 = registration_1['warpedmovout']
        ants.image_write(aligned_volume_1, os.path.join(output_root_path, uid, moving_files[0]))
        
        # registration for T2
        registration_T2 = ants.registration(fixed=fixed, moving=moving2, type_of_transform="SyN")
        aligned_volume_T2 = registration_T2['warpedmovout']
        ants.image_write(aligned_volume_T2, os.path.join(output_root_path, uid, moving_files[1]))
        
        print(reference_file)
        # copy and paste T2S to the output directory
        shutil.copy(reference_path, os.path.join(output_root_path, uid, reference_file))
        
def main():
    reference_seq = "T2S"
    output_root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_registered"
    registration_runner(reference_seq, output_root_path)
    
if __name__ == "__main__":
    main()