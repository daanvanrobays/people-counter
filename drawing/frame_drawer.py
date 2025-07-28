import cv2
import numpy as np

# --- Configuration for Drawing ---
PERSON_COLOR = (0, 255, 0)       # Green
UMBRELLA_COLOR = (255, 0, 0)     # Blue
COMPOSITE_COLOR = (0, 255, 255)  # Yellow
CORRELATION_COLOR = (255, 255, 255) # White
INFO_PANEL_COLOR = (0, 0, 0)      # Black
TEXT_COLOR = (255, 255, 255)    # White


def _draw_tracked_object(frame, object_id, data, label, color):
    """Helper function to draw a single tracked object."""
    centroid = data["centroid"]
    # Draw a small dot at the centroid
    cv2.circle(frame, centroid, 3, color, -1)
    # Draw the object ID label
    cv2.putText(frame, f"{label}{object_id}", (centroid[0] + 10, centroid[1] + 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)


def _draw_info_panel(frame, width, height, info_status, info_total):
    """Draws a semi-transparent panel with tracking information."""
    panel_height = 100
    # Create a semi-transparent black rectangle
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, height - panel_height), (width, height), INFO_PANEL_COLOR, -1)
    alpha = 0.6  # Transparency factor
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # Display status information
    y_pos = height - panel_height + 30
    for key, value in info_status:
        text = f"{key}: {value}"
        cv2.putText(frame, text, (15, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, TEXT_COLOR, 2)
        y_pos += 30

    # Display total count
    total_text = f"{info_total[0][0]}: {info_total[0][1]}"
    cv2.putText(frame, total_text, (width - 250, height - 35), cv2.FONT_HERSHEY_SIMPLEX, 1, TEXT_COLOR, 2)


def draw_on_frame(resized_frame, tracked_persons, tracked_umbrellas, correlations, width, height, info_status,
                  info_total, coords_left, tracked_composites=None):
    """Main function to draw all visual elements onto the frame."""
    # Draw the tracking lines
    cv2.line(resized_frame, (0, height // 2), (width, height // 2), (0, 0, 255), 1)
    cv2.line(resized_frame, (coords_left, 0), (coords_left, height), (0, 0, 255), 1)

    # Draw correlations first, so they are in the background
    for person_id, _, umbrella_id, _ in correlations:
        if person_id in tracked_persons and umbrella_id in tracked_umbrellas:
            person_centroid = tracked_persons[person_id]["centroid"]
            umbrella_centroid = tracked_umbrellas[umbrella_id]["centroid"]
            cv2.line(resized_frame, person_centroid, umbrella_centroid, CORRELATION_COLOR, 1)

    # Draw tracked persons
    for obj_id, data in tracked_persons.items():
        _draw_tracked_object(resized_frame, obj_id, data, "P", PERSON_COLOR)

    # Draw tracked umbrellas
    for obj_id, data in tracked_umbrellas.items():
        _draw_tracked_object(resized_frame, obj_id, data, "U", UMBRELLA_COLOR)

    # Draw composite objects (person-with-umbrella)
    if tracked_composites:
        for obj_id, data in tracked_composites.items():
            _draw_tracked_object(resized_frame, obj_id, data, "C", COMPOSITE_COLOR)

    # Draw the information panel
    _draw_info_panel(resized_frame, width, height, info_status, info_total)

    return resized_frame