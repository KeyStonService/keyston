# Kubernetes 操作 Runbook

## 常用操作

### Pod 管理

```bash
# 列出所有 Pod
kubectl get pods -n chatops -o wide

# 查看 Pod 詳情
kubectl describe pod <pod-name> -n chatops

# 查看 Pod 日誌
kubectl logs <pod-name> -n chatops
kubectl logs <pod-name> -n chatops --previous  # 上一個容器的日誌
kubectl logs <pod-name> -n chatops -f  # 實時日誌

# 進入 Pod
kubectl exec -it <pod-name> -n chatops -- /bin/sh

# 刪除 Pod (會自動重建)
kubectl delete pod <pod-name> -n chatops
```

### Deployment 管理

```bash
# 查看 Deployment
kubectl get deployments -n chatops

# 擴縮容
kubectl scale deployment <deployment-name> --replicas=5 -n chatops

# 重啟 Deployment
kubectl rollout restart deployment <deployment-name> -n chatops

# 暫停/恢復 Deployment
kubectl rollout pause deployment <deployment-name> -n chatops
kubectl rollout resume deployment <deployment-name> -n chatops

# 查看 Deployment 歷史
kubectl rollout history deployment <deployment-name> -n chatops
```

### 資源監控

```bash
# 查看 Pod 資源使用
kubectl top pods -n chatops

# 查看 Node 資源使用
kubectl top nodes

# 查看 HPA 狀態
kubectl get hpa -n chatops

# 查看 PDB 狀態
kubectl get pdb -n chatops
```

### 網絡診斷

```bash
# 查看 Services
kubectl get svc -n chatops

# 查看 Endpoints
kubectl get endpoints -n chatops

# 查看 Ingress
kubectl get ingress -n chatops

# DNS 測試
kubectl run debug --rm -it --image=busybox -n chatops -- nslookup chatops-gateway

# 網絡連通性測試
kubectl run debug --rm -it --image=curlimages/curl -n chatops -- curl http://chatops-gateway/health
```

### ConfigMap 和 Secret

```bash
# 查看 ConfigMaps
kubectl get configmaps -n chatops

# 查看 ConfigMap 內容
kubectl get configmap <name> -n chatops -o yaml

# 查看 Secrets (base64 編碼)
kubectl get secrets -n chatops
kubectl get secret <name> -n chatops -o jsonpath='{.data}' | base64 -d

# 更新 ConfigMap
kubectl create configmap <name> --from-file=<file> -n chatops --dry-run=client -o yaml | kubectl apply -f -
```

## 故障排查

### Pod 無法啟動

```bash
# 1. 查看 Pod 事件
kubectl describe pod <pod-name> -n chatops | tail -30

# 2. 常見原因:
# - ImagePullBackOff: 檢查鏡像名稱和拉取憑證
kubectl get events -n chatops --field-selector reason=Failed

# - CrashLoopBackOff: 檢查容器日誌
kubectl logs <pod-name> -n chatops --previous

# - Pending: 檢查資源不足或調度問題
kubectl describe pod <pod-name> -n chatops | grep -A5 Events
```

### Pod OOMKilled

```bash
# 1. 確認 OOM 事件
kubectl describe pod <pod-name> -n chatops | grep -i oom

# 2. 查看當前內存使用
kubectl top pod <pod-name> -n chatops

# 3. 解決方案
# - 增加內存限制
# - 優化應用內存使用
# - 檢查內存洩漏
```

### 高 CPU 使用

```bash
# 1. 識別高 CPU Pod
kubectl top pods -n chatops --sort-by=cpu

# 2. 進入容器分析
kubectl exec -it <pod-name> -n chatops -- top

# 3. 可能的解決方案
# - 擴容
# - 代碼優化
# - 限流
```

### 服務不可達

```bash
# 1. 檢查 Pod 是否運行
kubectl get pods -n chatops -l app=chatops-gateway

# 2. 檢查 Service Endpoints
kubectl get endpoints chatops-gateway -n chatops

# 3. 檢查 Pod 標籤匹配
kubectl get pods -n chatops --show-labels
kubectl describe svc chatops-gateway -n chatops

# 4. 測試 Service 連通性
kubectl run debug --rm -it --image=curlimages/curl -n chatops -- \
  curl -v http://chatops-gateway.chatops.svc.cluster.local/health
```

## 維護操作

### Node 維護

```bash
# 1. 驅逐 Node 上的 Pod
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# 2. 執行維護

# 3. 恢復 Node
kubectl uncordon <node-name>
```

### 清理資源

```bash
# 清理完成的 Job
kubectl delete jobs --field-selector status.successful=1 -n chatops

# 清理 Evicted Pods
kubectl delete pods --field-selector status.phase=Failed -n chatops

# 清理未使用的 ConfigMaps (謹慎!)
kubectl delete configmap <old-configmap> -n chatops
```

### 備份操作

```bash
# 導出所有資源定義
kubectl get all -n chatops -o yaml > chatops-backup.yaml

# 導出特定資源
kubectl get deployment,service,configmap,secret -n chatops -o yaml > chatops-resources.yaml

# 導出 ETCD 備份 (如需要)
# 通常由集群管理員執行
```

## 有用的 kubectl 別名

```bash
alias k='kubectl'
alias kn='kubectl -n chatops'
alias kgp='kubectl get pods -n chatops'
alias klogs='kubectl logs -n chatops'
alias kexec='kubectl exec -it -n chatops'
alias kdesc='kubectl describe -n chatops'
```
