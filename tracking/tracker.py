import logging
import datetime
import numpy as np
from typing import Tuple, Dict, List
from tracking.trackable_object import TrackableObject

log = logging.getLogger(__name__)


def log_event(event_type, count, delta, direction, height, centroid, initial_position):
    date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log.info(
        f"{date_time}: {event_type} - count: {count}, delta: {delta}, dir: {direction}, height: {height}, "
        f"centroid: {centroid}, position: {initial_position}")


def filter_detections(detections, target_class):
    filtered_detections = [tuple(map(int, det[:4])) for det in detections if int(det[5]) == target_class]
    return filtered_detections


def angle_from_vertical(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
    """
    Calculate the absolute angle between the line from p1 to p2 and the vertical line.

    :param p1: The starting point of the line (person centroid).
    :param p2: The ending point of the line (umbrella centroid).
    :return: The absolute angle in degrees between the line and the vertical line.
    """
    dx, dy = np.array(p2) - np.array(p1)
    angle = np.arctan2(dx, dy) * (180 / np.pi)  # Angle in degrees
    angle = 180 - np.abs(angle)  # Ensure angle is positive
    return angle


def correlate_objects(persons: Dict[int, Tuple[int, int]], umbrellas: Dict[int, Tuple[int, int]],
                      angle_offset: float = 45.0, distance_threshold: float = 85.0) -> List[Tuple[int, int]]:
    """
    Correlate detected umbrellas with detected persons based on proximity and vertical angle constraint.

    :param persons: Dictionary of tracked persons with their centroids.
    :param umbrellas: Dictionary of tracked umbrellas with their centroids.
    :param angle_offset: Maximum angle offset from the vertical line to consider (for both north and south).
    :param distance_threshold: Maximum distance to consider for correlation.
    :return: List of correlations as tuples of (person_id, umbrella_id).
    """
    correlations = []
    for person_id, person_centroid in persons.items():
        for umbrella_id, umbrella_centroid in umbrellas.items():
            distance = np.linalg.norm(np.array(person_centroid) - np.array(umbrella_centroid))
            if distance < distance_threshold:
                angle = angle_from_vertical(person_centroid, umbrella_centroid)
                if angle <= angle_offset:
                    correlations.append((person_id, umbrella_id))
    return correlations


def handle_tracked_objects(delta, height, total, total_down, total_up, trackable_objects, tracked_persons):
    # Convert filtered detections to list of bounding boxes
    # Update tracking with bounding boxes
    for (object_id, centroid) in tracked_persons.items():
        to = trackable_objects.get(object_id, None)
        if to is None:
            to = TrackableObject(object_id, centroid)
            to.initialPositionUp = centroid[1] < height // 2
        else:
            y = [c[1] for c in to.centroids]
            direction = centroid[1] - np.mean(y)
            to.centroids.append(centroid)

            if direction < 0 and centroid[1] < height // 2 and not to.initialPositionUp:
                total_up += 1
                delta -= 1
                log_event(f"EXIT PERSON {object_id}", total_up, delta, direction, height, centroid[1],
                          to.initialPositionUp)
                to.initialPositionUp = not to.initialPositionUp

            elif direction > 0 and centroid[1] > height // 2 and to.initialPositionUp:
                total_down += 1
                delta += 1
                log_event(f"ENTER PERSON {object_id}", total_down, delta, direction, height, centroid[1],
                          to.initialPositionUp)
                to.initialPositionUp = not to.initialPositionUp

            total = total_down - total_up
        trackable_objects[object_id] = to
    return delta, total, total_down, total_up
