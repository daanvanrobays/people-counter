import os
import json
from datetime import datetime

class DebugLogger:
    def __init__(self, config_id):
        self.config_id = config_id
        self.log_file = f"logs/tracker_{config_id}.json"
        self.max_logs = 500  # Keep last 500 log entries
        os.makedirs("logs", exist_ok=True)
        
    def log_event(self, level, message, data=None):
        """Log an event to the debug file"""
        try:
            # Read existing logs
            logs = []
            if os.path.exists(self.log_file):
                try:
                    with open(self.log_file, 'r') as f:
                        logs = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    logs = []
            
            # Add new log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": level,
                "message": message,
                "data": data or {}
            }
            logs.append(log_entry)
            
            # Keep only last max_logs entries
            if len(logs) > self.max_logs:
                logs = logs[-self.max_logs:]
            
            # Write back to file
            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            print(f"Failed to write debug log: {e}")
    
    def log_info(self, message, data=None):
        self.log_event("INFO", message, data)
    
    def log_warning(self, message, data=None):
        self.log_event("WARNING", message, data)
    
    def log_error(self, message, data=None):
        self.log_event("ERROR", message, data)

_debug_loggers = {}

def get_tracker_debug_logger(config_id: int) -> DebugLogger:
    if config_id not in _debug_loggers:
        _debug_loggers[config_id] = DebugLogger(config_id)
    return _debug_loggers[config_id]
