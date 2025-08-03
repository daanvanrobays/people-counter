# 🤖 YOLO Model Management Guide

The new clean architecture makes updating and managing YOLO models extremely easy. Here are all the ways you can work with models:

## 🚀 **Quick Model Switching**

### **1. Command Line (Runtime)**
```bash
# Switch to different models instantly
python yolov8_main.py -i 0 --model yolov8n.pt  # Fastest (Nano)
python yolov8_main.py -i 0 --model yolov8s.pt  # Small
python yolov8_main.py -i 0 --model yolov8m.pt  # Medium (default)
python yolov8_main.py -i 0 --model yolov8l.pt  # Large
python yolov8_main.py -i 0 --model yolov8x.pt  # Extra Large (best accuracy)

# Use custom trained models
python yolov8_main.py -i 0 --model path/to/custom_model.pt
```

### **2. Model Manager Utility**
```bash
# List all available models with status
python model_manager.py --list

# Set default model for config (persists across restarts)
python model_manager.py --set-default yolov8l.pt --config-id 0

# Download specific models
python model_manager.py --download yolov8x.pt

# Download all models at once
python model_manager.py --download-all

# Benchmark model performance
python model_manager.py --benchmark yolov8m.pt
```

### **3. Configuration-Based (Hot Reload)**
Update the configuration file or through the web UI:
```json
{
  "yolo_model": "yolov8l.pt",
  "config_updated": true
}
```
The system will automatically switch models during runtime!

### **4. Programmatic API**
```python
from yolov8.core.processor import VideoProcessor
from yolov8.management.model_manager import ModelManager

# Runtime model switching
processor = VideoProcessor(config_id=0)
success = processor.detector.switch_model("yolov8x.pt")

# Web UI integration
manager = ModelManager()
models = manager.get_available_models()
success, message = manager.set_active_model("yolov8l.pt", config_id=0)
```

## 📊 **Model Comparison**

| Model | Speed | Accuracy | Size | Best For |
|-------|-------|----------|------|----------|
| **yolov8n.pt** | ⚡⚡⚡⚡⚡ | ⭐⭐ | 6MB | Real-time, mobile, edge devices |
| **yolov8s.pt** | ⚡⚡⚡⚡ | ⭐⭐⭐ | 22MB | Fast processing, embedded systems |
| **yolov8m.pt** | ⚡⚡⚡ | ⭐⭐⭐⭐ | 52MB | **Default** - balanced performance |
| **yolov8l.pt** | ⚡⚡ | ⭐⭐⭐⭐⭐ | 88MB | Production systems, high accuracy |
| **yolov8x.pt** | ⚡ | ⭐⭐⭐⭐⭐⭐ | 137MB | Maximum accuracy, offline processing |

## 🎯 **Use Case Recommendations**

### **Real-Time Processing (Live RTSP)**
```bash
python yolov8_main.py -i 0 --model yolov8n.pt  # Best for 30+ FPS
```

### **High Accuracy Counting**
```bash
python yolov8_main.py -i 0 --model yolov8x.pt  # Most accurate detections
```

### **Balanced Production Use**
```bash
python yolov8_main.py -i 0 --model yolov8m.pt  # Default balanced choice
```

### **GPU Server Deployment**
```bash
python yolov8_main.py -i 0 --model yolov8l.pt  # Good accuracy with reasonable speed
```

## 🔧 **Technical Implementation**

### **Hot Model Switching**
The architecture supports switching models without stopping video processing:

1. **Detection Layer**: `YOLODetector` handles model loading/switching
2. **Configuration**: Models are specified in config files
3. **Hot Reload**: Config updates trigger automatic model switching
4. **Fallback**: Failed switches keep the current model running

### **Model Management API**
```python
from yolov8.management.model_manager import ModelManager

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