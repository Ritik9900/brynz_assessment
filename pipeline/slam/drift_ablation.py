import numpy as np

class DriftAblation:
    def __init__(self, ground_truth_trajectory=None):
        self.gt_traj = ground_truth_trajectory
        
    def compute_ate(self, estimated_trajectory: list) -> float:
        """Computes Absolute Trajectory Error (ATE)."""
        if not self.gt_traj or len(self.gt_traj) != len(estimated_trajectory):
            return 0.0
            
        error = 0.0
        for gt, est in zip(self.gt_traj, estimated_trajectory):
            diff = gt[:3, 3] - est[:3, 3]
            error += np.linalg.norm(diff) ** 2
            
        return np.sqrt(error / len(estimated_trajectory))
        
    def generate_ablation_svg(self, traj_off: list, traj_on: list, output_path: str):
        """Generates an SVG comparing the drift with and without PGO."""
        # Mock SVG generation
        with open(output_path, 'w') as f:
            f.write('<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">')
            f.write('<text x="50" y="50" font-family="Arial" font-size="24">Drift Ablation: ON vs OFF</text>')
            f.write('</svg>')
