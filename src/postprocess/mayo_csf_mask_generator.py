import subprocess
import os

root_path = "/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_bias_field_correction_resampled_0325_TEMP"
sequence = "3D_SAG_T1_MPRAGE_1MM"

for file in os.listdir(root_path):
    file_path = os.path.join(root_path, file, f"{sequence}_{file}.nii.gz")
    print(file_path)

    output_dir = f"/media/Datacenter_storage/Ji/csf_segment/{file}/T1"

    if not os.path.exists(output_dir):
        print(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir)
        print("Directory created successfully.")
    else:
        print("Output directory already exists.")

    command = [
        "fast", 
        "-t", "1",
        "-n", "3", 
        "-g", 
        "-o", output_dir,
        f"{file_path}"
    ]

    try:
        print("Running fast command...")
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Command completed successfully.")
        print("Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print("Error output:", e.stderr)