# 命名空間的核心特性

## Core Features of Namespaces

本章節詳細介紹命名空間的核心特性，包括隔離性、作用域和資源管理。

## 1. 隔離性 (Isolation)

### 1.1 資源隔離

命名空間提供完整的資源隔離機制：

```yaml
# Kubernetes 命名空間隔離範例
apiVersion: v1
kind: Namespace
metadata:
  name: team-alpha
  labels:
    team: alpha
    environment: production
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-alpha-quota
  namespace: team-alpha
spec:
  hard:
    pods: "20"
    requests.cpu: "4"
    requests.memory: "8Gi"
    limits.cpu: "8"
    limits.memory: "16Gi"
```

### 1.2 網路隔離

通過網路策略實現命名空間間的網路隔離：

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
  namespace: team-alpha
spec:
  podSelector: {}
  policyTypes:
    - Ingress
  ingress: []
```

### 1.3 進程隔離

Linux 命名空間提供進程級別的隔離：

```bash
# 創建新的 PID 命名空間
unshare --pid --fork bash

# 在新命名空間中，進程 ID 從 1 開始
ps aux
```

## 2. 作用域 (Scope)

### 2.1 命名空間範圍的資源

以下資源屬於特定命名空間：

| 資源類型 | 範例 |
|---------|------|
| Pods | 應用程式容器 |
| Services | 服務端點 |
| Deployments | 部署配置 |
| ConfigMaps | 配置映射 |
| Secrets | 密鑰管理 |

### 2.2 叢集範圍的資源

以下資源不屬於任何命名空間：

| 資源類型 | 說明 |
|---------|------|
| Nodes | 叢集節點 |
| PersistentVolumes | 持久化儲存卷 |
| ClusterRoles | 叢集角色 |
| Namespaces | 命名空間本身 |

### 2.3 作用域規則

```yaml
# 命名空間內的資源引用
apiVersion: v1
kind: Pod
metadata:
  name: my-app
  namespace: team-alpha
spec:
  containers:
    - name: app
      image: my-app:latest
      envFrom:
        - configMapRef:
            name: app-config  # 同一命名空間內的 ConfigMap
```

## 3. 資源管理 (Resource Management)

### 3.1 資源配額 (ResourceQuota)

限制命名空間可使用的資源總量：

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-resources
  namespace: team-alpha
spec:
  hard:
    # 計算資源
    requests.cpu: "10"
    requests.memory: "20Gi"
    limits.cpu: "20"
    limits.memory: "40Gi"
    # 物件數量
    pods: "50"
    services: "10"
    secrets: "20"
    configmaps: "20"
```

### 3.2 限制範圍 (LimitRange)

設定預設和最大資源限制：

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: team-alpha
spec:
  limits:
    - type: Container
      default:
        cpu: "500m"
        memory: "512Mi"
      defaultRequest:
        cpu: "200m"
        memory: "256Mi"
      max:
        cpu: "2"
        memory: "4Gi"
      min:
        cpu: "100m"
        memory: "128Mi"
```

### 3.3 資源監控

監控命名空間資源使用情況：

```bash
# 查看命名空間資源使用
kubectl top pods -n team-alpha

# 查看資源配額狀態
kubectl describe resourcequota -n team-alpha

# 查看限制範圍
kubectl describe limitrange -n team-alpha
```

## 4. 存取控制 (Access Control)

### 4.1 RBAC 整合

通過角色綁定限制命名空間存取：

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: developer-role
  namespace: team-alpha
rules:
  - apiGroups: [""]
    resources: ["pods", "services", "configmaps"]
    verbs: ["get", "list", "create", "update", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: developer-binding
  namespace: team-alpha
subjects:
  - kind: User
    name: developer@example.com
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: developer-role
  apiGroup: rbac.authorization.k8s.io
```

### 4.2 服務帳戶

每個命名空間可以有獨立的服務帳戶：

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-service-account
  namespace: team-alpha
```

## 5. 命名空間生命週期

### 5.1 創建命名空間

```bash
# 使用 kubectl
kubectl create namespace team-alpha

# 使用 YAML
kubectl apply -f - <<EOF
apiVersion: v1
kind: Namespace
metadata:
  name: team-alpha
  labels:
    team: alpha
EOF
```

### 5.2 刪除命名空間

```bash
# 刪除命名空間及其所有資源
kubectl delete namespace team-alpha

# 強制刪除（處理終止中的命名空間）
kubectl delete namespace team-alpha --force --grace-period=0
```

## 相關資源

- [Kubernetes Resource Quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/)
- [Kubernetes Limit Ranges](https://kubernetes.io/docs/concepts/policy/limit-range/)
- [Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

---

**上一章節**: [命名空間基礎概念介紹](./introduction.md)
**下一章節**: [命名空間在不同技術棧中的體現](./technology_stacks.md)
