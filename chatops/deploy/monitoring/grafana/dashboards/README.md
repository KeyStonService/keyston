# Grafana Dashboards

## 概述

ChatOps Platform 的 Grafana 監控儀表板集合。

## 儀表板列表

| Dashboard | UID | 描述 |
|-----------|-----|------|
| [Platform Overview](chatops-overview.json) | `chatops-overview` | 整體平台健康和服務狀態 |
| [SRE Golden Signals](sre-golden-signals.json) | `chatops-golden-signals` | SRE 四個黃金信號監控 |

## SRE Golden Signals

基於 Google SRE 的四個黃金信號:

### 1. Latency (延遲)
- P50/P90/P95/P99 請求延遲
- 按端點分組的延遲
- 延遲分布直方圖

### 2. Traffic (流量)
- 每秒請求數 (RPS)
- 按服務/狀態碼分組
- 流量趨勢

### 3. Errors (錯誤)
- 錯誤率 (5xx/總請求)
- 按服務分組的錯誤
- 錯誤類型分布

### 4. Saturation (飽和度)
- CPU 使用率
- 內存使用率
- 連接池使用率

## 安裝方式

### 方式 1: Grafana Provisioning

將儀表板文件放入 Grafana provisioning 目錄:

```yaml
# /etc/grafana/provisioning/dashboards/chatops.yaml
apiVersion: 1
providers:
  - name: ChatOps
    orgId: 1
    folder: ChatOps
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /var/lib/grafana/dashboards/chatops
```

### 方式 2: Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboards-chatops
  labels:
    grafana_dashboard: "1"
data:
  chatops-overview.json: |
    { ... }
  sre-golden-signals.json: |
    { ... }
```

### 方式 3: API 導入

```bash
# 使用 Grafana API
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $GRAFANA_TOKEN" \
  -d @sre-golden-signals.json \
  http://grafana:3000/api/dashboards/db
```

## 依賴

### 數據源

- **Prometheus**: 主要指標數據源
  - 需要配置 ServiceMonitor 或 PodMonitor
  - 指標來自應用程序和 kube-state-metrics

### 必要指標

```
# HTTP 請求指標
http_requests_total
http_request_duration_seconds_bucket

# Kubernetes 指標
kube_deployment_status_replicas_ready
kube_pod_container_status_restarts_total
container_cpu_usage_seconds_total
container_memory_working_set_bytes

# 應用程序指標
message_processed_total
message_processing_duration_seconds_bucket
queue_messages_pending

# 數據庫指標
pg_up
pg_stat_activity_count
pg_settings_max_connections

# Redis 指標
redis_up
redis_keyspace_hits_total
redis_keyspace_misses_total
redis_memory_used_bytes
```

## 自定義

### 修改閾值

編輯 JSON 文件中的 `thresholds` 部分:

```json
"thresholds": {
  "mode": "absolute",
  "steps": [
    { "color": "green", "value": null },
    { "color": "yellow", "value": 70 },
    { "color": "red", "value": 85 }
  ]
}
```

### 添加告警

使用 Grafana UI 或在 JSON 中添加 alert 規則:

```json
"alert": {
  "name": "High Error Rate",
  "conditions": [
    {
      "evaluator": { "params": [1], "type": "gt" },
      "operator": { "type": "and" },
      "query": { "params": ["A", "5m", "now"] },
      "reducer": { "params": [], "type": "avg" },
      "type": "query"
    }
  ],
  "frequency": "1m",
  "handler": 1,
  "noDataState": "no_data",
  "notifications": []
}
```

## 相關資源

- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Guide](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [SRE Book - Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)
