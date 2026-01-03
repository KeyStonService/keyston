# MachineNativeOps Auto-Monitor

自動監控和可觀測性系統 / Autonomous Monitoring and Observability System

## 概述 / Overview

MachineNativeOps Auto-Monitor 是一個自主監控系統，為 MachineNativeOps 平台提供：

- 系統級指標收集（CPU、記憶體、磁碟、網路）
- 服務健康監控
- 自動告警管理
- 時間序列數據儲存

MachineNativeOps Auto-Monitor is an autonomous monitoring system that provides:

- System-level metrics collection (CPU, memory, disk, network)
- Service health monitoring
- Automated alert management
- Time-series data storage

## 功能特性 / Features

### 指標收集 / Metrics Collection

- **系統指標** / System Metrics: CPU、記憶體、磁碟、網路統計
- **服務指標** / Service Metrics: 健康檢查、響應時間、自定義指標
- **自定義收集器** / Custom Collectors: 支援自定義數據源

### 告警管理 / Alert Management

- 基於規則的告警評估
- 多種嚴重級別（Critical、Error、Warning、Info）
- 告警歷史記錄
- 通知發送（可擴展）

### 數據儲存 / Data Storage

- SQLite 時間序列儲存
- 自動數據清理
- 查詢和分析支援

## 安裝 / Installation

```bash
cd engine/machinenativenops-auto-monitor
pip install -e .
```

## 使用方法 / Usage

### 命令行模式 / Command-line Mode

```bash
# 使用默認配置 / Use default configuration
python -m machinenativenops_auto_monitor

# 指定配置文件 / Specify configuration file
python -m machinenativenops_auto_monitor --config /etc/machinenativeops/auto-monitor.yaml

# 詳細輸出模式 / Verbose mode
python -m machinenativenops_auto_monitor --verbose

# 試運行模式（不發送告警或儲存數據）/ Dry-run mode
python -m machinenativenops_auto_monitor --dry-run

# 守護進程模式 / Daemon mode
python -m machinenativenops_auto_monitor --daemon
```

### Python API

```python
from machinenativenops_auto_monitor import AutoMonitorApp, AutoMonitorConfig

# 創建配置 / Create configuration
config = AutoMonitorConfig.default()
config.collection_interval = 60
config.namespace = "machinenativeops"

# 創建應用 / Create application
app = AutoMonitorApp(config)

# 運行監控 / Run monitoring
app.run()

# 或作為守護進程 / Or as daemon
app.run_daemon()
```

## 配置 / Configuration

配置文件示例 / Example configuration file:

```yaml
namespace: machinenativeops
version: 1.0.0
collection_interval: 30  # seconds

collectors:
  system:
    enabled: true
  
  service:
    enabled: true
    timeout: 5
    services:
      - name: api-gateway
        health_url: http://localhost:8080/health
        metrics_url: http://localhost:8080/metrics

alerts:
  enabled: true
  rules:
    - name: high_cpu_usage
      description: CPU usage is too high
      severity: warning
      condition: ">"
      threshold: 80.0
      duration: 60
    
    - name: low_disk_space
      description: Disk space is running low
      severity: critical
      condition: ">"
      threshold: 90.0
      duration: 300

storage:
  enabled: true
  backend: timeseries
  path: /var/lib/machinenativeops/metrics/metrics.db
  retention_days: 30

log_level: INFO
```

## 架構 / Architecture

```
machinenativenops_auto_monitor/
├── __init__.py          # 模組入口 / Module entry point
├── __main__.py          # CLI 入口 / CLI entry point
├── app.py               # 主應用程式 / Main application
├── config.py            # 配置管理 / Configuration management
├── collectors.py        # 指標收集器 / Metrics collectors
├── alerts.py            # 告警管理 / Alert management
└── 儲存.py              # 儲存管理 / Storage management
```

## 命名空間對齊 / Namespace Alignment

本模組完全對齊 MachineNativeOps 命名空間標準：

- 命名空間: `machinenativeops`
- API 版本: `machinenativeops.io/v1`
- 註冊表: `registry.machinenativeops.io`
- 配置路徑: `/etc/machinenativeops/`
- 證書路徑: `/etc/machinenativeops/pkl/`
- ETCD 集群: `super-agent-etcd-cluster`

This module fully aligns with MachineNativeOps namespace standards.

## 依賴 / Dependencies

- Python 3.8+
- psutil (系統指標收集 / system metrics collection)
- requests (服務監控 / service monitoring)
- PyYAML (配置管理 / configuration management)

## 開發 / Development

```bash
# 安裝開發依賴 / Install dev dependencies
pip install -e ".[dev]"

# 運行測試 / Run tests
pytest

# 代碼檢查 / Code linting
flake8 src/
```

## 授權 / License

Copyright © 2025 MachineNativeOps Platform Team
機器原生運維自動監控系統 (MachineNativeOps Auto-Monitor System)

## 📋 概述 (Overview)

The MachineNativeOps Auto-Monitor is an automated monitoring solution designed for machine-native operations infrastructure. It provides real-time metrics collection, log aggregation, event tracking, and intelligent alerting.

MachineNativeOps 自動監控是為機器原生運維基礎設施設計的自動監控解決方案。它提供實時指標收集、日誌聚合、事件追蹤和智能警報功能。

## 🎯 Features (特性)

- **📊 Metrics Collection**: System and application metrics collection
- **📝 Log Aggregation**: Centralized log collection and storage
- **🔔 Alert Management**: Intelligent alerting based on customizable rules
- **📈 Event Tracking**: System event detection and recording
- **💾 Flexible Storage**: Multiple storage backends (memory, file, database)
- **🚀 Async Operations**: Efficient async data collection

## 🚀 Quick Start (快速開始)

### Installation (安裝)

```bash
# Install dependencies
pip install -r requirements.txt

# Or install with optional features
pip install -r requirements.txt -r requirements-optional.txt
```

### Basic Usage (基本使用)

```bash
# Start with default configuration
python -m machinenativenops_auto_monitor

# Start with custom config
python -m machinenativenops_auto_monitor --config config.yaml

# Start in production mode
python -m machinenativenops_auto_monitor --mode production
```

### Configuration (配置)

Create a `config.yaml` file:

```yaml
# Application settings
mode: production
port: 8080
host: 0.0.0.0

# Collection intervals (seconds)
collection_interval: 10
log_collection_interval: 5
event_collection_interval: 15

# Storage settings
storage_backend: file
storage_path: /var/lib/machinenativeops/monitor
retention_days: 7

# Alert settings
enable_alerts: true
alert_channels:
  - type: webhook
    url: https://alerts.example.com/webhook

# Namespace configuration
namespace: machinenativeops
registry: registry.machinenativeops.io
certificate_path: etc/machinenativeops/pkl
cluster_token: super-agent-etcd-cluster
```

## 📁 Project Structure (項目結構)

```
machinenativenops-auto-monitor/
├── src/
│   └── machinenativenops_auto_monitor/
│       ├── __init__.py          # Package initialization
│       ├── __main__.py          # CLI entry point
│       ├── app.py               # Main application logic
│       ├── alerts.py            # Alert management
│       ├── collectors.py        # Data collectors
│       ├── config.py            # Configuration management
│       └── 儲存.py              # Storage backends
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

## 🔧 Architecture (架構)

### Components (組件)

1. **MetricsCollector** (指標收集器)
   - Collects system metrics (CPU, memory, disk, network)
   - Supports process-level metrics
   - Extensible for custom metrics

2. **LogCollector** (日誌收集器)
   - Aggregates logs from multiple sources
   - Supports structured logging
   - Buffered collection for efficiency

3. **EventCollector** (事件收集器)
   - Detects and records system events
   - Auto-detection of anomalies
   - Custom event support

4. **AlertManager** (警報管理器)
   - Rule-based alerting
   - Multiple severity levels
   - Alert routing and handling

5. **StorageBackend** (儲存後端)
   - In-memory storage for development
   - File-based storage for production
   - Database support (optional)

### Data Flow (數據流)

```
Collectors → Storage Backend → Alert Manager → Handlers
    ↓             ↓                 ↓             ↓
 Metrics        Logs             Alerts      Notifications
 Events     Persistence         Rules       Actions
```

## 📊 Metrics Collected (收集的指標)

- **System Metrics** (系統指標)
  - CPU usage percentage
  - Memory usage and availability
  - Disk usage and space
  - Network I/O statistics
  - Process count

- **Process Metrics** (進程指標)
  - Per-process CPU usage
  - Per-process memory usage
  - Thread count
  - Process status

## 🔔 Default Alert Rules (默認警報規則)

1. **high_cpu_usage**: Triggers when CPU > 80%
2. **high_memory_usage**: Triggers when memory > 85%
3. **disk_space_low**: Triggers when disk > 90%
4. **service_down**: Triggers when service health check fails

## 🛠️ Development (開發)

### Adding Custom Collectors (添加自定義收集器)

```python
from machinenativenops_auto_monitor.collectors import MetricsCollector

class CustomCollector(MetricsCollector):
    def collect(self):
        metrics = super().collect()
        metrics['custom_metric'] = self.get_custom_value()
        return metrics
```

### Adding Custom Alert Rules (添加自定義警報規則)

```python
from machinenativenops_auto_monitor.alerts import AlertRule, AlertSeverity

rule = AlertRule(
    name="custom_rule",
    condition=lambda m: m.get('custom_metric', 0) > 100,
    severity=AlertSeverity.WARNING,
    message_template="Custom metric exceeded: {custom_metric}",
)

alert_manager.add_rule(rule)
```

## 🧪 Testing (測試)

```bash
# Run in development mode with verbose logging
python -m machinenativenops_auto_monitor --mode development --verbose

# Check metrics collection
curl http://localhost:8080/metrics

# Check active alerts
curl http://localhost:8080/alerts
```

## 📝 License (許可證)

Copyright © 2024 MachineNativeOps

## 🤝 Contributing (貢獻)

Contributions are welcome! Please follow the MachineNativeOps contribution guidelines.

## 📞 Support (支持)

For issues and questions, please refer to the MachineNativeOps documentation or open an issue in the main repository.

---

**Namespace Alignment (命名空間對齊)**

This module follows MachineNativeOps namespace standards:

- Domain: `machinenativeops.io`
- Namespace: `machinenativeops`
- Registry: `registry.machinenativeops.io`
- Certificate Path: `etc/machinenativeops/pkl`
- Cluster Token: `super-agent-etcd-cluster`

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
git clone https://github.com/MachineNativeOps/machine-native-ops-machine-native-ops.git
cd machine-native-ops-machine-native-ops/engine/machinenativenops-auto-monitor

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

- Documentation: <https://docs.machinenativenops.io>
- Issues: <https://github.com/MachineNativeOps/machine-native-ops-machine-native-ops/issues>
- Community: <https://github.com/MachineNativeOps/machine-native-ops-machine-native-ops/discussions>
