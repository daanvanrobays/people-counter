"""Detection filtering utilities."""

from typing import List, Tuple


class DetectionFilter:
    """Filters and processes detection results."""
    
    @staticmethod
    def filter_by_class(detections: List[List[float]], 
                       target_class: int, 
                       confidence_threshold: float = 0.4) -> List[Tuple[int, int, int, int]]:
        """Filter detections by class and confidence.
        
        Args:
            detections: List of detections [x1, y1, x2, y2, conf, class_id]
            target_class: Target class ID to filter for
            confidence_threshold: Minimum confidence threshold
            
        Returns:
            List of filtered bounding boxes as (x1, y1, x2, y2) tuples
        """
        filtered_detections = []
        
        for detection in detections:
            if len(detection) < 6:
                continue
                
            x1, y1, x2, y2, confidence, class_id = detection
            
            if int(class_id) == target_class and confidence >= confidence_threshold:
                bbox = tuple(map(int, [x1, y1, x2, y2]))
                filtered_detections.append(bbox)
        
        return filtered_detections
    
    @staticmethod
    def filter_by_area(detections: List[Tuple[int, int, int, int]], 
                      min_area: int = 100, 
                      max_area: int = 50000) -> List[Tuple[int, int, int, int]]:
        """Filter detections by bounding box area.
        
        Args:
            detections: List of bounding boxes (x1, y1, x2, y2)
            min_area: Minimum area threshold
            max_area: Maximum area threshold
            
        Returns:
            List of filtered bounding boxes
        """
        filtered_detections = []
        
        for bbox in detections:
            x1, y1, x2, y2 = bbox
            area = (x2 - x1) * (y2 - y1)
            
            if min_area <= area <= max_area:
                filtered_detections.append(bbox)
        
        return filtered_detections
    
    @staticmethod
    def filter_by_aspect_ratio(detections: List[Tuple[int, int, int, int]], 
                              min_ratio: float = 0.2, 
                              max_ratio: float = 5.0) -> List[Tuple[int, int, int, int]]:
        """Filter detections by aspect ratio.
        
        Args:
            detections: List of bounding boxes (x1, y1, x2, y2)
            min_ratio: Minimum aspect ratio (width/height)
            max_ratio: Maximum aspect ratio (width/height)
            
        Returns:
            List of filtered bounding boxes
        """
        filtered_detections = []
        
        for bbox in detections:
            x1, y1, x2, y2 = bbox
            width = x2 - x1
            height = y2 - y1
            
            if height > 0:  # Avoid division by zero
                aspect_ratio = width / height
                if min_ratio <= aspect_ratio <= max_ratio:
                    filtered_detections.append(bbox)
        
        return filtered_detections
    
    @staticmethod
    def apply_nms(detections: List[List[float]], 
                  iou_threshold: float = 0.4) -> List[List[float]]:
        """Apply Non-Maximum Suppression to detections.
        
        Args:
            detections: List of detections [x1, y1, x2, y2, conf, class_id]
            iou_threshold: IoU threshold for NMS
            
        Returns:
            List of filtered detections after NMS
        """
        if not detections:
            return []
        
        # Sort by confidence (descending)
        detections = sorted(detections, key=lambda x: x[4], reverse=True)
        
        keep = []
        while detections:
            # Keep the detection with highest confidence
            current = detections.pop(0)
            keep.append(current)
            
            # Remove detections with high overlap
            remaining = []
            for detection in detections:
                iou = DetectionFilter._calculate_iou(current[:4], detection[:4])
                if iou < iou_threshold:
                    remaining.append(detection)
            
            detections = remaining
        
        return keep
    
    @staticmethod
    def _calculate_iou(box1: List[float], box2: List[float]) -> float:
        """Calculate Intersection over Union (IoU) between two boxes.
        
        Args:
            box1: First bounding box [x1, y1, x2, y2]
            box2: Second bounding box [x1, y1, x2, y2]
            
        Returns:
            IoU value between 0 and 1
        """
        # Calculate intersection area
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        if x2 <= x1 or y2 <= y1:
            return 0.0
        
        intersection = (x2 - x1) * (y2 - y1)
        
        # Calculate union area
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0