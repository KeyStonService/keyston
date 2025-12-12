# Kubernetes Phase 2 部署配置

## 📋 概覽

Phase 2 是 SynergyMesh 的完整生產級 Kubernetes 部署配置，包含：

- 完整的微服務架構
- 生產級監控系統
- 完善的日誌聚合
- 安全策略和網絡隔離
- 自動備份和災難恢復
- CI/CD 整合

## 🏗️ 架構組件

### 1. 命名空間與 RBAC (`01-namespace-rbac/`)

- **namespace.yaml**: 6 個命名空間（autofix, autofix-dev, autofix-staging,
  monitoring, logging, ingress-nginx）
- **rbac.yaml**: 完整的 RBAC 配置（管理員、開發者、查看者角色）
- **network-policies.yaml**: 網絡微分段策略
- **pod-security-policies.yaml**: Pod 安全策略

### 2. 存儲配置 (`02-storage/`)

- **storage-classes.yaml**: 4 種存儲類（fast-ssd, standard, local-storage, efs）
- **persistent-volume-claims.yaml**: 8 個 PVC（數據庫、緩存、監控、日誌）

### 3. 密鑰與配置 (`03-secrets-config/`)

- **secrets.yaml**: 密鑰模板（數據庫、API 密鑰、TLS 證書）
- **configmaps.yaml**: 應用配置（生產、開發環境）

### 4. 數據庫 (`04-databases/`)

#### PostgreSQL

- **statefulset.yaml**: 生產級配置（連接池、WAL、複製）
- **service.yaml**: Headless Service
- **backup-cronjob.yaml**: 每日自動備份
- **monitoring.yaml**: 監控導出器

#### Redis

- **statefulset.yaml**: 高可用配置（持久化、AOF）
- **service.yaml**: Headless Service
- **monitoring.yaml**: 監控導出器

### 5. 核心服務 (`05-core-services/`)

#### Code Analyzer

- 3 副本，自動擴展 (3-10)
- 資源：2Gi-4Gi 內存，1-2 CPU
- HPA、PDB、網絡策略

#### Vulnerability Detector

- 3 副本，自動擴展 (3-8)
- 資源：4Gi-8Gi 內存，2-4 CPU
- HPA、網絡策略

#### Auto Repair

- 2 副本，自動擴展 (2-6)
- 資源：2Gi-4Gi 內存，1-2 CPU
- HPA、網絡策略

#### Result Aggregator

- 2 副本
- 資源：1Gi-2Gi 內存，500m-1 CPU

#### Orchestrator

- 2 副本
- 資源：2Gi-4Gi 內存，1-2 CPU

#### Contracts L1

- 2 副本，自動擴展 (2-6)
- 資源：512Mi-1Gi 內存，250m-500m CPU
- HPA、PDB、網絡策略
- SLSA 認證與構建溯源服務

### 6. 監控系統 (`06-monitoring/`)

#### Prometheus

- 時序數據庫
- 自動服務發現
- 100Gi 存儲

#### Grafana

- 可視化儀表板
- 預配置數據源（Prometheus、Loki）
- 20Gi 存儲

#### Loki

- 日誌聚合
- 100Gi 存儲

#### Jaeger

- 分布式追蹤
- 端到端可觀測性

#### Alertmanager

- 告警管理
- Slack 整合

#### Node Exporter

- 節點指標收集
- DaemonSet 部署

### 7. 日誌系統 (`07-logging/`)

#### Fluent Bit

- 日誌收集器
- DaemonSet 部署
- 轉發至 Loki

### 8. Ingress Gateway (`08-ingress-gateway/`)

- **ingress-controller.yaml**: NGINX Ingress Controller
- **ingress-rules.yaml**: 路由規則（API、監控）

### 9. 備份與恢復 (`09-backup-recovery/`)

- **velero-backup.yaml**: 每日自動備份
- 30 天保留期

### 10. 測試 (`10-testing/`)

- **performance-tests.yaml**: K6 性能測試

### 11. CI/CD (`11-ci-cd/`)

- **argocd-deployment.yaml**: ArgoCD 部署

### 12. 安全 (`12-security/`)

- **falco-deployment.yaml**: 運行時安全監控
- **trivy-scanner.yaml**: 容器漏洞掃描

## 🚀 快速開始

### 前置要求

```bash
# 工具版本
kubectl >= 1.25
kustomize >= 4.5
helm >= 3.0
```

### 1. 部署到開發環境

```bash
# 應用開發環境配置
kubectl apply -k k8s/phase2/overlays/dev

# 驗證部署
kubectl get pods -n autofix-dev
```

### 2. 部署到預發布環境

```bash
# 應用預發布環境配置
kubectl apply -k k8s/phase2/overlays/staging

# 驗證部署
kubectl get pods -n autofix-staging
```

### 3. 部署到生產環境

```bash
# 創建密鑰（生產環境）
kubectl create secret generic autofix-secrets \
  --from-literal=DATABASE_PASSWORD=$(openssl rand -base64 32) \
  --from-literal=REDIS_PASSWORD=$(openssl rand -base64 32) \
  --from-literal=GITHUB_TOKEN=<YOUR_TOKEN> \
  --from-literal=SNYK_TOKEN=<YOUR_TOKEN> \
  -n autofix

# 應用生產環境配置
kubectl apply -k k8s/phase2/overlays/prod

# 驗證所有 Pod 運行
kubectl get pods -n autofix
kubectl get pods -n monitoring
kubectl get pods -n logging

# 檢查服務狀態
kubectl get svc -n autofix
kubectl get ingress -n autofix
```

## 📊 資源需求

### 開發環境

- **節點**: 3 個
- **CPU**: 12 核心
- **內存**: 24 GB
- **存儲**: 100 GB

### 生產環境

- **節點**: 10-20 個
- **CPU**: 40-80 核心
- **內存**: 80-160 GB
- **存儲**: 500 GB SSD

## 🔧 配置指南

### 自定義域名

編輯 `08-ingress-gateway/ingress-rules.yaml`:

```yaml
spec:
  rules:
    - host: your-domain.com # 修改為你的域名
```

### 調整副本數

編輯對應服務的 HPA 配置：

```yaml
spec:
  minReplicas: 3 # 最小副本數
  maxReplicas: 10 # 最大副本數
```

### 修改資源限制

編輯對應服務的 Deployment：

```yaml
resources:
  requests:
    memory: '2Gi'
    cpu: '1000m'
  limits:
    memory: '4Gi'
    cpu: '2000m'
```

## 🧪 驗證部署

### 檢查 Pod 狀態

```bash
# 查看所有命名空間的 Pod
kubectl get pods --all-namespaces

# 查看特定服務
kubectl get pods -n autofix -l app=code-analyzer

# 查看 Pod 詳情
kubectl describe pod <pod-name> -n autofix

# 查看日誌
kubectl logs -f <pod-name> -n autofix
```

### 測試服務連接

```bash
# 進入測試 Pod
kubectl run -it --rm debug \
  --image=nicolaka/netshoot \
  --restart=Never \
  -n autofix -- sh

# 測試服務
curl http://code-analyzer:8080/health
curl http://vulnerability-detector:8081/health
curl http://auto-repair:8082/health
curl http://orchestrator:8083/health
```

### 檢查監控

```bash
# Port-forward Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000

# 訪問 http://localhost:3000
# 用戶名: admin
# 密碼: admin

# Port-forward Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# 訪問 http://localhost:9090
```

## 📈 監控與告警

### Prometheus 指標

```
http://prometheus:9090/metrics
```

關鍵指標：

- 請求率：`rate(http_requests_total[5m])`
- 錯誤率：`rate(http_errors_total[5m])`
- 延遲：`histogram_quantile(0.95, http_request_duration_seconds_bucket)`
- CPU 使用率：`container_cpu_usage_seconds_total`
- 內存使用率：`container_memory_usage_bytes`

### Grafana 儀表板

預配置儀表板：

1. Kubernetes 集群概覽
2. 應用服務指標
3. 數據庫性能
4. 網絡流量
5. 日誌分析

### 告警規則

Alertmanager 配置的告警：

- Pod 重啟頻繁
- 高 CPU 使用率 (>80%)
- 高內存使用率 (>85%)
- 磁盤空間不足 (<10%)
- 服務不可用

## 🔒 安全最佳實踐

### 1. 網絡隔離

- ✅ 默認拒絕所有入站流量
- ✅ 僅允許必要的服務間通信
- ✅ Ingress 流量經過驗證

### 2. RBAC

- ✅ 最小權限原則
- ✅ 角色分離（管理員、開發者、查看者）
- ✅ ServiceAccount 綁定

### 3. Pod 安全

- ✅ 非 root 用戶運行
- ✅ 只讀根文件系統（部分服務）
- ✅ 資源限制

### 4. 密鑰管理

- ✅ Kubernetes Secrets
- ✅ 環境變量注入
- ✅ 建議使用 External Secrets Operator

### 5. 運行時安全

- ✅ Falco 監控異常行為
- ✅ Trivy 掃描容器漏洞

## 🔧 故障排查

### Pod 無法啟動

```bash
# 查看事件
kubectl get events -n autofix --sort-by='.lastTimestamp'

# 查看 Pod 狀態
kubectl describe pod <pod-name> -n autofix

# 查看日誌
kubectl logs <pod-name> -n autofix --previous
```

### 服務無法訪問

```bash
# 檢查服務端點
kubectl get endpoints -n autofix

# 檢查網絡策略
kubectl get networkpolicy -n autofix

# 測試 DNS
kubectl run -it --rm debug \
  --image=nicolaka/netshoot \
  --restart=Never \
  -n autofix -- nslookup code-analyzer
```

### 數據庫連接問題

```bash
# 查看 PostgreSQL 日誌
kubectl logs -n autofix postgres-0

# 進入 PostgreSQL Pod
kubectl exec -it -n autofix postgres-0 -- psql -U autofix_user -d autofix

# 檢查連接
\conninfo
\l
```

## 🎯 進階操作

### 滾動更新

```bash
# 更新鏡像
kubectl set image deployment/code-analyzer \
  code-analyzer=autofix/code-analyzer:v2.1.0 \
  -n autofix

# 查看滾動更新狀態
kubectl rollout status deployment/code-analyzer -n autofix

# 查看歷史
kubectl rollout history deployment/code-analyzer -n autofix
```

### 回滾部署

```bash
# 回滾到上一版本
kubectl rollout undo deployment/code-analyzer -n autofix

# 回滾到特定版本
kubectl rollout undo deployment/code-analyzer --to-revision=2 -n autofix
```

### 手動擴展

```bash
# 擴展副本數
kubectl scale deployment code-analyzer --replicas=5 -n autofix

# 查看 HPA 狀態
kubectl get hpa -n autofix
```

### 備份數據庫

```bash
# 手動備份
kubectl exec -n autofix postgres-0 -- \
  pg_dump -U autofix_user autofix > backup.sql

# 恢復備份
kubectl exec -i -n autofix postgres-0 -- \
  psql -U autofix_user autofix < backup.sql
```

## 📚 相關文檔

- [Phase 1 實作總結](../../PHASE1_IMPLEMENTATION_SUMMARY.md)
- [Phase 1 驗證報告](../../PHASE1_VALIDATION_REPORT.md)
- [監控指南](../../MONITORING_GUIDE.md)
- [生產就緒檢查清單](../../PRODUCTION_READINESS.md)

## ✅ 部署檢查清單

### 部署前

- [ ] 創建 Kubernetes 集群
- [ ] 安裝必要工具（kubectl, kustomize, helm）
- [ ] 配置密鑰
- [ ] 配置存儲類
- [ ] 安裝 Ingress Controller
- [ ] 配置 DNS

### 部署後

- [ ] 驗證所有 Pod 運行
- [ ] 測試服務健康檢查
- [ ] 配置 Grafana 儀表板
- [ ] 設置告警規則
- [ ] 測試備份策略
- [ ] 進行負載測試
- [ ] 驗證安全策略

## 🔄 更新記錄

- **2025-11-26**: Phase 2 初始發布
  - 完整微服務架構
  - 生產級監控系統
  - 完善的安全策略
  - 自動備份和恢復

## 📞 支持

如有問題，請聯繫：

- **團隊**: SynergyMesh Team
- **郵箱**: <support@synergymesh.com>
- **文檔**: <https://docs.synergymesh.com>

---

**版本**: 2.0.0  
**最後更新**: 2025-11-26  
**維護者**: SynergyMesh Platform Team
