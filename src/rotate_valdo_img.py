import os
import cv2

def rotate_image(image_path, output_path):
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to read image: {image_path}")
        return
    # Rotate 90 degrees counter-clockwise
    rotated_image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    
    print("output_path: ", output_path)
    # Save the rotated image
    cv2.imwrite(output_path, rotated_image)

def rotate_yolo_label(label_path, output_path, img_width, img_height):
    if not os.path.exists(label_path):
        print(f"Label file not found: {label_path}")
        return

    rotated_labels = []
    with open(label_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            parts = line.strip().split()
            if len(parts) < 5:
                continue  # Skip invalid lines
            class_id, x_center, y_center, width, height = map(float, parts)
            
            # Rotate YOLO coordinates
            new_x_center = y_center
            new_y_center = 1 - x_center
            new_width = height
            new_height = width
            
            rotated_labels.append(f"{int(class_id)} {new_x_center:.6f} {new_y_center:.6f} {new_width:.6f} {new_height:.6f}\n")
    
    print("label_path: ", label_path)
    # Save the rotated labels
    with open(output_path, "w") as f:
        f.writelines(rotated_labels)

def process_dataset(images_dir, labels_dir, output_images_dir, output_labels_dir):
    os.makedirs(output_images_dir, exist_ok=True)
    os.makedirs(output_labels_dir, exist_ok=True)

    for filename in os.listdir(images_dir):
        if filename.endswith((".jpg", ".png")):
            # Paths for images and labels
            image_path = os.path.join(images_dir, filename)
            label_path = os.path.join(labels_dir, f"{os.path.splitext(filename)[0]}.txt")
            output_image_path = os.path.join(output_images_dir, filename)
            output_label_path = os.path.join(output_labels_dir, f"{os.path.splitext(filename)[0]}.txt")
            
            print(image_path)
            # Get image dimensions
            image = cv2.imread(image_path)
            if image is None:
                print(f"Failed to read image: {image_path}")
                continue
            img_height, img_width = image.shape[:2]
            
            # Rotate image and label
            rotate_image(image_path, output_image_path)
            rotate_yolo_label(label_path, output_label_path, img_width, img_height)

if __name__ == "__main__":
    # Input directories
    task = "val"
    images_dir = f"/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_epd_gt_box_GAN/images/{task}"
    labels_dir = f"/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_epd_gt_box_GAN/labels/{task}"

    # Output directories
    output_images_dir = f"/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_epd_gt_box_GAN/images/{task}"
    output_labels_dir = f"/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_epd_gt_box_GAN/labels/{task}"

    process_dataset(images_dir, labels_dir, output_images_dir, output_labels_dir)