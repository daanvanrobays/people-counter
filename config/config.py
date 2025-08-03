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
    coords_left_line: int = 0
    coords_right_line: int = 640
    verbose: bool = False
    enable_composite_objects: bool = False
    debug_mode: bool = False
    yolo_model: str = "yolov8m.pt"


def get_config(input):
    # Check for temporary config file first
    temp_config_file = f"config/temp_config_{input}.json"
    if os.path.exists(temp_config_file):
        try:
            with open(temp_config_file, 'r') as f:
                config_data = json.load(f)
            # Filter out UI-specific fields that the Config class doesn't know about
            config_data.pop('config_updated', None)
            return Config(**config_data)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error loading temp config: {e}, falling back to default")

    if input == 0:
        return Config(
            enable_api=False,
            api_url="",
            api_interval=60,
            angle_offset=45.0,
            distance_offset=80.0,
            device="Kamerotski",
            stream_url="test/escalator.webm",
            coords_left_line=50,
            coords_right_line=480,
            enable_composite_objects=False,
            yolo_model="yolov8m.pt",
        )
    else:
        return Config(
            enable_api=False,
            api_url="",
            api_interval=60,
            angle_offset=45.0,
            distance_offset=80.0,
            device="Henk",
            stream_url="test/escalator.webm",
            coords_left_line=0,
            coords_right_line=395,
            enable_composite_objects=False,
            yolo_model="yolov8m.pt",
        )
