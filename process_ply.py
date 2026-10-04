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
            
        z_vals = points[:, 2]
        kde = gaussian_kde(z_vals, bw_method=self.bandwidth)
        z_range = np.linspace(z_vals.min(), z_vals.max(), 1000)
        density = kde(z_range)
        peaks, _ = find_peaks(density, distance=100)
        
        if len(peaks) < 2:
            return 0.0, 0.0, 0.0
            
        peak_densities = density[peaks]
        largest_peaks_idx = np.argsort(peak_densities)[-2:]
        z1 = z_range[peaks[largest_peaks_idx[0]]]
        z2 = z_range[peaks[largest_peaks_idx[1]]]
        z_floor = min(z1, z2)
        z_ceiling = max(z1, z2)
        return z_floor, z_ceiling, z_ceiling - z_floor

class WallExtractor:
    def __init__(self, grid_res: float = 0.01):
        self.grid_res = grid_res
        
    def extract_walls(self, pcd: o3d.geometry.PointCloud, z_floor: float, z_ceiling: float):
        points = np.asarray(pcd.points)
        mask = (points[:, 2] >= z_floor + 0.8) & (points[:, 2] <= z_ceiling - 0.4)
        sliced_points = points[mask]
        
        if len(sliced_points) == 0:
            return []
            
        min_x, min_y = np.min(sliced_points[:, 0]), np.min(sliced_points[:, 1])
        max_x, max_y = np.max(sliced_points[:, 0]), np.max(sliced_points[:, 1])
        
        width = int((max_x - min_x) / self.grid_res) + 1
        height = int((max_y - min_y) / self.grid_res) + 1
        occupancy_grid = np.zeros((height, width), dtype=np.uint8)
        
        u = ((sliced_points[:, 0] - min_x) / self.grid_res).astype(int)
        v = ((sliced_points[:, 1] - min_y) / self.grid_res).astype(int)
        occupancy_grid[v, u] = 255
        
        lines = cv2.HoughLinesP(occupancy_grid, 1, np.pi / 2, threshold=50, minLineLength=50, maxLineGap=10)
        extracted_walls = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line.flatten()
                p1 = np.array([x1 * self.grid_res + min_x, y1 * self.grid_res + min_y])
                p2 = np.array([x2 * self.grid_res + min_x, y2 * self.grid_res + min_y])
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
    z_floor, z_ceiling, height = detector.detect_heights(pcd)
    print(f"Floor Z: {z_floor:.3f} m")
    print(f"Ceiling Z: {z_ceiling:.3f} m")
    print(f"Calculated Ceiling Height: {height:.3f} m")

    # 2. Extract Walls
    print("\n--- Running Wall Extractor ---")
    extractor = WallExtractor(grid_res=0.01) # 1cm grid
    walls = extractor.extract_walls(pcd, z_floor, z_ceiling)
    
    print(f"Extracted {len(walls)} wall segments.")
    for i, (p1, p2) in enumerate(walls):
        length = np.linalg.norm(p2 - p1)
        print(f"Wall {i+1}: Start({p1[0]:.2f}, {p1[1]:.2f}) -> End({p2[0]:.2f}, {p2[1]:.2f}) | Length: {length:.2f} m")
        
    if args.plot and len(walls) > 0:
        plt.figure(figsize=(8, 8))
        
        # Collect all points to compute the Convex Hull (clean floorplan outline)
        all_points = []
        for p1, p2 in walls:
            all_points.append(p1)
            all_points.append(p2)
        all_points = np.array(all_points, dtype=np.float32)
        
        hull = cv2.convexHull(all_points)
        hull_points = hull.reshape(-1, 2)
        
        # Close the polygon by appending the first point at the end
        hull_points = np.vstack([hull_points, hull_points[0]])
        
        # Plot clean filled polygon outline
        plt.plot(hull_points[:, 0], hull_points[:, 1], 'b-', linewidth=3, label="Room Boundary")
        plt.fill(hull_points[:, 0], hull_points[:, 1], alpha=0.3, color='blue', label="Walkable Area")
        plt.scatter(hull_points[:, 0], hull_points[:, 1], c='red', s=50, label="Vertices", zorder=5)
        
        plt.title("Extracted 2D Floorplan (Convex Hull)")
        plt.xlabel("X (meters)")
        plt.ylabel("Y (meters)")
        plt.axis('equal')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plot_path = "output_walls.png"
        plt.savefig(plot_path)
        print(f"\nSaved 2D floorplan visualization to {plot_path}")

if __name__ == "__main__":
    main()
