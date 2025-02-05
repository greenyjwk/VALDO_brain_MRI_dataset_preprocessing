# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# import numpy as np
# from pathlib import Path

# def plot_area_distributions(csv_file: str, output_dir: str = 'distribution_plots'):
#     """
#     Create detailed distribution plots of CMB patch areas.
    
#     Args:
#         csv_file: Path to the CSV file containing patch areas
#         output_dir: Directory to save the plots
#     """
#     # Create output directory
#     output_dir = Path(output_dir)
#     output_dir.mkdir(exist_ok=True)
    
#     # Read CSV file
#     df = pd.read_csv(csv_file)
    
#     # Set style
#     plt.style.use('default')
    
#     # Create figure with multiple subplots
#     fig = plt.figure(figsize=(20, 15))
#     gs = plt.GridSpec(3, 2)
    
#     # 1. Combined histogram with KDE for all patches
#     ax0 = fig.add_subplot(gs[0, :])
#     sns.histplot(data=df, x='area', bins=50, kde=True, ax=ax0, color='blue', alpha=0.6)
#     ax0.set_title('Distribution of All CMB Patches (Train + Val)')
#     ax0.set_xlabel('Area (pixels)')
#     ax0.set_ylabel('Count')
    
#     # Add text with statistics for all patches
#     all_stats = f"All Patches:\n"
#     all_stats += f"Count: {len(df)}\n"
#     all_stats += f"Mean: {df['area'].mean():.2f}\n"
#     all_stats += f"Median: {df['area'].median():.2f}\n"
#     all_stats += f"Std: {df['area'].std():.2f}\n"
#     all_stats += f"Min: {df['area'].min():.2f}\n"
#     all_stats += f"Max: {df['area'].max():.2f}"
    
#     plt.figtext(0.95, 0.85, all_stats, 
#                 bbox=dict(facecolor='white', alpha=0.8),
#                 fontsize=10, ha='right')
    
#     # 2. Histogram with KDE by subset
#     ax1 = fig.add_subplot(gs[1, 0])
#     sns.histplot(data=df, x='area', hue='subset', kde=True, ax=ax1)
#     ax1.set_title('Distribution by Subset')
#     ax1.set_xlabel('Area (pixels)')
#     ax1.set_ylabel('Count')
    
#     # 3. Box plot
#     ax2 = fig.add_subplot(gs[1, 1])
#     sns.boxplot(data=df, x='subset', y='area', ax=ax2)
#     ax2.set_title('Box Plot of CMB Patch Areas')
#     ax2.set_xlabel('Subset')
#     ax2.set_ylabel('Area (pixels)')
    
#     # 4. Separate KDE plots for train and val
#     ax3 = fig.add_subplot(gs[2, :])
#     sns.kdeplot(data=df[df['subset'] == 'train'], x='area', label='Train', ax=ax3)
#     sns.kdeplot(data=df[df['subset'] == 'val'], x='area', label='Validation', ax=ax3)
#     ax3.set_title('Kernel Density Estimation of CMB Patch Areas')
#     ax3.set_xlabel('Area (pixels)')
#     ax3.set_ylabel('Density')
    
#     # Add summary statistics as text
#     stats_text = []
#     for subset in ['train', 'val']:
#         subset_data = df[df['subset'] == subset]['area']
#         stats = f"{subset.capitalize()} Set:\n"
#         stats += f"Count: {len(subset_data)}\n"
#         stats += f"Mean: {subset_data.mean():.2f}\n"
#         stats += f"Median: {subset_data.median():.2f}\n"
#         stats += f"Std: {subset_data.std():.2f}\n"
#         stats += f"Min: {subset_data.min():.2f}\n"
#         stats += f"Max: {subset_data.max():.2f}\n"
#         stats_text.append(stats)
    
#     plt.figtext(0.95, 0.5, '\n\n'.join(stats_text), 
#                 bbox=dict(facecolor='white', alpha=0.8),
#                 fontsize=10, ha='right')
    
#     # Adjust layout and save
#     plt.tight_layout()
#     plt.savefig(output_dir / 'cmb_area_distributions.png', dpi=300, bbox_inches='tight')
#     plt.close()
    
#     # Print summary
#     print("\nDistribution Statistics:")
#     print("\nAll patches:")
#     print(f"Total number of patches: {len(df)}")
#     print(f"Mean area: {df['area'].mean():.2f}")
#     print(f"Median area: {df['area'].median():.2f}")
#     print(f"Std area: {df['area'].std():.2f}")
    
#     for subset in ['train', 'val']:
#         subset_data = df[df['subset'] == subset]['area']
#         print(f"\n{subset.capitalize()} set:")
#         print(f"Number of patches: {len(subset_data)}")
#         print(f"Mean area: {subset_data.mean():.2f}")
#         print(f"Median area: {subset_data.median():.2f}")
#         print(f"Std area: {subset_data.std():.2f}")

# def main():
#     csv_file = "cmb_analysis_results/cmb_patch_areas.csv"
#     output_dir = "cmb_analysis_results/distribution_plots"
    
#     plot_area_distributions(csv_file, output_dir)
#     print(f"\nPlots saved in: {output_dir}")

# if __name__ == "__main__":
#     main()








# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# import numpy as np
# from pathlib import Path

# def plot_area_distribution(csv_file: str, output_dir: str = 'distribution_plots'):
#     """
#     Create a single distribution plot of all CMB patch areas.
    
#     Args:
#         csv_file: Path to the CSV file containing patch areas
#         output_dir: Directory to save the plot
#     """
#     # Create output directory
#     output_dir = Path(output_dir)
#     output_dir.mkdir(exist_ok=True)
    
#     # Read CSV file
#     df = pd.read_csv(csv_file)
    
#     # Create figure
#     plt.figure(figsize=(12, 8))
    
#     # Create histogram with KDE
#     sns.histplot(data=df, x='area', bins=50, kde=True, color='blue', alpha=0.6)
#     plt.title('Distribution of All CMB Patch Areas')
#     plt.xlabel('Area (pixels)')
#     plt.ylabel('Count')
    
#     # Add statistics text
#     stats_text = f"Statistics:\n"
#     stats_text += f"Total patches: {len(df)}\n"
#     stats_text += f"Mean: {df['area'].mean():.2f}\n"
#     stats_text += f"Median: {df['area'].median():.2f}\n"
#     stats_text += f"Std: {df['area'].std():.2f}\n"
#     stats_text += f"Min: {df['area'].min():.2f}\n"
#     stats_text += f"Max: {df['area'].max():.2f}"
    
#     plt.figtext(0.95, 0.7, stats_text, 
#                 bbox=dict(facecolor='white', alpha=0.8),
#                 fontsize=10, ha='right')
    
#     # Save plot
#     plt.tight_layout()
#     plt.savefig(output_dir / 'cmb_area_distribution_combined.png', dpi=300, bbox_inches='tight')
#     plt.close()
    
#     # Print statistics
#     print("\nDistribution Statistics:")
#     print(f"Total number of patches: {len(df)}")
#     print(f"Mean area: {df['area'].mean():.2f}")
#     print(f"Median area: {df['area'].median():.2f}")
#     print(f"Standard deviation: {df['area'].std():.2f}")
#     print(f"Minimum area: {df['area'].min():.2f}")
#     print(f"Maximum area: {df['area'].max():.2f}")

# def main():
#     csv_file = "cmb_analysis_results/cmb_patch_areas.csv"
#     output_dir = "cmb_analysis_results/distribution_plots"
    
#     plot_area_distribution(csv_file, output_dir)
#     print(f"\nPlot saved in: {output_dir}")

# if __name__ == "__main__":
#     main()
    
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

def add_value_labels(ax, spacing=5):
    """
    Add labels on top of each bar showing the count.
    
    Args:
        ax: Matplotlib axes object
        spacing: Vertical spacing for the labels
    """
    for rect in ax.patches:
        height = rect.get_height()
        if height > 0:  # Only add label if bar height is not zero
            ax.text(
                rect.get_x() + rect.get_width()/2,
                height + spacing,
                f'{int(height)}',
                ha='center',
                va='bottom',
                fontsize=8
            )

def plot_area_distribution(csv_file: str, output_dir: str = 'distribution_plots'):
    """
    Create a single distribution plot of all CMB patch areas with count labels.
    
    Args:
        csv_file: Path to the CSV file containing patch areas
        output_dir: Directory to save the plot
    """
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Read CSV file
    df = pd.read_csv(csv_file)
    
    # Create figure
    plt.figure(figsize=(15, 10))
    
    # Create histogram with KDE
    ax = sns.histplot(data=df, x='area', bins=50, kde=True, color='blue', alpha=0.6)
    plt.title('Distribution of All CMB Patch Areas', pad=20)  # Add padding to title
    plt.xlabel('Area (pixels)')
    plt.ylabel('Count')
    
    # Add count labels on top of bars
    add_value_labels(ax)
    
    # Add statistics text
    stats_text = f"Statistics:\n"
    stats_text += f"Total patches: {len(df)}\n"
    stats_text += f"Mean: {df['area'].mean():.2f}\n"
    stats_text += f"Median: {df['area'].median():.2f}\n"
    stats_text += f"Std: {df['area'].std():.2f}\n"
    stats_text += f"Min: {df['area'].min():.2f}\n"
    stats_text += f"Max: {df['area'].max():.2f}"
    
    plt.figtext(0.95, 0.7, stats_text, 
                bbox=dict(facecolor='white', alpha=0.8),
                fontsize=10, ha='right')
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save plot with high DPI
    plt.savefig(output_dir / 'cmb_area_distribution_combined.png', 
                dpi=300, 
                bbox_inches='tight',
                pad_inches=0.2)
    plt.close()
    
    # Print statistics
    print("\nDistribution Statistics:")
    print(f"Total number of patches: {len(df)}")
    print(f"Mean area: {df['area'].mean():.2f}")
    print(f"Median area: {df['area'].median():.2f}")
    print(f"Standard deviation: {df['area'].std():.2f}")
    print(f"Minimum area: {df['area'].min():.2f}")
    print(f"Maximum area: {df['area'].max():.2f}")

def main():
    csv_file = "/mnt/storage/ji/cmb_analysis_results_0205_2/cmb_patch_areas.csv"
    output_dir = "/mnt/storage/ji/cmb_analysis_results_0205_2/distribution_plots_0205"
    
    plot_area_distribution(csv_file, output_dir)
    print(f"\nPlot saved in: {output_dir}")

if __name__ == "__main__":
    main()