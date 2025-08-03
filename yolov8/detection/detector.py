"""YOLOv8 detection module."""

import logging
from typing import List
from ultralytics import YOLO

log = logging.getLogger(__name__)


class YOLODetector:
    """YOLOv8 object detector for people and umbrella detection."""
    
    def __init__(self, model_path: str = "yolov8m.pt"):
        """Initialize the YOLO detector.
        
        Args:
            model_path: Path to the YOLO model file
        """
        self.model_path = model_path
        self.model = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the YOLOv8 model."""
        try:
            self.model = YOLO(self.model_path)
            log.info(f"Loaded YOLOv8 model: {self.model_path}")
        except Exception as e:
            log.error(f"Failed to load model {self.model_path}: {e}")
            raise
    
    def detect(self, frame, verbose: bool = False) -> List[List[float]]:
        """Perform object detection on a frame.
        
        Args:
            frame: Input frame for detection
            verbose: Whether to enable verbose output
            
        Returns:
            List of detections in format [x1, y1, x2, y2, confidence, class_id]
        """
        if self.model is None:
            log.error("Model not loaded")
            return []
        
        try:
            results = self.model(frame, verbose=verbose)
            return self._process_results(results)
        except Exception as e:
            log.error(f"Detection failed: {e}")
            return []
    
    def _process_results(self, results) -> List[List[float]]:
        """Process YOLO results into standardized format.
        
        Args:
            results: Raw YOLO results
            
        Returns:
            List of detections in format [x1, y1, x2, y2, confidence, class_id]
        """
        detections = []
        
        for result in results:
            if result.boxes is None:
                continue
                
            boxes = result.boxes.cpu().numpy()
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                
                detections.append([x1, y1, x2, y2, confidence, class_id])
        
        return detections
    
    def get_class_names(self) -> dict:
        """Get the class names mapping.
        
        Returns:
            Dictionary mapping class IDs to class names
        """
        if self.model is None:
            return {}
        return self.model.names
    
    def switch_model(self, model_path: str) -> bool:
        """Switch to a different YOLO model.
        
        Args:
            model_path: Path to the new model file
            
        Returns:
            True if model switch was successful, False otherwise
        """
        try:
            old_model_path = self.model_path
            self.model_path = model_path
            self._load_model()
            log.info(f"Switched from {old_model_path} to {model_path}")
            return True
        except Exception as e:
            log.error(f"Failed to switch model to {model_path}: {e}")
            # Restore previous model
            self.model_path = old_model_path
            self._load_model()
            return False
    
    def get_model_info(self) -> dict:
        """Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        if self.model is None:
            return {}
        
        return {
            "model_path": self.model_path,
            "task": getattr(self.model, 'task', 'unknown'),
            "device": str(getattr(self.model, 'device', 'unknown')),
            "class_count": len(self.get_class_names())
        }