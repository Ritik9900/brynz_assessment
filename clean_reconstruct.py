import cv2
import numpy as np
import open3d as o3d
import pandas as pd
import os
import glob
from scipy.spatial.transform import Rotation as R
import sys

def load_camera_intrinsics(csv_path):
    try:
        matrix = np.loadtxt(csv_path, delimiter=',')
        if matrix.shape == (3, 3):
            return o3d.camera.PinholeCameraIntrinsic(
                width=1920, height=1440,
                fx=matrix[0, 0], fy=matrix[1, 1],
                cx=matrix[0, 2], cy=matrix[1, 2]
            )
    except:
        pass
    return o3d.camera.PinholeCameraIntrinsic(o3d.camera.PinholeCameraIntrinsicParameters.PrimeSenseDefault)

def load_odometry(csv_path):
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    poses = []
    for index, row in df.iterrows():
        pose = np.eye(4)
        if 'x' in df.columns:
            pose[0, 3] = row['x']
            pose[1, 3] = row['y']
            pose[2, 3] = row['z']
        if 'qx' in df.columns:
            quat = [row['qx'], row['qy'], row['qz'], row['qw']]
            pose[:3, :3] = R.from_quat(quat).as_matrix()
        poses.append(pose)
    return poses

def clean_reconstruct(base_path):
    print(f"Starting Clean Point Cloud Reconstruction for {base_path}...")
    
    rgb_video = os.path.join(base_path, 'rgb.mp4')
    depth_dir = os.path.join(base_path, 'depth')
    odometry_csv = os.path.join(base_path, 'odometry.csv')
    camera_matrix_csv = os.path.join(base_path, 'camera_matrix.csv')
    
    intrinsics = load_camera_intrinsics(camera_matrix_csv)
    poses = load_odometry(odometry_csv)
    
    cap = cv2.VideoCapture(rgb_video)
    depth_files = sorted(glob.glob(os.path.join(depth_dir, '*')))
    
    global_pcd = o3d.geometry.PointCloud()
    
    frame_idx = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or frame_idx >= len(depth_files) or frame_idx >= len(poses):
            break
            
        # Process every 2nd frame
        if frame_idx % 2 == 0:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_o3d = o3d.geometry.Image(rgb_frame)
            
            depth_img = cv2.imread(depth_files[frame_idx], cv2.IMREAD_UNCHANGED)
            if depth_img is not None:
                depth_img = cv2.resize(depth_img, (rgb_frame.shape[1], rgb_frame.shape[0]), interpolation=cv2.INTER_NEAREST)
                depth_o3d = o3d.geometry.Image(depth_img)
                
                rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
                    rgb_o3d, depth_o3d, depth_scale=1000.0, depth_trunc=3.0, convert_rgb_to_intensity=False
                )
                
                pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, intrinsics)
                pcd.transform(poses[frame_idx])
                
                global_pcd += pcd
                
        frame_idx += 1
        if frame_idx % 30 == 0:
            # Iterative downsampling to prevent memory explosion
            global_pcd = global_pcd.voxel_down_sample(voxel_size=0.01)
            print(f"Processed {frame_idx} frames...")

    cap.release()
    
    print("Applying final voxel downsampling and outlier removal...")
    global_pcd = global_pcd.voxel_down_sample(voxel_size=0.015)
    global_pcd, ind = global_pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
    
    output_ply = os.path.join(base_path, 'reconstructed_room_clean.ply')
    o3d.io.write_point_cloud(output_ply, global_pcd)
    print(f"Success! Saved clean point cloud to {output_ply}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        clean_reconstruct(sys.argv[1])
    else:
        print("Please provide a folder path.")
