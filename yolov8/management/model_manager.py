"""Model management for web UI integration."""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from ultralytics import YOLO

log = logging.getLogger(__name__)

# Model definitions
YOLO_MODELS = {
    "yolov8n.pt": {
        "name": "YOLOv8 Nano",
        "speed": "fastest",
        "accuracy": "lowest", 
        "size": "6MB",
        "description": "Best for real-time applications with limited resources",
        "recommended_for": ["Mobile devices", "Edge computing", "Real-time processing"]
    },
    "yolov8s.pt": {
        "name": "YOLOv8 Small",
        "speed": "very fast", 
        "accuracy": "low",
        "size": "22MB",
        "description": "Good balance for mobile/edge devices",
        "recommended_for": ["Embedded systems", "Fast processing", "Low memory devices"]
    },
    "yolov8m.pt": {
        "name": "YOLOv8 Medium",
        "speed": "fast",
        "accuracy": "medium", 
        "size": "52MB",
        "description": "Default model - good balance of speed and accuracy",
        "recommended_for": ["General purpose", "Balanced performance", "Production systems"]
    },
    "yolov8l.pt": {
        "name": "YOLOv8 Large", 
        "speed": "medium",
        "accuracy": "high",
        "size": "88MB", 
        "description": "Better accuracy for production systems",
        "recommended_for": ["High accuracy needs", "Server deployment", "Quality applications"]
    },
    "yolov8x.pt": {
        "name": "YOLOv8 Extra Large",
        "speed": "slow",
        "accuracy": "highest",
        "size": "137MB",
        "description": "Best accuracy, suitable for offline processing", 
        "recommended_for": ["Maximum accuracy", "Offline processing", "Research applications"]
    }
}


class ModelManager:
    """Manages YOLO models for the web interface."""
    
    def __init__(self):
        """Initialize the model manager."""
        self.models_info = YOLO_MODELS.copy()
    
    def get_available_models(self) -> Dict[str, Dict]:
        """Get all available models with their status.
        
        Returns:
            Dictionary with model info including download status
        """
        models = {}
        for model_file, info in self.models_info.items():
            models[model_file] = {
                **info,
                "downloaded": os.path.exists(model_file),
                "file_size": self._get_file_size(model_file) if os.path.exists(model_file) else None
            }
        return models
    
    def _get_file_size(self, file_path: str) -> str:
        """Get human readable file size."""
        try:
            size = os.path.getsize(file_path)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f}{unit}"
                size /= 1024.0
            return f"{size:.1f}TB"
        except OSError:
            return "Unknown"
    
    def download_model(self, model_name: str) -> Tuple[bool, str]:
        """Download a specific model.
        
        Args:
            model_name: Name of the model to download
            
        Returns:
            Tuple of (success, message)
        """
        if model_name not in self.models_info:
            return False, f"Unknown model: {model_name}"
        
        if os.path.exists(model_name):
            return True, f"Model {model_name} already exists"
        
        try:
            log.info(f"Downloading model: {model_name}")
            # This will automatically download the model
            model = YOLO(model_name)
            log.info(f"Successfully downloaded {model_name}")
            return True, f"Successfully downloaded {model_name}"
        except Exception as e:
            log.error(f"Failed to download {model_name}: {e}")
            return False, f"Failed to download {model_name}: {str(e)}"
    
    def delete_model(self, model_name: str) -> Tuple[bool, str]:
        """Delete a downloaded model.
        
        Args:
            model_name: Name of the model to delete
            
        Returns:
            Tuple of (success, message)
        """
        if model_name not in self.models_info:
            return False, f"Unknown model: {model_name}"
        
        if not os.path.exists(model_name):
            return False, f"Model {model_name} not found"
        
        try:
            os.remove(model_name)
            log.info(f"Deleted model: {model_name}")
            return True, f"Successfully deleted {model_name}"
        except Exception as e:
            log.error(f"Failed to delete {model_name}: {e}")
            return False, f"Failed to delete {model_name}: {str(e)}"
    
    def set_active_model(self, model_name: str, config_id: int = 0) -> Tuple[bool, str]:
        """Set the active model in configuration.
        
        Args:
            model_name: Name of the model to set as active
            config_id: Configuration ID
            
        Returns:
            Tuple of (success, message)
        """
        if model_name not in self.models_info:
            return False, f"Unknown model: {model_name}"
        
        if not os.path.exists(model_name):
            # Try to download it
            success, message = self.download_model(model_name)
            if not success:
                return False, f"Model not available and download failed: {message}"
        
        try:
            # Update the temp config file
            temp_config_file = f"config/temp_config_{config_id}.json"
            
            # Load existing config if it exists
            config_data = {}
            if os.path.exists(temp_config_file):
                with open(temp_config_file, 'r') as f:
                    config_data = json.load(f)
            
            # Update model and set update flag
            config_data['yolo_model'] = model_name
            config_data['config_updated'] = True
            
            # Save updated config
            os.makedirs(os.path.dirname(temp_config_file), exist_ok=True)
            with open(temp_config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            log.info(f"Set active model to {model_name} for config {config_id}")
            return True, f"Successfully set {model_name} as active model"
            
        except Exception as e:
            log.error(f"Failed to update configuration: {e}")
            return False, f"Failed to update configuration: {str(e)}"
    
    def get_current_model(self, config_id: int = 0) -> Optional[str]:
        """Get the currently configured model.
        
        Args:
            config_id: Configuration ID
            
        Returns:
            Current model name or None
        """
        try:
            from config.config import get_config
            config = get_config(config_id)
            return getattr(config, 'yolo_model', 'yolov8m.pt')
        except Exception as e:
            log.error(f"Failed to get current model: {e}")
            return None
    
    def test_model(self, model_name: str) -> Tuple[bool, Dict]:
        """Test a model's performance.
        
        Args:
            model_name: Name of the model to test
            
        Returns:
            Tuple of (success, performance_metrics)
        """
        if not os.path.exists(model_name):
            return False, {"error": f"Model {model_name} not found"}
        
        try:
            import time
            import numpy as np
            
            model = YOLO(model_name)
            
            # Create test image
            test_image = np.zeros((640, 640, 3), dtype=np.uint8)
            
            # Warm up
            model(test_image, verbose=False)
            
            # Performance test
            times = []
            for _ in range(5):  # Reduced for web UI
                start = time.time()
                results = model(test_image, verbose=False)
                end = time.time()
                times.append(end - start)
            
            avg_time = np.mean(times) * 1000  # Convert to ms
            fps = 1000 / avg_time
            
            metrics = {
                "avg_inference_time_ms": round(avg_time, 1),
                "estimated_fps": round(fps, 1),
                "min_time_ms": round(min(times) * 1000, 1),
                "max_time_ms": round(max(times) * 1000, 1),
                "model_info": self.models_info.get(model_name, {})
            }
            
            return True, metrics
            
        except Exception as e:
            log.error(f"Model test failed: {e}")
            return False, {"error": str(e)}
    
    def get_model_recommendations(self, use_case: str = "general") -> List[str]:
        """Get model recommendations based on use case.
        
        Args:
            use_case: Use case type (real_time, accuracy, balanced, mobile)
            
        Returns:
            List of recommended model names
        """
        recommendations = {
            "real_time": ["yolov8n.pt", "yolov8s.pt"],
            "accuracy": ["yolov8x.pt", "yolov8l.pt"],
            "balanced": ["yolov8m.pt", "yolov8l.pt"],
            "mobile": ["yolov8n.pt", "yolov8s.pt"],
            "general": ["yolov8m.pt", "yolov8s.pt", "yolov8l.pt"]
        }
        
        return recommendations.get(use_case, recommendations["general"])