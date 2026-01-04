# 回滾操作 Runbook

## 使用場景

- 新版本部署後發現嚴重問題
- 性能明顯下降
- 錯誤率突然上升
- 功能不符預期

## 回滾決策樹

```
部署後發現問題
       │
       ▼
┌─────────────────┐     是      ┌─────────────────┐
│ 是否影響用戶？   ├────────────▶│   立即回滾      │
└────────┬────────┘              └─────────────────┘
         │ 否
         ▼
┌─────────────────┐     是      ┌─────────────────┐
│ 能否快速修復？   ├────────────▶│   嘗試熱修復    │
└────────┬────────┘              └─────────────────┘
         │ 否
         ▼
┌─────────────────┐
│   回滾到穩定版   │
└─────────────────┘
```

## 回滾步驟

### 方法 1: Kubernetes 原生回滾

```bash
# 查看部署歷史
kubectl rollout history deployment/chatops-gateway -n chatops

# 回滾到上一版本
kubectl rollout undo deployment/chatops-gateway -n chatops

# 回滾到指定版本
kubectl rollout undo deployment/chatops-gateway -n chatops --to-revision=5

# 確認回滾狀態
kubectl rollout status deployment/chatops-gateway -n chatops
```

### 方法 2: Helm 回滾

```bash
# 查看 Helm 發布歷史
helm history chatops-platform -n chatops

# 回滾到上一版本
helm rollback chatops-platform -n chatops

# 回滾到指定版本
helm rollback chatops-platform 5 -n chatops

# 確認回滾
helm status chatops-platform -n chatops
```

### 方法 3: ArgoCD 回滾 (如使用)

```bash
# 列出應用歷史
argocd app history chatops-platform

# 回滾到指定版本
argocd app rollback chatops-platform <history-id>

# 或通過 UI
# ArgoCD Dashboard -> chatops-platform -> History -> Rollback
```

## 回滾後驗證

### 1. 服務健康檢查

```bash
# 檢查 Pod 狀態
kubectl get pods -n chatops -w

# 檢查服務端點
kubectl get endpoints -n chatops

# 測試健康檢查端點
curl -s http://chatops-gateway.chatops.svc.cluster.local/health
curl -s http://chatops-gateway.chatops.svc.cluster.local/ready
```

### 2. 功能驗證

```bash
# 運行核心功能測試
./scripts/smoke-test.sh production

# 驗證關鍵 API
curl -X GET https://api.chatops.example.com/v1/status
```

### 3. 指標確認

- [ ] 錯誤率恢復正常
- [ ] 延遲恢復正常
- [ ] 無新的告警觸發
- [ ] 資源使用穩定

## 回滾通知模板

```
📢 ROLLBACK NOTIFICATION

Service: ChatOps Platform
Rolled back from: v1.2.4
Rolled back to: v1.2.3
Time: 2024-01-15 14:30 UTC
Reason: [簡述原因]

Impact:
- [影響範圍]

Status: Monitoring
Next Steps:
- [後續行動]

Performed by: @engineer
```

## 常見問題

### Q: 回滾後數據庫遷移怎麼辦？

如果新版本包含數據庫遷移，回滾前需要：
1. 確認遷移是否可逆
2. 執行回滾遷移 (如果有)
3. 或保持數據庫狀態，確保舊代碼兼容

### Q: 回滾失敗怎麼辦？

1. 檢查鏡像是否存在
2. 檢查配置是否兼容
3. 檢查 Secret/ConfigMap 依賴
4. 考慮使用更早的穩定版本

### Q: 如何防止意外回滾？

1. 使用 revision 鎖定
2. 配置 minReadySeconds
3. 實施 PodDisruptionBudget
4. 自動化回滾驗證
