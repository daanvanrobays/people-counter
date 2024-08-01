import logging
import datetime
import numpy as np

log = logging.getLogger(__name__)


def log_event(event_type, count, delta, direction, height, centroid, initial_position):
    date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log.info(
        f"{date_time}: {event_type} - count: {count}, delta: {delta}, dir: {direction}, height: {height}, "
        f"centroid: {centroid}, position: {initial_position}")


def filter_detections(detections, target_class):
    filtered_detections = [tuple(map(int, det[:4])) for det in detections if int(det[5]) == target_class]
    return filtered_detections


def handle_tracked_objects(delta, height, total, total_down, total_up, tracked_objects):
    # Convert filtered detections to list of bounding boxes
    # Update tracking with bounding boxes
    for (object_id, data) in tracked_objects.items():
        centroid = data['centroid']

        if data.get('initialPositionUp') is None:
            data['initialPositionUp'] = centroid[1] < height // 2
        else:
            y = [c[1] for c in data['centroids']]
            direction = centroid[1] - np.mean(y)
            data['centroids'].append(centroid)
            if len(data['centroids']) > 10:
                data['centroids'].pop(0)

            if direction < 0 and centroid[1] < height // 2 and not data['initialPositionUp']:
                total_up += 1
                delta -= 1
                log_event(f"EXIT {data['type']} {object_id}", total_up, delta, direction, height,
                          centroid[1], data['initialPositionUp'])
                data['initialPositionUp'] = not data['initialPositionUp']

            elif direction > 0 and centroid[1] > height // 2 and data['initialPositionUp']:
                total_down += 1
                delta += 1
                log_event(f"ENTER {data['type']} {object_id}", total_down, delta, direction, height,
                          centroid[1], data['initialPositionUp'])
                data['initialPositionUp'] = not data['initialPositionUp']

            total = total_down - total_up
    return delta, total, total_down, total_up
