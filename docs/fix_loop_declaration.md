# Fix Declaration: Opening Width Gate Failure

### 1. Worst-Performing Gate
* Gate: Opening widths ≤ 2 cm on ≥ 85% of openings.
* Baseline Metric (Before Fix): 58.3% of openings within ≤ 2 cm. Mean Absolute Error (MAE) = 2.84 cm (FAIL).

### 2. Root-Cause Hypothesis & Evidence
* Evidence: In room_01 and connector_01, door widths were systematically overestimated by +2.5 cm to +4.2 cm. Inspection of raw depth maps reveals that LiDAR rays grazing door jambs suffer from multipath edge-bleeding ("flying pixels") that stretch into the adjacent room. The naive void detector treated these trailing edge points as open space, delaying the detected start of the wall.
* Hypothesis: The opening detector lacks edge-normal pruning. By filtering out points whose normals are nearly parallel to the camera view ray (|n · d| < 0.25) before computing wall-void contours, and applying a robust RANSAC boundary fit to the void endpoints, opening boundary precision will improve to ≤ 1.5 cm.

### 3. Intended Fix & Predicted Outcome
* Fix: Implement `prune_grazing_rays()` in `pipeline/cad/opening_detector.py` and replace threshold void scanning with bilateral edge boundary localization.
* Predicted Metric: ≥ 88.0% of openings ≤ 2 cm, with an MAE ≤ 1.4 cm.

---
### 4. Regeneration Commands
* Before Run:
  `python run_pipeline.py --input data/benchmark/multi_room --tier lidar --config configs/legacy_pre_fix.yaml`
* After Run:
  `python run_pipeline.py --input data/benchmark/multi_room --tier lidar --config configs/config.yaml`
* Verification Script:
  `python tests/evaluate_fix_loop.py`
