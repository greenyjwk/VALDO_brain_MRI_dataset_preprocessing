import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/media/Datacenter_storage/Ji/valdo_dataset/valdo_distrSampled_GAN_T1T2"
task = "val"
dir = os.path.join(root_path, "images", task)

for _, file in enumerate(os.listdir(dir)):
    img_path = os.path.join(dir, file)
    img = Image.open(img_path)
    img_array = np.array(img)

    # T1 = img_array[:,:,0]
    T2 = img_array[:,:,1]

    # one_channel = np.stack((T1), axis=-1)
    one_channel = T2
    one_channel = Image.fromarray(one_channel)
    one_channel.save(img_path)
    print(f"{img_path} is processed")


# import os
# import numpy as np
# import matplotlib.pyplot as plt
# from PIL import Image

# root_path = "/mnt/storage/ji/brain_mri_valdo_mayo/media/Datacenter_storage/Ji/valdo_dataset/valdo_distrSampled_GAN_T1T2"
# task = "train"
# dir = os.path.join(root_path, "images", task)

# for file in os.listdir(dir):
#     if file.lower().endswith(('.png', '.jpg', '.jpeg')):  # Only process image files
#         img_path = os.path.join(dir, file)
#         try:
#             img = Image.open(img_path)
#             img_array = np.array(img)
            
#             # Check if image has multiple channels
#             if img_array.shape[2] >= 2:
#                 # Extract T2 channel (second channel)
#                 T2 = img_array[:,:,1]
                
#                 # Convert back to PIL Image and save
#                 one_channel = Image.fromarray(T2)
#                 one_channel.save(img_path)
#                 print(f"{img_path} is processed")
#             else:
#                 print(f"Skipping {img_path}: not a multi-channel image")
                
#         except Exception as e:
#             print(f"Error processing {img_path}: {e}")