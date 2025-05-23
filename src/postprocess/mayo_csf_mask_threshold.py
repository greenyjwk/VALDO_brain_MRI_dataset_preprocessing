import subprocess
import os

task = "val"
root_path = f"/mnt/storage/ji/csf_segment_{task}"

for file in os.listdir(root_path):
    file_path = os.path.join(root_path, file, f"T1_pve_0.nii.gz")
    print(file_path)

    # output_dir = f"/media/Datacenter_storage/Ji/csf_segment/{file}"
    output_dir = f"/mnt/storage/ji/csf_segment_threshold_{task}/{file}/"

    if not os.path.exists(output_dir):
        print(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir)
        print("Directory created successfully.")
    else:
        print("Output directory already exists.")

    command = [
        "fslmaths",
        f"{root_path}/{file}/T1_pve_0.nii.gz",
        "-thr", "0.9",
        "-bin", f"{output_dir}/T1_seg_0.nii.gz"
    ]

    try:
        print("Running fast command...")
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Command completed successfully.")
        print("Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print("Error output:", e.stderr)
        
        

'''    
export FSLDIR=/home/ji/fsl
source $FSLDIR/etc/fslconf/fsl.sh
export PATH=$FSLDIR/bin:$PATH
'''