# import nibabel as nib
# import numpy as np
# from scipy.ndimage import zoom
# from scipy.ndimage import binary_erosion, binary_dilation
# import os
# import sys


# def main(mask_nifti_root_path, output_root_path):
#     temp_root = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/valdo_png/images/train"
#     train_uid_set = set()
#     for file in os.listdir(temp_root):
#         train_uid_set.add(file.split("_")[0])
#     print(train_uid_set)

#     for uid in os.listdir(mask_nifti_root_path):
#         nifti_path = os.path.join(mask_nifti_root_path, uid, f"{uid}_space-T2S_CMB.nii.gz")
#         print(nifti_path)

#         if uid in train_uid_set:
#             output_path = os.path.join(output_root_path, 'train')
#         else:
#             output_path = os.path.join(output_root_path, 'val')

#         mask_file = nib.load(nifti_path)
#         mask_file = mask_file.get_fdata()

#         for i in range(mask_file.shape[2]):
#             slice_data = mask_file[:,:,i]
#             slice_data = slice_data.astype(np.uint8)
#             file_name = f"{uid}_slice_{i:03d}.png"
#             file_name = os.path.join(output_path, file_name)
#             print(file_name)
        

# # Example usage
# if __name__ == "__main__":
#     mask_root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/cmb_csf"
#     output_root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/valdo_png/csf_mask/"
#     main(mask_root_path, output_root_path)




import os
import nibabel as nib
import numpy as np
from PIL import Image

def main(mask_nifti_root_path, output_root_path):
    # 1) Build train UID set from existing PNGs under images/train
    images_train_dir = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/valdo_png/images/train"
    train_uid_set = {
        fname.split("_")[0]
        for fname in os.listdir(images_train_dir)
        if fname.lower().endswith(".png")
    }
    print(f"[INFO] #train UIDs found: {len(train_uid_set)}")

    out_train = os.path.join(output_root_path, "train")
    out_val   = os.path.join(output_root_path, "val")
    os.makedirs(out_train, exist_ok=True)
    os.makedirs(out_val, exist_ok=True)

    for uid in sorted(os.listdir(mask_nifti_root_path)):
        uid_dir = os.path.join(mask_nifti_root_path, uid)
        if not os.path.isdir(uid_dir):
            continue

        nifti_path = os.path.join(uid_dir, f"{uid}_space-T2S_CMB.nii.gz")
        if not os.path.exists(nifti_path):
            print(f"[WARN] Missing NIfTI: {nifti_path}")
            continue

        # Decide split
        output_dir = out_train if uid in train_uid_set else out_val

        nii = nib.load(nifti_path)
        data = nii.get_fdata().astype(np.uint8)

        # Sanity check: 3D volume
        if data.ndim != 3:
            print(f"[WARN] Not 3D: {nifti_path} (shape={data.shape}) — skipping.")
            continue

        # 5) Save each axial slice as PNG (values preserved)
        depth = data.shape[2]
        for i in range(depth):
            slice_data = data[:, :, i]
            img = Image.fromarray(slice_data, mode="L")  # keeps 0/1/2 as-is
            png_name = f"{uid}_slice_{i:03d}.png"
            png_path = os.path.join(output_dir, png_name)
            img.save(png_path)

        print(f"[OK] {uid}: saved {depth} slices to {output_dir}")

if __name__ == "__main__":
    mask_root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/cmb_csf"
    output_root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/valdo_png/csf_mask"
    main(mask_root_path, output_root_path)