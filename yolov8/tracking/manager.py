"""Tracking manager that coordinates all tracking operations."""

import logging
from typing import Dict, List, Tuple, Any, Optional

from .filters import DetectionFilter
from .counter import PeopleCounter
from shared.tracking.centroid_tracker import CentroidTracker
from config.config import Config

log = logging.getLogger(__name__)


class TrackingManager:
    """Manages all tracking operations including detection filtering, object tracking, and counting."""
    
    def __init__(self, config: Config):
        """Initialize the tracking manager.
        
        Args:
            config: Configuration object
        """
        self.config = config
        
        # Initialize components
        self.filter = DetectionFilter()
        self.counter = PeopleCounter(config)
        self.tracker = CentroidTracker(
            max_disappeared=50,
            max_distance=50,
            composite_threshold=0.7,
            composite_frames=10
        )
    
    def process_detections(self, detections: List[List[float]], 
                         frame_height: int) -> Tuple[Dict, Dict, List, Dict, Tuple]:
        """Process detections through the complete tracking pipeline.
        
        Args:
            detections: Raw detections from YOLO
            frame_height: Height of the frame for counting logic
            
        Returns:
            Tuple of (filtered_persons, filtered_umbrellas, correlations, 
                     filtered_composites, count_stats)
        """
        # Filter detections by class
        person_detections = self.filter.filter_by_class(detections, target_class=0)
        umbrella_detections = self.filter.filter_by_class(detections, target_class=25)
        
        # Apply additional filtering if needed
        person_detections = self._apply_additional_filtering(person_detections)
        umbrella_detections = self._apply_additional_filtering(umbrella_detections)
        
        # Handle composite objects if enabled
        if self.config.enable_composite_objects:
            remaining_persons, remaining_umbrellas = self._handle_composite_objects(
                person_detections, umbrella_detections
            )
        else:
            remaining_persons = person_detections
            remaining_umbrellas = umbrella_detections
        
        # Update trackers
        filtered_persons = self.tracker.update(remaining_persons, obj_type="person")
        filtered_umbrellas = self.tracker.update(remaining_umbrellas, obj_type="umbrella")
        
        # Correlate objects
        correlations = self.tracker.correlate_objects(
            self.config.angle_offset,
            self.config.distance_offset
        )
        
        # Handle composite object logic
        filtered_composites = {}
        if self.config.enable_composite_objects:
            self.tracker.update_stable_correlations(correlations)
            self.tracker.check_composite_dissolution()
            filtered_composites = self.tracker.filter_by_type("person-with-umbrella")
        
        # Update counting logic
        count_stats = self.counter.update_counts(self.tracker.objects, frame_height)
        
        return (filtered_persons, filtered_umbrellas, correlations, 
                filtered_composites, count_stats)
    
    def _apply_additional_filtering(self, detections: List[Tuple[int, int, int, int]]) -> List[Tuple[int, int, int, int]]:
        """Apply additional filtering to detections.
        
        Args:
            detections: List of bounding boxes
            
        Returns:
            Filtered list of bounding boxes
        """
        # Apply area filtering
        detections = self.filter.filter_by_area(detections, min_area=100, max_area=50000)
        
        # Apply aspect ratio filtering
        detections = self.filter.filter_by_aspect_ratio(detections, min_ratio=0.2, max_ratio=5.0)
        
        return detections
    
    def _handle_composite_objects(self, person_detections: List[Tuple[int, int, int, int]], 
                                umbrella_detections: List[Tuple[int, int, int, int]]) -> Tuple[List, List]:
        """Handle composite object processing.
        
        Args:
            person_detections: List of person bounding boxes
            umbrella_detections: List of umbrella bounding boxes
            
        Returns:
            Tuple of (remaining_person_detections, remaining_umbrella_detections)
        """
        used_person_indices, used_umbrella_indices = self.tracker.update_composite_objects(
            person_detections, umbrella_detections
        )
        
        # Filter out detections used by composite objects
        remaining_persons = [
            bbox for i, bbox in enumerate(person_detections) 
            if i not in used_person_indices
        ]
        remaining_umbrellas = [
            bbox for i, bbox in enumerate(umbrella_detections) 
            if i not in used_umbrella_indices
        ]
        
        return remaining_persons, remaining_umbrellas
    
    def get_tracking_statistics(self) -> Dict[str, Any]:
        """Get comprehensive tracking statistics.
        
        Returns:
            Dictionary with tracking and counting statistics
        """
        # Get basic count statistics
        count_stats = self.counter.get_statistics()
        
        # Get tracking statistics
        total_objects = len(self.tracker.objects)
        persons = len(self.tracker.filter_by_type("person"))
        umbrellas = len(self.tracker.filter_by_type("umbrella"))
        composites = len(self.tracker.filter_by_type("person-with-umbrella"))
        
        return {
            **count_stats,
            "tracking": {
                "total_objects": total_objects,
                "persons": persons,
                "umbrellas": umbrellas,
                "composites": composites,
                "next_object_id": self.tracker.next_object_id
            }
        }
    
    def reset_tracking(self) -> None:
        """Reset all tracking state."""
        self.tracker = CentroidTracker(
            max_disappeared=50,
            max_distance=50,
            composite_threshold=0.7,
            composite_frames=10
        )
        self.counter.reset_counts()
        log.info("Tracking manager reset")
    
    def update_config(self, new_config: Config) -> None:
        """Update configuration for all components.
        
        Args:
            new_config: New configuration object
        """
        self.config = new_config
        self.counter.update_config(new_config)
        log.info("Tracking manager configuration updated")
    
    def get_object_history(self, object_id: int) -> Optional[Dict[str, Any]]:
        """Get the tracking history for a specific object.
        
        Args:
            object_id: ID of the object
            
        Returns:
            Object history data if found, None otherwise
        """
        return self.tracker.objects.get(object_id)