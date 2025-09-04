import SimpleITK as sitk
import numpy as np
import os

def rotate_nifti_90_counterclockwise(src_path, dest_path):
    """
    Rotate a NIfTI image 90 degrees counterclockwise in the x-y plane
    """
    try:
        print(f"Reading image: {src_path}")        
        # Check if source file exists
        if not os.path.exists(src_path):
            print(f"ERROR: Source file does not exist: {src_path}")
            return False
        
        # Read the image
        image = sitk.ReadImage(src_path)
        
        # Get original properties
        original_size = image.GetSize()
        original_spacing = image.GetSpacing()
        original_origin = image.GetOrigin()
        original_direction = image.GetDirection()
        
        print(f"Original image size: {original_size}")
        print(f"Original spacing: {original_spacing}")
        print(f"Original origin: {original_origin}")
        
        # Convert to numpy array (SimpleITK uses z,y,x ordering)
        image_array = sitk.GetArrayFromImage(image)
        print(f"Original array shape: {image_array.shape}")
        print(f"Value range: [{np.min(image_array):.3f}, {np.max(image_array):.3f}]")
        
        # Rotate 90 degrees counterclockwise in x-y plane
        # For SimpleITK arrays (z,y,x), we rotate on axes (2,1) which corresponds to (x,y)
        # k=1 means 90 degrees counterclockwise
        rotated_array = np.rot90(image_array, k=1, axes=(2, 1))
        
        print(f"Rotated array shape: {rotated_array.shape}")
        
        # Create new SimpleITK image from rotated array
        rotated_image = sitk.GetImageFromArray(rotated_array)
        
        # For 90-degree counterclockwise rotation in x-y plane:
        # - x becomes -y (but with array indexing, this is handled by rot90)
        # - y becomes x
        # So we need to swap x and y spacing
        new_spacing = [original_spacing[1], original_spacing[0], original_spacing[2]]  # swap x,y spacing
        rotated_image.SetSpacing(new_spacing)
        
        # Keep the same origin (simplified approach)
        rotated_image.SetOrigin(original_origin)
        
        # Keep the same direction matrix (simplified approach)
        rotated_image.SetDirection(original_direction)
        
        print(f"Final image size: {rotated_image.GetSize()}")
        print(f"Final spacing: {rotated_image.GetSpacing()}")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(dest_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Write the rotated image
        sitk.WriteImage(rotated_image, dest_path)
        print(f"SUCCESS: Rotated image saved to {dest_path}")
        
        # Verify the output
        verification_array = sitk.GetArrayFromImage(sitk.ReadImage(dest_path))
        print(f"Verification - saved image value range: [{np.min(verification_array):.3f}, {np.max(verification_array):.3f}]")
        print(f"Non-zero voxels: {np.count_nonzero(verification_array)}/{verification_array.size}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # ground truth
    root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/CSF_NIFTI/csf_segment_threshold_val"
    target_sequence = "seg_0"
    
    # Check if root path exists
    if not os.path.exists(root_path):
        print(f"ERROR: Root path does not exist: {root_path}")
        exit(1)
    
    print(f"Searching for subjects in: {root_path}")
    print(f"Target sequence: {target_sequence}")
    print("=" * 80)
    
    processed_count = 0
    error_count = 0
    skipped_count = 0
    
    # Get all directories that match sub-xxx pattern
    subject_dirs = [d for d in os.listdir(root_path) if d.startswith('sub-') and os.path.isdir(os.path.join(root_path, d))]
    subject_dirs.sort()  # Sort for consistent processing order    
    print(f"Found {len(subject_dirs)} subject directories")
    
    for uid in subject_dirs:
        print(f"\n--- Processing {uid} ---")
        uid_path = os.path.join(root_path, uid)
        
        # Look for the target T2S file
        found_file = False
        for file in os.listdir(uid_path):
            # if file.endswith(f"{target_sequence}.nii.gz") and file.startswith("sub"): # For general purpose
            if file.endswith(f"{target_sequence}.nii.gz"):   # For CSF rotatitng
                print(f"Found target file: {file}")
                found_file = True
                
                src_path = os.path.join(uid_path, file)
                dest_path = os.path.join(uid_path, file)
 
                # Perform the rotation
                success = rotate_nifti_90_counterclockwise(src_path, dest_path)
                
                if success:
                    print(f"✅ SUCCESS: {uid}")
                    processed_count += 1
                else:
                    print(f"❌ FAILED: {uid}")
                    error_count += 1
                break
        
        if not found_file:
            print(f"No matching {target_sequence} file found in {uid}")
            error_count += 1
    
    # Final summary
    print("\n" + "=" * 80)
    print("PROCESSING COMPLETE")
    print("=" * 80)
    print(f"Total subject directories found: {len(subject_dirs)}")
    print(f"Successfully processed: {processed_count}")
    print(f"Skipped (already exists): {skipped_count}")
    print(f"Errors/Not found: {error_count}")
    print(f"Success rate: {processed_count/(processed_count + error_count)*100:.1f}%" if (processed_count + error_count) > 0 else "N/A")