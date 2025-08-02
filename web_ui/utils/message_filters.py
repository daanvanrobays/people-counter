"""
Message filtering utilities for logging
"""
import re


def should_ignore_message(message):
    """Check if message should be completely ignored"""
    ignore_patterns = [
        # YOLO model architecture info that's not useful in logs
        r'\[INFO\]\s+\d+\s+-?\d+\s+\d+\s+\d+\s+models\.common\.',
        # Torch/CUDA initialization messages that are too verbose
        r'Using torch \d+\.\d+\.\d+',
        r'Using cache found in',
    ]
    
    for pattern in ignore_patterns:
        if re.search(pattern, message):
            return True
    return False


def is_info_message(message):
    """Check if message is informational (model loading, etc.)"""
    info_patterns = [
        r'\[INFO\]',
        r'Model loaded',
        r'Loading.*model',
        r'Fusing layers',
        r'Model Summary',
    ]
    
    for pattern in info_patterns:
        if re.search(pattern, message, re.IGNORECASE):
            return True
    return False


def is_rtsp_error(message):
    """Check if message is RTSP-related error"""
    rtsp_patterns = [
        r'rtsp://',
        r'Connection refused',
        r'Network is unreachable',
        r'No route to host',
        r'timed? ?out',
        r'RTSP',
    ]
    
    for pattern in rtsp_patterns:
        if re.search(pattern, message, re.IGNORECASE):
            return True
    return False


def is_ffmpeg_error(message):
    """Check if message is FFmpeg-related error"""
    ffmpeg_patterns = [
        r'ffmpeg',
        r'av_',
        r'codec',
        r'Invalid data found',
        r'moov atom not found',
    ]
    
    for pattern in ffmpeg_patterns:
        if re.search(pattern, message, re.IGNORECASE):
            return True
    return False