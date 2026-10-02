# Capture Route & Protocol (Stock Capture Route)

**Target Audience:** Non-engineer homeowners or field technicians.
**Supported Devices:** iPhone 15 Pro / iPhone 15 Pro Max (or newer Pro models).

## 1. What to Install
We use a reliable, off-the-shelf LiDAR data logger to capture the raw sensors.
1. Open the App Store on your iPhone.
2. Search for and install **Record3D**.
3. Open Record3D, go to Settings, and ensure the export format is set to **Raw Data (Depth + ARKit Odometry)** at **30 FPS**.

## 2. How to Walk & Capture
1. **Starting Point:** Stand at the entrance of the room with your back against the door frame.
2. **Start Recording:** Press the red record button. 
3. **The Walk:**
   - Walk slowly along the perimeter of the room (about 1 step per second).
   - Keep the phone held at chest height.
   - Point the camera slightly downwards (about 30 degrees) so it captures the intersection of the floor and the wall.
   - Once you complete the perimeter, stand in the center of the room and slowly pan the phone upwards to capture the ceiling.
4. **Time Limit:** Keep the capture under **60 seconds** per room to minimize ARKit drift.
5. **Stop:** Press stop when the room is fully mapped.

## 3. What to Avoid
- **Fast movements:** Do not whip or jerk the phone. It blurs the camera and breaks the pose tracking.
- **Mirrors and Glass:** If there is a large mirror or glass door, try to capture it at an angle rather than dead-on, as LiDAR pulses pass through or bounce off glass unpredictably.
- **Purely featureless walls:** If a wall is completely blank and white, make sure the floor or ceiling edge is visible in the frame so the tracker doesn't lose its position.

## 4. How to Hand the Files to the Pipeline
1. In the Record3D app, go to your library, select the capture, and tap **Export**.
2. Export as a `.zip` file via AirDrop, Email, or Google Drive to your computer.
3. Unzip the file. It will contain an `rgb.mp4`, a `depth/` folder, and `odometry.csv` / `camera_matrix.csv`.
4. Place this folder into the pipeline directory and run:
   ```bash
   python clean_reconstruct.py path_to_your_unzipped_folder
   python generate_contract.py
   ```
5. The system will automatically ingest the files, rebuild the room in 3D, extract the dimensions, and output the final structural contract JSON.
