# YOLOv8 People Counter - Clean Architecture

This module provides a clean, modular architecture for YOLOv8-based people counting with tracking and API integration.

## Architecture Overview

```
yolov8/
├── __init__.py                     # Main module exports
├── core/                          # Core processing logic
│   ├── __init__.py
│   └── processor.py               # Main video processor orchestrator
├── detection/                     # YOLO detection components
│   ├── __init__.py
│   └── detector.py               # YOLOv8 detector wrapper
├── video/                        # Video stream management
│   ├── __init__.py
│   └── stream_manager.py         # Stream handling for different sources
├── api/                          # API client components
│   ├── __init__.py
│   └── client.py                 # API client for posting data
├── tracking/                     # YOLOv8-specific tracking integration
│   ├── __init__.py
│   ├── manager.py                # Main tracking orchestrator
│   ├── counter.py                # People counting logic
│   └── filters.py                # Detection filtering utilities
├── visualization/                # Rendering and drawing components
│   ├── __init__.py
│   ├── renderer.py               # Frame rendering with tracking results
│   └── config.py                 # Visualization configuration
└── README.md                     # This file

## Shared Components

Core tracking and utility components are now located in the `shared/` folder:

```
shared/
├── tracking/                     # Core tracking algorithms
│   └── centroid_tracker.py      # Main tracking implementation
├── utils/                        # Shared utilities
│   ├── geometry.py               # Math/geometry functions
│   └── threading.py              # Threading utilities
└── logging/                      # Shared logging
    └── utils.py                  # Logging utilities
```

## Key Components

### Core Components

- **VideoProcessor**: Main orchestrator that coordinates all components
- **YOLODetector**: Handles YOLO model loading and inference
- **StreamManager**: Manages video input from various sources (files, RTSP, cameras)
- **APIClient**: Handles posting tracking data to external APIs

### Tracking Components

- **TrackingManager**: Coordinates detection filtering, object tracking, and counting
- **PeopleCounter**: Implements counting logic based on object movements
- **DetectionFilter**: Provides filtering utilities for raw detections

### Visualization Components

- **FrameRenderer**: Renders detection and tracking results on video frames
- **VisualizationConfig**: Configuration for colors, sizes, and rendering options

## Usage

### New Clean Architecture (Recommended)

```python
from yolov8.core.processor import VideoProcessor

# Initialize and run processor
processor = VideoProcessor(config_id=0)
processor.run()
```

Or use the command line:

```bash
python yolov8_main.py -i 0 --model yolov8m.pt --verbose
```

### Legacy Compatibility

The old `yolov8_video.py` entry point is still available for backward compatibility:

```bash
python yolov8_video.py -i 0
```

## Benefits of Clean Architecture

1. **Separation of Concerns**: Each component has a single responsibility
2. **Testability**: Components can be tested in isolation
3. **Maintainability**: Easier to modify and extend individual components
4. **Reusability**: Components can be reused in different contexts
5. **Configuration**: Centralized configuration management
6. **Error Handling**: Better error isolation and handling

## Component Details

### Detection Pipeline

1. **YOLODetector** performs inference on video frames
2. **DetectionFilter** filters results by class, confidence, area, etc.
3. **TrackingManager** coordinates the tracking pipeline

### Tracking Pipeline

1. Filter detections by class (person, umbrella)
2. Handle composite objects (person-with-umbrella) if enabled
3. Update centroid tracker with remaining detections
4. Correlate persons and umbrellas based on proximity and angle
5. Update counting logic based on object movements

### Visualization Pipeline

1. **FrameRenderer** draws tracking lines and boundaries
2. Renders object centroids with IDs
3. Shows correlations between objects
4. Displays information panel with statistics

## Configuration

The system uses the existing configuration system from `config/config.py`. All components accept and respect configuration updates through the `update_config()` method.

## Migration Guide

To migrate from the old architecture:

1. Replace `yolov8_video.py` calls with `yolov8_main.py`
2. Use individual components directly for custom implementations
3. Extend components by inheriting from base classes
4. Configure visualization through `VisualizationConfig`

## Extension Points

- Add new detection models by extending `YOLODetector`
- Implement custom counting logic by extending `PeopleCounter`
- Add new visualization elements through `FrameRenderer`
- Create custom API clients by extending `APIClient`