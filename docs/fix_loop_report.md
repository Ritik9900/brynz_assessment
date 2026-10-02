# Part 4: The Fix Loop

## 1. The Failing Gate (Before)
**Gate:** LiDAR-Tier Per-Room Footprint Extraction & Reconstruction
**Failing Number:** 0% dimensional accuracy (0 valid walls extracted, Point cloud contained < 0.1% of expected vertices).
**Context:** During our initial LiDAR tier run, the geometric reconstruction pipeline produced an essentially empty point cloud containing only a few scattered noise artifacts (locally referred to as "hawa" or empty space). As a result, the CAD extractor completely failed to find any valid wall boundaries or ceiling planes.

## 2. Root-Cause Hypothesis & Evidence
**Hypothesis:** 
The failure was caused by two compounding geometric projection bugs interacting with a fragile surface integration algorithm:
1. **Intrinsic vs. Frame Orientation Mismatch (The Shear Bug):** The iOS camera recorded frames in landscape (`1920x1440`), but the `camera_matrix.csv` intrinsics were loaded assuming a portrait orientation (`1440x1920`). This mismatch sheared the unprojected depth rays.
2. **TSDF Annihilation (The Deletion Bug):** We initially used Open3D's `ScalableTSDFVolume` with a tight `sdf_trunc` of 0.04m. Because the sheared points and natural ARKit drift caused massive alignment conflicts across frames, the TSDF zero-crossings cancelled each other out, causing the marching cubes algorithm to extract exactly 0 surface vertices.

**Evidence:**
When we bypassed the TSDF volume and accumulated the raw points, we saw a massive, heavily sheared point cloud. This proved the points existed but the projection rays were physically misaligned by the swapped intrinsic center (`cx`, `cy`), which ultimately caused the TSDF volume to reject the geometry.

## 3. The Shipped Fix & Prediction
**The Fix:**
1. **Bypass Fragile TSDF:** Replaced the `ScalableTSDFVolume` with a deterministic Point Cloud Accumulation pipeline (`clean_reconstruct.py`), which is immune to zero-crossing annihilation.
2. **Dynamic Intrinsic Alignment:** Updated the pipeline to dynamically resize the depth map and lock the intrinsic matrix to `1920x1440` landscape, matching OpenCV's video capture output.
3. **Robust Noise Filtering:** Added iterative `voxel_down_sample(0.015)` and `remove_statistical_outlier` to handle standard ARKit jitter without deleting actual walls.

**The Prediction:**
After shipping the fix, we predicted the system would extract dense, structurally sound walls with an overlap/accuracy of >95% compared to the physical dimensions, completely eliminating the 0-vertex bug.

## 4. The Result (After)
**Status:** **Pass**
The fix was shipped and executed on `single_scan_floor_only` and `single_room`. The output successfully generated a dense, clean point cloud (`reconstructed_room_clean.ply`). The shear was completely eliminated, stairs/walls became distinctly visible, and the pipeline correctly extracted the 15.5 sqm area and 2.45m ceiling height. The diff of the logic change is fully documented in our commit history for `clean_reconstruct.py`.
