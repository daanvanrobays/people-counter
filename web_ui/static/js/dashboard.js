// Tab switching functionality
function showTab(trackerId, tabName) {
    // Hide all tabs for this tracker
    document.querySelectorAll(`#testing-tab-${trackerId}, #config-tab-${trackerId}`).forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Hide all tab buttons for this tracker
    const tabNavigation = document.querySelectorAll('.tracker-panel')[trackerId].querySelector('.tab-navigation');
    tabNavigation.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab
    document.getElementById(`${tabName}-tab-${trackerId}`).classList.add('active');
    // Find the correct button and add the active class
    tabNavigation.querySelector(`.tab-btn[onclick*="showTab(${trackerId}, '${tabName}')"]`).classList.add('active');
    
    // Load appropriate data
    if (tabName === 'testing') {
        // Refresh logs and stream info
        refreshDebugLogs(trackerId);
        refreshStreamInfo();
    }
}

// Configuration management functions
function applyConfig(configId) {
    const testVideoMode = document.getElementById(`test-video-mode-${configId}`).checked;
    const streamUrl = document.getElementById(`stream-url-${configId}`).value;
    const device = document.getElementById(`device-${configId}`).value;
    const coordsLeftLine = parseInt(document.getElementById(`coords-left-line-${configId}`).value);
    const enableApi = document.getElementById(`enable-api-${configId}`).checked;
    const apiUrl = document.getElementById(`api-url-${configId}`).value;
    const apiInterval = parseInt(document.getElementById(`api-interval-${configId}`).value);

    const config = {
        debug_mode: testVideoMode,
        stream_url: streamUrl,
        device: device,
        coords_left_line: coordsLeftLine,
        enable_api: enableApi,
        api_url: apiUrl,
        api_interval: apiInterval
    };
    
    fetch(`/api/update_config/${configId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showAlert(result.message, 'success', configId);
        } else {
            showAlert(result.message, 'error', configId);
        }
    })
    .catch(error => {
        showAlert(`Error updating config ${configId}: ${error.message}`, 'error', configId);
    });
}

// Tracker control functions
function startTracker(trackerId) {
    fetch(`/api/start_tracker/${trackerId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            document.getElementById(`status-${trackerId}`).textContent = 'Running';
            document.getElementById(`status-${trackerId}`).className = 'status running';
            showAlert(result.message, 'success', trackerId);
        } else {
            showAlert(result.message, 'error', trackerId);
        }
    })
    .catch(error => {
        showAlert(`Error starting tracker ${trackerId}: ${error.message}`, 'error', trackerId);
    });
}

function stopTracker(trackerId) {
    fetch(`/api/stop_tracker/${trackerId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            document.getElementById(`status-${trackerId}`).textContent = 'Stopped';
            document.getElementById(`status-${trackerId}`).className = 'status stopped';
            showAlert(result.message, 'success', trackerId);
        } else {
            showAlert(result.message, 'error', trackerId);
        }
    })
    .catch(error => {
        showAlert(`Error stopping tracker ${trackerId}: ${error.message}`, 'error', trackerId);
    });
}

// Video stream functions
function startVideoStream(trackerId) {
    fetch(`/api/start_stream/${trackerId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            const videoContainer = document.getElementById(`video-stream-${trackerId}`);
            // Replace with actual video stream - add timestamp to prevent caching
            const timestamp = new Date().getTime();
            videoContainer.innerHTML = `<img src="/api/video_feed/${trackerId}?t=${timestamp}" alt="Live Stream" class="video-stream" onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQwIiBoZWlnaHQ9IjM2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMzMzIi8+PHRleHQgeD0iNTAlIiB5PSI0NSUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxOHB4IiBmaWxsPSIjZjNiMzIzIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5TdHJlYW0gRXJyb3I8L3RleHQ+PHRleHQgeD0iNTAlIiB5PSI1NSUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNHB4IiBmaWxsPSIjYWFhIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5DaGVjayBjb25maWd1cmF0aW9uPC90ZXh0Pjwvc3ZnPg=='">`;
            
            // Update health indicators
            document.getElementById(`health-dot-${trackerId}`).className = 'health-dot active';
            document.getElementById(`health-status-${trackerId}`).textContent = 'Active';
            
            // Start video refresh
            startVideoRefresh(trackerId);
            
            showAlert('Video stream started', 'success', trackerId);
        } else {
            showAlert(result.message, 'error', trackerId);
        }
    })
    .catch(error => {
        showAlert(`Error starting video stream: ${error.message}`, 'error', trackerId);
    });
}

function stopVideoStream(trackerId) {
    const videoContainer = document.getElementById(`video-stream-${trackerId}`);
    const trackerName = trackerId === 0 ? 'Entrance' : 'Exit';
    
    // Reset to placeholder SVG
    videoContainer.innerHTML = `
        <svg width="640" height="360" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="#333"/>
            <text x="50%" y="45%" font-family="Arial, sans-serif" font-size="18px" fill="#f3b323" text-anchor="middle">${trackerName} Feed</text>
            <text x="50%" y="55%" font-family="Arial, sans-serif" font-size="14px" fill="#aaa" text-anchor="middle">Click "Start Preview"</text>
        </svg>
    `;
    
    // Stop video refresh
    stopVideoRefresh(trackerId);
    
    // Update health indicators
    document.getElementById(`health-dot-${trackerId}`).className = 'health-dot inactive';
    document.getElementById(`health-status-${trackerId}`).textContent = 'Inactive';
    document.getElementById(`fps-display-${trackerId}`).textContent = '0.0 FPS';
    
    showAlert('Video stream stopped', 'info', trackerId);
}

// Test video mode functions
function toggleTestVideoMode(trackerId) {
    const checkbox = document.getElementById(`test-video-mode-${trackerId}`);
    const controlsPanel = document.getElementById(`test-video-controls-${trackerId}`);
    
    if (checkbox.checked) {
        controlsPanel.classList.remove('hidden');
    } else {
        controlsPanel.classList.add('hidden');
    }
}

function updateStreamUrl(trackerId) {
    const selectElement = document.getElementById(`test-video-${trackerId}`);
    const streamUrlInput = document.getElementById(`stream-url-${trackerId}`);
    
    if (selectElement.value) {
        streamUrlInput.value = selectElement.value;
    }
}

// Debug logs functions
function refreshDebugLogs(trackerId) {
    fetch(`/api/debug_logs/${trackerId}`)
    .then(response => response.json())
    .then(data => {
        const logsContainer = document.getElementById(`debug-logs-${trackerId}`);
        if (data.logs && data.logs.length > 0) {
            logsContainer.innerHTML = data.logs.map(log => 
                `<div class="log-entry ${log.level}">[${log.timestamp}] ${log.message}</div>`
            ).join('');
        } else {
            logsContainer.innerHTML = '<div class="log-entry info">No debug logs available</div>';
        }
    })
    .catch(error => {
        document.getElementById(`debug-logs-${trackerId}`).innerHTML = 
            `<div class="log-entry error">Error loading logs: ${error.message}</div>`;
    });
}

function clearDebugLogs(trackerId) {
    fetch(`/api/clear_logs/${trackerId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            document.getElementById(`debug-logs-${trackerId}`).innerHTML = 
                '<div class="log-entry info">Debug logs cleared</div>';
            showAlert('Debug logs cleared', 'success', trackerId);
        }
    })
    .catch(error => {
        showAlert(`Error clearing logs: ${error.message}`, 'error', trackerId);
    });
}

// Stream info refresh function
function refreshStreamInfo() {
    fetch('/api/stream_info')
    .then(response => response.json())
    .then(data => {
        // Update FPS displays and health indicators for all trackers
        data.trackers.forEach((tracker, index) => {
            document.getElementById(`fps-display-${index}`).textContent = `${tracker.fps} FPS`;
            
            const healthDot = document.getElementById(`health-dot-${index}`);
            const healthStatus = document.getElementById(`health-status-${index}`);
            
            if (tracker.active) {
                healthDot.className = 'health-dot active';
                healthStatus.textContent = 'Active';
            } else {
                healthDot.className = 'health-dot inactive';
                healthStatus.textContent = 'Inactive';
            }
        });
    })
    .catch(error => {
        console.error('Error refreshing stream info:', error);
    });
}

// Alert system
function showAlert(message, type, trackerId = null) {
    const alertClass = type === 'success' ? 'alert-success' : type === 'error' ? 'alert-error' : 'alert-info';
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert ${alertClass}`;
    alertDiv.textContent = message;
    
    // Add to the tracker panel or body
    const targetElement = trackerId !== null ? 
        document.querySelector(`.tracker-panel:nth-child(${trackerId + 1})`) : 
        document.body;
    
    targetElement.appendChild(alertDiv);
    
    // Remove after 3 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

// Video refresh management
let videoRefreshIntervals = {};

function refreshVideoFrame(trackerId) {
    const videoElement = document.querySelector(`#video-stream-${trackerId} img`);
    if (videoElement && videoElement.src.includes('/api/video_feed/')) {
        const timestamp = new Date().getTime();
        const baseSrc = videoElement.src.split('?')[0];
        videoElement.src = `${baseSrc}?t=${timestamp}`;
    }
}

function startVideoRefresh(trackerId) {
    stopVideoRefresh(trackerId); // Clear any existing interval
    videoRefreshIntervals[trackerId] = setInterval(() => {
        refreshVideoFrame(trackerId);
    }, 200); // Refresh every 200ms (5 FPS)
}

function stopVideoRefresh(trackerId) {
    if (videoRefreshIntervals[trackerId]) {
        clearInterval(videoRefreshIntervals[trackerId]);
        delete videoRefreshIntervals[trackerId];
    }
}

// Initialize the interface
window.addEventListener('load', () => {
    // Initial refresh of stream info and debug logs
    refreshStreamInfo();
    refreshDebugLogs(0);
    refreshDebugLogs(1);
    // Open config tab by default
    showTab(0, 'config');
    showTab(1, 'config');
    
    // Set up auto-refresh for logs
    setInterval(() => {
        if (document.getElementById('auto-refresh-logs-0').checked) {
            refreshDebugLogs(0);
        }
        if (document.getElementById('auto-refresh-logs-1').checked) {
            refreshDebugLogs(1);
        }
        refreshStreamInfo();
    }, 5000); // Refresh every 5 seconds
});
