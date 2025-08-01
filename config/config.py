import json
import os
from dataclasses import dataclass


@dataclass
class Config:
    enable_api: bool = False
    api_url: str = ""
    api_interval: int = 600
    angle_offset: float = 45.0
    distance_offset: float = 85.0
    device: str = "default"
    stream_url: str = ""
    coords_left_line: int = 640
    debug_mode: bool = False


def get_config(input):
    # Check for temporary config file first
    temp_config_file = f"config/temp_config_{input}.json"
    if os.path.exists(temp_config_file):
        try:
            with open(temp_config_file, 'r') as f:
                config_data = json.load(f)
            return Config(**config_data)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error loading temp config: {e}, falling back to default")
    
    # Original config logic
    if input == 0:
        return Config(
            enable_api=False,
            api_url="https://aff.SERVER.be/stats",
            api_interval=60,
            device="Kamerotski",
            stream_url="rtsp://admin:PASSWORD@192.168.1.167:554/cam/realmonitor?channel=1&subtype=0",
            coords_left_line=480
        )
    else:
        return Config(
            enable_api=False,
            api_url="https://aff.SERVER.be/stats",
            api_interval=60,
            device="Henk",
            stream_url="rtsp://admin:PASSWORD@192.168.1.49:554/cam/realmonitor?channel=1&subtype=0",
            coords_left_line=395
        )
