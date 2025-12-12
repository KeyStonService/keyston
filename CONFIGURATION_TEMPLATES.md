# 📐 系統配置範本 / System Configuration Templates

## 概述 / Overview

本目錄包含完整的系統配置範本，可直接複製使用或作為參考。

This directory contains complete system configuration templates that can be
copied directly or used as reference.

---

## 📁 範本清單 / Templates List

### 1. 基本應用配置 / Basic Application Configuration

**檔案**: `example-app-config.yml`

```yaml
# 應用程式基本配置
app:
  name: synergymesh
  version: 4.0.0
  environment: development
  port: 3000

# 日誌配置
logging:
  level: INFO
  format: json
  output: stdout

# 資料庫配置
database:
  type: postgresql
  host: localhost
  port: 5432
  name: synergymesh

# 快取配置
cache:
  type: redis
  host: localhost
  port: 6379
  ttl: 3600
```

### 2. Kubernetes 部署配置 / Kubernetes Deployment Template

**檔案**: `example-k8s-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: synergymesh
  namespace: synergymesh
spec:
  replicas: 3
  selector:
    matchLabels:
      app: synergymesh
  template:
    metadata:
      labels:
        app: synergymesh
    spec:
      containers:
        - name: synergymesh
          image: synergymesh:latest
          ports:
            - containerPort: 3000
          env:
            - name: ENVIRONMENT
              valueFrom:
                configMapKeyRef:
                  name: synergymesh-config
                  key: environment
          resources:
            requests:
              cpu: 250m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 10
```

### 3. Docker Compose 範本 / Docker Compose Template

**檔案**: `example-docker-compose.yml`

```yaml
version: '3.9'

services:
  app:
    build: .
    ports:
      - '3000:3000'
    environment:
      - ENVIRONMENT=development
      - DATABASE_URL=postgresql://user:password@db:5432/synergymesh
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=synergymesh
    volumes:
      - db_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - '6379:6379'

volumes:
  db_data:
```

### 4. 監控配置 / Monitoring Configuration

**檔案**: `example-monitoring.yml`

```yaml
# Prometheus 配置
prometheus:
  scrape_configs:
    - job_name: 'synergymesh'
      static_configs:
        - targets: ['localhost:3000']

# Alerting 配置
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']

# 告警規則
rule_files:
  - '/etc/prometheus/rules/*.yml'
```

### 5. 安全配置 / Security Configuration

**檔案**: `example-security.yml`

```yaml
# JWT 配置
jwt:
  secret: ${JWT_SECRET}
  expiration: 24h
  algorithm: HS256

# API 認證
auth:
  enabled: true
  provider: jwt

# CORS 配置
cors:
  enabled: true
  allowed_origins:
    - http://localhost:3000
    - https://example.com
  allowed_methods:
    - GET
    - POST
    - PUT
    - DELETE

# SSL/TLS
tls:
  enabled: true
  cert_file: /etc/ssl/certs/server.crt
  key_file: /etc/ssl/private/server.key
```

---

## 🚀 使用範本 / Using Templates

### 步驟 1: 複製範本 / Copy Template

```bash
cp examples/example-app-config.yml config/my-config.yml
```

### 步驟 2: 自定義配置 / Customize Configuration

```bash
# 編輯檔案
nano config/my-config.yml

# 或使用 sed 替換
sed -i 's/localhost/your-host/g' config/my-config.yml
```

### 步驟 3: 驗證配置 / Validate Configuration

```bash
# 驗證 YAML
python3 tools/docs/validate_index.py --config config/my-config.yml

# 或使用 yamllint
yamllint config/my-config.yml
```

### 步驟 4: 應用配置 / Apply Configuration

```bash
# 應用到系統
docker-compose -f docker-compose.yml config validate

# 或推送到 Kubernetes
kubectl apply -f infrastructure/kubernetes/manifests/
```

---

## 📋 常見配置場景 / Common Configuration Scenarios

### 開發環境 / Development Environment

```bash
# 複製開發範本
cp examples/example-docker-compose.yml docker-compose.dev.yml

# 修改環境變數
sed -i 's/production/development/g' docker-compose.dev.yml

# 啟動
docker-compose -f docker-compose.dev.yml up -d
```

### 預發佈環境 / Staging Environment

```bash
# 複製預發佈範本
cp examples/example-k8s-deployment.yaml infrastructure/kubernetes/staging-deployment.yaml

# 修改副本數
sed -i 's/replicas: 3/replicas: 2/g' infrastructure/kubernetes/staging-deployment.yaml

# 部署
kubectl apply -f infrastructure/kubernetes/staging-deployment.yaml -n staging
```

### 生產環境 / Production Environment

```bash
# 複製生產範本
cp examples/example-k8s-deployment.yaml infrastructure/kubernetes/prod-deployment.yaml

# 設置更嚴格的資源限制
sed -i 's/250m/500m/g' infrastructure/kubernetes/prod-deployment.yaml

# 部署
kubectl apply -f infrastructure/kubernetes/prod-deployment.yaml -n production
```

---

## 🔐 敏感資訊管理 / Sensitive Information Management

### ✅ 應該做 / Do's

```yaml
# 使用環境變數
database:
  url: ${DATABASE_URL}

# 使用 Secret 對象
secrets:
  api_key: ${API_KEY}

# 使用 .gitignore
.env
.env.local
secrets/
```

### ❌ 不應該做 / Don'ts

```yaml
# ❌ 硬編碼密鑰
database:
  password: "hardcoded_password"

# ❌ 提交敏感檔案
git add .env

# ❌ 在日誌中打印密鑰
console.log("API_KEY:", API_KEY)
```

---

## 📚 進階配置 / Advanced Configuration

### 多環境配置 / Multi-environment Configuration

```
config/
├── shared/
│   └── base.yml
├── development/
│   └── config.yml
├── staging/
│   └── config.yml
└── production/
    └── config.yml
```

### 配置優先級 / Configuration Priority

```
環境變數 > 命令行參數 > 本地配置 > 預設值
```

### 合併配置 / Merging Configurations

```bash
# 使用 YAML 合併
yq merge config/shared/base.yml config/development/config.yml
```

---

## 📖 相關文檔 / Related Documentation

- [配置中心](./config/README.md)
- [部署清單](./DEPLOYMENT_MANIFEST.md)
- [環境變數](./ENV.example)

---

## 🤝 貢獻範本 / Contributing Templates

如果您有新的配置範本，歡迎提交 PR！

If you have new configuration templates, welcome to submit a PR!

```bash
# 建立新範本
cp examples/example-template.yml examples/example-my-template.yml

# 編輯並提交
git add examples/example-my-template.yml
git commit -m "docs: Add new configuration template"
git push origin feature/new-template
```

---

## 📞 支援 / Support

- 📖 [文檔](./docs/)
- 🐛 [報告問題](https://github.com/SynergyMesh-admin/Unmanned-Island/issues)
- 💬 [討論](https://github.com/SynergyMesh-admin/Unmanned-Island/discussions)
