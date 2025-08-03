"""Frame rendering module for drawing detection and tracking results."""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Any, Optional

from .config import VisualizationConfig


class FrameRenderer:
    """Handles rendering of detection and tracking results on video frames."""
    
    def __init__(self, config: Optional[VisualizationConfig] = None):
        """Initialize the frame renderer.
        
        Args:
            config: Visualization configuration. Uses default if None.
        """
        self.config = config or VisualizationConfig()
    
    def render_frame(self, 
                    frame: np.ndarray,
                    tracked_persons: Dict[int, Dict[str, Any]],
                    tracked_umbrellas: Dict[int, Dict[str, Any]],
                    correlations: List[Tuple[int, float, int, float]],
                    width: int,
                    height: int,
                    info_status: List[Tuple[str, Any]],
                    coords_left: int,
                    coords_right: int,
                    tracked_composites: Optional[Dict[int, Dict[str, Any]]] = None) -> np.ndarray:
        """Render all visual elements onto the frame.
        
        Args:
            frame: Input frame to draw on
            tracked_persons: Dictionary of tracked person objects
            tracked_umbrellas: Dictionary of tracked umbrella objects
            correlations: List of correlations between persons and umbrellas
            width: Frame width
            height: Frame height
            info_status: Status information to display
            coords_left: Left tracking line coordinate
            coords_right: Right tracking line coordinate
            tracked_composites: Dictionary of tracked composite objects
            
        Returns:
            Frame with all visual elements drawn
        """
        # Create a copy to avoid modifying the original frame
        rendered_frame = frame.copy()
        
        # Draw tracking lines
        self._draw_tracking_lines(rendered_frame, width, height, coords_left, coords_right)
        
        # Draw correlations first (background)
        self._draw_correlations(rendered_frame, tracked_persons, tracked_umbrellas, correlations)
        
        # Draw tracked objects
        self._draw_tracked_objects(rendered_frame, tracked_persons, "P", self.config.person_color)
        self._draw_tracked_objects(rendered_frame, tracked_umbrellas, "U", self.config.umbrella_color)
        
        # Draw composite objects if provided
        if tracked_composites:
            self._draw_tracked_objects(rendered_frame, tracked_composites, "C", self.config.composite_color)
        
        # Draw information panel
        self._draw_info_panel(rendered_frame, width, height, info_status)
        
        return rendered_frame
    
    def _draw_tracking_lines(self, frame: np.ndarray, width: int, height: int, 
                           coords_left: int, coords_right: int) -> None:
        """Draw the tracking boundary lines.
        
        Args:
            frame: Frame to draw on
            width: Frame width
            height: Frame height
            coords_left: Left boundary coordinate
            coords_right: Right boundary coordinate
        """
        # Horizontal center line
        cv2.line(frame, (0, height // 2), (width, height // 2), 
                self.config.tracking_line_color, self.config.line_thickness)
        
        # Left vertical boundary
        cv2.line(frame, (coords_left, 0), (coords_left, height), 
                self.config.tracking_line_color, self.config.line_thickness)
        
        # Right vertical boundary
        cv2.line(frame, (coords_right, 0), (coords_right, height), 
                self.config.tracking_line_color, self.config.line_thickness)
    
    def _draw_correlations(self, frame: np.ndarray,
                          tracked_persons: Dict[int, Dict[str, Any]],
                          tracked_umbrellas: Dict[int, Dict[str, Any]],
                          correlations: List[Tuple[int, float, int, float]]) -> None:
        """Draw correlation lines between persons and umbrellas.
        
        Args:
            frame: Frame to draw on
            tracked_persons: Dictionary of tracked person objects
            tracked_umbrellas: Dictionary of tracked umbrella objects
            correlations: List of correlations to draw
        """
        for person_id, _, umbrella_id, _ in correlations:
            if person_id in tracked_persons and umbrella_id in tracked_umbrellas:
                person_centroid = tracked_persons[person_id]["centroid"]
                umbrella_centroid = tracked_umbrellas[umbrella_id]["centroid"]
                
                cv2.line(frame, person_centroid, umbrella_centroid,
                        self.config.correlation_color, self.config.line_thickness)
    
    def _draw_tracked_objects(self, frame: np.ndarray,
                            tracked_objects: Dict[int, Dict[str, Any]],
                            label_prefix: str,
                            color: Tuple[int, int, int]) -> None:
        """Draw tracked objects with their IDs.
        
        Args:
            frame: Frame to draw on
            tracked_objects: Dictionary of tracked objects
            label_prefix: Prefix for object labels (e.g., "P" for person)
            color: Color to use for drawing
        """
        for object_id, data in tracked_objects.items():
            self._draw_single_object(frame, object_id, data, label_prefix, color)
    
    def _draw_single_object(self, frame: np.ndarray, object_id: int,
                          data: Dict[str, Any], label: str,
                          color: Tuple[int, int, int]) -> None:
        """Draw a single tracked object.
        
        Args:
            frame: Frame to draw on
            object_id: ID of the object
            data: Object data containing centroid information
            label: Label prefix for the object
            color: Color to use for drawing
        """
        centroid = data["centroid"]
        
        # Draw centroid dot
        cv2.circle(frame, centroid, self.config.centroid_radius, color, -1)
        
        # Draw object ID label
        label_text = f"{label}{object_id}"
        label_position = (
            centroid[0] + self.config.label_offset_x,
            centroid[1] + self.config.label_offset_y
        )
        
        cv2.putText(frame, label_text, label_position,
                   cv2.FONT_HERSHEY_SIMPLEX, self.config.text_scale,
                   color, self.config.text_thickness)
    
    def _draw_info_panel(self, frame: np.ndarray, width: int, height: int,
                        info_status: List[Tuple[str, Any]]) -> None:
        """Draw the information panel with tracking statistics.
        
        Args:
            frame: Frame to draw on
            width: Frame width
            height: Frame height
            info_status: List of (key, value) pairs to display
        """
        panel_height = self.config.info_panel_height
        
        # Create semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, height - panel_height), (width, height),
                     self.config.info_panel_color, -1)
        
        # Blend overlay with original frame
        cv2.addWeighted(overlay, self.config.info_panel_alpha, frame,
                       1 - self.config.info_panel_alpha, 0, frame)
        
        # Draw text information
        y_position = height - panel_height + self.config.info_line_spacing
        
        for key, value in info_status:
            text = f"{key}: {value}"
            cv2.putText(frame, text, (self.config.info_text_margin, y_position),
                       cv2.FONT_HERSHEY_SIMPLEX, self.config.info_text_scale,
                       self.config.text_color, self.config.text_thickness)
            y_position += self.config.info_line_spacing
    
    def draw_detection_boxes(self, frame: np.ndarray,
                           detections: List[List[float]],
                           class_names: Optional[Dict[int, str]] = None,
                           confidence_threshold: float = 0.5) -> np.ndarray:
        """Draw detection bounding boxes on the frame.
        
        Args:
            frame: Frame to draw on
            detections: List of detections [x1, y1, x2, y2, conf, class_id]
            class_names: Optional mapping of class IDs to names
            confidence_threshold: Minimum confidence to draw
            
        Returns:
            Frame with detection boxes drawn
        """
        rendered_frame = frame.copy()
        
        for detection in detections:
            if len(detection) < 6:
                continue
                
            x1, y1, x2, y2, confidence, class_id = detection
            
            if confidence < confidence_threshold:
                continue
            
            # Convert coordinates to integers
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            class_id = int(class_id)
            
            # Choose color based on class
            if class_id == 0:  # Person
                color = self.config.person_color
            elif class_id == 25:  # Umbrella
                color = self.config.umbrella_color
            else:
                color = (128, 128, 128)  # Gray for other classes
            
            # Draw bounding box
            cv2.rectangle(rendered_frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{class_names.get(class_id, class_id) if class_names else class_id}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            
            # Draw label background
            cv2.rectangle(rendered_frame, (x1, y1 - label_size[1] - 10),
                         (x1 + label_size[0], y1), color, -1)
            
            # Draw label text
            cv2.putText(rendered_frame, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return rendered_frame
    
    def update_config(self, new_config: VisualizationConfig) -> None:
        """Update the visualization configuration.
        
        Args:
            new_config: New visualization configuration
        """
        self.config = new_config