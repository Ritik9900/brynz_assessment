from shapely.geometry import Polygon, Point, LineString
import numpy as np

class PolygonStitcher:
    def __init__(self):
        pass
        
    def generate_room_polygon(self, walls: list, center: np.ndarray) -> Polygon:
        """
        Ray-cast from room centers to wall segments to generate watertight Shapely 2D polygons.
        """
        # Simplified: assume walls form a closed loop or find intersection points
        # For mock, we just create a bounding box based on walls
        if not walls:
            return Polygon()
            
        points = []
        for p1, p2 in walls:
            points.append(p1)
            points.append(p2)
            
        points = np.array(points)
        min_x, min_y = np.min(points[:, 0]), np.min(points[:, 1])
        max_x, max_y = np.max(points[:, 0]), np.max(points[:, 1])
        
        return Polygon([(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)])
