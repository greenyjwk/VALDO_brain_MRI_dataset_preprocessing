import nibabel as nib
import os
import argparse
import numpy as np
import json
from PIL import Image

def extract_slices(nifti_data):
    # if len(nifti_data.shape) != 3:
    #     raise ValueError("Only 3D NIfTI files are supported!")
    slices = [nifti_data[:, :, i, :] for i in range(nifti_data.shape[2])]
    return slices

def save_slices_as_png(slices, output_dir, base_name):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for i, slice in enumerate(slices):        
        '''
        Normalize slice to 0-1 range before scaling to 0-255
        But YOLO itself does scaling, so it might be deleted in the future.
        '''
        slice_normalized = (slice - np.min(slice)) / (np.max(slice) - np.min(slice))
        img = Image.fromarray(np.uint8(slice_normalized * 255), mode="RGB")
        
        img = img.rotate(90, expand=True)
        modified_name = base_name.split('_')[0] + "_" + f"{i:d}.png"
        img.save(os.path.join(output_dir, modified_name))

def generate_yolo_labels(label_file, nifti_data, output_dir):
    with open(label_file, 'r') as f:
        data = json.load(f)
    coordinates = data['label']
    base_name = os.path.splitext(os.path.basename(label_file))[0][:8]  # Use the first 8 characters of the file name
    width, height, _, ch = nifti_data.shape

    # bounding box size in pixels
    # bbox_size = 32

    for coord in coordinates:
        # x, y, z = coord
        x, y, z, gt_width, gt_height = coord

        # Calculate center of the bounding box
        x_center, y_center = x, y

        # Calculate bounding box dimensions
        gt_box_width, gt_box_height = gt_width, gt_height

        # YOLOv5 format (x_center, y)_center, bbox_width, bbox_height)
        x_center_norm = x_center / width
        y_center_norm = y_center / height
        bbox_width_norm = gt_box_width / width
        bbox_height_norm = gt_box_height / height

        label_path = os.path.join(output_dir, f"{base_name}_{z:d}.txt")
        print(f"Generating label file: {label_path}")
        with open(label_path, 'a') as f:
            f.write(f"0 {x_center_norm:.6f} {y_center_norm:.6f} {bbox_width_norm:.6f} {bbox_height_norm:.6f}\n")

def main():
    parser = argparse.ArgumentParser(description='Generate YOLO labels from Nifti files')
    parser.add_argument("--nifti_dir", type=str, default='/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_stacked')
    parser.add_argument("--output_dir", type=str, default='/media/Datacenter_storage/Ji/mayo_yolo_dataset_temp')
    parser.add_argument("--output_dir_end_name", type=str, default='yolo_dataset')
    args = parser.parse_args()

    nifti_dir = args.nifti_dir
    output_dir = os.path.join(args.output_dir, args.output_dir_end_name, "images", "test")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for mrn in os.listdir(nifti_dir):
        for nifti_file in os.listdir(os.path.join(nifti_dir, mrn)):
            nifti_path = os.path.join(nifti_dir, mrn, nifti_file)
            nifti_img = nib.load(nifti_path)
            nifti_data = nifti_img.get_fdata()

            if not os.path.exists(nifti_path):
                print(f"File {nifti_path} not found!")
                continue
            slices = extract_slices(nifti_data)
            base_name = nifti_file.split('.')[0]
            save_slices_as_png(slices, output_dir, base_name)

    label_dir = os.path.join(args.output_dir, "cmb_coordinates")
    label_files = [f for f in os.listdir(label_dir) if f.endswith('.json')]
    output_label_dir = os.path.join(args.output_dir, args.output_dir_end_name, "labels", "test")

    # Ensure the output directory exists
    if not os.path.exists(output_label_dir):
        os.makedirs(output_label_dir)

    for label_file in label_files:
        label_path = os.path.join(label_dir, label_file)
        nifti_file = os.path.join(nifti_dir, label_file.replace(".json", ""), os.path.basename(label_file).replace('.json', '.nii.gz'))
        nifti_img = nib.load(nifti_file)
        nifti_data = nifti_img.get_fdata()
        generate_yolo_labels(label_path, nifti_data, output_label_dir)

if __name__ == "__main__":
    main()

# python3 Mayo_for_YOLO.py --nifti_dir /media/Datacenter_storage/Ji/microbleeds2/DicomHandler/NIFTI_splitted --output_dir /media/Datacenter_storage/Ji/mayo_yolo_dataset --output_dir_end_name yolo_dataset_frame2