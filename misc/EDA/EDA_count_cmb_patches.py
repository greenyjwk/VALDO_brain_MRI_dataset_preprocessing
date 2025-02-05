# import os
# from pathlib import Path

# def count_total_lines(folder_path):
#     """
#     Count total number of lines across all text files in a folder.
    
#     Args:
#         folder_path (str): Path to the folder containing text files
        
#     Returns:
#         int: Total number of lines across all text files
#     """
#     folder = Path(folder_path)
#     if not folder.exists() or not folder.is_dir():
#         raise ValueError(f"Invalid folder path: {folder_path}")
    
#     total_lines = 0
    
#     # Get all .txt files in the folder
#     txt_files = folder.glob('*.txt')
    
#     for file_path in txt_files:
#         try:
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 total_lines += sum(1 for _ in f)
#         except Exception as e:
#             print(f"Skipped {file_path.name}: {e}")
#             continue
    
#     return total_lines

# if __name__ == "__main__":
    
#     folder_path = "/mnt/storage/ji/brain_mri_valdo_mayo/YOLO_valdo_stacked_1mm_png_pm2_0205/labels/train"
#     try:
#         total = count_total_lines(folder_path)
#         print(f"\nTotal number of lines across all text files: {total}")
#     except ValueError as e:
#         print(f"Error: {e}")
import os
from pathlib import Path

def count_total_lines(folder_path):
    """
    Count total number of non-empty lines across all text files in a folder.
    
    Args:
        folder_path (str): Path to the folder containing text files
        
    Returns:
        int: Total number of non-empty lines across all text files
    """
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"Invalid folder path: {folder_path}")
    
    total_lines = 0
    
    # Get all .txt files in the folder
    txt_files = folder.glob('*.txt')
    
    for file_path in txt_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                total_lines += sum(1 for line in f if line.strip())
        except Exception as e:
            print(f"Skipped {file_path.name}: {e}")
            continue
    
    return total_lines

if __name__ == "__main__":
    
    folder_path = "/mnt/storage/ji/brain_mri_valdo_mayo/YOLO_valdo_stacked_1mm_png_pm2_0205/labels/train"
    try:
        total = count_total_lines(folder_path)
        print(f"\nTotal number of non-empty lines across all text files: {total}")
    except ValueError as e:
        print(f"Error: {e}")