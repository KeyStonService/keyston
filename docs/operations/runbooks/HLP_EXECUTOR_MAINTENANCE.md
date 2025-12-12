# HLP Executor 維護作業手冊 | HLP Executor Maintenance Runbook

**文件版本 | Document Version**: 1.0.0  
**最後更新 | Last Updated**: 2025-12-07  
**負責團隊 | Responsible Team**: Platform Engineering / SRE  
**維護窗口 | Maintenance Window**: Weekly Tue 02:00-04:00 UTC

---

## 📋 文件目的 | Document Purpose

本文件提供 HLP Executor Core
Plugin 的例行維護程序，包含定期維護任務、維護腳本和最佳實踐。

This document provides routine maintenance procedures for the HLP Executor Core
Plugin, including scheduled maintenance tasks, maintenance scripts, and best
practices.

---

## 📅 維護排程概覽 | Maintenance Schedule Overview

| 頻率     | 任務         | 維護窗口                   | 預計時間   | 優先級 |
| -------- | ------------ | -------------------------- | ---------- | ------ |
| **每日** | 狀態清理     | 03:00-03:15 UTC            | 5-10 分鐘  | P2     |
| **每週** | 滾動重啟     | 週二 02:00-04:00 UTC       | 15-30 分鐘 | P3     |
| **每月** | 完整健康檢查 | 第一個週二 02:00-03:00 UTC | 30-45 分鐘 | P2     |
| **每季** | 容量審查     | 季度末週二 02:00-05:00 UTC | 1-2 小時   | P1     |

---

## 📆 每日維護 | Daily Maintenance

### 1. 狀態清理 (State Cleanup)

#### 目的 | Purpose

自動清理超過 7 天的舊狀態和 checkpoint，防止磁碟空間耗盡。

Automatically clean up old states and checkpoints older than 7 days to prevent
disk space exhaustion.

#### 排程 | Schedule

- **時間 | Time**: 每日 03:00 UTC | Daily at 03:00 UTC
- **持續時間 | Duration**: 5-10 分鐘 | 5-10 minutes
- **影響 | Impact**: 無 (低流量時段) | None (low traffic period)

#### 自動化腳本 | Automated Script

```bash
#!/bin/bash
# File: /opt/hlp-executor/maintenance/daily-state-cleanup.sh
# Description: Daily state cleanup with 7-day retention
# Schedule: 03:00 UTC daily via Kubernetes CronJob

set -euo pipefail

NAMESPACE="unmanned-island-system"
DEPLOYMENT="hlp-executor-core"
MAX_AGE_DAYS=7
LOG_FILE="/var/log/hlp-executor/maintenance/state-cleanup-$(date +%Y%m%d).log"

echo "[$(date -Iseconds)] Starting daily state cleanup..." | tee -a "$LOG_FILE"

# Get executor pod
EXECUTOR_POD=$(kubectl get pods -n "$NAMESPACE" -l app=hlp-executor-core -o jsonpath='{.items[0].metadata.name}')

if [ -z "$EXECUTOR_POD" ]; then
  echo "[$(date -Iseconds)] ERROR: No executor pod found" | tee -a "$LOG_FILE"
  exit 1
fi

echo "[$(date -Iseconds)] Using pod: $EXECUTOR_POD" | tee -a "$LOG_FILE"

# Check disk space before cleanup
echo "[$(date -Iseconds)] Disk space before cleanup:" | tee -a "$LOG_FILE"
kubectl exec -n "$NAMESPACE" "$EXECUTOR_POD" -- df -h /var/lib/hlp-executor/state | tee -a "$LOG_FILE"

# Run checkpoint cleanup
echo "[$(date -Iseconds)] Running checkpoint cleanup (max age: ${MAX_AGE_DAYS} days)..." | tee -a "$LOG_FILE"
kubectl exec -n "$NAMESPACE" "$EXECUTOR_POD" -- \
  python3 -m core.safety_mechanisms.checkpoint_manager cleanup \
  --max-age-days "$MAX_AGE_DAYS" \
  --verbose 2>&1 | tee -a "$LOG_FILE"

CLEANUP_STATUS=${PIPESTATUS[0]}

if [ $CLEANUP_STATUS -eq 0 ]; then
  echo "[$(date -Iseconds)] Checkpoint cleanup completed successfully" | tee -a "$LOG_FILE"
else
  echo "[$(date -Iseconds)] WARNING: Checkpoint cleanup failed with exit code $CLEANUP_STATUS" | tee -a "$LOG_FILE"
fi

# Check disk space after cleanup
echo "[$(date -Iseconds)] Disk space after cleanup:" | tee -a "$LOG_FILE"
kubectl exec -n "$NAMESPACE" "$EXECUTOR_POD" -- df -h /var/lib/hlp-executor/state | tee -a "$LOG_FILE"

# Report metrics
DISK_USAGE=$(kubectl exec -n "$NAMESPACE" "$EXECUTOR_POD" -- \
  df -h /var/lib/hlp-executor/state | awk 'NR==2 {print $5}' | sed 's/%//')

echo "[$(date -Iseconds)] Current disk usage: ${DISK_USAGE}%" | tee -a "$LOG_FILE"

if [ "$DISK_USAGE" -gt 80 ]; then
  echo "[$(date -Iseconds)] WARNING: Disk usage above 80%, consider expanding PVC" | tee -a "$LOG_FILE"
  # Send alert
  curl -X POST "http://prometheus-alertmanager:9093/api/v1/alerts" \
    -H "Content-Type: application/json" \
    -d @- <<EOF
[{
  "labels": {
    "alertname": "HLPExecutorHighDiskUsage",
    "severity": "warning",
    "namespace": "$NAMESPACE",
    "disk_usage": "${DISK_USAGE}%"
  },
  "annotations": {
    "summary": "HLP Executor disk usage is ${DISK_USAGE}%",
    "description": "Consider expanding PVC or adjusting retention policy"
  }
}]
EOF
fi

echo "[$(date -Iseconds)] Daily state cleanup completed" | tee -a "$LOG_FILE"
exit 0
```

#### Kubernetes CronJob 定義 | Kubernetes CronJob Definition

```yaml
# File: infrastructure/kubernetes/cronjobs/hlp-executor-daily-cleanup.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: hlp-executor-daily-cleanup
  namespace: unmanned-island-system
  labels:
    app: hlp-executor-maintenance
    maintenance-type: state-cleanup
spec:
  schedule: '0 3 * * *' # 03:00 UTC daily
  timeZone: 'UTC'
  successfulJobsHistoryLimit: 7
  failedJobsHistoryLimit: 3
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      template:
        metadata:
          labels:
            app: hlp-executor-maintenance
            maintenance-task: daily-cleanup
        spec:
          serviceAccountName: hlp-executor-maintenance-sa
          restartPolicy: OnFailure
          containers:
            - name: cleanup
              image: bitnami/kubectl:1.28
              command:
                - /bin/bash
                - /scripts/daily-state-cleanup.sh
              volumeMounts:
                - name: maintenance-scripts
                  mountPath: /scripts
                - name: log-volume
                  mountPath: /var/log/hlp-executor/maintenance
              resources:
                requests:
                  cpu: 100m
                  memory: 128Mi
                limits:
                  cpu: 500m
                  memory: 512Mi
          volumes:
            - name: maintenance-scripts
              configMap:
                name: hlp-executor-maintenance-scripts
                defaultMode: 0755
            - name: log-volume
              persistentVolumeClaim:
                claimName: hlp-executor-maintenance-logs-pvc
```

#### 手動執行 | Manual Execution

```bash
# Trigger manual cleanup if needed
kubectl create job --from=cronjob/hlp-executor-daily-cleanup \
  hlp-executor-manual-cleanup-$(date +%s) \
  -n unmanned-island-system

# Monitor job progress
kubectl logs -n unmanned-island-system -l maintenance-task=daily-cleanup -f

# Check job status
kubectl get jobs -n unmanned-island-system -l maintenance-task=daily-cleanup
```

#### 驗證 | Verification

```bash
# 1. Check last cleanup job status
kubectl get jobs -n unmanned-island-system -l maintenance-task=daily-cleanup --sort-by=.metadata.creationTimestamp | tail -1

# 2. Verify disk space
kubectl exec -n unmanned-island-system deployment/hlp-executor-core -- \
  df -h /var/lib/hlp-executor/state

# 3. Check checkpoint count
kubectl exec -n unmanned-island-system deployment/hlp-executor-core -- \
  find /var/lib/hlp-executor/state/checkpoints -type f | wc -l

# 4. View cleanup logs
kubectl logs -n unmanned-island-system -l maintenance-task=daily-cleanup --tail=50
```

---

## 🔄 每週維護 | Weekly Maintenance

### 1. 滾動重啟 (Rolling Restart)

#### 目的 | Purpose

定期重啟以釋放記憶體、刷新配置並確保所有 Pod 運行最新版本。

Periodic restart to release memory, refresh configuration, and ensure all pods
run the latest version.

#### 排程 | Schedule

- **時間 | Time**: 每週二 02:00-04:00 UTC | Weekly Tuesday 02:00-04:00 UTC
- **持續時間 | Duration**: 15-30 分鐘 | 15-30 minutes
- **影響 | Impact**: 最小 (滾動重啟保持服務可用) | Minimal (rolling restart
  maintains availability)

#### 前置檢查 | Pre-Restart Checks

```bash
#!/bin/bash
# Pre-restart health checks

echo "=== Pre-Restart Health Checks ==="

# 1. Check current pod health
echo "1. Checking pod health..."
kubectl get pods -n unmanned-island-system -l app=hlp-executor-core

UNHEALTHY_PODS=$(kubectl get pods -n unmanned-island-system -l app=hlp-executor-core -o json | \
  jq -r '.items[] | select(.status.phase != "Running" or (.status.conditions[] | select(.type == "Ready" and .status != "True"))) | .metadata.name')

if [ -n "$UNHEALTHY_PODS" ]; then
  echo "WARNING: Unhealthy pods detected: $UNHEALTHY_PODS"
  echo "Investigate before proceeding with restart"
  exit 1
fi

# 2. Check for ongoing executions
echo "2. Checking for ongoing critical executions..."
RUNNING_COUNT=$(kubectl exec -n unmanned-island-system deployment/hlp-executor-core -- \
  curl -s http://localhost:8081/admin/executions?status=RUNNING | jq 'length')

echo "Running executions: $RUNNING_COUNT"

if [ "$RUNNING_COUNT" -gt 100 ]; then
  echo "WARNING: High number of running executions ($RUNNING_COUNT)"
  echo "Consider postponing restart or increasing replica count"
  read -p "Continue with restart? (yes/no): " confirm
  if [ "$confirm" != "yes" ]; then
    exit 1
  fi
fi

# 3. Verify PVC is healthy
echo "3. Checking PVC status..."
kubectl get pvc hlp-executor-state-pvc -n unmanned-island-system

PVC_STATUS=$(kubectl get pvc hlp-executor-state-pvc -n unmanned-island-system -o jsonpath='{.status.phase}')
if [ "$PVC_STATUS" != "Bound" ]; then
  echo "ERROR: PVC is not bound (status: $PVC_STATUS)"
  exit 1
fi

# 4. Check recent error rate
echo "4. Checking recent error rate..."
ERROR_RATE=$(kubectl exec -n unmanned-island-system deployment/hlp-executor-core -- \
  curl -s 'http://localhost:8080/metrics' | \
  grep 'hlp_executor_errors_total' | awk '{sum+=$2} END {print sum}')

echo "Recent errors: $ERROR_RATE"

if [ "$ERROR_RATE" -gt 50 ]; then
  echo "WARNING: High error rate detected ($ERROR_RATE errors)"
  echo "Consider investigating before restart"
fi

echo "=== Pre-Restart Checks Completed ==="
echo "System is ready for rolling restart"
```

#### 滾動重啟程序 | Rolling Restart Procedure

```bash
#!/bin/bash
# File: /opt/hlp-executor/maintenance/weekly-rolling-restart.sh
# Description: Weekly rolling restart with health verification
# Schedule: Tuesday 02:00 UTC weekly via Kubernetes CronJob

set -euo pipefail

NAMESPACE="unmanned-island-system"
DEPLOYMENT="hlp-executor-core"
LOG_FILE="/var/log/hlp-executor/maintenance/rolling-restart-$(date +%Y%m%d-%H%M%S).log"

echo "[$(date -Iseconds)] Starting weekly rolling restart..." | tee -a "$LOG_FILE"

# Step 1: Pre-restart snapshot
echo "[$(date -Iseconds)] Creating pre-restart state snapshot..." | tee -a "$LOG_FILE"
kubectl exec -n "$NAMESPACE" deployment/"$DEPLOYMENT" -- \
  python3 -m core.safety_mechanisms.checkpoint_manager snapshot \
  --type FULL \
  --name "pre-restart-$(date +%s)" 2>&1 | tee -a "$LOG_FILE"

# Step 2: Verify deployment is healthy
CURRENT_REPLICAS=$(kubectl get deployment "$DEPLOYMENT" -n "$NAMESPACE" -o jsonpath='{.status.replicas}')
READY_REPLICAS=$(kubectl get deployment "$DEPLOYMENT" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}')

echo "[$(date -Iseconds)] Current replicas: $CURRENT_REPLICAS, Ready: $READY_REPLICAS" | tee -a "$LOG_FILE"

if [ "$CURRENT_REPLICAS" != "$READY_REPLICAS" ]; then
  echo "[$(date -Iseconds)] ERROR: Not all replicas are ready" | tee -a "$LOG_FILE"
  exit 1
fi

# Step 3: Trigger rolling restart
echo "[$(date -Iseconds)] Triggering rolling restart..." | tee -a "$LOG_FILE"
kubectl rollout restart deployment/"$DEPLOYMENT" -n "$NAMESPACE" 2>&1 | tee -a "$LOG_FILE"

# Step 4: Monitor rollout progress
echo "[$(date -Iseconds)] Monitoring rollout progress..." | tee -a "$LOG_FILE"
kubectl rollout status deployment/"$DEPLOYMENT" -n "$NAMESPACE" --timeout=10m 2>&1 | tee -a "$LOG_FILE"

ROLLOUT_STATUS=${PIPESTATUS[0]}

if [ $ROLLOUT_STATUS -ne 0 ]; then
  echo "[$(date -Iseconds)] ERROR: Rollout failed" | tee -a "$LOG_FILE"

  # Attempt to rollback
  echo "[$(date -Iseconds)] Attempting automatic rollback..." | tee -a "$LOG_FILE"
  kubectl rollout undo deployment/"$DEPLOYMENT" -n "$NAMESPACE" 2>&1 | tee -a "$LOG_FILE"

  exit 1
fi

# Step 5: Post-restart verification
echo "[$(date -Iseconds)] Running post-restart verification..." | tee -a "$LOG_FILE"

sleep 30  # Allow pods to stabilize

# Verify all pods are healthy
READY_REPLICAS_AFTER=$(kubectl get deployment "$DEPLOYMENT" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}')
echo "[$(date -Iseconds)] Ready replicas after restart: $READY_REPLICAS_AFTER" | tee -a "$LOG_FILE"

if [ "$READY_REPLICAS_AFTER" != "$CURRENT_REPLICAS" ]; then
  echo "[$(date -Iseconds)] WARNING: Not all replicas are ready after restart" | tee -a "$LOG_FILE"
fi

# Verify health endpoints
for pod in $(kubectl get pods -n "$NAMESPACE" -l app=hlp-executor-core -o jsonpath='{.items[*].metadata.name}'); do
  echo "[$(date -Iseconds)] Checking health of $pod..." | tee -a "$LOG_FILE"
  kubectl exec -n "$NAMESPACE" "$pod" -- curl -f http://localhost:8080/healthz 2>&1 | tee -a "$LOG_FILE"
done

# Step 6: Verify service metrics
echo "[$(date -Iseconds)] Checking post-restart metrics..." | tee -a "$LOG_FILE"
kubectl exec -n "$NAMESPACE" deployment/"$DEPLOYMENT" -- \
  curl -s http://localhost:8080/metrics | grep -E "(up|health)" | tee -a "$LOG_FILE"

echo "[$(date -Iseconds)] Weekly rolling restart completed successfully" | tee -a "$LOG_FILE"
exit 0
```

#### 回滾程序 (如需要) | Rollback Procedure (If Needed)

```bash
# If restart causes issues, rollback immediately

# 1. Rollback deployment
kubectl rollout undo deployment/hlp-executor-core -n unmanned-island-system

# 2. Monitor rollback
kubectl rollout status deployment/hlp-executor-core -n unmanned-island-system

# 3. Verify health
kubectl get pods -n unmanned-island-system -l app=hlp-executor-core

# 4. Restore from pre-restart snapshot if state is corrupted
kubectl exec -n unmanned-island-system deployment/hlp-executor-core -- \
  python3 -m core.safety_mechanisms.checkpoint_manager list --recent 5 | grep "pre-restart"

# Use the latest pre-restart snapshot ID
kubectl exec -n unmanned-island-system deployment/hlp-executor-core -- \
  python3 -m core.safety_mechanisms.checkpoint_manager restore \
  --checkpoint-id <SNAPSHOT_ID> \
  --verify
```

---

## 📊 每月維護 | Monthly Maintenance

### 1. 完整健康檢查 (Comprehensive Health Check)

#### 排程 | Schedule

- **時間 | Time**: 每月第一個週二 02:00-03:00 UTC | First Tuesday of month
  02:00-03:00 UTC
- **持續時間 | Duration**: 30-45 分鐘 | 30-45 minutes

#### 檢查清單 | Checklist

```bash
#!/bin/bash
# Monthly comprehensive health check

echo "=== HLP Executor Monthly Health Check ==="
echo "Date: $(date -Iseconds)"
echo ""

# 1. Infrastructure Health
echo "1. INFRASTRUCTURE HEALTH"
echo "------------------------"
kubectl get nodes -o wide
kubectl top nodes
echo ""

# 2. Deployment Status
echo "2. DEPLOYMENT STATUS"
echo "--------------------"
kubectl get deployment hlp-executor-core -n unmanned-island-system -o wide
kubectl describe deployment hlp-executor-core -n unmanned-island-system | grep -A 10 "Conditions:"
echo ""

# 3. Pod Health
echo "3. POD HEALTH"
echo "-------------"
kubectl get pods -n unmanned-island-system -l app=hlp-executor-core -o wide
kubectl top pods -n unmanned-island-system -l app=hlp-executor-core
echo ""

# 4. Storage Health
echo "4. STORAGE HEALTH"
echo "-----------------"
kubectl get pvc -n unmanned-island-system
kubectl exec -n unmanned-island-system deployment/hlp-executor-core -- df -h /var/lib/hlp-executor/state
echo ""

# 5. Service Health
echo "5. SERVICE HEALTH"
echo "-----------------"
kubectl get svc -n unmanned-island-system -l app=hlp-executor-core
kubectl exec -n unmanned-island-system deployment/hlp-executor-core -- \
  curl -s http://localhost:8080/healthz | jq
echo ""

# 6. Network Policy
echo "6. NETWORK POLICY"
echo "-----------------"
kubectl get networkpolicy -n unmanned-island-system
echo ""

# 7. RBAC Configuration
echo "7. RBAC CONFIGURATION"
echo "---------------------"
kubectl get serviceaccount hlp-executor-sa -n unmanned-island-system
kubectl get rolebinding -n unmanned-island-system | grep hlp-executor
echo ""

# 8. ConfigMap and Secrets
echo "8. CONFIGMAP AND SECRETS"
echo "------------------------"
kubectl get configmap -n unmanned-island-system | grep hlp-executor
kubectl get secret -n unmanned-island-system | grep hlp-executor
echo ""

# 9. Circuit Breaker Status
echo "9. CIRCUIT BREAKER STATUS"
echo "-------------------------"
kubectl exec -n unmanned-island-system deployment/hlp-executor-core -- \
  curl -s http://localhost:8080/metrics | grep circuit_breaker_state
echo ""

# 10. Error Rates (Last 30 days)
echo "10. ERROR RATES (LAST 30 DAYS)"
echo "-------------------------------"
kubectl exec -n unmanned-island-system deployment/hlp-executor-core -- \
  curl -s http://localhost:8080/metrics | grep -E "(errors_total|failures_total)"
echo ""

# 11. State Persistence Metrics
echo "11. STATE PERSISTENCE METRICS"
echo "------------------------------"
kubectl exec -n unmanned-island-system deployment/hlp-executor-core -- \
  python3 -m core.safety_mechanisms.checkpoint_manager stats
echo ""

# 12. Performance Metrics
echo "12. PERFORMANCE METRICS"
echo "-----------------------"
kubectl exec -n unmanned-island-system deployment/hlp-executor-core -- \
  curl -s http://localhost:8080/metrics | grep -E "(latency|duration)" | head -20
echo ""

# 13. Recent Warnings/Errors in Logs
echo "13. RECENT WARNINGS/ERRORS"
echo "--------------------------"
kubectl logs -n unmanned-island-system -l app=hlp-executor-core --tail=1000 --since=720h | \
  grep -E "(WARN|ERROR|FATAL)" | tail -20
echo ""

echo "=== Health Check Completed ==="
```

#### 報告生成 | Report Generation

```bash
# Generate monthly health report
./monthly-health-check.sh > /tmp/hlp-executor-health-report-$(date +%Y%m).txt

# Archive report
gsutil cp /tmp/hlp-executor-health-report-$(date +%Y%m).txt \
  gs://unmanned-island-maintenance-reports/hlp-executor/

# Send report to team
cat /tmp/hlp-executor-health-report-$(date +%Y%m).txt | \
  mail -s "HLP Executor Monthly Health Report - $(date +%B%Y)" \
  platform-team@unmanned-island.com
```

---

## 📈 每季維護 | Quarterly Maintenance

### 1. 容量審查與規劃 (Capacity Review and Planning)

#### 排程 | Schedule

- **時間 | Time**: 季度末第一個週二 02:00-05:00 UTC | First Tuesday of
  quarter-end month 02:00-05:00 UTC
- **持續時間 | Duration**: 1-2 小時 | 1-2 hours

#### 容量分析 | Capacity Analysis

```bash
#!/bin/bash
# Quarterly capacity analysis

echo "=== HLP Executor Quarterly Capacity Review ==="
echo "Quarter: Q$(date +%q) $(date +%Y)"
echo ""

# 1. Historical Growth Analysis
echo "1. HISTORICAL GROWTH ANALYSIS"
echo "------------------------------"

# Query Prometheus for 90-day trends
curl -s "http://prometheus:9090/api/v1/query_range" \
  --data-urlencode 'query=avg(hlp_executor_executions_total)' \
  --data-urlencode "start=$(date -d '90 days ago' +%s)" \
  --data-urlencode "end=$(date +%s)" \
  --data-urlencode 'step=1d' | jq -r '.data.result[0].values[] | @tsv'

# 2. Resource Utilization Trends
echo ""
echo "2. RESOURCE UTILIZATION TRENDS"
echo "-------------------------------"

# CPU usage trend
curl -s "http://prometheus:9090/api/v1/query" \
  --data-urlencode 'query=avg(rate(container_cpu_usage_seconds_total{namespace="unmanned-island-system",pod=~"hlp-executor.*"}[30d]))' | \
  jq -r '.data.result[0].value[1]'

# Memory usage trend
curl -s "http://prometheus:9090/api/v1/query" \
  --data-urlencode 'query=avg(container_memory_working_set_bytes{namespace="unmanned-island-system",pod=~"hlp-executor.*"})/1024/1024/1024' | \
  jq -r '.data.result[0].value[1]'

# Storage usage trend
kubectl exec -n unmanned-island-system deployment/hlp-executor-core -- \
  df -h /var/lib/hlp-executor/state

# 3. Performance Metrics Trends
echo ""
echo "3. PERFORMANCE METRICS TRENDS"
echo "------------------------------"

# DAG parsing latency P95
curl -s "http://prometheus:9090/api/v1/query" \
  --data-urlencode 'query=histogram_quantile(0.95, rate(hlp_executor_dag_parsing_duration_seconds_bucket[30d]))' | \
  jq -r '.data.result[0].value[1]'

# State transition latency P90
curl -s "http://prometheus:9090/api/v1/query" \
  --data-urlencode 'query=histogram_quantile(0.90, rate(hlp_executor_state_transition_duration_seconds_bucket[30d]))' | \
  jq -r '.data.result[0].value[1]'

# 4. Capacity Recommendations
echo ""
echo "4. CAPACITY RECOMMENDATIONS"
echo "---------------------------"

CURRENT_REPLICAS=$(kubectl get deployment hlp-executor-core -n unmanned-island-system -o jsonpath='{.spec.replicas}')
CURRENT_CPU_REQUEST=$(kubectl get deployment hlp-executor-core -n unmanned-island-system -o jsonpath='{.spec.template.spec.containers[0].resources.requests.cpu}')
CURRENT_MEMORY_REQUEST=$(kubectl get deployment hlp-executor-core -n unmanned-island-system -o jsonpath='{.spec.template.spec.containers[0].resources.requests.memory}')
CURRENT_PVC_SIZE=$(kubectl get pvc hlp-executor-state-pvc -n unmanned-island-system -o jsonpath='{.spec.resources.requests.storage}')

echo "Current Configuration:"
echo "  Replicas: $CURRENT_REPLICAS"
echo "  CPU Request: $CURRENT_CPU_REQUEST"
echo "  Memory Request: $CURRENT_MEMORY_REQUEST"
echo "  PVC Size: $CURRENT_PVC_SIZE"
echo ""

# Calculate growth rate and project next quarter needs
# (This would typically use historical data analysis)
echo "Projected Q$(( $(date +%q) + 1 )) Needs:"
echo "  Replicas: [TBD based on growth]"
echo "  CPU Request: [TBD based on utilization]"
echo "  Memory Request: [TBD based on utilization]"
echo "  PVC Size: [TBD based on storage growth]"
echo ""

echo "=== Capacity Review Completed ==="
```

---

## 🛠️ 維護腳本參考 | Maintenance Scripts Reference

### 腳本位置 | Script Locations

```
/opt/hlp-executor/maintenance/
├── daily-state-cleanup.sh          # 每日狀態清理
├── weekly-rolling-restart.sh       # 每週滾動重啟
├── monthly-health-check.sh         # 每月健康檢查
├── quarterly-capacity-review.sh    # 每季容量審查
└── common/
    ├── pre-restart-checks.sh       # 重啟前檢查
    ├── post-restart-verify.sh      # 重啟後驗證
    └── emergency-rollback.sh       # 緊急回滾
```

### ConfigMap 配置 | ConfigMap Configuration

```yaml
# infrastructure/kubernetes/configmaps/hlp-executor-maintenance-scripts.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: hlp-executor-maintenance-scripts
  namespace: unmanned-island-system
data:
  daily-state-cleanup.sh: |
    #!/bin/bash
    # Content from above script

  weekly-rolling-restart.sh: |
    #!/bin/bash
    # Content from above script

  monthly-health-check.sh: |
    #!/bin/bash
    # Content from above script
```

---

## 🚨 緊急維護程序 | Emergency Maintenance Procedures

### 緊急配置變更 | Emergency Configuration Changes

```bash
# If urgent configuration change is needed without restart

# 1. Verify current configuration
kubectl get configmap hlp-executor-config -n unmanned-island-system -o yaml

# 2. Create backup
kubectl get configmap hlp-executor-config -n unmanned-island-system -o yaml > \
  /tmp/hlp-executor-config-backup-$(date +%s).yaml

# 3. Apply change
kubectl edit configmap hlp-executor-config -n unmanned-island-system

# 4. Verify change
kubectl get configmap hlp-executor-config -n unmanned-island-system -o yaml

# 5. Trigger config reload (if supported)
kubectl exec -n unmanned-island-system deployment/hlp-executor-core -- \
  curl -X POST http://localhost:8081/admin/reload-config

# 6. If reload not supported, perform rolling restart
kubectl rollout restart deployment/hlp-executor-core -n unmanned-island-system
```

### 緊急副本擴展 | Emergency Replica Scaling

```bash
# Scale up for high load
kubectl scale deployment hlp-executor-core -n unmanned-island-system --replicas=5

# Scale down if needed (ensure no critical executions)
kubectl scale deployment hlp-executor-core -n unmanned-island-system --replicas=2

# Wait for scaling to complete
kubectl wait --for=condition=available --timeout=180s \
  deployment/hlp-executor-core -n unmanned-island-system
```

---

## 📚 維護最佳實踐 | Maintenance Best Practices

### ✅ 做 | Do

1. **Always create state snapshot before maintenance** | 維護前總是創建狀態快照
2. **Verify health before and after** | 維護前後驗證健康狀態
3. **Use rolling restarts to minimize downtime** | 使用滾動重啟最小化停機時間
4. **Monitor metrics during maintenance** | 維護期間監控指標
5. **Keep maintenance logs** | 保留維護日誌
6. **Test rollback procedures regularly** | 定期測試回滾程序
7. **Communicate maintenance windows** | 提前溝通維護窗口
8. **Automate routine tasks** | 自動化例行任務

### ❌ 不要 | Don't

1. **Never skip pre-maintenance checks** | 不要跳過維護前檢查
2. **Never restart all replicas simultaneously** | 不要同時重啟所有副本
3. **Never delete state data without backup**
   | 不要在沒有備份的情況下刪除狀態數據
4. **Never perform major changes during peak hours**
   | 不要在高峰時段進行重大變更
5. **Never ignore post-maintenance warnings** | 不要忽視維護後的警告
6. **Never proceed if pre-checks fail** | 如果預檢失敗不要繼續
7. **Never modify production without testing**
   | 不要在未經測試的情況下修改生產環境
8. **Never forget to document changes** | 不要忘記記錄變更

---

## 🔗 相關資源 | Related Resources

- [HLP Executor Error Handling Runbook](./HLP_EXECUTOR_ERROR_HANDLING.md)
- [HLP Executor Emergency Runbook](./HLP_EXECUTOR_EMERGENCY.md)
- [HLP Executor SLO](../slo/HLP_EXECUTOR_SLO.md)
- [HLP Executor Deployment Checklist](../deployment/HLP_EXECUTOR_DEPLOYMENT_CHECKLIST.md)
- [Maintenance Scripts Repository](https://github.com/unmanned-island/hlp-executor-maintenance)

---

**文件維護者 | Document Maintainer**: Platform Engineering Team  
**審核週期 | Review Cycle**: Quarterly  
**下次審核 | Next Review**: 2026-03-07
