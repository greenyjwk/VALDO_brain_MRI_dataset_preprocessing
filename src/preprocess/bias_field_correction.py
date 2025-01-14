import os
from pathlib import Path
from nipype.interfaces.ants.segmentation import N4BiasFieldCorrection

def create_dir(path):
    path_obj = Path(path)
    if not path_obj.is_dir():
        path_obj.mkdir(parents=True, exist_ok=True)
    return

def unwarp_bias_field_correction(arg, **kwarg):
    return bias_field_correction(*arg, **kwarg)

def bias_field_correction(src_path, dst_path):
    print("N4ITK on: ", src_path)
    try:
        n4 = N4BiasFieldCorrection()
        n4.inputs.input_image = str(src_path)
        n4.inputs.output_image = str(dst_path)
        n4.inputs.dimension = 3
        n4.inputs.n_iterations = [100, 100, 60, 40]
        n4.inputs.shrink_factor = 3
        n4.inputs.convergence_threshold = 1e-4
        n4.inputs.bspline_fitting_distance = 300
        n4.run()
    except RuntimeError:
        print("\tFailed on: ", src_path)
    return

def bias_field_correction_runner(root_path, output_root_path):
    if not os.path.exists(output_root_path):
        os.mkdir(output_root_path)
    
    for uid in os.listdir(root_path):
        if uid == ".DS_Store":
            continue

        if not os.path.exists(os.path.join(output_root_path, uid)):
                os.mkdir(os.path.join(output_root_path, uid))

        for file in os.listdir(os.path.join(root_path, uid)):
            file_path = os.path.join(os.path.join(root_path, uid), file)
            output_file_path = os.path.join(output_root_path, uid, file)
            bias_field_correction(file_path, output_file_path)

def main():
    root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_skull_stripped"
    output_root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_bias_field_correction"
    bias_field_correction_runner(root_path, output_root_path)
    
if __name__ == "__main__":
    main()