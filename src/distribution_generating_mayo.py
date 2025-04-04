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

    def calculate_bbox_area(self, bbox: List[float], img_width: int, img_height: int) -> float:
        """Calculate the area of the bounding box."""
        box_width = bbox[3] * img_width
        box_height = bbox[4] * img_height
        return box_width * box_height

    def process_label_file(self, label_path: Path):
        """Process a single label file and calculate bounding box areas."""
        img_width, img_height = 256, 256  # Image size
        bboxes = self.read_label_file(label_path)
        
        for bbox in bboxes:
            area = self.calculate_bbox_area(bbox, img_width, img_height)
            self.results.append({
                'filename': label_path.stem,
                'area': area,
                'class_id': bbox[0],
                'center_x': bbox[1],
                'center_y': bbox[2],
                'width': bbox[3],
                'height': bbox[4]
            })

    def process_all_labels(self):
        label_dir = self.base_dir / 'labels' / 'test'

        total_files = len(list(label_dir.glob('*.txt')))
        for idx, label_file in enumerate(sorted(label_dir.glob('*.txt')), 1):
            self.process_label_file(label_file)
            if idx % 10 == 0:
                print(f"Processed {idx}/{total_files} files...")

    def plot_area_distribution(self):
        """Create plots of bounding box area distribution with area values on x-axis."""
        plt.figure(figsize=(15, 8))
        
        # Get areas
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
        
        plt.title('Distribution of Bounding Box Areas')
        plt.xlabel('Bounding Box Area (pixels)')
        plt.ylabel('Frequency')
        
        # Set x-ticks to show area values
        plt.xticks(x_values, [int(x) for x in x_values], rotation=45, ha='right')
        
        # Calculate statistics
        stats_text = (
            f"Statistical Information:\n"
            f"Total bounding boxes: {len(areas)}\n"
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
        plt.savefig(self.output_dir / 'bbox_area_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Save area-count table with statistics
        table_file = self.output_dir / 'bbox_area_frequency_table.csv'
        stats_file = self.output_dir / 'bbox_statistical_summary.txt'
        
        with open(table_file, 'w') as f:
            f.write("bbox_area,count\n")
            for area, count in sorted_items:
                f.write(f"{int(area)},{count}\n")
                print(f"{int(area)}\t{count}")
        
        # Save statistical summary
        with open(stats_file, 'w') as f:
            f.write(stats_text)

def main():
    base_dir = "/media/Datacenter_storage/Ji/brain_mri_valdo_mayo/mayo_yolo_t2s_only_rotated"
    output_dir = "/media/Datacenter_storage/Ji/distribution/mayo_yolo_t2s_only_rotated"
    
    calculator = CMBAreaCalculator(base_dir, output_dir)
    calculator.process_all_labels()
    calculator.plot_area_distribution()
    
    print(f"\nProcessing completed! Results saved in: {output_dir}")
    print("Outputs include:")
    print(f"- CSV file with bounding box areas: {output_dir}/bbox_area_frequency_table.csv")
    print(f"- Distribution plot: {output_dir}/bbox_area_distribution.png")

if __name__ == "__main__":
    main()