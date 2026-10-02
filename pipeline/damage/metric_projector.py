class MetricProjector:
    def __init__(self):
        pass
        
    def project_to_3d(self, mask_pixels: list, wall_plane: list) -> float:
        """
        Back-project segmented 2D mask pixels onto corresponding 3D wall polygon 
        to calculate exact surface area in m^2.
        """
        # Mock projection
        return 1.5 # Mock area
