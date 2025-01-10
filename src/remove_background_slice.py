import os

images_dir = "/mnt/storage/ji/new_preprocessed_valdo/images/train"
labels_dir = "/mnt/storage/ji/new_preprocessed_valdo/labels/train"

for label_file in os.listdir(labels_dir):
    label_path = os.path.join(labels_dir, label_file)

    # Check if the label file is empty or contains only whitespace
    with open(label_path, 'r') as file:
        content = file.read().strip()
        if not content:
            image_file = label_file.replace('.txt', '.png')
            image_path = os.path.join(images_dir, image_file)
            os.remove(label_path)
            os.remove(image_path)
            print(f"Deleted: {label_path} and {image_path}")

print("Cleanup complete.")