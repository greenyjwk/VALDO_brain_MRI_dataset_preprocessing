import os

root_path = "/media/Datacenter_storage/Ji/valdo_dataset/valdo_t2s_cmbOnly_GAN"
images_dir = f"{root_path}/images/train"
labels_dir = f"{root_path}/labels/train"

for label_file in os.listdir(labels_dir):
    label_path = os.path.join(labels_dir, label_file)
    with open(label_path, 'r') as file:
        content = file.read().strip()
        if not content:
            image_file = label_file.replace('.txt', '.png')
            image_path = os.path.join(images_dir, image_file)
            # mask_path = image_path.replace('images', 'masks')
            os.remove(label_path)
            os.remove(image_path)
            # os.remove(mask_path)
            print(f"Deleted: {label_path} and {image_path}")
print("Cleanup complete.")

'''
It removes png files that don't have cmb patches.
It is usually used from the train dataset.
'''