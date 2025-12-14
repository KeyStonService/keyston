# Contracts Service 運維手冊 (Runbook)

## 概述

本文件為 Contracts Service 的運維手冊，提供常見問題診斷與修復步驟。

## 服務資訊

- **服務名稱**: contracts-service
- **端口**: 3000
- **健康檢查**: `/healthz`, `/readyz`
- **指標端點**: `/metrics`
- **團隊**: contracts-team

## 快速診斷

### 檢查服務狀態

```bash
# 檢查 Pod 狀態
kubectl get pods -l app=contracts-service

# 檢查服務日誌
kubectl logs -l app=contracts-service --tail=100

# 檢查事件
kubectl get events --sort-by='.lastTimestamp' | grep contracts-service
```

### 健康檢查

```bash
# 本地檢查
curl http://localhost:3000/healthz

# Kubernetes 內檢查
kubectl port-forward svc/contracts-service 3000:80
curl http://localhost:3000/healthz
```

## 常見問題與解決方案

### 1. Pod 無法啟動

#### 症狀

- Pod 狀態為 `CrashLoopBackOff` 或 `Error`
- 健康檢查失敗

#### 診斷步驟

```bash
# 查看 Pod 詳細資訊
kubectl describe pod <pod-name>

# 查看日誌
kubectl logs <pod-name> --previous

# 檢查資源限制
kubectl top pod <pod-name>
```

#### 可能原因與解決方案

1. **映像拉取失敗**

   ```bash
   # 檢查映像是否存在
   docker pull ghcr.io/we-can-fix/synergymesh/contracts-service:latest
   
   # 檢查 ImagePullSecrets
   kubectl get secret -n default
   ```

2. **資源不足**

   ```bash
   # 檢查節點資源
   kubectl top nodes
   
   # 調整資源請求
   kubectl edit deployment contracts-service
   ```

3. **配置錯誤**

   ```bash
   # 檢查環境變數
   kubectl get deployment contracts-service -o yaml | grep -A 10 env:
   ```

### 2. 高錯誤率

#### 症狀

- 告警: `ContractsServiceHighErrorRate`
- 5xx 錯誤率超過 5%

#### 診斷步驟

```bash
# 查看最近的錯誤日誌
kubectl logs -l app=contracts-service --tail=200 | grep -i error

# 檢查指標
curl http://localhost:3000/metrics | grep http_requests_total

# 查看最近的 API 調用
kubectl logs -l app=contracts-service --tail=100 | grep "POST\|GET\|PUT\|DELETE"
```

#### 可能原因與解決方案

1. **外部依賴失敗**
   - 檢查與外部 API 的連接
   - 檢查 DNS 解析
   - 驗證 API 憑證

2. **資料庫連接問題**
   - 檢查資料庫連接字串
   - 驗證資料庫可用性
   - 檢查連接池配置

3. **程式碼 Bug**
   - 檢查最近的程式碼變更
   - 查看錯誤堆疊追蹤
   - 回滾到上一個穩定版本

### 3. 高延遲

#### 症狀

- 告警: `ContractsServiceHighLatency`
- P99 延遲超過 1 秒

#### 診斷步驟

```bash
# 檢查資源使用
kubectl top pod -l app=contracts-service

# 查看慢查詢日誌
kubectl logs -l app=contracts-service | grep "duration" | sort -n -k5

# 檢查 HPA 狀態
kubectl get hpa contracts-service-hpa
```

#### 可能原因與解決方案

1. **資源不足**

   ```bash
   # 手動擴展
   kubectl scale deployment contracts-service --replicas=5
   
   # 調整 HPA 配置
   kubectl edit hpa contracts-service-hpa
   ```

2. **外部 API 延遲**
   - 增加超時時間
   - 實施重試機制
   - 考慮快取策略

3. **資料庫查詢慢**
   - 檢查索引
   - 優化查詢
   - 增加連接池大小

### 4. Pod 頻繁重啟

#### 症狀

- 告警: `ContractsServiceFrequentRestarts`
- Pod 重啟次數持續增加

#### 診斷步驟

```bash
# 查看重啟原因
kubectl describe pod <pod-name> | grep -A 5 "Last State"

# 檢查 OOMKilled
kubectl describe pod <pod-name> | grep OOMKilled

# 查看資源使用趨勢
kubectl top pod -l app=contracts-service --containers
```

#### 可能原因與解決方案

1. **記憶體洩漏 (OOMKilled)**

   ```bash
   # 增加記憶體限制
   kubectl set resources deployment contracts-service \
     --limits=memory=1Gi
   ```

2. **健康檢查太嚴格**

   ```bash
   # 調整探針配置
   kubectl edit deployment contracts-service
   # 增加 initialDelaySeconds 和 failureThreshold
   ```

3. **應用程式崩潰**
   - 檢查錯誤日誌
   - 查看堆疊追蹤
   - 啟用詳細日誌級別

### 5. 記憶體使用率高

#### 症狀

- 告警: `ContractsServiceHighMemoryUsage`
- 記憶體使用超過 90%

#### 診斷步驟

```bash
# 檢查記憶體使用
kubectl top pod -l app=contracts-service

# 查看記憶體趨勢
kubectl get --raw /apis/metrics.k8s.io/v1beta1/namespaces/default/pods
```

#### 解決方案

```bash
# 1. 增加記憶體限制
kubectl set resources deployment contracts-service \
  --limits=memory=768Mi --requests=memory=256Mi

# 2. 重啟 Pod 釋放記憶體
kubectl rollout restart deployment contracts-service

# 3. 調查記憶體洩漏
# 啟用 Node.js heap dump
kubectl set env deployment/contracts-service NODE_OPTIONS="--max-old-space-size=512 --heapsnapshot-signal=SIGUSR2"
```

### 6. CPU 使用率高

#### 症狀

- 告警: `ContractsServiceHighCPUUsage`
- CPU 使用超過 90%

#### 診斷步驟

```bash
# 檢查 CPU 使用
kubectl top pod -l app=contracts-service

# 查看 CPU 節流
kubectl describe pod <pod-name> | grep -i cpu
```

#### 解決方案

```bash
# 1. 水平擴展
kubectl scale deployment contracts-service --replicas=5

# 2. 增加 CPU 限制
kubectl set resources deployment contracts-service \
  --limits=cpu=1000m --requests=cpu=200m

# 3. 檢查 CPU 密集型操作
kubectl logs -l app=contracts-service | grep -i "processing\|compute"
```

## 緊急回滾

### 回滾到上一個版本

```bash
# 查看部署歷史
kubectl rollout history deployment contracts-service

# 回滾到上一個版本
kubectl rollout undo deployment contracts-service

# 回滾到特定版本
kubectl rollout undo deployment contracts-service --to-revision=3
```

### 暫停流量

```bash
# 縮減到 0 副本
kubectl scale deployment contracts-service --replicas=0

# 刪除 Service (阻止流量)
kubectl delete service contracts-service
```

## 監控與告警

### Prometheus 查詢

```promql
# 錯誤率
rate(http_requests_total{job="contracts-service",status=~"5.."}[5m])

# 延遲 P99
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# CPU 使用率
rate(container_cpu_usage_seconds_total{pod=~"contracts-service-.*"}[5m])

# 記憶體使用率
container_memory_usage_bytes{pod=~"contracts-service-.*"}
```

### 告警配置位置

- 告警規則: `deploy/alerts.yaml`
- Grafana 儀表板: (待建立)

## 聯絡資訊

- **團隊**: contracts-team
- **Email**: <contracts-team@example.com>
- **Slack**: #contracts-service
- **On-call**: PagerDuty escalation policy

## 相關文件

- [架構文件](./architecture.zh.md)
- [API 文件](../README.md)
- [部署指南](../../../../docs/production-deployment-guide.zh.md)
- [SBOM](../sbom/README.md)

## 變更歷史

- 2025-11-24: 初始版本建立
