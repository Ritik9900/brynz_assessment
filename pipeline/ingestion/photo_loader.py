import os
import glob
from typing import List, Dict

class PhotoLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.rooms_data = {}
        
    def load(self) -> Dict[str, List[str]]:
        """
        Loads unposed stills per room.
        Expects directory structure: data_dir/room_name/image.jpg
        """
        if not os.path.exists(self.data_dir):
            return {}
            
        # Search for room subdirectories
        for item in os.listdir(self.data_dir):
            room_path = os.path.join(self.data_dir, item)
            if os.path.isdir(room_path):
                images = glob.glob(os.path.join(room_path, "*.jpg")) + \
                         glob.glob(os.path.join(room_path, "*.png"))
                if images:
                    self.rooms_data[item] = sorted(images)
                    
        return self.rooms_data

    def get_room_images(self, room_id: str) -> List[str]:
        return self.rooms_data.get(room_id, [])
