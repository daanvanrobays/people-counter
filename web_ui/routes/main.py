"""
Main routes for People Counter Web UI
"""
from flask import Blueprint, render_template
from web_ui.models.tracker_manager import tracker_manager

main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Main dashboard"""
    statuses = {}
    for config_id in [0, 1]:
        statuses[config_id] = tracker_manager.get_status(config_id)
    
    return render_template('dashboard.html',
                         configs=tracker_manager.configs,
                         statuses=statuses,
                         test_videos=tracker_manager.get_test_videos())