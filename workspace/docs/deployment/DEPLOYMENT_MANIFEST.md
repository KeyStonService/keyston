# 🚀 部署完整清單 / Complete Deployment Manifest

## 目的 / Purpose

本檔案列出所有必要的部署配置、依賴項和驗證步驟，確保系統完整部署。

This document lists all necessary deployment configurations, dependencies, and verification steps to ensure complete system deployment.

---

## 📋 預部署檢查清單 / Pre-Deployment Checklist

### 環境準備 / Environment Preparation

- [ ] Node.js >= 18.0.0
- [ ] Python >= 3.10
- [ ] Docker & Docker Compose
- [ ] kubectl (K8s 部署時)
- [ ] Git 已配置
- [ ] `.env` 檔案已建立

### 代碼準備 / Code Preparation

- [ ] 所有分支已合併至 main
- [ ] 版本號已更新 (package.json, __version__.py)
- [ ] CHANGELOG.md 已更新
- [ ] 標籤已創建 (git tag v X.Y.Z)

### 質量檢查 / Quality Assurance

- [ ] npm run lint 通過
- [ ] npm run test 全部通過
- [ ] 代碼覆蓋率 >= 85%
- [ ] npm run build 成功
- [ ] npm run docs:lint 通過
- [ ] python3 tools/docs/validate_index.py --verbose 通過

---

## 📦 依賴項清單 / Dependencies Manifest

### NPM 工作區依賴 / NPM Workspace Dependencies

```
root/
├── mcp-servers/
├── core/contract_service/contracts-L1/contracts/
├── core/advisory-database/
├── frontend/ui/
└── 其他工作區
```

### Python 依賴 / Python Dependencies

```bash
pip install -r requirements.txt
```

關鍵套件 / Key Packages:

- fastapi >= 0.100.0
- sqlalchemy >= 2.0.0
- pydantic >= 2.0.0
- python-dotenv >= 1.0.0
- pyyaml >= 6.0.0

### Docker 基礎映像 / Docker Base Images

- node:20-alpine
- python:3.10-slim
- postgres:15-alpine
- redis:7-alpine
- prometheus:latest
- grafana:latest

---

## 🔧 配置初始化 / Configuration Initialization

### 生成主配置 / Generate Master Configuration

```bash
# 複製範本
cp .env.example .env

# 編輯環境變數
nano .env

# 驗證配置
python3 tools/docs/validate_index.py --verbose
```

### 初始化資料庫 / Initialize Database

```bash
# 創建資料庫
createdb synergymesh

# 運行遷移
npm run db:migrate

# 加入種子數據 (可選)
npm run db:seed
```

### 初始化 Redis / Initialize Redis

```bash
# 本地開發
redis-server

# Docker
docker run -d -p 6379:6379 redis:7-alpine
```

---

## 🐳 Docker 部署流程 / Docker Deployment Process

### 步驟 1: 構建映像 / Build Images

```bash
# 前端 & 後端
docker-compose build

# 或單獨構建
docker build -f Dockerfile -t synergymesh-app:latest .
docker build -f apps/web/Dockerfile -t synergymesh-web:latest apps/web
docker build -f apps/web/Dockerfile.api -t synergymesh-api:latest apps/web
```

### 步驟 2: 啟動容器 / Start Containers

```bash
# 開發環境
docker-compose -f docker-compose.dev.yml up -d

# 生產環境
docker-compose up -d

# 驗證
docker ps
docker-compose ps
```

### 步驟 3: 驗證服務 / Verify Services

```bash
# 檢查容器日誌
docker-compose logs -f

# 檢查健康狀態
curl http://localhost:3000/health
curl http://localhost:8000/health

# 進入容器
docker exec -it synergymesh-app sh
```

### 步驟 4: 清理 / Cleanup

```bash
# 停止容器
docker-compose down

# 刪除映像
docker rmi synergymesh-app:latest synergymesh-web:latest
```

---

## ☸️ Kubernetes 部署流程 / Kubernetes Deployment Process

### 步驟 1: 準備叢集 / Prepare Cluster

```bash
# 建立命名空間
kubectl create namespace synergymesh

# 驗證命名空間
kubectl get namespace synergymesh
```

### 步驟 2: 創建 ConfigMap & Secret / Create ConfigMap & Secret

```bash
# ConfigMap
kubectl create configmap synergymesh-config \
  --from-file=config/ \
  -n synergymesh

# Secret
kubectl create secret generic synergymesh-secrets \
  --from-literal=DATABASE_URL=postgresql://... \
  --from-literal=JWT_SECRET=... \
  -n synergymesh

# 驗證
kubectl get configmap -n synergymesh
kubectl get secret -n synergymesh
```

### 步驟 3: 部署應用 / Deploy Application

```bash
# 應用所有清單
kubectl apply -f infrastructure/kubernetes/manifests/ -n synergymesh

# 或逐個應用
kubectl apply -f infrastructure/kubernetes/manifests/deployment.yaml -n synergymesh
kubectl apply -f infrastructure/kubernetes/manifests/service.yaml -n synergymesh
kubectl apply -f infrastructure/kubernetes/manifests/ingress.yaml -n synergymesh

# 驗證部署
kubectl rollout status deployment/synergymesh -n synergymesh
```

### 步驟 4: 驗證服務 / Verify Services

```bash
# 查看 Pod
kubectl get pods -n synergymesh

# 查看 Service
kubectl get svc -n synergymesh

# 查看日誌
kubectl logs -f deployment/synergymesh -n synergymesh

# 測試服務
kubectl port-forward svc/synergymesh 3000:3000 -n synergymesh
curl http://localhost:3000/health
```

### 步驟 5: 設置監控 / Setup Monitoring

```bash
# 部署 Prometheus
kubectl apply -f infrastructure/monitoring/prometheus/ -n synergymesh

# 部署 Grafana
kubectl apply -f infrastructure/monitoring/grafana/ -n synergymesh

# 訪問 Grafana
kubectl port-forward svc/grafana 3000:3000 -n synergymesh
# http://localhost:3000 (admin/admin)
```

---

## 🧪 部署後驗證 / Post-Deployment Verification

### 基本功能測試 / Basic Functionality Tests

```bash
# 健康檢查
curl -X GET http://localhost:3000/health
# 預期: { "status": "ok" }

# API 版本
curl -X GET http://localhost:3000/api/v1/version
# 預期: { "version": "X.Y.Z" }

# 資料庫連接
curl -X GET http://localhost:3000/api/v1/db/status
# 預期: { "connected": true }
```

### 效能驗證 / Performance Verification

```bash
# 響應時間測試
curl -X POST http://localhost:3000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "..."}' \
  -w "\nResponse time: %{time_total}s\n"

# 負載測試
npm run test:performance
```

### 安全驗證 / Security Verification

```bash
# HTTPS 檢查 (生產環境)
curl -I https://your-domain.com
# 預期: HTTP/2 200

# 安全頭檢查
curl -I http://localhost:3000 | grep -i "security\|x-\|cache"

# SSL 証書檢查
openssl s_client -connect your-domain.com:443 -showcerts < /dev/null
```

---

## 🔄 部署策略 / Deployment Strategies

### 滾動部署 (Rolling Deployment)

```bash
# 自動滾動更新
kubectl set image deployment/synergymesh \
  synergymesh=synergymesh:new-version \
  -n synergymesh

# 監控進度
kubectl rollout status deployment/synergymesh -n synergymesh
```

### 金絲雀部署 (Canary Deployment)

```bash
# 先部署金絲雀版本到 5% 流量
kubectl patch virtualservice synergymesh \
  -p '{"spec":{"hosts":[{"name":"synergymesh","weight":95}]}}' \
  -n synergymesh
```

### 藍綠部署 (Blue-Green Deployment)

```bash
# 部署新版本 (Green)
kubectl apply -f infrastructure/deployment/blue-green-deployment.yaml

# 切換流量
kubectl patch service synergymesh \
  -p '{"spec":{"selector":{"version":"green"}}}' \
  -n synergymesh

# 刪除舊版本 (Blue)
kubectl delete deployment synergymesh-blue -n synergymesh
```

---

## 🆘 故障排除 / Troubleshooting

### Pod 無法啟動 / Pod Won't Start

```bash
# 查看 Pod 事件
kubectl describe pod <pod-name> -n synergymesh

# 查看日誌
kubectl logs <pod-name> -n synergymesh

# 查看 CPU/Memory
kubectl top pods -n synergymesh
```

### 服務無法訪問 / Service Unreachable

```bash
# 檢查 Service
kubectl get svc -n synergymesh
kubectl describe svc synergymesh -n synergymesh

# 檢查 Endpoints
kubectl get endpoints -n synergymesh

# 測試連接
kubectl run -it --image=alpine test sh
# 在容器內執行: wget http://synergymesh:3000/health
```

### 資料庫連接失敗 / Database Connection Failed

```bash
# 檢查 Secret
kubectl get secret synergymesh-secrets -n synergymesh -o yaml

# 測試資料庫連接
kubectl exec -it <pod-name> -- psql -h postgres -U user -d synergymesh

# 查看資料庫日誌
docker logs synergymesh-postgres
```

---

## 📋 部署檢查清單 / Deployment Checklist

### 部署前 / Before Deployment

- [ ] 所有測試通過
- [ ] 代碼審查完成
- [ ] 文檔已更新
- [ ] 備份已建立
- [ ] 回滾計劃已準備

### 部署中 / During Deployment

- [ ] 監控系統已啟動
- [ ] 告警已配置
- [ ] 日誌正確記錄
- [ ] 沒有錯誤報告

### 部署後 / After Deployment

- [ ] 所有功能驗證通過
- [ ] 效能指標達標
- [ ] 無報告錯誤
- [ ] 用戶反饋良好
- [ ] 文件已發佈

---

## 📞 支援與聯繫 / Support & Contact

- 📖 [部署文檔](./docs/operations/)
- 🐛 [報告問題](https://github.com/SynergyMesh-admin/Unmanned-Island/issues)
- 💬 [討論](https://github.com/SynergyMesh-admin/Unmanned-Island/discussions)
- 📧 [聯繫我們](mailto:support@example.com)

---

