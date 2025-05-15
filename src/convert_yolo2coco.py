import fiftyone as fo
import fiftyone.zoo as foz

# Load a dataset from YOLO format
dataset = fo.Dataset.from_dir(
    dataset_type=fo.types.YOLOv5Dataset,
    data_path="/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_original_ESRGAN/images",
    labels_path="/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_original_ESRGAN/labels"
)

# Export in COCO format
dataset.export(
    export_dir="/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_original_ESRGAN/coco",
    dataset_type=fo.types.COCODetectionDataset
)
