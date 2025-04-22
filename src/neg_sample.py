import os
import cv2
import numpy as np
import sys
import random

IMG_SIZE = 2048
BOX_SIZE = 16
N_NEG_SAMPLES = 2  # Exactly 2 samples
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

def generate_brain_mask(image):
    mask = (image > 0).astype(np.uint8)
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask

# generating brain mask from the csf region
def generate_brain_mask(image):
    mask = (image > 0).astype(np.uint8)
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask


def generate_negative_samples(brain_mask):
    valid_coords = np.argwhere(brain_mask == 1)
    np.random.shuffle(valid_coords)

    negatives = []
    for y, x in valid_coords:
        x1 = x - BOX_SIZE // 2
        y1 = y - BOX_SIZE // 2
        x2 = x1 + BOX_SIZE
        y2 = y1 + BOX_SIZE

        if x1 < 0 or y1 < 0 or x2 > IMG_SIZE or y2 > IMG_SIZE:
            continue  # skip boxes out of bounds

        box_region = brain_mask[y1:y2, x1:x2]
        if box_region.shape != (BOX_SIZE, BOX_SIZE) or np.mean(box_region) < 0.95:
            continue

        negatives.append((x1, y1, x2, y2))

        if len(negatives) == N_NEG_SAMPLES:
            break

    return negatives

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

def main(images_path, labels_path, output_labels_path, ):
    
    path_list = os.listdir(images_path)
    random.shuffle(path_list)
    negative_num = 100
    for filename in path_list:
        if filename.endswith((".jpg", ".png")):
            
            image_name = os.path.splitext(filename)[0]
            image_path = os.path.join(images_path, filename)
            label_path = os.path.join(labels_path, f"{image_name}.txt")
            output_label_path = os.path.join(output_labels_path, f"{image_name}.txt")
            print(label_path)            
            if not os.path.exists(label_path):
                open(label_path, "w").close()

            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            brain_mask = generate_brain_mask(image)
            negative_boxes = generate_negative_samples(brain_mask)

            if os.path.getsize(label_path) <= 0: # if the text file is empty    
                negative_num -= 1
                with open(label_path, "r") as f:
                    original_label_lines = f.readlines()
                save_labels(output_label_path, original_label_lines, negative_boxes)
        if 0 == negative_num:
            break

if __name__ == "__main__":
    task = 'train'
    images_path = f"/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_epd_gt_box_t2s_GAN_2class/images/{task}"
    labels_path = f"/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_epd_gt_box_t2s_GAN_2class/labels/{task}"
    output_labels_path = f"/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_epd_gt_box_t2s_GAN_2class_TEMP/labels/{task}"
    # csf = f"/mnt/storage/ji/csf_segment"
    os.makedirs(output_labels_path, exist_ok=True)
    main(images_path, labels_path, output_labels_path)