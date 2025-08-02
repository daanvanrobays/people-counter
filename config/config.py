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


def get_config(config_type: int = 0):
    if config_type == 0:
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
        )
