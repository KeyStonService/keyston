# 🚀 Kind Cluster 快速參考指南

## 一鍵使用

當你打開 GitHub Codespaces 時，**完整生產環境**自動部署。無需任何手動操作！

**自動部署內容**:

- 3-node Kubernetes cluster (1 control-plane + 2 workers)
- NGINX Ingress Controller
- Prometheus + Grafana 監控堆疊
- ArgoCD GitOps 系統
- cert-manager TLS 管理
- Metrics Server
- 持續健康監控
- 自動化測試驗證

## 常用命令

### 🔍 檢查狀態

```bash
# 查看 cluster 列表
kind get clusters

# 查看節點狀態
kubectl get nodes

# 查看 cluster 資訊
kubectl cluster-info

# 查看所有 pods
kubectl get pods -A

# 查看資源使用
kubectl top nodes
kubectl top pods -A
```

### 🎛️ 多環境管理

```bash
# 建立新環境
./devcontainer/scripts/multi-cluster-manager.sh create dev 1

# 切換環境
./devcontainer/scripts/multi-cluster-manager.sh switch dev

# 查看所有環境
./devcontainer/scripts/multi-cluster-manager.sh status

# 刪除環境
./devcontainer/scripts/multi-cluster-manager.sh delete dev
```

### 🔄 GitOps 操作

```bash
# 訪問 ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
# 瀏覽器開啟: https://localhost:8080

# 取得 ArgoCD 密碼
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d

# ArgoCD CLI 操作
argocd app list
argocd app sync <app-name>

# Flux 操作
flux get all
flux reconcile source git <repo-name>
```

### 📊 監控與可觀測性

```bash
# 訪問 Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# 瀏覽器開啟: http://localhost:3000
# 預設帳號: admin / prom-operator

# 訪問 Prometheus
kubectl port-forward -n monitoring \
  svc/prometheus-kube-prometheus-prometheus 9090:9090

# 查看健康監控日誌
tail -f /tmp/kind-cluster-health.log

# 手動健康檢查
./devcontainer/scripts/health-monitor.sh
```

### 🧪 測試與驗證

```bash
# 執行完整測試套件
./devcontainer/scripts/run-tests.sh

# 查看測試結果
cat /tmp/kind-cluster-test-results.log

# 測試特定功能
kubectl run test-pod --image=nginx --rm -it -- /bin/sh
```

### 🛠️ 管理 Cluster

```bash
# 重新部署 Helm charts
./devcontainer/scripts/setup-helm-charts.sh

# 重新設置 GitOps
./devcontainer/scripts/setup-gitops.sh argocd

# 查看已安裝的 Helm releases
helm list -A

# 刪除 cluster
kind delete cluster --name governance-test

# 重新建立 cluster（完整堆疊）
./devcontainer/scripts/setup-kind-cluster.sh
```

### 📦 部署測試應用

```bash
# 部署 nginx
kubectl create deployment nginx --image=nginx

# 暴露服務
kubectl expose deployment nginx --port=80 --type=ClusterIP

# 建立 Ingress
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
spec:
  rules:
  - host: nginx.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx
            port:
              number: 80
EOF

# 查看服務
kubectl get svc
kubectl get ingress

# 清理
kubectl delete deployment nginx
kubectl delete service nginx
kubectl delete ingress nginx-ingress
```

## 🔧 進階配置

### 自訂 Cluster 配置

編輯 `.devcontainer/kind-cluster-config.yaml`:

- 調整節點數量
- 修改資源分配
- 配置網路設定
- 啟用 feature gates

### GitOps 工作流

1. 編輯 `.devcontainer/gitops/` 目錄下的manifests
2. Git commit 並push
3. ArgoCD 自動同步部署

### 環境變數

- `KIND_CLUSTER_NAME`: Cluster 名稱（預設: governance-test）
- `KIND_CLUSTER_CONFIG`: 配置檔路徑
- `HEALTH_CHECK_INTERVAL`: 健康檢查間隔（秒，預設: 60）
- `GITOPS_REPO`: GitOps repository URL

### 🐛 故障排除

```bash
# 查看容器
podman ps -a

# 查看 logs
podman logs <container_name>

# 重置環境
kind delete cluster --name governance-test
podman system prune -a -f
.devcontainer/scripts/setup-kind-cluster.sh
```

## 環境變數

- `KIND_EXPERIMENTAL_PROVIDER=podman` - 使用 Podman 作為容器引擎
- `KIND_CLUSTER_NAME=governance-test` - Cluster 名稱

## 相關文件

- [完整文檔](KIND_CLUSTER_README.md)
- [驗證清單](VALIDATION_CHECKLIST.md)

## 支援

如有問題，請查看 [Kind 官方文檔](https://kind.sigs.k8s.io/) 或提交 Issue。
