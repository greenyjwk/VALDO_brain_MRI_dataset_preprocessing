import os
import re
import json
import SimpleITK as sitk
import sys
import shutil

def resample_runner(reference_seq, input_root_path, output_root_path, config):
    
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

        output_root_dir = os.path.join(output_root_path, uid)
        if not os.path.exists(output_root_dir):
            os.makedirs(output_root_dir)

        fixed_path = os.path.join(input_root_path, uid, reference_file)
        moving1_path = os.path.join(input_root_path, uid, moving_files[0])
        moving2_path = os.path.join(input_root_path, uid, moving_files[1])

        output_resampled_A = os.path.join(output_root_dir, moving_files[0])
        output_resampled_B = os.path.join(output_root_dir, moving_files[1])
        otuput_fixed = os.path.join(output_root_dir, reference_file)

        # Load NIfTI files
        moving1 = sitk.ReadImage(moving1_path)  # NIfTI file A
        moving2 = sitk.ReadImage(moving2_path)  # NIfTI file A
        fixed = sitk.ReadImage(fixed_path)  # NIfTI file B (target dimensions)
  
        if fixed.GetDimension() == 4:
            fixed = fixed[:,:,:,config['mayo_TE_frame']]  # Selecting 3rd TE
            

        # Set up the resampling filter
        resample = sitk.ResampleImageFilter()
        resample.SetOutputSpacing(fixed.GetSpacing())       # Match spacing of B
        resample.SetSize(fixed.GetSize())                   # Match size of B
        resample.SetOutputOrigin(fixed.GetOrigin())         # Match origin of B
        resample.SetOutputDirection(fixed.GetDirection())   # Match direction of B
        resample.SetInterpolator(sitk.sitkLinear)             # Use linear interpolation (or other types if needed)


        # Resample image A and B
        resampled_A = resample.Execute(moving1)
        sitk.WriteImage(resampled_A, output_resampled_A)

        resampled_B = resample.Execute(moving2)
        sitk.WriteImage(resampled_B, output_resampled_B)
        
        # copy and paste T2S to the output directory
        shutil.copy(fixed_path, otuput_fixed)

def main():
    config_dir = "/media/Datacenter_storage/Ji/VALDO_brain_MRI_dataset_preprocessing/configs"
    config_path = os.path.join(config_dir, 'config.json')
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    dataset = config['dataset']

    if dataset == 'mayo':
        reference_seq = config["mayo_registration_reference"]
        input_root_path = config["mayo_input_output_src"]
        output_root_path_resampled = config["mayo_resample_output"]
        resample_runner(input_root_path, output_root_path_resampled, reference_seq, config)
    
if __name__ == "__main__":
    main()