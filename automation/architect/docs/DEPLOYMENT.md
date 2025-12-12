# Deployment Guide

# 部署指南 - Automation Architect

## 目錄 Table of Contents

1. [系統需求](#系統需求)
2. [本地開發部署](#本地開發部署)
3. [Docker 部署](#docker-部署)
4. [Kubernetes 部署](#kubernetes-部署)
5. [生產環境配置](#生產環境配置)
6. [監控與告警](#監控與告警)
7. [故障排除](#故障排除)

---

## 系統需求

### 硬件需求 Hardware Requirements

**最小配置 Minimum:**

- CPU: 2 cores
- RAM: 4 GB
- Disk: 20 GB

**推薦配置 Recommended:**

- CPU: 4+ cores
- RAM: 8+ GB
- Disk: 50+ GB SSD

### 軟件需求 Software Requirements

- **Python**: >= 3.8 (推薦 3.10)
- **Node.js**: >= 18.0.0 (如需 TypeScript 分析)
- **Docker**: >= 20.10 (可選)
- **Kubernetes**: >= 1.24 (可選)

---

## 本地開發部署

### 1. 克隆倉庫

```bash
git clone https://github.com/we-can-fix/synergymesh.git
cd synergymesh/automation-architect
```

### 2. 創建虛擬環境

```bash
# 使用 venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 或使用 conda
conda create -n automation-architect python=3.10
conda activate automation-architect
```

### 3. 安裝依賴

```bash
pip install -r requirements.txt
```

### 4. 配置環境變量

```bash
# 創建 .env 文件
cat > .env << EOF
ENVIRONMENT=development
LOG_LEVEL=DEBUG
REDIS_HOST=localhost
REDIS_PORT=6379
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=automation_architect
POSTGRES_USER=automation
POSTGRES_PASSWORD=your_password_here
EOF
```

### 5. 初始化數據庫（可選）

```bash
# 如果使用 PostgreSQL
createdb automation_architect
python scripts/init_db.py
```

### 6. 運行測試

```bash
# 運行單元測試
pytest tests/unit/ -v

# 運行集成測試
pytest tests/integration/ -v

# 生成覆蓋率報告
pytest --cov=core --cov-report=html
```

### 7. 運行示例

```bash
python examples/basic_usage.py
```

---

## Docker 部署

### 單容器部署

#### 1. 構建 Docker 鏡像

```bash
cd automation-architect
docker build -t automation-architect:latest .
```

#### 2. 運行容器

```bash
docker run -d \
  --name automation-architect \
  -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/reports:/app/reports \
  -v $(pwd)/config:/app/config \
  -e ENVIRONMENT=production \
  -e LOG_LEVEL=INFO \
  automation-architect:latest
```

#### 3. 查看日誌

```bash
docker logs -f automation-architect
```

### Docker Compose 部署（推薦）

#### 1. 啟動所有服務

```bash
cd automation-architect
docker-compose up -d
```

這將啟動：

- automation-architect (主服務)
- redis (緩存)
- postgres (數據庫)
- prometheus (監控)
- grafana (可視化)

#### 2. 查看服務狀態

```bash
docker-compose ps
```

#### 3. 查看日誌

```bash
# 所有服務
docker-compose logs -f

# 特定服務
docker-compose logs -f automation-architect
```

#### 4. 停止服務

```bash
docker-compose down
```

#### 5. 清理數據

```bash
# 停止並刪除卷
docker-compose down -v
```

### 服務訪問

- **主服務**: <http://localhost:8000>
- **Prometheus**: <http://localhost:9090>
- **Grafana**: <http://localhost:3000> (admin/admin)
- **Redis**: localhost:6379
- **PostgreSQL**: localhost:5432

---

## Kubernetes 部署

### 1. 準備 Kubernetes 配置

創建 `k8s/` 目錄並添加以下文件：

#### namespace.yaml

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: automation-architect
```

#### configmap.yaml

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: automation-architect-config
  namespace: automation-architect
data:
  ENVIRONMENT: 'production'
  LOG_LEVEL: 'INFO'
  REDIS_HOST: 'redis-service'
  POSTGRES_HOST: 'postgres-service'
```

#### secret.yaml

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: automation-architect-secret
  namespace: automation-architect
type: Opaque
stringData:
  POSTGRES_PASSWORD: 'your_password_here'
  API_TOKEN: 'your_api_token_here'
```

#### deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: automation-architect
  namespace: automation-architect
spec:
  replicas: 3
  selector:
    matchLabels:
      app: automation-architect
  template:
    metadata:
      labels:
        app: automation-architect
    spec:
      containers:
        - name: automation-architect
          image: automation-architect:latest
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: automation-architect-config
            - secretRef:
                name: automation-architect-secret
          resources:
            requests:
              cpu: '500m'
              memory: '1Gi'
            limits:
              cpu: '2000m'
              memory: '4Gi'
          volumeMounts:
            - name: logs
              mountPath: /app/logs
            - name: reports
              mountPath: /app/reports
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
      volumes:
        - name: logs
          persistentVolumeClaim:
            claimName: logs-pvc
        - name: reports
          persistentVolumeClaim:
            claimName: reports-pvc
```

#### service.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: automation-architect-service
  namespace: automation-architect
spec:
  selector:
    app: automation-architect
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

### 2. 部署到 Kubernetes

```bash
# 創建命名空間
kubectl apply -f k8s/namespace.yaml

# 部署配置和密鑰
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# 部署應用
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### 3. 驗證部署

```bash
# 查看 Pod 狀態
kubectl get pods -n automation-architect

# 查看服務
kubectl get svc -n automation-architect

# 查看日誌
kubectl logs -f deployment/automation-architect -n automation-architect
```

### 4. 擴展副本

```bash
kubectl scale deployment automation-architect \
  --replicas=5 \
  -n automation-architect
```

### 5. 滾動更新

```bash
# 更新鏡像
kubectl set image deployment/automation-architect \
  automation-architect=automation-architect:v2.1.0 \
  -n automation-architect

# 查看更新狀態
kubectl rollout status deployment/automation-architect \
  -n automation-architect
```

---

## 生產環境配置

### 環境變量

創建 `.env.production` 文件：

```bash
# 環境
ENVIRONMENT=production

# 日誌
LOG_LEVEL=INFO
LOG_FORMAT=json

# Redis
REDIS_HOST=redis.production.internal
REDIS_PORT=6379
REDIS_PASSWORD=<strong-password>
REDIS_DB=0

# PostgreSQL
POSTGRES_HOST=postgres.production.internal
POSTGRES_PORT=5432
POSTGRES_DB=automation_architect
POSTGRES_USER=automation
POSTGRES_PASSWORD=<strong-password>
POSTGRES_SSL=true

# 安全
API_TOKEN=<your-secure-token>
JWT_SECRET=<your-jwt-secret>
ENCRYPTION_KEY=<your-encryption-key>

# 性能
MAX_WORKERS=16
TIMEOUT=600
CACHE_TTL=7200

# 監控
PROMETHEUS_PORT=9090
ENABLE_METRICS=true
```

### 安全配置

#### 1. 使用密鑰管理

```bash
# AWS Secrets Manager
aws secretsmanager create-secret \
  --name automation-architect/production \
  --secret-string file://secrets.json

# Azure Key Vault
az keyvault secret set \
  --vault-name automation-vault \
  --name db-password \
  --value <password>
```

#### 2. 啟用 TLS

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name automation-architect.example.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 性能優化

#### 1. Redis 集群

```yaml
# docker-compose.production.yml
redis-cluster:
  image: redis:7-alpine
  command: redis-server --cluster-enabled yes
  deploy:
    replicas: 6
```

#### 2. PostgreSQL 調優

```sql
-- postgresql.conf
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
work_mem = 10MB
min_wal_size = 1GB
max_wal_size = 4GB
```

---

## 監控與告警

### Prometheus 指標

訪問 <http://localhost:9090> 查看指標。

**重要指標:**

- `analysis_duration_seconds`: 分析耗時
- `analysis_total`: 分析總數
- `security_issues_detected`: 安全問題檢測數
- `repair_success_rate`: 修復成功率
- `system_cpu_usage`: CPU 使用率
- `system_memory_usage`: 內存使用

### Grafana 儀表板

1. 訪問 <http://localhost:3000>
2. 默認登錄: admin/admin
3. 添加 Prometheus 數據源
4. 導入儀表板: `monitoring/grafana/dashboards/automation-architect.json`

### 告警規則

創建 `monitoring/prometheus/alerts.yml`:

```yaml
groups:
  - name: automation-architect
    rules:
      - alert: HighCPUUsage
        expr: system_cpu_usage > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: 'High CPU usage detected'

      - alert: HighSecurityIssues
        expr: security_issues_detected > 10
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: 'High number of security issues'
```

---

## 故障排除

### 常見問題

#### 1. 容器無法啟動

```bash
# 查看詳細日誌
docker logs automation-architect

# 檢查配置
docker exec automation-architect env
```

#### 2. 數據庫連接失敗

```bash
# 測試連接
docker exec automation-architect \
  psql -h postgres -U automation -d automation_architect -c "SELECT 1"

# 檢查網絡
docker network inspect automation-network
```

#### 3. 性能問題

```bash
# 查看資源使用
docker stats automation-architect

# 增加資源限制
docker update --memory=8g --cpus=4 automation-architect
```

#### 4. Redis 連接超時

```bash
# 測試 Redis
docker exec automation-redis redis-cli ping

# 檢查連接數
docker exec automation-redis redis-cli INFO clients
```

### 日誌級別調整

```bash
# 臨時調整日誌級別
docker exec automation-architect \
  python -c "import logging; logging.basicConfig(level=logging.DEBUG)"

# 永久調整
docker exec -it automation-architect sh
vi config/automation-architect.yml
# 修改 log_level: DEBUG
```

### 數據備份

```bash
# 備份 PostgreSQL
docker exec postgres pg_dump -U automation automation_architect > backup.sql

# 恢復
cat backup.sql | docker exec -i postgres psql -U automation automation_architect
```

---

## 維護與升級

### 版本升級

```bash
# 1. 備份數據
./scripts/backup.sh

# 2. 停止服務
docker-compose down

# 3. 拉取新版本
docker pull automation-architect:v2.1.0

# 4. 更新配置
vi docker-compose.yml  # 更新鏡像標籤

# 5. 啟動服務
docker-compose up -d

# 6. 驗證
docker-compose logs -f automation-architect
```

### 健康檢查

```bash
# HTTP 健康檢查
curl http://localhost:8000/health

# 深度健康檢查
curl http://localhost:8000/health/deep
```

---

## 參考資料 References

- [Docker 官方文檔](https://docs.docker.com/)
- [Kubernetes 官方文檔](https://kubernetes.io/docs/)
- [Prometheus 監控指南](https://prometheus.io/docs/)
- [項目 README](../README.md)

---

**版本 Version**: 2.0.0  
**最後更新 Last Updated**: 2025-11-25
