import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

root_path = "/media/Datacenter_storage/Ji/valdo_dataset/valdo_distrSampled_GAN_T1T2"
task = "val"
dir = os.path.join(root_path, "images", task)

for _, file in enumerate(os.listdir(dir)):
    img_path = os.path.join(dir, file)
    img = Image.open(img_path)
    img_array = np.array(img)

    T1 = img_array[:,:,0]
    T2 = img_array[:,:,1]
    T2S = img_array[:,:,2]

    two_channels = np.stack((T1, T2), axis=-1)
    two_channels = Image.fromarray(two_channels)
    two_channels.save(img_path)
    print(f"{img_path} is processed")