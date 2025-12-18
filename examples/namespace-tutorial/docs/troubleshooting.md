# 故障排除與診斷

## Troubleshooting and Diagnostics

本章節提供命名空間相關問題的診斷和解決方案。

## 1. 常見問題

### 1.1 命名空間卡在 "Terminating" 狀態

#### 症狀

```bash
$ kubectl get namespace
NAME              STATUS        AGE
stuck-namespace   Terminating   5h
```

#### 診斷步驟

```bash
# 1. 檢查命名空間狀態
kubectl get namespace stuck-namespace -o yaml

# 2. 查看是否有殘留的 finalizers
kubectl get namespace stuck-namespace -o jsonpath='{.spec.finalizers}'

# 3. 查看命名空間中的資源
kubectl api-resources --verbs=list --namespaced -o name | \
  xargs -n 1 kubectl get -n stuck-namespace --ignore-not-found
```

#### 解決方案

```bash
# 方案 1: 刪除殘留資源
kubectl delete all --all -n stuck-namespace

# 方案 2: 強制移除 finalizers（謹慎使用）
kubectl get namespace stuck-namespace -o json | \
  jq '.spec.finalizers = []' | \
  kubectl replace --raw "/api/v1/namespaces/stuck-namespace/finalize" -f -

# 方案 3: 使用 kubectl patch
kubectl patch namespace stuck-namespace -p '{"spec":{"finalizers":[]}}' --type=merge
```

### 1.2 資源配額超限

#### 症狀

```bash
$ kubectl create -f pod.yaml -n my-namespace
Error: pods "my-pod" is forbidden: exceeded quota: compute-resources
```

#### 診斷步驟

```bash
# 查看配額狀態
kubectl describe resourcequota -n my-namespace

# 輸出範例：
# Name:            compute-resources
# Namespace:       my-namespace
# Resource         Used    Hard
# --------         ----    ----
# pods             10      10     # 已達上限
# requests.cpu     4       4      # 已達上限
# requests.memory  8Gi     8Gi    # 已達上限
```

#### 解決方案

```bash
# 方案 1: 刪除不需要的 Pod
kubectl delete pod unused-pod -n my-namespace

# 方案 2: 調整配額（需要管理員權限）
kubectl patch resourcequota compute-resources -n my-namespace \
  -p '{"spec":{"hard":{"pods":"20"}}}'

# 方案 3: 減少新 Pod 的資源請求
```

### 1.3 網路策略阻擋流量

#### 症狀

```bash
# Pod 無法連接到其他服務
$ kubectl exec -it my-pod -n my-namespace -- curl http://service.other-namespace:80
curl: (7) Failed to connect to service.other-namespace port 80: Connection timed out
```

#### 診斷步驟

```bash
# 1. 檢查網路策略
kubectl get networkpolicy -n my-namespace
kubectl get networkpolicy -n other-namespace

# 2. 查看策略詳情
kubectl describe networkpolicy -n my-namespace

# 3. 驗證標籤是否匹配
kubectl get pod my-pod -n my-namespace --show-labels
kubectl get namespace other-namespace --show-labels
```

#### 解決方案

```yaml
# 添加允許跨命名空間通訊的策略
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-my-namespace
  namespace: other-namespace
spec:
  podSelector:
    matchLabels:
      app: target-service
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: my-namespace
```

### 1.4 RBAC 權限不足

#### 症狀

```bash
$ kubectl get pods -n restricted-namespace
Error from server (Forbidden): pods is forbidden: User "user@example.com" 
cannot list resource "pods" in API group "" in the namespace "restricted-namespace"
```

#### 診斷步驟

```bash
# 1. 檢查用戶權限
kubectl auth can-i list pods -n restricted-namespace --as user@example.com

# 2. 查看角色綁定
kubectl get rolebindings -n restricted-namespace
kubectl get clusterrolebindings | grep user@example.com

# 3. 檢查角色定義
kubectl describe role -n restricted-namespace
```

#### 解決方案

```yaml
# 授予適當的權限
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: user-read-access
  namespace: restricted-namespace
subjects:
  - kind: User
    name: user@example.com
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: view
  apiGroup: rbac.authorization.k8s.io
```

## 2. 診斷工具

### 2.1 命名空間健康檢查腳本

```bash
#!/bin/bash
# namespace_health_check.sh

NAMESPACE=$1

if [ -z "$NAMESPACE" ]; then
  echo "Usage: $0 <namespace>"
  exit 1
fi

echo "=== 命名空間健康檢查: $NAMESPACE ==="

# 檢查命名空間是否存在
if ! kubectl get namespace "$NAMESPACE" &>/dev/null; then
  echo "錯誤: 命名空間 $NAMESPACE 不存在"
  exit 1
fi

echo ""
echo "--- 基本資訊 ---"
kubectl get namespace "$NAMESPACE" -o wide

echo ""
echo "--- 資源配額狀態 ---"
kubectl describe resourcequota -n "$NAMESPACE" 2>/dev/null || echo "無資源配額"

echo ""
echo "--- Pod 狀態 ---"
kubectl get pods -n "$NAMESPACE" -o wide

echo ""
echo "--- 服務狀態 ---"
kubectl get services -n "$NAMESPACE"

echo ""
echo "--- 網路策略 ---"
kubectl get networkpolicy -n "$NAMESPACE" 2>/dev/null || echo "無網路策略"

echo ""
echo "--- 事件（最近 10 條）---"
kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' | tail -10

echo ""
echo "--- 問題 Pod ---"
kubectl get pods -n "$NAMESPACE" --field-selector=status.phase!=Running,status.phase!=Succeeded
```

### 2.2 資源使用監控

```bash
#!/bin/bash
# monitor_namespace_resources.sh

NAMESPACE=$1
INTERVAL=${2:-30}

echo "監控命名空間 $NAMESPACE 的資源使用（每 ${INTERVAL} 秒更新）"
echo "按 Ctrl+C 停止"

while true; do
  clear
  date
  echo ""
  echo "=== CPU 和記憶體使用 ==="
  kubectl top pods -n "$NAMESPACE" 2>/dev/null || echo "Metrics Server 未啟用"
  
  echo ""
  echo "=== 資源配額使用率 ==="
  kubectl get resourcequota -n "$NAMESPACE" -o custom-columns=\
NAME:.metadata.name,\
PODS:.status.used.pods/.status.hard.pods,\
CPU:.status.used.requests\\.cpu/.status.hard.requests\\.cpu,\
MEMORY:.status.used.requests\\.memory/.status.hard.requests\\.memory
  
  sleep "$INTERVAL"
done
```

### 2.3 跨命名空間連通性測試

```bash
#!/bin/bash
# test_namespace_connectivity.sh

SOURCE_NS=$1
TARGET_NS=$2
TARGET_SVC=$3

if [ -z "$SOURCE_NS" ] || [ -z "$TARGET_NS" ] || [ -z "$TARGET_SVC" ]; then
  echo "Usage: $0 <source-namespace> <target-namespace> <target-service>"
  exit 1
fi

# 創建測試 Pod
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: connectivity-test
  namespace: $SOURCE_NS
spec:
  containers:
  - name: test
    image: busybox
    command: ['sleep', '300']
  restartPolicy: Never
EOF

# 等待 Pod 就緒
kubectl wait --for=condition=Ready pod/connectivity-test -n "$SOURCE_NS" --timeout=60s

# 測試連通性
echo "測試從 $SOURCE_NS 到 $TARGET_NS/$TARGET_SVC 的連通性..."
kubectl exec -n "$SOURCE_NS" connectivity-test -- \
  wget -qO- --timeout=5 "http://${TARGET_SVC}.${TARGET_NS}.svc.cluster.local" && \
  echo "連通性測試成功" || \
  echo "連通性測試失敗"

# 清理
kubectl delete pod connectivity-test -n "$SOURCE_NS"
```

## 3. 日誌收集

### 3.1 收集命名空間診斷資訊

```bash
#!/bin/bash
# collect_namespace_diagnostics.sh

NAMESPACE=$1
OUTPUT_DIR="namespace-diagnostics-$(date +%Y%m%d-%H%M%S)"

mkdir -p "$OUTPUT_DIR"

echo "收集命名空間 $NAMESPACE 的診斷資訊..."

# 命名空間配置
kubectl get namespace "$NAMESPACE" -o yaml > "$OUTPUT_DIR/namespace.yaml"

# 所有資源
kubectl get all -n "$NAMESPACE" -o yaml > "$OUTPUT_DIR/all-resources.yaml"

# 配額和限制
kubectl get resourcequota -n "$NAMESPACE" -o yaml > "$OUTPUT_DIR/quotas.yaml" 2>/dev/null
kubectl get limitrange -n "$NAMESPACE" -o yaml > "$OUTPUT_DIR/limits.yaml" 2>/dev/null

# 網路策略
kubectl get networkpolicy -n "$NAMESPACE" -o yaml > "$OUTPUT_DIR/network-policies.yaml" 2>/dev/null

# RBAC
kubectl get role,rolebinding -n "$NAMESPACE" -o yaml > "$OUTPUT_DIR/rbac.yaml"

# 事件
kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' > "$OUTPUT_DIR/events.txt"

# Pod 日誌
for pod in $(kubectl get pods -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}'); do
  kubectl logs "$pod" -n "$NAMESPACE" --all-containers > "$OUTPUT_DIR/logs-${pod}.txt" 2>&1
done

# 打包
tar -czvf "${OUTPUT_DIR}.tar.gz" "$OUTPUT_DIR"
rm -rf "$OUTPUT_DIR"

echo "診斷資訊已保存到 ${OUTPUT_DIR}.tar.gz"
```

## 4. 常見錯誤代碼

| 錯誤代碼 | 說明 | 解決方向 |
|---------|------|---------|
| `Forbidden` | RBAC 權限不足 | 檢查角色綁定 |
| `ResourceQuotaExceeded` | 超出資源配額 | 調整配額或減少使用 |
| `NetworkPolicyDenied` | 網路策略阻擋 | 添加允許規則 |
| `NamespaceTerminating` | 命名空間刪除中 | 清理 finalizers |
| `InvalidNamespace` | 命名空間不存在 | 創建命名空間 |

## 5. 預防措施

### 5.1 監控告警設定

```yaml
# Prometheus 告警規則
groups:
  - name: namespace-alerts
    rules:
      - alert: NamespaceQuotaExceeded90Percent
        expr: |
          sum by (namespace, resource) (
            kube_resourcequota{type="used"}
          ) / sum by (namespace, resource) (
            kube_resourcequota{type="hard"}
          ) > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "命名空間 {{ $labels.namespace }} 資源配額即將耗盡"
          
      - alert: NamespaceTerminatingTooLong
        expr: |
          kube_namespace_status_phase{phase="Terminating"} == 1
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "命名空間 {{ $labels.namespace }} 長時間處於 Terminating 狀態"
```

### 5.2 定期健康檢查

```bash
# 添加到 crontab
# 每小時檢查所有命名空間健康狀態
0 * * * * /path/to/namespace_health_check_all.sh >> /var/log/namespace-health.log 2>&1
```

---

**上一章節**: [實際應用場景與案例研究](./use_cases.md)
**返回目錄**: [README](../README.md)
