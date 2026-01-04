# ChatOps 災難恢復計劃

## 概述

本文檔定義 ChatOps 平台的災難恢復 (DR) 策略、流程和恢復目標。

## 恢復目標

| 指標 | 目標 | 說明 |
|------|------|------|
| **RTO** (Recovery Time Objective) | 4 小時 | 最大可接受停機時間 |
| **RPO** (Recovery Point Objective) | 1 小時 | 最大可接受數據丟失時間 |
| **MTTR** (Mean Time To Recovery) | 2 小時 | 平均恢復時間 |

## 災難分類

### 第一級: 服務降級
- 部分功能不可用
- 性能明顯下降
- 不需要切換區域

### 第二級: 區域性故障
- 單一可用區失效
- 需要跨 AZ 故障切換
- 自動故障切換生效

### 第三級: 區域性災難
- 整個 AWS 區域不可用
- 需要跨區域故障切換
- 手動介入恢復

## 基礎設施恢復

### EKS 集群

#### 恢復策略
- 多可用區部署
- 節點自動修復
- 自動擴縮容

#### 恢復步驟 (如需重建)
```bash
# 1. 使用 Terraform 重建
cd deploy/terraform/environments/prod
terraform init
terraform apply

# 2. 配置 kubectl
aws eks update-kubeconfig --name chatops-prod --region us-east-1

# 3. 驗證集群
kubectl get nodes
kubectl get namespaces
```

### RDS 數據庫

#### 恢復策略
- Multi-AZ 自動故障切換
- 自動備份 (每日 + 事務日誌)
- 跨區域只讀副本 (DR)

#### 從快照恢復
```bash
# 1. 查找最新快照
aws rds describe-db-snapshots \
  --db-instance-identifier chatops-prod \
  --query 'DBSnapshots | sort_by(@, &SnapshotCreateTime) | [-1]'

# 2. 從快照恢復
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier chatops-prod-restored \
  --db-snapshot-identifier <snapshot-id> \
  --db-instance-class db.r6g.xlarge \
  --availability-zone us-east-1a

# 3. 等待恢復完成
aws rds wait db-instance-available \
  --db-instance-identifier chatops-prod-restored

# 4. 更新應用配置指向新數據庫
```

#### 跨區域恢復
```bash
# 1. 提升只讀副本為主節點
aws rds promote-read-replica \
  --db-instance-identifier chatops-dr-replica

# 2. 更新 DNS 或應用配置
```

### Redis 緩存

#### 恢復策略
- ElastiCache Multi-AZ
- 自動故障切換
- 定期快照

#### 恢復步驟
```bash
# 從快照恢復
aws elasticache create-replication-group \
  --replication-group-id chatops-redis-restored \
  --replication-group-description "Restored from snapshot" \
  --snapshot-name chatops-redis-snapshot-20240115
```

## 應用層恢復

### 1. 恢復 Kubernetes 資源

```bash
# 從備份恢復
kubectl apply -f backups/chatops-resources-latest.yaml

# 或使用 Helm
helm install chatops-platform ./deploy/helm/charts/chatops-platform \
  --namespace chatops \
  --values ./deploy/helm/charts/chatops-platform/values-prod.yaml
```

### 2. 驗證服務

```bash
# 檢查所有 Pod
kubectl get pods -n chatops

# 檢查服務端點
kubectl get endpoints -n chatops

# 運行健康檢查
curl -s https://api.chatops.example.com/health
```

### 3. 驗證數據完整性

```sql
-- 檢查關鍵表記錄數
SELECT
  'users' AS table_name, count(*) FROM users
UNION ALL
SELECT 'sessions', count(*) FROM sessions
UNION ALL
SELECT 'messages', count(*) FROM messages;

-- 檢查最新記錄時間
SELECT MAX(created_at) FROM messages;
```

## DR 測試計劃

### 季度 DR 演練

1. **準備階段**
   - 通知相關團隊
   - 準備測試環境
   - 備份當前狀態

2. **執行階段**
   - 模擬故障場景
   - 執行恢復步驟
   - 記錄時間和問題

3. **驗證階段**
   - 功能驗證
   - 數據驗證
   - 性能驗證

4. **總結階段**
   - 記錄發現問題
   - 更新 DR 文檔
   - 制定改進計劃

### 測試場景

| 場景 | 頻率 | 預期 RTO |
|------|------|----------|
| 單 Pod 故障 | 每月 | 自動恢復 < 5 分鐘 |
| 單節點故障 | 每月 | 自動恢復 < 10 分鐘 |
| 數據庫故障切換 | 每季 | < 5 分鐘 |
| 完整區域故障 | 每年 | < 4 小時 |

## 聯繫人和職責

| 角色 | 職責 | 聯繫方式 |
|------|------|----------|
| DR Coordinator | 統籌 DR 流程 | @dr-coordinator |
| Infra Lead | 基礎設施恢復 | @infra-lead |
| DBA | 數據庫恢復 | @dba-team |
| App Lead | 應用層恢復 | @app-lead |
| On-Call | 初始響應 | PagerDuty |

## 相關文檔

- [備份恢復指南](backup-restore.md)
- [故障切換程序](failover/README.md)
- [事件響應流程](../incident-response/playbooks/general-incident.md)
