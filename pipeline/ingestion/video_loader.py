import cv2
import os

class VideoLoader:
    def __init__(self, video_path: str):
        self.video_path = video_path
        self.cap = None
        self.fps = 0
        self.frame_count = 0
        
    def load(self) -> bool:
        """Opens video file and reads metadata."""
        if not os.path.exists(self.video_path):
            return False
            
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            return False
            
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return True
        
    def get_frame(self, frame_idx: int):
        if self.cap is None:
            return None
            
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None
        
    def extract_keyframes(self, sample_rate_hz: float = 1.0):
        """Extracts keyframes at a given Hz."""
        if self.cap is None or self.fps <= 0:
            return []
            
        frames = []
        step = max(1, int(self.fps / sample_rate_hz))
        
        for i in range(0, self.frame_count, step):
            frame = self.get_frame(i)
            if frame is not None:
                frames.append(frame)
                
        return frames

    def release(self):
        if self.cap is not None:
            self.cap.release()
