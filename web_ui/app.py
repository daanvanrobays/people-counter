#!/usr/bin/env python3
"""
Flask Application Factory for People Counter Web UI
"""
import os
from flask import Flask

def create_app(config_name='default'):
    """Flask application factory"""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Configuration
    app.config.from_object(f'web_ui.config.settings.{config_name.title()}Config')
    
    # Register Blueprints
    from web_ui.routes.main import main
    from web_ui.routes.api import api  
    from web_ui.routes.video import video
    
    app.register_blueprint(main)
    app.register_blueprint(api)
    app.register_blueprint(video)
    
    # Initialize extensions/services
    from web_ui.models.tracker_manager import tracker_manager
    app.tracker_manager = tracker_manager
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("Starting YOLOv7 Multi-Tracker Web UI...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)