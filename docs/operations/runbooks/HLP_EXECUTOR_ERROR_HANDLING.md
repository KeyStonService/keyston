# HLP Executor 錯誤處理手冊 | HLP Executor Error Handling Runbook

**文件版本 | Document Version**: 1.0.0  
**最後更新 | Last Updated**: 2025-12-07  
**負責團隊 | Responsible Team**: Platform Engineering / SRE  
**嚴重性級別 | Severity Level**: P1 (Critical)

---

## 📋 文件目的 | Document Purpose

本文件提供 HLP Executor Core Plugin 的錯誤處理指南，包含常見故障模式、診斷步驟、恢復策略和升級路徑。

This document provides error handling guidelines for the HLP Executor Core Plugin, including common failure modes, diagnostic steps, recovery strategies, and escalation paths.

---

## 🎯 常見故障模式 | Common Failure Modes

### 1. Kubernetes API 不可用 | Kubernetes API Unavailable

#### 症狀 | Symptoms
```
ERROR: Failed to connect to Kubernetes API server
Connection refused: https://kubernetes.default.svc:443
circuit_breaker: kubernetes_api OPEN (failure_threshold: 5 reached)
```

#### 影響範圍 | Impact Scope
- ⚠️ **嚴重性**: P1 - Critical
- 🎯 **影響範圍**: 所有 HLP 執行無法進行 | All HLP executions blocked
- ⏱️ **RTO**: < 30 seconds
- 📊 **SLO 影響**: Availability SLO 違反 | Availability SLO violation

#### 診斷步驟 | Diagnostic Steps

1. **檢查 Kubernetes API Server 狀態 | Check Kubernetes API Server Status**
   ```bash
   # Check if API server is responding
   kubectl cluster-info
   
   # Check API server pods status
   kubectl get pods -n kube-system | grep kube-apiserver
   
   # Check API server logs
   kubectl logs -n kube-system -l component=kube-apiserver --tail=100
   ```

2. **驗證網路連接 | Verify Network Connectivity**
   ```bash
   # From HLP Executor pod
   kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
     curl -k https://kubernetes.default.svc:443/healthz
   
   # Check DNS resolution
   kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
     nslookup kubernetes.default.svc
   ```

3. **檢查服務帳戶權限 | Check ServiceAccount Permissions**
   ```bash
   # Verify ServiceAccount exists
   kubectl get serviceaccount hlp-executor-sa -n unmanned-island-system
   
   # Check RBAC permissions
   kubectl auth can-i --list --as=system:serviceaccount:unmanned-island-system:hlp-executor-sa
   
   # Verify token is mounted
   kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
     ls -la /var/run/secrets/kubernetes.io/serviceaccount/
   ```

4. **檢查斷路器狀態 | Check Circuit Breaker Status**
   ```bash
   # Query Prometheus metrics
   curl -s http://prometheus:9090/api/v1/query \
     --data-urlencode 'query=hlp_executor_circuit_breaker_state{service="kubernetes_api"}' | jq
   
   # Check circuit breaker metrics
   kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
     curl http://localhost:8080/metrics | grep circuit_breaker
   ```

#### 恢復策略 | Recovery Strategies

##### 策略 A: 重置斷路器 (Circuit Breaker Reset)
```bash
# Reset circuit breaker via admin API
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl -X POST http://localhost:8081/admin/circuit-breaker/kubernetes_api/reset

# Verify circuit breaker is closed
kubectl logs -n unmanned-island-system deployment/hlp-executor-core --tail=20 | grep "circuit_breaker.*CLOSED"
```

**使用時機 | When to Use**: API server 已恢復但斷路器仍開啟 | API server recovered but circuit breaker still open  
**預期時間 | Expected Time**: < 10 seconds  
**風險等級 | Risk Level**: LOW

##### 策略 B: 重啟 HLP Executor Pod
```bash
# Graceful restart
kubectl rollout restart deployment/hlp-executor-core -n unmanned-island-system

# Monitor restart progress
kubectl rollout status deployment/hlp-executor-core -n unmanned-island-system

# Verify health
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl http://localhost:8080/healthz
```

**使用時機 | When to Use**: 斷路器重置失敗或連線仍有問題 | Circuit breaker reset failed or connection still problematic  
**預期時間 | Expected Time**: 30-60 seconds  
**風險等級 | Risk Level**: MEDIUM

##### 策略 C: 更新 RBAC 配置
```bash
# Reapply RBAC configuration
kubectl apply -f infrastructure/kubernetes/rbac/hlp-executor-rbac.yaml

# Verify role binding
kubectl get rolebinding hlp-executor-binding -n unmanned-island-system -o yaml

# Restart pods to pick up new permissions
kubectl rollout restart deployment/hlp-executor-core -n unmanned-island-system
```

**使用時機 | When to Use**: 診斷顯示權限問題 | Diagnostics show permission issues  
**預期時間 | Expected Time**: 1-2 minutes  
**風險等級 | Risk Level**: LOW

---

### 2. 狀態持久化失敗 | State Persistence Failures

#### 症狀 | Symptoms
```
ERROR: Failed to persist execution state
PersistentVolumeClaim not bound: hlp-executor-state-pvc
checkpoint_manager: Failed to write checkpoint (disk full)
state_corruption_detected: Checkpoint validation failed
```

#### 影響範圍 | Impact Scope
- ⚠️ **嚴重性**: P2 - High
- 🎯 **影響範圍**: 執行狀態可能遺失，部分回滾功能受損 | Execution state may be lost, partial rollback impaired
- ⏱️ **RTO**: < 2 minutes
- 📊 **SLO 影響**: State transition latency 增加 | State transition latency increased

#### 診斷步驟 | Diagnostic Steps

1. **檢查 PVC 狀態 | Check PVC Status**
   ```bash
   # Check PVC binding status
   kubectl get pvc hlp-executor-state-pvc -n unmanned-island-system
   
   # Check PV details
   kubectl describe pvc hlp-executor-state-pvc -n unmanned-island-system
   
   # Check storage class
   kubectl get storageclass
   ```

2. **檢查磁碟空間 | Check Disk Space**
   ```bash
   # Check pod disk usage
   kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- df -h
   
   # Check state directory size
   kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
     du -sh /var/lib/hlp-executor/state/*
   
   # Check checkpoint count
   kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
     find /var/lib/hlp-executor/state/checkpoints -type f | wc -l
   ```

3. **驗證 Checkpoint 完整性 | Verify Checkpoint Integrity**
   ```bash
   # Run checkpoint validation
   kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
     python3 -m core.safety_mechanisms.checkpoint_manager validate --all
   
   # Check for corrupted files
   kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
     find /var/lib/hlp-executor/state -type f -exec md5sum {} \; | \
     grep -v -f /var/lib/hlp-executor/state/checksums.txt
   ```

#### 恢復策略 | Recovery Strategies

##### 策略 A: 清理過期 Checkpoint
```bash
# Manual cleanup (older than 7 days)
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  python3 -m core.safety_mechanisms.checkpoint_manager cleanup --max-age-days 7

# Verify disk space after cleanup
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- df -h

# Check service health
kubectl logs -n unmanned-island-system deployment/hlp-executor-core --tail=50 | \
  grep -E "(checkpoint_cleanup|disk_space)"
```

**使用時機 | When to Use**: 磁碟空間不足 | Disk space insufficient  
**預期時間 | Expected Time**: 30-90 seconds  
**風險等級 | Risk Level**: LOW

##### 策略 B: 擴充 PVC 容量
```bash
# Check if storage class supports expansion
kubectl get storageclass -o json | jq '.items[] | select(.metadata.name=="standard") | .allowVolumeExpansion'

# Patch PVC to increase size
kubectl patch pvc hlp-executor-state-pvc -n unmanned-island-system \
  -p '{"spec":{"resources":{"requests":{"storage":"20Gi"}}}}'

# Monitor expansion progress
kubectl get pvc hlp-executor-state-pvc -n unmanned-island-system --watch

# Restart pod if needed
kubectl rollout restart deployment/hlp-executor-core -n unmanned-island-system
```

**使用時機 | When to Use**: 清理後空間仍不足 | Cleanup insufficient  
**預期時間 | Expected Time**: 2-5 minutes  
**風險等級 | Risk Level**: MEDIUM

##### 策略 C: 從最近的 Checkpoint 恢復
```bash
# List available checkpoints
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  python3 -m core.safety_mechanisms.checkpoint_manager list --recent 5

# Restore from specific checkpoint
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  python3 -m core.safety_mechanisms.checkpoint_manager restore --checkpoint-id <CHECKPOINT_ID>

# Verify restoration
kubectl logs -n unmanned-island-system deployment/hlp-executor-core --tail=100 | \
  grep "checkpoint_restore"
```

**使用時機 | When to Use**: 狀態損壞，需要恢復到已知良好狀態 | State corrupted, need to restore to known good state  
**預期時間 | Expected Time**: 1-3 minutes  
**風險等級 | Risk Level**: MEDIUM

---

### 3. Quantum Backend 不可用 | Quantum Backend Unavailable

#### 症狀 | Symptoms
```
ERROR: Quantum backend connection timeout
quantum_api: HTTP 503 Service Unavailable
circuit_breaker: quantum_backend HALF_OPEN (attempting recovery)
retry_policy: Exponential backoff (attempt 3/5)
```

#### 影響範圍 | Impact Scope
- ⚠️ **嚴重性**: P2 - High
- 🎯 **影響範圍**: 需要量子處理的 HLP 執行受阻 | HLP executions requiring quantum processing blocked
- ⏱️ **RTO**: < 5 minutes
- 📊 **SLO 影響**: DAG parsing latency 增加 | DAG parsing latency increased

#### 診斷步驟 | Diagnostic Steps

1. **檢查 Quantum Backend 健康狀態 | Check Quantum Backend Health**
   ```bash
   # Check quantum service endpoint
   kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
     curl -v http://quantum-backend-service:8080/health
   
   # Check quantum backend pods
   kubectl get pods -n quantum-system -l app=quantum-backend
   
   # Check quantum backend logs
   kubectl logs -n quantum-system -l app=quantum-backend --tail=100
   ```

2. **檢查網路策略 | Check Network Policies**
   ```bash
   # Verify network policy allows communication
   kubectl get networkpolicy -n unmanned-island-system
   kubectl describe networkpolicy hlp-executor-netpol -n unmanned-island-system
   
   # Test connectivity
   kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
     nc -zv quantum-backend-service.quantum-system.svc.cluster.local 8080
   ```

3. **檢查重試策略狀態 | Check Retry Policy Status**
   ```bash
   # Check retry metrics
   kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
     curl http://localhost:8080/metrics | grep -E "(retry_attempt|backoff_duration)"
   
   # View retry policy configuration
   kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
     cat /etc/hlp-executor/config/retry-policies.yaml
   ```

#### 恢復策略 | Recovery Strategies

##### 策略 A: 等待自動恢復 (配合斷路器)
```bash
# Monitor circuit breaker state transitions
watch -n 5 'kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl -s http://localhost:8080/metrics | grep "circuit_breaker.*quantum"'

# Check half-open retry attempts
kubectl logs -n unmanned-island-system deployment/hlp-executor-core -f | \
  grep -E "(circuit_breaker|quantum_backend|retry_attempt)"
```

**使用時機 | When to Use**: Quantum backend 短暫故障 | Quantum backend transient failure  
**預期時間 | Expected Time**: 2-5 minutes (根據配置 | Based on configuration)  
**風險等級 | Risk Level**: LOW

##### 策略 B: 手動重啟 Quantum Backend
```bash
# Restart quantum backend deployment
kubectl rollout restart deployment/quantum-backend -n quantum-system

# Wait for rollout to complete
kubectl rollout status deployment/quantum-backend -n quantum-system

# Reset HLP Executor circuit breaker
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl -X POST http://localhost:8081/admin/circuit-breaker/quantum_backend/reset
```

**使用時機 | When to Use**: Quantum backend 無回應或自動恢復失敗 | Quantum backend unresponsive or auto-recovery failed  
**預期時間 | Expected Time**: 1-3 minutes  
**風險等級 | Risk Level**: MEDIUM

##### 策略 C: 降級模式 (跳過量子處理)
```bash
# Enable fallback mode
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl -X POST http://localhost:8081/admin/feature-flags \
  -H "Content-Type: application/json" \
  -d '{"quantum_fallback_enabled": true}'

# Verify fallback is active
kubectl logs -n unmanned-island-system deployment/hlp-executor-core --tail=20 | \
  grep "fallback_mode"

# Monitor execution metrics
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl http://localhost:8080/metrics | grep "hlp_executor_fallback_usage"
```

**使用時機 | When to Use**: 緊急情況需要繼續處理非量子任務 | Emergency need to process non-quantum tasks  
**預期時間 | Expected Time**: < 30 seconds  
**風險等級 | Risk Level**: HIGH (功能降級 | Functionality degraded)

---

## 📞 升級路徑 | Escalation Paths

### 升級矩陣 | Escalation Matrix

| 嚴重性 | 初始響應 | 升級時間 | 升級對象 |
|--------|----------|----------|----------|
| **P1 - Critical** | On-Call SRE | 立即 | Platform Lead → CTO |
| **P2 - High** | On-Call SRE | 15 分鐘 | Platform Lead |
| **P3 - Medium** | 值班工程師 | 1 小時 | Team Lead |
| **P4 - Low** | 值班工程師 | 4 小時 | 無需升級 |

### 升級流程 | Escalation Flow

```mermaid
graph TD
    A[故障檢測 | Fault Detected] --> B{嚴重性評估 | Severity Assessment}
    B -->|P1| C[立即通知 On-Call SRE<br/>Immediately Notify On-Call SRE]
    B -->|P2| D[通知 On-Call SRE<br/>Notify On-Call SRE]
    B -->|P3/P4| E[創建工單<br/>Create Ticket]
    
    C --> F{15分鐘內解決?<br/>Resolved in 15min?}
    F -->|否 No| G[升級至 Platform Lead]
    G --> H{30分鐘內解決?<br/>Resolved in 30min?}
    H -->|否 No| I[升級至 CTO]
    
    D --> J{1小時內解決?<br/>Resolved in 1hr?}
    J -->|否 No| G
    
    F -->|是 Yes| K[事後檢討<br/>Post-Mortem]
    H -->|是 Yes| K
    J -->|是 Yes| K
```

### 聯絡方式 | Contact Information

```yaml
escalation_contacts:
  on_call_sre:
    pagerduty: "https://unmanned-island.pagerduty.com/services/P1234"
    slack: "#sre-on-call"
    phone: "+1-555-0100"
  
  platform_lead:
    email: "platform-lead@unmanned-island.com"
    slack: "@platform-lead"
    phone: "+1-555-0101"
  
  cto:
    email: "cto@unmanned-island.com"
    slack: "@cto"
    phone: "+1-555-0102"
```

---

## 📊 監控與告警 | Monitoring and Alerting

### 關鍵指標 | Key Metrics

```yaml
critical_metrics:
  - name: hlp_executor_kubernetes_api_errors_total
    alert_threshold: "> 5 in 1m"
    severity: P1
  
  - name: hlp_executor_state_persistence_failures_total
    alert_threshold: "> 3 in 5m"
    severity: P2
  
  - name: hlp_executor_quantum_backend_timeouts_total
    alert_threshold: "> 10 in 5m"
    severity: P2
  
  - name: hlp_executor_circuit_breaker_open
    alert_threshold: "== 1"
    severity: P1
```

### Prometheus 查詢範例 | Prometheus Query Examples

```promql
# Circuit breaker open rate
rate(hlp_executor_circuit_breaker_state_changes{state="OPEN"}[5m])

# State persistence failure rate
rate(hlp_executor_state_persistence_failures_total[5m])

# Quantum backend timeout percentage
(rate(hlp_executor_quantum_backend_timeouts_total[5m]) / 
 rate(hlp_executor_quantum_backend_requests_total[5m])) * 100

# Average recovery time
avg(hlp_executor_recovery_duration_seconds) by (failure_type)
```

---

## 🔄 預防措施 | Preventive Measures

### 1. 定期健康檢查 | Regular Health Checks
```bash
# Weekly health check script
#!/bin/bash
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  python3 -m core.safety_mechanisms.checkpoint_manager validate --all

kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl http://localhost:8080/healthz/deep

kubectl top pod -n unmanned-island-system -l app=hlp-executor-core
```

### 2. 容量規劃 | Capacity Planning
- 每月檢查 PVC 使用率 | Monthly PVC utilization review
- 提前擴容 (使用率 > 70%) | Proactive expansion (utilization > 70%)
- 監控 checkpoint 增長趨勢 | Monitor checkpoint growth trend

### 3. 演練 | Drills
- 季度性故障恢復演練 | Quarterly failure recovery drills
- 模擬 Kubernetes API 不可用 | Simulate Kubernetes API unavailable
- 測試備份恢復流程 | Test backup recovery procedures

---

## 📚 參考文件 | Reference Documents

- [HLP Executor Emergency Runbook](./HLP_EXECUTOR_EMERGENCY.md)
- [HLP Executor Maintenance Guide](./HLP_EXECUTOR_MAINTENANCE.md)
- [HLP Executor SLO](../slo/HLP_EXECUTOR_SLO.md)
- [HLP Executor Deployment Checklist](../deployment/HLP_EXECUTOR_DEPLOYMENT_CHECKLIST.md)
- [Safety Mechanisms Configuration](/config/safety-mechanisms.yaml)
- [Monitoring Configuration](/config/monitoring.yaml)

---

**文件維護者 | Document Maintainer**: Platform Engineering Team  
**審核週期 | Review Cycle**: Quarterly  
**下次審核 | Next Review**: 2026-03-07
