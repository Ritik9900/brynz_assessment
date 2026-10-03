# Brynz Reconstruction Pipeline

A deterministic, hybrid geometric-AI architecture to extract structural dimensions and damage metrics from consumer-grade LiDAR, Video, and Photo captures.

## Requirements
- Python 3.9+
- iPhone 15 Pro / Pro Max (for Tier 3 LiDAR) or standard (for Photos/Video)
- Dependencies: `pip install -r requirements.txt` (includes `open3d`, `opencv-python`, `numpy`, `matplotlib`, `scipy`, `pandas`)

## Quickstart (Under 15 Minutes)
To run the full pipeline on a fresh capture folder (e.g., `my_room_capture/` containing `rgb.mp4`, `depth/`, and `odometry.csv`):

### 1. Clean & Reconstruct 3D Geometry
This generates a highly accurate, noise-filtered 3D point cloud of the room, fixing any ARKit drift or intrinsic shearing.
```bash
python clean_reconstruct.py my_room_capture
```

### 2. Global Stitching (For Multi-Room)
If you captured multiple rooms separately, stitch them into a single global pose graph:
```bash
python stitch_rooms.py room1_clean.ply room2_clean.ply room3_clean.ply
```
*Outputs: `combined_house.ply`*

### 3. Generate 2D Rendered Blueprint
Extracts walls and slices the point cloud to generate a 2D floorplan.
```bash
python render_2d_plan.py combined_house.ply
```
*Outputs: `rendered_floorplan.png`*

### 4. Rule Evaluation & Output Contract
Applies the JSON rule engine (`rules.json`) and pricing database (`pricing_db.json`) against the extracted geometry to generate the final schema-compliant contract.
```bash
python generate_contract.py
```
*Outputs: `final_contract.json`*

## Documentation
- [Technical Architecture](docs/technical_report.md)
- [Fix Loop Declaration](docs/fix_loop_report.md)
- [Benchmark Analysis](docs/benchmark_report.md)
- [Capture Protocol](docs/capture_protocol.md)
- [Compliance Matrix](docs/compliance_matrix.md)
