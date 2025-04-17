import os
import cv2
import numpy as np
import glob
import shutil
from pathlib import Path
from tqdm import tqdm

def enhance_microbleed_contrast(image, dark_threshold=50, clip_limit=4.0):
    """
    Apply enhanced contrast specifically for microbleed detection,
    with more aggressive enhancement in darker regions.
    """
    # Ensure we're working with grayscale
    if len(image.shape) > 2:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Create a mask for darker regions
    dark_mask = gray < dark_threshold
    
    # Apply more aggressive contrast enhancement to darker regions
    result = gray.copy()
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(4, 4))
    enhanced = clahe.apply(result)
    
    # Replace only in dark regions
    result[dark_mask] = enhanced[dark_mask]
    
    return result

def apply_clahe(image, clip_limit=2.0, tile_grid_size=(8, 8)):
    """Apply CLAHE to grayscale image."""
    # Ensure we're working with grayscale
    if len(image.shape) > 2:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
        
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    return clahe.apply(gray)

def apply_gamma_correction(image, gamma=1.5):
    """Apply gamma correction to enhance darker regions."""
    # Ensure we're working with grayscale
    if len(image.shape) > 2:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
        
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype("uint8")
    return cv2.LUT(gray, table)

def enhance_local_contrast(image, kernel_size=(7, 7), sigma=0):
    """Enhance local contrast using unsharp masking."""
    # Ensure we're working with grayscale
    if len(image.shape) > 2:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    blurred = cv2.GaussianBlur(gray, kernel_size, sigma)
    mask = gray.astype(np.float32) - blurred.astype(np.float32)
    sharpened = cv2.add(gray, mask.astype(np.int8))
    
    return np.clip(sharpened, 0, 255).astype(np.uint8)

def adaptive_thresholding(image, block_size=11, c=2):
    """Use adaptive thresholding to enhance local contrast."""
    # Ensure we're working with grayscale
    if len(image.shape) > 2:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Apply adaptive threshold
    # We'll produce a binary image, then blend it with original to enhance features
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, block_size, c
    )
    
    # Blend with original (50% each)
    enhanced = cv2.addWeighted(gray, 0.7, thresh, 0.3, 0)
    return enhanced

def blend_techniques(image, techniques_list):
    """Apply multiple techniques and blend the results."""
    # Ensure we're working with grayscale
    if len(image.shape) > 2:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    results = [gray.copy()]  # Start with original
    
    # Apply each technique
    for technique, params in techniques_list:
        results.append(technique(gray, **params))
    
    # Blend all results with equal weight
    weight = 1.0 / len(results)
    blended = np.zeros_like(gray, dtype=np.float32)
    
    for img in results:
        blended += img.astype(np.float32) * weight
    
    return np.clip(blended, 0, 255).astype(np.uint8)

def process_dataset(input_dir, output_dir, augmentation_techniques):
    """
    Process all PNG images in the dataset with the specified augmentation techniques.
    Maintains YOLO format by copying corresponding annotation files.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all PNG files in the input directory
    image_files = glob.glob(os.path.join(input_dir, "**", "*.png"), recursive=True)
    print(f"Found {len(image_files)} PNG files to process")
    
    # Process each image
    for img_path in tqdm(image_files):
        # Load image as grayscale
        image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            print(f"Warning: Could not read {img_path}")
            continue
        
        # Get relative path to maintain folder structure
        rel_path = os.path.relpath(img_path, input_dir)
        img_dir = os.path.dirname(rel_path)
        img_name = os.path.basename(img_path)
        
        # Create corresponding output directory
        out_img_dir = os.path.join(output_dir, img_dir)
        os.makedirs(out_img_dir, exist_ok=True)
        
        # Get corresponding annotation file (same name but .txt extension for YOLO format)
        txt_path = os.path.splitext(img_path)[0] + '.txt'
        
        # Apply each augmentation technique and save the result
        for aug_name, aug_func, aug_params in augmentation_techniques:
            # Apply the augmentation
            aug_image = aug_func(image, **aug_params)
            
            # Generate output file name with augmentation identifier
            base_name = os.path.splitext(img_name)[0]
            aug_img_name = f"{base_name}_{aug_name}.png"
            aug_txt_name = f"{base_name}_{aug_name}.txt"
            
            # Save augmented image
            out_img_path = os.path.join(out_img_dir, aug_img_name)
            cv2.imwrite(out_img_path, aug_image)
            
            # Copy corresponding annotation file if it exists
            if os.path.exists(txt_path):
                out_txt_path = os.path.join(out_img_dir, aug_txt_name)
                shutil.copy(txt_path, out_txt_path)
            else:
                print(f"Warning: No annotation file found for {img_path}")
        
        # Also copy the original image and annotation to the new dataset
        orig_out_img_path = os.path.join(out_img_dir, img_name)
        cv2.imwrite(orig_out_img_path, image)
        
        if os.path.exists(txt_path):
            orig_out_txt_path = os.path.join(out_img_dir, os.path.basename(txt_path))
            shutil.copy(txt_path, orig_out_txt_path)

def main():
    # Define input and output directories
    input_dir = "/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_yolo_t2s_only_rotated_GAN_enhanced_contrast/images/test"  # Change this to your dataset path
    output_dir = "/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_yolo_t2s_only_rotated_GAN_enhanced_contrast_dst/images/test"  # Change this to your output path
    
    # Define augmentation techniques with their parameters
    augmentation_techniques = [
        ("clahe_mild", apply_clahe, {"clip_limit": 2.0, "tile_grid_size": (8, 8)}),
        ("clahe_strong", apply_clahe, {"clip_limit": 4.0, "tile_grid_size": (4, 4)}),
        ("gamma1.5", apply_gamma_correction, {"gamma": 1.5}),
        ("gamma2.0", apply_gamma_correction, {"gamma": 2.0}),
        ("local_contrast", enhance_local_contrast, {"kernel_size": (7, 7), "sigma": 0}),
        ("dark_enhance_mild", enhance_microbleed_contrast, {"dark_threshold": 50, "clip_limit": 3.0}),
        ("dark_enhance_strong", enhance_microbleed_contrast, {"dark_threshold": 70, "clip_limit": 5.0}),
        ("adaptive_thresh", adaptive_thresholding, {"block_size": 11, "c": 2}),
        # Add a blended technique combining multiple methods
        ("blend", blend_techniques, {"techniques_list": [
            (apply_clahe, {"clip_limit": 3.0, "tile_grid_size": (8, 8)}),
            (apply_gamma_correction, {"gamma": 1.8}),
            (enhance_microbleed_contrast, {"dark_threshold": 60, "clip_limit": 4.0})
        ]}),
    ]
    
    # Process the dataset
    process_dataset(input_dir, output_dir, augmentation_techniques)
    
    print(f"Augmented dataset created at {output_dir}")

if __name__ == "__main__":
    main()