# 🚀 快速開始 - 生產部署 / Production Quick Start

**語言**: [繁體中文](#快速開始---生產部署) |
[English](#quick-start---production-deployment)

---

## 快速開始 - 生產部署

### 📋 5 分鐘快速設置

#### 1️⃣ 環境準備

```bash
# 克隆倉庫
git clone https://github.com/SynergyMesh-admin/Unmanned-Island.git
cd unmanned-island

# 複製環境配置
cp .env.example .env

# 編輯 .env 檔案並設定生產值
nano .env  # 或使用 vim/code
```

#### 2️⃣ 依賴安裝

```bash
# 安裝 Node.js 依賴
npm install

# 安裝 Python 依賴
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

#### 3️⃣ 構建應用

```bash
# 編譯所有模組
npm run build

# 運行測試
npm run test

# 運行 Lint 檢查
npm run lint
```

#### 4️⃣ 啟動服務

```bash
# 開發環境
npm run dev:stack

# 或使用 Docker
docker-compose up -d

# 驗證服務
curl http://localhost:3000/health
```

---

## 詳細設置指南

### 📦 核心模組初始化

#### 合約服務 (Contract Service)

```bash
cd core/contract_service/contracts-L1/contracts
npm install
npm run build
npm start
```

#### MCP 伺服器

```bash
cd mcp-servers
npm install
npm start
```

#### Python 工具驗證

```bash
python3 tools/docs/validate_index.py --verbose
```

---

### 🐳 Docker 部署

#### 開發環境快速啟動

```bash
docker-compose -f docker-compose.dev.yml up -d
docker-compose logs -f
```

#### 生產環境部署

```bash
# 構建映像
docker build -t synergymesh:latest .

# 啟動容器
docker-compose up -d

# 查看日誌
docker-compose logs -f synergymesh
```

---

### 🔄 Kubernetes 部署

#### 基本步驟

```bash
# 建立命名空間
kubectl create namespace synergymesh

# 建立 ConfigMap 和 Secret
kubectl apply -f infrastructure/kubernetes/manifests/configmap.yaml
kubectl apply -f infrastructure/kubernetes/manifests/secret.yaml

# 部署應用
kubectl apply -f infrastructure/kubernetes/manifests/deployment.yaml
kubectl apply -f infrastructure/kubernetes/manifests/service.yaml

# 驗證部署
kubectl rollout status deployment/synergymesh -n synergymesh
kubectl get pods -n synergymesh
```

---

### 📊 監控與日誌

#### 查看應用日誌

```bash
# Docker
docker-compose logs -f synergymesh

# Kubernetes
kubectl logs -f deployment/synergymesh -n synergymesh

# 系統日誌
tail -f logs/synergymesh.log
```

#### 訪問監控儀表板

```
Prometheus: http://localhost:9090
Grafana:    http://localhost:3000 (admin/admin)
```

---

### 🔒 安全配置

#### SSL/TLS 設置

```bash
# 生成自簽証書 (測試用)
openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365 -nodes

# 或使用 Let's Encrypt
certbot certonly --standalone -d your-domain.com
```

#### API 金鑰管理

```bash
# 生成新的 JWT 密鑰
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

# 更新 .env 檔案
JWT_SECRET=<generated-key>
```

---

### ✅ 驗證清單

- [ ] 應用健康檢查通過: `curl http://localhost:3000/health`
- [ ] 資料庫連線正常: `npm run test:db`
- [ ] 所有 API 端點可訪問
- [ ] 監控系統運作正常
- [ ] 日誌正確記錄
- [ ] 安全掃描無高風險項目

---

### 🆘 故障排除

#### 埠被佔用

```bash
# 查找佔用埠的進程
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# 終止進程
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

#### 資料庫連線失敗

```bash
# 檢查資料庫服務
docker ps | grep postgres
psql -h localhost -U postgres -d synergymesh

# 或重置資料庫
npm run db:reset
npm run db:migrate
```

#### Docker 容器無法啟動

```bash
# 檢查日誌
docker-compose logs synergymesh

# 重建映像
docker-compose build --no-cache
docker-compose up -d
```

---

## 📚 進階指南

- [完整部署檢查清單](./DEPLOYMENT_CHECKLIST.md)
- [系統架構文檔](./docs/architecture/SYSTEM_ARCHITECTURE.md)
- [運維手冊](./docs/operations/)
- [API 文檔](./docs/AUTO_ASSIGNMENT_API.md)

---

## 🤝 支援

- 📖 [文檔](./docs/)
- 🐛 [問題報告](https://github.com/SynergyMesh-admin/Unmanned-Island/issues)
- 💬 [討論](https://github.com/SynergyMesh-admin/Unmanned-Island/discussions)

---

---

## Quick Start - Production Deployment

### 📋 5-Minute Quick Setup

#### 1️⃣ Environment Preparation

```bash
# Clone repository
git clone https://github.com/SynergyMesh-admin/Unmanned-Island.git
cd unmanned-island

# Copy environment configuration
cp .env.example .env

# Edit .env file and set production values
nano .env  # or use vim/code
```

#### 2️⃣ Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

#### 3️⃣ Build Application

```bash
# Compile all modules
npm run build

# Run tests
npm run test

# Run linting
npm run lint
```

#### 4️⃣ Start Services

```bash
# Development environment
npm run dev:stack

# Or use Docker
docker-compose up -d

# Verify services
curl http://localhost:3000/health
```

---

### 📦 Core Module Initialization

#### Contract Service

```bash
cd core/contract_service/contracts-L1/contracts
npm install
npm run build
npm start
```

#### MCP Servers

```bash
cd mcp-servers
npm install
npm start
```

#### Python Tool Validation

```bash
python3 tools/docs/validate_index.py --verbose
```

---

### 🐳 Docker Deployment

#### Development Quick Start

```bash
docker-compose -f docker-compose.dev.yml up -d
docker-compose logs -f
```

#### Production Deployment

```bash
# Build image
docker build -t synergymesh:latest .

# Start containers
docker-compose up -d

# View logs
docker-compose logs -f synergymesh
```

---

### 🔄 Kubernetes Deployment

#### Basic Steps

```bash
# Create namespace
kubectl create namespace synergymesh

# Create ConfigMap and Secret
kubectl apply -f infrastructure/kubernetes/manifests/configmap.yaml
kubectl apply -f infrastructure/kubernetes/manifests/secret.yaml

# Deploy application
kubectl apply -f infrastructure/kubernetes/manifests/deployment.yaml
kubectl apply -f infrastructure/kubernetes/manifests/service.yaml

# Verify deployment
kubectl rollout status deployment/synergymesh -n synergymesh
kubectl get pods -n synergymesh
```

---

### 📊 Monitoring & Logging

#### View Application Logs

```bash
# Docker
docker-compose logs -f synergymesh

# Kubernetes
kubectl logs -f deployment/synergymesh -n synergymesh

# System logs
tail -f logs/synergymesh.log
```

#### Access Monitoring Dashboards

```
Prometheus: http://localhost:9090
Grafana:    http://localhost:3000 (admin/admin)
```

---

### 🔒 Security Configuration

#### SSL/TLS Setup

```bash
# Generate self-signed certificate (testing only)
openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365 -nodes

# Or use Let's Encrypt
certbot certonly --standalone -d your-domain.com
```

#### API Key Management

```bash
# Generate new JWT secret
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

# Update .env file
JWT_SECRET=<generated-key>
```

---

### ✅ Verification Checklist

- [ ] Application health check passes: `curl http://localhost:3000/health`
- [ ] Database connection works: `npm run test:db`
- [ ] All API endpoints are accessible
- [ ] Monitoring system is operational
- [ ] Logs are being recorded correctly
- [ ] Security scan shows no high-risk issues

---

### 🆘 Troubleshooting

#### Port Already in Use

```bash
# Find process using port
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

#### Database Connection Failed

```bash
# Check database service
docker ps | grep postgres
psql -h localhost -U postgres -d synergymesh

# Or reset database
npm run db:reset
npm run db:migrate
```

#### Docker Container Won't Start

```bash
# Check logs
docker-compose logs synergymesh

# Rebuild image
docker-compose build --no-cache
docker-compose up -d
```

---

## 📚 Advanced Guides

- [Complete Deployment Checklist](./DEPLOYMENT_CHECKLIST.md)
- [System Architecture](./docs/architecture/SYSTEM_ARCHITECTURE.md)
- [Operations Guide](./docs/operations/)
- [API Documentation](./docs/AUTO_ASSIGNMENT_API.md)

---

## 🤝 Support

- 📖 [Documentation](./docs/)
- 🐛
  [Issue Tracker](https://github.com/SynergyMesh-admin/Unmanned-Island/issues)
- 💬
  [Discussions](https://github.com/SynergyMesh-admin/Unmanned-Island/discussions)
