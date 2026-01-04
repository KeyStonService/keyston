# 故障切換程序

## 概述

本目錄包含各類故障切換的詳細操作程序。

## 故障切換類型

| 類型 | 場景 | 自動/手動 | RTO |
|------|------|-----------|-----|
| Pod 故障 | 容器崩潰 | 自動 | < 1 分鐘 |
| Node 故障 | EC2 實例失效 | 自動 | < 5 分鐘 |
| AZ 故障 | 可用區不可用 | 半自動 | < 15 分鐘 |
| 數據庫故障 | RDS 主節點失效 | 自動 | < 2 分鐘 |
| 區域故障 | AWS 區域不可用 | 手動 | < 4 小時 |

## Pod 故障切換

### 自動恢復機制
- Kubernetes 自動重啟失敗的容器
- Deployment 維持期望副本數
- Liveness probe 檢測不健康 Pod

### 驗證
```bash
# 查看 Pod 重啟歷史
kubectl get pods -n chatops -o wide

# 查看事件
kubectl get events -n chatops --sort-by='.lastTimestamp'
```

## Node 故障切換

### 自動恢復機制
- EKS 自動替換不健康節點
- Pod 自動調度到健康節點
- PodDisruptionBudget 保證最小可用數

### 手動介入 (如需要)
```bash
# 驅逐問題節點上的 Pod
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# 或直接刪除節點 (ASG 會創建新節點)
kubectl delete node <node-name>
```

## 數據庫故障切換

### RDS Multi-AZ 自動故障切換

AWS RDS Multi-AZ 部署自動處理:
1. 主節點故障檢測 (< 30 秒)
2. 自動 DNS 切換到備用節點
3. 備用節點提升為主節點
4. 應用自動重連

### 監控故障切換
```bash
# 查看 RDS 事件
aws rds describe-events \
  --source-identifier chatops-prod \
  --source-type db-instance \
  --duration 60

# 確認當前主節點
aws rds describe-db-instances \
  --db-instance-identifier chatops-prod \
  --query 'DBInstances[0].{Status: DBInstanceStatus, AZ: AvailabilityZone}'
```

### 應用端重連
```bash
# 如果應用未自動重連，重啟 Pod
kubectl rollout restart deployment/chatops-gateway -n chatops
```

## 跨區域故障切換

### 準備工作

1. **確認 DR 區域資源就緒**
   ```bash
   # 檢查 DR 區域 EKS
   aws eks describe-cluster --name chatops-dr --region us-west-2

   # 檢查 DR 數據庫副本
   aws rds describe-db-instances \
     --db-instance-identifier chatops-dr-replica \
     --region us-west-2
   ```

2. **同步最新配置**
   ```bash
   # 確保 DR 區域有最新的 Helm values
   # 確保 Secret 已同步
   ```

### 故障切換步驟

#### Step 1: 宣布災難
```
🔴 DISASTER DECLARED

Region: us-east-1
Impact: Complete service outage
Action: Initiating cross-region failover to us-west-2
```

#### Step 2: 停止主區域流量
```bash
# 更新 Route53 健康檢查
aws route53 update-health-check \
  --health-check-id <id> \
  --disabled

# 或更新 Route53 記錄
aws route53 change-resource-record-sets \
  --hosted-zone-id <zone-id> \
  --change-batch file://failover-dns.json
```

#### Step 3: 提升 DR 數據庫
```bash
# 提升只讀副本為主節點
aws rds promote-read-replica \
  --db-instance-identifier chatops-dr-replica \
  --region us-west-2

# 等待提升完成
aws rds wait db-instance-available \
  --db-instance-identifier chatops-dr-replica \
  --region us-west-2
```

#### Step 4: 更新應用配置
```bash
# 切換到 DR 區域
export AWS_REGION=us-west-2
aws eks update-kubeconfig --name chatops-dr --region us-west-2

# 更新數據庫連接
kubectl set env deployment/chatops-gateway \
  DATABASE_HOST=chatops-dr-replica.xxx.us-west-2.rds.amazonaws.com \
  -n chatops
```

#### Step 5: 驗證服務
```bash
# 檢查 Pod 狀態
kubectl get pods -n chatops

# 運行健康檢查
curl -s https://api-dr.chatops.example.com/health

# 運行功能測試
./scripts/smoke-test.sh dr
```

#### Step 6: 切換 DNS
```bash
# 更新 Route53 指向 DR 區域
aws route53 change-resource-record-sets \
  --hosted-zone-id <zone-id> \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.chatops.example.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "<dr-alb-zone>",
          "DNSName": "<dr-alb-dns>",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }'
```

## 故障恢復 (Failback)

當主區域恢復後:

1. **驗證主區域健康**
2. **同步數據到主區域**
3. **測試主區域服務**
4. **逐步切換流量回主區域**
5. **重建 DR 複製**

## 故障切換測試

每季度進行故障切換測試:
- 數據庫故障切換測試
- 節點故障模擬
- 應用彈性測試

記錄測試結果並更新程序。
