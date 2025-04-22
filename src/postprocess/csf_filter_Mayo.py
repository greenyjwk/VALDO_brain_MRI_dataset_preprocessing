import os
import json
import nibabel as nib
import numpy as np

def main(data):
    csf_filter_json = "/media/Datacenter_storage/Ji/yolo8_cerebral_microbleeds/runs/test/t2S_gan_0.013/csf_filter_predictions.json"
    if not os.path.exists(csf_filter_json) or os.stat(csf_filter_json).st_size == 0:
        with open(csf_filter_json, "w") as file:
            json.dump([], file)

    for detection in data:
    
        image_id = detection["image_id"]
        uid = image_id.split("_")[0]
        slice_id = int(image_id.split("_")[1])
        bbox = detection["bbox"]
        csf_mask_path = os.path.join(f"/media/Datacenter_storage/Ji/csf_segment_threshold", uid, "T1_seg_0.nii.gz")
        
        # if uid != "4817777" and uid != 29:
        #     continue


        with open(csf_filter_json, "r") as file:
            csf_filter_data = json.load(file)

        x_center = int(bbox[0] // 4)
        y_center = int(bbox[1] // 4)
        print(x_center, y_center)
        image = nib.load(csf_mask_path)
        image = image.get_fdata()
        image = np.rot90(image[:,:,slice_id])
    
        print("image[y_center, x_center]", image[y_center, x_center])
        
        if image[y_center, x_center] == 0.0:
            csf_filter_data.append(detection)
            print(f"0: {detection}")
        elif image[y_center, x_center] == 1.0:
            print(f"1: {detection}")
        
        # # Define the 3x3 box around the center
        # y_min = max(0, y_center - 1)
        # y_max = min(image.shape[0], y_center + 2)
        # x_min = max(0, x_center - 1)
        # x_max = min(image.shape[1], x_center + 2)

        # # Extract the 3x3 box
        # box = image[y_min:y_max, x_min:x_max]
        # print("3x3 box values:", box)

        # # Check if any value in the 3x3 box is 0.0
        # if np.any(box == 1.0):
        #     print(f"csf overlapped found in 3x3 box: {detection}")
        # else:
        #     csf_filter_data.append(detection)
        #     print(f"No csf overlapped found in 3x3 box: {detection}")

        with open(csf_filter_json, "w") as file:
            json.dump(csf_filter_data, file, indent=4)

if __name__ == "__main__":
    file_path = "/media/Datacenter_storage/Ji/yolo8_cerebral_microbleeds/runs/test/t2S_gan_0.013/predictions.json"
    with open(file_path, "r") as file:
        data = json.load(file)
    main(data)