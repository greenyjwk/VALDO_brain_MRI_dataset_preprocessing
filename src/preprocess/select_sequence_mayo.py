import os
import re
import glob
import shutil

def select_sequence_mayo(sequence, config):
    sequence = re.sub(r'\s+', '_', sequence)
    root_path = f"/media/Datacenter_storage/Ji/{sequence}/extracted-images"
    output_dir = os.path.join(config["mayo_input_output_src"])

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for uid, subdir in enumerate(os.listdir(root_path)):
        uid = str(uid)
        if subdir == ".DS_Store":
            continue
        subdir_path = os.path.join(root_path, subdir)
        nifti_files = glob.glob(os.path.join(subdir_path, '**', '*.nii.gz'), recursive=True)
        if nifti_files:
            img = nifti_files[0]  # Assuming there is only one NIfTI file
            mrn = img.split('/')[-1].split('_')[0]
            mrn_path = os.path.join(output_dir, mrn)
            if not os.path.exists(mrn_path):            
                os.makedirs(mrn_path)
            print(img)
            
            print(mrn)
            shutil.copy(img, os.path.join(mrn_path, f"{sequence}_{mrn}.nii.gz"))
        else:
            print(f"No NIfTI file found in {subdir_path}")
        
def main():
    sequence = '3D_SAG_T1_MPRAGE_1MM'
    dataset = 'mayo'
    if dataset == 'mayo':
        select_sequence_mayo(sequence)
    
if __name__ == "__main__":
    main()