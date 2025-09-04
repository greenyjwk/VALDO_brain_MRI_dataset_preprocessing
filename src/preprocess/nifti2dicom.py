import nibabel as nib
import numpy as np
import os
import glob
import subprocess

output_dir = "/media/Datacenter_storage/PublicDatasets/valdo_dicom/Task2"
root_dir = "/media/Datacenter_storage/valdo_dataset/Task2"

for sub_dir in os.listdir(root_dir):
    sub_dir_root = os.path.join(root_dir, sub_dir)
    nii_file = glob.glob(os.path.join(sub_dir_root, "*T2S.nii.gz"))
    
    if len(nii_file) == 0:
        continue
    nii_file = nii_file[0]
    temp_output_dir = os.path.join(output_dir, sub_dir)
    if not os.path.exists(temp_output_dir):
        os.makedirs(temp_output_dir, exist_ok=True)
    print(temp_output_dir)
    print(nii_file)
    
    # cmd = [
    #     'niix2dcm',
    #     '-d', temp_output_dir,  # output directory
    #     nii_file                # input NIFTI file
    # ]


    cmd = [
        'nii2dcm', 
        nii_file, 
        temp_output_dir,  # output directory
        '-d', 'MR'
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)