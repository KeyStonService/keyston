# Tier 1: Contracts L1 Service 部署計劃

**服務名稱**: Contracts L1 Service  
**部署層級**: Tier 1 - 核心服務層  
**成熟度評分**: 39/50 (生產就緒)  
**計劃日期**: 2025-11-24  
**預計完成**: Week 1 (3-5 天)

---

## 📊 服務概覽

### 基本資訊

- **位置**: `core/contract_service/contracts-L1/contracts/`
- **類型**: RESTful API 微服務
- **技術棧**: TypeScript, Express.js, Node.js 18+
- **端口**: 3000
- **版本**: 1.0.0

### 核心功能

1. **SLSA Provenance 管理**
   - 構建來源追蹤
   - 供應鏈安全驗證
   - SLSA Level 3 合規

2. **構建認證 (Build Attestation)**
   - 自動化認證生成
   - Sigstore 簽章整合
   - in-toto 格式支援

3. **合約管理**
   - RESTful API 端點
   - 資料驗證 (Zod)
   - 錯誤處理中介層

4. **安全整合**
   - Helmet 安全標頭
   - CORS 跨域配置
   - Sigstore 驗證

---

## 🎯 部署目標與成功標準

### Phase 1.1: 環境準備 (Day 1)

**目標**: 完成部署環境設定

#### 任務清單

- [ ] 確認 Docker 環境 (v20.10+)
- [ ] 確認 Node.js 版本 (v18+)
- [ ] 設定環境變數檔案 (.env)
- [ ] 建立日誌目錄
- [ ] 配置網路設定

#### 環境變數配置

創建 `core/contract_service/contracts-L1/contracts/.env`:

```bash
# 應用程式設定
NODE_ENV=production
PORT=3000
LOG_LEVEL=info
HOST=0.0.0.0

# 資料庫設定 (如需要)
DATABASE_URL=postgresql://user:pass@localhost:5432/contracts_l1
DATABASE_POOL_MIN=2
DATABASE_POOL_MAX=10

# Sigstore 設定
SIGSTORE_VERIFY_URL=https://fulcio.sigstore.dev
SIGSTORE_REKOR_URL=https://rekor.sigstore.dev

# 安全設定
CORS_ORIGIN=https://your-domain.com
API_KEY_SECRET=your-secret-key-here

# 監控設定
ENABLE_METRICS=true
METRICS_PORT=9090
```

#### 成功標準

- ✅ Docker 正常運行
- ✅ 環境變數已設定
- ✅ 網路連通性測試通過

---

### Phase 1.2: 建置與測試 (Day 1-2)

**目標**: 完成應用程式建置與單元測試

#### 任務清單

- [ ] 安裝依賴 (`npm ci`)
- [ ] 執行 TypeScript 型別檢查
- [ ] 執行 ESLint 程式碼檢查
- [ ] 執行單元測試
- [ ] 建置 TypeScript (`npm run build`)
- [ ] 驗證建置產物

#### 建置步驟

```bash
cd core/contract_service/contracts-L1/contracts/

# 1. 安裝依賴
npm ci

# 2. 型別檢查
npm run typecheck

# 3. 程式碼檢查
npm run lint

# 4. 單元測試
npm run test

# 5. 建置
npm run build

# 6. 驗證
ls -la dist/
node dist/server.js --version
```

#### 成功標準

- ✅ 所有測試通過 (0 失敗)
- ✅ ESLint 無警告
- ✅ TypeScript 編譯無錯誤
- ✅ dist/ 目錄包含完整建置產物

---

### Phase 1.3: Docker 映像建置 (Day 2)

**目標**: 建立生產就緒的 Docker 映像

#### 任務清單

- [ ] 建置 Docker 映像
- [ ] 標記映像版本
- [ ] 執行映像安全掃描
- [ ] 測試映像啟動
- [ ] 推送至容器註冊表

#### Docker 建置步驟

```bash
cd core/contract_service/contracts-L1/contracts/

# 1. 建置映像
docker build -t synergymesh-contracts-l1:1.0.0 .
docker build -t synergymesh-contracts-l1:latest .

# 2. 驗證映像大小
docker images | grep synergymesh-contracts-l1

# 3. 安全掃描 (使用 Trivy)
trivy image synergymesh-contracts-l1:1.0.0

# 4. 測試啟動
docker run --rm -p 3000:3000 \
  -e NODE_ENV=production \
  synergymesh-contracts-l1:1.0.0

# 5. 推送至註冊表
docker tag synergymesh-contracts-l1:1.0.0 your-registry/synergymesh-contracts-l1:1.0.0
docker push your-registry/synergymesh-contracts-l1:1.0.0
```

#### 映像規格

- **基礎映像**: node:18-slim
- **多階段建置**: Builder + Runner
- **安全**: 非 root 使用者 (nodejs:1001)
- **預期大小**: ~200-300 MB

#### 成功標準

- ✅ 映像建置成功
- ✅ 安全掃描無高危漏洞
- ✅ 映像啟動正常
- ✅ 健康檢查端點回應

---

### Phase 1.4: 本地部署測試 (Day 2-3)

**目標**: 在本地環境完整測試服務

#### 任務清單

- [ ] 使用 Docker Compose 啟動
- [ ] 驗證健康檢查端點
- [ ] 測試 API 端點
- [ ] 執行整合測試
- [ ] 壓力測試
- [ ] 日誌輸出驗證

#### 啟動服務

```bash
# 使用專案根目錄的 docker-compose.yml
cd /home/runner/work/synergymesh/synergymesh/

# 僅啟動 Contracts L1
docker-compose up -d contracts-l1

# 查看日誌
docker-compose logs -f contracts-l1

# 查看狀態
docker-compose ps contracts-l1
```

#### API 端點測試

```bash
# 1. 健康檢查
curl http://localhost:3000/healthz
# 預期: {"status":"ok","service":"contracts-l1","version":"1.0.0"}

# 2. API 版本資訊
curl http://localhost:3000/api/v1/version
# 預期: {"version":"1.0.0","environment":"production"}

# 3. Provenance 端點
curl http://localhost:3000/api/v1/provenance
# 預期: 200 OK

# 4. SLSA 驗證端點
curl -X POST http://localhost:3000/api/v1/slsa/validate \
  -H "Content-Type: application/json" \
  -d '{"artifact":"test"}'
```

#### 壓力測試

```bash
# 使用 Apache Bench
ab -n 1000 -c 10 http://localhost:3000/healthz

# 預期結果:
# - Requests per second: > 500
# - 95% 回應時間: < 100ms
# - 失敗率: 0%
```

#### 成功標準

- ✅ 健康檢查回應 200 OK
- ✅ 所有 API 端點正常運作
- ✅ 壓力測試通過
- ✅ 無錯誤日誌
- ✅ 記憶體使用 < 512MB
- ✅ CPU 使用 < 50%

---

### Phase 1.5: CI/CD Pipeline 整合 (Day 3)

**目標**: 設定自動化部署流程

#### 任務清單

- [ ] 建立 GitHub Actions workflow
- [ ] 配置自動建置
- [ ] 配置自動測試
- [ ] 配置自動部署
- [ ] 設定 SBOM 生成
- [ ] 配置 Provenance 生成

#### GitHub Actions Workflow

創建 `.github/workflows/deploy-contracts-l1.yml`:

```yaml
name: Deploy Contracts L1

on:
  push:
    branches: [main]
    paths:
      - 'core/contract_service/contracts-L1/contracts/**'
  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      id-token: write
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: core/contract_service/contracts-L1/contracts/package-lock.json
      
      - name: Install Dependencies
        working-directory: core/contract_service/contracts-L1/contracts
        run: npm ci
      
      - name: Lint & Test
        working-directory: core/contract_service/contracts-L1/contracts
        run: |
          npm run lint
          npm run test
      
      - name: Build
        working-directory: core/contract_service/contracts-L1/contracts
        run: npm run build
      
      - name: Generate SBOM
        working-directory: core/contract_service/contracts-L1/contracts
        run: |
          npm install -g @cyclonedx/cyclonedx-npm
          cyclonedx-npm --output-file sbom.json
      
      - name: Build Docker Image
        working-directory: core/contract_service/contracts-L1/contracts
        run: |
          docker build -t ghcr.io/${{ github.repository }}/contracts-l1:${{ github.sha }} .
          docker build -t ghcr.io/${{ github.repository }}/contracts-l1:latest .
      
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Push Docker Image
        run: |
          docker push ghcr.io/${{ github.repository }}/contracts-l1:${{ github.sha }}
          docker push ghcr.io/${{ github.repository }}/contracts-l1:latest
      
      - name: Generate Provenance
        uses: slsa-framework/slsa-github-generator/.github/workflows/generator_container_slsa3.yml@v1.9.0
        with:
          image: ghcr.io/${{ github.repository }}/contracts-l1
          digest: ${{ steps.build.outputs.digest }}
```

#### 成功標準

- ✅ Workflow 成功執行
- ✅ 映像自動推送
- ✅ SBOM 自動生成
- ✅ Provenance 自動生成

---

### Phase 1.6: 生產環境部署 (Day 4)

**目標**: 部署至生產環境

#### 部署選項

##### 選項 A: Kubernetes 部署

創建 `core/contract_service/contracts-L1/contracts/deploy/k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: contracts-l1
  namespace: synergymesh
  labels:
    app: contracts-l1
    tier: core
spec:
  replicas: 3
  selector:
    matchLabels:
      app: contracts-l1
  template:
    metadata:
      labels:
        app: contracts-l1
        tier: core
    spec:
      containers:
      - name: contracts-l1
        image: ghcr.io/your-org/synergymesh/contracts-l1:1.0.0
        ports:
        - containerPort: 3000
          name: http
        env:
        - name: NODE_ENV
          value: "production"
        - name: PORT
          value: "3000"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /healthz
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /healthz
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: contracts-l1
  namespace: synergymesh
spec:
  type: ClusterIP
  selector:
    app: contracts-l1
  ports:
  - port: 80
    targetPort: 3000
    name: http
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: contracts-l1
  namespace: synergymesh
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - contracts-l1.synergymesh.com
    secretName: contracts-l1-tls
  rules:
  - host: contracts-l1.synergymesh.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: contracts-l1
            port:
              number: 80
```

部署命令:

```bash
# 應用配置
kubectl apply -f core/contract_service/contracts-L1/contracts/deploy/k8s/

# 查看部署狀態
kubectl get deployment contracts-l1 -n synergymesh

# 查看 Pod 狀態
kubectl get pods -n synergymesh -l app=contracts-l1

# 查看日誌
kubectl logs -n synergymesh -l app=contracts-l1 -f
```

##### 選項 B: Docker Compose (生產)

使用專案根目錄的 `docker-compose.yml`:

```bash
# 啟動服務
docker-compose up -d contracts-l1

# 擴展副本
docker-compose up -d --scale contracts-l1=3
```

##### 選項 C: AWS ECS 部署

創建 ECS Task Definition 和 Service。

#### 成功標準

- ✅ 服務成功部署
- ✅ 所有實例健康
- ✅ 負載平衡器正常運作
- ✅ HTTPS 憑證有效

---

### Phase 1.7: 監控與告警設定 (Day 4-5)

**目標**: 建立完整的監控與告警系統

#### 任務清單

- [ ] 配置 Prometheus 指標收集
- [ ] 設定 Grafana 儀表板
- [ ] 配置日誌聚合
- [ ] 設定告警規則
- [ ] 配置 on-call 輪值

#### Prometheus 指標端點

在服務中添加 `/metrics` 端點，暴露：

- HTTP 請求計數
- 回應時間分布
- 錯誤率
- 記憶體使用
- CPU 使用

#### Grafana 儀表板

創建包含以下面板的儀表板：

1. **請求指標**
   - RPS (Requests Per Second)
   - 回應時間 (p50, p95, p99)
   - 錯誤率

2. **系統指標**
   - CPU 使用率
   - 記憶體使用率
   - 網路 I/O

3. **業務指標**
   - Provenance 驗證次數
   - SLSA 驗證成功率
   - Attestation 生成次數

#### 告警規則

```yaml
groups:
  - name: contracts-l1
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "高錯誤率檢測"
          description: "Contracts L1 服務錯誤率超過 5%"
      
      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "回應時間過慢"
          description: "95% 回應時間超過 100ms"
      
      - alert: ServiceDown
        expr: up{job="contracts-l1"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "服務停止"
          description: "Contracts L1 服務無法訪問"
```

#### 成功標準

- ✅ Prometheus 正常收集指標
- ✅ Grafana 儀表板顯示正常
- ✅ 告警規則已配置
- ✅ 告警測試通過

---

### Phase 1.8: 性能測試與優化 (Day 5)

**目標**: 確保服務性能達標

#### 任務清單

- [ ] 執行負載測試
- [ ] 執行壓力測試
- [ ] 執行耐久性測試
- [ ] 分析性能瓶頸
- [ ] 執行優化

#### 負載測試

```bash
# 使用 k6 進行負載測試
k6 run - <<EOF
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },  // 提升至 100 用戶
    { duration: '5m', target: 100 },  // 維持 100 用戶
    { duration: '2m', target: 200 },  // 提升至 200 用戶
    { duration: '5m', target: 200 },  // 維持 200 用戶
    { duration: '2m', target: 0 },    // 降至 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<100'], // 95% 請求 < 100ms
    http_req_failed: ['rate<0.01'],   // 錯誤率 < 1%
  },
};

export default function () {
  let res = http.get('http://contracts-l1.synergymesh.com/healthz');
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
  sleep(1);
}
EOF
```

#### 性能目標

- **吞吐量**: > 500 RPS
- **回應時間** (p95): < 100ms
- **回應時間** (p99): < 200ms
- **錯誤率**: < 0.1%
- **可用性**: 99.9%

#### 成功標準

- ✅ 所有性能目標達成
- ✅ 無記憶體洩漏
- ✅ 無性能退化

---

### Phase 1.9: 文檔與 Runbook (Day 5)

**目標**: 完整的操作文檔

#### 任務清單

- [ ] 撰寫 API 文檔
- [ ] 撰寫部署文檔
- [ ] 撰寫 Runbook
- [ ] 撰寫故障排除指南
- [ ] 撰寫災難恢復計劃

#### 文檔清單

1. **API 文檔** (`docs/api/contracts-l1-api.md`)
   - 所有端點說明
   - 請求/回應範例
   - 錯誤代碼

2. **部署文檔** (`docs/deployment/contracts-l1-deployment.md`)
   - 環境要求
   - 部署步驟
   - 回滾程序

3. **Runbook** (`docs/runbooks/contracts-l1-runbook.md`)
   - 日常操作
   - 常見問題處理
   - 緊急聯絡方式

4. **故障排除** (`docs/troubleshooting/contracts-l1-troubleshooting.md`)
   - 常見問題與解決方案
   - 日誌分析指南
   - 調試技巧

#### 成功標準

- ✅ 所有文檔已撰寫
- ✅ 文檔已審查
- ✅ 文檔已發布

---

### Phase 1.10: 上線檢查清單 (Day 5)

**目標**: 最終上線前檢查

#### 檢查清單

- [ ] 所有測試通過
- [ ] 性能測試達標
- [ ] 監控系統正常
- [ ] 告警系統正常
- [ ] 日誌系統正常
- [ ] 備份系統正常
- [ ] 災難恢復計劃已測試
- [ ] 文檔已完成
- [ ] 團隊已培訓
- [ ] 上線計劃已批准

#### 上線流程

1. **凍結代碼** (上線前 24 小時)
2. **最終測試** (上線前 12 小時)
3. **準備回滾方案** (上線前 6 小時)
4. **執行上線** (維護時段)
5. **監控觀察** (上線後 24 小時)
6. **上線後審查** (上線後 1 週)

---

## 📊 資源需求

### 硬體資源

- **CPU**: 1-2 cores
- **記憶體**: 512MB-1GB
- **儲存**: 10GB
- **網路**: 1Gbps

### 人力資源

- **開發**: 1 人 (配置與測試)
- **DevOps**: 1 人 (部署與監控)
- **QA**: 0.5 人 (測試驗證)

### 預算估計

- **雲端運算**: $50-100/月 (單實例)
- **監控工具**: $0 (開源)
- **域名與 SSL**: $20/年
- **總計**: ~$600-1200/年

---

## ⚠️ 風險與緩解

### 風險 1: 依賴項漏洞

**機率**: 中  
**影響**: 高  
**緩解措施**:

- 使用 `npm audit` 定期掃描
- 自動化安全更新
- 使用 Dependabot

### 風險 2: 性能不足

**機率**: 低  
**影響**: 中  
**緩解措施**:

- 水平擴展 (增加副本)
- 啟用快取
- 優化資料庫查詢

### 風險 3: 服務中斷

**機率**: 低  
**影響**: 高  
**緩解措施**:

- 多副本部署 (3+)
- 健康檢查與自動重啟
- 完整備份與恢復計劃

---

## 📞 支援與聯絡

### 技術支援

- **開發團隊**: <dev-team@isynergymesh.com>
- **DevOps 團隊**: <devops@isynergymesh.com>
- **Slack**: #contracts-l1-support

### 緊急聯絡

- **On-Call**: +1-XXX-XXX-XXXX
- **事件響應**: <incident@isynergymesh.com>
- **響應時間**: < 15 分鐘

---

## 📈 後續步驟

完成 Tier 1 部署後，進行：

1. **Week 2**: 部署 MCP Servers (Tier 2)
2. **Week 3**: 整合 Auto-Fix Bot
3. **Week 4**: 監控與儀表板優化

---

**文檔版本**: 1.0.0  
**最後更新**: 2025-11-24  
**審查者**: Platform Governance Team  
**批准狀態**: 待批准
