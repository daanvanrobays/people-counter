"""
Video streaming routes for People Counter Web UI
"""
import time
import cv2
import numpy as np
from flask import Blueprint, Response, request, send_from_directory
from web_ui.models.tracker_manager import tracker_manager

video = Blueprint('video', __name__)


def generate_frames(config_id):
    """Generate video frames for streaming"""
    while True:
        try:
            frame = tracker_manager.video_streamer.get_frame(config_id)
            if frame is not None:
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                else:
                    # Fallback to black frame if encoding fails
                    yield _generate_black_frame()
            else:
                # Send a black frame if no video available
                yield _generate_black_frame()
        except Exception as e:
            print(f"Error in generate_frames for config {config_id}: {e}")
            yield _generate_black_frame()
        
        time.sleep(0.033)  # ~30 FPS


def _generate_black_frame():
    """Generate a black frame for streaming"""
    black_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Add text overlay to indicate no video
    cv2.putText(black_frame, 'No Video Feed', (240, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    ret, buffer = cv2.imencode('.jpg', black_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    if ret:
        frame_bytes = buffer.tobytes()
        return (b'--frame\r\n' 
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    return b''


@video.route('/video_feed/<int:config_id>')
def video_feed(config_id):
    """Video streaming route"""
    print(f"Video feed requested for config {config_id}")
    
    # Check if single frame is requested
    single_frame = request.args.get('single_frame', '0') == '1'
    
    if single_frame:
        # Return single JPEG frame
        frame = tracker_manager.video_streamer.get_frame(config_id)
        if frame is not None:
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ret:
                return Response(buffer.tobytes(), mimetype='image/jpeg')
        
        # Return black frame if no video available
        black_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(black_frame, 'No Video Feed', (240, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        ret, buffer = cv2.imencode('.jpg', black_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if ret:
            return Response(buffer.tobytes(), mimetype='image/jpeg')
        return "Error generating frame", 500
    else:
        # Return MJPEG stream (fallback)
        return Response(generate_frames(config_id),
                        mimetype='multipart/x-mixed-replace; boundary=frame')


@video.route('/back_25_d.png')
def background_image():
    """Serve the background image"""
    return send_from_directory('../web_ui/static', 'back_25_d.png')


@video.route('/test_image')
def test_image():
    """Test image endpoint for debugging"""
    print("Test image endpoint called")
    # Return a simple test image
    import numpy as np
    
    # Create a simple test image
    test_img = np.zeros((240, 320, 3), dtype=np.uint8)
    cv2.putText(test_img, 'TEST IMAGE', (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    ret, buffer = cv2.imencode('.jpg', test_img)
    if ret:
        return Response(buffer.tobytes(), mimetype='image/jpeg')
    return "Error generating test image", 500