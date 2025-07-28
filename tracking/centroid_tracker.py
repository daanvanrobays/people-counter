from typing import List, Tuple
from scipy.spatial import distance as dist
from scipy.optimize import linear_sum_assignment
from collections import OrderedDict
import numpy as np
import logging

from helpers.utils import get_matching_indices, compute_centroids, angle_from_vertical, calculate_iou

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

    def register(self, rect, obj_type):
        """Register a new object with a given bounding box."""
        if self.next_object_id > 99:
            self.next_object_id = 0

        # To prevent overwriting an existing object, find the next available ID
        while self.next_object_id in self.objects:
            self.next_object_id += 1
        
        # Calculate centroid from bounding box
        centroid = (int((rect[0] + rect[2]) / 2.0), int((rect[1] + rect[3]) / 2.0))
            
        self.objects[self.next_object_id] = {
            'centroid': centroid, 
            'centroids': [centroid], 
            'bbox': rect,
            'bboxes': [rect],
            'type': obj_type, 
            'correlations': OrderedDict()
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

        filtered_objects = self.filter_by_type(obj_type)

        if not filtered_objects:
            self.initialize_objects(rects, obj_type)
        else:
            self.match_objects(rects, obj_type)

        return self.filter_by_type(obj_type)

    def handle_disappeared_objects(self):
        """Mark all tracked objects as disappeared and deregister if needed."""
        for object_id in list(self.disappeared.keys()):
            self.disappeared[object_id] += 1
            if self.disappeared[object_id] > self.max_disappeared:
                self.deregister(object_id)

    def initialize_objects(self, input_rects, obj_type):
        """Register new bounding boxes as new objects."""
        for rect in input_rects:
            self.register(rect, obj_type)

    def match_objects(self, input_rects, obj_type):
        """
        Match input bounding boxes to existing objects and update or register them.

        :param obj_type: Type of objects to be tracked.
        :param input_rects: List of bounding boxes from the current frame.
        """
        input_centroids = compute_centroids(input_rects)
        
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
            new_centroid = (int(input_centroids[col][0]), int(input_centroids[col][1]))
            filtered_objects[object_id]['centroid'] = new_centroid
            filtered_objects[object_id]['centroids'].append(new_centroid)
            filtered_objects[object_id]['bbox'] = input_rects[col]
            filtered_objects[object_id]['bboxes'].append(input_rects[col])
            
            # Keep history limited
            if len(filtered_objects[object_id]['centroids']) > 10:
                filtered_objects[object_id]['centroids'].pop(0)
            if len(filtered_objects[object_id]['bboxes']) > 10:
                filtered_objects[object_id]['bboxes'].pop(0)
                
            self.disappeared[object_id] = 0
            used_rows.add(row)
            used_cols.add(col)

        self.handle_unmatched_objects(distance_matrix, used_rows, used_cols, object_ids, input_rects, obj_type)

    def handle_unmatched_objects(self, distance_matrix, used_rows, used_cols, object_ids, input_rects, obj_type):
        """
        Handle objects that were not matched and register new objects if needed.

        :param distance_matrix: Distance matrix between object centroids and input centroids.
        :param used_rows: Set of used row indices.
        :param used_cols: Set of used column indices.
        :param object_ids: List of object IDs.
        :param input_rects: List of input bounding boxes.
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
                self.register(input_rects[col], obj_type)

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
        Uses dynamic scoring and one-to-one optimal matching via Hungarian algorithm.

        :param angle_offset: Maximum angle offset from the vertical line to consider (for both north and south).
        :param distance_threshold: Maximum distance to consider for correlation.
        """
        persons = self.filter_by_type('person')
        umbrellas = self.filter_by_type('umbrella')

        if not persons or not umbrellas:
            return []

        # Step 1: Update correlation scores for all pairs
        self._update_correlation_scores(persons, umbrellas, angle_offset, distance_threshold)
        
        # Step 2: Apply one-to-one optimal matching
        optimal_matches = self._find_optimal_matches(persons, umbrellas)
        
        # Step 3: Return correlations for matched pairs
        correlations = []
        for person_id, umbrella_id in optimal_matches:
            person_score = persons[person_id]['correlations'].get(umbrella_id, 0)
            umbrella_score = umbrellas[umbrella_id]['correlations'].get(person_id, 0)
            correlations.append((person_id, person_score, umbrella_id, umbrella_score))
        
        return correlations

    def _update_correlation_scores(self, persons, umbrellas, angle_offset, distance_threshold):
        """Update correlation scores for all person-umbrella pairs including IoU."""
        for person_id, person_data in persons.items():
            for umbrella_id, umbrella_data in umbrellas.items():
                distance = np.linalg.norm(np.array(person_data["centroid"]) - np.array(umbrella_data["centroid"]))
                
                # Calculate IoU if both objects have bounding boxes
                iou = 0.0
                if 'bbox' in person_data and 'bbox' in umbrella_data:
                    iou = calculate_iou(person_data['bbox'], umbrella_data['bbox'])
                
                if distance < distance_threshold:
                    angle = angle_from_vertical(person_data['centroid'], umbrella_data['centroid'])
                    if angle <= angle_offset:
                        # Dynamic score increment: inversely proportional to distance and angle
                        # Normalize distance (0-1, where 1 is closest)
                        distance_factor = max(0, 1 - (distance / distance_threshold))
                        # Normalize angle (0-1, where 1 is most vertical)  
                        angle_factor = max(0, 1 - (angle / angle_offset))
                        
                        # IoU provides strong evidence of correlation
                        # Scale IoU contribution: IoU > 0.1 provides significant boost
                        iou_factor = min(1.0, iou * 5.0) if iou > 0.05 else 0.0
                        
                        # Combined score increment with IoU weighting
                        base_score = 0.01 + (0.04 * distance_factor * angle_factor)
                        iou_bonus = 0.06 * iou_factor  # Up to 0.06 bonus for high IoU
                        score_increment = base_score + iou_bonus
                        
                        update_score(person_data, umbrella_id, score_increment)
                        update_score(umbrella_data, person_id, score_increment)
                    else:
                        # If IoU is high but angle is wrong, be less harsh
                        if iou > 0.1:
                            # High IoU suggests they're related despite angle issues
                            score_increment = 0.02 * iou
                            update_score(person_data, umbrella_id, score_increment)
                            update_score(umbrella_data, person_id, score_increment)
                        else:
                            # Gradual score decay for angle misalignment
                            angle_penalty = min(0.03, (angle - angle_offset) / angle_offset * 0.03)
                            score_decrement = -angle_penalty
                            update_score(person_data, umbrella_id, score_decrement)
                            update_score(umbrella_data, person_id, score_decrement)
                else:
                    # If distance is far but IoU is high, still give some credit
                    if iou > 0.1:
                        score_increment = 0.015 * iou
                        update_score(person_data, umbrella_id, score_increment)
                        update_score(umbrella_data, person_id, score_increment)
                    else:
                        # Gradual score decay for distance - less harsh for brief separations
                        distance_penalty = min(0.02, (distance - distance_threshold) / distance_threshold * 0.02)
                        score_decrement = -distance_penalty
                        update_score(person_data, umbrella_id, score_decrement)
                        update_score(umbrella_data, person_id, score_decrement)

    def _find_optimal_matches(self, persons, umbrellas, min_score_threshold=0.1):
        """
        Find optimal one-to-one matches using Hungarian algorithm.
        
        :param persons: Dictionary of person objects
        :param umbrellas: Dictionary of umbrella objects  
        :param min_score_threshold: Minimum score to consider a valid match
        :return: List of (person_id, umbrella_id) tuples for optimal matches
        """
        person_ids = list(persons.keys())
        umbrella_ids = list(umbrellas.keys())
        
        if not person_ids or not umbrella_ids:
            return []
        
        # Create cost matrix (negative scores since Hungarian minimizes cost)
        cost_matrix = np.full((len(person_ids), len(umbrella_ids)), 1.0)  # High cost for no correlation
        
        for i, person_id in enumerate(person_ids):
            person_correlations = persons[person_id]['correlations']
            for j, umbrella_id in enumerate(umbrella_ids):
                if umbrella_id in person_correlations:
                    score = person_correlations[umbrella_id]
                    if score >= min_score_threshold:
                        cost_matrix[i, j] = 1.0 - score  # Convert to cost (lower is better)
        
        # Apply Hungarian algorithm
        person_indices, umbrella_indices = linear_sum_assignment(cost_matrix)
        
        # Extract valid matches (below cost threshold)
        optimal_matches = []
        for p_idx, u_idx in zip(person_indices, umbrella_indices):
            if cost_matrix[p_idx, u_idx] < (1.0 - min_score_threshold):  # Valid match
                optimal_matches.append((person_ids[p_idx], umbrella_ids[u_idx]))
        
        return optimal_matches
