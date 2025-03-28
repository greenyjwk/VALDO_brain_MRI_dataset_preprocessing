import os
import subprocess

def skull_stripped_runner(root_path, output_root_path):
    '''
    Please run the following commands in the terminal

    FREESURFER_HOME=/mnt/storage/ji/freesurfer
    source $FREESURFER_HOME/SetUpFreeSurfer.sh
    or
    FREESURFER_HOME=/media/Datacenter_storage/Ji/freesurfer
    source $FREESURFER_HOME/SetUpFreeSurfer.sh
    '''

    if not os.path.exists(output_root_path):
        os.mkdir(output_root_path)

    for uid in os.listdir(root_path):
        if uid == ".DS_Store":
            continue

        if not os.path.exists(os.path.join(output_root_path, uid)):
                os.mkdir(os.path.join(output_root_path, uid))

        for file in os.listdir(os.path.join(root_path, uid)):
            if file.endswith("CMB.nii.gz"):
                continue
            file_path = os.path.join(os.path.join(root_path, uid), file)
            output_file_path = os.path.join(output_root_path, uid, file)
            command = ['mri_synthstrip', '-i', file_path, '-o', output_file_path]
            try:
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                print("Output:", result.stdout)
            except subprocess.CalledProcessError as e:
                print("Error:", e.stderr)

def main():
    root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_registered"
    output_root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_skull_stripped"
    skull_stripped_runner(root_path, output_root_path)
    
if __name__ == "__main__":
    main()