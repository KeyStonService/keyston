# 數據庫操作 Runbook

## 連接信息

### 生產環境
```bash
# 通過 kubectl port-forward
kubectl port-forward svc/chatops-postgresql 5432:5432 -n chatops

# 連接
psql -h localhost -U chatops -d chatops
```

### 使用 AWS RDS
```bash
# 獲取端點
aws rds describe-db-instances --db-instance-identifier chatops-prod \
  --query 'DBInstances[0].Endpoint'

# 連接
psql -h <endpoint> -U chatops -d chatops
```

## 日常操作

### 查看連接狀態

```sql
-- 當前連接數
SELECT count(*) FROM pg_stat_activity;

-- 連接詳情
SELECT
  pid, usename, application_name, client_addr,
  state, query_start, query
FROM pg_stat_activity
ORDER BY query_start;

-- 按狀態分組
SELECT state, count(*)
FROM pg_stat_activity
GROUP BY state;
```

### 查看數據庫大小

```sql
-- 數據庫總大小
SELECT pg_size_pretty(pg_database_size('chatops'));

-- 表大小排名
SELECT
  schemaname || '.' || tablename AS table,
  pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename)) AS total_size,
  pg_size_pretty(pg_relation_size(schemaname || '.' || tablename)) AS data_size,
  pg_size_pretty(pg_indexes_size(schemaname || '.' || tablename::regclass)) AS index_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname || '.' || tablename) DESC
LIMIT 20;

-- 索引大小
SELECT
  indexrelname AS index,
  pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 20;
```

### 性能分析

```sql
-- 啟用 pg_stat_statements (如未啟用)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 慢查詢 Top 10
SELECT
  query,
  calls,
  round(total_exec_time::numeric, 2) AS total_time_ms,
  round(mean_exec_time::numeric, 2) AS mean_time_ms,
  rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 最頻繁的查詢
SELECT
  query,
  calls,
  round(total_exec_time::numeric, 2) AS total_time_ms
FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 10;

-- 重置統計
SELECT pg_stat_statements_reset();
```

### 鎖分析

```sql
-- 查看當前鎖
SELECT
  l.pid,
  l.locktype,
  l.mode,
  l.granted,
  a.query
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE NOT l.granted;

-- 查看阻塞關係
SELECT
  blocked.pid AS blocked_pid,
  blocked.query AS blocked_query,
  blocking.pid AS blocking_pid,
  blocking.query AS blocking_query
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked ON blocked.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
  AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
  AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
  AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
  AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
  AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
  AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
  AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
  AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
  AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
  AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking ON blocking.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

## 維護操作

### VACUUM 和 ANALYZE

```sql
-- 分析單表
ANALYZE table_name;

-- VACUUM 單表
VACUUM table_name;

-- VACUUM FULL (需要表鎖，生產慎用)
VACUUM FULL table_name;

-- 自動 VACUUM 狀態
SELECT
  relname,
  last_vacuum,
  last_autovacuum,
  last_analyze,
  last_autoanalyze
FROM pg_stat_user_tables;
```

### 索引維護

```sql
-- 查看未使用的索引
SELECT
  schemaname || '.' || relname AS table,
  indexrelname AS index,
  pg_size_pretty(pg_relation_size(indexrelid)) AS size,
  idx_scan AS scans
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexrelid::regclass::text NOT LIKE '%_pkey'
ORDER BY pg_relation_size(indexrelid) DESC;

-- 重建索引 (在線)
REINDEX INDEX CONCURRENTLY index_name;

-- 重建表的所有索引
REINDEX TABLE CONCURRENTLY table_name;
```

### 數據清理

```sql
-- 清理舊日誌數據
DELETE FROM logs
WHERE created_at < NOW() - INTERVAL '90 days';

-- 批量刪除 (避免長事務)
DO $$
DECLARE
  batch_size INT := 10000;
  deleted INT := 1;
BEGIN
  WHILE deleted > 0 LOOP
    DELETE FROM logs
    WHERE id IN (
      SELECT id FROM logs
      WHERE created_at < NOW() - INTERVAL '90 days'
      LIMIT batch_size
    );
    GET DIAGNOSTICS deleted = ROW_COUNT;
    COMMIT;
  END LOOP;
END $$;
```

## 備份與恢復

### 邏輯備份

```bash
# 備份整個數據庫
pg_dump -h <host> -U chatops -d chatops -F c -f chatops_backup.dump

# 備份特定表
pg_dump -h <host> -U chatops -d chatops -t table_name -F c -f table_backup.dump

# 只備份結構
pg_dump -h <host> -U chatops -d chatops --schema-only -f schema.sql

# 只備份數據
pg_dump -h <host> -U chatops -d chatops --data-only -f data.sql
```

### 恢復

```bash
# 恢復 custom 格式備份
pg_restore -h <host> -U chatops -d chatops -c chatops_backup.dump

# 恢復到新數據庫
createdb -h <host> -U chatops chatops_new
pg_restore -h <host> -U chatops -d chatops_new chatops_backup.dump

# 恢復 SQL 格式
psql -h <host> -U chatops -d chatops < backup.sql
```

### AWS RDS 備份

```bash
# 創建手動快照
aws rds create-db-snapshot \
  --db-instance-identifier chatops-prod \
  --db-snapshot-identifier chatops-prod-manual-$(date +%Y%m%d)

# 查看快照
aws rds describe-db-snapshots \
  --db-instance-identifier chatops-prod

# 從快照恢復
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier chatops-prod-restored \
  --db-snapshot-identifier chatops-prod-manual-20240115
```

## 緊急操作

### 終止問題查詢

```sql
-- 取消查詢 (優雅)
SELECT pg_cancel_backend(<pid>);

-- 終止連接 (強制)
SELECT pg_terminate_backend(<pid>);

-- 終止所有來自特定應用的連接
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE application_name = 'problem_app';
```

### 只讀模式

```sql
-- 設置為只讀
ALTER DATABASE chatops SET default_transaction_read_only = on;

-- 恢復讀寫
ALTER DATABASE chatops SET default_transaction_read_only = off;
```
