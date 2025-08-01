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
    verbose: bool = False
    enable_composite_objects: bool = False
    tracking_algorithm: str = "centroid"  # "centroid" or "kalman"


def get_config(config_type: int = 0):
    if config_type == 0:
        return Config(
            enable_api=False,
            api_url="",
            api_interval=60,
            angle_offset=45.0,
            distance_offset=80.0,
            device="Kamerotski",
            stream_url="test/umbrella-2.mp4",
            coords_left_line=640,
            enable_composite_objects=True,
            tracking_algorithm="centroid",
        )
    else:
        return Config(
            enable_api=False,
            api_url="",
            api_interval=60,
            angle_offset=45.0,
            distance_offset=80.0,
            device="Henk",
            stream_url="",
            coords_left_line=640,
            enable_composite_objects=False,
            tracking_algorithm="kalman",
        )
