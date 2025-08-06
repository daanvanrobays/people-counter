# People Counter

Advanced real-time people counting system with modern web interface, intelligent debug logging, and comprehensive model management. Features clean modular architecture powered by YOLO11 object detection.

## 🚀 What's New

### ✨ **Modern Web Interface (2025 Update)**
- **🎛️ Advanced Dashboard**: Real-time tracker management with live status updates
- **📝 Smart Debug Logging**: Intelligent log filtering with performance controls
- **🔄 Auto-Refresh Logs**: Always see latest activity with smooth scrolling
- **📱 Mobile Responsive**: Works perfectly on all devices
- **🎨 Enhanced UI**: Toast notifications, smooth animations, professional styling

### 🤖 **YOLO11 Model Management**
- **🆕 Latest Models**: YOLO11 nano to extra-large (yolo11n.pt to yolo11x.pt)
- **⚡ Hot Model Switching**: Change models during runtime without restart
- **📊 Performance Benchmarking**: Built-in model performance testing
- **🌐 Web-Based Management**: Complete model control through web interface
- **🔧 Smart Defaults**: Optimized model selection for different use cases

### 🎯 **Quick Start Examples**
```bash
# Start with web interface (recommended)
python run.py

# Direct command line with different models
python detection_main.py -i 0 --model yolo11n.pt  # Fastest
python detection_main.py -i 0 --model yolo11x.pt  # Most accurate

# Model management
python model_manager.py --list                     # Show available models
python model_manager.py --set-default yolo11l.pt  # Set default model
```

## Features

### 🎯 Core Functionality
- **Real-time People Detection**: YOLOv8-powered person detection and tracking
- **Directional Counting**: Separate counting for entry/exit with configurable detection lines
- **Composite Object Tracking**: Advanced tracking of people with umbrellas
- **Multi-Stream Support**: Handle multiple RTSP streams or test videos simultaneously
- **Intelligent Model Management**: Easy switching between YOLOv8 models (nano to extra-large)

### 🌐 Modern Web Interface
- **Real-Time Dashboard**: Live tracker status with instant updates
- **Smart Debug Logging**: Intelligent filtering with performance toggle
- **Device-Named Notifications**: User-friendly alerts using device names
- **Auto-Scrolling Logs**: Latest activity always visible
- **Mobile-First Design**: Professional responsive interface
- **Toast Notifications**: Elegant feedback system with smooth animations

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
# Start modern web UI with advanced dashboard
python run.py
```
Open browser to `http://localhost:5000`

**Features:**
- Real-time tracker management dashboard  
- Smart debug logging with performance controls
- Device-named notifications and status updates
- Mobile-responsive design with toast notifications

#### Direct Command Line
```bash
# New detection system (recommended)
python detection_main.py -i 0 --model yolo11m.pt --verbose

# Legacy YOLOv8 compatibility  
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

### Modern Web Interface
1. **Configuration Tab**: Adjust detection parameters, stream URLs, API settings
2. **Testing Tab**: Smart debug logging with performance controls
3. **Real-time Dashboard**: Live tracker status with device-named notifications  
4. **Auto-Scrolling Logs**: Latest activity always visible with smooth animations
5. **Mobile Responsive**: Professional interface that works on all devices

## Architecture

### Clean Modular Design
```
project/
├── shared/                    # Shared components
│   ├── tracking/              # Core tracking algorithms
│   ├── utils/                 # Utilities (threading, geometry)
│   └── logging/               # Smart debug logging system
├── detection/                 # Modern YOLO11 detection system
│   ├── core/                  # Main processing logic
│   ├── detection/             # YOLO11 detection
│   ├── video/                 # Stream management
│   ├── api/                   # API client integration
│   ├── tracking/              # Tracking integration
│   ├── visualization/         # Frame rendering
│   └── management/            # Model management
├── web_ui/                    # Modern web interface
│   ├── routes/                # Flask routes & REST API
│   ├── models/                # Tracker management
│   ├── static/                # CSS, JS, responsive design
│   └── templates/             # HTML templates
├── yolov8/                    # Legacy YOLOv8 (deprecated)
└── config/                    # Configuration management
```

### Core Components
- **`detection_main.py`**: Modern YOLO11 detection system entry point
- **`web_tracker_ui.py`**: Advanced web interface with smart logging
- **`model_manager.py`**: YOLO model management utility
- **`shared/logging/`**: Intelligent debug logging system
- **`shared/tracking/`**: Core tracking algorithms with Kalman filtering
- **`config/config.py`**: Enhanced configuration management

### Detection Pipeline
1. **Video Input**: RTSP stream or video file
2. **Object Detection**: YOLO11 person detection with intelligent filtering
3. **Tracking**: Centroid-based tracking with Kalman filtering
4. **Counting Logic**: Directional counting based on detection lines
5. **Smart Logging**: Intelligent debug logging with performance controls
6. **Output**: Real-time counts, web dashboard updates, API integration

## Model Selection & Performance

### Available YOLO Models
| Model | Speed | Accuracy | Size | Best For |
|-------|-------|----------|------|----------|
| **yolo11n.pt** | ⚡⚡⚡⚡⚡ | ⭐⭐ | 5MB | Real-time, mobile, edge devices |
| **yolo11s.pt** | ⚡⚡⚡⚡ | ⭐⭐⭐ | 20MB | Fast processing, embedded systems |
| **yolo11m.pt** | ⚡⚡⚡ | ⭐⭐⭐⭐ | 49MB | **Default** - balanced performance |
| **yolo11l.pt** | ⚡⚡ | ⭐⭐⭐⭐⭐ | 86MB | Production systems, high accuracy |
| **yolo11x.pt** | ⚡ | ⭐⭐⭐⭐⭐⭐ | 135MB | Maximum accuracy, offline processing |

### GPU Requirements
- **Minimum**: GTX 1060 / RTX 2060 (6GB VRAM)
- **Recommended**: RTX 3070+ / RTX 4070+ (8GB+ VRAM)
- **Multiple Streams**: RTX 4080+ (12GB+ VRAM)

### Performance Tips
- Use `yolo11n.pt` for fastest inference on lower-end hardware
- Use `yolo11m.pt` for balanced accuracy/speed (default)
- Use `yolo11l.pt` or `yolo11x.pt` for maximum accuracy
- Switch models instantly: `python model_manager.py --set-default yolo11l.pt`
- Benchmark models: `python model_manager.py --benchmark yolo11m.pt`
- **Debug Logging**: Toggle off in web interface for better performance on long-running systems

## Troubleshooting

### Common Issues
- **CUDA not available**: Install CUDA toolkit and compatible PyTorch
- **Memory errors**: Reduce batch size or video resolution
- **Stream connection**: Check RTSP URL format and network connectivity
- **Package conflicts**: Use clean virtual environment

### Smart Debug Logging
Use the enhanced debug logging system in the web interface:
- **Performance Toggle**: Enable/disable logging for optimal performance
- **Auto-Scrolling Logs**: Latest activity always visible
- **Intelligent Filtering**: Clean, readable log messages
- **Real-Time Updates**: Immediate feedback on system status
- **Device Names**: User-friendly notifications with device names

## API Reference

### REST Endpoints

#### Tracker Management
- `POST /api/start_tracker/<id>` - Start tracker instance
- `POST /api/stop_tracker/<id>` - Stop tracker instance
- `POST /api/update_config/<id>` - Update tracker configuration
- `POST /api/update_debug_logging/<id>` - Toggle debug logging for performance

#### Model Management (New!)
- `GET /api/models` - List all available models with status
- `POST /api/models/download` - Download a specific model
- `POST /api/models/set/<id>` - Set model for tracker configuration
- `GET /api/models/current/<id>` - Get current model for tracker
- `POST /api/models/test` - Test model performance
- `GET /api/models/recommendations` - Get model recommendations

## Migration Guide

### From Legacy to Clean Architecture

The project has been restructured with a clean modular architecture. Here's how to migrate:

#### ✅ **Recommended New Usage:**
```bash
# Use modern detection system
python detection_main.py -i 0 --model yolo11l.pt --verbose

# Advanced web interface (recommended)
python run.py

# Model management
python model_manager.py --list
python model_manager.py --set-default yolo11x.pt
```

#### 📦 **Import Changes:**
```python
# New recommended imports
from detection.core.processor import VideoProcessor
from shared.tracking import CentroidTracker
from shared.logging.utils import get_tracker_debug_logger

# Legacy imports still work (deprecated)
from yolov8.core.processor import VideoProcessor
from tracking.centroid_tracker import CentroidTracker
```

### Benefits of New Architecture
- **🎛️ Modern Web Interface**: Advanced dashboard with smart debug logging
- **📝 Performance Controls**: Toggle debug logging for optimal performance
- **🔔 Device-Named Notifications**: User-friendly alerts with device names
- **🔄 Auto-Scrolling Logs**: Latest activity always visible
- **📱 Mobile Responsive**: Professional interface for all devices
- **🔧 Easy Model Switching**: YOLO11 models with one command
- **🛠️ Future-Ready**: Clean modular architecture for easy extension

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
