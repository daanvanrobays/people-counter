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


def get_config(config_type: int = 0):
    if config_type == 0:
        return Config(
            enable_api=False,
            api_url="",
            api_interval=60,
            angle_offset=45.0,
            distance_offset=80.0,
            device="Kamerotski",
            stream_url="",
            coords_left_line=530,
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
            coords_left_line=370,
        )
