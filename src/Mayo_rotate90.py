import os
import cv2
import numpy as np
from pathlib import Path

def rotate_yolo_bbox(x_center, y_center, width, height, img_width, img_height):
    """
    Rotate bbox 90 degrees clockwise.
    Input coordinates are normalized YOLO format.
    """
    # Convert to absolute coordinates
    x_center = x_center * img_width
    y_center = y_center * img_height
    width = width * img_width
    height = height * img_height
    
    # Rotate center point 90 degrees clockwise
    new_x = img_height - y_center
    new_y = x_center
    
    # Swap width and height
    new_width = height
    new_height = width
    
    # Convert back to normalized coordinates
    # Note: After rotation, img_width and img_height are swapped
    new_x_norm = new_x / img_height  # using original height as new width
    new_y_norm = new_y / img_width   # using original width as new height
    new_width_norm = new_width / img_height
    new_height_norm = new_height / img_width
    
    return new_x_norm, new_y_norm, new_width_norm, new_height_norm

def process_files(image_dir, label_dir):
    # Create output directories
    output_image_dir = os.path.join(image_dir, 'rotated')
    output_label_dir = os.path.join(label_dir, 'rotated')
    os.makedirs(output_image_dir, exist_ok=True)
    os.makedirs(output_label_dir, exist_ok=True)
    
    # Process each image
    for img_path in Path(image_dir).glob('*.png'):
        # Read and rotate image
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"Could not read image: {img_path}")
            continue
            
        img_height, img_width = img.shape[:2]
        rotated_img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        
        # Save rotated image
        output_img_path = os.path.join(output_image_dir, img_path.name)
        cv2.imwrite(output_img_path, rotated_img)
        print(f"Processed image: {img_path.name}")
        
        # Check if corresponding label exists
        label_path = os.path.join(label_dir, img_path.stem + '.txt')
        if os.path.exists(label_path):
            # Process labels
            with open(label_path, 'r') as f:
                labels = f.readlines()
                
            new_labels = []
            for label in labels:
                parts = label.strip().split()
                if len(parts) != 5:
                    print(f"Invalid label format in {label_path}")
                    continue
                    
                class_id = parts[0]
                x_center, y_center, width, height = map(float, parts[1:])
                
                # Rotate bbox
                new_x, new_y, new_w, new_h = rotate_yolo_bbox(
                    x_center, y_center, width, height, img_width, img_height
                )
                
                new_labels.append(f"{class_id} {new_x:.6f} {new_y:.6f} {new_w:.6f} {new_h:.6f}")
            
            # Save rotated labels
            output_label_path = os.path.join(output_label_dir, img_path.stem + '.txt')
            with open(output_label_path, 'w') as f:
                f.write('\n'.join(new_labels))
            print(f"Processed label: {img_path.stem}.txt")
        else:
            print(f"No label file found for: {img_path.name} (skipping label)")

# Replace these paths with your actual paths
image_dir = '/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_yolo_t2s_only_rotated/images/test'
label_dir = '/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_yolo_t2s_only_rotated/labels/test'

process_files(image_dir, label_dir)