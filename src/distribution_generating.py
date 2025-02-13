import os
import numpy as np
import cv2
from pathlib import Path
import matplotlib.pyplot as plt
from typing import List, Dict

class CMBAreaCalculator:
    def __init__(self, base_dir: str, output_dir: str):
        self.base_dir = Path(base_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.viz_dir = self.output_dir / 'visualizations'
        self.viz_dir.mkdir(exist_ok=True)
        self.results = []

    def read_label_file(self, label_path: Path) -> List[List[float]]:
        """Read bounding box information from label file."""
        bboxes = []
        if label_path.exists():
            with open(label_path, 'r') as f:
                for line in f:
                    if line.strip().startswith('0'):  # CMB class
                        bbox = [float(x) for x in line.strip().split()]
                        bboxes.append(bbox)
        return bboxes

    def calculate_area_in_bbox(self, mask: np.ndarray, bbox: List[float]) -> int:
        """Calculate CMB area within the ground truth box."""
        height, width = mask.shape
        
        # Convert normalized bbox coordinates to pixel coordinates
        center_x = int(bbox[1] * width)
        center_y = int(bbox[2] * height)
        box_width = int(bbox[3] * width)
        box_height = int(bbox[4] * height)
        
        # Calculate box boundaries
        x1 = max(0, int(center_x - box_width/2))
        y1 = max(0, int(center_y - box_height/2))
        x2 = min(width, int(center_x + box_width/2))
        y2 = min(height, int(center_y + box_height/2))
        
        # Extract region and count CMB pixels
        region = mask[y1:y2, x1:x2]
        area = np.sum(region == 255)
        
        return area, (x1, y1, x2, y2)

    def visualize_bbox_and_area(self, mask: np.ndarray, bbox_coords: tuple, 
                              patch_id: int, filename: str):
        """Visualize mask with bounding box."""
        x1, y1, x2, y2 = bbox_coords
        vis_img = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
        
        # Draw bounding box
        cv2.rectangle(vis_img, (x1, y1), (x2, y2), (0, 255, 0), 1)
        
        # Add patch ID
        cv2.putText(vis_img, f"Patch {patch_id}", (x1, y1-5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        cv2.imwrite(str(self.viz_dir / f"{filename}_bbox_{patch_id}.png"), vis_img)

    def process_mask_file(self, mask_path: Path, subset: str):
        """Process a single mask file and calculate CMB areas within bboxes."""
        # Read mask
        mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
        if mask is None:
            print(f"Warning: Could not read {mask_path}")
            return
        
        # Get corresponding label file
        label_path = self.base_dir / 'labels' / subset / f"{mask_path.stem}.txt"
        bboxes = self.read_label_file(label_path)
        
        # Process each bounding box
        for patch_id, bbox in enumerate(bboxes):
            # Calculate area within bbox
            area, bbox_coords = self.calculate_area_in_bbox(mask, bbox)
            
            # Visualize if area is found
            if area > 0:
                self.visualize_bbox_and_area(mask, bbox_coords, patch_id, mask_path.stem)
            
            # Store results
            self.results.append({
                'filename': mask_path.stem,
                'subset': subset,
                'patch_id': patch_id,
                'area': area,
                'class_id': bbox[0],
                'center_x': bbox[1],
                'center_y': bbox[2],
                'width': bbox[3],
                'height': bbox[4]
            })

    def process_all_masks(self):
        """Process all mask files in both train and val directories."""
        for subset in ['train', 'val']:
            mask_dir = self.base_dir / 'masks' / subset
            print(f"\nProcessing {subset} directory...")
            
            total_files = len(list(mask_dir.glob('*.png')))
            for idx, mask_file in enumerate(sorted(mask_dir.glob('*.png')), 1):
                self.process_mask_file(mask_file, subset)
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
        """Create plots of CMB patch area distribution with area values on x-axis."""
        plt.figure(figsize=(15, 8))
        
        # Get areas for train and val combined
        areas = [r['area'] for r in self.results]
        
        # Calculate frequency of each unique area
        area_counts = {}
        for area in areas:
            area_counts[area] = area_counts.get(area, 0) + 1
        
        # Sort by area value
        sorted_items = sorted(area_counts.items())
        x_values = [item[0] for item in sorted_items]
        counts = [item[1] for item in sorted_items]
        
        # Create bar plot using actual area values for x-axis
        plt.bar(x_values, counts, alpha=0.6, color='blue')
        
        # Add count labels on top of bars
        for x, count in zip(x_values, counts):
            plt.text(x, count, str(count), 
                    ha='center', va='bottom', fontsize=8)
        
        plt.title('Distribution of CMB Patch Areas')
        plt.xlabel('CMB Area (pixels)')
        plt.ylabel('Frequency')
        
        # Set x-ticks to show area values
        plt.xticks(x_values, [int(x) for x in x_values], rotation=45, ha='right')
        
        # Calculate statistics
        stats_text = (
            f"Statistical Information:\n"
            f"Total patches: {len(areas)}\n"
            f"Unique areas: {len(x_values)}\n"
            f"Mean: {np.mean(areas):.2f}\n"
            f"Median: {np.median(areas):.2f}\n"
            f"Std: {np.std(areas):.2f}\n"
            f"Min: {np.min(areas):.2f}\n"
            f"Max: {np.max(areas):.2f}\n"
            f"25th percentile: {np.percentile(areas, 25):.2f}\n"
            f"75th percentile: {np.percentile(areas, 75):.2f}"
        )
        
        # Add statistics text to plot
        plt.figtext(0.95, 0.7, stats_text, 
                   bbox=dict(facecolor='white', alpha=0.8),
                   fontsize=10, ha='right')
        
        # Add grid for better readability
        plt.grid(True, alpha=0.3)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save plot
        plt.savefig(self.output_dir / 'area_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Save area-count table with statistics
        table_file = self.output_dir / 'area_frequency_table.csv'
        stats_file = self.output_dir / 'statistical_summary.txt'
        
        # Save frequency table
        print("\nCMB Area Frequency Table:")
        print("Area\tCount")
        print("-" * 20)
        
        with open(table_file, 'w') as f:
            f.write("cmb_area,count\n")
            for area, count in sorted_items:
                f.write(f"{int(area)},{count}\n")
                print(f"{int(area)}\t{count}")
        
        # Save statistical summary
        with open(stats_file, 'w') as f:
            f.write(stats_text)
        
        # Print statistical summary
        print("\nStatistical Summary:")
        print(f"Total patches: {len(areas)}")
        print(f"Unique areas: {len(x_values)}")
        print(f"Mean area: {np.mean(areas):.2f}")
        print(f"Median area: {np.median(areas):.2f}")
        print(f"Standard deviation: {np.std(areas):.2f}")
        print(f"Minimum area: {np.min(areas):.2f}")
        print(f"Maximum area: {np.max(areas):.2f}")
        print(f"25th percentile: {np.percentile(areas, 25):.2f}")
        print(f"75th percentile: {np.percentile(areas, 75):.2f}")
        
        print(f"\nStatistical summary saved to: {stats_file}")
        print(f"Frequency table saved to: {table_file}")

def main():
    base_dir = "/mnt/storage/ji/brain_mri_valdo_mayo/valdo_resample_ALFA_YOLO_PNG_all_slices"
    output_dir = "/mnt/storage/ji/distribution/valdo_resample_ALFA_YOLO_PNG_all_slices"
    
    calculator = CMBAreaCalculator(base_dir, output_dir)
    calculator.process_all_masks()
    calculator.save_results()
    calculator.plot_area_distribution()
    
    print(f"\nProcessing completed! Results saved in: {output_dir}")
    print("Outputs include:")
    print(f"- CSV file with patch areas: {output_dir}/cmb_patch_areas.csv")
    print(f"- Visualizations: {output_dir}/visualizations/")
    print(f"- Distribution plot: {output_dir}/area_distribution.png")

if __name__ == "__main__":
    main()