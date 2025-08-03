"""Main video processing orchestrator."""

import cv2
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, Optional

from ..detection.detector import YOLODetector
from ..video.stream_manager import StreamManager
from ..api.client import APIClient
from ..tracking.manager import TrackingManager
from ..visualization.renderer import FrameRenderer
from config.config import Config, get_config

log = logging.getLogger(__name__)


class VideoProcessor:
    """Main video processing class that orchestrates detection, tracking, and API reporting."""
    
    def __init__(self, config_id: int):
        """Initialize the video processor with configuration."""
        self.config_id = config_id
        self.config = get_config(config_id)
        self.last_config_check = time.time()
        
        # Initialize components
        self.detector = YOLODetector(model_path=self.config.yolo_model)
        self.stream_manager = StreamManager(self.config.stream_url)
        self.api_client = APIClient(self.config) if self.config.enable_api else None
        self.tracking_manager = TrackingManager(self.config)
        self.renderer = FrameRenderer()
        
        # Processing state
        self.width: Optional[int] = None
        self.height: Optional[int] = None
        self.total_frames = 1
        self.api_time = time.time() if self.config.enable_api else None
    
    def check_config_update(self) -> None:
        """Check for configuration updates and reload if needed."""
        current_time = time.time()
        if current_time - self.last_config_check > 0.5:
            updated_config = self._load_updated_config()
            if updated_config:
                old_model = self.config.yolo_model
                self.config = updated_config
                
                # Update API client
                if self.api_client:
                    self.api_client.update_config(self.config)
                
                # Update tracking manager
                self.tracking_manager.update_config(self.config)
                
                # Switch model if changed
                if old_model != self.config.yolo_model:
                    if self.detector.switch_model(self.config.yolo_model):
                        log.info(f"Switched YOLO model from {old_model} to {self.config.yolo_model}")
                    else:
                        log.warning(f"Failed to switch model to {self.config.yolo_model}, keeping {old_model}")
                
                log.info("Configuration reloaded")
            self.last_config_check = current_time
    
    def _load_updated_config(self) -> Optional[Config]:
        """Load updated configuration from temp file."""
        import json
        import os
        
        temp_config_file = f"config/temp_config_{self.config_id}.json"
        
        try:
            if os.path.exists(temp_config_file):
                with open(temp_config_file, 'r') as f:
                    config_data = json.load(f)
                
                if config_data.get('config_updated', False):
                    log.info("Config file updated, reloading configuration...")
                    new_config = get_config(self.config_id)
                    
                    # Clear the flag
                    config_data['config_updated'] = False
                    with open(temp_config_file, 'w') as f:
                        json.dump(config_data, f, indent=2)
                    
                    return new_config
        except Exception as e:
            log.warning(f"Error checking config update: {e}")
        
        return None
    
    def initialize_frame_dimensions(self, frame) -> None:
        """Initialize frame dimensions for processing."""
        if self.width is None or self.height is None:
            (self.height, self.width) = frame.shape[:2]
            log.info(f'Frame dimensions: {self.height=}, {self.width=}')
            self.width = 640
            self.height = 360
    
    def process_frame(self, frame) -> Tuple[any, bool]:
        """Process a single frame through the detection and tracking pipeline."""
        self.initialize_frame_dimensions(frame)
        
        # Resize frame for faster processing
        resized_frame = cv2.resize(frame, (640, 360))
        
        # Perform detection
        detections = self.detector.detect(resized_frame)
        
        # Process detections through tracking pipeline
        (filtered_persons, filtered_umbrellas, correlations, 
         filtered_composites, count_stats) = self.tracking_manager.process_detections(
            detections, self.height
        )
        
        # Unpack count statistics
        delta, total, total_down, total_up = count_stats
        
        # Prepare status info
        info_status = [("Exit", total_up), ("Enter", total_down), ("Delta", delta)]
        
        # Render results on frame
        processed_frame = self.renderer.render_frame(
            resized_frame, filtered_persons, filtered_umbrellas, correlations,
            self.width, self.height, info_status, 
            self.config.coords_left_line, self.config.coords_right_line, 
            filtered_composites
        )
        
        # Handle API reporting
        self._handle_api_reporting(total, total_down, total_up, delta)
        
        self.total_frames += 1
        return processed_frame, True
    
    def _handle_api_reporting(self, total: int, total_down: int, total_up: int, delta: int) -> None:
        """Handle API reporting if enabled and interval has passed."""
        if self.api_client and self.api_time and (time.time() - self.api_time) > self.config.api_interval:
            with ThreadPoolExecutor(max_workers=4) as executor:
                executor.submit(
                    self.api_client.post_data,
                    total, total_down, total_up, delta
                )
            self.api_time = time.time()
    
    def run(self) -> None:
        """Main processing loop."""
        log.info("Starting video processing...")
        
        try:
            while True:
                # Check for config updates
                self.check_config_update()
                
                # Get next frame
                frame = self.stream_manager.get_frame()
                if frame is None:
                    break
                
                # Process frame
                processed_frame, should_continue = self.process_frame(frame)
                if not should_continue:
                    break
                
                # Display frame
                cv2.imshow('AFF People Tracker', processed_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            log.info("Processing interrupted by user")
        except Exception as e:
            log.error(f"Error during processing: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self.stream_manager:
            self.stream_manager.cleanup()
        cv2.destroyAllWindows()
        log.info("Video processing stopped")