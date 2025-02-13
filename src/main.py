import os
import sys
import json
import argparse
import subprocess
from preprocess.registration import registration_runner
from preprocess.skull_stripped import skull_stripped_runner
from preprocess.bias_field_correction import bias_field_correction_runner
from preprocess.select_sequence import select_sequence_valdo
from preprocess.resample import resample_runner

# def setup_freesurfer():
#     # Set the FREESURFER_HOME environment variable
#     os.environ['FREESURFER_HOME'] = '/mnt/storage/ji/freesurfer'
    
#     # Source the SetUpFreeSurfer.sh script
#     setup_script = os.path.join(os.environ['FREESURFER_HOME'], 'SetUpFreeSurfer.sh')
#     command = f"source {setup_script} && echo $FREESURFER_HOME"
    
#     # Run the command in a shell
#     result = subprocess.run(command, shell=True, executable='/bin/bash', capture_output=True, text=True)
    
#     if result.returncode == 0:
#         print("FREESURFER_HOME is set to:", result.stdout.strip())
#     else:
#         print("Error setting up FreeSurfer:", result.stderr)

def main():
    parser = argparse.ArgumentParser(description="Create 3-channel NIfTI images")
    parser.add_argument('--dataset', type=str, choices=['mayo', 'valdo'], default='mayo', required=False)    
    args = parser.parse_args()

    if args.dataset == 'mayo':
        config_path = "/media/Datacenter_storage/Ji/VALDO_brain_MRI_dataset_preprocessing/configs/config.json"
    elif args.dataset == 'valdo':
        config_path = "/mnt/storage/ji/VALDO_brain_MRI_dataset_preprocessing/configs/config.json"
    
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    dataset = config['dataset']
    if dataset == 'valdo':
        input_root_path = config["valdo_input_output_src"]
        reference_seq = config["valdo_registration_reference"]
            
        select_sequence_valdo('T1', config)
        select_sequence_valdo("T2", config)
        select_sequence_valdo('T2S', config)
        
        output_root_path_registered = config["valdo_registration_output"]
        registration_runner(reference_seq, input_root_path, output_root_path_registered, config)
        
        output_root_path_skull_stripped = output_root_path_registered.replace("registered", "skull_stripped")
        skull_stripped_runner(output_root_path_registered, output_root_path_skull_stripped)
        
        output_root_path_bias_field_correction = output_root_path_skull_stripped.replace("skull_stripped", "bias_field_correction")
        bias_field_correction_runner(output_root_path_skull_stripped, output_root_path_bias_field_correction)

    elif dataset == 'mayo':
        input_root_path = config["mayo_input_output_src"]
        reference_seq = config["mayo_registration_reference"]
        T1_seq = config["mayo_t1"]
        T2_seq = config["mayo_t2"]

        # select_sequence_mayo(reference_seq, config)
        # select_sequence_mayo(T1_seq, config)
        # select_sequence_mayo(T2_seq, config)

        output_root_path_resampled = config["mayo_resample_output"]
        # resample_runner(reference_seq, input_root_path, output_root_path_resampled, config)

        output_root_path_registered = config["mayo_registration_output"]
        registration_runner(reference_seq, output_root_path_resampled, output_root_path_registered, config)

        output_root_path_skull_stripped = output_root_path_registered.replace("registered", "skull_stripped")
        skull_stripped_runner(output_root_path_registered, output_root_path_skull_stripped)

        output_root_path_bias_field_correction = output_root_path_skull_stripped.replace("skull_stripped", "bias_field_correction")
        bias_field_correction_runner(output_root_path_skull_stripped, output_root_path_bias_field_correction)

if __name__ == "__main__":
    # setup_freesurfer()
    main()
    
'''
    For skull-stripping environment variable, please run the following commands in the terminal.

    FREESURFER_HOME=/mnt/storage/ji/freesurfer
    source $FREESURFER_HOME/SetUpFreeSurfer.sh
    or
    FREESURFER_HOME=/media/Datacenter_storage/Ji/freesurfer
    source $FREESURFER_HOME/SetUpFreeSurfer.sh
    '''