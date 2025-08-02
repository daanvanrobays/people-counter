import argparse
from concurrent.futures import ThreadPoolExecutor

import torch
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

    # Load model and classes
    model, device = load_model()

    # Initialize the video stream
    cap = cv2.VideoCapture(config.stream_url)

    # Initialize CentroidTracker
    centroid_tracker = CentroidTracker(max_disappeared=50, max_distance=50)

    # Loop over the frames from the video stream
    while True:
        ret, frame = cap.read()

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
                                                                    centroid_tracker.objects, config.coords_left_line, config.coords_right_line)

        info_status = [("Exit", total_up), ("Enter", total_down), ("Delta", delta)]
        info_total = [("Total people inside", total)]

        # Draw results on the frame
        frame = draw_on_frame(resized_frame, filtered_persons, filtered_umbrellas, correlations,
                              width, height, info_status, info_total, config.coords_left_line, config.coords_right_line)

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
