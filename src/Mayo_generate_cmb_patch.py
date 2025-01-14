import nibabel as nib
import numpy as np
from PIL import Image
import os
import json

def extract_region(nifti_path, coord, idx, size=32, output_dir='extracted_regions'):
    os.makedirs(output_dir, exist_ok=True)
    # Load NIfTI file
    img = nib.load(nifti_path)
    data = img.get_fdata()
    data = np.rot90(data)

    # Extract coordinates
    x, y, z = coord
    y_temp = y
    y = x
    x = y_temp
    
    # Calculate region boundaries
    half_size = size // 2
    x_start = max(0, x - half_size)
    x_end = min(data.shape[0], x + half_size)
    y_start = max(0, y - half_size)
    y_end = min(data.shape[1], y + half_size)
    
    # Extract the region
    region = data[x_start:x_end, y_start:y_end, z]
    
    # Handle potential NaN or infinite values
    region = np.nan_to_num(region)
    
    # Normalize pixel values to 0-255 range
    if region.max() != region.min():
        region_normalized = ((region - region.min()) * (255.0 / (region.max() - region.min()))).astype(np.uint8)
    else:
        region_normalized = np.zeros_like(region, dtype=np.uint8)
    
    img = Image.fromarray(region_normalized)
    mrn = nifti_path.split('/')[-1].split('_')[0]
    output_filename = f'{mrn}_i{idx}_x{y}_y{x}_z{z}.png'
    output_path = os.path.join(output_dir, output_filename)
    img.save(output_path)
    
    return output_path

# Example usage
if __name__ == "__main__":
    # for mrn in os.scandir("/media/Datacenter_storage/Ji/generate_batch_mayodataset/cmb_coordinates"):
    for mrn in os.scandir("/media/Datacenter_storage/Ji/mayo_yolo_dataset/cmb_coordinates"):
        with open(mrn.path, 'r') as file:
            data = json.load(file)
            for nifti_path, coordinates in data.items():
                for idx, coord in enumerate(coordinates):
                    output_path = extract_region(nifti_path, coord, idx)
                    print(f"Saved region at coordinates {coord} to {output_path}")