# 🤖 YOLO Model Management Guide (2025)

Advanced YOLO11 model management with web interface integration, performance controls, and intelligent debugging. The modern architecture makes model switching seamless across all interfaces.

## 🚀 **Quick Model Switching**

### **1. Modern Detection System (Recommended)**
```bash
# Switch to different YOLO11 models instantly
python detection_main.py -i 0 --model yolo11n.pt  # Fastest (Nano)
python detection_main.py -i 0 --model yolo11s.pt  # Small
python detection_main.py -i 0 --model yolo11m.pt  # Medium (default)
python detection_main.py -i 0 --model yolo11l.pt  # Large
python detection_main.py -i 0 --model yolo11x.pt  # Extra Large (best accuracy)

# Use custom trained models
python detection_main.py -i 0 --model path/to/custom_model.pt

# Enable debug logging for troubleshooting
python detection_main.py -i 0 --model yolo11m.pt --verbose
```

### **2. Model Manager Utility**
```bash
# List all available models with status
python model_manager.py --list

# Set default model for config (persists across restarts)
python model_manager.py --set-default yolo11l.pt --config-id 0

# Download specific YOLO11 models
python model_manager.py --download yolo11x.pt

# Download all models at once
python model_manager.py --download-all

# Benchmark model performance
python model_manager.py --benchmark yolo11m.pt
```

### **3. Web Interface (Recommended)**
The modern web interface provides the easiest model management:

**Access**: Open browser to `http://localhost:5000` after running `python web_tracker_ui.py`

**Features**:
- **Real-Time Dashboard**: Live tracker status with device names
- **Smart Debug Logging**: Toggle performance logging on/off
- **Model Configuration**: Set YOLO11 models per tracker
- **Instant Updates**: Changes apply immediately without restart
- **Mobile Responsive**: Works on all devices

### **4. Configuration-Based (Hot Reload)**
Update the configuration file or through the web UI:
```json
{
  "yolo_model": "yolo11l.pt",
  "enable_debug_logging": true,
  "config_updated": true
}
```
The system will automatically switch models and update logging during runtime!

### **5. Programmatic API**
```python
from detection.core.processor import VideoProcessor
from detection.management.model_manager import ModelManager

# Runtime model switching
processor = VideoProcessor(config_id=0)
success = processor.detector.switch_model("yolo11x.pt")

# Web UI integration
manager = ModelManager()
models = manager.get_available_models()
success, message = manager.set_active_model("yolo11l.pt", config_id=0)
```

## 📊 **YOLO11 Model Comparison**

| Model | Speed | Accuracy | Size | Best For | Memory Usage |
|-------|-------|----------|------|----------|--------------|
| **yolo11n.pt** | ⚡⚡⚡⚡⚡ | ⭐⭐ | 5MB | Real-time, mobile, edge devices | ~2GB VRAM |
| **yolo11s.pt** | ⚡⚡⚡⚡ | ⭐⭐⭐ | 20MB | Fast processing, embedded systems | ~3GB VRAM |
| **yolo11m.pt** | ⚡⚡⚡ | ⭐⭐⭐⭐ | 49MB | **Default** - balanced performance | ~4GB VRAM |
| **yolo11l.pt** | ⚡⚡ | ⭐⭐⭐⭐⭐ | 86MB | Production systems, high accuracy | ~6GB VRAM |
| **yolo11x.pt** | ⚡ | ⭐⭐⭐⭐⭐⭐ | 135MB | Maximum accuracy, offline processing | ~8GB VRAM |

## 🎯 **Use Case Recommendations**

### **Real-Time Processing (Live RTSP)**
```bash
python detection_main.py -i 0 --model yolo11n.pt  # Best for 30+ FPS
# Enable debug logging if needed
python detection_main.py -i 0 --model yolo11n.pt --verbose
```

### **High Accuracy Counting**
```bash
python detection_main.py -i 0 --model yolo11x.pt  # Most accurate detections
# For production, disable debug logging for better performance
```

### **Balanced Production Use (Recommended)**
```bash
python detection_main.py -i 0 --model yolo11m.pt  # Default balanced choice
# Use web interface for easier management: python web_tracker_ui.py
```

### **GPU Server Deployment**
```bash
python detection_main.py -i 0 --model yolo11l.pt  # Good accuracy with reasonable speed
# Toggle debug logging via web interface for performance optimization
```

## 🔧 **Technical Implementation**

### **Hot Model Switching**
The modern architecture supports switching models without stopping video processing:

1. **Detection Layer**: YOLO11 detector handles model loading/switching
2. **Web Interface**: Real-time model switching through dashboard
3. **Configuration**: Models specified in config with debug logging controls
4. **Hot Reload**: Config updates trigger automatic model switching
5. **Smart Logging**: Performance toggle for production deployments
6. **Fallback**: Failed switches keep the current model running

### **Enhanced Features (2025)**
- **Device-Named Notifications**: User-friendly feedback instead of "tracker 0"
- **Performance Controls**: Toggle debug logging for optimal performance
- **Auto-Scrolling Logs**: Latest activity always visible
- **Mobile Interface**: Model management from any device
- **Toast Notifications**: Professional feedback system

### **Model Management API**
```python
from detection.management.model_manager import ModelManager

manager = ModelManager()

# Get available models with download status
models = manager.get_available_models()

# Download and set active
success, msg = manager.download_model("yolov8l.pt")
success, msg = manager.set_active_model("yolov8l.pt", config_id=0)

# Performance testing
success, metrics = manager.test_model("yolov8m.pt")
print(f"FPS: {metrics['estimated_fps']}")
```

## 🌐 **Web UI Integration**

The `ModelManager` class is designed for easy web UI integration:

- **Model Status**: See which models are downloaded
- **One-Click Download**: Download models from the web interface
- **Performance Metrics**: Real-time benchmarking
- **Hot Switching**: Change models without stopping video processing
- **Recommendations**: Get model suggestions based on use case

## 🔄 **Migration Examples**

### **From YOLOv8m to YOLOv8l (Better Accuracy)**
```bash
# Method 1: Command line override
python yolov8_main.py -i 0 --model yolov8l.pt

# Method 2: Set as default
python model_manager.py --set-default yolov8l.pt

# Method 3: Web UI (update config)
# Update yolo_model field in configuration
```

### **Custom Trained Model**
```bash
# Place your custom model in the project directory
cp /path/to/my_custom_yolov8.pt ./

# Use it directly
python yolov8_main.py -i 0 --model my_custom_yolov8.pt
```

## 📈 **Performance Tuning**

### **Real-Time Optimization**
1. **Use yolov8n.pt** for maximum speed
2. **Reduce input resolution** in config
3. **Disable composite objects** if not needed
4. **Optimize tracking parameters**

### **Accuracy Optimization**
1. **Use yolov8x.pt** for best detection
2. **Increase confidence thresholds**
3. **Enable composite object tracking**
4. **Fine-tune detection parameters**

## 🛠️ **Troubleshooting**

### **Model Download Issues**
```bash
# Manual download and verify
python -c "from ultralytics import YOLO; YOLO('yolov8l.pt')"
```

### **Model Switch Failures**
- Check model file exists
- Verify file permissions
- Check disk space
- Review logs for specific errors

### **Performance Issues**
```bash
# Benchmark different models
python model_manager.py --benchmark yolov8n.pt
python model_manager.py --benchmark yolov8m.pt
python model_manager.py --benchmark yolov8l.pt
```

The clean architecture makes model management a breeze! 🎉