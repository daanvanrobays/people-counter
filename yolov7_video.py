import argparse
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor

import cv2
import torch

from api.api import post_api
from config.config import get_config
from drawing.frame_drawer import draw_on_frame
from helpers.logging_utils import get_tracker_debug_logger
from helpers.thread import ThreadingClass
from tracking.centroid_tracker import CentroidTracker
from tracking.tracker import filter_detections, handle_tracked_objects

logging.basicConfig(level=logging.INFO, format="[INFO] %(message)s")
log = logging.getLogger(__name__)

def load_model():
    """Load the YOLOv7 model with GPU support if available."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    log.info(f'cuda={torch.cuda.is_available()}: {device}')
    return torch.hub.load('WongKinYiu/yolov7', 'custom', 'yolov7.pt', source='github').to(device), device


def parse_arguments():
    # function to parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", type=int, default=0,
                    help="config input")
    args = vars(ap.parse_args())
    return args


def check_config_update(config_id, last_modified_time):
    """Check if config file has been updated"""
    temp_config_file = f"config/temp_config_{config_id}.json"
    
    try:
        if os.path.exists(temp_config_file):
            current_modified_time = os.path.getmtime(temp_config_file)
            if current_modified_time > last_modified_time:
                log.info("Config file updated, reloading configuration...")
                new_config = get_config(config_id)
                return new_config, current_modified_time
    except Exception as e:
        log.warning(f"Error checking config update: {e}")
    
    return None, last_modified_time


def main():
    args = parse_arguments()
    config_id = args["input"]
    config = get_config(config_id)

    # Initialize debug logger
    debug_logger = get_tracker_debug_logger(config_id)
    debug_logger.stream_url = config.stream_url
    debug_logger.log_info(f"Tracker {config_id} starting", {
        "device": config.device,
        "stream_url": config.stream_url,
        "coords_left_line": config.coords_left_line
    })

    # Initialize config modification tracking
    temp_config_file = f"config/temp_config_{config_id}.json"
    last_config_check = time.time()
    config_modified_time = os.path.getmtime(temp_config_file) if os.path.exists(temp_config_file) else 0

    api_time = time.time() if config.enable_api else None

    width, height = None, None
    total_frames = 1
    total_down = 0
    total_up = 0
    delta = 0
    total = 0

    # Load model and classes
    debug_logger.log_info("Loading YOLOv7 model")
    model, device = load_model()
    debug_logger.log_info(f"Model loaded successfully on device: {device}")

    # Initialize the video stream based on the mode
    cap = None
    if config.debug_mode:
        debug_logger.log_info(f"Using local test video: {config.stream_url}")
        cap = cv2.VideoCapture(config.stream_url)
        if not cap.isOpened():
            debug_logger.log_error(f"Failed to open test video: {config.stream_url}")
            return
    else:
        debug_logger.log_info(f"Connecting to RTSP stream with threaded capture: {config.stream_url}")
        cap = ThreadingClass(config.stream_url, debug_logger)
        # Give the threaded capture a moment to initialize
        time.sleep(1)

    # Initialize CentroidTracker
    centroid_tracker = CentroidTracker(max_disappeared=50, max_distance=50)
    debug_logger.log_info("CentroidTracker initialized")

    # Loop over the frames from the video stream
    while True:
        # Check for config updates every 2 seconds
        current_time = time.time()
        if current_time - last_config_check > 2.0:
            updated_config, config_modified_time = check_config_update(config_id, config_modified_time)
            if updated_config:
                # NOTE: Stream URL changes are not applied mid-stream. Requires a restart.
                config = updated_config
                debug_logger.stream_url = config.stream_url
                debug_logger.log_info("Configuration reloaded", {
                    "coords_left_line": config.coords_left_line,
                    "angle_offset": config.angle_offset,
                    "distance_offset": config.distance_offset,
                })
            last_config_check = current_time

        # Read the next frame from the stream
        if config.debug_mode:
            ret, frame = cap.read()
        else:
            frame = cap.read()

        if width is None or height is None:
            (height, width) = frame.shape[:2]
            log.info(f'{height=}, {width=}')
            width = 640
            height = 360

        # Resize frame for faster processing
        resized_frame = cv2.resize(frame, (640, 360))

        # Perform inference
        # if total_frames % 2 == 0:
        #     flap = 'drol'
        # else:
        #     results = model(resized_frame, size=640)  # Specify size for faster inference
        results = model(resized_frame, size=640)  # Specify size for faster inference

        # Process results
        detections = results.xyxy[0].cpu().numpy()  # Move to CPU and convert to numpy array

        # Class IDs: 0 for person, 25 for umbrella
        person_detections = filter_detections(detections, target_class=0)
        umbrella_detections = filter_detections(detections, target_class=25)

        # Convert bounding boxes to centroids
        person_centroids = [det[:4] for det in person_detections]
        umbrella_centroids = [det[:4] for det in umbrella_detections]

        # Update trackers
        filtered_persons = centroid_tracker.update(person_centroids, obj_type="person")
        filtered_umbrellas = centroid_tracker.update(umbrella_centroids, obj_type="umbrella")

        correlations = centroid_tracker.correlate_objects(config.angle_offset, config.distance_offset)

        delta, total, total_down, total_up = handle_tracked_objects(delta, height, total, total_down, total_up,
                                                                    centroid_tracker.objects, config.coords_left_line, debug_logger)

        info_status = [("Exit", total_up), ("Enter", total_down), ("Delta", delta)]
        info_total = [("Total people inside", total)]

        # Draw results on the frame
        frame = draw_on_frame(resized_frame, filtered_persons, filtered_umbrellas, correlations,
                              width, height, info_status, info_total, config.coords_left_line)

        if config.enable_api and (time.time() - api_time) > config.api_interval:
            with ThreadPoolExecutor(max_workers=4) as executor:
                # Submit tasks to the executor
                executor.submit(post_api, config.api_url, config.device, total, total_down, total_up, delta)

            api_time = time.time()
            delta = 0

        total_frames += 1
        # Show the output frame
        cv2.imshow(f"{config.device}: AFF People Tracker", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == "__main__":
    main()
