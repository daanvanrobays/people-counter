"""YOLO11 Video Processing Module

A clean architecture for YOLO11-based people counting with tracking and API integration.
"""

from .core.processor import VideoProcessor
from .detection.detector import YOLODetector
from .video.stream_manager import StreamManager
from .api.client import APIClient

__version__ = "1.0.0"
__all__ = ["VideoProcessor", "YOLODetector", "StreamManager", "APIClient"]