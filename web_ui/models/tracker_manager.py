"""
Tracker Management for People Counter Web UI
"""
import json
import os
import subprocess
import threading

from config.config import get_config
from shared.logging.utils import get_tracker_debug_logger
from web_ui.models.video_streamer import VideoStreamer
from web_ui.utils.message_filters import (
    should_ignore_message, is_info_message, 
    is_rtsp_error, is_ffmpeg_error
)
from detection.management.model_manager import ModelManager


class TrackerManager:
    """Manages tracker processes and configurations"""
    
    def __init__(self):
        self.processes = {}
        self.configs = {}
        self.stderr_threads = {}
        self.video_streamer = VideoStreamer()
        self.model_manager = ModelManager()
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
                'yolo_model': getattr(config, 'yolo_model', 'yolo11m.pt'),
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
                        debug_logger.log_info(f"Model: {decoded_line}")
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

    def _get_device_name(self, config_id):
        """Get device name from config or fallback to tracker ID"""
        config = self.configs.get(config_id, {})
        device_name = config.get('device', '').strip()
        return device_name if device_name else f"Tracker {config_id}"
    
    def start_tracker(self, config_id):
        """Start a specific tracker instance"""
        if config_id in self.processes and self.processes[config_id].poll() is None:
            device_name = self._get_device_name(config_id)
            return {"success": False, "message": f"{device_name} is already running"}
        
        try:
            # Create temporary config
            self.save_temp_config(config_id)
            
            # Get the YOLO model from config
            config = self.configs[config_id]
            yolo_model = config.get('yolo_model', 'yolo11m.pt')
            
            # Build command with model parameter
            cmd = [
                "python", "detection_main.py", 
                "-i", str(config_id),
                "--model", yolo_model
            ]
            
            # Add verbose flag if in debug mode
            if config.get('debug_mode', False):
                cmd.append("--verbose")
            
            # Start the process, redirecting stderr to a pipe
            process = subprocess.Popen(cmd, cwd=os.getcwd(), stderr=subprocess.PIPE)
            
            self.processes[config_id] = process

            # Start a thread to read stderr
            stderr_thread = threading.Thread(
                target=self._log_stderr_output,
                args=(config_id, process.stderr)
            )
            stderr_thread.daemon = True
            stderr_thread.start()
            self.stderr_threads[config_id] = stderr_thread
            
            mode_text = "debug mode" if config['debug_mode'] else "live mode"
            model_text = f"using {yolo_model}"
            device_name = self._get_device_name(config_id)
            return {"success": True, "message": f"{device_name} started in {mode_text} {model_text}!"}
            
        except Exception as e:
            device_name = self._get_device_name(config_id)
            return {"success": False, "message": f"Failed to start {device_name}: {str(e)}"}

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
            device_name = self._get_device_name(config_id)
            return {"success": True, "message": f"{device_name} stopped and logs cleared"}
        
        device_name = self._get_device_name(config_id)
        return {"success": False, "message": f"{device_name} is not running"}
    
    def clear_debug_logs(self, config_id):
        """Clear debug logs for a specific tracker"""
        log_file = f"logs/tracker_{config_id}.json"
        if os.path.exists(log_file):
            try:
                os.remove(log_file)
                device_name = self._get_device_name(config_id)
                return {"success": True, "message": f"Debug logs cleared for {device_name}"}
            except Exception as e:
                return {"success": False, "message": str(e)}
        return {"success": True, "message": "No log file to clear"}
    
    def save_temp_config(self, config_id, config_updated=False):
        """Save temporary config file"""
        config = self.configs[config_id].copy()
        
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
        device_name = self._get_device_name(config_id)
        return {"success": True, "message": f"Configuration updated for {device_name}"}
    
    def update_debug_logging(self, config_id, enable_debug_logging):
        """Update debug logging setting for a tracker"""
        self.configs[config_id]['enable_debug_logging'] = enable_debug_logging
        # Save to temp file so running tracker can detect the change
        self.save_temp_config(config_id, config_updated=True)
        device_name = self._get_device_name(config_id)
        status = "enabled" if enable_debug_logging else "disabled"
        return {"success": True, "message": f"Debug logging {status} for {device_name}"}
    
    # Model Management Methods
    def get_available_models(self):
        """Get all available YOLO models with their status"""
        return self.model_manager.get_available_models()
    
    def download_model(self, model_name):
        """Download a specific YOLO model"""
        return self.model_manager.download_model(model_name)
    
    def set_model_for_config(self, config_id, model_name):
        """Set the YOLO model for a specific configuration"""
        # Update the local config
        self.configs[config_id]['yolo_model'] = model_name
        
        # Save to temp config file with update flag
        self.save_temp_config(config_id, config_updated=True)
        
        # Also set as active model using model manager
        success, message = self.model_manager.set_active_model(model_name, config_id)
        
        if success:
            device_name = self._get_device_name(config_id)
            return {"success": True, "message": f"Model set to {model_name} for {device_name}"}
        else:
            return {"success": False, "message": message}
    
    def get_current_model(self, config_id):
        """Get the current YOLO model for a configuration"""
        return self.configs[config_id].get('yolo_model', 'yolo11m.pt')
    
    def test_model_performance(self, model_name):
        """Test the performance of a specific model"""
        return self.model_manager.test_model(model_name)
    
    def get_model_recommendations(self, use_case="general"):
        """Get model recommendations based on use case"""
        return self.model_manager.get_model_recommendations(use_case)


# Global tracker manager instance
tracker_manager = TrackerManager()