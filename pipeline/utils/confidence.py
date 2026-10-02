class ConfidenceEstimator:
    def __init__(self):
        self.sensor_sigmas = {
            'lidar': 0.012,
            'video': 0.028,
            'photos': 0.075
        }
        self.slam_sigma = 0.005
        self.ransac_sigma = 0.005
        
    def estimate_confidence_interval(self, value: float, tier: str) -> dict:
        """
        Emit 95% Confidence Intervals.
        """
        sigma_sensor = self.sensor_sigmas.get(tier, 0.05)
        sigma_wall = (sigma_sensor**2 + self.slam_sigma**2 + self.ransac_sigma**2)**0.5
        
        return {
            "lower": float(value - 1.96 * sigma_wall),
            "upper": float(value + 1.96 * sigma_wall),
            "confidence_level": 0.95
        }
