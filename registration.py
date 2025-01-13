import shutil
import os
import ants

def registration():
    root_path = "/mnt/storage/cmb_segmentation_dataset/Task2"
    output_dir = "/mnt/storage/ji/VALDO_preprocessing/registered"

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    for subdir in os.listdir(root_path):
        print(subdir)
        if subdir == ".DS_Store":
            continue
        T1 = os.path.join(root_path, subdir, subdir + "_space-T2S_desc-masked_T1.nii.gz")
        T2 = os.path.join(root_path, subdir, subdir + "_space-T2S_desc-masked_T2.nii.gz")
        T2S = os.path.join(root_path, subdir, subdir + "_space-T2S_desc-masked_T2S.nii.gz")
    
        fixed = ants.image_read(T2S)
        moving_T1 = ants.image_read(T1)
        moving_T2 = ants.image_read(T2)

        # creating subdirecty from output directory
        if not os.path.exists(os.path.join(output_dir, subdir)):
            os.mkdir(os.path.join(output_dir, subdir))

        # registration for T1
        registration_T1 = ants.registration(fixed=fixed, moving=moving_T1, type_of_transform="SyN")
        aligned_volume_T1 = registration_T1['warpedmovout']
        ants.image_write(aligned_volume_T1, os.path.join(output_dir, subdir, subdir + "_space-T2S_desc-masked_T1.nii.gz"))
        
        # registration for T2
        registration_T2 = ants.registration(fixed=fixed, moving=moving_T2, type_of_transform="SyN")
        aligned_volume_T2 = registration_T2['warpedmovout']
        ants.image_write(aligned_volume_T2, os.path.join(output_dir, subdir, subdir + "_space-T2S_desc-masked_T2.nii.gz"))

        # copy and paste T2S to the output directory
        shutil.copy(T2S, os.path.join(output_dir, subdir, subdir + "_space-T2S_desc-masked_T2S.nii.gz"))
        
def main():
    registration()
    
if __name__ == "__main__":
    main()