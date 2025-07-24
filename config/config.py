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


def get_config(input):
    # initiate config.
    if input == 0:
        return Config(
            enable_api=True,
            api_url="https://aff.SERVER.be/stats",
            api_interval=60,
            angle_offset=45.0,
            distance_offset=80.0,
            device="Kamerotski",
            stream_url="rtsp://admin:PASSWORD@192.168.1.167:554/cam/realmonitor?channel=1&subtype=0",
            coords_left_line=480
        )
    else:
        return Config(
            enable_api=True,
            api_url="https://aff.SERVER.be/stats",
            api_interval=60,
            angle_offset=45.0,
            distance_offset=85.0,
            device="Henk",
            stream_url="rtsp://admin:PASSWORD@192.168.1.49:554/cam/realmonitor?channel=1&subtype=0",
            coords_left_line=395
        )
