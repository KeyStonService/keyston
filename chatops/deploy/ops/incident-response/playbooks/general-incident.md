# 通用事件響應 Playbook

## 🚨 收到告警時

### 第一步: 確認 (0-5 分鐘)

1. **確認告警**
   ```bash
   # 查看告警詳情
   # 確認不是誤報
   ```

2. **初步評估**
   - [ ] 哪些服務受影響？
   - [ ] 多少用戶受影響？
   - [ ] 問題何時開始？
   - [ ] 最近有什麼變更？

3. **確定嚴重性**
   - P0: 全面中斷 → 立即建立 Bridge
   - P1: 重大降級 → 評估是否需要 Bridge
   - P2: 部分影響 → 繼續調查
   - P3: 輕微問題 → 正常處理

### 第二步: 溝通 (5-10 分鐘)

1. **建立事件頻道** (P0/P1)
   ```
   Slack: #inc-YYYYMMDD-brief-description
   ```

2. **發布初始通知**
   ```
   🔴 INCIDENT DECLARED

   Severity: P[X]
   Impact: [簡述影響]
   Status: Investigating

   War Room: #inc-xxxx
   Lead: @oncall-engineer
   ```

3. **通知相關團隊**
   - 使用 @channel 或 @team 提醒
   - P0/P1: 同時電話通知

### 第三步: 調查 (10-30 分鐘)

1. **收集數據**
   ```bash
   # 檢查服務狀態
   kubectl get pods -n chatops
   kubectl get events -n chatops --sort-by='.lastTimestamp'

   # 檢查日誌
   kubectl logs -n chatops -l app=chatops-gateway --tail=100

   # 檢查指標
   # 打開 Grafana dashboard
   ```

2. **常見檢查點**
   - [ ] Pod 狀態和重啟次數
   - [ ] 資源使用 (CPU/Memory)
   - [ ] 網絡連接
   - [ ] 外部依賴狀態
   - [ ] 最近部署或配置變更

3. **記錄發現**
   - 在事件頻道記錄所有發現
   - 使用時間戳標記

### 第四步: 緩解 (視情況)

1. **快速緩解選項**

   **回滾部署**
   ```bash
   kubectl rollout undo deployment/chatops-gateway -n chatops
   kubectl rollout status deployment/chatops-gateway -n chatops
   ```

   **擴容服務**
   ```bash
   kubectl scale deployment/chatops-gateway --replicas=10 -n chatops
   ```

   **重啟服務**
   ```bash
   kubectl rollout restart deployment/chatops-gateway -n chatops
   ```

   **流量切換**
   ```bash
   # 更新 Ingress 規則或 Service
   ```

2. **更新狀態**
   ```
   🟡 MITIGATING

   Action taken: [採取的行動]
   Expected resolution: [預計恢復時間]
   ```

### 第五步: 解決

1. **確認恢復**
   - [ ] 關鍵指標恢復正常
   - [ ] 錯誤率下降到基線
   - [ ] 用戶回報問題解決

2. **穩定觀察**
   - 持續監控 15-30 分鐘
   - 確認沒有復發跡象

3. **宣布解決**
   ```
   🟢 RESOLVED

   Duration: X hours Y minutes
   Root Cause: [簡述]
   Resolution: [採取的措施]

   Post-mortem scheduled: [日期]
   ```

### 第六步: 後續

1. **事件記錄**
   - 完成事件報告
   - 收集所有相關日誌和指標

2. **Post-Mortem**
   - 48-72 小時內安排
   - 邀請所有相關人員

3. **行動項目**
   - 創建 JIRA tickets
   - 分配負責人
   - 設定截止日期

---

## 常用命令速查

### Kubernetes
```bash
# 獲取所有資源狀態
kubectl get all -n chatops

# 查看 Pod 詳情
kubectl describe pod <pod-name> -n chatops

# 查看日誌
kubectl logs -f <pod-name> -n chatops

# 進入容器
kubectl exec -it <pod-name> -n chatops -- /bin/sh

# 查看最近事件
kubectl get events -n chatops --sort-by='.lastTimestamp' | tail -20
```

### 數據庫
```bash
# 連接數據庫
kubectl exec -it <db-pod> -n chatops -- psql -U postgres

# 查看連接數
SELECT count(*) FROM pg_stat_activity;

# 查看慢查詢
SELECT * FROM pg_stat_activity WHERE state = 'active' ORDER BY query_start;
```

### 網絡
```bash
# 測試服務連通性
kubectl run debug --rm -it --image=busybox -- /bin/sh
nslookup <service-name>
wget -qO- http://<service-name>:<port>/health
```

---

## 事件角色

| 角色 | 職責 |
|------|------|
| **Incident Commander** | 統籌協調，決策，對外溝通 |
| **Tech Lead** | 技術方向，分配任務 |
| **Communicator** | 狀態更新，利益相關者溝通 |
| **Scribe** | 記錄時間線，收集信息 |
| **Subject Matter Expert** | 特定領域專家支持 |
