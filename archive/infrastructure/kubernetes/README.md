# Kubernetes Deployment Guide

## 📦 目錄結構

完整的 Kubernetes 生產部署配置，包含 23 個配置文件，2,500+ 行 YAML。

```
k8s/
├── namespace.yaml                    # 命名空間、資源配額、限制範圍
├── configmap.yaml                    # 配置映射（所有服務配置）
├── secrets.yaml                      # 密鑰管理模板
├── storage/
│   ├── pvc.yaml                      # 持久卷聲明（PostgreSQL, Redis, Prometheus, Loki）
│   └── storageclass.yaml             # 存儲類定義（fast-ssd, standard-hdd）
├── database/
│   ├── postgres-statefulset.yaml     # PostgreSQL StatefulSet（3副本）
│   └── postgres-service.yaml         # 數據庫 Headless Service
├── cache/
│   ├── redis-statefulset.yaml        # Redis StatefulSet（3副本）
│   └── redis-service.yaml            # 緩存 Headless Service
├── services/
│   ├── code-analyzer-deployment.yaml       # 代碼分析服務（3副本）
│   ├── vulnerability-detector-deployment.yaml # 漏洞檢測服務（3副本）
│   ├── auto-repair-deployment.yaml         # 自動修復服務（2副本）
│   ├── orchestrator-deployment.yaml        # 編排器服務（2副本）
│   └── services.yaml                       # 所有服務 ClusterIP 定義
├── monitoring/
│   ├── prometheus-deployment.yaml          # Prometheus 監控
│   ├── grafana-deployment.yaml             # Grafana 儀表板
│   ├── loki-deployment.yaml                # Loki 日誌聚合
│   ├── jaeger-deployment.yaml              # Jaeger 分布式追蹤
│   └── monitoring-services.yaml            # 監控服務定義
├── ingress/
│   ├── ingress.yaml                        # NGINX Ingress 路由配置
│   └── cert-manager.yaml                   # Let's Encrypt SSL 證書
├── rbac/
│   ├── serviceaccount.yaml                 # ServiceAccount
│   ├── role.yaml                           # Role（最小權限）
│   └── rolebinding.yaml                    # RoleBinding
├── hpa/
│   ├── hpa.yaml                            # 水平自動擴展（4個服務）
│   └── vpa.yaml                            # 垂直自動擴展
├── network-policies/
│   └── network-policy.yaml                 # 網絡安全策略
├── kustomization.yaml                      # Kustomize 基礎配置
└── overlays/
    ├── dev/kustomization.yaml              # 開發環境覆蓋
    ├── staging/kustomization.yaml          # 預發布環境覆蓋
    └── prod/kustomization.yaml             # 生產環境覆蓋
```

---

## 🚀 快速開始

### 前置要求

- Kubernetes 集群（≥1.25）
- kubectl（≥1.25）
- kustomize（≥4.5）
- Helm（可選，用於安裝 cert-manager、ingress-nginx）

### 1. 創建密鑰

```bash
# 創建命名空間
kubectl create namespace autofix-bot

# 創建密鑰（替換為實際密碼）
kubectl create secret generic autofix-bot-secrets \
  --from-literal=db-username=autofix_bot \
  --from-literal=db-password=<STRONG_PASSWORD> \
  --from-literal=redis-password=<STRONG_PASSWORD> \
  --from-literal=sonarqube-token=<YOUR_TOKEN> \
  --from-literal=snyk-token=<YOUR_TOKEN> \
  --from-literal=github-token=<YOUR_TOKEN> \
  --from-literal=encryption-key=$(openssl rand -hex 16) \
  -n autofix-bot
```

### 2. 部署至開發環境

```bash
# 應用開發環境配置
kubectl apply -k k8s/overlays/dev

# 驗證部署
kubectl get pods -n autofix-bot-dev
kubectl get svc -n autofix-bot-dev
```

### 3. 部署至生產環境

```bash
# 更新配置（如需要）
vim k8s/configmap.yaml
vim k8s/ingress/ingress.yaml  # 修改域名

# 應用生產環境配置
kubectl apply -k k8s/overlays/prod

# 驗證所有 Pod 運行
kubectl get pods -n autofix-bot

# 查看服務狀態
kubectl get svc -n autofix-bot

# 檢查 Ingress
kubectl get ingress -n autofix-bot
```

---

## 📊 資源需求

### 最小集群要求

#### 開發環境

- **節點**: 3 個
- **CPU**: 12 核心
- **內存**: 24 GB
- **存儲**: 100 GB

#### 生產環境

- **節點**: 10 個（可擴展至 20）
- **CPU**: 40 核心（可擴展至 80）
- **內存**: 80 GB（可擴展至 160）
- **存儲**: 500 GB SSD

### 服務資源分配

| 服務 | 副本 | CPU 請求 | CPU 限制 | 內存請求 | 內存限制 |
|------|------|----------|----------|----------|----------|
| Code Analyzer | 3 | 1 | 2 | 2Gi | 4Gi |
| Vulnerability Detector | 3 | 2 | 4 | 4Gi | 8Gi |
| Auto Repair | 2 | 1 | 2 | 2Gi | 4Gi |
| Orchestrator | 2 | 1 | 2 | 2Gi | 4Gi |
| PostgreSQL | 3 | 2 | 4 | 4Gi | 8Gi |
| Redis | 3 | 1 | 2 | 2Gi | 4Gi |
| Prometheus | 1 | 2 | 4 | 4Gi | 8Gi |
| Grafana | 1 | 0.5 | 1 | 1Gi | 2Gi |
| Loki | 1 | 1 | 2 | 2Gi | 4Gi |
| Jaeger | 1 | 1 | 2 | 2Gi | 4Gi |

---

## 🔧 配置說明

### ConfigMap

包含所有服務的配置：

- 數據庫連接
- Redis 配置
- 服務端口
- 分析和修復配置
- 監控配置
- SLSA Level 3 配置

### Secrets

敏感數據（需要手動創建）：

- 數據庫密碼
- Redis 密碼
- API 密鑰（SonarQube, Snyk, GitHub）
- 加密密鑰

### Ingress

路由配置：

- `/api/analyze` → Code Analyzer
- `/api/scan` → Vulnerability Detector
- `/api/repair` → Auto Repair
- `/api/orchestrate` → Orchestrator
- `/grafana` → Grafana 儀表板
- `/prometheus` → Prometheus UI

### HPA（自動擴展）

- **Code Analyzer**: 3-10 副本（CPU 70%, 內存 80%）
- **Vulnerability Detector**: 3-8 副本（CPU 75%）
- **Auto Repair**: 2-6 副本（CPU 70%）
- **Orchestrator**: 2-5 副本（CPU 60%）

---

## 🧪 驗證與測試

### 1. 檢查 Pod 狀態

```bash
# 查看所有 Pod
kubectl get pods -n autofix-bot

# 查看特定服務
kubectl get pods -n autofix-bot -l app=code-analyzer

# 查看 Pod 詳情
kubectl describe pod <pod-name> -n autofix-bot

# 查看 Pod 日誌
kubectl logs -f <pod-name> -n autofix-bot
```

### 2. 測試服務健康

```bash
# 進入測試 Pod
kubectl run -it --rm test-pod \
  --image=curlimages/curl \
  --restart=Never \
  -n autofix-bot -- sh

# 在 Pod 內測試服務
curl http://code-analyzer:8080/health
curl http://vulnerability-detector:8081/health
curl http://auto-repair:8082/health
curl http://orchestrator:8083/health
```

### 3. 測試 Ingress

```bash
# 獲取 Ingress 地址
kubectl get ingress -n autofix-bot

# 測試端點
curl https://autofix-bot.example.com/api/analyze/health
curl https://autofix-bot.example.com/api/scan/health
```

### 4. 負載測試

```bash
# 使用 hey 進行負載測試
hey -n 10000 -c 100 https://autofix-bot.example.com/api/analyze

# 監控 HPA 擴展
kubectl get hpa -n autofix-bot -w
```

---

## 📈 監控與日誌

### Prometheus

- **URL**: `https://autofix-bot.example.com/prometheus`
- **指標**: 請求率、錯誤率、延遲、資源使用

### Grafana

- **URL**: `https://autofix-bot.example.com/grafana`
- **默認用戶**: admin
- **密碼**: 查看 secrets

### Loki

- **端點**: `http://loki:3100`
- **日誌聚合**: 所有服務日誌

### Jaeger

- **UI**: 通過 port-forward 訪問
- **追蹤**: 完整的分布式追蹤

```bash
# Port-forward Jaeger UI
kubectl port-forward -n autofix-bot svc/jaeger 16686:16686
# 訪問: http://localhost:16686
```

---

## 🔒 安全最佳實踐

### 已實施的安全措施

1. ✅ **最小權限 RBAC**: 僅授予必要權限
2. ✅ **Network Policies**: 網絡隔離和訪問控制
3. ✅ **Secrets 加密**: 敏感數據加密存儲
4. ✅ **Pod Security**: SecurityContext 配置
5. ✅ **TLS/SSL**: 所有外部通信加密
6. ✅ **資源限制**: 防止資源耗盡攻擊

### Pod Security Context

所有 Pod 使用：

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
```

---

## 🔧 故障排查

### Pod 無法啟動

```bash
# 查看事件
kubectl get events -n autofix-bot --sort-by='.lastTimestamp'

# 查看 Pod 狀態
kubectl describe pod <pod-name> -n autofix-bot

# 查看日誌
kubectl logs <pod-name> -n autofix-bot --previous
```

### 服務無法訪問

```bash
# 檢查服務端點
kubectl get endpoints -n autofix-bot

# 測試服務連接
kubectl run -it --rm debug \
  --image=nicolaka/netshoot \
  --restart=Never \
  -n autofix-bot -- sh

# 在 debug Pod 內
curl http://code-analyzer:8080/health
nslookup code-analyzer
```

### 數據庫連接問題

```bash
# 查看 PostgreSQL Pod
kubectl logs -n autofix-bot postgres-0

# 進入 PostgreSQL Pod
kubectl exec -it -n autofix-bot postgres-0 -- psql -U autofix_bot -d autofix_bot
```

---

## 🎯 進階操作

### 更新部署

```bash
# 更新鏡像
kubectl set image deployment/code-analyzer \
  code-analyzer=autofix-bot/code-analyzer:v2.0.0 \
  -n autofix-bot

# 查看滾動更新狀態
kubectl rollout status deployment/code-analyzer -n autofix-bot
```

### 回滾部署

```bash
# 查看歷史
kubectl rollout history deployment/code-analyzer -n autofix-bot

# 回滾
kubectl rollout undo deployment/code-analyzer -n autofix-bot
```

### 擴展服務

```bash
# 手動擴展
kubectl scale deployment code-analyzer --replicas=5 -n autofix-bot

# 查看 HPA 狀態
kubectl get hpa -n autofix-bot
```

### 備份與恢復

```bash
# 備份 PostgreSQL
kubectl exec -n autofix-bot postgres-0 -- \
  pg_dump -U autofix_bot autofix_bot > backup.sql

# 恢復
kubectl exec -i -n autofix-bot postgres-0 -- \
  psql -U autofix_bot autofix_bot < backup.sql
```

---

## 📚 相關文檔

- [Phase 1 實作總結](../PHASE1_IMPLEMENTATION_SUMMARY.md)
- [Phase 1 驗證報告](../PHASE1_VALIDATION_REPORT.md)
- [自動修復配置](../auto-fix-bot.yml)
- [Agent 架構](../agent/)
- [JSON Schemas](../schemas/)

---

## ✅ 檢查清單

### 部署前

- [ ] 創建 Kubernetes 集群
- [ ] 安裝 kubectl 和 kustomize
- [ ] 創建密鑰
- [ ] 配置存儲類
- [ ] 安裝 Ingress Controller
- [ ] 安裝 cert-manager

### 部署後

- [ ] 驗證所有 Pod 運行
- [ ] 測試服務健康檢查
- [ ] 配置 Grafana 儀表板
- [ ] 設置告警規則
- [ ] 配置備份策略
- [ ] 負載測試

---

**最後更新**: 2025-11-25  
**版本**: 1.0.0  
**維護者**: SynergyMesh Team
