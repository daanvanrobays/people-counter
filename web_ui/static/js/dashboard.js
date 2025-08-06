// Helper function to get device name
function getDeviceName(trackerId) {
    const deviceInput = document.getElementById(`device-${trackerId}`);
    return deviceInput ? deviceInput.value || `Tracker ${trackerId}` : `Tracker ${trackerId}`;
}

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
    }
}

// Configuration management functions
function applyConfig(configId) {
    const streamUrl = document.getElementById(`stream-url-${configId}`).value;
    const device = document.getElementById(`device-${configId}`).value;
    const coordsLeftLine = parseInt(document.getElementById(`coords-left-line-${configId}`).value);
    const coordsRightLine = parseInt(document.getElementById(`coords-right-line-${configId}`).value);
    const enableApi = document.getElementById(`enable-api-${configId}`).checked;
    const apiUrl = document.getElementById(`api-url-${configId}`).value;
    const apiInterval = parseInt(document.getElementById(`api-interval-${configId}`).value);

    const config = {
        debug_mode: false, // Default to false since test video mode was removed
        stream_url: streamUrl,
        device: device,
        coords_left_line: coordsLeftLine,
        coords_right_line: coordsRightLine,
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
        const deviceName = getDeviceName(configId);
        showAlert(`Error updating config for ${deviceName}: ${error.message}`, 'error', configId);
    });
}

// Auto-refresh management
let autoRefreshIntervals = {};

// Handle debug logging toggle
function toggleDebugLogging(trackerId) {
    const checkbox = document.getElementById(`enable-debug-logging-${trackerId}`);
    const isEnabled = checkbox.checked;
    
    // Update the config with the new debug logging state
    const config = {
        enable_debug_logging: isEnabled
    };
    
    fetch(`/api/update_debug_logging/${trackerId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            const deviceName = getDeviceName(trackerId);
            const message = isEnabled ? 
                `Debug logging enabled for ${deviceName}` : 
                `Debug logging disabled for ${deviceName}`;
            showAlert(message, 'info', trackerId);
        } else {
            showAlert(result.message, 'error', trackerId);
            // Revert checkbox state on error
            checkbox.checked = !isEnabled;
        }
    })
    .catch(error => {
        const deviceName = getDeviceName(trackerId);
        showAlert(`Error updating debug logging for ${deviceName}: ${error.message}`, 'error', trackerId);
        // Revert checkbox state on error
        checkbox.checked = !isEnabled;
    });
}


function startAutoRefresh(trackerId) {
    // Clear any existing interval
    if (autoRefreshIntervals[trackerId]) {
        clearInterval(autoRefreshIntervals[trackerId]);
    }
    
    // Always start auto-refresh when tracker is running
    autoRefreshIntervals[trackerId] = setInterval(() => {
        refreshDebugLogs(trackerId);
    }, 3000); // Refresh every 3 seconds
}

function stopAutoRefresh(trackerId) {
    if (autoRefreshIntervals[trackerId]) {
        clearInterval(autoRefreshIntervals[trackerId]);
        delete autoRefreshIntervals[trackerId];
    }
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
            startAutoRefresh(trackerId);
            showAlert(result.message, 'success', trackerId);
        } else {
            showAlert(result.message, 'error', trackerId);
        }
    })
    .catch(error => {
        const deviceName = getDeviceName(trackerId);
        showAlert(`Error starting ${deviceName}: ${error.message}`, 'error', trackerId);
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
            stopAutoRefresh(trackerId);
            showAlert(result.message, 'success', trackerId);
        } else {
            showAlert(result.message, 'error', trackerId);
        }
    })
    .catch(error => {
        const deviceName = getDeviceName(trackerId);
        showAlert(`Error stopping ${deviceName}: ${error.message}`, 'error', trackerId);
    });
}

// Helper function to clean log messages and format timestamps
function formatLogEntry(log) {
    // Parse the ISO timestamp to a more readable format
    const timestamp = new Date(log.timestamp).toLocaleTimeString('en-US', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    // Clean the message by removing embedded timestamps and log levels
    let cleanMessage = log.message;
    
    // Remove embedded [INFO], [WARNING], [ERROR] prefixes
    cleanMessage = cleanMessage.replace(/^\[INFO\]\s*/, '');
    cleanMessage = cleanMessage.replace(/^\[WARNING\]\s*/, '');
    cleanMessage = cleanMessage.replace(/^\[ERROR\]\s*/, '');
    
    // Remove embedded timestamps (various formats)
    cleanMessage = cleanMessage.replace(/^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}:\s*/, '');
    cleanMessage = cleanMessage.replace(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[.\d]*:\s*/, '');
    cleanMessage = cleanMessage.replace(/^\d{2}:\d{2}:\d{2}:\s*/, '');
    
    return {
        timestamp: timestamp,
        message: cleanMessage.trim(),
        level: log.level.toLowerCase()
    };
}

// Helper function for smooth scroll to bottom
function scrollToBottomSmooth(element) {
    // Use requestAnimationFrame for smoother scrolling
    const targetScrollTop = element.scrollHeight - element.clientHeight;
    const startScrollTop = element.scrollTop;
    const distance = targetScrollTop - startScrollTop;
    const duration = 300; // 300ms animation
    let startTime = null;
    
    function animation(currentTime) {
        if (startTime === null) startTime = currentTime;
        const timeElapsed = currentTime - startTime;
        const progress = Math.min(timeElapsed / duration, 1);
        
        // Easing function (ease-out)
        const easeOut = 1 - Math.pow(1 - progress, 3);
        element.scrollTop = startScrollTop + (distance * easeOut);
        
        if (timeElapsed < duration) {
            requestAnimationFrame(animation);
        }
    }
    
    requestAnimationFrame(animation);
}

// Debug logs functions
function refreshDebugLogs(trackerId) {
    fetch(`/api/debug_logs/${trackerId}`)
    .then(response => response.json())
    .then(data => {
        const logsContainer = document.getElementById(`debug-logs-${trackerId}`);
        if (data.logs && data.logs.length > 0) {
            // Store current scroll position to check if user was at bottom
            const wasAtBottom = logsContainer.scrollTop >= (logsContainer.scrollHeight - logsContainer.clientHeight - 50);
            
            // Store previous log count to detect new logs
            const previousLogCount = logsContainer.children.length;
            const newLogCount = data.logs.length;
            const hasNewLogs = newLogCount > previousLogCount;
            
            logsContainer.innerHTML = data.logs.map((log, index) => {
                const isNewLog = hasNewLogs && index >= previousLogCount;
                const newLogClass = isNewLog ? ' new-log' : '';
                const formattedLog = formatLogEntry(log);
                return `<div class="log-entry ${formattedLog.level}${newLogClass}">
                    <span class="log-timestamp">${formattedLog.timestamp}</span>
                    <span class="log-message">${formattedLog.message}</span>
                </div>`;
            }).join('');
            
            // Auto-scroll to bottom if user was previously at bottom, on first load, or when new logs arrive
            if (wasAtBottom || logsContainer.scrollTop === 0 || hasNewLogs) {
                setTimeout(() => scrollToBottomSmooth(logsContainer), 100); // Small delay to allow DOM update
            }
            
            // Remove new-log class after animation
            if (hasNewLogs) {
                setTimeout(() => {
                    logsContainer.querySelectorAll('.log-entry.new-log').forEach(entry => {
                        entry.classList.remove('new-log');
                    });
                }, 1000);
            }
        } else {
            logsContainer.innerHTML = '<div class="log-entry info">No debug logs available</div>';
        }
    })
    .catch(error => {
        const logsContainer = document.getElementById(`debug-logs-${trackerId}`);
        logsContainer.innerHTML = 
            `<div class="log-entry error">Error loading logs: ${error.message}</div>`;
        // Scroll to show error message
        scrollToBottomSmooth(logsContainer);
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

// Alert system
function showAlert(message, type, trackerId = null) {
    // Create toast container if it doesn't exist
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    // Add to container
    container.appendChild(toast);
    
    // Remove after 4 seconds
    setTimeout(() => {
        toast.remove();
    }, 4000);
}

// Initialize the interface
window.addEventListener('load', () => {
    // Initial refresh of debug logs
    refreshDebugLogs(0);
    refreshDebugLogs(1);
    // Open config tab by default
    showTab(0, 'config');
    showTab(1, 'config');
    
    // Check if trackers are already running and start auto-refresh
    const status0 = document.getElementById('status-0').textContent;
    const status1 = document.getElementById('status-1').textContent;
    
    if (status0 === 'Running') {
        startAutoRefresh(0);
    }
    if (status1 === 'Running') {
        startAutoRefresh(1);
    }
    
    // Set up event listeners for debug logging checkboxes
    document.getElementById('enable-debug-logging-0').addEventListener('change', () => toggleDebugLogging(0));
    document.getElementById('enable-debug-logging-1').addEventListener('change', () => toggleDebugLogging(1));
    
});
