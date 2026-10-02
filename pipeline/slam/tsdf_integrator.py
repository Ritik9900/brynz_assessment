import open3d as o3d
import numpy as np

class TSDFIntegrator:
    def __init__(self, voxel_length: float = 0.01, sdf_trunc: float = 0.04):
        self.voxel_length = voxel_length
        self.sdf_trunc = sdf_trunc
        self.volume = o3d.pipelines.integration.ScalableTSDFVolume(
            voxel_length=self.voxel_length,
            sdf_trunc=self.sdf_trunc,
            color_type=o3d.pipelines.integration.TSDFVolumeColorType.RGB8
        )
        
    def integrate(self, color_image: o3d.geometry.Image, depth_image: o3d.geometry.Image, 
                  intrinsic: o3d.camera.PinholeCameraIntrinsic, extrinsic: np.ndarray):
        """
        Integrates a new RGB-D frame into the TSDF volume.
        """
        rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(
            color_image, depth_image, depth_scale=1000.0, depth_trunc=3.0, convert_rgb_to_intensity=False
        )
        
        self.volume.integrate(rgbd, intrinsic, extrinsic)
        
    def extract_point_cloud(self) -> o3d.geometry.PointCloud:
        """
        Extracts the voxelized point cloud from the TSDF volume.
        """
        return self.volume.extract_point_cloud()
