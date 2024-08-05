from typing import List, Tuple
from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np
import logging

from helpers.utils import get_matching_indices, compute_centroids, angle_from_vertical

log = logging.getLogger(__name__)


def update_score(obj_data, other_object_id, increment):
    """
    Update the correlation score for a matched object.

    :param obj_data: Data of the object being updated (person or umbrella).
    :param other_object_id: ID of the matched object (person or umbrella).
    :param increment: Value to increment (or decrement) the score.
    """
    if other_object_id in obj_data['correlations']:
        obj_data['correlations'][other_object_id] += increment
    else:
        obj_data['correlations'][other_object_id] = increment

    # Ensure the score stays within a defined range, e.g., 0 to 1
    obj_data['correlations'][other_object_id] = min(max(obj_data['correlations'][other_object_id], 0), 1)


class CentroidTracker:
    def __init__(self, max_disappeared=50, max_distance=50):
        """
        Initializes the centroid tracking with parameters for handling
        object disappearance and distance threshold for matching objects.

        :param max_disappeared: Maximum number of frames an object can
                                be missing before it is deregistered.
        :param max_distance: Maximum distance between centroids to
                             consider them the same object.
        """
        self.next_object_id = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance

    def register(self, centroid, obj_type):
        """Register a new object with a given centroid."""
        self.objects[self.next_object_id] = {
            'centroid': centroid, 'centroids': [centroid], 'type': obj_type, 'correlations': OrderedDict()
        }
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1

    def deregister(self, object_id):
        """Deregister an object by its ID."""
        del self.objects[object_id]
        del self.disappeared[object_id]

    def update(self, rects, obj_type):
        """
        Update the tracking with the latest bounding box rectangles.

        :param obj_type: Type of objects to be tracked.
        :param rects: List of bounding boxes as (x1, y1, x2, y2).
        :return: Dictionary of object IDs and their centroids.
        """
        if not rects:
            self.handle_disappeared_objects()
            return self.filter_by_type(obj_type)

        input_centroids = compute_centroids(rects)

        filtered_objects = self.filter_by_type(obj_type)

        if not filtered_objects:
            self.initialize_objects(input_centroids, obj_type)
        else:
            self.match_objects(input_centroids, obj_type)

        return self.filter_by_type(obj_type)

    def handle_disappeared_objects(self):
        """Mark all tracked objects as disappeared and deregister if needed."""
        for object_id in list(self.disappeared.keys()):
            self.disappeared[object_id] += 1
            if self.disappeared[object_id] > self.max_disappeared:
                self.deregister(object_id)

    def initialize_objects(self, input_centroids, obj_type):
        """Register new centroids as new objects."""
        for centroid in input_centroids:
            self.register(centroid, obj_type)

    def match_objects(self, input_centroids, obj_type):
        """
        Match input centroids to existing objects and update or register them.

        :param obj_type: Type of objects to be tracked.
        :param input_centroids: Numpy array of centroids from the current frame.
        """
        filtered_objects = self.filter_by_type(obj_type)
        object_ids = list(filtered_objects.keys())
        object_centroids = [data['centroid'] for data in filtered_objects.values()]
        distance_matrix = dist.cdist(np.array(object_centroids), input_centroids)

        rows, cols = get_matching_indices(distance_matrix)
        used_rows, used_cols = set(), set()

        for row, col in zip(rows, cols):
            if row in used_rows or col in used_cols:
                continue

            if distance_matrix[row, col] > self.max_distance:
                continue

            object_id = object_ids[row]
            filtered_objects[object_id]['centroid'] = input_centroids[col]
            filtered_objects[object_id]['centroids'].append(input_centroids[col])
            self.disappeared[object_id] = 0
            used_rows.add(row)
            used_cols.add(col)

        self.handle_unmatched_objects(distance_matrix, used_rows, used_cols, object_ids, input_centroids, obj_type)

    def handle_unmatched_objects(self, distance_matrix, used_rows, used_cols, object_ids, input_centroids, obj_type):
        """
        Handle objects that were not matched and register new objects if needed.

        :param distance_matrix: Distance matrix between object centroids and input centroids.
        :param used_rows: Set of used row indices.
        :param used_cols: Set of used column indices.
        :param object_ids: List of object IDs.
        :param input_centroids: Numpy array of input centroids.
        """
        unused_rows = set(range(distance_matrix.shape[0])) - used_rows
        unused_cols = set(range(distance_matrix.shape[1])) - used_cols

        if len(unused_rows) >= len(unused_cols):
            for row in unused_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
        else:
            for col in unused_cols:
                self.register(input_centroids[col], obj_type)

    def filter_by_type(self, obj_type):
        """
        Filter tracked objects by their type.

        :param obj_type: The type of objects to filter.
        :return: Dictionary of filtered objects.
        """
        return {object_id: data for object_id, data in self.objects.items() if data['type'] == obj_type}

    def correlate_objects(self, angle_offset: float = 45.0,
                          distance_threshold: float = 80.0) -> List[Tuple[int, float, int, float]]:
        """
        Correlate detected umbrellas with detected persons based on proximity and vertical angle constraint.

        :param angle_offset: Maximum angle offset from the vertical line to consider (for both north and south).
        :param distance_threshold: Maximum distance to consider for correlation.
        """
        persons = self.filter_by_type('person')
        umbrellas = self.filter_by_type('umbrella')

        correlations = []
        for person_id, person_data in persons.items():
            for umbrella_id, umbrella_data in umbrellas.items():
                distance = np.linalg.norm(np.array(person_data["centroid"]) - np.array(umbrella_data["centroid"]))
                if distance < distance_threshold:
                    angle = angle_from_vertical(person_data['centroid'], umbrella_data['centroid'])
                    if angle <= angle_offset:
                        # Increase score if within threshold distance and angle
                        score_increment = 0.02
                        update_score(person_data, umbrella_id, score_increment)
                        update_score(umbrella_data, person_id, score_increment)

                        correlations.append((person_id, person_data['correlations'][umbrella_id],
                                             umbrella_id, umbrella_data['correlations'][person_id]))
                    else:
                        # Decrease score if angle is beyond threshold
                        score_decrement = -0.05
                        update_score(person_data, umbrella_id, score_decrement)
                        update_score(umbrella_data, person_id, score_decrement)
                else:
                    # Decrease score if distance is beyond threshold
                    score_decrement = -0.05
                    update_score(person_data, umbrella_id, score_decrement)
                    update_score(umbrella_data, person_id, score_decrement)

        return correlations
