# People Counter

Advanced real-time people counting system with clean modular architecture, featuring web-based management interface and intelligent model management, powered by YOLOv8 object detection.

## 🚀 What's New

### ✨ **Clean Architecture & Model Management**
- **🏗️ Modular Design**: Separate modules for processing, web UI, and shared components
- **🤖 Smart Model Management**: Easy switching between 5 YOLO models (nano to extra-large)
- **⚡ Hot Model Switching**: Change models during runtime without restart
- **📊 Performance Benchmarking**: Built-in model performance testing
- **🌐 Web UI Integration**: Complete model management through web interface
- **🔄 Backwards Compatibility**: Legacy code continues to work with deprecation warnings

### 🎯 **Quick Start Examples**
```bash
# Start with different models
python yolov8_main.py -i 0 --model yolov8n.pt  # Fastest
python yolov8_main.py -i 0 --model yolov8x.pt  # Most accurate

# Model management
python model_manager.py --list                  # Show available models
python model_manager.py --set-default yolov8l.pt  # Set default model
```

## Features

### 🎯 Core Functionality
- **Real-time People Detection**: YOLOv8-powered person detection and tracking
- **Directional Counting**: Separate counting for entry/exit with configurable detection lines
- **Composite Object Tracking**: Advanced tracking of people with umbrellas
- **Multi-Stream Support**: Handle multiple RTSP streams or test videos simultaneously
- **Intelligent Model Management**: Easy switching between YOLOv8 models (nano to extra-large)

### 🌐 Web Interface
- **Live Video Streaming**: Real-time preview with detection overlays
- **Dynamic Configuration**: Adjust detection parameters without restart
- **Model Management UI**: Download, switch, and benchmark YOLO models
- **System Monitoring**: GPU utilization, stream health, performance metrics
- **Debug Logging**: Comprehensive logging with real-time viewing

### 🔧 Advanced Features
- **Clean Modular Architecture**: Separate modules for processing, web UI, and shared components
- **Hot Model Switching**: Change YOLO models during runtime without restart
- **Performance Benchmarking**: Built-in model performance testing
- **Kalman Filter Tracking**: Smooth object tracking with prediction
- **CUDA GPU Support**: Optimized for NVIDIA GPU acceleration
- **API Integration**: REST API for external data collection
- **Flexible Video Sources**: RTSP streams, local video files, test videos

## Quick Start

### Prerequisites
- Python 3.10+ recommended
- NVIDIA GPU with CUDA support (optional but recommended)
- 8GB+ RAM for optimal performance

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd people-counter
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   # For CUDA support (recommended):
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
   
   # Install all dependencies:
   pip install -r requirements.txt
   ```

4. **Download YOLO models** (optional - auto-downloaded on first run)
   ```bash
   # List available models
   python model_manager.py --list
   
   # Download specific models
   python model_manager.py --download yolov8l.pt
   
   # Download all models
   python model_manager.py --download-all
   ```

### Running the Application

#### Web Interface (Recommended)
```bash
# Start web UI with tracker management
python web_tracker_ui.py
```
Open browser to `http://localhost:5000`

#### Direct Command Line
```bash
# New clean architecture (recommended)
python yolov8_main.py -i 0 --model yolov8m.pt --verbose

# Legacy compatibility
python yolov8_video.py -i 0
```

#### Model Management
```bash
# List available models with status
python model_manager.py --list

# Set default model for configuration
python model_manager.py --set-default yolov8l.pt --config-id 0

# Benchmark model performance
python model_manager.py --benchmark yolov8m.pt
```

## Configuration

### Stream Configuration
- **RTSP Streams**: `rtsp://camera-ip:port/stream`
- **Test Videos**: Place in `test/` directory, reference as `test/video.mp4`
- **Detection Lines**: Configure entry/exit counting boundaries
- **API Settings**: Enable external data collection

### Web Interface
1. **Configuration Tab**: Adjust detection parameters, stream URLs, API settings
2. **Model Management**: Download, switch, and benchmark YOLO models
3. **Testing Tab**: Live video preview, test video mode, debug logs
4. **Real-time Updates**: Changes apply immediately without restart

## Architecture

### Clean Modular Design
```
project/
├── shared/                    # Shared components
│   ├── tracking/              # Core tracking algorithms
│   ├── utils/                 # Utilities (threading, geometry)
│   └── logging/               # Logging infrastructure
├── yolov8/                    # YOLOv8 processing module
│   ├── core/                  # Main processing logic
│   ├── detection/             # YOLO detection
│   ├── video/                 # Stream management
│   ├── api/                   # API client
│   ├── tracking/              # Tracking integration
│   ├── visualization/         # Frame rendering
│   └── management/            # Model management
├── web_ui/                    # Web interface
│   ├── routes/                # Flask routes & API
│   ├── models/                # Data models
│   └── static/templates/      # Frontend assets
└── config/                    # Application configuration
```

### Core Components
- **`yolov8_main.py`**: New clean architecture entry point
- **`yolov8_video.py`**: Legacy compatibility wrapper
- **`model_manager.py`**: YOLO model management utility
- **`web_tracker_ui.py`**: Flask web interface
- **`shared/tracking/`**: Core tracking algorithms
- **`config/config.py`**: Configuration management

### Detection Pipeline
1. **Video Input**: RTSP stream or video file
2. **Object Detection**: YOLOv8 person detection
3. **Tracking**: Centroid-based tracking with Kalman filtering
4. **Counting Logic**: Directional counting based on detection lines
5. **Output**: Real-time counts, API updates, web display

## Model Selection & Performance

### Available YOLO Models
| Model | Speed | Accuracy | Size | Best For |
|-------|-------|----------|------|----------|
| **yolov8n.pt** | ⚡⚡⚡⚡⚡ | ⭐⭐ | 6MB | Real-time, mobile, edge devices |
| **yolov8s.pt** | ⚡⚡⚡⚡ | ⭐⭐⭐ | 22MB | Fast processing, embedded systems |
| **yolov8m.pt** | ⚡⚡⚡ | ⭐⭐⭐⭐ | 52MB | **Default** - balanced performance |
| **yolov8l.pt** | ⚡⚡ | ⭐⭐⭐⭐⭐ | 88MB | Production systems, high accuracy |
| **yolov8x.pt** | ⚡ | ⭐⭐⭐⭐⭐⭐ | 137MB | Maximum accuracy, offline processing |

### GPU Requirements
- **Minimum**: GTX 1060 / RTX 2060 (6GB VRAM)
- **Recommended**: RTX 3070+ / RTX 4070+ (8GB+ VRAM)
- **Multiple Streams**: RTX 4080+ (12GB+ VRAM)

### Performance Tips
- Use `yolov8n.pt` for fastest inference on lower-end hardware
- Use `yolov8m.pt` for balanced accuracy/speed (default)
- Use `yolov8l.pt` or `yolov8x.pt` for maximum accuracy
- Switch models instantly: `python model_manager.py --set-default yolov8l.pt`
- Benchmark models: `python model_manager.py --benchmark yolov8m.pt`

## Troubleshooting

### Common Issues
- **CUDA not available**: Install CUDA toolkit and compatible PyTorch
- **Memory errors**: Reduce batch size or video resolution
- **Stream connection**: Check RTSP URL format and network connectivity
- **Package conflicts**: Use clean virtual environment

### Debug Mode
Enable debug logging in the web interface to diagnose issues:
- Stream connectivity problems
- Detection accuracy issues
- Performance bottlenecks

## API Reference

### REST Endpoints

#### Tracker Management
- `POST /api/start/<id>` - Start tracker instance
- `POST /api/stop/<id>` - Stop tracker instance
- `GET /api/status` - Get status of all trackers
- `POST /api/update_config/<id>` - Update tracker configuration

#### Model Management (New!)
- `GET /api/models` - List all available models with status
- `POST /api/models/download` - Download a specific model
- `POST /api/models/set/<id>` - Set model for tracker configuration
- `GET /api/models/current/<id>` - Get current model for tracker
- `POST /api/models/test` - Test model performance
- `GET /api/models/recommendations` - Get model recommendations

#### Video Streaming
- `POST /api/start_stream/<id>` - Start video stream preview
- `GET /api/stop_stream/<id>` - Stop video stream
- `GET /api/video_feed/<id>` - Get video frame (JPEG)
- `GET /api/stream_info` - Get stream status for all trackers

## Migration Guide

### From Legacy to Clean Architecture

The project has been restructured with a clean modular architecture. Here's how to migrate:

#### ✅ **Recommended New Usage:**
```bash
# Use new entry point
python yolov8_main.py -i 0 --model yolov8l.pt --verbose

# Model management
python model_manager.py --list
python model_manager.py --set-default yolov8x.pt
```

#### ⚠️ **Legacy Compatibility:**
```bash
# Old method still works (with deprecation warning)
python yolov8_video.py -i 0
```

#### 📦 **Import Changes:**
```python
# New recommended imports
from yolov8.core.processor import VideoProcessor
from shared.tracking import CentroidTracker
from shared.utils import ThreadingClass

# Legacy imports still work (with warnings)
from tracking.centroid_tracker import CentroidTracker
```

### Benefits of New Architecture
- **🔧 Easy Model Switching**: Change YOLO models with one command
- **🎯 Clean Separation**: Modular components for better maintenance
- **🔄 Hot Configuration**: Update settings without restart
- **📊 Performance Monitoring**: Built-in model benchmarking
- **🌐 Web UI Integration**: Complete model management through web interface
- **🛠️ Future-Ready**: Easy to extend with new features

## Documentation

### Additional Resources
- [**Model Management Guide**](MODEL_MANAGEMENT.md) - Complete guide to YOLO model management
- [**Shared Architecture**](SHARED_ARCHITECTURE.md) - Details about the modular architecture
- [**Final Architecture**](ARCHITECTURE) - Complete architecture overview
- [**Test Results**](TEST_RESULTS.md) - Comprehensive testing documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **YOLOv8**: [Ultralytics](https://github.com/ultralytics/ultralytics)
- **Tracking Algorithms**: FilterPy, OpenCV contributions
- **Web Framework**: Flask and related libraries
