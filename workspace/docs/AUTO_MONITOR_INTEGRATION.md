# Auto-Monitor Integration Guide

## Overview

The MachineNativeOps Auto-Monitor is a production-ready monitoring solution integrated into the MachineNativeOps (AI Architecture & Artifact Provisioning System) architecture. It provides comprehensive system monitoring, quantum state tracking, and integration with the unified gates workflow.

## Architecture Integration

### Module Registration

The Auto-Monitor is registered in `root.modules.yaml` as a core monitoring module:

```yaml
- name: machinenativenops-auto-monitor
  version: 2.0.0
  description: Production-ready auto-monitoring with quantum state tracking
  entrypoint: /usr/bin/machinenativenops-auto-monitor
  group: monitoring
  priority: 55
  enabled: true
  auto_start: true
```

### Dependencies

The Auto-Monitor depends on the following MachineNativeOps modules:

1. **config-manager** (>=1.0.0) - Configuration management
2. **logging-service** (>=1.0.0) - Centralized logging
3. **database-connector** (>=1.0.0) - Database connectivity

### Load Sequence

The Auto-Monitor is loaded in **Stage 2** of the module load sequence, alongside other supporting services:

```
Stage 0: config-manager
Stage 1: logging-service, database-connector, etc.
Stage 2: machinenativenops-auto-monitor ← HERE
Stage 3: governance-engine, trust-manager
Stage 4: provenance-tracker, integrity-validator
Stage 5: super-execution-engine
```

## Resource Allocation

### CPU Resources

- **Request**: 200m (0.2 CPU cores)
- **Limit**: 1000m (1.0 CPU core)

### Memory Resources

- **Request**: 256Mi
- **Limit**: 1Gi

### Storage Resources

- **Request**: 500Mi
- **Limit**: 5Gi

## Configuration

### Environment Variables

The Auto-Monitor is configured through the following environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `MNO_PROMETHEUS_PORT` | `8000` | Prometheus metrics exposition port |
| `MNO_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARN, ERROR) |
| `QUANTUM_ENABLED` | `false` | Enable quantum state monitoring |
| `AUTO_REPAIR_ENABLED` | `false` | Enable auto-repair capabilities (Phase 1: disabled) |
| `MNO_DATABASE_PATH` | `/var/lib/machinenativenops/auto_monitor/metrics.db` | SQLite database path |

### Configuration File

The Auto-Monitor can also be configured via YAML file at:

- `/etc/machinenativenops/monitor_config.yaml` (system-wide)
- Custom path via `MNO_CONFIG_FILE` environment variable

## Integration with Unified Gates

### Workflow Integration

The Auto-Monitor is integrated into the MachineNativeOps Unified Gates workflow (`.github/workflows/machine-native-ops-unified-gates.yml`):

```yaml
- name: Setup MachineNativeOps Environment
  run: |
    # Install Auto-Monitor dependencies
    pip install -r engine/machinenativenops-auto-monitor/requirements.txt
    
    # Start Auto-Monitor in background
    machinenativenops-auto-monitor serve &
    MONITOR_PID=$!
    
    # Wait for service to be ready
    sleep 15

- name: Execute SuperAgent Gate Orchestration
  run: |
    # Check Auto-Monitor is running
    curl -f http://localhost:8000/health || exit 1
```

### Metrics Collection

During gate validation, the workflow collects metrics from the Auto-Monitor:

```yaml
- name: Collect Monitoring Metrics
  run: |
    # Get Prometheus metrics
    curl -X GET http://localhost:8000/metrics --fail | tee gate_metrics.txt
    
    # Get system status
    curl -X GET http://localhost:8000/status --fail | tee system_status.txt
```

### Gate Report Integration

Auto-Monitor metrics are included in the comprehensive gate validation report:

```markdown
## System Metrics
### Auto-Monitor Metrics
```

$(cat gate_metrics.txt)

```

### System Status
```

$(cat system_status.txt)

```
```

## Health Checks

### Endpoint Configuration

The Auto-Monitor provides a health check endpoint:

```yaml
health_check:
  endpoint: /health
  interval: 30s
  timeout: 10s
  retries: 3
```

### Health Check Response

```json
{
  "status": "healthy",
  "timestamp": "2025-12-21T10:30:00Z",
  "uptime": 3600,
  "version": "2.0.0",
  "services": {
    "database": "healthy",
    "prometheus": "healthy",
    "collectors": "healthy"
  }
}
```

## API Endpoints

The Auto-Monitor exposes the following HTTP endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check status |
| `/metrics` | GET | Prometheus metrics |
| `/status` | GET | Detailed service status |
| `/api/v1/metrics` | GET | Recent metrics (JSON) |
| `/api/v1/alerts` | GET | Active alerts |
| `/docs` | GET | FastAPI documentation |

## Monitoring Capabilities

### System Metrics

The Auto-Monitor collects the following system metrics:

- **CPU Usage**: Per-core and aggregate CPU utilization
- **Memory Usage**: RAM usage, swap usage, available memory
- **Disk Usage**: Disk space utilization per mount point
- **Network I/O**: Network traffic statistics

### Quantum Metrics (Optional)

When `QUANTUM_ENABLED=true`:

- **Quantum Fidelity**: Quantum state fidelity measurements
- **Coherence Time**: Quantum coherence time tracking
- **Error Rate**: Quantum error rate monitoring

### Kubernetes Metrics (Optional)

When running in Kubernetes:

- **Pod Status**: Pod health and readiness
- **Service Status**: Service availability
- **Resource Usage**: Container resource utilization

## Alert Management

### Threshold Configuration

Default alert thresholds:

```yaml
monitoring:
  cpu_threshold: 80.0          # CPU alert at 80%
  memory_threshold: 85.0       # Memory alert at 85%
  disk_threshold: 90.0         # Disk alert at 90%
  api_response_threshold: 2000.0  # API response time > 2000ms
```

### Alert Actions

When thresholds are exceeded:

1. **Log Alert**: Alert is logged to the logging service
2. **Metrics Update**: Alert counter is incremented
3. **Notification**: (Optional) Send notification via configured channels
4. **Auto-Repair**: (Phase 2) Trigger auto-repair if enabled

## Deployment Scenarios

### Standalone Deployment

```bash
# Install the package
pip install machinenativenops-auto-monitor

# Run the service
machinenativenops-auto-monitor serve
```

### Systemd Service

```ini
[Unit]
Description=MachineNativeOps Auto Monitor
After=network.target

[Service]
Type=simple
User=machinenativenops
ExecStart=/usr/bin/machinenativenops-auto-monitor serve
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: machinenativenops-auto-monitor
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: monitor
        image: machinenativenops/auto-monitor:v2.0.0
        ports:
        - containerPort: 8000
          name: metrics
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

### Docker Compose

```yaml
services:
  auto-monitor:
    image: machinenativenops/auto-monitor:v2.0.0
    ports:
      - "8000:8000"
    environment:
      - MNO_LOG_LEVEL=INFO
      - QUANTUM_ENABLED=false
    volumes:
      - monitor-data:/var/lib/machinenativenops/auto_monitor
```

## Prometheus Integration

### Scrape Configuration

Add the Auto-Monitor to your Prometheus configuration:

```yaml
scrape_configs:
  - job_name: 'machinenativenops-auto-monitor'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

### Available Metrics

The Auto-Monitor exposes the following Prometheus metrics:

- `mno_cpu_usage_percent` - CPU usage percentage
- `mno_memory_usage_bytes` - Memory usage in bytes
- `mno_disk_usage_percent` - Disk usage percentage
- `mno_network_bytes_sent` - Network bytes sent
- `mno_network_bytes_recv` - Network bytes received
- `mno_alert_count` - Number of active alerts
- `mno_uptime_seconds` - Service uptime in seconds

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Change the port
export MNO_PROMETHEUS_PORT=8001
machinenativenops-auto-monitor serve
```

#### Database Locked

```bash
# Check for other running instances
ps aux | grep machinenativenops-auto-monitor

# Kill stale processes
pkill -f machinenativenops-auto-monitor
```

#### Permission Denied

```bash
# Ensure proper permissions
sudo chown -R machinenativenops:machinenativenops /var/lib/machinenativenops/auto_monitor
sudo chmod 755 /var/lib/machinenativenops/auto_monitor
```

### Debug Mode

Enable debug logging for troubleshooting:

```bash
# Via environment variable
MNO_LOG_LEVEL=DEBUG machinenativenops-auto-monitor serve

# Via command line
machinenativenops-auto-monitor serve --log-level DEBUG
```

### Logs

View logs:

```bash
# Systemd logs
journalctl -u machinenativenops-auto-monitor -f

# Application logs
tail -f /var/log/machinenativenops/monitor.log
```

## Performance Considerations

### Resource Usage

Typical resource usage:

- **CPU**: 5-10% under normal load
- **Memory**: 100-200 MB
- **Disk I/O**: Minimal (periodic database writes)
- **Network**: Low (metrics exposition only)

### Scaling

For high-load environments:

1. **Increase Collection Interval**: Reduce metric collection frequency
2. **Database Optimization**: Use external database instead of SQLite
3. **Horizontal Scaling**: Deploy multiple instances with load balancing
4. **Metric Aggregation**: Use Prometheus for long-term storage

## Security Considerations

### Network Security

- Auto-Monitor listens on localhost by default
- Use reverse proxy (nginx, traefik) for external access
- Enable TLS/SSL for production deployments

### File Permissions

- Database files: 0600 (owner read/write only)
- Configuration files: 0644 (owner read/write, others read)
- Log files: 0644 (owner read/write, others read)

### RBAC (Kubernetes)

Minimal required permissions:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: machinenativenops-auto-monitor
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]
```

## Future Enhancements

### Phase 2 Features

- **Auto-Repair**: Automated issue remediation
- **Predictive Alerts**: ML-based anomaly detection
- **Advanced Quantum Monitoring**: Enhanced quantum state tracking
- **Multi-Cluster Support**: Cross-cluster monitoring
- **Custom Collectors**: Plugin system for custom metrics

### Roadmap

- Q1 2025: Auto-repair capabilities
- Q2 2025: Predictive alerting
- Q3 2025: Multi-cluster support
- Q4 2025: Plugin system

## Support

- **Documentation**: <https://docs.machinenativenops.io>
- **Issues**: <https://github.com/MachineNativeOps/machine-native-ops-machine-native-ops/issues>
- **Community**: <https://github.com/MachineNativeOps/machine-native-ops-machine-native-ops/discussions>

## References

- [Auto-Monitor README](../engine/machinenativenops-auto-monitor/README.md)
- [MachineNativeOps Unified Gates Workflow](../.github/workflows/machine-native-ops-unified-gates.yml)
- [Root Modules Configuration](../root.modules.yaml)
- [SuperAgent Integration](../agents/super-agent/README.md)
