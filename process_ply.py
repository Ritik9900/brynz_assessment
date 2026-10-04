import argparse
import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from scipy.signal import find_peaks
import cv2

class CeilingDetector:
    def __init__(self, bandwidth: float = 0.005):
        self.bandwidth = bandwidth
        
    def detect_heights(self, pcd: o3d.geometry.PointCloud) -> tuple:
        points = np.asarray(pcd.points)
        if len(points) == 0:
            return 0.0, 0.0, 0.0
            
        # Y axis is UP in ARKit
        y_vals = points[:, 1] 
        kde = gaussian_kde(y_vals, bw_method=self.bandwidth)
        y_range = np.linspace(y_vals.min(), y_vals.max(), 1000)
        density = kde(y_range)
        peaks, _ = find_peaks(density, distance=100)
        
        if len(peaks) < 2:
            return 0.0, 0.0, 0.0
            
        peak_densities = density[peaks]
        largest_peaks_idx = np.argsort(peak_densities)[-2:]
        y1 = y_range[peaks[largest_peaks_idx[0]]]
        y2 = y_range[peaks[largest_peaks_idx[1]]]
        y_floor = min(y1, y2)
        y_ceiling = max(y1, y2)
        
        # Robust fallback for incomplete scans (missing ceilings)
        if y_ceiling - y_floor < 2.0:
            print("Warning: Detected ceiling height is unreasonably low. Assuming scan is missing ceiling. Falling back to standard 2.5m ceiling.")
            y_ceiling = y_floor + 2.5
            
        return y_floor, y_ceiling, y_ceiling - y_floor

class WallExtractor:
    def __init__(self, grid_res: float = 0.01):
        self.grid_res = grid_res
        
    def extract_walls(self, pcd: o3d.geometry.PointCloud, y_floor: float, y_ceiling: float):
        points = np.asarray(pcd.points)
        # Slice horizontally across Y axis
        mask = (points[:, 1] >= y_floor + 0.3) & (points[:, 1] <= y_ceiling - 0.3)
        sliced_points = points[mask]
        
        if len(sliced_points) == 0:
            return []
            
        # Floorplan is on X-Z plane
        min_x, min_z = np.min(sliced_points[:, 0]), np.min(sliced_points[:, 2])
        max_x, max_z = np.max(sliced_points[:, 0]), np.max(sliced_points[:, 2])
        
        width = int((max_x - min_x) / self.grid_res) + 1
        height = int((max_z - min_z) / self.grid_res) + 1
        occupancy_grid = np.zeros((height, width), dtype=np.uint8)
        
        u = ((sliced_points[:, 0] - min_x) / self.grid_res).astype(int)
        v = ((sliced_points[:, 2] - min_z) / self.grid_res).astype(int)
        occupancy_grid[v, u] = 255
        
        lines = cv2.HoughLinesP(occupancy_grid, 1, np.pi / 2, threshold=50, minLineLength=50, maxLineGap=10)
        extracted_walls = []
        if lines is not None:
            for line in lines:
                x1, z1, x2, z2 = line.flatten()
                p1 = np.array([x1 * self.grid_res + min_x, z1 * self.grid_res + min_z])
                p2 = np.array([x2 * self.grid_res + min_x, z2 * self.grid_res + min_z])
                extracted_walls.append((p1, p2))
                
        return extracted_walls

def main():
    parser = argparse.ArgumentParser(description="Process PLY file directly for CAD extraction")
    parser.add_argument("--input", required=True, help="Path to reconstructed_room.ply")
    parser.add_argument("--plot", action="store_true", help="Plot 2D walls")
    args = parser.parse_args()

    print(f"Loading point cloud from {args.input}...")
    pcd = o3d.io.read_point_cloud(args.input)
    
    if len(pcd.points) == 0:
        print("Error: Point cloud is empty or failed to load.")
        return

    # Downsample point cloud for faster KDE processing
    print(f"Original points: {len(pcd.points)}")
    pcd = pcd.voxel_down_sample(voxel_size=0.01)
    print(f"Downsampled points: {len(pcd.points)}")

    # 1. Detect Ceiling & Floor
    print("\n--- Running Ceiling Detector ---")
    detector = CeilingDetector(bandwidth=0.005) # 5mm bandwidth as specified
    y_floor, y_ceiling, room_height = detector.detect_heights(pcd)
    print(f"Floor Y: {y_floor:.3f} m")
    print(f"Ceiling Y: {y_ceiling:.3f} m")
    print(f"Calculated Ceiling Height: {room_height:.3f} m")

    # 2. Extract Walls
    print("\n--- Running Wall Extractor ---")
    extractor = WallExtractor(grid_res=0.01) # 1cm grid
    walls = extractor.extract_walls(pcd, y_floor, y_ceiling)
    
    print(f"Extracted {len(walls)} wall segments.")
    for i, (p1, p2) in enumerate(walls):
        length = np.linalg.norm(p2 - p1)
        print(f"Wall {i+1}: Start({p1[0]:.2f}, {p1[1]:.2f}) -> End({p2[0]:.2f}, {p2[1]:.2f}) | Length: {length:.2f} m")
        
    if args.plot:
        print("\nRendering Blueprint-Style 2D Floor Plan...")
        plt.figure(figsize=(10, 10))
        
        # Use points that are BETWEEN floor and ceiling (to see walls clearly)
        points = np.asarray(pcd.points)
        mask = (points[:, 1] >= y_floor + 0.5) & (points[:, 1] <= y_ceiling - 0.5)
        sliced_points = points[mask]
        
        # X and Z are the floorplan axes
        x_vals = sliced_points[:, 0]
        z_vals = sliced_points[:, 2]
        
        # Create a 2D histogram density plot (blueprint style)
        plt.hist2d(x_vals, z_vals, bins=300, cmap='Blues', cmin=1)
        
        plt.title("Rendered 2D Floor Plan (Blueprint Map)", fontsize=16)
        plt.xlabel("X (meters)", fontsize=12)
        plt.ylabel("Z (meters)", fontsize=12)
        plt.axis('equal')
        plt.grid(True, linestyle='--', alpha=0.5)
        
        plot_path = "docs/rendered_floorplan.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Saved Blueprint 2D floorplan visualization to {plot_path}")

if __name__ == "__main__":
    main()
