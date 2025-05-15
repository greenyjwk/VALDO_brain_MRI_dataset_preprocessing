import os
import cv2
import numpy as np
import sys
import random
import nibabel as nib

IMG_SIZE = 2048
BOX_SIZE = 24  # 16x16
N_NEG_SAMPLES = None  # Exactly 2 samples
NEGATIVE_CLASS_ID = 1  # non-CMB class

def load_yolo_labels(label_path):
    print(label_path)
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

# generating brain mask from the csf region
def generate_brain_mask(image):
    mask = (image > 0).astype(np.uint8)
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask

def generate_csf_mask(csf_path, slice_num):
    csf_img = nib.load(csf_path)
    csf_img = csf_img.get_fdata()
    csf_img = csf_img[:, :, slice_num]  # Assuming the CSF mask is in the first slice
    csf_mask = csf_img.astype(np.uint8)
    csf_mask = np.rot90(csf_mask, k=1)
    return csf_mask


# def generate_negative_samples(csf_mask, original_image, box_size=8):
#     # Scale factor between mask and image
#     scale_factor = 4
    
#     # Size of box in mask coordinates
#     mask_box_size = box_size // scale_factor
    
#     h, w = csf_mask.shape
#     negatives = []
    
#     # Create used mask to track placed boxes
#     used_mask = np.zeros_like(csf_mask)
    
#     # Iterate through the mask in a grid pattern
#     for mask_y in range(0, h - mask_box_size + 1, mask_box_size):
#         for mask_x in range(0, w - mask_box_size + 1, mask_box_size):
#             mask_x1, mask_y1 = mask_x, mask_y
#             mask_x2, mask_y2 = mask_x + mask_box_size, mask_y + mask_box_size
            
#             # Check if the entire box region is valid CSF
#             box_region = csf_mask[mask_y1:mask_y2, mask_x1:mask_x2]
#             used_region = used_mask[mask_y1:mask_y2, mask_x1:mask_x2]
            
#             # Ensure box is fully within CSF and not already used
#             if (box_region.shape == (mask_box_size, mask_box_size) and 
#                 np.all(box_region == 1) and 
#                 np.all(used_region == 0)):
                
#                 # Convert to image coordinates
#                 x1 = mask_x1 * scale_factor
#                 y1 = mask_y1 * scale_factor
#                 x2 = mask_x2 * scale_factor
#                 y2 = mask_y2 * scale_factor
                
#                 # Check the percentage of black pixels in the original image
#                 img_box = original_image[y1:y2, x1:x2]
                
#                 if np.all(img_box == 0):
#                     continue
                
#                 black_pixel_percentage = np.sum(img_box == 0) / (box_size * box_size)
                
#                 # Skip if more than 50% of pixels are black
#                 if black_pixel_percentage > 0.8:
#                     continue

#                 negatives.append((x1, y1, x2, y2))

#                 # Mark region as used in mask space
#                 used_mask[mask_y1:mask_y2, mask_x1:mask_x2] = 1
                
#                 # Break if we've reached the desired number of samples
#                 if N_NEG_SAMPLES is not None and len(negatives) >= N_NEG_SAMPLES:
#                     return negatives[:N_NEG_SAMPLES]
    
#     return negatives[:N_NEG_SAMPLES] if N_NEG_SAMPLES is not None and negatives else negatives


def generate_negative_samples(csf_mask, original_image, min_box_size=5, max_box_size=10):
    scale_factor = int(original_image.shape[0] // csf_mask.shape[0])
    h, w = csf_mask.shape
    negatives = []
    
    # Create used mask to track placed boxes
    used_mask = np.zeros_like(csf_mask)
    
    # Iterate through the mask in a grid pattern
    for mask_y in range(0, h, min_box_size):
        for mask_x in range(0, w, min_box_size):
            # Randomly select a box size within the range
            box_size = random.randint(min_box_size, max_box_size)
            mask_box_size = box_size // scale_factor
            
            mask_x1, mask_y1 = mask_x, mask_y
            mask_x2, mask_y2 = mask_x + mask_box_size, mask_y + mask_box_size
            
            # Ensure the box is within bounds
            if mask_x2 > w or mask_y2 > h:
                continue
            
            # Check if the entire box region is valid CSF
            box_region = csf_mask[mask_y1:mask_y2, mask_x1:mask_x2]
            used_region = used_mask[mask_y1:mask_y2, mask_x1:mask_x2]
            
            # Ensure box is fully within CSF and not already used
            if (box_region.shape == (mask_box_size, mask_box_size) and 
                np.all(box_region == 1) and 
                np.all(used_region == 0)):
                
                # Convert to image coordinates
                x1 = mask_x1 * scale_factor
                y1 = mask_y1 * scale_factor
                x2 = mask_x2 * scale_factor
                y2 = mask_y2 * scale_factor
                
                # Check the percentage of black pixels in the original image
                img_box = original_image[y1:y2, x1:x2]
                
                if np.all(img_box == 0):
                    continue
                
                black_pixel_percentage = np.sum(img_box == 0) / (box_size * box_size)
                
                if black_pixel_percentage > 0.8:
                    continue

                negatives.append((x1, y1, x2, y2))
                used_mask[mask_y1:mask_y2, mask_x1:mask_x2] = 1
                if N_NEG_SAMPLES is not None and len(negatives) >= N_NEG_SAMPLES:
                    return negatives[:N_NEG_SAMPLES]
    
    return negatives[:N_NEG_SAMPLES] if N_NEG_SAMPLES is not None and negatives else negatives


def save_labels(output_path, original_labels, negative_boxes):
    lines = original_labels.copy()
    for box in negative_boxes:
        x1, y1, x2, y2 = box
        x_center = (x1 + x2) / 2 / IMG_SIZE
        y_center = (y1 + y2) / 2 / IMG_SIZE
        width = BOX_SIZE / IMG_SIZE
        height = BOX_SIZE / IMG_SIZE
        line = f"{NEGATIVE_CLASS_ID} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
        lines.append(line)

    with open(output_path, "w") as f:
        f.writelines(lines)

def main(images_path, labels_path, output_labels_path):
    csf_root_path = "/mnt/storage/ji/csf_segment_threshold_train"
    path_list = os.listdir(images_path)
    random.shuffle(path_list)
    for filename in path_list:
        print(filename)
        if filename.endswith((".jpg", ".png")):
            image_name = os.path.splitext(filename)[0]
            image_path = os.path.join(images_path, filename)
            label_path = os.path.join(labels_path, f"{image_name}.txt")
            uid = image_name.split("_")[0]
            slice_num = int(image_name.split("_")[2].split('.')[0])

            print(uid, "   ",slice_num)
            csf_path = os.path.join(csf_root_path, f"{uid}", "T1_seg_0.nii.gz")

            output_label_path = os.path.join(output_labels_path, f"{image_name}.txt")
            if not os.path.exists(label_path):
                open(label_path, "w").close()

            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            csf_mask = generate_csf_mask(csf_path, slice_num)
            negative_boxes = generate_negative_samples(csf_mask, image)

            with open(label_path, "r") as f:
                original_label_lines = f.readlines()
            save_labels(output_label_path, original_label_lines, negative_boxes)


if __name__ == "__main__":
    task = 'train'
    images_path = f"/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_epd_gt_box_t2s_GAN_cmbTrainOnly/images/{task}"
    labels_path = f"/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_epd_gt_box_t2s_GAN_cmbTrainOnly/labels/{task}"
    output_labels_path = f"/mnt/storage/ji/brain_mri_valdo_mayo/TEMP4_train/labels/{task}"

    os.makedirs(output_labels_path, exist_ok=True)
    main(images_path, labels_path, output_labels_path)