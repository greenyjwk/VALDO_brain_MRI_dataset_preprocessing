from preprocess.registration import registration_runner
from preprocess.skull_stripped import skull_stripped_runner
from preprocess.bias_field_correction import bias_field_correction_runner
from preprocess.select_sequence import select_sequence_valdo
from preprocess.select_sequence_mayo import select_sequence_mayo

def main():

    dataset = 'mayo'
    if dataset == 'valdo':
        select_sequence_valdo('T1')
        select_sequence_valdo("T2")
        select_sequence_valdo('T2S')

        reference_seq = "T2S"
        output_root_path_registered = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_registered"
        input_root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo"
        registration_runner(reference_seq, input_root_path, output_root_path_registered)
        
        output_root_path_skull_stripped = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_skull_stripped"
        skull_stripped_runner(output_root_path_registered, output_root_path_skull_stripped)
        
        output_root_path_bias_field_correction = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_bias_field_correction"
        bias_field_correction_runner(output_root_path_skull_stripped, output_root_path_bias_field_correction)

    elif dataset == 'mayo':
        reference_seq = "Axial 3TE T2 STAR"
        T1_seq = "3D SAG T1 MPRAGE 1MM"
        T2_seq = "SAG 3D T2 SPACE"

        select_sequence_mayo(reference_seq)
        select_sequence_mayo(T1_seq)
        select_sequence_mayo(T2_seq)

        output_root_path_registered = "/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_registered"
        input_root_path = "/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo"
        registration_runner(reference_seq, input_root_path, output_root_path_registered)

        output_root_path_skull_stripped = "/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_skull_stripped"
        skull_stripped_runner(output_root_path_registered, output_root_path_skull_stripped)

        output_root_path_bias_field_correction = "/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_bias_field_correction"
        bias_field_correction_runner(output_root_path_skull_stripped, output_root_path_bias_field_correction)

if __name__ == "__main__":
    main()