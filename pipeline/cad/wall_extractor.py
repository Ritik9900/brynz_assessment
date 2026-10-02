import numpy as np
import open3d as o3d
import cv2

class WallExtractor:
    def __init__(self, grid_res: float = 0.01):
        self.grid_res = grid_res
        
    def extract_walls(self, pcd: o3d.geometry.PointCloud, z_floor: float, z_ceiling: float):
        """
        Slices 3D point cloud, projects to 2D occupancy grid, and extracts wall lines.
        """
        points = np.asarray(pcd.points)
        
        # Slice between [Z_floor + 0.8m, Z_ceiling - 0.4m]
        mask = (points[:, 2] >= z_floor + 0.8) & (points[:, 2] <= z_ceiling - 0.4)
        sliced_points = points[mask]
        
        if len(sliced_points) == 0:
            return []
            
        # Project to 2D grid
        min_x, min_y = np.min(sliced_points[:, 0]), np.min(sliced_points[:, 1])
        max_x, max_y = np.max(sliced_points[:, 0]), np.max(sliced_points[:, 1])
        
        width = int((max_x - min_x) / self.grid_res) + 1
        height = int((max_y - min_y) / self.grid_res) + 1
        
        occupancy_grid = np.zeros((height, width), dtype=np.uint8)
        
        u = ((sliced_points[:, 0] - min_x) / self.grid_res).astype(int)
        v = ((sliced_points[:, 1] - min_y) / self.grid_res).astype(int)
        
        occupancy_grid[v, u] = 255
        
        # RANSAC/Hough to find lines (Manhattan regularization simplified here)
        lines = cv2.HoughLinesP(occupancy_grid, 1, np.pi / 2, threshold=50, minLineLength=50, maxLineGap=10)
        
        extracted_walls = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                p1 = np.array([x1 * self.grid_res + min_x, y1 * self.grid_res + min_y])
                p2 = np.array([x2 * self.grid_res + min_x, y2 * self.grid_res + min_y])
                extracted_walls.append((p1, p2))
                
        return extracted_walls
