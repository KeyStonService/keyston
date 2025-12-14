# HLP Executor 緊急應變手冊 | HLP Executor Emergency Runbook

**文件版本 | Document Version**: 1.0.0  
**最後更新 | Last Updated**: 2025-12-07  
**負責團隊 | Responsible Team**: SRE / Incident Response  
**緊急聯絡 | Emergency Contact**: PagerDuty Service ID: P1234

---

## 📋 文件目的 | Document Purpose

本文件定義 HLP Executor 的緊急應變程序，包含 P1/P2 級別事件的症狀識別、診斷步驟、恢復措施和升級路徑。

This document defines emergency response procedures for HLP Executor, including symptom identification, diagnostic steps, recovery actions, and escalation paths for P1/P2 incidents.

---

## 🚨 緊急等級定義 | Emergency Level Definitions

| 等級 | 名稱 | 定義 | 響應時間 | 恢復目標 (RTO) |
|------|------|------|----------|----------------|
| **P1** | Critical | 服務完全中斷 | < 5 分鐘 | < 30 秒 |
| **P2** | High | 服務功能受損 | < 15 分鐘 | < 5 分鐘 |
| **P3** | Medium | 服務性能下降 | < 1 小時 | < 30 分鐘 |
| **P4** | Low | 輕微問題 | < 4 小時 | < 2 小時 |

---

## 🔴 P1: executor-core-down (所有副本不健康 | All Replicas Unhealthy)

### ⚠️ 嚴重性標識 | Severity Indicators

```
🚨 CRITICAL - P1 INCIDENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
服務狀態 | Service Status: DOWN
影響範圍 | Impact: 100% (所有 HLP 執行停止)
檢測時間 | Detected: <TIMESTAMP>
響應團隊 | Response Team: On-Call SRE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 🎯 症狀識別 | Symptom Identification

#### 自動檢測 | Automatic Detection
```yaml
alerting_rules:
  - alert: HLPExecutorAllReplicasDown
    expr: |
      sum(up{job="hlp-executor-core"}) == 0
    for: 1m
    severity: P1
    annotations:
      summary: "All HLP Executor replicas are down"
      description: "All {{ $labels.namespace }}/{{ $labels.deployment }} replicas are unhealthy"
```

#### 明顯症狀 | Observable Symptoms
- ❌ 所有 `/healthz` 端點返回 503 或無回應 | All `/healthz` endpoints return 503 or no response
- ❌ Prometheus 顯示 0 個健康副本 | Prometheus shows 0 healthy replicas
- ❌ kubectl 顯示所有 Pod 處於 CrashLoopBackOff、Error 或 Pending 狀態
- ❌ 用戶報告無法提交新的 HLP 執行 | Users report inability to submit new HLP executions
- ❌ 監控儀表板顯示服務完全離線 | Monitoring dashboard shows service completely offline

#### 業務影響 | Business Impact
- 🚫 所有新的 HLP 執行請求被拒絕 | All new HLP execution requests rejected
- 🚫 進行中的執行可能中斷 | In-progress executions may be interrupted
- 🚫 狀態同步停止 | State synchronization stopped
- 📉 SLO 違反: Availability < 99.9% | SLO violation: Availability < 99.9%

### 🔍 診斷步驟 | Diagnostic Steps

#### 第一步：快速狀態檢查 (< 30 秒)
```bash
# 1. Check pod status
kubectl get pods -n unmanned-island-system -l app=hlp-executor-core

# 2. Quick event check
kubectl get events -n unmanned-island-system --sort-by='.lastTimestamp' | grep hlp-executor | tail -10

# 3. Check deployment status
kubectl describe deployment hlp-executor-core -n unmanned-island-system | tail -30

# Expected output analysis:
# - All pods in CrashLoopBackOff → Application crash (proceed to Step 2)
# - All pods in Pending → Resource/scheduling issue (proceed to Step 3)
# - All pods in Error → Configuration issue (proceed to Step 4)
```

#### 第二步：應用層診斷 (如果 Pod CrashLoopBackOff)
```bash
# 1. Get recent logs from crashed pods
kubectl logs -n unmanned-island-system -l app=hlp-executor-core --tail=200 --all-containers

# 2. Check for common crash patterns
kubectl logs -n unmanned-island-system -l app=hlp-executor-core --tail=500 | \
  grep -E "(FATAL|panic|segfault|OOMKilled|Error:|Exception:)"

# 3. Check previous container logs
for pod in $(kubectl get pods -n unmanned-island-system -l app=hlp-executor-core -o name); do
  echo "=== Previous logs for $pod ==="
  kubectl logs -n unmanned-island-system $pod --previous --tail=100 2>/dev/null || echo "No previous logs"
done

# Common crash reasons to look for:
# - "cannot connect to database" → Database connectivity issue
# - "failed to load configuration" → ConfigMap/Secret issue
# - "OOMKilled" → Memory limit too low
# - "certificate verification failed" → TLS/certificate issue
```

#### 第三步：資源層診斷 (如果 Pod Pending)
```bash
# 1. Check node resources
kubectl top nodes

# 2. Check pod resource requests
kubectl describe pod -n unmanned-island-system -l app=hlp-executor-core | \
  grep -A 5 "Requests:"

# 3. Check scheduler events
kubectl get events -n unmanned-island-system --field-selector involvedObject.kind=Pod | \
  grep -E "(FailedScheduling|Insufficient)"

# 4. Check PVC binding
kubectl get pvc -n unmanned-island-system hlp-executor-state-pvc

# Common reasons:
# - Insufficient CPU/memory on nodes
# - PVC not bound
# - Affinity/anti-affinity rules blocking scheduling
# - Node selector/taint issues
```

#### 第四步：配置層診斷 (如果 Pod Error)
```bash
# 1. Check ConfigMap
kubectl get configmap hlp-executor-config -n unmanned-island-system -o yaml

# 2. Check Secret exists and is valid
kubectl get secret hlp-executor-secrets -n unmanned-island-system

# 3. Verify RBAC
kubectl auth can-i --list --as=system:serviceaccount:unmanned-island-system:hlp-executor-sa

# 4. Check image pull
kubectl describe pod -n unmanned-island-system -l app=hlp-executor-core | \
  grep -E "(Image|ImagePull)"

# Common issues:
# - ConfigMap missing or malformed
# - Secret missing or invalid
# - RBAC permissions insufficient
# - Image pull errors (ImagePullBackOff)
```

### 🛠️ 恢復措施 | Recovery Actions

#### 恢復路徑 A: 快速重啟 (應用層問題)
**使用場景**: 暫時性應用崩潰，配置正確 | Transient application crash, configuration correct

```bash
# Step 1: Force restart all pods
kubectl rollout restart deployment/hlp-executor-core -n unmanned-island-system

# Step 2: Monitor rollout progress (wait up to 60 seconds)
kubectl rollout status deployment/hlp-executor-core -n unmanned-island-system --timeout=60s

# Step 3: Verify health
kubectl get pods -n unmanned-island-system -l app=hlp-executor-core
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl -f http://localhost:8080/healthz

# Step 4: Verify service is accepting requests
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl -f http://localhost:8080/status

# Expected recovery time: 30-60 seconds
```

#### 恢復路徑 B: 配置修復 (配置問題)
**使用場景**: ConfigMap/Secret 錯誤或遺失 | ConfigMap/Secret errors or missing

```bash
# Step 1: Backup current configuration
kubectl get configmap hlp-executor-config -n unmanned-island-system -o yaml > /tmp/hlp-executor-config-backup.yaml

# Step 2: Restore from known-good configuration
kubectl apply -f infrastructure/kubernetes/config/hlp-executor-config.yaml

# Step 3: Verify configuration is valid
kubectl get configmap hlp-executor-config -n unmanned-island-system -o yaml | \
  python3 -m yaml.tool  # Syntax check

# Step 4: Restart pods to pick up new configuration
kubectl rollout restart deployment/hlp-executor-core -n unmanned-island-system

# Step 5: Monitor recovery
kubectl logs -n unmanned-island-system -l app=hlp-executor-core -f --tail=50

# Expected recovery time: 1-2 minutes
```

#### 恢復路徑 C: 資源調整 (資源不足)
**使用場景**: 節點資源不足，Pod 無法調度 | Insufficient node resources, pods cannot be scheduled

```bash
# Step 1: Reduce resource requests temporarily (emergency only!)
kubectl patch deployment hlp-executor-core -n unmanned-island-system -p '
{
  "spec": {
    "template": {
      "spec": {
        "containers": [
          {
            "name": "executor",
            "resources": {
              "requests": {
                "cpu": "250m",
                "memory": "256Mi"
              }
            }
          }
        ]
      }
    }
  }
}'

# Step 2: Scale down replicas temporarily if needed
kubectl scale deployment hlp-executor-core -n unmanned-island-system --replicas=1

# Step 3: Wait for pod to schedule
kubectl wait --for=condition=Ready pod -l app=hlp-executor-core -n unmanned-island-system --timeout=120s

# Step 4: Verify service is functional
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl -f http://localhost:8080/healthz

# ⚠️ IMPORTANT: Scale back up once stable
kubectl scale deployment hlp-executor-core -n unmanned-island-system --replicas=3

# Expected recovery time: 2-3 minutes
```

#### 恢復路徑 D: 緊急回滾 (新版本問題)
**使用場景**: 最近部署的版本導致故障 | Recent deployment caused failure

```bash
# Step 1: Check rollout history
kubectl rollout history deployment/hlp-executor-core -n unmanned-island-system

# Step 2: Rollback to previous version
kubectl rollout undo deployment/hlp-executor-core -n unmanned-island-system

# Step 3: Monitor rollback progress
kubectl rollout status deployment/hlp-executor-core -n unmanned-island-system

# Step 4: Verify health after rollback
kubectl get pods -n unmanned-island-system -l app=hlp-executor-core
kubectl logs -n unmanned-island-system -l app=hlp-executor-core --tail=100

# Step 5: Notify team about version issue
# Post in Slack #incidents channel with version details

# Expected recovery time: 1-2 minutes
```

### 📞 升級路徑 | Escalation Path

```
┌─────────────────────────────────────────────────────────┐
│                   P1 升級路徑 | P1 Escalation Path       │
└─────────────────────────────────────────────────────────┘

T+0:     Alert triggered
         ↓
T+1min:  On-Call SRE notified via PagerDuty
         ↓
T+5min:  If not acknowledged → Escalate to Platform Lead
         ↓
T+15min: If not resolved → Escalate to CTO
         ↓
T+30min: If not resolved → Engage vendor support (if applicable)
```

#### 升級觸發條件 | Escalation Triggers
- ⏱️ **5 分鐘**: On-Call SRE 未響應 | On-Call SRE not responding
- ⏱️ **15 分鐘**: 恢復措施無效 | Recovery actions ineffective
- ⏱️ **30 分鐘**: 需要額外資源或授權 | Additional resources or authorization needed

---

## 🟠 P2: state-corruption-detected (狀態機異常 | State Machine Inconsistent)

### ⚠️ 嚴重性標識 | Severity Indicators

```
⚠️  HIGH PRIORITY - P2 INCIDENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
服務狀態 | Service Status: DEGRADED
影響範圍 | Impact: 部分執行可能失敗或卡住
檢測時間 | Detected: <TIMESTAMP>
響應團隊 | Response Team: On-Call SRE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 🎯 症狀識別 | Symptom Identification

#### 自動檢測 | Automatic Detection
```yaml
alerting_rules:
  - alert: HLPExecutorStateCorruptionDetected
    expr: |
      rate(hlp_executor_state_corruption_total[5m]) > 0
    for: 2m
    severity: P2
    annotations:
      summary: "HLP Executor state corruption detected"
      description: "{{ $value }} corruptions detected in the last 5 minutes"
```

#### 明顯症狀 | Observable Symptoms
- ⚠️ 執行卡在相同階段超過預期時間 | Executions stuck in same phase beyond expected time
- ⚠️ 狀態轉換驗證失敗 | State transition validation failures
- ⚠️ Checkpoint 無法恢復或驗證失敗 | Checkpoints cannot be restored or validation fails
- ⚠️ 日誌中出現 "state_machine_error" 或 "invalid_state_transition" | Logs show "state_machine_error" or "invalid_state_transition"
- ⚠️ Prometheus 顯示異常的狀態轉換延遲 | Prometheus shows abnormal state transition latency

#### 業務影響 | Business Impact
- ⚠️ 部分 HLP 執行可能進入不一致狀態 | Some HLP executions may enter inconsistent state
- ⚠️ 回滾功能可能受損 | Rollback functionality may be impaired
- ⚠️ 執行時間增加 | Execution time increased
- 📊 SLO 影響: State transition latency > P90 50ms | SLO impact: State transition latency > P90 50ms

### 🔍 診斷步驟 | Diagnostic Steps

#### 第一步：識別受影響的執行 (< 1 分鐘)
```bash
# 1. Query for corrupted state metrics
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl -s http://localhost:8080/metrics | grep -E "state_corruption|invalid_state"

# 2. Check execution status via admin API
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl http://localhost:8081/admin/executions?status=STUCK | jq

# 3. Check recent logs for state errors
kubectl logs -n unmanned-island-system -l app=hlp-executor-core --tail=500 | \
  grep -i -E "(state.*corrupt|invalid.*state|checkpoint.*fail)" | tail -20

# 4. List executions with long phase duration
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  python3 -m tools.list_stuck_executions --threshold-minutes 10
```

#### 第二步：驗證 Checkpoint 完整性
```bash
# 1. Run checkpoint validation
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  python3 -m core.safety_mechanisms.checkpoint_manager validate --recent 20

# 2. Check for corrupted checkpoint files
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  find /var/lib/hlp-executor/state/checkpoints -type f -exec file {} \; | \
  grep -v "data"

# 3. Verify checkpoint metadata
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  python3 -m core.safety_mechanisms.checkpoint_manager inspect --checkpoint-id <ID>
```

#### 第三步：分析狀態機日誌
```bash
# 1. Extract state transition logs
kubectl logs -n unmanned-island-system -l app=hlp-executor-core --tail=1000 | \
  grep "state_transition" > /tmp/state_transitions.log

# 2. Analyze for invalid transitions
python3 << 'EOF'
import json
with open('/tmp/state_transitions.log') as f:
    for line in f:
        try:
            log = json.loads(line)
            if log.get('valid') == False:
                print(f"Invalid transition: {log['from_state']} -> {log['to_state']}")
                print(f"  Execution ID: {log.get('execution_id')}")
                print(f"  Reason: {log.get('reason')}")
        except:
            pass
EOF

# 3. Check for concurrent state updates (race conditions)
kubectl logs -n unmanned-island-system -l app=hlp-executor-core --tail=1000 | \
  grep -E "(concurrent_update|race_condition|lock_timeout)"
```

### 🛠️ 恢復措施 | Recovery Actions

#### 恢復路徑 A: 單一執行恢復 (隔離問題)
**使用場景**: 只有少數執行受影響 | Only a few executions affected

```bash
# Step 1: Identify stuck execution IDs
STUCK_EXECUTIONS=$(kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl -s http://localhost:8081/admin/executions?status=STUCK | jq -r '.[].execution_id')

# Step 2: Attempt to recover each execution
for exec_id in $STUCK_EXECUTIONS; do
  echo "Recovering execution: $exec_id"
  
  # Try to rollback to last known good checkpoint
  kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
    python3 -m core.safety_mechanisms.partial_rollback \
    --execution-id "$exec_id" \
    --scope phase \
    --to-checkpoint latest-valid
  
  # Verify recovery
  kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
    curl -s "http://localhost:8081/admin/executions/$exec_id/status" | jq
done

# Expected recovery time: 2-5 minutes per execution
```

#### 恢復路徑 B: 重建狀態索引 (廣泛問題)
**使用場景**: 多個執行受影響，狀態索引可能損壞 | Multiple executions affected, state index may be corrupted

```bash
# Step 1: Enable maintenance mode (new executions queued)
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl -X POST http://localhost:8081/admin/maintenance-mode \
  -d '{"enabled": true, "reason": "state_index_rebuild"}'

# Step 2: Export current state for backup
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  python3 -m core.safety_mechanisms.checkpoint_manager export-all \
  --output /var/lib/hlp-executor/state/backup/state-export-$(date +%s).tar.gz

# Step 3: Rebuild state index
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  python3 -m tools.rebuild_state_index --verify --fix-inconsistencies

# Step 4: Verify index integrity
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  python3 -m tools.verify_state_index --verbose

# Step 5: Disable maintenance mode
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl -X POST http://localhost:8081/admin/maintenance-mode \
  -d '{"enabled": false}'

# Step 6: Resume stuck executions
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl -X POST http://localhost:8081/admin/executions/resume-all

# Expected recovery time: 5-10 minutes
```

#### 恢復路徑 C: 完整回滾與重啟 (嚴重損壞)
**使用場景**: 狀態嚴重損壞，無法在線修復 | Severe corruption, cannot be fixed online

```bash
# Step 1: Stop all new executions (circuit breaker)
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl -X POST http://localhost:8081/admin/circuit-breaker/hlp_execution/open

# Step 2: Wait for in-progress executions to complete or timeout (max 5 min)
watch -n 10 'kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl -s http://localhost:8081/admin/executions?status=RUNNING | jq "length"'

# Step 3: Create full state snapshot before recovery
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  python3 -m core.safety_mechanisms.checkpoint_manager snapshot \
  --type FULL \
  --name "pre-recovery-$(date +%s)"

# Step 4: Restore from last known good full snapshot
LAST_GOOD_SNAPSHOT=$(kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  python3 -m core.safety_mechanisms.checkpoint_manager list --type FULL | \
  grep "VALID" | head -1 | awk '{print $2}')

kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  python3 -m core.safety_mechanisms.checkpoint_manager restore \
  --checkpoint-id "$LAST_GOOD_SNAPSHOT" \
  --verify

# Step 5: Restart HLP Executor pods
kubectl rollout restart deployment/hlp-executor-core -n unmanned-island-system
kubectl rollout status deployment/hlp-executor-core -n unmanned-island-system

# Step 6: Re-enable executions
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl -X POST http://localhost:8081/admin/circuit-breaker/hlp_execution/close

# Expected recovery time: 10-15 minutes
# Data loss: Executions since last snapshot may need to be re-submitted
```

### 📞 升級路徑 | Escalation Path

```
┌─────────────────────────────────────────────────────────┐
│                   P2 升級路徑 | P2 Escalation Path       │
└─────────────────────────────────────────────────────────┘

T+0:     Alert triggered
         ↓
T+5min:  On-Call SRE notified via PagerDuty
         ↓
T+15min: If recovery not progressing → Notify Platform Lead
         ↓
T+1hr:   If not resolved → Escalate to CTO
         ↓
T+2hr:   If not resolved → Schedule incident review
```

---

## 📊 事後處理 | Post-Incident Actions

### 立即行動 (事件解決後 1 小時內)
- [ ] 更新事件追蹤工單狀態 | Update incident tracking ticket status
- [ ] 在 Slack #incidents 頻道發布解決通知 | Post resolution notice in Slack #incidents channel
- [ ] 保存所有診斷日誌和指標 | Preserve all diagnostic logs and metrics
- [ ] 創建初步事件報告 | Create preliminary incident report

### 24 小時內
- [ ] 完成詳細事件報告 (Post-Mortem) | Complete detailed incident report (Post-Mortem)
- [ ] 識別根本原因 | Identify root cause
- [ ] 列出行動項目 (Action Items) | List action items
- [ ] 安排事件檢討會議 | Schedule incident review meeting

### 1 週內
- [ ] 實施預防措施 | Implement preventive measures
- [ ] 更新 Runbook (如果流程有改進) | Update Runbook (if process improved)
- [ ] 更新監控告警規則 (如果需要) | Update monitoring/alerting rules (if needed)
- [ ] 與團隊分享經驗教訓 | Share lessons learned with team

---

## 📞 緊急聯絡方式 | Emergency Contacts

```yaml
emergency_contacts:
  primary_oncall:
    pagerduty: "https://unmanned-island.pagerduty.com/services/P1234-HLP-EXECUTOR"
    slack: "#sre-oncall"
    phone: "+1-555-SRE-0100"
  
  platform_lead:
    name: "Platform Engineering Lead"
    slack: "@platform-lead"
    email: "platform-lead@unmanned-island.com"
    phone: "+1-555-PLAT-101"
  
  cto:
    name: "Chief Technology Officer"
    slack: "@cto"
    email: "cto@unmanned-island.com"
    phone: "+1-555-CTO-0102"
  
  vendor_support:
    kubernetes: "https://support.kubernetes.io"
    cloud_provider: "+1-800-CLOUD-00"
```

---

## 🔗 相關資源 | Related Resources

- [HLP Executor Error Handling Runbook](./HLP_EXECUTOR_ERROR_HANDLING.md)
- [HLP Executor Maintenance Guide](./HLP_EXECUTOR_MAINTENANCE.md)
- [HLP Executor SLO](../slo/HLP_EXECUTOR_SLO.md)
- [Incident Management Process](../../INCIDENT_MANAGEMENT.md)
- [PagerDuty Integration](https://unmanned-island.pagerduty.com)
- [Slack Incident Channel](https://unmanned-island.slack.com/archives/incidents)

---

**文件維護者 | Document Maintainer**: SRE Team  
**審核週期 | Review Cycle**: After each P1/P2 incident  
**緊急更新流程 | Emergency Update Process**: Direct commit + immediate team notification
