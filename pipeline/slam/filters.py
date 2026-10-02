import open3d as o3d
import numpy as np
import cv2

def statistical_outlier_removal(pcd: o3d.geometry.PointCloud, nb_neighbors: int = 20, std_ratio: float = 2.0) -> o3d.geometry.PointCloud:
    """
    Removes statistical outliers from a point cloud.
    """
    cl, ind = pcd.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
    return pcd.select_by_index(ind)

def bilateral_depth_filter(depth_map: np.ndarray, d: int = 5, sigma_color: float = 0.1, sigma_space: float = 5.0) -> np.ndarray:
    """
    Applies bilateral filtering to depth map to reduce multipath noise.
    Assumes depth map is in meters (float32).
    """
    # cv2.bilateralFilter works best on float32 if values are appropriately scaled
    filtered = cv2.bilateralFilter(depth_map, d, sigma_color, sigma_space)
    return filtered
