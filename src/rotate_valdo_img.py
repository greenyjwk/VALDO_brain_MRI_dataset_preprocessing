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
    # Input and output paths
    src_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/bias_field_correction/sub-218/sub-218_space-T2S_desc-masked_T2S.nii.gz"
    
    # Create output filename
    base_dir = os.path.dirname(src_path)
    base_filename = os.path.basename(src_path)
    name_without_ext = base_filename.replace('.nii.gz', '')
    dest_path = os.path.join(base_dir, f"{name_without_ext}_rotated.nii.gz")
    
    print(f"Input file: {src_path}")
    print(f"Output file: {dest_path}")
    print("-" * 60)
    
    # Perform the rotation
    success = rotate_nifti_90_counterclockwise(src_path, dest_path)
    
    if success:
        print("\n✅ Rotation completed successfully!")
        print(f"Rotated file saved as: {dest_path}")
    else:
        print("\n❌ Rotation failed!")