from preprocess.registration import registration_runner
from preprocess.skull_stripped import skull_stripped_runner
from preprocess.bias_field_correction import bias_field_correction_runner
from preprocess.select_sequence import select_sequence_valdo

def main():

    dataset = 'valdo'
    if dataset == 'valdo':
        select_sequence_valdo('T1')
        select_sequence_valdo("T2")
        select_sequence_valdo('T2S')

    reference_seq = "T2S"
    output_root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_registered"
    registration_runner(reference_seq, output_root_path)
    
    root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_registered"
    output_root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_skull_stripped"
    skull_stripped_runner(root_path, output_root_path)
    
    root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_skull_stripped"
    output_root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_bias_field_correction"
    bias_field_correction_runner(root_path, output_root_path)

if __name__ == "__main__":
    main()