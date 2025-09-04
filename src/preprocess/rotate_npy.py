import os
import numpy as np

root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO_3consecutive_npy_preprocessed"
img_root_path = f"{root_path}/MRI_Brain_CMB/imgs"
gt_root_path = f"{root_path}/MRI_Brain_CMB/gts"

for file in os.listdir(img_root_path):
    img_path  = os.path.join(img_root_path, file)   # shape (H,W,3)
    mask_path = os.path.join(gt_root_path, file)
    
    print(img_path)
    print(mask_path)
    
    # Load
    img  = np.load(img_path)     # (H,W,3)
    mask = np.load(mask_path)    # (H,W)

    img_rot  = np.rot90(img,  k=-1, axes=(0, 1))
    mask_rot = np.rot90(mask, k=-1, axes=(0, 1))

    np.save(img_path, img_rot)
    np.save(mask_path, mask_rot)
    print("Done:", img_rot.shape, mask_rot.shape)
    print()