import torch
import cv2
import yaml
import logging


log = logging.getLogger(__name__)


def load_model():
    """Load the YOLOv7 model with GPU support if available."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    log.info(f'cuda={torch.cuda.is_available()}: {device}')
    return torch.hub.load('WongKinYiu/yolov7', 'custom', 'yolov7.pt', source='github').to(device), device


def load_classes(yaml_path='data/coco.yaml'):
    """Load COCO class labels from the yaml file."""
    with open(yaml_path, 'r') as f:
        coco_config = yaml.safe_load(f)
    return coco_config['names']


def draw_boxes(frame, detections, classes, target_classes):
    """Draw bounding boxes on the frame."""
    for det in detections:
        x1, y1, x2, y2, conf, cls_id = det
        if int(cls_id) in target_classes:
            label = f"{classes[int(cls_id)]} {conf:.2f}"
            color = (0, 255, 0)  # Green color for bounding box
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame


def main():
    # Load model and classes
    model, device = load_model()
    classes = load_classes('data/coco.yaml')

    # Class IDs for person (0) and umbrella (25)
    target_classes = [0, 25]

    # Initialize the video stream
    cap = cv2.VideoCapture('test/umbrella-1.mp4')

    # Frame skip rate
    frame_skip = 5

    # Loop over the frames from the video stream
    frame_count = 0

    # Loop over the frames from the video stream
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Skip frames
        # frame_count += 1
        # if frame_count % frame_skip != 0:
        #     continue

        # Resize frame for faster processing
        resized_frame = cv2.resize(frame, (640, 480))

        # Perform inference
        results = model(resized_frame, size=640)  # Specify size for faster inference

        # Process results
        detections = results.xyxy[0].cpu().numpy()  # Move to CPU and convert to numpy array
        frame = draw_boxes(resized_frame, detections, classes, target_classes)

        # Show the output frame
        cv2.imshow('YOLOv7 Object Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
