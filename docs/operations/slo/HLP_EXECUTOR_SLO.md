# HLP Executor 服務等級目標 | HLP Executor Service Level Objectives (SLO)

**文件版本 | Document Version**: 1.0.0  
**最後更新 | Last Updated**: 2025-12-07  
**負責團隊 | Responsible Team**: Platform Engineering / SRE  
**審核週期 | Review Cycle**: Quarterly

---

## 📋 文件目的 | Document Purpose

本文件定義 HLP Executor Core
Plugin 的服務等級目標 (SLO)，包含關鍵性能指標、測量方法和合規監控策略。

This document defines Service Level Objectives (SLO) for the HLP Executor Core
Plugin, including key performance metrics, measurement methods, and compliance
monitoring strategies.

---

## 🎯 SLO 概覽 | SLO Overview

### SLO 層級 | SLO Tiers

HLP Executor 的 SLO 分為三個層級，確保全面的服務質量保證：

HLP Executor SLOs are organized into three tiers to ensure comprehensive service
quality assurance:

| 層級       | 類別           | 重要性   | 影響範圍     |
| ---------- | -------------- | -------- | ------------ |
| **Tier 1** | 可用性與可靠性 | Critical | 服務整體運行 |
| **Tier 2** | 性能與延遲     | High     | 用戶體驗     |
| **Tier 3** | 容量與效率     | Medium   | 資源優化     |

---

## 📊 Tier 1: 可用性與可靠性 SLO | Availability and Reliability SLO

### 1.1 服務可用性 | Service Availability

#### 目標 | Objective

```yaml
slo_name: hlp_executor_availability
target: 99.9%
measurement_window: 30 days
calculation_method: uptime / total_time
```

#### 定義 | Definition

服務可用性定義為 HLP Executor 能夠接受和處理請求的時間百分比。

Service availability is defined as the percentage of time the HLP Executor is
able to accept and process requests.

#### 測量方法 | Measurement Method

**Prometheus Query**:

```promql
# 30天可用性 | 30-day availability
(
  sum(up{job="hlp-executor-core"} == 1)
  /
  count(up{job="hlp-executor-core"})
) * 100

# 或使用 SLI (Service Level Indicator)
100 * (
  1 - (
    sum(rate(hlp_executor_requests_total{status=~"5.."}[30d]))
    /
    sum(rate(hlp_executor_requests_total[30d]))
  )
)
```

**監控配置 | Monitoring Configuration**:

```yaml
# prometheus-rules.yml
groups:
  - name: hlp_executor_availability
    interval: 1m
    rules:
      - record: hlp_executor:availability:30d
        expr: |
          100 * (
            1 - (
              sum(rate(hlp_executor_requests_total{status=~"5.."}[30d]))
              /
              sum(rate(hlp_executor_requests_total[30d]))
            )
          )

      - alert: HLPExecutorAvailabilitySLOViolation
        expr: hlp_executor:availability:30d < 99.9
        for: 5m
        labels:
          severity: critical
          slo_tier: tier1
        annotations:
          summary: 'HLP Executor availability SLO violation'
          description: 'Availability is {{ $value }}%, below 99.9% target'
          dashboard: 'https://grafana/d/hlp-executor-slo'
```

#### 排除情況 | Exclusions

以下情況不計入可用性計算：

- 計劃性維護窗口 (每週二 02:00-04:00 UTC)
- 上游依賴完全故障 (Kubernetes API Server 完全不可用)
- 災難性基礎設施故障 (整個 region 故障)

The following are excluded from availability calculation:

- Scheduled maintenance windows (Weekly Tuesday 02:00-04:00 UTC)
- Complete upstream dependency failures (Kubernetes API Server completely
  unavailable)
- Catastrophic infrastructure failures (Entire region down)

#### 錯誤預算 | Error Budget

```yaml
error_budget:
  monthly: 43.2 minutes # (30 days * 24 hours * 60 min) * 0.1%
  daily: 1.44 minutes # 24 hours * 60 min * 0.1%
  weekly: 10.08 minutes # 7 days * 24 hours * 60 min * 0.1%

  alerting_thresholds:
    - consumed: 25%
      action: notify_team
    - consumed: 50%
      action: escalate_to_lead
    - consumed: 75%
      action: freeze_non_critical_changes
    - consumed: 90%
      action: emergency_response
```

---

### 1.2 恢復時間目標 | Recovery Time Objective (RTO)

#### 目標 | Objective

```yaml
slo_name: hlp_executor_rto
target: < 30 seconds
measurement_window: per incident
calculation_method: time_to_restore_service
severity: P1
```

#### 定義 | Definition

RTO 是指從檢測到服務中斷到服務完全恢復的最大允許時間。

RTO is the maximum acceptable time from service outage detection to full service
restoration.

#### 測量方法 | Measurement Method

**Prometheus Query**:

```promql
# 平均恢復時間 | Average recovery time
avg(hlp_executor_recovery_duration_seconds)

# P95 恢復時間 | P95 recovery time
histogram_quantile(0.95,
  rate(hlp_executor_recovery_duration_seconds_bucket[30d])
)
```

**監控配置 | Monitoring Configuration**:

```yaml
groups:
  - name: hlp_executor_rto
    interval: 30s
    rules:
      - alert: HLPExecutorRTOSLOViolation
        expr: hlp_executor_recovery_duration_seconds > 30
        for: 1m
        labels:
          severity: critical
          slo_tier: tier1
        annotations:
          summary: 'HLP Executor RTO SLO violation'
          description: 'Recovery took {{ $value }}s, exceeding 30s target'
```

#### RTO 分層 | RTO by Severity

| 嚴重性        | RTO 目標     | 測量方法           |
| ------------- | ------------ | ------------------ |
| P1 - Critical | < 30 seconds | 自動檢測到服務恢復 |
| P2 - High     | < 5 minutes  | 自動檢測到服務恢復 |
| P3 - Medium   | < 30 minutes | 手動確認到服務恢復 |
| P4 - Low      | < 2 hours    | 手動確認到服務恢復 |

---

### 1.3 恢復點目標 | Recovery Point Objective (RPO)

#### 目標 | Objective

```yaml
slo_name: hlp_executor_rpo
target: < 5 minutes
measurement_window: per incident
calculation_method: data_loss_window
```

#### 定義 | Definition

RPO 是指在災難恢復場景中，可接受的最大數據遺失時間窗口。

RPO is the maximum acceptable time window of data loss in disaster recovery
scenarios.

#### 測量方法 | Measurement Method

**實現機制 | Implementation**:

- Checkpoint 頻率: 每 60 秒 | Checkpoint frequency: Every 60 seconds
- 增量快照: 每 5 分鐘 | Incremental snapshots: Every 5 minutes
- 完整快照: 每 1 小時 | Full snapshots: Every 1 hour

**驗證查詢 | Verification Query**:

```promql
# 最近 checkpoint 時間 | Time since last checkpoint
time() - hlp_executor_last_checkpoint_timestamp_seconds < 300
```

---

## 🚀 Tier 2: 性能與延遲 SLO | Performance and Latency SLO

### 2.1 DAG 解析延遲 | DAG Parsing Latency

#### 目標 | Objective

```yaml
slo_name: hlp_executor_dag_parsing_latency
target: P95 < 120ms
measurement_window: 7 days
calculation_method: histogram_quantile
```

#### 定義 | Definition

DAG 解析延遲是指從接收 DAG 定義到解析完成並準備執行的時間。

DAG parsing latency is the time from receiving a DAG definition to parsing
completion and readiness for execution.

#### 測量方法 | Measurement Method

**Prometheus Query**:

```promql
# P50, P90, P95, P99 延遲 | P50, P90, P95, P99 latencies
histogram_quantile(0.50,
  rate(hlp_executor_dag_parsing_duration_seconds_bucket[7d])
)

histogram_quantile(0.95,
  rate(hlp_executor_dag_parsing_duration_seconds_bucket[7d])
)
```

**監控配置 | Monitoring Configuration**:

```yaml
groups:
  - name: hlp_executor_dag_parsing_latency
    interval: 1m
    rules:
      - record: hlp_executor:dag_parsing_latency:p95:7d
        expr: |
          histogram_quantile(0.95, 
            rate(hlp_executor_dag_parsing_duration_seconds_bucket[7d])
          )

      - alert: HLPExecutorDAGParsingLatencySLOViolation
        expr: hlp_executor:dag_parsing_latency:p95:7d > 0.120
        for: 10m
        labels:
          severity: warning
          slo_tier: tier2
        annotations:
          summary: 'HLP Executor DAG parsing latency SLO violation'
          description: 'P95 latency is {{ $value }}s, exceeding 120ms target'
```

#### 性能基準 | Performance Benchmarks

| 百分位 | 目標    | 當前   | 狀態    |
| ------ | ------- | ------ | ------- |
| P50    | < 50ms  | ~35ms  | ✅ 達標 |
| P90    | < 100ms | ~85ms  | ✅ 達標 |
| P95    | < 120ms | ~110ms | ✅ 達標 |
| P99    | < 200ms | ~180ms | ✅ 達標 |

---

### 2.2 狀態轉換延遲 | State Transition Latency

#### 目標 | Objective

```yaml
slo_name: hlp_executor_state_transition_latency
target: P90 < 50ms
measurement_window: 7 days
calculation_method: histogram_quantile
```

#### 定義 | Definition

狀態轉換延遲是指執行從一個狀態轉換到下一個狀態所需的時間，包括驗證和持久化。

State transition latency is the time required for an execution to transition
from one state to the next, including validation and persistence.

#### 測量方法 | Measurement Method

**Prometheus Query**:

```promql
# P90 狀態轉換延遲 | P90 state transition latency
histogram_quantile(0.90,
  rate(hlp_executor_state_transition_duration_seconds_bucket[7d])
)

# 按狀態類型分組 | Grouped by state type
histogram_quantile(0.90,
  sum by (from_state, to_state) (
    rate(hlp_executor_state_transition_duration_seconds_bucket[7d])
  )
)
```

**監控配置 | Monitoring Configuration**:

```yaml
groups:
  - name: hlp_executor_state_transition_latency
    interval: 1m
    rules:
      - record: hlp_executor:state_transition_latency:p90:7d
        expr: |
          histogram_quantile(0.90, 
            rate(hlp_executor_state_transition_duration_seconds_bucket[7d])
          )

      - alert: HLPExecutorStateTransitionLatencySLOViolation
        expr: hlp_executor:state_transition_latency:p90:7d > 0.050
        for: 10m
        labels:
          severity: warning
          slo_tier: tier2
        annotations:
          summary: 'HLP Executor state transition latency SLO violation'
          description: 'P90 latency is {{ $value }}s, exceeding 50ms target'
```

#### 性能基準 | Performance Benchmarks

| 狀態轉換類型        | P90 目標 | P90 當前 |
| ------------------- | -------- | -------- |
| PENDING → RUNNING   | < 50ms   | ~30ms    |
| RUNNING → COMPLETED | < 50ms   | ~40ms    |
| RUNNING → FAILED    | < 50ms   | ~35ms    |
| ANY → ROLLING_BACK  | < 100ms  | ~80ms    |

---

### 2.3 請求處理吞吐量 | Request Processing Throughput

#### 目標 | Objective

```yaml
slo_name: hlp_executor_throughput
target: > 1000 requests/second
measurement_window: 5 minutes
calculation_method: rate
```

#### 定義 | Definition

請求處理吞吐量是指 HLP Executor 每秒可以處理的請求數量。

Request processing throughput is the number of requests HLP Executor can process
per second.

#### 測量方法 | Measurement Method

**Prometheus Query**:

```promql
# 當前吞吐量 (requests/sec) | Current throughput (requests/sec)
sum(rate(hlp_executor_requests_total[5m]))

# 按狀態碼分組 | Grouped by status code
sum by (status) (rate(hlp_executor_requests_total[5m]))
```

**監控配置 | Monitoring Configuration**:

```yaml
groups:
  - name: hlp_executor_throughput
    interval: 1m
    rules:
      - record: hlp_executor:throughput:5m
        expr: sum(rate(hlp_executor_requests_total[5m]))

      - alert: HLPExecutorThroughputSLOViolation
        expr: hlp_executor:throughput:5m < 1000
        for: 5m
        labels:
          severity: warning
          slo_tier: tier2
        annotations:
          summary: 'HLP Executor throughput below SLO'
          description:
            'Current throughput is {{ $value }} req/s, below 1000 req/s target'
```

---

## 💾 Tier 3: 容量與效率 SLO | Capacity and Efficiency SLO

### 3.1 資源利用率 | Resource Utilization

#### 目標 | Objective

```yaml
slo_name: hlp_executor_resource_utilization
targets:
  cpu_utilization: 60-80%
  memory_utilization: 70-85%
  disk_utilization: < 80%
measurement_window: 7 days
```

#### 定義 | Definition

資源利用率目標確保系統運行在最佳效率範圍內，既不浪費資源也不過度負載。

Resource utilization targets ensure the system operates within optimal
efficiency ranges, neither wasting resources nor being overloaded.

#### 測量方法 | Measurement Method

**Prometheus Query**:

```promql
# CPU 利用率 | CPU utilization
avg(
  rate(container_cpu_usage_seconds_total{
    namespace="unmanned-island-system",
    pod=~"hlp-executor-core-.*"
  }[5m])
) * 100

# 記憶體利用率 | Memory utilization
avg(
  container_memory_working_set_bytes{
    namespace="unmanned-island-system",
    pod=~"hlp-executor-core-.*"
  }
  /
  container_spec_memory_limit_bytes{
    namespace="unmanned-island-system",
    pod=~"hlp-executor-core-.*"
  }
) * 100

# 磁碟利用率 | Disk utilization
(
  kubelet_volume_stats_used_bytes{
    namespace="unmanned-island-system",
    persistentvolumeclaim="hlp-executor-state-pvc"
  }
  /
  kubelet_volume_stats_capacity_bytes{
    namespace="unmanned-island-system",
    persistentvolumeclaim="hlp-executor-state-pvc"
  }
) * 100
```

**監控配置 | Monitoring Configuration**:

```yaml
groups:
  - name: hlp_executor_resource_utilization
    interval: 1m
    rules:
      - alert: HLPExecutorCPUOverUtilized
        expr: |
          avg(
            rate(container_cpu_usage_seconds_total{
              namespace="unmanned-island-system",
              pod=~"hlp-executor-core-.*"
            }[5m])
          ) * 100 > 80
        for: 15m
        labels:
          severity: warning
          slo_tier: tier3
        annotations:
          summary: 'HLP Executor CPU over-utilized'
          description:
            'CPU utilization is {{ $value }}%, exceeding 80% threshold'

      - alert: HLPExecutorCPUUnderUtilized
        expr: |
          avg(
            rate(container_cpu_usage_seconds_total{
              namespace="unmanned-island-system",
              pod=~"hlp-executor-core-.*"
            }[5m])
          ) * 100 < 40
        for: 6h
        labels:
          severity: info
          slo_tier: tier3
        annotations:
          summary: 'HLP Executor CPU under-utilized'
          description: 'CPU utilization is {{ $value }}%, consider scaling down'

      - alert: HLPExecutorDiskHighUsage
        expr: |
          (
            kubelet_volume_stats_used_bytes{
              namespace="unmanned-island-system",
              persistentvolumeclaim="hlp-executor-state-pvc"
            }
            /
            kubelet_volume_stats_capacity_bytes{
              namespace="unmanned-island-system",
              persistentvolumeclaim="hlp-executor-state-pvc"
            }
          ) * 100 > 80
        for: 10m
        labels:
          severity: warning
          slo_tier: tier3
        annotations:
          summary: 'HLP Executor disk usage high'
          description:
            'Disk utilization is {{ $value }}%, exceeding 80% threshold'
```

---

### 3.2 錯誤率 | Error Rate

#### 目標 | Objective

```yaml
slo_name: hlp_executor_error_rate
target: < 1%
measurement_window: 7 days
calculation_method: errors / total_requests
```

#### 定義 | Definition

錯誤率是指失敗請求數量佔總請求數量的百分比。

Error rate is the percentage of failed requests out of total requests.

#### 測量方法 | Measurement Method

**Prometheus Query**:

```promql
# 7天錯誤率 | 7-day error rate
(
  sum(rate(hlp_executor_requests_total{status=~"5.."}[7d]))
  /
  sum(rate(hlp_executor_requests_total[7d]))
) * 100

# 按錯誤類型分組 | Grouped by error type
sum by (error_type) (
  rate(hlp_executor_errors_total[7d])
)
```

**監控配置 | Monitoring Configuration**:

```yaml
groups:
  - name: hlp_executor_error_rate
    interval: 1m
    rules:
      - record: hlp_executor:error_rate:7d
        expr: |
          (
            sum(rate(hlp_executor_requests_total{status=~"5.."}[7d]))
            /
            sum(rate(hlp_executor_requests_total[7d]))
          ) * 100

      - alert: HLPExecutorErrorRateSLOViolation
        expr: hlp_executor:error_rate:7d > 1
        for: 10m
        labels:
          severity: warning
          slo_tier: tier3
        annotations:
          summary: 'HLP Executor error rate SLO violation'
          description: 'Error rate is {{ $value }}%, exceeding 1% target'
```

---

## 📋 SLO 指標彙總表 | SLO Metrics Summary Table

| SLO 名稱               | 層級   | 目標         | 測量窗口 | 告警閾值       | 嚴重性       |
| ---------------------- | ------ | ------------ | -------- | -------------- | ------------ |
| **可用性**             | Tier 1 | > 99.9%      | 30 天    | < 99.9%        | Critical     |
| **RTO**                | Tier 1 | < 30s        | 每次事件 | > 30s          | Critical     |
| **RPO**                | Tier 1 | < 5min       | 每次事件 | > 5min         | High         |
| **DAG 解析延遲 (P95)** | Tier 2 | < 120ms      | 7 天     | > 120ms        | Warning      |
| **狀態轉換延遲 (P90)** | Tier 2 | < 50ms       | 7 天     | > 50ms         | Warning      |
| **吞吐量**             | Tier 2 | > 1000 req/s | 5 分鐘   | < 1000 req/s   | Warning      |
| **CPU 利用率**         | Tier 3 | 60-80%       | 7 天     | < 40% 或 > 80% | Warning/Info |
| **記憶體利用率**       | Tier 3 | 70-85%       | 7 天     | < 50% 或 > 90% | Warning/Info |
| **磁碟利用率**         | Tier 3 | < 80%        | 即時     | > 80%          | Warning      |
| **錯誤率**             | Tier 3 | < 1%         | 7 天     | > 1%           | Warning      |

---

## 📈 SLO 合規監控 | SLO Compliance Monitoring

### Grafana 儀表板 | Grafana Dashboard

#### 主要面板 | Main Panels

```yaml
dashboard:
  title: 'HLP Executor SLO Dashboard'
  uid: 'hlp-executor-slo'
  panels:
    - title: 'Availability (30-day)'
      type: gauge
      target: 99.9%
      query: hlp_executor:availability:30d

    - title: 'Error Budget Consumption'
      type: stat
      query: |
        (
          (43.2 - (43.2 * hlp_executor:availability:30d / 100))
          / 43.2
        ) * 100

    - title: 'DAG Parsing Latency Heatmap'
      type: heatmap
      query: |
        sum(rate(hlp_executor_dag_parsing_duration_seconds_bucket[5m])) by (le)

    - title: 'State Transition Latency (P50, P90, P95, P99)'
      type: graph
      queries:
        - p50: histogram_quantile(0.50, rate(...))
        - p90: histogram_quantile(0.90, rate(...))
        - p95: histogram_quantile(0.95, rate(...))
        - p99: histogram_quantile(0.99, rate(...))

    - title: 'SLO Compliance Status'
      type: table
      query: |
        # Shows compliance status for all SLOs
```

### 週報生成 | Weekly Report Generation

```bash
#!/bin/bash
# Generate weekly SLO compliance report

REPORT_FILE="/tmp/hlp-executor-slo-report-$(date +%Y%W).txt"

cat > "$REPORT_FILE" <<EOF
HLP Executor SLO Compliance Report
Week: $(date +%Y-W%W)
Generated: $(date -Iseconds)

═══════════════════════════════════════════════════════

TIER 1: AVAILABILITY AND RELIABILITY
────────────────────────────────────────────────────────

Availability (30-day):
$(curl -s "http://prometheus:9090/api/v1/query" \
  --data-urlencode 'query=hlp_executor:availability:30d' | \
  jq -r '.data.result[0].value[1]')%
Target: 99.9%
Status: $(if [ $(curl -s "http://prometheus:9090/api/v1/query" --data-urlencode 'query=hlp_executor:availability:30d' | jq -r '.data.result[0].value[1]' | awk '{print ($1 >= 99.9)}') -eq 1 ]; then echo "✅ COMPLIANT"; else echo "❌ VIOLATION"; fi)

Error Budget Remaining:
$(curl -s "http://prometheus:9090/api/v1/query" \
  --data-urlencode 'query=(43.2 - (43.2 * (100 - hlp_executor:availability:30d) / 0.1))' | \
  jq -r '.data.result[0].value[1]') minutes
Target: > 0 minutes

═══════════════════════════════════════════════════════

TIER 2: PERFORMANCE AND LATENCY
────────────────────────────────────────────────────────

DAG Parsing Latency (P95):
$(curl -s "http://prometheus:9090/api/v1/query" \
  --data-urlencode 'query=histogram_quantile(0.95, rate(hlp_executor_dag_parsing_duration_seconds_bucket[7d]))' | \
  jq -r '.data.result[0].value[1]')s
Target: < 0.120s
Status: $(if [ $(curl -s "http://prometheus:9090/api/v1/query" --data-urlencode 'query=histogram_quantile(0.95, rate(hlp_executor_dag_parsing_duration_seconds_bucket[7d]))' | jq -r '.data.result[0].value[1]' | awk '{print ($1 < 0.120)}') -eq 1 ]; then echo "✅ COMPLIANT"; else echo "❌ VIOLATION"; fi)

State Transition Latency (P90):
$(curl -s "http://prometheus:9090/api/v1/query" \
  --data-urlencode 'query=histogram_quantile(0.90, rate(hlp_executor_state_transition_duration_seconds_bucket[7d]))' | \
  jq -r '.data.result[0].value[1]')s
Target: < 0.050s
Status: $(if [ $(curl -s "http://prometheus:9090/api/v1/query" --data-urlencode 'query=histogram_quantile(0.90, rate(hlp_executor_state_transition_duration_seconds_bucket[7d]))' | jq -r '.data.result[0].value[1]' | awk '{print ($1 < 0.050)}') -eq 1 ]; then echo "✅ COMPLIANT"; else echo "❌ VIOLATION"; fi)

═══════════════════════════════════════════════════════

TIER 3: CAPACITY AND EFFICIENCY
────────────────────────────────────────────────────────

Error Rate (7-day):
$(curl -s "http://prometheus:9090/api/v1/query" \
  --data-urlencode 'query=hlp_executor:error_rate:7d' | \
  jq -r '.data.result[0].value[1]')%
Target: < 1%
Status: $(if [ $(curl -s "http://prometheus:9090/api/v1/query" --data-urlencode 'query=hlp_executor:error_rate:7d' | jq -r '.data.result[0].value[1]' | awk '{print ($1 < 1)}') -eq 1 ]; then echo "✅ COMPLIANT"; else echo "❌ VIOLATION"; fi)

═══════════════════════════════════════════════════════
EOF

# Send report
cat "$REPORT_FILE" | \
  mail -s "HLP Executor Weekly SLO Report - Week $(date +%Y-W%W)" \
  platform-team@unmanned-island.com

echo "SLO report generated: $REPORT_FILE"
```

---

## 🔍 SLO 審查流程 | SLO Review Process

### 每週審查 | Weekly Review

- **時間**: 每週一 10:00 UTC
- **參與者**: SRE Team, Platform Engineering Lead
- **議程**:
  1. 檢查 SLO 合規狀態
  2. 分析任何違規
  3. 審查錯誤預算消耗
  4. 識別趨勢和模式

### 季度審查 | Quarterly Review

- **時間**: 每季第一個月第一週
- **參與者**: 全體工程團隊, 管理層
- **議程**:
  1. 全面 SLO 合規回顧
  2. 評估 SLO 是否仍然合適
  3. 調整 SLO 目標 (如需要)
  4. 容量規劃和資源優化

---

## 🔗 相關資源 | Related Resources

- [HLP Executor Error Handling Runbook](../runbooks/HLP_EXECUTOR_ERROR_HANDLING.md)
- [HLP Executor Emergency Runbook](../runbooks/HLP_EXECUTOR_EMERGENCY.md)
- [HLP Executor Maintenance Guide](../runbooks/HLP_EXECUTOR_MAINTENANCE.md)
- [Monitoring Configuration](/config/monitoring.yaml)
- [Prometheus Rules](/config/prometheus-rules.yml)
- [Grafana Dashboard](https://grafana/d/hlp-executor-slo)

---

**文件維護者 | Document Maintainer**: Platform Engineering Team  
**審核週期 | Review Cycle**: Quarterly  
**下次審核 | Next Review**: 2026-03-07
