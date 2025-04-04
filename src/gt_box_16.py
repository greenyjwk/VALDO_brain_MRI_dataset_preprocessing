import os

labels_dir = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_epd_gt_box_t2s_cmb_slice_only_train_16px_2cls/labels/train"
fixed_width, fixed_height = 16 / 512, 16 / 512

# Process each label file
for filename in os.listdir(labels_dir):
    if filename.endswith(".txt"):
        file_path = os.path.join(labels_dir, filename)
        with open(file_path, "r") as file:
            lines = file.readlines()
            print(lines)
        new_lines = []
        for line in lines:
            class_id, x_center, y_center, _, _ = line.strip().split()
            new_line = f"{class_id} {x_center} {y_center} {fixed_width:.6f} {fixed_height:.6f}\n"
            new_lines.append(new_line)

        # Save the modified labels back to the file
        with open(file_path, "w") as file:
            file.writelines(new_lines)

print("All labels adjusted to 16x16 pixel bounding boxes successfully!")
