"""
Tracker Management for People Counter Web UI
"""
import json
import os
import subprocess
import threading

from config.config import get_config
from helpers.logging_utils import get_tracker_debug_logger
from web_ui.models.video_streamer import VideoStreamer
from web_ui.utils.message_filters import (
    should_ignore_message, is_info_message, 
    is_rtsp_error, is_ffmpeg_error
)


class TrackerManager:
    """Manages tracker processes and configurations"""
    
    def __init__(self):
        self.processes = {}
        self.configs = {}
        self.stderr_threads = {}
        self.video_streamer = VideoStreamer()
        self.load_default_configs()

    def load_default_configs(self):
        """Load default configurations"""
        for config_id in [0, 1]:
            config = get_config(config_id)
            self.configs[config_id] = {
                'enable_api': config.enable_api,
                'api_url': config.api_url,
                'api_interval': config.api_interval,
                'device': config.device,
                'stream_url': config.stream_url,
                'coords_left_line': config.coords_left_line,
                'coords_right_line': config.coords_right_line,
                'angle_offset': config.angle_offset,
                'distance_offset': config.distance_offset,
                'debug_mode': False
            }

    def get_status(self, config_id):
        """Get status of a tracker"""
        if config_id in self.processes:
            if self.processes[config_id].poll() is None:
                return "Running"
            else:
                del self.processes[config_id]
                return "Stopped"
        return "Stopped"
    
    def get_test_videos(self):
        """Get list of available test videos"""
        test_dir = "test"
        if not os.path.exists(test_dir):
            return []
        
        video_extensions = ['.mp4', '.webm', '.avi', '.mov', '.mkv']
        test_videos = []
        
        for file in os.listdir(test_dir):
            if any(file.lower().endswith(ext) for ext in video_extensions):
                test_videos.append(f"{test_dir}/{file}")
        
        return sorted(test_videos)

    def _log_stderr_output(self, config_id, stderr_stream):
        """Process and filter stderr output from tracker processes"""
        debug_logger = get_tracker_debug_logger(config_id)
        for line in iter(stderr_stream.readline, b''):
            try:
                decoded_line = line.decode('utf-8').strip()
                if decoded_line:
                    # Filter and categorize different types of messages
                    if should_ignore_message(decoded_line):
                        continue  # Skip logging entirely
                    elif is_info_message(decoded_line):
                        debug_logger.log_info(f"Model Info: {decoded_line}")
                    elif is_rtsp_error(decoded_line):
                        debug_logger.log_error(f"RTSP Error: {decoded_line}")
                    elif is_ffmpeg_error(decoded_line):
                        debug_logger.log_error(f"FFmpeg Error: {decoded_line}")
                    else:
                        debug_logger.log_warning(f"System: {decoded_line}")
            except UnicodeDecodeError:
                debug_logger.log_error(f"System Error (undecodable): {line.hex()}")
            except ValueError:
                # This can happen if the stream is closed unexpectedly
                break
        stderr_stream.close()

    def start_tracker(self, config_id):
        """Start a specific tracker instance"""
        if config_id in self.processes and self.processes[config_id].poll() is None:
            return {"success": False, "message": f"Tracker {config_id} is already running"}
        
        try:
            # Create temporary config
            self.save_temp_config(config_id)
            
            # Start the process, redirecting stderr to a pipe
            process = subprocess.Popen([
                "python", "yolov8_video.py", "-i", str(config_id)
            ], cwd=os.getcwd(), stderr=subprocess.PIPE)
            
            self.processes[config_id] = process

            # Start a thread to read stderr
            stderr_thread = threading.Thread(
                target=self._log_stderr_output,
                args=(config_id, process.stderr)
            )
            stderr_thread.daemon = True
            stderr_thread.start()
            self.stderr_threads[config_id] = stderr_thread
            
            config = self.configs[config_id]
            mode_text = "debug mode" if config['debug_mode'] else "live mode"
            return {"success": True, "message": f"Tracker {config_id} started in {mode_text}!"}
            
        except Exception as e:
            return {"success": False, "message": f"Failed to start tracker {config_id}: {str(e)}"}

    def stop_tracker(self, config_id):
        """Stop a specific tracker instance"""
        if config_id in self.processes:
            try:
                self.processes[config_id].terminate()
                self.processes[config_id].wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.processes[config_id].kill()
            except:
                pass
            
            self.processes.pop(config_id, None)
            
            # Ensure stderr thread is cleaned up
            if config_id in self.stderr_threads:
                self.stderr_threads.pop(config_id, None)

            self.clear_debug_logs(config_id)  # Clear logs on stop
            return {"success": True, "message": f"Tracker {config_id} stopped and logs cleared"}
        
        return {"success": False, "message": f"Tracker {config_id} is not running"}
    
    def clear_debug_logs(self, config_id):
        """Clear debug logs for a specific tracker"""
        log_file = f"logs/tracker_{config_id}.json"
        if os.path.exists(log_file):
            try:
                os.remove(log_file)
                return {"success": True, "message": f"Debug logs cleared for tracker {config_id}"}
            except Exception as e:
                return {"success": False, "message": str(e)}
        return {"success": True, "message": "No log file to clear"}
    
    def save_temp_config(self, config_id, config_updated=False):
        """Save temporary config file"""
        config = self.configs[config_id].copy()
        
        # Remove debug_mode and test_video from the saved config since they're UI-only
        config.pop('test_video', None)
        
        # Add config_updated flag
        config['config_updated'] = config_updated
        
        # Save to temporary config file
        os.makedirs("config", exist_ok=True)
        config_file = f"config/temp_config_{config_id}.json"
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def update_config(self, config_id, new_config):
        """Update configuration and save to temp file"""
        self.configs[config_id].update(new_config)
        # Important: Save to temp file with flag so running tracker can detect the change
        self.save_temp_config(config_id, config_updated=True)
    
    def start_video_stream(self, config_id):
        """Start video stream for preview"""
        config = self.configs[config_id]
        stream_url = config['stream_url']
        return self.video_streamer.start_video_capture(config_id, stream_url)
    
    def stop_video_stream(self, config_id):
        """Stop video stream"""
        self.video_streamer.stop_video_capture(config_id)


# Global tracker manager instance
tracker_manager = TrackerManager()