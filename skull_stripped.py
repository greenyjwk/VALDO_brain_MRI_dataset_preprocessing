import os
import subprocess

def skull_stripped_runner():
    '''
    Please run the following commands in the terminal

    FREESURFER_HOME=/mnt/storage/ji/freesurfer
    source $FREESURFER_HOME/SetUpFreeSurfer.sh
    '''

    root_path = "/mnt/storage/ji/VALDO_preprocessing/registered"
    output_dir = "/mnt/storage/ji/VALDO_preprocessing/skull-stripped"

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    for subdir in os.listdir(root_path):
        print(subdir)
        if subdir == ".DS_Store":
            continue
        T1 = os.path.join(root_path, subdir, subdir + "_space-T2S_desc-masked_T1.nii.gz")
        T2 = os.path.join(root_path, subdir, subdir + "_space-T2S_desc-masked_T2.nii.gz")
        T2S = os.path.join(root_path, subdir, subdir + "_space-T2S_desc-masked_T2S.nii.gz")

        # creating subdirecty from output directory
        if not os.path.exists(os.path.join(output_dir, subdir)):
            os.mkdir(os.path.join(output_dir, subdir))

        # skull_stripping for T1
        command = ['mri_synthstrip', '-i', T1, '-o', os.path.join(output_dir, subdir, subdir+"_space-T2S_desc-masked_T1.nii.gz")]
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print("Output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error:", e.stderr)
        

        # skull_stripping for T2
        command = ['mri_synthstrip', '-i', T2, '-o', os.path.join(output_dir, subdir, subdir+"_space-T2S_desc-masked_T2.nii.gz")]
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print("Output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error:", e.stderr)
        
        
        # skull_stripping for T2S
        command = ['mri_synthstrip', '-i', T2S, '-o', os.path.join(output_dir, subdir, subdir+"_space-T2S_desc-masked_T2S.nii.gz")]
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print("Output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error:", e.stderr)
            
def main():
    skull_stripped()
    
if __name__ == "__main__":
    main()