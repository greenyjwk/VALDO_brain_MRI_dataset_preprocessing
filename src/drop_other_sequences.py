import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

root_path = "/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_yolo_t2"
task = "test"
dir = os.path.join(root_path, "images", task)

for _, file in enumerate(os.listdir(dir)):
    img_path = os.path.join(dir, file)
    img = Image.open(img_path)
    img_array = np.array(img)

    # T1 = img_array[:,:,0]
    T2 = img_array[:,:,1]
    T2_star = img_array[:,:,2]

    one_channel = T2
    one_channel = Image.fromarray(one_channel)
    one_channel.save(img_path)
    print(f"{img_path} is processed")