from typing import Tuple
import numpy as np


def get_matching_indices(distance_matrix):
    """
    Get sorted row and column indices based on distance matrix.

    :param distance_matrix: Distance matrix between object centroids and input centroids.
    :return: Tuple of row indices and column indices.
    """
    rows = distance_matrix.min(axis=1).argsort()
    columns = distance_matrix.argmin(axis=1)[rows]
    return rows, columns


def compute_centroids(rects):
    """
    Compute centroids from bounding box coordinates.

    :param rects: List of bounding boxes as (x1, y1, x2, y2).
    :return: Numpy array of centroids.
    """
    centroids = np.zeros((len(rects), 2), dtype="int")
    for i, (start_x, start_y, end_x, end_y) in enumerate(rects):
        centroids[i] = (int((start_x + end_x) / 2.0), int((start_y + end_y) / 2.0))
    return centroids


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
