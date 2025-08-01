#!/usr/bin/env python3
import json
import os
import subprocess
import threading

from flask import Flask, render_template, request, jsonify, send_from_directory

from config.config import get_config
from helpers.logging_utils import get_tracker_debug_logger # Import get_tracker_debug_logger

app = Flask(__name__)

class TrackerManager:
    def __init__(self):
        self.processes = {}
        self.configs = {}
        self.stderr_threads = {}
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
                test_videos.append(file)
        
        return sorted(test_videos)

    def _log_stderr_output(self, config_id, stderr_stream):
        debug_logger = get_tracker_debug_logger(config_id)
        for line in iter(stderr_stream.readline, b''):
            try:
                decoded_line = line.decode('utf-8').strip()
                if decoded_line:
                    debug_logger.log_error(f"RTSP/FFmpeg Error: {decoded_line}")
            except UnicodeDecodeError:
                debug_logger.log_error(f"RTSP/FFmpeg Error (undecodable): {line.hex()}")
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
                "python", "yolov7_video.py", "-i", str(config_id)
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
                # The thread should exit when the pipe closes, but we can join it for good measure
                # A small timeout to avoid blocking indefinitely
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
    
    def save_temp_config(self, config_id):
        """Save temporary config file"""
        config = self.configs[config_id].copy()
        
        # Remove debug_mode and test_video from the saved config since they're UI-only
        config.pop('test_video', None)
        
        # Save to temporary config file
        os.makedirs("config", exist_ok=True)
        config_file = f"config/temp_config_{config_id}.json"
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def update_config(self, config_id, new_config):
        """Update configuration and save to temp file"""
        self.configs[config_id].update(new_config)
        # Important: Save to temp file so running tracker can detect the change
        self.save_temp_config(config_id)

# Global tracker manager
tracker_manager = TrackerManager()

@app.route('/')
def index():
    """Main dashboard"""
    statuses = {}
    for config_id in [0, 1]:
        statuses[config_id] = tracker_manager.get_status(config_id)
    
    return render_template('dashboard.html', 
                         configs=tracker_manager.configs,
                         statuses=statuses,
                         test_videos=tracker_manager.get_test_videos())

@app.route('/api/status')
def api_status():
    """Get status of all trackers"""
    statuses = {}
    for config_id in [0, 1]:
        statuses[config_id] = tracker_manager.get_status(config_id)
    return jsonify(statuses)

@app.route('/api/start/<int:config_id>')
def api_start(config_id):
    """Start a tracker"""
    result = tracker_manager.start_tracker(config_id)
    return jsonify(result)

@app.route('/api/stop/<int:config_id>')
def api_stop(config_id):
    """Stop a tracker"""
    result = tracker_manager.stop_tracker(config_id)
    return jsonify(result)

@app.route('/api/start_all')
def api_start_all():
    """Start all trackers"""
    results = []
    for config_id in [0, 1]:
        result = tracker_manager.start_tracker(config_id)
        results.append(f"Config {config_id}: {result['message']}")
    
    return jsonify({"success": True, "message": "; ".join(results)})

@app.route('/api/stop_all')
def api_stop_all():
    """Stop all trackers"""
    results = []
    for config_id in [0, 1]:
        result = tracker_manager.stop_tracker(config_id)
        results.append(f"Config {config_id}: {result['message']}")
    
    return jsonify({"success": True, "message": "; ".join(results)})

@app.route('/api/update_config/<int:config_id>', methods=['POST'])
def api_update_config(config_id):
    """Update configuration"""
    try:
        new_config = request.json
        tracker_manager.update_config(config_id, new_config)
        return jsonify({"success": True, "message": f"Config {config_id} updated"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/debug_logs/<int:config_id>')
def api_get_debug_logs(config_id):
    """Get debug logs for a tracker"""
    try:
        log_file = f"logs/tracker_{config_id}.json"
        if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
            with open(log_file, 'r') as f:
                logs = json.load(f)
            # Return only the last 50 logs for performance
            return jsonify({"success": True, "logs": logs[-50:]})
        else:
            return jsonify({"success": True, "logs": []})
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "logs": []})

@app.route('/api/debug_logs/<int:config_id>/clear', methods=['POST'])
def api_clear_debug_logs(config_id):
    """Clear debug logs for a tracker"""
    result = tracker_manager.clear_debug_logs(config_id)
    return jsonify(result)

@app.route('/back_25_d.png')
def background_image():
    """Serve the background image"""
    return send_from_directory('templates', 'back_25_d.png')

if __name__ == '__main__':
    print("Starting YOLOv7 Multi-Tracker Web UI...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)