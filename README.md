# People Counter

Advanced real-time people counting system with web-based management interface, powered by YOLOv8 object detection.

## Features

### 🎯 Core Functionality
- **Real-time People Detection**: YOLOv8-powered person detection and tracking
- **Directional Counting**: Separate counting for entry/exit with configurable detection lines
- **Composite Object Tracking**: Advanced tracking of people with umbrellas
- **Multi-Stream Support**: Handle multiple RTSP streams or test videos simultaneously

### 🌐 Web Interface
- **Live Video Streaming**: Real-time preview with detection overlays
- **Dynamic Configuration**: Adjust detection parameters without restart
- **System Monitoring**: GPU utilization, stream health, performance metrics
- **Debug Logging**: Comprehensive logging with real-time viewing

### 🔧 Advanced Features
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
   # YOLOv8 models will be automatically downloaded when needed
   # Available models: yolov8n.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
   ```

### Running the Application

#### Web Interface (Recommended)
```bash
python run.py
```
Open browser to `http://localhost:5000`

#### Direct Command Line
```bash
# Run tracker directly (config ID: 0 or 1)
python yolov8_video.py -i 0
```

## Configuration

### Stream Configuration
- **RTSP Streams**: `rtsp://camera-ip:port/stream`
- **Test Videos**: Place in `test/` directory, reference as `test/video.mp4`
- **Detection Lines**: Configure entry/exit counting boundaries
- **API Settings**: Enable external data collection

### Web Interface
1. **Configuration Tab**: Adjust detection parameters, stream URLs, API settings
2. **Testing Tab**: Live video preview, test video mode, debug logs
3. **Real-time Updates**: Changes apply immediately without restart

## Architecture

### Core Components
- **`yolov8_video.py`**: Main YOLOv8 detection engine
- **`web_tracker_ui.py`**: Flask web interface
- **`tracking/centroid_tracker.py`**: Object tracking algorithms
- **`config/config.py`**: Configuration management
- **`drawing/frame_drawer.py`**: Video annotation and visualization

### Detection Pipeline
1. **Video Input**: RTSP stream or video file
2. **Object Detection**: YOLOv8 person detection
3. **Tracking**: Centroid-based tracking with Kalman filtering
4. **Counting Logic**: Directional counting based on detection lines
5. **Output**: Real-time counts, API updates, web display

## Performance Optimization

### GPU Requirements
- **Minimum**: GTX 1060 / RTX 2060 (6GB VRAM)
- **Recommended**: RTX 3070+ / RTX 4070+ (8GB+ VRAM)
- **Multiple Streams**: RTX 4080+ (12GB+ VRAM)

### Performance Tips
- Use YOLOv8n for fastest inference on lower-end hardware
- Use YOLOv8m for balanced accuracy/speed
- Reduce video resolution for better performance
- Enable CUDA memory optimization in settings

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
- `POST /api/tracker/{id}/start` - Start tracker
- `POST /api/tracker/{id}/stop` - Stop tracker  
- `PUT /api/tracker/{id}/config` - Update configuration
- `GET /api/tracker/{id}/status` - Get tracker status

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **YOLOv8**: [Ultralytics](https://github.com/ultralytics/ultralytics)
- **Tracking Algorithms**: FilterPy, OpenCV contributions
- **Web Framework**: Flask and related libraries
