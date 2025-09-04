import os
import sys

root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/bias_field_correction"
for uid in os.listdir(root_path):
    print(uid)
    
    file_path = os.path.join(root_path, uid, f'{uid}_space-T2S_desc-masked_T2S_rotated.nii.gz')
    try:    
        os.remove(file_path)
        print("Successfully deleted:", file_path)

    except Exception as e:
        print(f"Error deleting {file_path}: {e}")

