# 🏗️ Infrastructure - 基礎設施 / Infrastructure

## 概述 / Overview

`infrastructure/` 目錄包含所有基礎設施配置、容器編排、監控系統和部署清單。

The `infrastructure/` directory contains all infrastructure configuration, container orchestration, monitoring systems, and deployment manifests.

---

## 📁 目錄結構 / Directory Structure

```
infrastructure/
├── README.md                           # 基礎設施說明
│
├── 🐳 kubernetes/                      # Kubernetes 編排
│   ├── README.md
│   ├── manifests/                      # K8s 清單
│   │   ├── namespace.yaml
│   │   ├── configmap.yaml
│   │   ├── secret.yaml
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── ingress.yaml
│   │   ├── pvc.yaml
│   │   └── hpa.yaml                   # 自動伸縮
│   │
│   ├── helm/                           # Helm Chart (可選)
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │
│   ├── kustomize/                      # Kustomize 配置 (可選)
│   │   ├── kustomization.yaml
│   │   ├── base/
│   │   └── overlays/
│   │
│   └── scripts/                        # K8s 腳本
│       ├── deploy.sh
│       ├── rollback.sh
│       └── cleanup.sh
│
├── 📊 monitoring/                      # 監控系統
│   ├── README.md
│   ├── prometheus/
│   │   ├── prometheus.yml              # Prometheus 配置
│   │   ├── rules.yml                   # 告警規則
│   │   └── recording_rules.yml
│   │
│   ├── grafana/
│   │   ├── datasources.yaml
│   │   ├── dashboards/
│   │   │   ├── overview.json
│   │   │   ├── services.json
│   │   │   └── infrastructure.json
│   │   └── provisioning/
│   │
│   ├── alerting/
│   │   ├── alertmanager.yml
│   │   ├── slack-channel.yml
│   │   └── email-template.txt
│   │
│   └── logging/
│       ├── elasticsearch.yml           # Elasticsearch 配置
│       ├── kibana.yml
│       └── logstash.conf
│
├── 🚀 deployment/                      # 部署配置
│   ├── README.md
│   ├── docker-compose.prod.yml         # 生產容器編排
│   ├── docker-compose.staging.yml      # 預發佈容器編排
│   ├── ci-deployment.yaml              # CI/CD 流程
│   ├── canary-deployment.yaml          # 金絲雀部署
│   └── blue-green-deployment.yaml      # 藍綠部署
│
├── 🔄 drift-detection/                 # 漂移檢測
│   ├── README.md
│   ├── drift-detector.py
│   ├── reconciler.py
│   └── config-snapshot.yaml
│
├── 🔐 security/                        # 安全配置
│   ├── README.md
│   ├── network-policy.yaml
│   ├── rbac.yaml
│   ├── pod-security-policy.yaml
│   ├── secrets-encryption.yaml
│   └── ingress-tls.yaml
│
├── 📈 scaling/                         # 伸縮配置
│   ├── README.md
│   ├── hpa.yaml                        # 水平自動伸縮
│   ├── vpa.yaml                        # 垂直自動伸縮
│   └── metrics-server.yaml
│
├── 🔍 observability/                   # 可觀測性
│   ├── README.md
│   ├── jaeger-deployment.yaml          # 分散式追蹤
│   ├── opentelemetry-config.yaml
│   └── metrics-collection.yaml
│
└── scripts/                            # 基礎設施腳本
    ├── setup.sh                        # 環境設置
    ├── validate.sh                     # 配置驗證
    ├── backup.sh                       # 備份
    ├── restore.sh                      # 復原
    └── health-check.sh                 # 健康檢查
```

---

## 🔑 核心功能 / Core Features

### Kubernetes 編排 (Kubernetes Orchestration)

- Pod 部署與管理
- Service 發現
- Ingress 控制
- 持久化儲存
- 自動伸縮

### 監控系統 (Monitoring System)

- Prometheus 指標收集
- Grafana 可視化儀表板
- AlertManager 告警路由
- ELK Stack 日誌聚合

### 部署策略 (Deployment Strategies)

- 標準滾動部署
- 金絲雀部署
- 藍綠部署
- 特性開關

### 漂移檢測 (Drift Detection)

- 自動檢測配置漂移
- 自動修復
- 審計記錄

---

## 🚀 使用指南 / Usage Guide

### 部署至 Kubernetes / Deploy to Kubernetes

```bash
# 1. 驗證配置
kubectl apply -f infrastructure/kubernetes/manifests/ --dry-run=client

# 2. 部署
kubectl apply -f infrastructure/kubernetes/manifests/

# 3. 驗證部署
kubectl rollout status deployment/synergymesh -n synergymesh

# 4. 查看服務
kubectl get svc -n synergymesh
```

### 部署至 Docker Compose / Deploy to Docker Compose

```bash
# 開發環境
docker-compose -f docker-compose.dev.yml up -d

# 生產環境
docker-compose -f infrastructure/deployment/docker-compose.prod.yml up -d
```

### 設置監控 / Setup Monitoring

```bash
# 部署 Prometheus
kubectl apply -f infrastructure/monitoring/prometheus/

# 部署 Grafana
kubectl apply -f infrastructure/monitoring/grafana/

# 訪問 Grafana
kubectl port-forward svc/grafana 3000:3000 -n synergymesh
# 開啟瀏覽器: http://localhost:3000
```

---

## 📊 監控儀表板 / Monitoring Dashboards

### 系統概覽 (System Overview)

- CPU & 記憶體使用率
- 網絡 I/O
- 磁盤使用率

### 服務監控 (Service Monitoring)

- 請求速率
- 錯誤率
- 延遲分布
- 可用性

### 基礎設施監控 (Infrastructure Monitoring)

- Node 狀態
- Pod 健康
- 存儲使用
- 網絡狀態

---

## 🔐 安全 / Security

### Network Policy

定義 Pod 間的網絡訪問規則。

### RBAC (Role-Based Access Control)

- ServiceAccount 創建
- ClusterRole 定義
- RoleBinding 配置

### Secret 管理

```bash
# 創建 Secret
kubectl create secret generic db-credentials \
  --from-literal=username=user \
  --from-literal=password=password \
  -n synergymesh
```

### TLS 配置

```bash
# 為 Ingress 配置 TLS
kubectl apply -f infrastructure/security/ingress-tls.yaml
```

---

## 📈 伸縮配置 / Scaling Configuration

### 水平自動伸縮 (HPA - Horizontal Pod Autoscaler)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: synergymesh-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: synergymesh
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 垂直自動伸縮 (VPA - Vertical Pod Autoscaler)

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: synergymesh-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: synergymesh
  updatePolicy:
    updateMode: "Auto"
```

---

## 🔄 漂移檢測與修復 / Drift Detection & Reconciliation

### 運行漂移檢測

```bash
python3 infrastructure/drift-detection/drift-detector.py \
  --config infrastructure/kubernetes/manifests/ \
  --output drift-report.yaml
```

### 自動修復漂移

```bash
python3 infrastructure/drift-detection/reconciler.py \
  --drift-report drift-report.yaml \
  --auto-fix
```

---

## 🧪 驗證與測試 / Validation & Testing

### 驗證 Kubernetes 清單

```bash
# 語法檢查
kubectl apply -f manifests/ --dry-run=client

# Schema 驗證
kubeval manifests/*.yaml

# OPA 策略檢查
conftest test manifests/*.yaml -p infrastructure/security/policies/
```

### 健康檢查

```bash
bash infrastructure/scripts/health-check.sh
```

---

## 📈 效能優化 / Performance Optimization

### 資源限制 (Resource Limits)

```yaml
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi
```

### 節點親和力 (Node Affinity)

```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: node-type
          operator: In
          values:
          - compute
```

---

## 📖 詳細文檔 / Detailed Documentation

- [Kubernetes 配置](./kubernetes/README.md)
- [監控系統](./monitoring/README.md)
- [部署策略](./deployment/README.md)
- [漂移檢測](./drift-detection/README.md)
- [安全配置](./security/README.md)

---

## 🤝 貢獻指南 / Contributing

在修改基礎設施時：

1. 遵循 Kubernetes 最佳實踐
2. 驗證 YAML 配置
3. 測試部署流程
4. 更新文檔

---

## 📞 支援 / Support

- 📖 [基礎設施文檔](./README.md)
- 🐛 [報告問題](https://github.com/SynergyMesh-admin/Unmanned-Island/issues)
- 💬 [討論](https://github.com/SynergyMesh-admin/Unmanned-Island/discussions)
