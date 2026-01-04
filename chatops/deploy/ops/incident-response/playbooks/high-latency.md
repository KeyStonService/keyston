# 高延遲事件 Playbook

## 觸發條件
- P95 延遲 > 2 秒
- 平均響應時間 > 1 秒
- 用戶報告應用緩慢

## 診斷流程

### Step 1: 確定影響範圍

1. **檢查整體延遲**
   - Grafana Dashboard: API 延遲面板
   - 確認哪些端點受影響

2. **檢查外部依賴**
   ```
   外部服務狀態頁面:
   - AWS: status.aws.amazon.com
   - 第三方 API: [各服務狀態頁]
   ```

### Step 2: 定位瓶頸

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───▶│   Gateway   │───▶│   Engine    │───▶│  Database   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                         │                   │                  │
                         ▼                   ▼                  ▼
                   檢查 Pod 資源       檢查處理時間        檢查查詢性能
```

**Gateway 層**
```bash
# 檢查 Pod 資源使用
kubectl top pods -n chatops -l app=chatops-gateway

# 檢查請求隊列
kubectl logs -n chatops -l app=chatops-gateway --tail=100 | grep -i "queue\|pending"
```

**Engine 層**
```bash
# 檢查處理延遲
kubectl logs -n chatops -l app=chatops-engine --tail=100 | grep -E "took [0-9]+ms"

# 檢查任務積壓
kubectl exec -it <engine-pod> -n chatops -- curl localhost:8000/metrics | grep queue
```

**Database 層**
```sql
-- 檢查慢查詢
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- 檢查等待事件
SELECT wait_event_type, wait_event, count(*)
FROM pg_stat_activity
WHERE state = 'active'
GROUP BY 1, 2;
```

**Redis 層**
```bash
# 檢查 Redis 延遲
redis-cli --latency

# 檢查慢命令
redis-cli SLOWLOG GET 10
```

### Step 3: 常見原因與解決方案

#### 原因 1: Pod 資源不足

**症狀**
- CPU throttling
- Memory 接近限制
- Pod 重啟

**解決方案**
```bash
# 臨時擴容
kubectl scale deployment/chatops-gateway --replicas=10 -n chatops

# 增加資源限制 (需要修改 values 並部署)
# resources:
#   limits:
#     cpu: "2"
#     memory: 2Gi
```

#### 原因 2: 數據庫查詢慢

**症狀**
- 數據庫 CPU 高
- 特定查詢時間長
- 鎖等待

**解決方案**
```sql
-- 添加缺失索引
CREATE INDEX CONCURRENTLY idx_xxx ON table(column);

-- 終止長時間查詢
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE state = 'active' AND query_start < NOW() - INTERVAL '5 minutes';
```

#### 原因 3: 外部 API 延遲

**症狀**
- 外部調用超時
- 特定功能延遲
- 第三方服務降級

**解決方案**
```bash
# 啟用 fallback 模式
kubectl set env deployment/chatops-gateway EXTERNAL_API_FALLBACK=true -n chatops

# 減少超時時間
kubectl set env deployment/chatops-gateway EXTERNAL_API_TIMEOUT=5s -n chatops
```

#### 原因 4: 流量突增

**症狀**
- 請求數突然增加
- 所有服務同時變慢
- 可能有惡意流量

**解決方案**
```bash
# 自動擴容已啟用情況下
kubectl get hpa -n chatops

# 手動擴容
kubectl scale deployment/chatops-gateway --replicas=20 -n chatops

# 如果是惡意流量，啟用限流
# 更新 Ingress 配置或 WAF 規則
```

#### 原因 5: 網絡問題

**症狀**
- 服務間通信延遲
- DNS 解析慢
- TCP 重傳增加

**解決方案**
```bash
# 檢查 DNS 解析
kubectl run debug --rm -it --image=busybox -- nslookup chatops-gateway.chatops.svc.cluster.local

# 檢查服務端點
kubectl get endpoints -n chatops

# 檢查網絡策略
kubectl get networkpolicies -n chatops
```

### Step 4: 緩解措施優先級

1. **立即擴容** - 最快的緩解方式
2. **啟用緩存** - 減少後端負載
3. **降級非核心功能** - 保護核心路徑
4. **限流** - 防止過載
5. **回滾最近變更** - 如果與最近部署相關

### Step 5: 監控恢復

```bash
# 持續觀察延遲指標
watch -n 5 'kubectl top pods -n chatops'

# 檢查錯誤率
kubectl logs -n chatops -l app=chatops-gateway --tail=100 | grep -c ERROR
```

## 恢復確認

- [ ] P95 延遲 < 500ms
- [ ] 平均響應時間 < 200ms
- [ ] 錯誤率 < 0.1%
- [ ] 無請求積壓
- [ ] 資源使用正常
- [ ] 用戶回報問題解決

## 後續優化

- 分析延遲根本原因
- 更新告警閾值
- 考慮增加基線容量
- 檢討 SLO 是否合理
