# 命名空間設計原則

## Design Principles for Namespaces

本章節介紹設計和規劃命名空間時應遵循的原則和最佳實踐。

## 1. 清晰性原則 (Clarity)

### 1.1 命名規範

命名空間名稱應當清晰、有意義且易於理解：

```yaml
# ✅ 好的命名
namespaces:
  - team-frontend-prod      # 團隊-功能-環境
  - team-backend-staging
  - shared-services-prod

# ❌ 不好的命名
namespaces:
  - ns1
  - test123
  - my-stuff
```

### 1.2 命名模式

推薦的命名模式：

| 模式 | 範例 | 適用場景 |
|-----|------|---------|
| `<team>-<env>` | `platform-prod` | 小型團隊 |
| `<app>-<env>` | `webapp-staging` | 單一應用 |
| `<team>-<app>-<env>` | `backend-api-prod` | 大型組織 |
| `<project>-<component>` | `ecommerce-payment` | 專案導向 |

### 1.3 標籤策略

使用標籤增強可讀性：

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: team-alpha-prod
  labels:
    # 必要標籤
    team: alpha
    environment: production
    cost-center: "CC-001"
    # 可選標籤
    managed-by: terraform
    created-at: "2024-01-15"
  annotations:
    owner: team-alpha@company.com
    description: "Team Alpha production environment"
```

## 2. 一致性原則 (Consistency)

### 2.1 跨環境一致性

保持不同環境間的命名空間結構一致：

```yaml
# 開發環境
environments:
  development:
    namespaces:
      - frontend-dev
      - backend-dev
      - database-dev
  
  staging:
    namespaces:
      - frontend-staging
      - backend-staging
      - database-staging
  
  production:
    namespaces:
      - frontend-prod
      - backend-prod
      - database-prod
```

### 2.2 資源配置一致性

使用模板確保配置一致：

```yaml
# namespace-template.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ${NAMESPACE_NAME}
  labels:
    team: ${TEAM}
    environment: ${ENV}
    managed-by: automation
spec:
  finalizers:
    - kubernetes
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: default-quota
  namespace: ${NAMESPACE_NAME}
spec:
  hard:
    pods: "${POD_LIMIT}"
    requests.cpu: "${CPU_REQUEST}"
    requests.memory: "${MEMORY_REQUEST}"
```

### 2.3 RBAC 一致性

為每個命名空間定義標準角色：

```yaml
# 標準開發者角色
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: standard-developer
  namespace: ${NAMESPACE}
rules:
  - apiGroups: ["", "apps", "batch"]
    resources: ["pods", "deployments", "jobs", "configmaps", "secrets"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
  - apiGroups: [""]
    resources: ["pods/log", "pods/exec"]
    verbs: ["get", "create"]
```

## 3. 隔離性原則 (Isolation)

### 3.1 安全邊界

根據安全需求設計隔離邊界：

```yaml
# 高安全性命名空間
apiVersion: v1
kind: Namespace
metadata:
  name: secure-workloads
  labels:
    security-level: high
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### 3.2 網路隔離

預設拒絕所有流量，明確允許需要的通訊：

```yaml
# 預設拒絕策略
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: secure-workloads
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
---
# 允許同命名空間內通訊
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-same-namespace
  namespace: secure-workloads
spec:
  podSelector: {}
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: secure-workloads
```

### 3.3 資源隔離

確保命名空間間的資源不會相互影響：

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: resource-limits
  namespace: team-alpha-prod
spec:
  hard:
    # 防止單一命名空間耗盡叢集資源
    pods: "100"
    requests.cpu: "50"
    requests.memory: "100Gi"
    limits.cpu: "100"
    limits.memory: "200Gi"
    # 限制儲存使用
    persistentvolumeclaims: "20"
    requests.storage: "500Gi"
```

## 4. 可擴展性原則 (Scalability)

### 4.1 層次結構設計

設計可擴展的命名空間層次：

```
organization/
├── platform/          # 平台團隊
│   ├── platform-tools-prod
│   ├── platform-monitoring-prod
│   └── platform-logging-prod
├── product-a/         # 產品 A
│   ├── product-a-frontend-prod
│   ├── product-a-backend-prod
│   └── product-a-database-prod
└── product-b/         # 產品 B
    ├── product-b-api-prod
    └── product-b-workers-prod
```

### 4.2 自動化創建

使用自動化工具管理命名空間生命週期：

```yaml
# Terraform 範例
resource "kubernetes_namespace" "team_namespace" {
  for_each = toset(var.teams)
  
  metadata {
    name = "${each.key}-${var.environment}"
    
    labels = {
      team        = each.key
      environment = var.environment
      managed-by  = "terraform"
    }
  }
}

resource "kubernetes_resource_quota" "team_quota" {
  for_each = kubernetes_namespace.team_namespace
  
  metadata {
    name      = "default-quota"
    namespace = each.value.metadata[0].name
  }
  
  spec {
    hard = {
      pods               = var.pod_limit
      "requests.cpu"     = var.cpu_request
      "requests.memory"  = var.memory_request
    }
  }
}
```

### 4.3 命名空間生命週期管理

```yaml
# 命名空間生命週期策略
lifecycle:
  creation:
    - create namespace
    - apply resource quota
    - apply limit range
    - apply network policies
    - create default service account
    - bind RBAC roles
  
  maintenance:
    - monitor resource usage
    - audit access logs
    - review and update quotas
  
  deletion:
    - notify stakeholders
    - backup critical data
    - remove RBAC bindings
    - delete namespace
```

## 5. 安全性原則 (Security)

### 5.1 最小權限原則

```yaml
# 只授予必要的權限
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: minimal-reader
  namespace: team-alpha-prod
rules:
  - apiGroups: [""]
    resources: ["pods", "services"]
    verbs: ["get", "list"]  # 只讀權限
```

### 5.2 Pod 安全標準

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: restricted-namespace
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/audit-version: latest
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/warn-version: latest
```

### 5.3 稽核日誌

確保所有命名空間操作都有稽核記錄：

```yaml
# Kubernetes 稽核策略
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  - level: RequestResponse
    namespaces: ["production-*"]
    resources:
      - group: ""
        resources: ["secrets", "configmaps"]
    verbs: ["create", "update", "delete"]
  
  - level: Metadata
    namespaces: ["*"]
    resources:
      - group: ""
        resources: ["pods", "services"]
```

## 6. 設計檢查清單

在創建新命名空間前，確認以下事項：

- [ ] 命名符合組織命名規範
- [ ] 標籤和註解完整
- [ ] 資源配額已配置
- [ ] 限制範圍已設定
- [ ] 網路策略已應用
- [ ] RBAC 角色已綁定
- [ ] Pod 安全標準已啟用
- [ ] 監控和告警已配置
- [ ] 文檔已更新

---

**上一章節**: [命名空間在不同技術棧中的體現](./technology_stacks.md)
**下一章節**: [實際應用場景與案例研究](./use_cases.md)
