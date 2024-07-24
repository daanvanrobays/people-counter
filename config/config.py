from dataclasses import dataclass


@dataclass
class Config:
    enable_api: bool = False
    api_url: str = ""
    api_interval: int = 600
    correlation_angle: float = 45.0
    correlation_distance: float = 85.0
    device: str = "default"
    stream_url: str = ""


def get_config():
    # initiate config.
    return Config(
        enable_api=False,
        api_url="",
        api_interval=60,
        correlation_angle=45.0,
        correlation_distance=85.0,
        device="Kamerotski",
        stream_url=""
    )
