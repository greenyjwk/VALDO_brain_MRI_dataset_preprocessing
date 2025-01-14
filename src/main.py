import os
import json
from preprocess.registration import registration_runner
from preprocess.skull_stripped import skull_stripped_runner
from preprocess.bias_field_correction import bias_field_correction_runner
from preprocess.select_sequence import select_sequence_valdo
from preprocess.select_sequence_mayo import select_sequence_mayo

def main():
    config_dir = "/media/Datacenter_storage/Ji/VALDO_brain_MRI_dataset_preprocessing/configs"
    config_path = os.path.join(config_dir, 'config.json')
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    dataset = config['dataset']
    if dataset == 'valdo':
        select_sequence_valdo('T1')
        select_sequence_valdo("T2")
        select_sequence_valdo('T2S')

        input_root_path = config["valdo_input_src"]
        reference_seq = config["VALDO_registration_reference"]
        
        output_root_path_registered = config["valdo_registration_output"]
        registration_runner(reference_seq, input_root_path, output_root_path_registered)
        
        output_root_path_skull_stripped = config["valdo_skull_stripped_output"]
        skull_stripped_runner(output_root_path_registered, output_root_path_skull_stripped)
        
        output_root_path_bias_field_correction = config["valdo_bias_field_correction_output"]
        bias_field_correction_runner(output_root_path_skull_stripped, output_root_path_bias_field_correction)

    elif dataset == 'mayo':
        reference_seq = config["mayo_registration_reference"]
        T1_seq = config["mayo_t1"]
        T2_seq = config["mayo_t2"]

        select_sequence_mayo(reference_seq, config)
        select_sequence_mayo(T1_seq, config)
        select_sequence_mayo(T2_seq, config)

        output_root_path_registered = config["mayo_registration_output"]
        input_root_path = config["mayo_input_src"]
        registration_runner(reference_seq, input_root_path, output_root_path_registered, config)

        output_root_path_skull_stripped = config["mayo_skull_stripped_output"]
        skull_stripped_runner(output_root_path_registered, output_root_path_skull_stripped)

        output_root_path_bias_field_correction = config["mayo_bias_field_correction_output"]
        bias_field_correction_runner(output_root_path_skull_stripped, output_root_path_bias_field_correction)

if __name__ == "__main__":
    main()