import os
import shutil

root_dir = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/Task2"
root_dir_dest = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/bias_field_correction"
for uid in os.listdir(root_dir):
    if uid.startswith('.') or uid == ".DS_Store":
        continue
    print(uid)
    for file in os.listdir(os.path.join(root_dir, uid)):
        if file.endswith('CMB.nii.gz'):
            file_path = os.path.join(root_dir, uid, file)
            dest_path = os.path.join(root_dir_dest, uid, file)
            print(file_path)
            print(dest_path)
            print()

            shutil.copy2(file_path, dest_path)