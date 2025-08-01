import logging
import datetime
import numpy as np

log = logging.getLogger(__name__)


def filter_detections(detections, target_class, confidence_threshold=0.6):
    filtered_detections = [
        tuple(map(int, det[:4])) for det in detections
        if int(det[5]) == target_class and det[4] >= confidence_threshold
    ]
    return filtered_detections

def handle_tracked_objects(delta, height, total, total_down, total_up, tracked_objects, coords_left, debug_logger=None):
    # Convert filtered detections to list of bounding boxes
    # Update tracking with bounding boxes
    for (object_id, data) in tracked_objects.items():
        if data['type'] == 'umbrella':
            continue

        centroid = data['centroid']

        if data.get('initialPositionUp') is None:
            data['initialPositionUp'] = centroid[1] < height // 2
        else:
            y = [c[1] for c in data['centroids']]
            direction = centroid[1] - np.mean(y)
            data['centroids'].append(centroid)
            if len(data['centroids']) > 10:
                data['centroids'].pop(0)

            if direction < 0 and centroid[0] < coords_left and centroid[1] < height // 2 and not data['initialPositionUp']:
                total_up += 1
                delta -= 1
                log_message = f"EXIT {data['type']} {object_id}"
                if debug_logger:
                    debug_logger.log_info(log_message)
                data['initialPositionUp'] = not data['initialPositionUp']
            elif direction < 0 and centroid[0] > coords_left and centroid[1] < height // 2 and not data['initialPositionUp']:
                data['initialPositionUp'] = not data['initialPositionUp']

            elif direction > 0 and centroid[0] < coords_left and centroid[1] > height // 2 and data['initialPositionUp']:
                total_down += 1
                delta += 1
                log_message = f"ENTER {data['type']} {object_id}"
                if debug_logger:
                    debug_logger.log_info(log_message)
                data['initialPositionUp'] = not data['initialPositionUp']
            elif direction > 0 and centroid[0] > coords_left and centroid[1] > height // 2 and data['initialPositionUp']:
                data['initialPositionUp'] = not data['initialPositionUp']

            total = total_down - total_up
    return delta, total, total_down, total_up
