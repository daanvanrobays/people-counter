"""
Video Streaming Management for People Counter Web UI
"""
import threading
import time
import cv2
import numpy as np


class VideoStreamer:
    """Manages video capture and streaming for multiple tracker configurations"""
    
    def __init__(self):
        self.video_captures = {}
        self.frame_buffers = {}
        self.fps_counters = {}
        self.stream_health = {}
        self.capture_threads = {}
        self.stop_flags = {}
        
    def start_video_capture(self, config_id, stream_url):
        """Start video capture for a specific config"""
        if config_id in self.video_captures:
            self.stop_video_capture(config_id)
            
        try:
            print(f"Starting video capture for config {config_id} with URL: {stream_url}")
            
            # Handle different video sources
            video_path = stream_url  # Default
            if stream_url.startswith('test/'):
                # Test video file with full path
                video_path = stream_url
            elif stream_url.endswith(('.mp4', '.webm', '.avi', '.mov', '.mkv')):
                # Video file, check if it needs test/ prefix
                if not stream_url.startswith('test/') and not stream_url.startswith('/'):
                    # Assume it's a test video file
                    video_path = f"test/{stream_url}"
                else:
                    video_path = stream_url
            elif stream_url.startswith('rtsp://'):
                # RTSP stream
                video_path = stream_url
            
            print(f"Attempting to open video path: {video_path}")
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                error_msg = f"Failed to open stream: {stream_url} (tried path: {video_path})"
                print(error_msg)
                self.stream_health[config_id] = {"status": "error", "message": error_msg}
                return False
                
            # Set buffer size to reduce latency (only for live streams)
            if not video_path.startswith('test/'):
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            self.video_captures[config_id] = cap
            self.frame_buffers[config_id] = None
            self.fps_counters[config_id] = {"count": 0, "start_time": time.time(), "fps": 0.0}
            self.stream_health[config_id] = {"status": "healthy", "message": "Stream active"}
            self.stop_flags[config_id] = False
            
            # Start capture thread
            thread = threading.Thread(target=self._capture_frames, args=(config_id,))
            thread.daemon = True
            thread.start()
            self.capture_threads[config_id] = thread
            
            print(f"Video capture started successfully for config {config_id}")
            return True
        except Exception as e:
            error_msg = f"Exception starting video capture: {str(e)}"
            print(error_msg)
            self.stream_health[config_id] = {"status": "error", "message": error_msg}
            return False
    
    def stop_video_capture(self, config_id):
        """Stop video capture for a specific config"""
        # Set stop flag first to signal the thread to stop
        self.stop_flags[config_id] = True
        
        if config_id in self.video_captures:
            cap = self.video_captures.pop(config_id)
            cap.release()
            
        self.frame_buffers.pop(config_id, None)
        self.fps_counters.pop(config_id, None)
        self.stream_health.pop(config_id, None)
        self.capture_threads.pop(config_id, None)
        self.stop_flags.pop(config_id, None)
    
    def _capture_frames(self, config_id):
        """Continuously capture frames in a separate thread"""
        cap = self.video_captures.get(config_id)
        if not cap:
            return
            
        fps_counter = self.fps_counters[config_id]
        consecutive_failures = 0
        max_failures = 30  # Allow 30 consecutive failures before giving up
        
        # Get video properties
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        is_video_file = frame_count > 0
        
        # Set target FPS (limit to reasonable values)
        if is_video_file and video_fps > 0:
            target_fps = min(video_fps, 30.0)  # Cap at 30 FPS
        else:
            target_fps = 25.0  # Default for RTSP streams
            
        frame_delay = 1.0 / target_fps if target_fps > 0 else 0.04  # ~25 FPS fallback
        
        print(f"Config {config_id}: Video FPS={video_fps}, Target FPS={target_fps}, Frame count={frame_count}")
        
        while config_id in self.video_captures and not self.stop_flags.get(config_id, False):
            # Check stop flag again at the beginning of each iteration
            if self.stop_flags.get(config_id, False):
                break
                
            frame_start_time = time.time()
            
            try:
                ret, frame = cap.read()
                if ret:
                    consecutive_failures = 0  # Reset failure counter
                    
                    # Update FPS counter
                    fps_counter["count"] += 1
                    current_time = time.time()
                    if current_time - fps_counter["start_time"] >= 1.0:
                        fps_counter["fps"] = fps_counter["count"] / (current_time - fps_counter["start_time"])
                        fps_counter["count"] = 0
                        fps_counter["start_time"] = current_time
                    
                    # Store latest frame
                    self.frame_buffers[config_id] = frame.copy()
                    self.stream_health[config_id] = {"status": "healthy", "message": "Stream active"}
                    
                else:
                    consecutive_failures += 1
                    
                    # For video files, try to loop back to the beginning (if not stopped)
                    if is_video_file and not self.stop_flags.get(config_id, False):
                        current_pos = cap.get(cv2.CAP_PROP_POS_FRAMES)
                        if current_pos >= frame_count - 1:  # Near or at end
                            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to beginning
                            print(f"Looping video file for config {config_id} (was at frame {current_pos}/{frame_count})")
                            consecutive_failures = 0  # Reset failures on successful loop
                            continue
                    
                    if consecutive_failures >= max_failures:
                        self.stream_health[config_id] = {"status": "error", "message": "Too many consecutive frame read failures"}
                        print(f"Stopping capture for config {config_id} due to too many failures")
                        break
                    else:
                        self.stream_health[config_id] = {"status": "error", "message": f"Failed to read frame (attempt {consecutive_failures}/{max_failures})"}
                        time.sleep(0.1)  # Brief pause before retry
                        continue
                        
            except Exception as e:
                consecutive_failures += 1
                error_msg = f"Exception in frame capture: {str(e)}"
                print(error_msg)
                self.stream_health[config_id] = {"status": "error", "message": error_msg}
                if consecutive_failures >= max_failures:
                    break
                time.sleep(0.1)
                continue
            
            # Frame rate limiting
            frame_process_time = time.time() - frame_start_time
            sleep_time = frame_delay - frame_process_time
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def get_frame(self, config_id):
        """Get the latest frame for a config"""
        return self.frame_buffers.get(config_id)
    
    def get_fps(self, config_id):
        """Get current FPS for a config"""
        fps_counter = self.fps_counters.get(config_id, {})
        return fps_counter.get("fps", 0.0)
    
    def get_stream_health(self, config_id):
        """Get stream health status"""
        return self.stream_health.get(config_id, {"status": "inactive", "message": "Stream not started"})