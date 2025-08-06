"""
API routes for People Counter Web UI
"""
import json
import os
from flask import Blueprint, jsonify, request
from web_ui.models.tracker_manager import tracker_manager

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/status')
def status():
    """Get status of all trackers"""
    statuses = {}
    for config_id in [0, 1]:
        statuses[config_id] = tracker_manager.get_status(config_id)
    return jsonify(statuses)


@api.route('/start/<int:config_id>')
def start(config_id):
    """Start a tracker"""
    result = tracker_manager.start_tracker(config_id)
    return jsonify(result)


@api.route('/stop/<int:config_id>')
def stop(config_id):
    """Stop a tracker"""
    result = tracker_manager.stop_tracker(config_id)
    return jsonify(result)


@api.route('/update_config/<int:config_id>', methods=['POST'])
def update_config(config_id):
    """Update configuration"""
    try:
        new_config = request.json
        result = tracker_manager.update_config(config_id, new_config)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@api.route('/debug_logs/<int:config_id>')
def get_debug_logs(config_id):
    """Get debug logs for a tracker"""
    try:
        log_file = f"logs/tracker_{config_id}.json"
        if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
            with open(log_file, 'r') as f:
                logs = json.load(f)
            # Return only the last 50 logs for performance
            return jsonify({"success": True, "logs": logs[-50:]})
        else:
            return jsonify({"success": True, "logs": []})
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "logs": []})


@api.route('/debug_logs/<int:config_id>/clear', methods=['POST'])
def clear_debug_logs(config_id):
    """Clear debug logs for a tracker"""
    result = tracker_manager.clear_debug_logs(config_id)
    return jsonify(result)


# Additional routes to match JavaScript expectations
@api.route('/start_tracker/<int:tracker_id>', methods=['POST'])
def start_tracker(tracker_id):
    """Start a tracker (alias for start)"""
    result = tracker_manager.start_tracker(tracker_id)
    return jsonify(result)


@api.route('/stop_tracker/<int:tracker_id>', methods=['POST'])
def stop_tracker(tracker_id):
    """Stop a tracker (alias for stop)"""
    result = tracker_manager.stop_tracker(tracker_id)
    return jsonify(result)


@api.route('/clear_logs/<int:tracker_id>', methods=['POST'])
def clear_logs(tracker_id):
    """Clear debug logs (alias for debug_logs clear)"""
    result = tracker_manager.clear_debug_logs(tracker_id)
    return jsonify(result)


@api.route('/update_debug_logging/<int:config_id>', methods=['POST'])
def update_debug_logging(config_id):
    """Update debug logging setting for a tracker"""
    try:
        new_setting = request.json
        enable_debug_logging = new_setting.get('enable_debug_logging', True)
        result = tracker_manager.update_debug_logging(config_id, enable_debug_logging)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# Model Management API Routes
@api.route('/models')
def get_models():
    """Get all available YOLO models with their status"""
    models = tracker_manager.get_available_models()
    return jsonify({"success": True, "models": models})


@api.route('/models/download', methods=['POST'])
def download_model():
    """Download a specific YOLO model"""
    try:
        data = request.json
        model_name = data.get('model_name')
        
        if not model_name:
            return jsonify({"success": False, "message": "Model name is required"})
        
        success, message = tracker_manager.download_model(model_name)
        return jsonify({"success": success, "message": message})
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@api.route('/models/set/<int:config_id>', methods=['POST'])
def set_model(config_id):
    """Set the YOLO model for a specific configuration"""
    try:
        data = request.json
        model_name = data.get('model_name')
        
        if not model_name:
            return jsonify({"success": False, "message": "Model name is required"})
        
        result = tracker_manager.set_model_for_config(config_id, model_name)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@api.route('/models/current/<int:config_id>')
def get_current_model(config_id):
    """Get the current YOLO model for a configuration"""
    current_model = tracker_manager.get_current_model(config_id)
    return jsonify({"success": True, "current_model": current_model})


@api.route('/models/test', methods=['POST'])
def test_model():
    """Test the performance of a specific model"""
    try:
        data = request.json
        model_name = data.get('model_name')
        
        if not model_name:
            return jsonify({"success": False, "message": "Model name is required"})
        
        success, metrics = tracker_manager.test_model_performance(model_name)
        if success:
            return jsonify({"success": True, "metrics": metrics})
        else:
            return jsonify({"success": False, "message": metrics.get("error", "Test failed")})
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@api.route('/models/recommendations')
def get_model_recommendations():
    """Get model recommendations based on use case"""
    use_case = request.args.get('use_case', 'general')
    recommendations = tracker_manager.get_model_recommendations(use_case)
    return jsonify({"success": True, "recommendations": recommendations})