import numpy as np
import open3d as o3d
from scipy.stats import gaussian_kde
from scipy.signal import find_peaks

class CeilingDetector:
    def __init__(self, bandwidth: float = 0.005):
        self.bandwidth = bandwidth
        
    def detect_heights(self, pcd: o3d.geometry.PointCloud) -> tuple:
        """
        Projects points to Z-axis and uses KDE to find floor and ceiling Z coordinates.
        Returns (z_floor, z_ceiling, ceiling_height_m).
        """
        points = np.asarray(pcd.points)
        if len(points) == 0:
            return 0.0, 0.0, 0.0
            
        z_vals = points[:, 2]
        
        # Kernel Density Estimation
        kde = gaussian_kde(z_vals, bw_method=self.bandwidth)
        z_range = np.linspace(z_vals.min(), z_vals.max(), 1000)
        density = kde(z_range)
        
        # Find modes
        peaks, _ = find_peaks(density, distance=100)
        
        if len(peaks) < 2:
            return 0.0, 0.0, 0.0
            
        # The two largest peaks should be floor and ceiling
        peak_densities = density[peaks]
        largest_peaks_idx = np.argsort(peak_densities)[-2:]
        
        z1 = z_range[peaks[largest_peaks_idx[0]]]
        z2 = z_range[peaks[largest_peaks_idx[1]]]
        
        z_floor = min(z1, z2)
        z_ceiling = max(z1, z2)
        
        return z_floor, z_ceiling, z_ceiling - z_floor
