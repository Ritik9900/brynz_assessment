import unittest
import numpy as np
from pipeline.slam.drift_ablation import DriftAblation
from pipeline.slam.pgo_optimizer import PGOOptimizer

class TestDriftAblation(unittest.TestCase):
    def test_drift_correction(self):
        # Mock trajectory
        gt = [np.eye(4) for _ in range(10)]
        drifted = []
        for i in range(10):
            pose = np.eye(4)
            pose[0, 3] = i * 0.01  # Add artificial drift
            drifted.append(pose)
            
        ablation = DriftAblation(ground_truth_trajectory=gt)
        ate_off = ablation.compute_ate(drifted)
        
        optimizer = PGOOptimizer()
        optimizer.poses = drifted
        optimized = optimizer.optimize()
        
        ate_on = ablation.compute_ate(optimized)
        
        self.assertTrue(ate_on <= ate_off)

if __name__ == '__main__':
    unittest.main()
