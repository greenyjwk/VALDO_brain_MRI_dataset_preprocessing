# import os
# import cv2
# import numpy as np
# import sys
# import random
# import nibabel as nib

# IMG_SIZE = 1024
# MIN_BOX_SIZE = 12  # Minimum box size
# MAX_BOX_SIZE = 42  # Maximum box size
# N_NEG_SAMPLES = None  # Exactly 2 samples
# NEGATIVE_CLASS_ID = 1  # non-CMB class

# def load_yolo_labels(label_path):
#     print(label_path)
#     boxes = []
#     with open(label_path, "r") as f:
#         lines = f.readlines()
#         for line in lines:
#             parts = line.strip().split()
#             _, x_center, y_center, width, height = map(float, parts)
#             x_center *= IMG_SIZE
#             y_center *= IMG_SIZE
#             width *= IMG_SIZE
#             height *= IMG_SIZE
#             x1 = int(x_center - width / 2)
#             y1 = int(y_center - height / 2)
#             x2 = int(x_center + width / 2)
#             y2 = int(y_center + height / 2)
#             boxes.append((x1, y1, x2, y2))
#     return boxes

# def has_overlap(box, boxes):
#     x1, y1, x2, y2 = box
#     for bx in boxes:
#         bx1, by1, bx2, by2 = bx
#         ix1, iy1 = max(x1, bx1), max(y1, by1)
#         ix2, iy2 = min(x2, bx2), min(y2, by2)
#         if ix1 < ix2 and iy1 < iy2:
#             return True
#     return False

# # generating brain mask from the csf region
# def generate_brain_mask(image):
#     mask = (image > 0).astype(np.uint8)
#     kernel = np.ones((5,5), np.uint8)
#     mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
#     mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
#     return mask

# def generate_csf_mask(csf_path, slice_num):
#     csf_img = nib.load(csf_path)
#     csf_img = csf_img.get_fdata()
#     csf_img = csf_img[:, :, slice_num]  # Assuming the CSF mask is in the first slice
#     csf_mask = csf_img.astype(np.uint8)
#     csf_mask = np.rot90(csf_mask, k=1)
#     return csf_mask


# def generate_negative_samples(csf_mask, original_image):
#     # Scale factor between mask and image
#     scale_factor = 4
    
#     h, w = csf_mask.shape
#     negatives = []
    
#     # Create used mask to track placed boxes
#     used_mask = np.zeros_like(csf_mask)
    
#     # Generate a list of random box sizes between MIN_BOX_SIZE and MAX_BOX_SIZE
#     # Make sure they're divisible by scale_factor for proper alignment
#     possible_box_sizes = list(range(MIN_BOX_SIZE, MAX_BOX_SIZE + 1, 4))
    
#     # Try placing boxes at random positions with random sizes
#     attempts = 0
#     max_attempts = 1000  # Prevent infinite loop
    
#     while (N_NEG_SAMPLES is None or len(negatives) < N_NEG_SAMPLES) and attempts < max_attempts:
#         attempts += 1
        
#         # Select a random box size
#         box_size = random.choice(possible_box_sizes)
#         mask_box_size = box_size // scale_factor
        
#         # Select a random position in the mask
#         mask_x = random.randint(0, w - mask_box_size)
#         mask_y = random.randint(0, h - mask_box_size)
        
#         mask_x1, mask_y1 = mask_x, mask_y
#         mask_x2, mask_y2 = mask_x + mask_box_size, mask_y + mask_box_size
        
#         # Check if the entire box region is valid CSF
#         box_region = csf_mask[mask_y1:mask_y2, mask_x1:mask_x2]
#         used_region = used_mask[mask_y1:mask_y2, mask_x1:mask_x2]
        
#         # Ensure box is fully within CSF and not already used
#         if (box_region.shape == (mask_box_size, mask_box_size) and 
#             np.all(box_region == 1) and 
#             np.all(used_region == 0)):
            
#             # Convert to image coordinates
#             x1 = mask_x1 * scale_factor
#             y1 = mask_y1 * scale_factor
#             x2 = mask_x2 * scale_factor
#             y2 = mask_y2 * scale_factor
            
#             # Check the percentage of black pixels in the original image
#             img_box = original_image[y1:y2, x1:x2]
            
#             if np.all(img_box == 0):
#                 continue
#             print(img_box.shape)
#             black_pixel_percentage = np.sum(img_box == 0) / (box_size * box_size)
            
#             # Skip if more than 80% of pixels are black
#             if black_pixel_percentage > 0.8:
#                 continue

#             negatives.append((x1, y1, x2, y2))

#             # Mark region as used in mask space
#             used_mask[mask_y1:mask_y2, mask_x1:mask_x2] = 1

#             # Reset attempts counter after successful placement
#             attempts = 0
    
#     return negatives[:N_NEG_SAMPLES] if N_NEG_SAMPLES is not None and negatives else negatives

# def save_labels(output_path, original_labels, negative_boxes):
#     lines = original_labels.copy()
#     for box in negative_boxes:
#         x1, y1, x2, y2 = box
#         width = (x2 - x1) / IMG_SIZE
#         height = (y2 - y1) / IMG_SIZE
#         x_center = (x1 + x2) / 2 / IMG_SIZE
#         y_center = (y1 + y2) / 2 / IMG_SIZE
#         line = f"{NEGATIVE_CLASS_ID} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
#         lines.append(line)

#     with open(output_path, "w") as f:
#         f.writelines(lines)

# def main(images_path, labels_path, output_labels_path, dataset):
#     # csf_root_path = "/mnt/storage/ji/csf_segment_threshold_train"
#     csf_root_path =  "/media/Datacenter_storage/Ji/csf_segment_threshold"
#     path_list = os.listdir(images_path)
#     random.shuffle(path_list)

#     ##### Being used only when smapling is neccessry
#     path_list = random.sample(path_list, 200)
#     #####
    
#     for filename in path_list:
#         print(filename)
#         if filename.endswith((".jpg", ".png")):
#             image_name = os.path.splitext(filename)[0]
#             image_path = os.path.join(images_path, filename)
#             label_path = os.path.join(labels_path, f"{image_name}.txt")
#             print(label_path)
#             sys.exit()
#             uid = image_name.split("_")[0]

#             if dataset=="valdo":
#                 slice_num = int(image_name.split("_")[2].split('.')[0])
#             elif dataset=="mayo":
#                 print(image_name.split("_")[1])
#                 slice_num = int(image_name.split("_")[1])
            
#             csf_path = os.path.join(csf_root_path, f"{uid}", "T1_seg_0.nii.gz")

#             output_label_path = os.path.join(output_labels_path, f"{image_name}.txt")
#             if not os.path.exists(label_path):
#                 open(label_path, "w").close()

#             image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
#             csf_mask = generate_csf_mask(csf_path, slice_num)
#             negative_boxes = generate_negative_samples(csf_mask, image)

#             # with open(label_path, "r") as f:
#             #     original_label_lines = f.readlines()
#             with open(label_path, "r") as f:
#                 original_label_lines = f.readlines()


#             save_labels(output_label_path, original_label_lines, negative_boxes)

# if __name__ == "__main__":
#     task = 'test'
#     # images_path = f"/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_epd_gt_box_GAN_cmbOnly_2class_csf/images/{task}"
#     # labels_path = f"/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_epd_gt_box_GAN_cmbOnly_2class_csf/labels/{task}"
#     # output_labels_path = f"/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_epd_gt_box_GAN_cmbOnly_2class_csf/labels/{task}"

#     images_path = f"/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_yolo_all_sequence/images/{task}"
#     labels_path = f"/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_yolo_all_sequence/labels/{task}"
#     output_labels_path = f"/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_yolo_all_sequence/csf_labels/{task}"

#     os.makedirs(output_labels_path, exist_ok=True)
#     main(images_path, labels_path, output_labels_path, dataset="mayo")

# '''
# export FSLDIR=/home/ji/fsl
# source $FSLDIR/etc/fslconf/fsl.sh
# export PATH=$FSLDIR/bin:$PATH
# '''




import os
import cv2
import numpy as np
import sys
import random
import nibabel as nib

IMG_SIZE = 1024
MIN_BOX_SIZE = 12  # Minimum box size
MAX_BOX_SIZE = 42  # Maximum box size
N_NEG_SAMPLES = None  # Exactly 2 samples, or None for unlimited
NEGATIVE_CLASS_ID = 1  # non-CMB class

def load_yolo_labels(label_path):
    boxes = []
    with open(label_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            parts = line.strip().split()
            _, x_center, y_center, width, height = map(float, parts)
            x_center *= IMG_SIZE
            y_center *= IMG_SIZE
            width *= IMG_SIZE
            height *= IMG_SIZE
            x1 = int(x_center - width / 2)
            y1 = int(y_center - height / 2)
            x2 = int(x_center + width / 2)
            y2 = int(y_center + height / 2)
            boxes.append((x1, y1, x2, y2))
    return boxes

def has_overlap(box, boxes):
    x1, y1, x2, y2 = box
    for bx in boxes:
        bx1, by1, bx2, by2 = bx
        ix1, iy1 = max(x1, bx1), max(y1, by1)
        ix2, iy2 = min(x2, bx2), min(y2, by2)
        if ix1 < ix2 and iy1 < iy2:
            return True
    return False

def generate_brain_mask(image):
    mask = (image > 0).astype(np.uint8)
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask

def generate_csf_mask(csf_path, slice_num):
    csf_img = nib.load(csf_path)
    csf_img = csf_img.get_fdata()
    csf_img = csf_img[:, :, slice_num]
    csf_mask = csf_img.astype(np.uint8)
    csf_mask = np.rot90(csf_mask, k=1)
    return csf_mask

def generate_negative_samples(csf_mask, original_image):
    scale_factor = 4
    h, w = csf_mask.shape
    negatives = []
    used_mask = np.zeros_like(csf_mask)
    possible_box_sizes = list(range(MIN_BOX_SIZE, MAX_BOX_SIZE + 1, 4))
    attempts = 0
    max_attempts = 1000

    while (N_NEG_SAMPLES is None or len(negatives) < N_NEG_SAMPLES) and attempts < max_attempts:
        attempts += 1
        box_size = random.choice(possible_box_sizes)
        mask_box_size = box_size // scale_factor
        mask_x = random.randint(0, w - mask_box_size)
        mask_y = random.randint(0, h - mask_box_size)
        mask_x1, mask_y1 = mask_x, mask_y
        mask_x2, mask_y2 = mask_x + mask_box_size, mask_y + mask_box_size
        box_region = csf_mask[mask_y1:mask_y2, mask_x1:mask_x2]
        used_region = used_mask[mask_y1:mask_y2, mask_x1:mask_x2]
        if (box_region.shape == (mask_box_size, mask_box_size) and 
            np.all(box_region == 1) and 
            np.all(used_region == 0)):
            x1 = mask_x1 * scale_factor
            y1 = mask_y1 * scale_factor
            x2 = mask_x2 * scale_factor
            y2 = mask_y2 * scale_factor
            img_box = original_image[y1:y2, x1:x2]
            if np.all(img_box == 0):
                continue
            black_pixel_percentage = np.sum(img_box == 0) / (box_size * box_size)
            if black_pixel_percentage > 0.8:
                continue
            negatives.append((x1, y1, x2, y2))
            used_mask[mask_y1:mask_y2, mask_x1:mask_x2] = 1
            attempts = 0
    return negatives[:N_NEG_SAMPLES] if N_NEG_SAMPLES is not None and negatives else negatives

def save_labels(output_path, original_labels, negative_boxes):
    # Ensure all lines end with \n
    lines = []
    for l in original_labels:
        if not l.strip():
            continue  # skip empty lines
        if not l.endswith('\n'):
            lines.append(l.strip() + '\n')
        else:
            lines.append(l)
    # Add negative samples
    for box in negative_boxes:
        x1, y1, x2, y2 = box
        width = (x2 - x1) / IMG_SIZE
        height = (y2 - y1) / IMG_SIZE
        x_center = (x1 + x2) / 2 / IMG_SIZE
        y_center = (y1 + y2) / 2 / IMG_SIZE
        line = f"{NEGATIVE_CLASS_ID} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
        lines.append(line)
    with open(output_path, "w") as f:
        f.writelines(lines)

def main(images_path, labels_path, output_labels_path, dataset):
    csf_root_path =  "/media/Datacenter_storage/Ji/csf_segment_threshold"
    path_list = os.listdir(images_path)
    random.shuffle(path_list)
    # Example: sample for testing, remove in production!
    # path_list = random.sample(path_list, 200)
    for filename in path_list:
        if not filename.endswith((".jpg", ".png")):
            continue
        image_name = os.path.splitext(filename)[0]
        image_path = os.path.join(images_path, filename)
        label_path = os.path.join(labels_path, f"{image_name}.txt")
        uid = image_name.split("_")[0]
        if dataset=="valdo":
            slice_num = int(image_name.split("_")[2].split('.')[0])
        elif dataset=="mayo":
            slice_num = int(image_name.split("_")[1])
        csf_path = os.path.join(csf_root_path, f"{uid}", "T1_seg_0.nii.gz")
        output_label_path = os.path.join(output_labels_path, f"{image_name}.txt")
        # --- read the original label file, create an empty list if it doesn't exist ---
        if os.path.exists(label_path):
            with open(label_path, "r") as f:
                original_label_lines = f.readlines()
        else:
            original_label_lines = []
        # --- process image/mask ---
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        csf_mask = generate_csf_mask(csf_path, slice_num)
        negative_boxes = generate_negative_samples(csf_mask, image)
        # --- append negatives and write out ---
        save_labels(output_label_path, original_label_lines, negative_boxes)
        print(f"Wrote: {output_label_path} | Orig: {len(original_label_lines)} | Neg: {len(negative_boxes)}")

if __name__ == "__main__":
    task = 'test'
    images_path = f"/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_yolo_all_sequence/images/{task}"
    labels_path = f"/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_yolo_all_sequence/labels/{task}"
    output_labels_path = f"/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_yolo_all_sequence/csf_labels/{task}"
    os.makedirs(output_labels_path, exist_ok=True)
    main(images_path, labels_path, output_labels_path, dataset="mayo")