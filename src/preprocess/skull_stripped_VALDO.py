import os
import sys
import subprocess
import nibabel as nib
import numpy as np

SEQUENCE = "T1"

def skull_stripped_runner(root_path, output_root_path):
    # os.makedirs(output_root_path, exist_ok=True)

    for uid in os.listdir(root_path):        
        if uid.startswith('.') or uid == ".DS_Store":
            continue

        for file in os.listdir(os.path.join(root_path, uid)):
            if file.startswith('.') or file.endswith(".dcm"):
                continue
            if not file.endswith(f'{SEQUENCE}.nii.gz'): # T2S Sequence Only
                continue

            user_output_dir = os.path.join(output_root_path, uid)
            print(user_output_dir)
            os.makedirs(user_output_dir, exist_ok=True)

            file_path = os.path.join(root_path, uid, file)
            output_file_path = os.path.join(user_output_dir, file)
            
            try:
                # PRE-PROCESS: Check and clean input file for NaN values
                print(f"Checking {file} for NaN values...")
                orig_img = nib.load(file_path)
                orig_data = orig_img.get_fdata()
                
                nan_count = np.isnan(orig_data).sum()
                inf_count = np.isinf(orig_data).sum()
                
                if nan_count > 0 or inf_count > 0:
                    print(f"  ⚠️ Found {nan_count} NaN and {inf_count} inf values - cleaning...")
                    
                    # Clean the data
                    cleaned_data = np.nan_to_num(orig_data, nan=0.0)
                    
                    # Create temporary cleaned file for FreeSurfer
                    temp_cleaned_path = file_path.replace('.nii.gz', '_temp_clean.nii.gz')
                    cleaned_img = nib.Nifti1Image(cleaned_data, orig_img.affine, orig_img.header)
                    nib.save(cleaned_img, temp_cleaned_path)
                    
                    input_file_for_freesurfer = temp_cleaned_path
                    print(f"  ✅ Using cleaned file for FreeSurfer")
                else:
                    print(f"  ✅ No NaN/inf values found")
                    input_file_for_freesurfer = file_path
                
                # Run skull stripping on cleaned file
                print(f"Running FreeSurfer skull stripping...")
                command = ['mri_synthstrip', '-i', input_file_for_freesurfer, '-o', output_file_path]
                
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                print(f"  ✅ FreeSurfer completed successfully")
                
                # POST-PROCESS: Apply FreeSurfer mask to original image
                stripped_img = nib.load(output_file_path)
                
                # Create mask from stripped image
                mask = (stripped_img.get_fdata() > 0).astype(float)
                print(f"Mask unique values: {np.unique(mask)}")
                
                # Apply mask to ORIGINAL image (preserves original intensities)
                final_data = orig_data * mask
                
                # Clean final data just in case
                final_data = np.nan_to_num(final_data, nan=0.0)

                # Save with original intensities
                final_nii = nib.Nifti1Image(final_data, orig_img.affine, orig_img.header)
                nib.save(final_nii, output_file_path)
                
                print(f"✅ Processed: {file}")
                
                # Clean up temporary file if it was created
                if input_file_for_freesurfer != file_path and os.path.exists(input_file_for_freesurfer):
                    os.remove(input_file_for_freesurfer)
                    print(f"🗑️ Cleaned up temporary file")
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Error processing {file}:")
                print(f"   Command: {' '.join(command)}")
                print(f"   Error: {e.stderr}")
                
                # Clean up temporary file on error
                if 'input_file_for_freesurfer' in locals() and input_file_for_freesurfer != file_path:
                    if os.path.exists(input_file_for_freesurfer):
                        os.remove(input_file_for_freesurfer)
                        
            except Exception as e:
                print(f"❌ Unexpected error processing {file}: {str(e)}")

def main():
    root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/Task2"
    output_root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/skull_stripped"
    skull_stripped_runner(root_path, output_root_path)

if __name__ == "__main__":
    main()

'''
Please run the following commands in the terminal

FREESURFER_HOME=/mnt/storage/ji/freesurfer
source $FREESURFER_HOME/SetUpFreeSurfer.sh
or
FREESURFER_HOME=/media/Datacenter_storage/Ji/freesurfer
source $FREESURFER_HOME/SetUpFreeSurfer.sh
'''



# import os
# import sys
# import subprocess
# import nibabel as nib
# import numpy as np

# SEQUENCE = "T1"  # e.g., "T1", "T2S", etc.

# def run_synthstrip(input_path: str, brain_out: str, mask_out: str):
#     """
#     Runs FreeSurfer SynthStrip to produce a brain-only image and a binary mask.
#     """
#     command = [
#         'mri_synthstrip',
#         '-i', input_path,
#         '-o', brain_out,
#         '-m', mask_out
#     ]
#     result = subprocess.run(command, check=True, capture_output=True, text=True)
#     return result

# def save_with_clean_header(data: np.ndarray, like_img: nib.Nifti1Image, out_path: str):
#     """
#     Save NIfTI as float32 with clean scaling (slope=1, inter=0), preserving affine and
#     essential header fields but avoiding double-scaling brightness shifts.
#     """
#     # Ensure float32
#     data = data.astype(np.float32, copy=False)

#     # Copy header from the original image to preserve meta (dim, pixdim, etc.)
#     new_hdr = like_img.header.copy()
#     # Set dtype float32 explicitly
#     new_hdr.set_data_dtype(np.float32)

#     # Reset scaling to identity to prevent viewers from applying old int16 scaling again
#     try:
#         # Works on Nifti1Header in recent nibabel
#         new_hdr['scl_slope'] = 1
#         new_hdr['scl_inter'] = 0
#     except Exception:
#         pass

#     # Build and save
#     out_img = nib.Nifti1Image(data, like_img.affine, header=new_hdr)
#     nib.save(out_img, out_path)

# def skull_stripped_runner(root_path, output_root_path):
#     for uid in os.listdir(root_path):
#         if uid.startswith('.') or uid == ".DS_Store":
#             continue

#         uid_dir = os.path.join(root_path, uid)
#         if not os.path.isdir(uid_dir):
#             continue

#         for file in os.listdir(uid_dir):
#             # Skip hidden and DICOMs; keep only the chosen sequence
#             if file.startswith('.') or file.endswith(".dcm"):
#                 continue
#             if not file.endswith(f'{SEQUENCE}.nii.gz'):
#                 continue

#             user_output_dir = os.path.join(output_root_path, uid)
#             os.makedirs(user_output_dir, exist_ok=True)

#             file_path = os.path.join(uid_dir, file)
#             brain_out_path = os.path.join(user_output_dir, file)  # brain image (we overwrite later with masked original)
#             mask_out_path  = brain_out_path.replace('.nii.gz', '_mask.nii.gz')
#             temp_cleaned_path = None

#             print(f"\n▶ Processing: {file_path}")
#             try:
#                 # --- PRE: load & clean input if needed (NaN/Inf) ---
#                 orig_img = nib.load(file_path)
#                 orig_data = orig_img.get_fdata()
#                 nan_count = int(np.isnan(orig_data).sum())
#                 inf_count = int(np.isinf(orig_data).sum())
#                 if nan_count > 0 or inf_count > 0:
#                     print(f"  ⚠ Found {nan_count} NaN and {inf_count} Inf values — cleaning for SynthStrip...")
#                     cleaned_data = np.nan_to_num(orig_data, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)
#                     temp_cleaned_path = file_path.replace('.nii.gz', '_temp_clean.nii.gz')
#                     nib.save(nib.Nifti1Image(cleaned_data, orig_img.affine, orig_img.header), temp_cleaned_path)
#                     input_for_synthstrip = temp_cleaned_path
#                 else:
#                     input_for_synthstrip = file_path
#                     print("  ✅ No NaN/Inf detected")

#                 # --- RUN: SynthStrip (brain + mask) ---
#                 print("  🚀 Running SynthStrip (brain + mask)...")
#                 run_synthstrip(input_for_synthstrip, brain_out_path, mask_out_path)
#                 print("  ✅ SynthStrip finished")

#                 # --- LOAD: mask, ensure binary ---
#                 mask_img = nib.load(mask_out_path)
#                 mask_data = mask_img.get_fdata()
#                 # Be strict: threshold to avoid soft edges/ghosts
#                 mask = (mask_data > 0.5).astype(np.float32)

#                 # --- APPLY: mask to ORIGINAL intensities (not SynthStrip brain image) ---
#                 final_data = orig_data * mask
#                 final_data = np.nan_to_num(final_data, nan=0.0, posinf=0.0, neginf=0.0)

#                 # --- SAVE: with clean header (float32, slope=1, inter=0) ---
#                 save_with_clean_header(final_data, orig_img, brain_out_path)
#                 print(f"  💾 Saved masked image (clean header): {brain_out_path}")

#                 # Optionally keep or remove the mask file; here we keep it
#                 # If you want to delete: os.remove(mask_out_path)

#             except subprocess.CalledProcessError as e:
#                 print(f"❌ SynthStrip error for {file}:")
#                 print(f"   stderr: {e.stderr.strip() if e.stderr else '(no stderr)'}")
#             except Exception as e:
#                 print(f"❌ Unexpected error for {file}: {e}")
#             finally:
#                 # Cleanup temporary cleaned file if created
#                 if temp_cleaned_path and os.path.exists(temp_cleaned_path):
#                     os.remove(temp_cleaned_path)
#                     print("  🧹 Removed temporary cleaned file")

# def main():
#     root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/Task2"
#     output_root_path = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/skull_stripped_TEMP"
#     skull_stripped_runner(root_path, output_root_path)

# if __name__ == "__main__":
#     main()

# """
# Before running, set up FreeSurfer (pick your install path):

# FREESURFER_HOME=/mnt/storage/ji/freesurfer
# source $FREESURFER_HOME/SetUpFreeSurfer.sh

# # or

# FREESURFER_HOME=/media/Datacenter_storage/Ji/freesurfer
# source $FREESURFER_HOME/SetUpFreeSurfer.sh
# """