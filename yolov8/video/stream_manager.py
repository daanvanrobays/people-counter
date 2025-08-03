"""Video stream management for different input sources."""

import cv2
import logging
from typing import Optional, Union
from shared.utils.threading import ThreadingClass

log = logging.getLogger(__name__)


class StreamManager:
    """Manages video input streams from various sources."""
    
    def __init__(self, stream_url: Union[str, int]):
        """Initialize the stream manager.
        
        Args:
            stream_url: Video source (file path, RTSP URL, or camera index)
        """
        self.stream_url = stream_url
        self.is_network_stream = self._is_network_stream(stream_url)
        self.cap = None
        self._initialize_stream()
    
    def _is_network_stream(self, stream_url: Union[str, int]) -> bool:
        """Determine if the stream is a network source.
        
        Args:
            stream_url: Video source URL or path
            
        Returns:
            True if it's a network stream, False otherwise
        """
        if isinstance(stream_url, int):
            return False
        
        return (isinstance(stream_url, str) and 
                (stream_url.startswith("rtsp://") or
                 stream_url.startswith("http://") or
                 stream_url.startswith("https://")))
    
    def _initialize_stream(self) -> None:
        """Initialize the video stream based on the source type."""
        try:
            if self.is_network_stream:
                log.info(f"Initializing threaded video stream for: {self.stream_url}")
                self.cap = ThreadingClass(self.stream_url)
            else:
                log.info(f"Initializing direct video capture for: {self.stream_url}")
                self.cap = cv2.VideoCapture(self.stream_url)
                
                # Verify the stream is opened for local sources
                if not self.cap.isOpened():
                    raise RuntimeError(f"Failed to open video source: {self.stream_url}")
                    
        except Exception as e:
            log.error(f"Failed to initialize stream {self.stream_url}: {e}")
            raise
    
    def get_frame(self) -> Optional[any]:
        """Get the next frame from the video stream.
        
        Returns:
            Frame data if available, None if stream ended or failed
        """
        if self.cap is None:
            log.error("Stream not initialized")
            return None
        
        try:
            if self.is_network_stream:
                # Threaded stream returns frame directly
                frame = self.cap.read()
                return frame
            else:
                # Standard OpenCV capture returns (success, frame)
                ret, frame = self.cap.read()
                if not ret:
                    log.info("End of video stream reached")
                    return None
                return frame
                
        except Exception as e:
            log.error(f"Error reading frame: {e}")
            return None
    
    def get_stream_info(self) -> dict:
        """Get information about the current stream.
        
        Returns:
            Dictionary with stream information
        """
        info = {
            "stream_url": self.stream_url,
            "is_network_stream": self.is_network_stream,
            "is_opened": False,
            "fps": None,
            "frame_width": None,
            "frame_height": None,
            "frame_count": None
        }
        
        if self.cap is None:
            return info
        
        try:
            if self.is_network_stream:
                # Threaded streams don't provide detailed properties
                info["is_opened"] = True
            else:
                info["is_opened"] = self.cap.isOpened()
                if info["is_opened"]:
                    info["fps"] = self.cap.get(cv2.CAP_PROP_FPS)
                    info["frame_width"] = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    info["frame_height"] = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    info["frame_count"] = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    
        except Exception as e:
            log.warning(f"Error getting stream info: {e}")
        
        return info
    
    def seek_frame(self, frame_number: int) -> bool:
        """Seek to a specific frame (only for local video files).
        
        Args:
            frame_number: Frame number to seek to
            
        Returns:
            True if seek was successful, False otherwise
        """
        if self.is_network_stream or self.cap is None:
            log.warning("Seeking not supported for network streams")
            return False
        
        try:
            success = self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            if success:
                log.info(f"Seeked to frame {frame_number}")
            return success
        except Exception as e:
            log.error(f"Error seeking to frame {frame_number}: {e}")
            return False
    
    def restart_stream(self) -> bool:
        """Restart the video stream.
        
        Returns:
            True if restart was successful, False otherwise
        """
        try:
            log.info("Restarting video stream...")
            self.cleanup()
            self._initialize_stream()
            return True
        except Exception as e:
            log.error(f"Failed to restart stream: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up the video stream resources."""
        if self.cap is not None:
            try:
                if hasattr(self.cap, 'stop'):
                    # Threaded stream cleanup
                    self.cap.stop()
                else:
                    # Standard OpenCV cleanup
                    self.cap.release()
                log.info("Video stream cleaned up")
            except Exception as e:
                log.warning(f"Error during stream cleanup: {e}")
            finally:
                self.cap = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()