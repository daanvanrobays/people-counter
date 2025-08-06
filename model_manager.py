#!/usr/bin/env python3
"""YOLO Model Management Utility

Easy script to download, list, and switch between different YOLO11 models.
"""

import argparse
import json
import os

from ultralytics import YOLO

# Available YOLO11 models with their properties
YOLO_MODELS = {
    "yolo11n.pt": {
        "name": "YOLO11 Nano",
        "speed": "fastest",
        "accuracy": "lowest",
        "size": "~6MB",
        "description": "Best for real-time applications with limited resources"
    },
    "yolo11s.pt": {
        "name": "YOLO11 Small", 
        "speed": "very fast",
        "accuracy": "low",
        "size": "~22MB",
        "description": "Good balance for mobile/edge devices"
    },
    "yolo11m.pt": {
        "name": "YOLO11 Medium",
        "speed": "fast", 
        "accuracy": "medium",
        "size": "~52MB",
        "description": "Default model - good balance of speed and accuracy"
    },
    "yolo11l.pt": {
        "name": "YOLO11 Large",
        "speed": "medium",
        "accuracy": "high", 
        "size": "~88MB",
        "description": "Better accuracy for production systems"
    },
    "yolo11x.pt": {
        "name": "YOLO11 Extra Large",
        "speed": "slow",
        "accuracy": "highest",
        "size": "~137MB", 
        "description": "Best accuracy, suitable for offline processing"
    }
}


def list_models():
    """List all available YOLO models with their properties."""
    print("🤖 Available YOLO11 Models:\n")
    
    for model_file, info in YOLO_MODELS.items():
        exists = "✅" if os.path.exists(model_file) else "⬇️"
        print(f"{exists} {model_file}")
        print(f"   Name: {info['name']}")
        print(f"   Speed: {info['speed']} | Accuracy: {info['accuracy']} | Size: {info['size']}")
        print(f"   {info['description']}")
        print()


def download_model(model_name):
    """Download a specific YOLO model."""
    if model_name not in YOLO_MODELS:
        print(f"❌ Unknown model: {model_name}")
        print(f"Available models: {', '.join(YOLO_MODELS.keys())}")
        return False
    
    if os.path.exists(model_name):
        print(f"✅ Model {model_name} already exists")
        return True
    
    print(f"⬇️ Downloading {model_name}...")
    try:
        # This will automatically download the model
        model = YOLO(model_name)
        print(f"✅ Successfully downloaded {model_name}")
        return True
    except Exception as e:
        print(f"❌ Failed to download {model_name}: {e}")
        return False


def set_default_model(model_name, config_id=0):
    """Set the default model in configuration."""
    if model_name not in YOLO_MODELS:
        print(f"❌ Unknown model: {model_name}")
        return False
    
    if not os.path.exists(model_name):
        print(f"⬇️ Model {model_name} not found locally. Downloading...")
        if not download_model(model_name):
            return False
    
    # Update the temp config file
    temp_config_file = f"config/temp_config_{config_id}.json"
    
    try:
        # Load existing config if it exists
        config_data = {}
        if os.path.exists(temp_config_file):
            with open(temp_config_file, 'r') as f:
                config_data = json.load(f)
        
        # Update model and set update flag
        config_data['yolo_model'] = model_name
        config_data['config_updated'] = True
        
        # Save updated config
        os.makedirs(os.path.dirname(temp_config_file), exist_ok=True)
        with open(temp_config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        print(f"✅ Set default model to {model_name} for config {config_id}")
        print(f"🔄 Restart your video processor to apply changes")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update configuration: {e}")
        return False


def benchmark_model(model_name):
    """Run a quick benchmark on a model."""
    if not os.path.exists(model_name):
        print(f"⬇️ Model {model_name} not found. Downloading...")
        if not download_model(model_name):
            return
    
    print(f"🏃 Benchmarking {model_name}...")
    try:
        import time
        import numpy as np
        
        model = YOLO(model_name)
        
        # Create dummy image
        dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
        
        # Warm up
        model(dummy_image, verbose=False)
        
        # Benchmark
        times = []
        for i in range(10):
            start = time.time()
            results = model(dummy_image, verbose=False)
            end = time.time()
            times.append(end - start)
        
        avg_time = np.mean(times) * 1000  # Convert to ms
        fps = 1000 / avg_time
        
        print(f"📊 Benchmark Results for {model_name}:")
        print(f"   Average inference time: {avg_time:.1f}ms")
        print(f"   Estimated FPS: {fps:.1f}")
        
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="YOLO Model Manager")
    parser.add_argument("--list", action="store_true", help="List all available models")
    parser.add_argument("--download", type=str, help="Download a specific model")
    parser.add_argument("--set-default", type=str, help="Set default model for processing")
    parser.add_argument("--config-id", type=int, default=0, help="Configuration ID (default: 0)")
    parser.add_argument("--benchmark", type=str, help="Benchmark a model")
    parser.add_argument("--download-all", action="store_true", help="Download all models")
    
    args = parser.parse_args()
    
    if args.list:
        list_models()
    elif args.download:
        download_model(args.download)
    elif args.download_all:
        print("⬇️ Downloading all YOLO11 models...")
        for model_name in YOLO_MODELS.keys():
            download_model(model_name)
    elif args.set_default:
        set_default_model(args.set_default, args.config_id)
    elif args.benchmark:
        benchmark_model(args.benchmark)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()