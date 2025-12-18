# 實際應用場景與案例研究

## Real-World Use Cases and Case Studies

本章節展示命名空間在實際生產環境中的應用場景和案例研究。

## 1. 多租戶隔離

### 1.1 場景描述

一家 SaaS 公司需要在同一個 Kubernetes 叢集中為多個客戶提供隔離的服務環境。

### 1.2 解決方案

```yaml
# 為每個租戶創建獨立命名空間
apiVersion: v1
kind: Namespace
metadata:
  name: tenant-acme-corp
  labels:
    tenant: acme-corp
    tier: enterprise
    billing-id: "ACME-001"
---
apiVersion: v1
kind: Namespace
metadata:
  name: tenant-startup-xyz
  labels:
    tenant: startup-xyz
    tier: standard
    billing-id: "XYZ-002"
```

### 1.3 資源配額（按服務等級）

```yaml
# 企業級租戶配額
apiVersion: v1
kind: ResourceQuota
metadata:
  name: enterprise-quota
  namespace: tenant-acme-corp
spec:
  hard:
    pods: "200"
    requests.cpu: "100"
    requests.memory: "200Gi"
    limits.cpu: "200"
    limits.memory: "400Gi"
    persistentvolumeclaims: "50"
---
# 標準級租戶配額
apiVersion: v1
kind: ResourceQuota
metadata:
  name: standard-quota
  namespace: tenant-startup-xyz
spec:
  hard:
    pods: "50"
    requests.cpu: "20"
    requests.memory: "40Gi"
    limits.cpu: "40"
    limits.memory: "80Gi"
    persistentvolumeclaims: "10"
```

### 1.4 網路隔離

```yaml
# 完全隔離租戶間的網路
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: tenant-isolation
  namespace: tenant-acme-corp
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              tenant: acme-corp
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              tenant: acme-corp
    - to:
        - namespaceSelector:
            matchLabels:
              purpose: shared-services
```

## 2. 環境分離（Dev/Staging/Production）

### 2.1 場景描述

開發團隊需要在同一叢集中維護開發、測試和生產三個環境。

### 2.2 命名空間結構

```yaml
# 開發環境
apiVersion: v1
kind: Namespace
metadata:
  name: myapp-development
  labels:
    app: myapp
    environment: development
    team: engineering
---
# 測試環境
apiVersion: v1
kind: Namespace
metadata:
  name: myapp-staging
  labels:
    app: myapp
    environment: staging
    team: engineering
---
# 生產環境
apiVersion: v1
kind: Namespace
metadata:
  name: myapp-production
  labels:
    app: myapp
    environment: production
    team: engineering
    pod-security.kubernetes.io/enforce: restricted
```

### 2.3 環境特定配置

```yaml
# 開發環境 - 寬鬆配置
apiVersion: v1
kind: LimitRange
metadata:
  name: dev-limits
  namespace: myapp-development
spec:
  limits:
    - type: Container
      default:
        cpu: "200m"
        memory: "256Mi"
      defaultRequest:
        cpu: "100m"
        memory: "128Mi"
---
# 生產環境 - 嚴格配置
apiVersion: v1
kind: LimitRange
metadata:
  name: prod-limits
  namespace: myapp-production
spec:
  limits:
    - type: Container
      default:
        cpu: "1"
        memory: "1Gi"
      defaultRequest:
        cpu: "500m"
        memory: "512Mi"
      max:
        cpu: "4"
        memory: "8Gi"
      min:
        cpu: "200m"
        memory: "256Mi"
```

## 3. 微服務架構

### 3.1 場景描述

電商平台採用微服務架構，需要合理組織數十個微服務。

### 3.2 按領域劃分命名空間

```yaml
# 用戶服務領域
apiVersion: v1
kind: Namespace
metadata:
  name: domain-user
  labels:
    domain: user
    team: user-platform
---
# 訂單服務領域
apiVersion: v1
kind: Namespace
metadata:
  name: domain-order
  labels:
    domain: order
    team: order-processing
---
# 支付服務領域
apiVersion: v1
kind: Namespace
metadata:
  name: domain-payment
  labels:
    domain: payment
    team: payment-gateway
    security-level: high
---
# 庫存服務領域
apiVersion: v1
kind: Namespace
metadata:
  name: domain-inventory
  labels:
    domain: inventory
    team: warehouse-ops
```

### 3.3 跨命名空間服務發現

```yaml
# 支付服務（在 domain-payment 命名空間）
apiVersion: v1
kind: Service
metadata:
  name: payment-service
  namespace: domain-payment
spec:
  selector:
    app: payment-api
  ports:
    - port: 80
      targetPort: 8080
---
# 訂單服務調用支付服務
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-processor
  namespace: domain-order
spec:
  template:
    spec:
      containers:
        - name: order-processor
          env:
            # 跨命名空間服務 DNS
            - name: PAYMENT_SERVICE_URL
              value: "http://payment-service.domain-payment.svc.cluster.local"
```

### 3.4 網路策略允許跨領域通訊

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-order-to-payment
  namespace: domain-payment
spec:
  podSelector:
    matchLabels:
      app: payment-api
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              domain: order
        - podSelector:
            matchLabels:
              app: order-processor
      ports:
        - protocol: TCP
          port: 8080
```

## 4. CI/CD 管道隔離

### 4.1 場景描述

DevOps 團隊需要為每個 CI/CD 管道提供隔離的執行環境。

### 4.2 動態命名空間

```yaml
# CI 管道專用命名空間模板
apiVersion: v1
kind: Namespace
metadata:
  name: ci-pipeline-${PIPELINE_ID}
  labels:
    purpose: ci-cd
    pipeline-id: ${PIPELINE_ID}
    branch: ${BRANCH_NAME}
    ttl: "24h"
  annotations:
    ci-cd/created-at: ${TIMESTAMP}
    ci-cd/created-by: ${USER}
```

### 4.3 自動清理

```bash
#!/bin/bash
# cleanup_ci_namespaces.sh - 清理過期的 CI 命名空間

MAX_AGE_HOURS=24

# 獲取所有 CI 命名空間
kubectl get namespaces -l purpose=ci-cd -o json | \
jq -r '.items[] | select(.metadata.annotations["ci-cd/created-at"] != null) | 
  select((now - (.metadata.annotations["ci-cd/created-at"] | tonumber)) > ('$MAX_AGE_HOURS' * 3600)) | 
  .metadata.name' | \
while read ns; do
  echo "Deleting expired namespace: $ns"
  kubectl delete namespace "$ns" --grace-period=60
done
```

### 4.4 資源限制

```yaml
# CI 命名空間資源配額
apiVersion: v1
kind: ResourceQuota
metadata:
  name: ci-quota
  namespace: ci-pipeline-${PIPELINE_ID}
spec:
  hard:
    pods: "20"
    requests.cpu: "4"
    requests.memory: "8Gi"
    limits.cpu: "8"
    limits.memory: "16Gi"
    # 限制執行時間（通過 Job 設定）
```

## 5. 共享服務架構

### 5.1 場景描述

組織需要提供共享服務（如監控、日誌、訊息佇列）給所有團隊使用。

### 5.2 共享服務命名空間

```yaml
# 監控服務
apiVersion: v1
kind: Namespace
metadata:
  name: shared-monitoring
  labels:
    purpose: shared-services
    service: monitoring
---
# 日誌服務
apiVersion: v1
kind: Namespace
metadata:
  name: shared-logging
  labels:
    purpose: shared-services
    service: logging
---
# 訊息佇列
apiVersion: v1
kind: Namespace
metadata:
  name: shared-messaging
  labels:
    purpose: shared-services
    service: messaging
```

### 5.3 允許所有命名空間存取共享服務

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-all-to-monitoring
  namespace: shared-monitoring
spec:
  podSelector:
    matchLabels:
      app: prometheus
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector: {}  # 允許所有命名空間
      ports:
        - protocol: TCP
          port: 9090
```

## 6. 案例研究：金融服務公司

### 6.1 背景

一家金融服務公司需要在 Kubernetes 上運行符合監管要求的應用程式。

### 6.2 命名空間設計

```yaml
# 高安全性區域
namespaces:
  - name: secure-trading
    security-level: critical
    compliance: [PCI-DSS, SOX]
    isolation: strict
    
  - name: secure-banking
    security-level: critical
    compliance: [PCI-DSS]
    isolation: strict

# 一般業務區域
  - name: internal-tools
    security-level: standard
    compliance: [internal-policy]
    isolation: moderate

# 開發區域
  - name: dev-sandbox
    security-level: low
    compliance: []
    isolation: minimal
```

### 6.3 合規性配置

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: secure-trading
  labels:
    security-level: critical
    compliance-pci-dss: "true"
    compliance-sox: "true"
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
  annotations:
    compliance/last-audit: "2024-01-15"
    compliance/next-audit: "2024-04-15"
    compliance/auditor: "external-audit-firm"
```

### 6.4 稽核和監控

```yaml
# 稽核日誌策略
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  # 記錄高安全命名空間的所有操作
  - level: RequestResponse
    namespaces: ["secure-trading", "secure-banking"]
    resources:
      - group: ""
        resources: ["*"]
    verbs: ["*"]
```

## 7. 最佳實踐總結

| 場景 | 命名空間策略 | 關鍵考量 |
|-----|-------------|---------|
| 多租戶 | 每租戶獨立命名空間 | 資源配額、網路隔離、計費 |
| 環境分離 | 每環境獨立命名空間 | 配置差異、存取控制 |
| 微服務 | 按領域劃分命名空間 | 服務發現、跨域通訊 |
| CI/CD | 動態命名空間 | 自動清理、資源限制 |
| 共享服務 | 專用共享命名空間 | 存取策略、高可用 |
| 合規要求 | 按安全級別劃分 | 稽核日誌、隔離策略 |

---

**上一章節**: [命名空間設計原則](./design_principles.md)
**下一章節**: [故障排除與診斷](./troubleshooting.md)
