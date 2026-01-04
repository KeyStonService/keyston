# 部署操作 Runbook

## 概述

本目錄包含 ChatOps 平台的部署相關操作手冊。

## 部署流程

### 標準部署

```bash
# 1. 確認要部署的版本
export VERSION=1.2.3
export ENVIRONMENT=production

# 2. 執行 Helm 升級
helm upgrade chatops-platform ./deploy/helm/charts/chatops-platform \
  --namespace chatops \
  --values ./deploy/helm/charts/chatops-platform/values.yaml \
  --values ./deploy/helm/charts/chatops-platform/values-${ENVIRONMENT}.yaml \
  --set global.image.tag=${VERSION} \
  --wait \
  --timeout 10m

# 3. 驗證部署
kubectl rollout status deployment/chatops-gateway -n chatops
kubectl rollout status deployment/chatops-engine -n chatops

# 4. 運行冒煙測試
./scripts/smoke-test.sh ${ENVIRONMENT}
```

### 金絲雀部署

```bash
# 1. 部署金絲雀版本 (10% 流量)
helm upgrade chatops-platform-canary ./deploy/helm/charts/chatops-platform \
  --namespace chatops-canary \
  --set replicaCount=1 \
  --set global.image.tag=${VERSION}

# 2. 監控金絲雀指標
# - 錯誤率對比
# - 延遲對比
# - 資源使用

# 3. 逐步增加流量
# 10% -> 25% -> 50% -> 100%

# 4. 完成或回滾
helm upgrade chatops-platform ./deploy/helm/charts/chatops-platform \
  --namespace chatops \
  --set global.image.tag=${VERSION}
```

## 文件索引

| 文件 | 說明 |
|------|------|
| [rollback.md](rollback.md) | 回滾操作 |
| [blue-green.md](blue-green.md) | 藍綠部署 |
| [hotfix.md](hotfix.md) | 緊急修復部署 |
