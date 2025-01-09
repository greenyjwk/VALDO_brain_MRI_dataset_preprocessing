import os
import subprocess
from pathlib import Path
from nipype.interfaces.ants.segmentation import N4BiasFieldCorrection

root_path = "/mnt/storage/ji/VALDO_preprocessing/skull-stripped"
output_dir = "/mnt/storage/ji/VALDO_preprocessing/bias-field-correction"

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

if not os.path.exists(output_dir):
    os.mkdir(output_dir)

for subdir in os.listdir(root_path):
    print(subdir)
    if subdir == ".DS_Store":
        continue

    T1 = os.path.join(root_path, subdir, subdir + "_space-T2S_desc-masked_T1.nii.gz")
    T2 = os.path.join(root_path, subdir, subdir + "_space-T2S_desc-masked_T2.nii.gz")
    T2S = os.path.join(root_path, subdir, subdir + "_space-T2S_desc-masked_T2S.nii.gz")

    # creating subdirecty from output directory
    if not os.path.exists(os.path.join(output_dir, subdir)):
        os.mkdir(os.path.join(output_dir, subdir))

    # bias_field_correction for T1
    bias_field_correction(T1, os.path.join(output_dir, subdir, subdir+"_space-T2S_desc-masked_T1.nii.gz"))
    
    # bias_field_correction for T2
    bias_field_correction(T2, os.path.join(output_dir, subdir, subdir+"_space-T2S_desc-masked_T2.nii.gz"))
    
    # bias_field_correction for T2S
    bias_field_correction(T2S, os.path.join(output_dir, subdir, subdir+"_space-T2S_desc-masked_T2S.nii.gz"))