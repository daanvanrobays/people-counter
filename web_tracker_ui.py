#!/usr/bin/env python3
"""
YOLOv7 Multi-Tracker Web UI - Modular Architecture
"""
import sys
import os

# Add the current directory to Python path so we can import web_ui
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web_ui.app import create_app

# Create app instance for external imports (like run.py)
app = create_app()

if __name__ == '__main__':
    print("Starting YOLOv7 Multi-Tracker Web UI...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)