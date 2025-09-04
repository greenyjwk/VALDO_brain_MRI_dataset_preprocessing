# import sys
# import shutil
# import os
# import ants
# import json
# import re
# import numpy as np

# # def registration_runner(reference_seq, input_root_path, output_root_path, config):
# def registration_runner(reference_seq, input_root_path, output_root_path, config):
#     print("Mayo Registration")
#     reference_seq = re.sub(r'\s+', '_', reference_seq)

#     if not os.path.exists(output_root_path):
#         os.mkdir(output_root_path)
    
#     subfolders = os.listdir(input_root_path)

#     for uid in subfolders:
#         print(uid)
#         if uid == ".DS_Store" or uid.startswith('.') or uid.endswith('CMB.nii.gz'):
#             continue

#         # Find the file that starts with reference_seq
#         reference_file = None
#         moving_files = []
#         for file in os.listdir(os.path.join(input_root_path, uid)):
#             # print(file)
#             if file.startswith(".") or file.endswith(".dcm"):
#                 continue
#             if file.endswith(f"{reference_seq}.nii.gz"):
#                 reference_file = file
#             else:
#                 moving_files.append(file)
        
#         print(reference_file)
#         print()
#         print(moving_files)
#         print('----------')
#         if reference_file is None or len(moving_files) < 2:
#             print(f"Files not found for subdir: {uid}")
#             continue

#         reference_path = os.path.join(input_root_path, uid, reference_file)
#         # reference_path = fixed
#         moving1 = os.path.join(input_root_path, uid, moving_files[0])
#         moving2 = os.path.join(input_root_path, uid, moving_files[1])
        
#         print("refrence_path ", reference_path)
#         print("moving1 ", moving1)
#         print("moving2 ", moving2)
    
#         fixed = ants.image_read(reference_path)
#         moving1 = ants.image_read(moving1)
#         moving2 = ants.image_read(moving2)

#         moving1 = ants.from_numpy(np.flip(moving1.numpy(), axis=0), spacing=moving1.spacing)
#         moving2 = ants.from_numpy(np.flip(moving2.numpy(), axis=0), spacing=moving2.spacing)           

#         moving1 = ants.from_numpy(np.flip(moving1.numpy(), axis=0), spacing=moving1.spacing)
#         moving2 = ants.from_numpy(np.flip(moving2.numpy(), axis=0), spacing=moving2.spacing) 

#         if config["dataset"] == 'mayo':
#             if fixed.shape[3] > 1:
#                 fixed = fixed[:,:,:,config['mayo_TE_frame']]  # Selecting 3rd TE
#                 print(fixed.shape)

#         # creating subdirectory from output directory
#         if not os.path.exists(os.path.join(output_root_path, uid)):
#             os.mkdir(os.path.join(output_root_path, uid))

#         try:
#             # registration for T1
#             # “SyN”: Symmetric normalization: Affine + deformable transformation, with mutual information as optimization metric.
#             registration_T1 = ants.registration(fixed=fixed, moving=moving1, type_of_transform=config["registration_type"])
#             aligned_volume_T1 = registration_T1['warpedmovout']   # Since the moving image is warped to the fixed image space
#             ants.image_write(aligned_volume_T1, os.path.join(output_root_path, uid, moving_files[0]))

#             # registration for T2
#             registration_T2 = ants.registration(fixed=fixed, moving=moving2, type_of_transform=config["registration_type"])
#             aligned_volume_T2 = registration_T2['warpedmovout'] # Since the moving image is warped to the fixed image space
#             ants.image_write(aligned_volume_T2, os.path.join(output_root_path, uid, moving_files[1]))
            
#             # copy and paste T2S to the output directory
#             shutil.copy(reference_path, os.path.join(output_root_path, uid, reference_file))
#         except RuntimeError as e:
#             print(f"Registration for T2 failed for {uid} with error: {e}")
#             continue
        
# def main():
#     config_path = '/media/Datacenter_storage/Ji/VALDO_brain_MRI_dataset_preprocessing/configs/config.json'
#     with open(config_path, 'r') as config_file:
#         config = json.load(config_file)

#     reference_seq = "T2S"
#     input_root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/Task2"
#     output_root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/registration"
#     registration_runner(reference_seq, input_root_path, output_root_path, config)

# if __name__ == "__main__":
#     main()



import sys
import shutil
import os
import ants
import json
import re
import numpy as np

def list_masks(dirpath):
    # Only pick segmentation masks that end with CMB.nii.gz
    return [f for f in os.listdir(dirpath)
            if f.endswith('CMB.nii.gz') and not f.startswith('.')]

def apply_same_flip_as_moving(img_ants):
    # You flip moving images along axis=0; mirror that here for masks in moving space
    return ants.from_numpy(np.flip(img_ants.numpy(), axis=0), spacing=img_ants.spacing)

def warp_mask_to_fixed(mask_img, fixed_img, fwdtransforms, out_path):
    warped = ants.apply_transforms(
        fixed=fixed_img,
        moving=mask_img,
        transformlist=fwdtransforms,
        interpolator='nearestNeighbor'
    )
    ants.image_write(warped, out_path)

def warp_mask_to_moving(mask_img, moving_img, invtransforms, out_path):
    warped = ants.apply_transforms(
        fixed=moving_img,
        moving=mask_img,
        transformlist=invtransforms,
        interpolator='nearestNeighbor'
    )
    ants.image_write(warped, out_path)

def registration_runner(reference_seq, input_root_path, output_root_path, config):
    print("Mayo Registration")
    reference_seq = re.sub(r'\s+', '_', reference_seq)

    os.makedirs(output_root_path, exist_ok=True)
    subfolders = os.listdir(input_root_path)

    for uid in subfolders:
        print(uid)
        if uid == ".DS_Store" or uid.startswith('.'):
            continue

        uid_dir = os.path.join(input_root_path, uid)
        if not os.path.isdir(uid_dir):
            continue

        # Separate reference, movings, and masks
        reference_file = None
        moving_files = []
        mask_files = []

        for file in os.listdir(uid_dir):
            if file.startswith(".") or file.endswith(".dcm"):
                continue
            if file.endswith(f"{reference_seq}.nii.gz"):
                reference_file = file
            elif file.endswith('CMB.nii.gz'):
                mask_files.append(file)
            else:
                moving_files.append(file)

        print("reference:", reference_file)
        print("movings:  ", moving_files)
        print("masks:    ", mask_files)
        print('----------')

        if reference_file is None or len(moving_files) < 2:
            print(f"Files not found for subdir: {uid}")
            continue

        reference_path = os.path.join(uid_dir, reference_file)
        moving1_path  = os.path.join(uid_dir, moving_files[0])
        moving2_path  = os.path.join(uid_dir, moving_files[1])

        print("reference_path ", reference_path)
        print("moving1        ", moving1_path)
        print("moving2        ", moving2_path)

        fixed  = ants.image_read(reference_path)
        moving1 = ants.image_read(moving1_path)
        moving2 = ants.image_read(moving2_path)

        # Flip each moving image ONCE (you had it twice before)
        moving1 = ants.from_numpy(np.flip(moving1.numpy(), axis=0), spacing=moving1.spacing)
        moving2 = ants.from_numpy(np.flip(moving2.numpy(), axis=0), spacing=moving2.spacing)

        # If fixed is 4D T2* with multiple TEs, select your TE frame
        if config.get("dataset") == 'mayo':
            # antsImage supports .shape; handle both 3D/4D safely
            shp = getattr(fixed, "shape", None)
            if shp is not None and len(shp) == 4 and shp[3] > 1:
                fixed = fixed[:,:,:,config['mayo_TE_frame']]
                print("fixed (single TE) shape:", fixed.shape)

        out_uid = os.path.join(output_root_path, uid)
        os.makedirs(out_uid, exist_ok=True)

        try:
            # Register moving1 -> fixed (e.g., T1 -> T2S)
            reg1 = ants.registration(fixed=fixed, moving=moving1, type_of_transform=config["registration_type"])
            ants.image_write(reg1['warpedmovout'], os.path.join(out_uid, moving_files[0]))

            # Register moving2 -> fixed (e.g., T2 -> T2S)
            reg2 = ants.registration(fixed=fixed, moving=moving2, type_of_transform=config["registration_type"])
            ants.image_write(reg2['warpedmovout'], os.path.join(out_uid, moving_files[1]))

            # Copy fixed (T2S) image into output
            shutil.copy(reference_path, os.path.join(out_uid, reference_file))

            # ---------- Handle CMB masks ----------
            for m in mask_files:
                mask_path = os.path.join(uid_dir, m)
                mask_img  = ants.image_read(mask_path)

                # Heuristic: if shape & spacing match fixed, treat as fixed-space mask
                is_fixed_space = (mask_img.shape == fixed.shape and np.allclose(mask_img.spacing, fixed.spacing))

                if is_fixed_space:
                    # 1) Save mask in fixed space as-is
                    ants.image_write(mask_img, os.path.join(out_uid, m))

                    # 2) Optionally project it to moving spaces (inverse transforms)
                    out_to_m1 = os.path.join(out_uid, m.replace('.nii.gz', f'__in_{os.path.splitext(moving_files[0])[0]}.nii.gz'))
                    warp_mask_to_moving(mask_img, moving1, reg1['invtransforms'], out_to_m1)

                    out_to_m2 = os.path.join(out_uid, m.replace('.nii.gz', f'__in_{os.path.splitext(moving_files[1])[0]}.nii.gz'))
                    warp_mask_to_moving(mask_img, moving2, reg2['invtransforms'], out_to_m2)

                else:
                    # Mask likely lives in one of the moving spaces. Choose by closest shape/spacing.
                    def closer_to(a_img, b_img, m_img):
                        s1 = np.sum(np.abs(np.array(a_img.shape) - np.array(m_img.shape))) + np.sum(np.abs(np.array(a_img.spacing) - np.array(m_img.spacing)))
                        s2 = np.sum(np.abs(np.array(b_img.shape) - np.array(m_img.shape))) + np.sum(np.abs(np.array(b_img.spacing) - np.array(m_img.spacing)))
                        return 'a' if s1 <= s2 else 'b'

                    which = closer_to(moving1, moving2, mask_img)

                    # Apply the SAME pre-registration flip as the corresponding moving image
                    mask_img_flipped = apply_same_flip_as_moving(mask_img)

                    out_to_fixed = os.path.join(out_uid, m.replace('.nii.gz', f'__to_{os.path.splitext(reference_file)[0]}.nii.gz'))
                    if which == 'a':
                        warp_mask_to_fixed(mask_img_flipped, fixed, reg1['fwdtransforms'], out_to_fixed)
                    else:
                        warp_mask_to_fixed(mask_img_flipped, fixed, reg2['fwdtransforms'], out_to_fixed)

        except RuntimeError as e:
            print(f"Registration failed for {uid} with error: {e}")
            continue

def main():
    config_path = '/media/Datacenter_storage/Ji/VALDO_brain_MRI_dataset_preprocessing/configs/config.json'
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    reference_seq = "T2S"
    input_root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/Task2"
    output_root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/registration"
    registration_runner(reference_seq, input_root_path, output_root_path, config)

if __name__ == "__main__":
    main()