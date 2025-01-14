import shutil
import os

def select_sequence_valdo(sequence, config):
    root_path = "/mnt/storage/cmb_segmentation_dataset/Task2"
    output_dir = config["valdo_input_output_src"]

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for uid, subdir in enumerate(os.listdir(root_path)):
        uid = str(uid)
        print(subdir)
        if subdir == ".DS_Store":
            continue
        img = os.path.join(root_path, subdir, subdir + f"_space-T2S_desc-masked_{sequence}.nii.gz")

        # copy and paste T2S to the output directory
        subdir_path = os.path.join(output_dir, subdir)
        if not os.path.exists(subdir_path):            
            os.makedirs(subdir_path)
        # shutil.copy(img, os.path.join(uid_path, f"{sequence}_{uid}_" + subdir + f"_space-T2S_desc-masked_{sequence}.nii.gz"))
        shutil.copy(img, os.path.join(output_dir, subdir, f"{sequence}_{subdir}.nii.gz"))
        
def main():
    sequence = 'T1'
    dataset = 'valdo'
    if dataset == 'valdo':
        select_sequence_valdo(sequence)
    
if __name__ == "__main__":
    main()