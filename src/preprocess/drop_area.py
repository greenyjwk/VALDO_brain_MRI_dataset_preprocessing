import csv
import os
import sys

def main():
    # Define the paths
    csv_file_path = '/mnt/storage/ji/valdo_resample_ALFA_bbox_distribution/cmb_patch_areas.csv'
    labels_path = '/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_all_slices/labels/val'
    
    # Read the CSV file and collect filenames and bounding boxes with area 1
    to_remove = []
    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:    
            if float(row['area']) == 3:
                filename = row['filename'].replace('.png', '.txt')
                bbox = [int(float(row['class_id'])), row['center_x'], row['center_y'], row['width'], row['height']]
                to_remove.append((filename, bbox))
                
    # Function to format YOLO bounding box
    def format_bbox(bbox):
        return ' '.join(map(str, bbox))

    # Process each file and remove the corresponding bounding boxes
    for filename, bbox in to_remove:
        file_path = os.path.join(labels_path, filename+'.txt')
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                lines = file.readlines()
            bbox_str = format_bbox(bbox)
            with open(file_path, 'w') as file:
                for line in lines:
                    
                    if line.strip() != bbox_str:
                        file.write(line)
                        
if __name__ == "__main__":
    main()