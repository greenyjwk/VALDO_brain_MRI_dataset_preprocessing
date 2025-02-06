import csv
import os
import sys

def main():
    # Define the paths
    csv_file_path = '/mnt/storage/ji/cmb_analysis_results_0205_2/cmb_patch_areas.csv'
    labels_path = '/mnt/storage/ji/brain_mri_valdo_mayo/YOLO_valdo_stacked_1mm_png_pm2_0205__temp/labels/train'
    
    # Read the CSV file and collect filenames and bounding boxes with area 1
    to_remove = []
    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:    
            if float(row['area']) == 1:
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
                    print("bbox_str: ", bbox_str)
                    print("line.strip: ", line.strip())
                    print()
                    print()
                    if line.strip() != bbox_str:
                        file.write(line)
                        
if __name__ == "__main__":
    main()