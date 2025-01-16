import os
import sys
import nibabel as nib
import numpy as np
from PIL import Image
from scipy import ndimage
from sklearn.model_selection import train_test_split

num_256, num_512 = 0, 0

def get_instance_bounding_boxes(mask):
    # Label connected components
    labeled_mask, num_labels = ndimage.label(mask)
    bboxes = []
    for label in range(1, num_labels + 1):
        instance_mask = labeled_mask == label
        rows = np.any(instance_mask, axis=1)
        cols = np.any(instance_mask, axis=0)
        y_min, y_max = np.where(rows)[0][[0, -1]]
        x_min, x_max = np.where(cols)[0][[0, -1]]
        bboxes.append((x_min, y_min, x_max, y_max))
    return bboxes

def process_nifti(mask_path, vol_path, output_dir, subject_id, task):
    global num_512
    global num_256
    # Load the NIfTI files
    mask_nifti = nib.load(mask_path)
    mask_data = mask_nifti.get_fdata()
    vol_nifti = nib.load(vol_path)
    vol_data = vol_nifti.get_fdata()

    print(f"Processing subject {subject_id}")
    print(f"Mask shape: {mask_data.shape}")
    if mask_data.shape[0] == 256:
        num_256 = num_256 + 1
    print(f"Volume shape: {vol_data.shape}")
    if mask_data.shape[0] == 512:
        num_512 = num_512 + 1
    original_volume = vol_data
    segmentation_mask = mask_data
    os.makedirs(os.path.join(output_dir, 'images', task), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'labels', task), exist_ok=True)

    # for z in range(original_volume.shape[2]):
    #     slice_data = original_volume[:, :, z, :]
    #     # slice_data = original_volume[:, :, z, 2]    # choosing only one channel from 3 channels
    #     mask_slice = segmentation_mask[:, :, z]

    #     # Normalize and save the image slice
    #     slice_data = (255 * ((slice_data - slice_data.min()) / (slice_data.max() - slice_data.min()))).astype(np.uint8)
    #     slice_img = Image.fromarray(slice_data)
    #     slice_img.save(os.path.join(output_dir, 'images', task, f'{subject_id}_slice_{z:03d}.png'))


    for z in range(original_volume.shape[2]):
        # Get the slice with all channels
        slice_data = original_volume[:, :, z, :]  # Shape: (height, width, 3)
        mask_slice = segmentation_mask[:, :, z]
        
        # Normalize each channel separately
        normalized_slice = np.zeros_like(slice_data, dtype=np.uint8)  # Explicitly create uint8 array
        for c in range(slice_data.shape[-1]):
            channel_data = slice_data[:, :, c]
            if channel_data.max() != channel_data.min():  # Avoid division by zero
                normalized_slice[:, :, c] = (255 * ((channel_data - channel_data.min()) / 
                                                (channel_data.max() - channel_data.min()))).astype(np.uint8)
            else:
                normalized_slice[:, :, c] = np.zeros_like(channel_data, dtype=np.uint8)

        # Debug prints
        print(f"Normalized slice shape: {normalized_slice.shape}")
        print(f"Normalized slice dtype: {normalized_slice.dtype}")
        
        # Make sure the array is contiguous before converting to image
        normalized_slice = np.ascontiguousarray(normalized_slice)
        
        # Save the image slice
        slice_img = Image.fromarray(normalized_slice, mode='RGB')  # Explicitly specify RGB mode
        slice_img.save(os.path.join(output_dir, 'images', task, f'{subject_id}_slice_{z:03d}.png'))
        



        # Get 2D bounding boxes for each instance in this slice
        bboxes = get_instance_bounding_boxes(mask_slice)

        if bboxes:
            # Convert to YOLO format
            img_height, img_width, ch = slice_data.shape
            yolo_bboxes = []
            for bbox in bboxes:
                x_center = (bbox[0] + bbox[2]) / (2 * img_width)
                y_center = (bbox[1] + bbox[3]) / (2 * img_height)
                width = (bbox[2] - bbox[0]) / img_width
                height = (bbox[3] - bbox[1]) / img_height
                yolo_bboxes.append(f"0 {x_center} {y_center} {width} {height}")

            # Save YOLO annotation
            with open(os.path.join(output_dir, 'labels', task, f'{subject_id}_slice_{z:03d}.txt'), 'w') as f:
                f.write('\n'.join(yolo_bboxes))
        else:
            with open(os.path.join(output_dir, 'labels', task, f'{subject_id}_slice_{z:03d}.txt'), 'w') as f:
                pass

def process_all_subjects(original_data_dir, preprocessed_img_dir, output_dir):
    train, val = get_train_val(original_data_dir)

    for train_mask_path in train:
        train_mask_path = train_mask_path.split('/')[-1]
        train_subject_id = train_mask_path.split('_')[0]
        train_mask_path = train_mask_path.split('_')[:2]
        train_mask_path = train_mask_path[0] + '_' + train_mask_path[1] + '_CMB.nii.gz'

        # Construct the corresponding volume file path
        vol_path = os.path.join(preprocessed_img_dir, train_subject_id, f'{train_subject_id}.nii.gz')   # preprcessed img path
        train_mask_path =  os.path.join(original_data_dir, train_subject_id, train_mask_path)           # original mask path

        print("vol_path", vol_path)
        print("train_mask_path", train_mask_path)
        
        if os.path.exists(vol_path):
            process_nifti(train_mask_path, vol_path, output_dir, train_subject_id, task='train')
        else:
            print(f"Volume file not found for subject {train_subject_id}")

    for val_mask_path in val:
        val_mask_path = val_mask_path.split('/')[-1]
        val_subject_id = val_mask_path.split('_')[0]
        val_mask_path = val_mask_path.split('_')[:2]
        val_mask_path = val_mask_path[0] + '_' + val_mask_path[1] + '_CMB.nii.gz'

        # vol_path = os.path.join(preprocessed_img_dir, f'{val_subject_id}_space-T2S_desc-masked_T2S.nii.gz')
        # vol_path = os.path.join(preprocessed_img_dir, val_subject_id, f'{val_subject_id}_space-T2S_desc-masked_T2S.nii.gz')
        vol_path = os.path.join(preprocessed_img_dir, val_subject_id, f'{val_subject_id}.nii.gz') # For the 3 channel volume
        val_mask_path =  os.path.join(original_data_dir, val_subject_id, val_mask_path)

        if os.path.exists(vol_path):
            process_nifti(val_mask_path, vol_path, output_dir, val_subject_id, task='val')
        else:
            print(f"Volume file not found for subject {val_subject_id}")

def get_train_val(root_dir):
    cmb_group = []
    non_cmb_group = []
    # Iterate through all files in the subdirectories
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file == ".DS_Store":
                continue
            file_path = os.path.join(subdir, file)

            # Load the NIfTI file
            nifti_img = nib.load(file_path)
            nifti_data = nifti_img.get_fdata()
            unique_values = np.unique(nifti_data)

            # Check the unique values and categorize the file
            if set(unique_values) == {0, 1}:
                cmb_group.append(file_path)
            elif set(unique_values) == {0}:
                non_cmb_group.append(file_path)

    # Split the files into training and validation sets
    train_cmb_group, val_cmb_group = train_test_split(cmb_group, test_size=0.2, random_state=42)
    train_non_cmb_group, val_non_cmb_group = train_test_split(non_cmb_group, test_size=0.2, random_state=42)

    # Combine the training and validation sets from both groups
    train_files = train_cmb_group + train_non_cmb_group
    val_files = val_cmb_group + val_non_cmb_group

    # Print the results
    print("Training files:")
    for file in train_files:
        print(file)

    print("\nValidation files:")
    for file in val_files:
        print(file)
    return train_files, val_files

def main():
    original_data_dir = "/mnt/storage/cmb_segmentation_dataset/Task2"
    preprocessed_img_dir = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_stacked"
    output_dir = "/mnt/storage/ji/brain_mri_valdo_mayo/YOLO_valdo_stacked_temp"
    process_all_subjects(original_data_dir, preprocessed_img_dir, output_dir)

if __name__ == "__main__":
    main()