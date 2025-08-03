"""Visualization configuration settings."""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class VisualizationConfig:
    """Configuration for visualization elements."""
    
    # Color settings (BGR format for OpenCV)
    person_color: Tuple[int, int, int] = (0, 255, 0)      # Green
    umbrella_color: Tuple[int, int, int] = (255, 0, 0)     # Blue
    composite_color: Tuple[int, int, int] = (0, 255, 255)  # Yellow
    correlation_color: Tuple[int, int, int] = (255, 255, 255)  # White
    info_panel_color: Tuple[int, int, int] = (0, 0, 0)     # Black
    text_color: Tuple[int, int, int] = (255, 255, 255)     # White
    tracking_line_color: Tuple[int, int, int] = (0, 0, 255)  # Red
    
    # Size settings
    centroid_radius: int = 3
    line_thickness: int = 1
    text_thickness: int = 2
    text_scale: float = 0.6
    info_text_scale: float = 0.7
    
    # Info panel settings
    info_panel_height: int = 100
    info_panel_alpha: float = 0.6
    info_text_margin: int = 15
    info_line_spacing: int = 30
    
    # Label settings
    label_offset_x: int = 10
    label_offset_y: int = 10