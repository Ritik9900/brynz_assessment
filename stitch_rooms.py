import open3d as o3d
import numpy as np
import sys
import os

def preprocess_point_cloud(pcd, voxel_size):
    # Downsample and compute features
    pcd_down = pcd.voxel_down_sample(voxel_size)
    radius_normal = voxel_size * 2
    pcd_down.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))
    radius_feature = voxel_size * 5
    pcd_fpfh = o3d.pipelines.registration.compute_fpfh_feature(
        pcd_down, o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100))
    return pcd_down, pcd_fpfh

def get_registration_matrix(source_down, target_down, source_fpfh, target_fpfh, voxel_size):
    distance_threshold = voxel_size * 1.5
    
    # 1. Fast Global Registration
    global_result = o3d.pipelines.registration.registration_fgr_based_on_feature_matching(
        source_down, target_down, source_fpfh, target_fpfh,
        o3d.pipelines.registration.FastGlobalRegistrationOption(
            maximum_correspondence_distance=distance_threshold))
            
    # 2. Point-to-Plane ICP for robust tight lock
    icp_result = o3d.pipelines.registration.registration_icp(
        source_down, target_down, voxel_size * 0.4, global_result.transformation,
        o3d.pipelines.registration.TransformationEstimationPointToPlane(),
        o3d.pipelines.registration.ICPConvergenceCriteria(relative_fitness=1e-6, relative_rmse=1e-6, max_iteration=50))
        
    # 3. Calculate Information Matrix (Confidence in the match)
    information_icp = o3d.pipelines.registration.get_information_matrix_from_point_clouds(
        source_down, target_down, voxel_size * 1.5, icp_result.transformation)
        
    return icp_result.transformation, information_icp

def stitch_with_pose_graph(ply_files):
    if len(ply_files) < 2:
        print("Need at least 2 .ply files to stitch.")
        return

    print("Loading point clouds...")
    pcds = [o3d.io.read_point_cloud(f) for f in ply_files]
    voxel_size = 0.1 # 10cm voxel size
    
    pcds_down = []
    fpfhs = []
    for pcd in pcds:
        down, fpfh = preprocess_point_cloud(pcd, voxel_size)
        pcds_down.append(down)
        fpfhs.append(fpfh)

    print("Building Pose Graph...")
    pose_graph = o3d.pipelines.registration.PoseGraph()
    odometry = np.identity(4)
    pose_graph.nodes.append(o3d.pipelines.registration.PoseGraphNode(odometry))

    n_pcds = len(pcds)
    
    # Compare every point cloud against every other point cloud to find "Loop Closures"
    for source_id in range(n_pcds):
        for target_id in range(source_id + 1, n_pcds):
            print(f"  Matching room {source_id} to room {target_id}...")
            
            transformation, information = get_registration_matrix(
                pcds_down[source_id], pcds_down[target_id], 
                fpfhs[source_id], fpfhs[target_id], voxel_size)
                
            if target_id == source_id + 1: # Odometry edge (Sequential)
                odometry = np.dot(transformation, odometry)
                pose_graph.nodes.append(o3d.pipelines.registration.PoseGraphNode(np.linalg.inv(odometry)))
                pose_graph.edges.append(o3d.pipelines.registration.PoseGraphEdge(source_id, target_id, transformation, information, uncertain=False))
            else: # Loop closure edge (Non-sequential overlap)
                pose_graph.edges.append(o3d.pipelines.registration.PoseGraphEdge(source_id, target_id, transformation, information, uncertain=True))

    print("Optimizing Pose Graph (Distributing drift errors)...")
    option = o3d.pipelines.registration.GlobalOptimizationOption(
        max_correspondence_distance=voxel_size * 1.5,
        edge_prune_threshold=0.25,
        reference_node=0)
        
    o3d.pipelines.registration.global_optimization(
        pose_graph,
        o3d.pipelines.registration.GlobalOptimizationLevenbergMarquardt(),
        o3d.pipelines.registration.GlobalOptimizationConvergenceCriteria(),
        option)

    print("Merging globally optimized point clouds...")
    master_pcd = o3d.geometry.PointCloud()
    for point_id in range(n_pcds):
        # Transform the raw point cloud by the globally optimized pose
        pcds[point_id].transform(pose_graph.nodes[point_id].pose)
        master_pcd += pcds[point_id]

    master_pcd = master_pcd.voxel_down_sample(voxel_size=0.02)
    output_file = "combined_house.ply"
    o3d.io.write_point_cloud(output_file, master_pcd)
    print(f"Finished stitching! Saved combined point cloud to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python stitch_rooms.py <room1.ply> <room2.ply> ...")
    else:
        files_to_stitch = sys.argv[1:]
        for f in files_to_stitch:
            if not os.path.exists(f):
                print(f"Error: File not found: {f}")
                sys.exit(1)
        stitch_with_pose_graph(files_to_stitch)
