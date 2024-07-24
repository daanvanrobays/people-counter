import torch
import cv2
import logging
import time

from config.config import get_config
from drawing.frame_drawer import draw_on_frame
from tracking.centroid_tracker import CentroidTracker
from tracking.tracker import filter_detections, correlate_objects, handle_tracked_objects
from api.api import post_api

logging.basicConfig(level=logging.INFO, format="[INFO] %(message)s")
log = logging.getLogger(__name__)


def load_model():
    """Load the YOLOv7 model with GPU support if available."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    log.info(f'cuda={torch.cuda.is_available()}: {device}')
    return torch.hub.load('WongKinYiu/yolov7', 'custom', 'yolov7.pt', source='github').to(device), device


def main():
    config = get_config()

    api_time = time.time() if config.enable_api else None
    correlation_angle = config.correlation_angle
    correlation_distance = config.correlation_distance

    width, height = None, None
    trackable_objects = {}
    # total_frames = 1
    total_down = 0
    total_up = 0
    delta = 0
    total = 0

    # Load model and classes
    model, device = load_model()

    # Initialize the video stream
    # cap = cv2.VideoCapture('test/umbrella-2.mp4')
    cap = cv2.VideoCapture(config.stream_url)

    # Initialize CentroidTracker
    person_tracker = CentroidTracker(max_disappeared=50, max_distance=50)
    umbrella_tracker = CentroidTracker(max_disappeared=50, max_distance=50)

    # Loop over the frames from the video stream
    while True:
        ret, frame = cap.read()
        if not ret:
            break

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
        # log.info(detections)

        # Class IDs: 0 for person, 25 for umbrella
        person_detections = filter_detections(detections, target_class=0)
        umbrella_detections = filter_detections(detections, target_class=25)

        # Convert bounding boxes to centroids
        person_centroids = [det[:4] for det in person_detections]
        umbrella_centroids = [det[:4] for det in umbrella_detections]

        # Update trackers
        tracked_persons = person_tracker.update(person_centroids)
        tracked_umbrellas = umbrella_tracker.update(umbrella_centroids)

        # Correlate persons with umbrellas
        correlations = correlate_objects(tracked_persons, tracked_umbrellas, correlation_angle, correlation_distance)

        # Persons
        delta, total, total_down, total_up = handle_tracked_objects(delta, height, total, total_down, total_up,
                                                                    trackable_objects, tracked_persons)

        # Umbrellas
        # delta, total, total_down, total_up = handle_tracked_objects(delta, height, total, total_down, total_up,
        #                                                             trackable_objects, tracked_umbrellas)

        info_status = [("Exit", total_up), ("Enter", total_down), ("Delta", delta)]
        info_total = [("Total people inside", total)]

        # Draw results on the frame
        frame = draw_on_frame(resized_frame, tracked_persons, tracked_umbrellas, correlations, width, height,
                              info_status, info_total)

        if config.enable_api and (time.time() - api_time) > config.api_interval:
            try:
                post_api(config.api_url, config.device, total, total_down, total_up, delta)
                api_time = time.time()
            except Exception as ex:
                log.error(repr(ex))
            finally:
                delta = 0

        # total_frames += 1
        # Show the output frame
        cv2.imshow('AFF People Tracker', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == "__main__":
    main()
