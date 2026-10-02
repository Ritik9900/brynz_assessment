import os
import json
import csv
import numpy as np
import open3d as o3d
import cv2

class LidarLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.poses = []
        self.intrinsics = None
        self.rgb_files = []
        self.depth_files = []
        
    def load(self):
        """Loads RGB, Depth, Intrinsics and Odometry from Record3D exported format."""
        odom_file = os.path.join(self.data_dir, "odometry.csv")
        matrix_file = os.path.join(self.data_dir, "camera_matrix.csv")
        
        if os.path.exists(matrix_file):
            self.intrinsics = self._parse_intrinsics(matrix_file)
        
        if os.path.exists(odom_file):
            self.poses = self._parse_odometry(odom_file)
            
        rgb_dir = os.path.join(self.data_dir, "rgb")
        depth_dir = os.path.join(self.data_dir, "depth")
        
        if os.path.exists(rgb_dir):
            self.rgb_files = sorted([os.path.join(rgb_dir, f) for f in os.listdir(rgb_dir) if f.endswith('.jpg') or f.endswith('.png')])
            
        if os.path.exists(depth_dir):
            self.depth_files = sorted([os.path.join(depth_dir, f) for f in os.listdir(depth_dir) if f.endswith('.png')])
            
        return len(self.poses)
        
    def _parse_intrinsics(self, file_path):
        K = np.eye(3)
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i < 3:
                    K[i, :] = [float(x) for x in row[:3]]
        return K

    def _parse_odometry(self, file_path):
        poses = []
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            # Record3D odometry is usually px, py, pz, qx, qy, qz, qw or full 4x4 matrix
            # Assuming 4x4 matrix flattened row-major for simplicity or similar format
            for row in reader:
                try:
                    # Parse based on expected ARKit 4x4 matrix flatten length or position+quaternion
                    if len(row) >= 16:
                        mat = np.array([float(x) for x in row[:16]]).reshape(4, 4)
                        poses.append(mat)
                    elif len(row) >= 7:
                        # Extract translation and quaternion, skipping for this template
                        pass
                except ValueError:
                    pass # Header row
        return poses

    def unproject_depth(self, frame_idx: int) -> o3d.geometry.PointCloud:
        """Unprojects a depth map to a point cloud using the camera intrinsics."""
        if not self.intrinsics is not None or frame_idx >= len(self.depth_files):
            return o3d.geometry.PointCloud()
            
        depth_img = cv2.imread(self.depth_files[frame_idx], cv2.IMREAD_UNCHANGED)
        if depth_img is None:
            return o3d.geometry.PointCloud()
            
        # Assuming 16-bit depth in millimeters
        depth_map = depth_img.astype(np.float32) / 1000.0 
        
        h, w = depth_map.shape
        fx, fy = self.intrinsics[0, 0], self.intrinsics[1, 1]
        cx, cy = self.intrinsics[0, 2], self.intrinsics[1, 2]
        
        v, u = np.indices((h, w))
        z = depth_map
        x = (u - cx) * z / fx
        y = (v - cy) * z / fy
        
        points = np.stack((x, y, z), axis=-1).reshape(-1, 3)
        valid = z.flatten() > 0
        
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points[valid])
        
        return pcd
