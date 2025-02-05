import os
import numpy as np
import cv2
from pathlib import Path
import matplotlib.pyplot as plt
from typing import List, Dict

class CMBAreaCalculator:
    def __init__(self, base_dir: str, output_dir: str):
        """
        Initialize the CMB Area Calculator.
        
        Args:
            base_dir: Base directory containing masks/train and masks/val
            output_dir: Directory to save results and visualizations
        """
        self.base_dir = Path(base_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories for different outputs
        self.viz_dir = self.output_dir / 'visualizations'
        self.viz_dir.mkdir(exist_ok=True)

        # Store results
        self.results = []

    def read_label_file(self, label_path: Path) -> List[List[float]]:
        """
        Read bounding box information from label file.

        Args:
            label_path: Path to the label file

        Returns:
            List of bounding boxes [class_id, center_x, center_y, width, height]
        """
        bboxes = []
        if label_path.exists():
            with open(label_path, 'r') as f:
                for line in f:
                    if line.strip().startswith('0'):  # CMB class
                        bbox = [float(x) for x in line.strip().split()]
                        bboxes.append(bbox)
        return bboxes

    def visualize_components(self, mask: np.ndarray, labels: np.ndarray, filename: str):
        """
        Create visualization of individual CMB components.

        Args:
            mask: Original binary mask
            labels: Connected components labels
            filename: Original filename for saving
        """
        # Create RGB visualization
        vis_img = np.zeros((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)

        # Assign different colors to different components
        num_labels = labels.max() + 1
        colors = np.random.randint(50, 255, size=(num_labels, 3), dtype=np.uint8)
        colors[0] = 0  # background black
        
        for label_id in range(1, num_labels):
            component_mask = (labels == label_id)
            vis_img[component_mask] = colors[label_id]
            
            # Calculate centroid of the component
            y, x = np.where(component_mask)
            centroid_y = int(np.mean(y))
            centroid_x = int(np.mean(x))
            
            # Draw patch ID
            cv2.putText(vis_img, str(label_id-1), (centroid_x, centroid_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Save visualization
        cv2.imwrite(str(self.viz_dir / f"{filename}_components.png"), vis_img)

    def process_mask_file(self, mask_path: Path, subset: str):
        """
        Process a single mask file to calculate CMB patch areas.
        
        Args:
            mask_path: Path to the mask file
            subset: 'train' or 'val'
        """
        # Read mask
        mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
        if mask is None:
            print(f"Warning: Could not read {mask_path}")
            return
        
        # Get corresponding label file
        label_path = self.base_dir / 'labels' / subset / f"{mask_path.stem}.txt"
        bboxes = self.read_label_file(label_path)
        
        # Convert to binary mask
        binary_mask = (mask == 255).astype(np.uint8)
        
        # Find connected components
        num_labels, labels = cv2.connectedComponents(binary_mask, connectivity=8)
        
        # Create visualization if there are CMB patches
        if num_labels > 1:
            self.visualize_components(mask, labels, mask_path.stem)
        
        # Process each component (excluding background label 0)
        for label_id in range(1, num_labels):
            # Create mask for this specific component
            component_mask = (labels == label_id)
            
            # Calculate area for this specific component
            area = np.sum(mask[component_mask] == 255)
            
            # Get corresponding bbox if available
            bbox_info = bboxes[label_id-1] if label_id-1 < len(bboxes) else [0, 0, 0, 0, 0]
            
            # Store results
            self.results.append({
                'filename': mask_path.stem,
                'subset': subset,
                'patch_id': label_id - 1,
                'area': area,
                'class_id': bbox_info[0],
                'center_x': bbox_info[1],
                'center_y': bbox_info[2],
                'width': bbox_info[3],
                'height': bbox_info[4]
            })

    def process_all_masks(self):
        """Process all mask files in both train and val directories."""
        for subset in ['train', 'val']:
            mask_dir = self.base_dir / 'masks' / subset
            print(f"\nProcessing {subset} directory...")
            
            # Get total number of files for progress tracking
            total_files = len(list(mask_dir.glob('*.png')))
            
            # Process each PNG file
            for idx, mask_file in enumerate(sorted(mask_dir.glob('*.png')), 1):
                self.process_mask_file(mask_file, subset)
                
                # Print progress
                if idx % 10 == 0:
                    print(f"Processed {idx}/{total_files} files...")

    def save_results(self):
        """Save results to CSV file."""
        output_file = self.output_dir / 'cmb_patch_areas.csv'
        
        print(f"\nSaving results to {output_file}")
        with open(output_file, 'w') as f:
            f.write("filename,subset,patch_id,area,class_id,center_x,center_y,width,height\n")
            for result in self.results:
                f.write(f"{result['filename']},{result['subset']},"
                       f"{result['patch_id']},{result['area']},"
                       f"{result['class_id']},{result['center_x']},"
                       f"{result['center_y']},{result['width']},{result['height']}\n")

    def plot_area_distribution(self):
        """Create plots of CMB patch area distribution."""
        plt.figure(figsize=(12, 6))
        
        # Get areas for train and val
        train_areas = [r['area'] for r in self.results if r['subset'] == 'train']
        val_areas = [r['area'] for r in self.results if r['subset'] == 'val']
        
        # Plot histograms
        plt.hist(train_areas, bins=50, alpha=0.5, label='Train', color='blue')
        plt.hist(val_areas, bins=50, alpha=0.5, label='Val', color='orange')
        
        plt.title('Distribution of CMB Patch Areas')
        plt.xlabel('Area (pixels)')
        plt.ylabel('Count')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Save plot
        plt.savefig(self.output_dir / 'area_distribution.png')
        plt.close()

    def print_statistics(self):
        """Print summary statistics of the CMB patches."""
        train_areas = [r['area'] for r in self.results if r['subset'] == 'train']
        val_areas = [r['area'] for r in self.results if r['subset'] == 'val']
        
        print("\nSummary Statistics:")
        for subset, areas in [('Train', train_areas), ('Val', val_areas)]:
            if areas:
                print(f"\n{subset} Set:")
                print(f"  Total patches: {len(areas)}")
                print(f"  Mean area: {np.mean(areas):.2f}")
                print(f"  Median area: {np.median(areas):.2f}")
                print(f"  Min area: {np.min(areas)}")
                print(f"  Max area: {np.max(areas)}")
                print(f"  Std area: {np.std(areas):.2f}")

def main():
    # Set paths
    base_dir = "/mnt/storage/ji/brain_mri_valdo_mayo/YOLO_valdo_stacked_1mm_png_pm2_0205"
    output_dir = "cmb_analysis_results_0205_2"

    # Create calculator instance
    calculator = CMBAreaCalculator(base_dir, output_dir)

    # Process all masks
    calculator.process_all_masks()

    # Save results and create visualizations
    calculator.save_results()
    calculator.plot_area_distribution()
    calculator.print_statistics()

    print(f"\nProcessing completed! Results saved in: {output_dir}")
    print("Outputs include:")
    print(f"- CSV file with all patch areas and bboxes: {output_dir}/cmb_patch_areas.csv")
    print(f"- Component visualizations: {output_dir}/visualizations/")
    print(f"- Area distribution plot: {output_dir}/area_distribution.png")

if __name__ == "__main__":
    main()