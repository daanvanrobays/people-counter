import cv2


def draw_boxes_model(frame, detections, classes, target_classes):
    """Draw bounding boxes on the frame."""
    for det in detections:
        x1, y1, x2, y2, conf, cls_id = det
        if int(cls_id) in target_classes:
            # label = f"{classes[int(cls_id)]} {conf:.2f}"
            color = (255, 255, 255)  # Green color for bounding box
            cv2.rectangle(frame, (int(x1)-5, int(y1)-5), (int(x2)-5, int(y2)-5), color, 2)
            # cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame


def draw_info(frame, width, height, info_status, info_total):
    cv2.line(frame, (0, height // 2), (width, height // 2), (0, 0, 255), 1)
    for (i, (k, v)) in enumerate(info_status):
        text = "{}: {}".format(k, v)
        cv2.putText(frame, text, (10, height - ((i * 20) + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    for (i, (k, v)) in enumerate(info_total):
        text = "{}: {}".format(k, v)
        cv2.putText(frame, text, (265, height - ((i * 20) + 60)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return frame


def draw_tracking_info(frame, object_id, centroid):
    text = f"ID {object_id}"
    cv2.putText(frame, text, (centroid[0], centroid[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 0, 0), -1)


def draw_boxes(frame, tracked_objects, label):
    """Draw bounding boxes and labels on the frame."""
    for obj_id, centroid in tracked_objects.items():
        color = (0, 255, 0) if label == "P" else (0, 0, 255)
        cv2.circle(frame, centroid, 5, color, -1)
        cv2.putText(frame, f"{label}{obj_id}", (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    color, 2)
    return frame


def draw_correlations(frame, correlations, tracked_persons, tracked_umbrellas):
    """Draw lines between correlated objects."""
    for person_id, umbrella_id in correlations:
        person_centroid = tracked_persons[person_id]
        umbrella_centroid = tracked_umbrellas[umbrella_id]
        cv2.line(frame, person_centroid, umbrella_centroid, (255, 0, 0), 2)
    return frame


def draw_on_frame(resized_frame, tracked_persons, tracked_umbrellas, correlations, width, height, info_status,
                  info_total):
    frame = draw_boxes(resized_frame, tracked_persons, "P")
    frame = draw_boxes(resized_frame, tracked_umbrellas, "U")
    frame = draw_correlations(resized_frame, correlations, tracked_persons, tracked_umbrellas)
    frame = draw_info(resized_frame, width, height, info_status, info_total)
    return frame
