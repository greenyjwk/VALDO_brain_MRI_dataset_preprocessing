import os
import json
import glob
from PIL import Image
import argparse
from tqdm import tqdm
import numpy as np

def yolo_to_coco(yolo_dataset_path, output_path, task, categories=None):
    # Initialize COCO format structure
    coco_format = {
        "images": [],
        "annotations": [],
        "categories": []
    }
    
    # Get category names
    if categories is None:
        try:
            with open(os.path.join(yolo_dataset_path, "classes.txt"), 'r') as f:
                categories = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            raise FileNotFoundError("classes.txt not found. Please provide category names.")
    
    # Add categories to COCO format
    for i, category in enumerate(categories):  # COCO IDs start from 1
        coco_format["categories"].append({
            "id": i,
            "name": category
        })
    
    # Get all image files
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
    image_paths = []
    for ext in image_extensions:
        image_paths.extend(glob.glob(os.path.join(yolo_dataset_path, f'images/{task}', ext)))
    

    print(image_paths)
    annotation_id = 1
    
    # Process each image and its annotations
    for img_id, img_path in enumerate(tqdm(image_paths, desc="Converting")):
        img_filename = os.path.basename(img_path)
        img_name_without_ext = os.path.splitext(img_filename)[0]
        
        # Get image dimensions
        with Image.open(img_path) as img:
            width, height = img.size
        
        # Add image info to COCO format
        coco_format["images"].append({
            "id": img_id,
            "file_name": img_filename,
            "width": width,
            "height": height
        })
        
        # Look for the corresponding annotation file
        ann_path = os.path.join(yolo_dataset_path, f'labels/{task}', f"{img_name_without_ext}.txt")
        
        if os.path.exists(ann_path):
            with open(ann_path, 'r') as f:
                lines = f.readlines()
                
                for line in lines:
                    line = line.strip().split()
                    if len(line) < 5:  # Skip invalid lines
                        continue
                    
                    # Parse YOLO format (class_id, x_center, y_center, width, height)
                    class_id = int(line[0])
                    x_center = float(line[1])
                    y_center = float(line[2])
                    box_width = float(line[3])
                    box_height = float(line[4])
                    
                    # Convert YOLO's normalized coordinates to COCO pixel coordinates
                    x_min = int((x_center - box_width/2) * width)
                    y_min = int((y_center - box_height/2) * height)
                    bbox_width = int(box_width * width)
                    bbox_height = int(box_height * height)
                    
                    # Ensure coordinates are valid
                    x_min = max(0, x_min)
                    y_min = max(0, y_min)
                    bbox_width = min(width - x_min, bbox_width)
                    bbox_height = min(height - y_min, bbox_height)
                    
                    # Skip invalid boxes
                    if bbox_width <= 0 or bbox_height <= 0:
                        continue
                    
                    # COCO's category_id starts from 1, but YOLO's class_id starts from 0
                    category_id = class_id
                    
                    # Add annotation to COCO format
                    coco_format["annotations"].append({
                        "id": annotation_id,
                        "image_id": img_id,
                        "category_id": category_id,
                        "bbox": [x_min, y_min, bbox_width, bbox_height],
                        "area": bbox_width * bbox_height,
                        "iscrowd": 0
                    })
                    
                    annotation_id += 1
    
    
    output_path = os.path.join(output_path, f"{task}.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save to JSON file
    with open(output_path, 'w') as f:
        json.dump(coco_format, f, indent=4)
    
    print(f"Conversion complete! COCO format annotations saved to {output_path}")
    print(f"Converted {len(coco_format['images'])} images and {len(coco_format['annotations'])} annotations.")

def coco_to_yolo(coco_json_path, output_dir):
    """
    Convert COCO format annotations to YOLO format.
    
    Args:
        coco_json_path: Path to the COCO json file
        output_dir: Directory to save YOLO format files
    """
    # Create output directories
    labels_dir = os.path.join(output_dir, 'labels')
    os.makedirs(labels_dir, exist_ok=True)
    
    # Load COCO json
    with open(coco_json_path, 'r') as f:
        coco_data = json.load(f)
    
    # Create a dictionary mapping image_id to file_name
    image_dict = {img['id']: img for img in coco_data['images']}
    
    # Create a dictionary mapping category_id to index (YOLO uses 0-indexed class IDs)
    category_map = {cat['id']: i for i, cat in enumerate(coco_data['categories'])}
    
    # Write class names to classes.txt
    with open(os.path.join(output_dir, 'classes.txt'), 'w') as f:
        for cat in sorted(coco_data['categories'], key=lambda x: category_map[x['id']]):
            f.write(f"{cat['name']}\n")
    
    # Group annotations by image_id
    annotations_by_image = {}
    for ann in coco_data['annotations']:
        image_id = ann['image_id']
        if image_id not in annotations_by_image:
            annotations_by_image[image_id] = []
        annotations_by_image[image_id].append(ann)
    
    # Process each image
    for img_id, img_info in tqdm(image_dict.items(), desc="Converting"):
        filename = os.path.splitext(img_info['file_name'])[0]
        img_width = img_info['width']
        img_height = img_info['height']
        
        # Get annotations for this image
        annotations = annotations_by_image.get(img_id, [])
        
        # Create YOLO annotation file
        with open(os.path.join(labels_dir, f"{filename}.txt"), 'w') as f:
            for ann in annotations:
                # Get category index (0-indexed for YOLO)
                category_idx = category_map[ann['category_id']]
                
                # Extract bounding box coordinates (COCO: [x_min, y_min, width, height])
                x_min, y_min, width, height = ann['bbox']
                
                # Convert to YOLO format (center_x, center_y, width, height, normalized)
                x_center = (x_min + width / 2) / img_width
                y_center = (y_min + height / 2) / img_height
                norm_width = width / img_width
                norm_height = height / img_height
                
                # Write to file
                f.write(f"{category_idx} {x_center:.6f} {y_center:.6f} {norm_width:.6f} {norm_height:.6f}\n")
    
    print(f"Conversion complete! YOLO format annotations saved to {labels_dir}")
    print(f"Converted annotations for {len(image_dict)} images.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert between YOLO and COCO annotation formats")
    parser.add_argument("--mode", type=str, required=True, choices=["yolo2coco", "coco2yolo"], 
                      help="Conversion mode: yolo2coco or coco2yolo")
    parser.add_argument("--input", type=str, required=True, 
                      help="Input path: YOLO dataset directory or COCO JSON file")
    parser.add_argument("--output", type=str, required=True, 
                      help="Output path: COCO JSON file or YOLO dataset directory")
    
    parser.add_argument("--task", type=str, required=True)
    parser.add_argument("--categories", nargs='+', help="Category names (only needed for YOLO to COCO if classes.txt is missing)")
    
    args = parser.parse_args()
    
    if args.mode == "yolo2coco":
        yolo_to_coco(args.input, args.output, args.task, args.categories)
    else:
        coco_to_yolo(args.input, args.output)

# python3 yolo2coco.py --mode yolo2coco --input /media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_yolo_t2s_only_rotated/images --output /media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_yolo_t2s_only_rotated_coco/annotations.json --categories cmb
# python3 /mnt/storage/ji/VALDO_brain_MRI_dataset_preprocessing/src/yolo2coco.py --mode yolo2coco --input /mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_epd_gt_box_allSequence_cmb_slice_only_train_small_dropped --output /mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_epd_gt_box_allSequence_cmb_slice_only_train_small_dropped_coco/val.json --categories cmb
# python3 /mnt/storage/ji/VALDO_brain_MRI_dataset_preprocessing/src/yolo2coco.py --mode yolo2coco --input /mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_epd_gt_box_t2s_cmb_slice_only_train_16px_2cls_upright --output /mnt/storage/ji/brain_mri_valdo_mayo/2cls_coco --task train --categories cmb non-cmb

# python3 /mnt/storage/ji/VALDO_brain_MRI_dataset_preprocessing/src/yolo2coco.py --mode yolo2coco --input /mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_epd_gt_box_t2s_GAN_3slices_cmbTrainOnly --output /mnt/storage/ji/brain_mri_valdo_mayo/3slice_coco --task train --categories cmb




# python3 yolo2coco.py --mode yolo2coco --input /media/Datacenter_storage/Ji/valdo_dataset/valdo_t2s_cmbOnly_GAN/images --output /media/Datacenter_storage/Ji/valdo_dataset/valdo_t2s_cmbOnly_GAN/annotations.json --categories cmb