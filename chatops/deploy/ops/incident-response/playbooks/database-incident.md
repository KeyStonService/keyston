# 數據庫事件 Playbook

## 場景: 數據庫連接問題

### 症狀
- 應用日誌顯示 "connection refused" 或 "too many connections"
- 響應時間突然增加
- 數據庫相關錯誤率上升

### 診斷步驟

1. **檢查 RDS 狀態**
   ```bash
   aws rds describe-db-instances --db-instance-identifier chatops-prod
   ```

2. **檢查連接數**
   ```sql
   SELECT count(*) FROM pg_stat_activity;
   SELECT max_conn FROM (SELECT setting::int AS max_conn FROM pg_settings WHERE name = 'max_connections') t;
   ```

3. **查看活躍連接**
   ```sql
   SELECT
     pid,
     usename,
     application_name,
     client_addr,
     state,
     query_start,
     query
   FROM pg_stat_activity
   WHERE state != 'idle'
   ORDER BY query_start;
   ```

### 緩解措施

**連接數過多**
```sql
-- 終止空閒連接
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND query_start < NOW() - INTERVAL '10 minutes';

-- 終止長時間運行的查詢
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'active'
  AND query_start < NOW() - INTERVAL '30 minutes';
```

**應用端調整**
```bash
# 減少連接池大小
kubectl set env deployment/chatops-gateway DATABASE_POOL_SIZE=5 -n chatops
```

---

## 場景: 數據庫性能下降

### 症狀
- 查詢響應時間增加
- CPU 使用率高
- 磁盤 I/O 增加

### 診斷步驟

1. **查看 RDS 性能指標**
   - CloudWatch: CPU, Memory, IOPS, Connections
   - Performance Insights: Top SQL, Wait events

2. **識別慢查詢**
   ```sql
   SELECT
     query,
     calls,
     total_time,
     mean_time,
     rows
   FROM pg_stat_statements
   ORDER BY total_time DESC
   LIMIT 20;
   ```

3. **檢查鎖等待**
   ```sql
   SELECT
     blocked_locks.pid AS blocked_pid,
     blocked_activity.usename AS blocked_user,
     blocking_locks.pid AS blocking_pid,
     blocking_activity.usename AS blocking_user,
     blocked_activity.query AS blocked_statement
   FROM pg_catalog.pg_locks blocked_locks
   JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
   JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
   JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
   WHERE NOT blocked_locks.granted;
   ```

### 緩解措施

**終止問題查詢**
```sql
SELECT pg_cancel_backend(<pid>);  -- 嘗試取消
SELECT pg_terminate_backend(<pid>);  -- 強制終止
```

**臨時增加資源**
```bash
# 修改 RDS 實例類型 (需要維護窗口或接受短暫中斷)
aws rds modify-db-instance \
  --db-instance-identifier chatops-prod \
  --db-instance-class db.r6g.2xlarge \
  --apply-immediately
```

**啟用讀副本分流**
```bash
# 確認讀副本狀態
aws rds describe-db-instances --db-instance-identifier chatops-prod-read
```

---

## 場景: 數據庫主節點故障

### 症狀
- 所有數據庫連接失敗
- RDS 事件顯示故障切換
- 應用無法寫入數據

### 診斷步驟

1. **檢查 RDS 事件**
   ```bash
   aws rds describe-events \
     --source-identifier chatops-prod \
     --source-type db-instance \
     --duration 60
   ```

2. **確認當前主節點**
   ```bash
   aws rds describe-db-instances \
     --db-instance-identifier chatops-prod \
     --query 'DBInstances[0].DBInstanceStatus'
   ```

### 緩解措施

**等待自動故障切換**
- Multi-AZ 部署通常在 1-2 分鐘內完成切換
- 監控 RDS 事件確認切換完成

**手動故障切換** (如需要)
```bash
aws rds reboot-db-instance \
  --db-instance-identifier chatops-prod \
  --force-failover
```

**應用端重連**
```bash
# 重啟應用 Pod 以重新建立連接
kubectl rollout restart deployment/chatops-gateway -n chatops
kubectl rollout restart deployment/chatops-engine -n chatops
```

---

## 場景: 數據庫存儲空間不足

### 症狀
- 寫入操作失敗
- 告警: "Storage space running low"
- 數據庫進入只讀模式

### 診斷步驟

1. **檢查存儲使用**
   ```bash
   aws cloudwatch get-metric-statistics \
     --namespace AWS/RDS \
     --metric-name FreeStorageSpace \
     --dimensions Name=DBInstanceIdentifier,Value=chatops-prod \
     --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
     --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
     --period 300 \
     --statistics Average
   ```

2. **識別大表**
   ```sql
   SELECT
     schemaname,
     tablename,
     pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
   FROM pg_tables
   ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
   LIMIT 20;
   ```

### 緩解措施

**緊急擴容**
```bash
aws rds modify-db-instance \
  --db-instance-identifier chatops-prod \
  --allocated-storage 500 \
  --apply-immediately
```

**清理空間**
```sql
-- 清理過期數據
DELETE FROM logs WHERE created_at < NOW() - INTERVAL '90 days';

-- VACUUM 回收空間
VACUUM FULL logs;

-- 刪除未使用的索引
DROP INDEX IF EXISTS idx_unused;
```

---

## 恢復確認檢查清單

- [ ] 數據庫可連接
- [ ] 讀寫操作正常
- [ ] 連接池健康
- [ ] 應用錯誤率恢復正常
- [ ] 性能指標正常
- [ ] 告警已清除
