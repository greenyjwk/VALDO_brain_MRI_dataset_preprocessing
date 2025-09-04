# import nibabel as nib
# import numpy as np
# import os
# import sys
# import glob
# import json
# import argparse
# import re

# def main():
#     parser = argparse.ArgumentParser(description="Create 3-channel NIfTI images")
#     parser.add_argument('--dataset', type=str, choices=['mayo', 'valdo'], default='valdo', required=False)
    
#     # Mayo
#     if args.dataset == 'mayo':
#         parser.add_argument('--src_path', type=str, required=False, default="/MAYO_cerebral_microbleeds/mayo_bias_field_correction")
#         parser.add_argument('--output_path', type=str, required=False, default="/MAYO_cerebral_microbleeds/mayo_stacked")
#         parser.add_argument('--config_path', type=str, required=False, default="/VALDO_brain_MRI_dataset_preprocessing/configs/config.json")
#     # Valdo
#     elif args.dataset == 'valdo':
#         parser.add_argument('--src_path', type=str, required=False, default="/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/bias_field_correction")
#         parser.add_argument('--output_path', type=str, required=False, default="/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/3ch_stacked")
#         parser.add_argument('--config_path', type=str, required=False, default="/VALDO_brain_MRI_dataset_preprocessing/configs/config.json")

#     args = parser.parse_args()
#     dataset = args.dataset
    
#     if args.dataset == 'mayo':
#         root = "/media/Datacenter_storage/PublicDatasets"
#         src_path = root + args.src_path
#         output_dir = root + args.output_path
#         config_path = "/media/Datacenter_storage/Ji/VALDO_brain_MRI_dataset_preprocessing/configs/config.json"
#     elif args.dataset == "valdo":
#         # root = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/bias_field_correction"
#         src_path = root + args.src_path
#         output_dir = root + args.output_path
#         config_path = "/media/Datacenter_storage/Ji/VALDO_brain_MRI_dataset_preprocessing/configs/config.json"

#     # config file
#     with open(config_path, 'r') as config_file:
#         config = json.load(config_file)

#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)

#     for uid in os.listdir(src_path):
#         subdir_path = os.path.join(src_path, uid)
        
#         # creating subdirectory in output directory
#         if not os.path.exists(os.path.join(output_dir, uid)):
#             os.mkdir(os.path.join(output_dir, uid))

#         if args.dataset == 'mayo':
#             nii1 = glob.glob(os.path.join(subdir_path, f"{config['mayo_stack_order'][0]}*.nii.gz"))
#             nii2 = glob.glob(os.path.join(subdir_path, f"{config['mayo_stack_order'][1]}*.nii.gz"))
#             nii3 = glob.glob(os.path.join(subdir_path, f"{config['mayo_stack_order'][2]}*.nii.gz"))
#         elif args.dataset == 'valdo':
#             nii1 = glob.glob(os.path.join(subdir_path, f"*{config['valdo_stack_order'][0]}.nii.gz"))
#             nii2 = glob.glob(os.path.join(subdir_path, f"*{config['valdo_stack_order'][1]}.nii.gz"))
#             nii3 = glob.glob(os.path.join(subdir_path, f"*{config['valdo_stack_order'][2]}.nii.gz"))
            
#             print(nii1)
#             print(nii2)
#             print(nii3)

#         if not nii1 or not nii2 or not nii3:
#             print(f"Files not found for subdir: {uid}")
#             continue

#         nii1 = nib.load(nii1[0])
#         nii2 = nib.load(nii2[0])
#         nii3 = nib.load(nii3[0])

#         # Extract data arrays
#         data1 = nii1.get_fdata()
#         data2 = nii2.get_fdata()
#         data3 = nii3.get_fdata()

#         # Stack the arrays along a new 4th dimension (channel dimension)
#         combined_data = np.stack([data1, data2, data3], axis=-1)

#         # Create a new NIfTI image
#         combined_nii = nib.Nifti1Image(combined_data, affine=nii3.affine)

#         # Save the combined image
#         output_file = os.path.join(output_dir, uid, f"{uid}.nii.gz")
#         nib.save(combined_nii, output_file)

# if __name__ == "__main__":
#     main()


import nibabel as nib
import numpy as np
import os
import sys
import shutil
import glob
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description="Create 3-channel NIfTI images")
    parser.add_argument('--dataset', type=str, choices=['mayo', 'valdo'], default='valdo')

    # Define these args once (not conditionally). We’ll set sensible defaults after parsing.
    parser.add_argument('--src_path', type=str, required=False)
    parser.add_argument('--output_path', type=str, required=False)
    parser.add_argument('--config_path', type=str, required=False)

    args = parser.parse_args()

    # Defaults depending on dataset
    if args.dataset == 'mayo':
        root = "/media/Datacenter_storage/PublicDatasets"
        src_path = args.src_path or "/MAYO_cerebral_microbleeds/mayo_bias_field_correction"
        output_path = args.output_path or "/MAYO_cerebral_microbleeds/mayo_stacked"
        config_path = args.config_path or "/media/Datacenter_storage/Ji/VALDO_brain_MRI_dataset_preprocessing/configs/config.json"
    else:  # valdo
        root = ""  # paths are already absolute below
        src_path = args.src_path or "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/bias_field_correction_resampled"
        output_path = args.output_path or "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/3ch_stacked"
        config_path = args.config_path or "/media/Datacenter_storage/Ji/VALDO_brain_MRI_dataset_preprocessing/configs/config.json"

    src_path = os.path.join(root, src_path.lstrip("/")) if root else src_path
    output_dir = os.path.join(root, output_path.lstrip("/")) if root else output_path

    # Read config
    with open(config_path, 'r') as f:
        config = json.load(f)

    os.makedirs(output_dir, exist_ok=True)

    # Walk subjects
    for uid in os.listdir(src_path):
        subdir_path = os.path.join(src_path, uid)
        if not os.path.isdir(subdir_path):
            continue

        out_subdir = os.path.join(output_dir, uid)
        os.makedirs(out_subdir, exist_ok=True)

        if args.dataset == 'mayo':
            a = glob.glob(os.path.join(subdir_path, f"{config['mayo_stack_order'][0]}*.nii.gz"))
            b = glob.glob(os.path.join(subdir_path, f"{config['mayo_stack_order'][1]}*.nii.gz"))
            c = glob.glob(os.path.join(subdir_path, f"{config['mayo_stack_order'][2]}*.nii.gz"))
        else:  # valdo
            a = glob.glob(os.path.join(subdir_path, f"*{config['valdo_stack_order'][0]}.nii.gz"))
            b = glob.glob(os.path.join(subdir_path, f"*{config['valdo_stack_order'][1]}.nii.gz"))
            c = glob.glob(os.path.join(subdir_path, f"*{config['valdo_stack_order'][2]}.nii.gz"))

            mask = glob.glob(os.path.join(subdir_path, f"*CMB.nii.gz"))
            print(mask)
            # sys.exit()
            print(a); print(b); print(c)

        if not a or not b or not c:
            print(f"Files not found for subdir: {uid}")
            continue

        nii1 = nib.load(a[0])
        nii2 = nib.load(b[0])
        nii3 = nib.load(c[0])

        # Sanity checks (avoid silent misalignment)
        if (nii1.shape != nii2.shape) or (nii1.shape != nii3.shape):
            print(f"[WARN] Shape mismatch in {uid}: {nii1.shape}, {nii2.shape}, {nii3.shape}. Skipping.")
            continue
        if not (np.allclose(nii1.affine, nii2.affine) and np.allclose(nii1.affine, nii3.affine)):
            print(f"[WARN] Affine mismatch in {uid}. Consider resampling. Using nii1 affine.")
            # Optionally: resample nii2/nii3 to nii1 here.

        data1 = nii1.get_fdata()
        data2 = nii2.get_fdata()
        data3 = nii3.get_fdata()

        combined = np.stack([data1, data2, data3], axis=-1)  # H x W x D x 3
        combined_nii = nib.Nifti1Image(combined, affine=nii1.affine)

        out_file = os.path.join(out_subdir, f"{uid}.nii.gz")
        nib.save(combined_nii, out_file)

        shutil.copy(mask[0], os.path.join(output_path, uid, f"{uid}_space-T2S_CMB.nii.gz") )
        # cerebral_microbleeds_VALDO/bias_field_correction_resampled/sub-103/sub-103_space-T2S_CMB.nii.gz

        print("Wrote:", out_file)

if __name__ == "__main__":
    main()