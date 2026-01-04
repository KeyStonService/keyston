# 備份與恢復指南

## 備份策略總覽

| 資源類型 | 備份頻率 | 保留期限 | 位置 |
|----------|----------|----------|------|
| RDS 數據庫 | 每日自動 + 事務日誌 | 35 天 | AWS 原生 |
| RDS 手動快照 | 每週 | 90 天 | AWS 原生 |
| Redis 快照 | 每日 | 7 天 | AWS 原生 |
| Kubernetes 資源 | 每日 | 30 天 | S3 |
| 配置文件 | Git 版本控制 | 永久 | GitHub |

## RDS 數據庫備份

### 自動備份

AWS RDS 自動備份已配置:
- 備份窗口: 03:00-04:00 UTC
- 保留期: 35 天
- 多區域複製: 啟用

### 手動快照

```bash
# 創建手動快照
aws rds create-db-snapshot \
  --db-instance-identifier chatops-prod \
  --db-snapshot-identifier chatops-prod-$(date +%Y%m%d-%H%M%S)

# 驗證快照
aws rds describe-db-snapshots \
  --db-snapshot-identifier chatops-prod-20240115-120000

# 複製快照到其他區域
aws rds copy-db-snapshot \
  --source-db-snapshot-identifier arn:aws:rds:us-east-1:123456789:snapshot:chatops-prod-20240115 \
  --target-db-snapshot-identifier chatops-prod-20240115-dr \
  --source-region us-east-1 \
  --region us-west-2
```

### 恢復數據庫

#### 從最新自動備份恢復
```bash
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier chatops-prod \
  --target-db-instance-identifier chatops-prod-restored \
  --use-latest-restorable-time
```

#### 恢復到特定時間點
```bash
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier chatops-prod \
  --target-db-instance-identifier chatops-prod-restored \
  --restore-time 2024-01-15T10:00:00Z
```

#### 從快照恢復
```bash
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier chatops-prod-restored \
  --db-snapshot-identifier chatops-prod-20240115-120000 \
  --db-instance-class db.r6g.xlarge \
  --multi-az
```

## Redis 備份

### 創建快照

```bash
# ElastiCache 快照
aws elasticache create-snapshot \
  --replication-group-id chatops-redis \
  --snapshot-name chatops-redis-$(date +%Y%m%d)

# Kubernetes 內 Redis (如使用)
kubectl exec -n chatops redis-master-0 -- redis-cli BGSAVE
kubectl cp chatops/redis-master-0:/data/dump.rdb ./redis-backup.rdb
```

### 恢復 Redis

```bash
# 從 ElastiCache 快照恢復
aws elasticache create-replication-group \
  --replication-group-id chatops-redis-new \
  --replication-group-description "Restored from snapshot" \
  --snapshot-name chatops-redis-20240115

# Kubernetes Redis
kubectl cp ./redis-backup.rdb chatops/redis-master-0:/data/dump.rdb
kubectl delete pod redis-master-0 -n chatops  # 重啟加載
```

## Kubernetes 資源備份

### 使用 Velero 備份

```bash
# 安裝 Velero
velero install \
  --provider aws \
  --bucket chatops-velero-backups \
  --secret-file ./credentials-velero

# 創建備份
velero backup create chatops-full-$(date +%Y%m%d) \
  --include-namespaces chatops

# 定期備份調度
velero schedule create chatops-daily \
  --schedule="0 2 * * *" \
  --include-namespaces chatops \
  --ttl 720h  # 30 天

# 查看備份
velero backup get
```

### 恢復 Kubernetes 資源

```bash
# 查看可用備份
velero backup get

# 恢復整個命名空間
velero restore create --from-backup chatops-full-20240115

# 恢復特定資源
velero restore create --from-backup chatops-full-20240115 \
  --include-resources deployments,services,configmaps
```

### 手動備份 (無 Velero)

```bash
# 導出所有資源
kubectl get all,configmap,secret,pvc -n chatops -o yaml > k8s-backup-$(date +%Y%m%d).yaml

# 導出特定類型
for resource in deployment service configmap secret; do
  kubectl get $resource -n chatops -o yaml > $resource-backup.yaml
done
```

## 配置和代碼備份

### Git 倉庫

所有配置都存儲在 Git:
- Terraform 配置
- Helm charts
- Kubernetes manifests
- CI/CD 配置

### 導出 Secrets

```bash
# 備份 Secrets (加密)
kubectl get secrets -n chatops -o json | \
  sops --encrypt --kms arn:aws:kms:us-east-1:xxx:key/xxx > secrets-backup.enc.json

# 恢復
sops --decrypt secrets-backup.enc.json | kubectl apply -f -
```

## 備份驗證

### 每日檢查

```bash
# RDS 備份檢查
aws rds describe-db-instance-automated-backups \
  --db-instance-identifier chatops-prod

# Velero 備份狀態
velero backup get | head -5
```

### 每週恢復測試

```bash
# 1. 在測試環境恢復 RDS 快照
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier chatops-test-restore \
  --db-snapshot-identifier chatops-prod-latest

# 2. 驗證數據完整性
psql -h chatops-test-restore.xxx.rds.amazonaws.com -U chatops -c "SELECT count(*) FROM users;"

# 3. 清理測試實例
aws rds delete-db-instance \
  --db-instance-identifier chatops-test-restore \
  --skip-final-snapshot
```

## 備份告警

CloudWatch 告警配置:
- RDS 備份失敗
- Velero 備份失敗
- 備份大小異常

## 文檔更新

最後更新: 2024-01-15
下次審查: 2024-04-15
