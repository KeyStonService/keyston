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
