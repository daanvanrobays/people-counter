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


def get_config():
    # initiate config.
    return Config(
        enable_api=False,
        api_url="",
        api_interval=60,
        angle_offset=45.0,
        distance_offset=80.0,
        device="Kamerotski",
        stream_url=""
    )
