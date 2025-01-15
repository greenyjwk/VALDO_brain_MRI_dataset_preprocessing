import os
import json
import argparse
from preprocess.registration import registration_runner
from preprocess.skull_stripped import skull_stripped_runner
from preprocess.bias_field_correction import bias_field_correction_runner
from preprocess.select_sequence import select_sequence_valdo
from preprocess.select_sequence_mayo import select_sequence_mayo

def main():
    parser = argparse.ArgumentParser(description="Create 3-channel NIfTI images")
    parser.add_argument('--dataset', type=str, choices=['mayo', 'valdo'], default='valdo', required=False)    
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
            
        # select_sequence_valdo('T1', config)
        # select_sequence_valdo("T2", config)
        # select_sequence_valdo('T2S', config)
        
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

        select_sequence_mayo(reference_seq, config)
        select_sequence_mayo(T1_seq, config)
        select_sequence_mayo(T2_seq, config)

        output_root_path_registered = config["mayo_registration_output"]
        registration_runner(reference_seq, input_root_path, output_root_path_registered, config)

        output_root_path_skull_stripped = output_root_path_registered.replace("registered", "skull_stripped")
        skull_stripped_runner(output_root_path_registered, output_root_path_skull_stripped)

        output_root_path_bias_field_correction = output_root_path_skull_stripped.replace("skull_stripped", "bias_field_correction")
        bias_field_correction_runner(output_root_path_skull_stripped, output_root_path_bias_field_correction)

if __name__ == "__main__":
    main()