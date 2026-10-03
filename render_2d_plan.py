import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import sys
import os

def generate_2d_map(ply_path, output_png):
    print(f"Loading global point cloud: {ply_path}")
    pcd = o3d.io.read_point_cloud(ply_path)
    points = np.asarray(pcd.points)

    if len(points) == 0:
        print("Point cloud is empty!")
        return

    # Extract Z-axis bounds (floor and ceiling detection)
    z_vals = points[:, 1]  # Assuming Y is Up in OpenCV/Open3D convention, so index 1 is height
    kde = gaussian_kde(z_vals[::10])  # Sample every 10th point for speed
    z_range = np.linspace(np.min(z_vals), np.max(z_vals), 500)
    density = kde(z_range)

    from scipy.signal import find_peaks
    peaks, _ = find_peaks(density, height=np.max(density)*0.1, distance=50)
    
    if len(peaks) < 2:
        print("Warning: Could not clearly separate floor and ceiling. Using min/max bounds.")
        floor_z = np.percentile(z_vals, 2)
        ceil_z = np.percentile(z_vals, 98)
    else:
        # Lowest peak is floor, highest peak is ceiling
        peak_zs = sorted(z_range[peaks])
        floor_z = peak_zs[0]
        ceil_z = peak_zs[-1]

    # Slice the walls: take points that are between floor + 0.5m and ceil - 0.5m
    wall_mask = (points[:, 1] > floor_z + 0.5) & (points[:, 1] < ceil_z - 0.5)
    wall_points = points[wall_mask]

    # Project to 2D (X and Z coordinates in OpenCV are the ground plane)
    x_coords = wall_points[:, 0]
    y_coords = wall_points[:, 2]

    print("Rendering 2D Floorplan...")
    plt.figure(figsize=(10, 10), facecolor='white')
    # Plot as a 2D histogram/heatmap for a solid blueprint look
    plt.hist2d(x_coords, y_coords, bins=250, cmap='Blues', cmin=1)
    
    plt.title("Rendered 2D Floor Plan (Combined House)", fontsize=16, pad=20)
    plt.xlabel("X (meters)")
    plt.ylabel("Z (meters)")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.axis('equal')
    
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    print(f"Success! 2D Floorplan saved to {output_png}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ply_file = sys.argv[1]
    else:
        ply_file = "combined_house.ply"
        
    out_file = "rendered_floorplan.png"
    if os.path.exists(ply_file):
        generate_2d_map(ply_file, out_file)
    else:
        print(f"Error: {ply_file} not found.")
