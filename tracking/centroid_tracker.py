from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np


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

    def register(self, centroid):
        """Register a new object with a given centroid."""
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1

    def deregister(self, object_id):
        """Deregister an object by its ID."""
        del self.objects[object_id]
        del self.disappeared[object_id]

    def update(self, rects):
        """
        Update the tracking with the latest bounding box rectangles.

        :param rects: List of bounding boxes as (x1, y1, x2, y2).
        :return: Dictionary of object IDs and their centroids.
        """
        if not rects:
            self.handle_disappeared_objects()
            return self.objects

        input_centroids = self.compute_centroids(rects)

        if not self.objects:
            self.initialize_objects(input_centroids)
        else:
            self.match_objects(input_centroids)

        return self.objects

    def handle_disappeared_objects(self):
        """Mark all tracked objects as disappeared and deregister if needed."""
        for object_id in list(self.disappeared.keys()):
            self.disappeared[object_id] += 1
            if self.disappeared[object_id] > self.max_disappeared:
                self.deregister(object_id)

    def compute_centroids(self, rects):
        """
        Compute centroids from bounding box coordinates.

        :param rects: List of bounding boxes as (x1, y1, x2, y2).
        :return: Numpy array of centroids.
        """
        centroids = np.zeros((len(rects), 2), dtype="int")
        for i, (start_x, start_y, end_x, end_y) in enumerate(rects):
            centroids[i] = (int((start_x + end_x) / 2.0), int((start_y + end_y) / 2.0))
        return centroids

    def initialize_objects(self, input_centroids):
        """Register new centroids as new objects."""
        for centroid in input_centroids:
            self.register(centroid)

    def match_objects(self, input_centroids):
        """
        Match input centroids to existing objects and update or register them.

        :param input_centroids: Numpy array of centroids from the current frame.
        """
        object_ids = list(self.objects.keys())
        object_centroids = list(self.objects.values())
        distance_matrix = dist.cdist(np.array(object_centroids), input_centroids)

        rows, cols = self.get_matching_indices(distance_matrix)
        used_rows, used_cols = set(), set()

        for row, col in zip(rows, cols):
            if row in used_rows or col in used_cols:
                continue

            if distance_matrix[row, col] > self.max_distance:
                continue

            object_id = object_ids[row]
            self.objects[object_id] = input_centroids[col]
            self.disappeared[object_id] = 0
            used_rows.add(row)
            used_cols.add(col)

        self.handle_unmatched_objects(distance_matrix, used_rows, used_cols, object_ids, input_centroids)

    def get_matching_indices(self, distance_matrix):
        """
        Get sorted row and column indices based on distance matrix.

        :param distance_matrix: Distance matrix between object centroids and input centroids.
        :return: Tuple of row indices and column indices.
        """
        rows = distance_matrix.min(axis=1).argsort()
        cols = distance_matrix.argmin(axis=1)[rows]
        return rows, cols

    def handle_unmatched_objects(self, distance_matrix, used_rows, used_cols, object_ids, input_centroids):
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
                self.register(input_centroids[col])
