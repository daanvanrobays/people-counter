"""People counting logic based on object tracking."""

import logging
import datetime
import numpy as np
from typing import Dict, Any, Tuple
from config.config import Config

log = logging.getLogger(__name__)


class PeopleCounter:
    """Handles people counting logic based on tracked object movements."""
    
    def __init__(self, config: Config):
        """Initialize the people counter.
        
        Args:
            config: Configuration object with counting parameters
        """
        self.config = config
        self.total_down = 0
        self.total_up = 0
        self.delta = 0
        self.total = 0
    
    def update_counts(self, tracked_objects: Dict[int, Dict[str, Any]], 
                     frame_height: int) -> Tuple[int, int, int, int]:
        """Update people counts based on tracked object movements.
        
        Args:
            tracked_objects: Dictionary of tracked objects
            frame_height: Height of the frame for direction calculation
            
        Returns:
            Tuple of (delta, total, total_down, total_up)
        """
        for object_id, data in tracked_objects.items():
            centroid = data['centroid']
            
            # Initialize tracking state if needed
            if data.get('initialPositionUp') is None:
                data['initialPositionUp'] = centroid[1] < frame_height // 2
            else:
                # Calculate movement direction
                y_positions = [c[1] for c in data['centroids']]
                direction = centroid[1] - np.mean(y_positions)
                
                # Update centroid history
                data['centroids'].append(centroid)
                if len(data['centroids']) > 10:
                    data['centroids'].pop(0)
                
                # Check for crossing events
                self._check_crossing_event(object_id, data, direction, frame_height, centroid)
        
        # Update total count
        self.total = self.total_down - self.total_up
        
        return self.delta, self.total, self.total_down, self.total_up
    
    def _check_crossing_event(self, object_id: int, data: Dict[str, Any], 
                            direction: float, frame_height: int, centroid: Tuple[int, int]) -> None:
        """Check if an object has crossed a counting line.
        
        Args:
            object_id: ID of the tracked object
            data: Object tracking data
            direction: Movement direction (negative = up, positive = down)
            frame_height: Height of the frame
            centroid: Current centroid position
        """
        x, y = centroid
        is_in_counting_zone = self.config.coords_left_line < x < self.config.coords_right_line
        is_upper_half = y < frame_height // 2
        is_lower_half = y > frame_height // 2
        
        # Check for entering (moving up, crossing into upper half)
        if (direction < 0 and is_in_counting_zone and is_upper_half and 
            not data['initialPositionUp']):
            self.total_down += 1
            self.delta += 1
            self._log_crossing_event("ENTER", data['type'], object_id, self.total_down, 
                                   self.delta, direction, frame_height, centroid, 
                                   data['initialPositionUp'])
            data['initialPositionUp'] = True
            
        # Check for boundary reset (outside counting zone)
        elif (direction < 0 and not is_in_counting_zone and is_upper_half and 
              not data['initialPositionUp']):
            data['initialPositionUp'] = True
            
        # Check for exiting (moving down, crossing into lower half)
        elif (direction > 0 and is_in_counting_zone and is_lower_half and 
              data['initialPositionUp']):
            self.total_up += 1
            self.delta -= 1
            self._log_crossing_event("EXIT", data['type'], object_id, self.total_up, 
                                   self.delta, direction, frame_height, centroid, 
                                   data['initialPositionUp'])
            data['initialPositionUp'] = False
            
        # Check for boundary reset (outside counting zone)
        elif (direction > 0 and not is_in_counting_zone and is_lower_half and 
              data['initialPositionUp']):
            data['initialPositionUp'] = False
    
    def _log_crossing_event(self, event_type: str, object_type: str, object_id: int,
                          count: int, delta: int, direction: float, frame_height: int,
                          centroid: Tuple[int, int], initial_position: bool) -> None:
        """Log a crossing event.
        
        Args:
            event_type: Type of event ("ENTER" or "EXIT")
            object_type: Type of object (e.g., "person", "umbrella")
            object_id: ID of the object
            count: Current count for this event type
            delta: Current delta value
            direction: Movement direction
            frame_height: Frame height
            centroid: Object centroid position
            initial_position: Initial position flag
        """

        if self.config.verbose:
            log.info(
                f"{event_type} {object_type} {object_id} - "
                f"count: {count}, delta: {delta}, dir: {direction:.2f}, "
                f"height: {frame_height}, centroid: {centroid}, "
                f"initial_pos_up: {initial_position}"
            )
        else:
            log.info(
                f"{event_type} {object_type} {object_id} - "
                f"count: {count}, delta: {delta}"
            )
    
    def reset_counts(self) -> None:
        """Reset all counting statistics."""
        self.total_down = 0
        self.total_up = 0
        self.delta = 0
        self.total = 0
        log.info("People counter statistics reset")
    
    def get_statistics(self) -> Dict[str, int]:
        """Get current counting statistics.
        
        Returns:
            Dictionary with current statistics
        """
        return {
            "total_down": self.total_down,
            "total_up": self.total_up,
            "delta": self.delta,
            "total": self.total
        }
    
    def update_config(self, new_config: Config) -> None:
        """Update the configuration.
        
        Args:
            new_config: New configuration object
        """
        self.config = new_config
        log.info("People counter configuration updated")