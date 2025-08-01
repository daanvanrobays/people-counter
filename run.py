#!/usr/bin/env python3
"""
Simple launcher for the YOLOv7 Multi-Tracker Web UI
"""
import os
import sys
import webbrowser
import time
import threading

def main():
    print("🚀 Starting AFF People Tracker Web UI...")
    print("=" * 50)
    
    # Check if Flask is installed
    try:
        import flask
    except ImportError:
        print("❌ Flask is not installed. Installing now...")
        os.system("pip install flask")
        print("✅ Flask installed successfully!")

    # Import and start the web UI
    try:
        from web_tracker_ui import app
        
        print("✅ Web UI server starting...")
        print("📋 Features available:")
        print("   • Start/Stop individual trackers")
        print("   • Debug mode with test video selection")
        print("   • Real-time status monitoring")
        print("   • Configuration management")
        print("")
        print("🌐 Opening browser in 3 seconds...")
        print("   URL: http://localhost:5000")
        print("")
        print("🛑 To stop the server, press Ctrl+C")
        print("=" * 50)
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(3)
            try:
                webbrowser.open('http://localhost:5000')
            except:
                pass  # Browser opening is optional
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Start the Flask app
        app.run(debug=False, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting web UI: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()