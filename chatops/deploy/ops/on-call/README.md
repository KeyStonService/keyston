# On-Call 指南

## 值班職責

### 主要職責
1. **監控告警**: 及時響應 PagerDuty 告警
2. **初步診斷**: 快速評估問題嚴重性
3. **緊急處理**: 執行緩解措施或升級
4. **溝通協調**: 保持利益相關者知情
5. **文檔記錄**: 記錄事件處理過程

### 響應時間 SLA

| 嚴重性 | 響應時間 | 確認時間 |
|--------|----------|----------|
| P0 | 5 分鐘 | 15 分鐘 |
| P1 | 15 分鐘 | 30 分鐘 |
| P2 | 30 分鐘 | 2 小時 |
| P3 | 2 小時 | 下一工作日 |

## 值班準備

### 開始值班前

- [ ] 確認 PagerDuty 通知設置
- [ ] 確認 VPN 連接正常
- [ ] 確認 kubectl 配置有效
- [ ] 確認 AWS 控制台訪問
- [ ] 熟悉最近的變更和部署
- [ ] 確認緊急聯繫人列表

### 工具訪問

| 工具 | URL | 用途 |
|------|-----|------|
| PagerDuty | pagerduty.com/chatops | 告警管理 |
| Grafana | grafana.chatops.example.com | 監控儀表板 |
| AWS Console | console.aws.amazon.com | 基礎設施 |
| Slack | #chatops-oncall | 團隊溝通 |
| Runbooks | deploy/ops/runbooks/ | 操作手冊 |

## 告警響應流程

### 1. 收到告警

```
📟 PagerDuty 告警

[P1] High Error Rate - chatops-gateway
Triggered at: 2024-01-15 14:30 UTC
Error rate: 5.2% (threshold: 1%)
```

### 2. 確認告警

在 PagerDuty 中確認 (Acknowledge) 告警

### 3. 初步評估

```bash
# 快速檢查服務狀態
kubectl get pods -n chatops
kubectl get events -n chatops --sort-by='.lastTimestamp' | tail -10

# 查看錯誤日誌
kubectl logs -n chatops -l app=chatops-gateway --tail=50 | grep -i error
```

### 4. 判斷嚴重性

參考 [嚴重性等級定義](../incident-response/severity-levels.md)

### 5. 採取行動

根據問題類型，參考相應 Runbook:
- [通用事件響應](../incident-response/playbooks/general-incident.md)
- [數據庫事件](../incident-response/playbooks/database-incident.md)
- [高延遲事件](../incident-response/playbooks/high-latency.md)

### 6. 解決或升級

如果無法在 30 分鐘內解決:
- 按升級流程通知下一級
- 繼續協助直到問題解決

## 常見告警和處理

### CPU 使用率高

```bash
# 查看哪些 Pod CPU 高
kubectl top pods -n chatops --sort-by=cpu

# 擴容
kubectl scale deployment/<name> --replicas=+2 -n chatops
```

### 內存使用率高

```bash
# 查看內存使用
kubectl top pods -n chatops --sort-by=memory

# 重啟高內存 Pod
kubectl delete pod <pod-name> -n chatops
```

### 錯誤率上升

```bash
# 查看最近部署
kubectl rollout history deployment/chatops-gateway -n chatops

# 回滾
kubectl rollout undo deployment/chatops-gateway -n chatops
```

### 數據庫連接問題

```bash
# 檢查 RDS 狀態
aws rds describe-db-instances --db-instance-identifier chatops-prod

# 重啟應用重新建立連接
kubectl rollout restart deployment/chatops-gateway -n chatops
```

## 值班結束

### 交接清單

- [ ] 未解決事件狀態
- [ ] 正在進行的變更
- [ ] 需要關注的告警
- [ ] 特殊情況說明

### 交接模板

```
📋 On-Call Handoff

Period: 2024-01-15 00:00 - 2024-01-22 00:00

Events:
- [P1] High latency on 01-17, resolved in 45min (root cause: DB query)
- [P2] Node failure on 01-19, auto-recovered

Ongoing:
- Monitoring increased memory usage on chatops-engine
- Scheduled maintenance on 01-23

Notes:
- New release v1.2.4 deployed on 01-16, watch for regressions
```

## 值班福利

- 值班補貼: $XXX/週
- 替換休假: 值班後可申請補休
- 事件獎金: 成功處理 P0 事件

## 支持資源

- **On-Call 支持群**: #oncall-support
- **技術問題**: 對應團隊 Slack 頻道
- **管理問題**: @engineering-manager
