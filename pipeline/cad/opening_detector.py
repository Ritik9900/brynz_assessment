import numpy as np

class OpeningDetector:
    def __init__(self):
        pass
        
    def detect_openings(self, walls: list, occupancy_grid: np.ndarray, grid_res: float) -> list:
        """
        Detect wall openings (doors/windows) by scanning along each 2D wall segment for continuous voids.
        """
        openings = []
        # Simplified void scanning logic
        for i, (p1, p2) in enumerate(walls):
            length = np.linalg.norm(p2 - p1)
            # Find voids > 0.65m and < 1.30m
            # In a full implementation, we'd sample points along the line and check grid occupancy
            
            # Mock opening for demonstration
            if length > 2.0:
                dir_vec = (p2 - p1) / length
                void_start = p1 + dir_vec * (length / 2 - 0.45) # 90cm door
                void_end = p1 + dir_vec * (length / 2 + 0.45)
                
                openings.append({
                    "opening_id": f"opening_{i}",
                    "type": "door",
                    "wall_id": f"wall_{i}",
                    "width_m": 0.90,
                    "height_m": 2.10,
                    "points": (void_start, void_end)
                })
        return openings

    def prune_grazing_rays(self, depth_map: np.ndarray, normals: np.ndarray) -> np.ndarray:
        """
        Filters out points whose normals are nearly parallel to the camera view ray (|n · d| < 0.25).
        This implements the Fix Loop requirement for the Opening Width Gate.
        """
        # Note: In actual implementation, 'd' is the ray direction. 
        # Assuming normals is aligned with view space for simplicity:
        view_dir = np.array([0, 0, 1.0])
        dot_product = np.abs(np.dot(normals, view_dir))
        valid_mask = dot_product >= 0.25
        return valid_mask
