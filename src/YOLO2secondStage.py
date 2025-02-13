# import json
# import cv2
# import os
# import numpy as np
# from pathlib import Path

# def calculate_iou(box1, box2):
#     """
#     Calculate IoU between two boxes
#     Boxes are in format [x, y, width, height]
#     """
#     # Convert to x1, y1, x2, y2
#     box1_x1 = box1[0]
#     box1_y1 = box1[1]
#     box1_x2 = box1[0] + box1[2]
#     box1_y2 = box1[1] + box1[3]
    
#     box2_x1 = box2[0]
#     box2_y1 = box2[1]
#     box2_x2 = box2[0] + box2[2]
#     box2_y2 = box2[1] + box2[3]
    
#     # Calculate intersection
#     x1 = max(box1_x1, box2_x1)
#     y1 = max(box1_y1, box2_y1)
#     x2 = min(box1_x2, box2_x2)
#     y2 = min(box1_y2, box2_y2)
    
#     if x2 < x1 or y2 < y1:
#         return 0.0
        
#     intersection = (x2 - x1) * (y2 - y1)
    
#     # Calculate union
#     box1_area = (box1_x2 - box1_x1) * (box1_y2 - box1_y1)
#     box2_area = (box2_x2 - box2_x1) * (box2_y2 - box2_y1)
#     union = box1_area + box2_area - intersection
    
#     return intersection / union if union > 0 else 0

# def extract_fixed_size_patch(image, center_x, center_y, patch_size=16):
#     """
#     Extract a fixed-size patch centered on the given coordinates
#     Ensures output is exactly patch_size x patch_size
#     """
#     height, width = image.shape[:2]
#     half_size = patch_size // 2
    
#     # Calculate patch boundaries
#     x_min = int(center_x - half_size)
#     y_min = int(center_y - half_size)
#     x_max = int(x_min + patch_size)  # Force patch_size width
#     y_max = int(y_min + patch_size)  # Force patch_size height
    
#     # Create empty patch
#     patch = np.zeros((patch_size, patch_size, 3), dtype=np.uint8)
    
#     # Calculate valid regions
#     valid_x_min = max(0, x_min)
#     valid_x_max = min(width, x_max)
#     valid_y_min = max(0, y_min)
#     valid_y_max = min(height, y_max)
    
#     # Calculate placement in patch
#     patch_x_start = max(0, -x_min)
#     patch_y_start = max(0, -y_min)
    
#     # Copy valid region
#     valid_region = image[valid_y_min:valid_y_max, valid_x_min:valid_x_max]
#     patch[patch_y_start:patch_y_start + valid_region.shape[0], 
#           patch_x_start:patch_x_start + valid_region.shape[1]] = valid_region
    
#     return patch

# def process_patches(json_data, image_dir, output_base_dir):
#     """
#     Process patches and save them to appropriate folders based on score and IOU
#     If no score_one_boxes exist, save all patches to cmb-mimic
#     """
#     # Create output directories
#     cmb_dir = Path(output_base_dir) / 'cmb'
#     cmb_mimic_dir = Path(output_base_dir) / 'cmb-mimic'
#     cmb_dir.mkdir(parents=True, exist_ok=True)
#     cmb_mimic_dir.mkdir(parents=True, exist_ok=True)
    
#     # Group boxes by image_id
#     boxes_by_image = {}
#     for item in json_data:
#         image_id = item['image_id']
#         if image_id not in boxes_by_image:
#             boxes_by_image[image_id] = []
#         boxes_by_image[image_id].append(item)
    
#     # Process each image
#     for image_id, boxes in boxes_by_image.items():
#         image_path = Path(image_dir) / f"{image_id}.png"
#         if not image_path.exists():
#             print(f"Image not found: {image_path}")
#             continue
        
#         # Read image
#         image = cv2.imread(str(image_path))
#         if image is None:
#             print(f"Could not read image: {image_path}")
#             continue
            
#         height, width = image.shape[:2]
        
#         # First, find boxes with score == 1
#         score_one_boxes = []
#         for box in boxes:
#             if box['score'] == 1:
#                 bbox = box['bbox']
#                 score_one_boxes.append({
#                     'box': bbox,
#                     'original': box
#                 })
                
#                 # Extract and save patch for score == 1
#                 center_x = bbox[0] + bbox[2]/2
#                 center_y = bbox[1] + bbox[3]/2
#                 patch = extract_fixed_size_patch(image, center_x, center_y)
#                 patch_path = cmb_dir / f"{image_id}_x{int(center_x)}_y{int(center_y)}.png"
#                 cv2.imwrite(str(patch_path), patch)
        
#         # If no score_one_boxes exist, save all patches to cmb-mimic
#         if not score_one_boxes:
#             for box in boxes:
#                 bbox = box['bbox']
#                 center_x = bbox[0] + bbox[2]/2
#                 center_y = bbox[1] + bbox[3]/2
#                 patch = extract_fixed_size_patch(image, center_x, center_y)
#                 patch_path = cmb_mimic_dir / f"{image_id}_x{int(center_x)}_y{int(center_y)}.png"
#                 cv2.imwrite(str(patch_path), patch)
#         else:
#             # Process other boxes for IOU check
#             for box in boxes:
#                 if box['score'] == 1.0:
#                     continue
                    
#                 current_bbox = box['bbox']
#                 center_x = current_bbox[0] + current_bbox[2]/2
#                 center_y = current_bbox[1] + current_bbox[3]/2
                
#                 # Check IOU with score == 1 boxes
#                 for score_one_box in score_one_boxes:
#                     iou = calculate_iou(current_bbox, score_one_box['box'])
#                     if iou < 0.7:
#                         # Extract and save patch
#                         patch = extract_fixed_size_patch(image, center_x, center_y)
#                         patch_path = cmb_mimic_dir / f"{image_id}_x{int(center_x)}_y{int(center_y)}.png"
#                         cv2.imwrite(str(patch_path), patch)
#                         break

# # Main execution
# if __name__ == "__main__":
#     # Load JSON data
#     json_path = "/mnt/storage/ji/runs/detect/val4/predictions.json"
#     with open(json_path, 'r') as f:
#         json_data = json.load(f)
    
#     # Set directories
#     image_dir = "/mnt/storage/ji/brain_mri_valdo_mayo/YOLO_valdo_stacked/images/val"
#     output_base_dir = "/mnt/storage/ji/patch_output"
    
#     # Process patches
#     process_patches(json_data, image_dir, output_base_dir)  

    
import json
import cv2
import os
import numpy as np
from pathlib import Path

def is_background_patch(patch, threshold=2, pixel_threshold=0.95):
    """
    Check if a patch is background (mostly black)
    threshold: pixel intensity threshold (0-255)
    pixel_threshold: percentage of dark pixels required to be considered background
    """
    # Convert to grayscale if needed
    if len(patch.shape) == 3:
        gray_patch = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)
    else:
        gray_patch = patch
    
    # Count dark pixels
    dark_pixels = np.sum(gray_patch < threshold)
    total_pixels = patch.shape[0] * patch.shape[1]
    
    # Return True if the percentage of dark pixels exceeds the threshold
    return (dark_pixels / total_pixels) > pixel_threshold

def calculate_iou(box1, box2):
    """
    Calculate IoU between two boxes
    Boxes are in format [x, y, width, height]
    """
    # Convert to x1, y1, x2, y2
    box1_x1 = box1[0]
    box1_y1 = box1[1]
    box1_x2 = box1[0] + box1[2]
    box1_y2 = box1[1] + box1[3]
    
    box2_x1 = box2[0]
    box2_y1 = box2[1]
    box2_x2 = box2[0] + box2[2]
    box2_y2 = box2[1] + box2[3]
    
    # Calculate intersection
    x1 = max(box1_x1, box2_x1)
    y1 = max(box1_y1, box2_y1)
    x2 = min(box1_x2, box2_x2)
    y2 = min(box1_y2, box2_y2)
    
    if x2 < x1 or y2 < y1:
        return 0.0
        
    intersection = (x2 - x1) * (y2 - y1)
    
    # Calculate union
    box1_area = (box1_x2 - box1_x1) * (box1_y2 - box1_y1)
    box2_area = (box2_x2 - box2_x1) * (box2_y2 - box2_y1)
    union = box1_area + box2_area - intersection
    
    return intersection / union if union > 0 else 0

def extract_fixed_size_patch(image, center_x, center_y, patch_size=16):
    """
    Extract a fixed-size patch centered on the given coordinates
    Ensures output is exactly patch_size x patch_size
    """
    height, width = image.shape[:2]
    half_size = patch_size // 2
    
    # Calculate patch boundaries
    x_min = int(center_x - half_size)
    y_min = int(center_y - half_size)
    x_max = int(x_min + patch_size)
    y_max = int(y_min + patch_size)
    
    # Create empty patch
    patch = np.zeros((patch_size, patch_size, 3), dtype=np.uint8)
    
    # Calculate valid regions
    valid_x_min = max(0, x_min)
    valid_x_max = min(width, x_max)
    valid_y_min = max(0, y_min)
    valid_y_max = min(height, y_max)
    
    # Calculate placement in patch
    patch_x_start = max(0, -x_min)
    patch_y_start = max(0, -y_min)
    
    # Copy valid region
    valid_region = image[valid_y_min:valid_y_max, valid_x_min:valid_x_max]
    patch[patch_y_start:patch_y_start + valid_region.shape[0], 
          patch_x_start:patch_x_start + valid_region.shape[1]] = valid_region
    
    return patch

def process_patches(json_data, image_dir, output_base_dir):
    """
    Process patches and save them to appropriate folders based on score and IOU
    Skip background patches
    """
    # Create output directories
    cmb_dir = Path(output_base_dir) / 'cmb'
    cmb_mimic_dir = Path(output_base_dir) / 'cmb-mimic'
    cmb_dir.mkdir(parents=True, exist_ok=True)
    cmb_mimic_dir.mkdir(parents=True, exist_ok=True)
    
    # Group boxes by image_id
    boxes_by_image = {}
    for item in json_data:
        image_id = item['image_id']
        if image_id not in boxes_by_image:
            boxes_by_image[image_id] = []
        boxes_by_image[image_id].append(item)
    
    # Process each image
    for image_id, boxes in boxes_by_image.items():
        image_path = Path(image_dir) / f"{image_id}.png"
        if not image_path.exists():
            print(f"Image not found: {image_path}")
            continue
        
        # Read image
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"Could not read image: {image_path}")
            continue
            
        height, width = image.shape[:2]
        
        # First, find boxes with score == 1
        score_one_boxes = []
        for box in boxes:
            if box['score'] == 1:
                bbox = box['bbox']
                center_x = bbox[0] + bbox[2]/2
                center_y = bbox[1] + bbox[3]/2
                
                # Extract patch and check if it's background
                patch = extract_fixed_size_patch(image, center_x, center_y)
                if not is_background_patch(patch):
                    score_one_boxes.append({
                        'box': bbox,
                        'original': box
                    })
                    
                    # Save patch
                    patch_path = cmb_dir / f"{image_id}_x{int(center_x)}_y{int(center_y)}.png"
                    cv2.imwrite(str(patch_path), patch)
        
        # If no score_one_boxes exist, save all non-background patches to cmb-mimic
        if not score_one_boxes:
            for box in boxes:
                bbox = box['bbox']
                center_x = bbox[0] + bbox[2]/2
                center_y = bbox[1] + bbox[3]/2
                
                patch = extract_fixed_size_patch(image, center_x, center_y)
                if not is_background_patch(patch):
                    patch_path = cmb_mimic_dir / f"{image_id}_x{int(center_x)}_y{int(center_y)}.png"
                    cv2.imwrite(str(patch_path), patch)
        else:
            # Process other boxes for IOU check
            for box in boxes:
                if box['score'] == 1:
                    continue
                    
                current_bbox = box['bbox']
                center_x = current_bbox[0] + current_bbox[2]/2
                center_y = current_bbox[1] + current_bbox[3]/2
                
                # First check if patch is background
                patch = extract_fixed_size_patch(image, center_x, center_y)
                if is_background_patch(patch):
                    continue
                
                # Check IOU with score == 1 boxes
                for score_one_box in score_one_boxes:
                    iou = calculate_iou(current_bbox, score_one_box['box'])
                    if iou < 0.3:
                        # Save patch
                        patch_path = cmb_mimic_dir / f"{image_id}_x{int(center_x)}_y{int(center_y)}.png"
                        cv2.imwrite(str(patch_path), patch)
                        break

# Main execution
if __name__ == "__main__":
    # Load JSON data
    json_path = "/mnt/storage/ji/runs/detect/train_for_2nd_stage2/predictions.json"
    with open(json_path, 'r') as f:
        json_data = json.load(f)
    
    # Set directories
    image_dir = "/mnt/storage/ji/brain_mri_valdo_mayo/YOLO_valdo_stacked/images/train"
    output_base_dir = "/mnt/storage/ji/patch_output_train"
    
    # Process patches
    process_patches(json_data, image_dir, output_base_dir)