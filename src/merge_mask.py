import nibabel as nib
import numpy as np
from scipy.ndimage import zoom
from scipy.ndimage import binary_erosion, binary_dilation
import os

def resize_mask(mask_data, target_shape, method='nearest'):
    # Calculate zoom factors for each dimension
    zoom_factors = [target_shape[i] / mask_data.shape[i] for i in range(len(target_shape))]
    
    if method == 'nearest':
        # Simple nearest neighbor interpolation
        resized = zoom(mask_data.astype(float), zoom_factors, order=0)
        return (resized > 0.5).astype(int)
    
def combine_masks(csf_path, cmb_path, output_path, resize_method='nearest'):
    # Load the NIFTI files
    print("Loading NIFTI files...")
    csf_nii = nib.load(csf_path)
    cmb_nii = nib.load(cmb_path)
    
    csf_data = csf_nii.get_fdata()
    cmb_data = cmb_nii.get_fdata()
    
    print(f"CSF mask shape: {csf_data.shape}")
    print(f"Microbleeds mask shape: {cmb_data.shape}")
    
    # Convert to integer arrays (0 and 1)
    csf_data = (csf_data > 0.5).astype(int)
    cmb_data = (cmb_data > 0.5).astype(int)
    
    # Resize CSF mask to match microbleeds mask dimensions
    print(f"Resizing CSF mask from {cmb_data.shape} to {csf_data.shape} using {resize_method} method...")
    # csf_resized = resize_mask(csf_data, cmb_data.shape, method=resize_method)
    cmb_resized = resize_mask(cmb_data, csf_data.shape, method=resize_method)
    cmb_data = cmb_resized

    print("Combining masks...")
    combined_mask = np.zeros_like(cmb_data, dtype=int)
    combined_mask[csf_data == 1] = 2
    combined_mask[cmb_data == 1] = 1
        
    print(f"Combined mask labels: {np.unique(combined_mask)}")
    print(f"Label counts:")
    print(f"  Background (0): {np.sum(combined_mask == 0)}")
    print(f"  Microbleeds (1): {np.sum(combined_mask == 1)}")
    print(f"  CSF (2): {np.sum(combined_mask == 2)}")
    
    # Create new NIFTI image using microbleeds header and affine
    print("Saving combined mask...")
    combined_nii = nib.Nifti1Image(combined_mask, cmb_nii.affine, cmb_nii.header)
    nib.save(combined_nii, output_path)
    
    print(f"Combined mask saved to: {output_path}")
    return combined_mask

# Example usage
if __name__ == "__main__":
    cmb_root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/bias_field_correction"
    csf_root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/CSF_NIFTI/csf_segment_threshold_train"
    output_root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/cmb_csf"

    for uid in os.listdir(cmb_root_path):
        os.makedirs(os.path.join(output_root_path, uid), exist_ok=True)

        # cerebral_microbleeds_VALDO/bias_field_correction/sub-102/sub-102_space-T2S_CMB.nii.gz
        cmb_mask_path = os.path.join(cmb_root_path, uid, f"{uid}_space-T2S_CMB.nii.gz")
        csf_mask_path = os.path.join(csf_root_path, uid, "T1_seg_0.nii.gz")
        output_mask_path = os.path.join(output_root_path, uid, f"{uid}_space-T2S_CMB.nii.gz")
    
        combined_mask = combine_masks(
            csf_mask_path, 
            cmb_mask_path, 
            output_mask_path,
            resize_method='nearest'
        )