#!/bin/bash
# Config Manager Module Startup Script

set -e

# Module Configuration
MODULE_NAME="config-manager"
MODULE_VERSION="1.0.0"
MODULE_DIR="/opt/machinenativenops/modules/${MODULE_NAME}"
DEFAULT_PORT="8080"
PYTHON_PATH="/usr/bin/python3"

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [${MODULE_NAME}] $1"
}

# Error handling
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Check dependencies
check_dependencies() {
    log "Checking dependencies..."
    
    # Check Python
    if ! command -v ${PYTHON_PATH} &> /dev/null; then
        error_exit "Python not found at ${PYTHON_PATH}"
    fi
    
    # Check required files
    if [[ ! -f "${MODULE_DIR}/main.py" ]]; then
        error_exit "main.py not found in ${MODULE_DIR}"
    fi
    
    if [[ ! -f "${MODULE_DIR}/requirements.txt" ]]; then
        error_exit "requirements.txt not found in ${MODULE_DIR}"
    fi
    
    log "Dependencies check passed"
}

# Setup environment
setup_environment() {
    log "Setting up environment..."
    
    # Set default values
    export PORT=${PORT:-${DEFAULT_PORT}}
    export CONFIG_PATH=${CONFIG_PATH:-"/etc/machinenativenops/config"}
    export MODULE_NAME=${MODULE_NAME}
    export MODULE_VERSION=${MODULE_VERSION}
    
    # Add module directory to Python path
    export PYTHONPATH="${MODULE_DIR}:${PYTHONPATH}"
    
    log "Environment setup complete"
    log "PORT: ${PORT}"
    log "CONFIG_PATH: ${CONFIG_PATH}"
}

# Install dependencies
install_dependencies() {
    log "Installing Python dependencies..."
    
    cd "${MODULE_DIR}"
    ${PYTHON_PATH} -m pip install -r requirements.txt --quiet
    
    if [[ $? -ne 0 ]]; then
        error_exit "Failed to install dependencies"
    fi
    
    log "Dependencies installed successfully"
}

# Check port availability
check_port() {
    local port=${1:-${PORT}}
    
    log "Checking port ${port} availability..."
    
    if netstat -tlnp 2>/dev/null | grep -q ":${port} "; then
        error_exit "Port ${port} is already in use"
    fi
    
    log "Port ${port} is available"
}

# Start the service
start_service() {
    log "Starting ${MODULE_NAME} v${MODULE_VERSION}..."
    
    cd "${MODULE_DIR}"
    
    # Start the service in background
    nohup ${PYTHON_PATH} main.py > /var/log/machinenativenops/${MODULE_NAME}.log 2>&1 &
    
    local pid=$!
    
    log "Service started with PID: ${pid}"
    
    # Wait a moment for the service to start
    sleep 2
    
    # Check if the service is running
    if kill -0 ${pid} 2>/dev/null; then
        log "Service is running successfully"
        echo ${pid} > /var/run/machinenativenops/${MODULE_NAME}.pid
        log "PID file created: /var/run/machinenativenops/${MODULE_NAME}.pid"
    else
        error_exit "Service failed to start"
    fi
    
    # Wait for health check
    log "Waiting for health check..."
    local health_check_timeout=30
    local health_check_interval=2
    local elapsed=0
    
    while [[ ${elapsed} -lt ${health_check_timeout} ]]; do
        if curl -s -f http://localhost:${PORT}/health > /dev/null 2>&1; then
            log "Health check passed"
            log "Service is ready at: http://localhost:${PORT}/health"
            return 0
        fi
        
        sleep ${health_check_interval}
        elapsed=$((elapsed + health_check_interval))
    done
    
    error_exit "Health check failed after ${health_check_timeout} seconds"
}

# Main execution
main() {
    log "=== MachineNativeOps Config Manager Startup ==="
    log "Module: ${MODULE_NAME} v${MODULE_VERSION}"
    log "Directory: ${MODULE_DIR}"
    
    # Create necessary directories
    mkdir -p /var/log/machinenativenops
    mkdir -p /var/run/machinenativenops
    
    check_dependencies
    setup_environment
    install_dependencies
    check_port
    start_service
    
    log "=== ${MODULE_NAME} startup completed successfully ==="
}

# Handle signals
trap 'log "Received interrupt signal, shutting down..."; exit 0' INT TERM

# Execute main function
main "$@"