# MachineNativeOps Auto Monitor

## Overview

MachineNativeOps Auto Monitor is a production-ready system monitoring solution with quantum state tracking capabilities. It provides real-time metrics collection, alerting, and observability for modern computing environments including quantum workloads.

## Features

- **System Monitoring**: CPU, memory, disk, and network metrics
- **Quantum Monitoring**: Quantum state fidelity, coherence time, and error rate tracking
- **Kubernetes Integration**: Service and pod monitoring with auto-discovery
- **Prometheus Integration**: Built-in metrics exposition
- **Alert Management**: Threshold-based alerting with auto-repair capabilities
- **Database Storage**: SQLite-based metrics storage with retention policies
- **FastAPI Web Interface**: REST API for health checks and metrics retrieval
- **Production Ready**: Systemd service integration and proper packaging

## Installation

### From Source (Development)

```bash
# Clone repository
git clone https://github.com/MachineNativeOps/machine-native-ops-aaps.git
cd machine-native-ops-aaps/engine/machinenativenops-auto-monitor

# Install in development mode
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

### From Package (Production)

```bash
# Install from PyPI (when published)
pip install machinenativenops-auto-monitor

# Or from wheel
pip install machinenativenops-auto-monitor-2.0.0-py3-none-any.whl
```

## Configuration

The monitor uses YAML configuration files. The default configuration is located at:
- Package: `assets/default_config.yaml`
- System: `/etc/machinenativenops/monitor_config.yaml`

### Generate Default Configuration

```bash
# Print to stdout
machinenativenops-auto-monitor print-default-config

# Save to file
machinenativenops-auto-monitor print-default-config --output my_config.yaml
```

### Environment Variables

Key configuration can be overridden via environment variables:

```bash
export MNO_CONFIG_FILE="/path/to/config.yaml"
export MNO_LOG_LEVEL="DEBUG"
export MNO_PROMETHEUS_PORT="8080"
export MNO_DATABASE_PATH="/path/to/metrics.db"
export QUANTUM_ENABLED="true"
export AUTO_REPAIR_ENABLED="false"
```

## Usage

### Start Monitoring Service

```bash
# Using default configuration
machinenativenops-auto-monitor serve

# With custom configuration
machinenativenops-auto-monitor serve --config /path/to/config.yaml

# With debug logging
machinenativenops-auto-monitor serve --log-level DEBUG
```

### One-Time Collection

```bash
# Collect once and print results
machinenativenops-auto-monitor once

# Save results to file
machinenativenops-auto-monitor once --output metrics.json
```

### Configuration Validation

```bash
# Validate configuration file
machinenativenops-auto-monitor validate-config --config my_config.yaml
```

### Database Statistics

```bash
# Show database statistics
machinenativenops-auto-monitor database-stats
```

## API Endpoints

When running in `serve` mode, the monitor provides several HTTP endpoints:

- **Health Check**: `GET /health` - Service health status
- **Metrics**: `GET /metrics` - Prometheus metrics
- **Status**: `GET /status` - Detailed service status
- **API Documentation**: `GET /docs` - FastAPI documentation

### Example API Usage

```bash
# Health check
curl http://localhost:8000/health

# Get recent metrics
curl http://localhost:8000/api/v1/metrics?limit=10

# Get active alerts
curl http://localhost:8000/api/v1/alerts

# Prometheus metrics
curl http://localhost:8000/metrics
```

## Prometheus Integration

The monitor exposes metrics in Prometheus format on the configured port (default: 8000):

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'machinenativenops-auto-monitor'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

## Systemd Service

The package includes a system wrapper suitable for systemd service:

```ini
# /etc/systemd/system/machinenativenops-auto-monitor.service
[Unit]
Description=MachineNativeOps Auto Monitor
After=network.target

[Service]
Type=simple
User=machinenativenops
Group=machinenativenops
ExecStart=/usr/bin/machinenativenops-auto-monitor serve
Restart=always
RestartSec=10
Environment=MNO_LOG_LEVEL=INFO

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable machinenativenops-auto-monitor
sudo systemctl start machinenativenops-auto-monitor
sudo systemctl status machinenativenops-auto-monitor
```

## Kubernetes Deployment

The monitor can be deployed as a Kubernetes Deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: machinenativenops-auto-monitor
  namespace: machinenativenops-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: machinenativenops-auto-monitor
  template:
    metadata:
      labels:
        app: machinenativenops-auto-monitor
    spec:
      serviceAccountName: machinenativenops-auto-monitor
      containers:
      - name: monitor
        image: machinenativenops/auto-monitor:v2.0.0
        ports:
        - containerPort: 8000
          name: metrics
        env:
        - name: MNO_LOG_LEVEL
          value: "INFO"
        - name: QUANTUM_ENABLED
          value: "false"
        volumeMounts:
        - name: data
          mountPath: /var/lib/machinenativenops/auto_monitor
        - name: config
          mountPath: /etc/machinenativenops
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: machinenativenops-auto-monitor-data
      - name: config
        configMap:
          name: machinenativenops-auto-monitor-config
```

## Configuration Reference

### Monitoring Configuration

```yaml
monitoring:
  interval: 30                    # Collection interval in seconds
  prometheus_port: 8000           # Prometheus metrics port
  health_check_timeout: 5         # Health check timeout
  cpu_threshold: 80.0             # CPU alert threshold (%)
  memory_threshold: 85.0          # Memory alert threshold (%)
  disk_threshold: 90.0            # Disk alert threshold (%)
  api_response_threshold: 2000.0  # API response time threshold (ms)
```

### Quantum Configuration

```yaml
quantum:
  enabled: false                  # Enable quantum monitoring
  fidelity_threshold: 0.94        # Quantum fidelity threshold
  coherence_time_threshold: 100.0 # Coherence time threshold (μs)
  error_rate_threshold: 0.01      # Quantum error rate threshold
  services: {}                    # Quantum service endpoints
```

### Auto-Repair Configuration

```yaml
auto_repair:
  enabled: false                  # Enable auto-repair (Phase 1: disabled)
  max_repair_attempts: 3          # Max repair attempts
  cooldown_period: 300            # Cooldown period (seconds)
  strategies: []                  # Repair strategies
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=machinenativenops_auto_monitor --cov-report=html
```

### Code Quality

```bash
# Format code
black src/
ruff check src/ --fix

# Type checking
mypy src/
```

### Building Package

```bash
# Build wheel
python -m build

# Build in development mode
pip install -e .
```

## Architecture

The monitor follows a modular architecture:

- **Main Application** (`app.py`): Core monitoring logic and FastAPI server
- **Collectors** (`collectors.py`): System, quantum, and Kubernetes metrics collection
- **Storage** (`storage.py`): SQLite database management
- **Alerts** (`alerts.py`): Alert management and auto-repair
- **Configuration** (`config.py`): Configuration management with Pydantic
- **CLI** (`__main__.py`): Command-line interface

## Security Considerations

- **No Auto-Installation**: Dependencies are handled at build time
- **Network Security**: No external connections by default
- **File Permissions**: Proper file permissions for data directories
- **RBAC**: Minimal Kubernetes permissions required
- **SSL/TLS**: Secure configuration for network communications

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure proper file permissions
2. **Database Locked**: Check for other running instances
3. **Port Already in Use**: Change prometheus_port in configuration
4. **Kubernetes Access**: Verify RBAC permissions

### Debug Mode

```bash
# Enable debug logging
machinenativenops-auto-monitor serve --log-level DEBUG

# Or via environment
MNO_LOG_LEVEL=DEBUG machinenativenops-auto-monitor serve
```

### Logs

```bash
# View system logs (systemd)
journalctl -u machinenativenops-auto-monitor -f

# View application logs
tail -f /var/log/machinenativenops/monitor.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Architecture Hash

`e7f8a9b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9`

## Support

- Documentation: https://docs.machinenativenops.io
- Issues: https://github.com/MachineNativeOps/machine-native-ops-aaps/issues
- Community: https://github.com/MachineNativeOps/machine-native-ops-aaps/discussions