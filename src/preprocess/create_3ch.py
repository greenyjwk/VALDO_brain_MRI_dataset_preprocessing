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

        data1 = nii1.get_fdata()
        data2 = nii2.get_fdata()
        data3 = nii3.get_fdata()        

        combined = np.stack([data1, data2, data3], axis=-1)  # H x W x D x 3
        combined_nii = nib.Nifti1Image(combined, affine=nii1.affine)

        out_file = os.path.join(out_subdir, f"{uid}.nii.gz")
        nib.save(combined_nii, out_file)
        shutil.copy(mask[0], os.path.join(output_path, uid, f"{uid}_space-T2S_CMB.nii.gz") )    # copy paste the mask file
        print("Wrote:", out_file)

if __name__ == "__main__":
    main()