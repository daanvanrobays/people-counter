import argparse
from concurrent.futures import ThreadPoolExecutor
from ultralytics import YOLO

import cv2
import logging
import time

from config.config import get_config
from drawing.frame_drawer import draw_on_frame
from helpers.thread import ThreadingClass
from tracking.centroid_tracker import CentroidTracker
from tracking.tracker import filter_detections, handle_tracked_objects
from api.api import post_api

logging.basicConfig(level=logging.INFO, format="[INFO] %(message)s")
log = logging.getLogger(__name__)


def load_model():
    """Load the YOLOv8 model."""
    model = YOLO("yolov8m.pt")
    return model, None  # device is handled by ultralytics


def parse_arguments():
    # function to parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", type=int, default=0,
                    help="config input")
    args = vars(ap.parse_args())
    return args


def main():
    args = parse_arguments()
    config = get_config(args["input"])

    api_time = time.time() if config.enable_api else None

    width, height = None, None
    total_frames = 1
    total_down = 0
    total_up = 0
    delta = 0
    total = 0

    # Load model
    model, _ = load_model()

    # Initialize the video stream based on the source
    is_network_stream = isinstance(config.stream_url, str) and \
                        (config.stream_url.startswith("rtsp://") or
                         config.stream_url.startswith("http://") or
                         config.stream_url.startswith("https://"))

    if is_network_stream:
        log.info("Using threaded video stream for network source.")
        cap = ThreadingClass(config.stream_url)
    else:
        log.info("Using direct video capture for local source.")
        cap = cv2.VideoCapture(config.stream_url)

    # Initialize tracker based on configuration
    tracker = CentroidTracker(max_disappeared=50, max_distance=50,
                              composite_threshold=0.7, composite_frames=10)

    # Loop over the frames from the video stream
    while True:
        if is_network_stream:
            frame = cap.read()
        else:
            ret, frame = cap.read()
            if not ret:
                break  # End of video file

        if frame is None:
            break

        if width is None or height is None:
            (height, width) = frame.shape[:2]
            log.info(f'{height=}, {width=}')
            width = 640
            height = 360

        # Resize frame for faster processing
        resized_frame = cv2.resize(frame, (640, 360))

        # Perform inference
        results = model(resized_frame, verbose=False)

        # Process results
        detections = []
        for result in results:
            boxes = result.boxes.cpu().numpy()
            for box in boxes:
                (x1, y1, x2, y2) = box.xyxy[0]
                conf = box.conf[0]
                cls = int(box.cls[0])
                detections.append([x1, y1, x2, y2, conf, cls])

        # Class IDs: 0 for person, 25 for umbrella
        person_detections = filter_detections(detections, target_class=0)
        umbrella_detections = []

        # Use full bounding boxes for tracking (includes IoU calculation)
        person_bboxes = [det[:4] for det in person_detections]
        umbrella_bboxes = [det[:4] for det in umbrella_detections]

        if config.enable_composite_objects:
            # Update composite objects first to claim their detections
            used_person_indices, used_umbrella_indices = tracker.update_composite_objects(person_bboxes, umbrella_bboxes)

            # Filter out detections that were used by composite objects
            remaining_person_bboxes = [bbox for i, bbox in enumerate(person_bboxes) if i not in used_person_indices]
            remaining_umbrella_bboxes = [bbox for i, bbox in enumerate(umbrella_bboxes) if i not in used_umbrella_indices]
        else:
            # No composite objects, use all detections
            remaining_person_bboxes = person_bboxes
            remaining_umbrella_bboxes = umbrella_bboxes

        # Update trackers with remaining detections
        filtered_persons = tracker.update(remaining_person_bboxes, obj_type="person")
        filtered_umbrellas = tracker.update(remaining_umbrella_bboxes, obj_type="umbrella")

        correlations = tracker.correlate_objects(config.angle_offset, config.distance_offset)

        # Handle composite object logic if enabled
        if config.enable_composite_objects:
            # Update stable correlations and create composite objects
            tracker.update_stable_correlations(correlations)
            
            # Check for composite dissolution
            tracker.check_composite_dissolution()
            
            # Get composite objects
            filtered_composites = tracker.filter_by_type("person-with-umbrella")
        else:
            filtered_composites = {}

        delta, total, total_down, total_up = handle_tracked_objects(config, delta, height, total, total_down, total_up,
                                                                    tracker.objects, config.coords_left_line, config.coords_right_line)

        info_status = [("Exit", total_up), ("Enter", total_down), ("Delta", delta)]

        # Draw results on the frame
        frame = draw_on_frame(resized_frame, filtered_persons, filtered_umbrellas, correlations,
                              width, height, info_status, config.coords_left_line, config.coords_right_line, filtered_composites)

        if config.enable_api and (time.time() - api_time) > config.api_interval:
            with ThreadPoolExecutor(max_workers=4) as executor:
                # Submit tasks to the executor
                executor.submit(post_api, config.api_url, config.device, total, total_down, total_up, delta)

            api_time = time.time()
            delta = 0

        total_frames += 1
        # Show the output frame
        cv2.imshow('AFF People Tracker', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == "__main__":
    main()
