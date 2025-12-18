# Contracts Service 架構文件

## 概述

Contracts Service 是 SynergyMesh 平台的核心服務之一，負責 SLSA (Supply-chain Levels for Software Artifacts) 合約管理與構建溯源驗證。

## 服務定位

- **類型**: 微服務 (Microservice)
- **語言**: TypeScript / Node.js
- **框架**: Express.js
- **部署方式**: Kubernetes容器化部署
- **團隊**: contracts-team

## 核心功能

### 1. 溯源認證 (Provenance Attestation)

- 建立構建認證
- 驗證溯源資料
- 匯入/匯出認證
- 檔案摘要生成

### 2. SLSA 驗證

- SLSA Level 1-3 合規驗證
- 契約認證
- 摘要生成
- 認證摘要查詢

## 技術架構

### 分層架構

```
┌─────────────────────────────────────────┐
│           API Layer (Routes)             │
│  /api/v1/provenance/*                    │
│  /api/v1/slsa/*                          │
│  /healthz, /readyz, /metrics             │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│        Controller Layer                  │
│  - ProvenanceController                  │
│  - SLSAController                        │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Service Layer                    │
│  - 業務邏輯處理                           │
│  - 資料驗證                               │
│  - 外部依賴呼叫                           │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      External Dependencies               │
│  - Sigstore (簽章驗證)                   │
│  - SBOM 服務                             │
└─────────────────────────────────────────┘
```

### 目錄結構

```
core/contract_service/contracts-L1/contracts/
├── src/
│   ├── server.ts              # 應用程式入口
│   ├── routes.ts              # 路由定義
│   ├── config.ts              # 配置管理
│   ├── controllers/           # 控制器層
│   │   ├── provenance.ts
│   │   └── slsa.ts
│   ├── middleware/            # 中介層
│   │   ├── logging.ts
│   │   └── error.ts
│   └── services/              # 服務層
│       └── ...
├── deploy/                    # Kubernetes 配置
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── rbac.yaml
│   ├── networkpolicy.yaml
│   ├── hpa.yaml
│   ├── pdb.yaml
│   ├── monitoring.yaml
│   └── alerts.yaml
├── docs/                      # 文件
│   ├── architecture.zh.md
│   └── runbook.zh.md
├── policy/                    # 政策定義
│   └── manifest-policies.rego
├── sbom/                      # 軟體物料清單
│   └── README.md
├── Dockerfile                 # 容器映像定義
└── package.json               # 專案配置
```

## 資料流

### 請求處理流程

```
客戶端 → Ingress → Service → Pod
                              ↓
                   Logging Middleware
                              ↓
                         Routes
                              ↓
                      Controllers
                              ↓
                   Business Logic
                              ↓
                  External Services
                              ↓
                      Response
```

### 健康檢查流程

```
Kubernetes Probe → /healthz → 200 OK
                 → /readyz  → 200 OK
```

## 安全設計

### 容器安全

- ✅ 非 root 使用者 (UID 1001)
- ✅ 只讀根文件系統
- ✅ 禁用權限提升
- ✅ Drop ALL capabilities
- ✅ SeccompProfile: RuntimeDefault

### 網路安全

- ✅ NetworkPolicy 限制流量
- ✅ 入站流量白名單
- ✅ 出站流量限制
- ✅ TLS 加密（若啟用 Ingress）

### RBAC

- ✅ 專用 ServiceAccount
- ✅ 最小權限原則
- ✅ 明確的 Role 定義
- ✅ RoleBinding 綁定

## 供應鏈安全

### SBOM (Software Bill of Materials)

- 格式: CycloneDX JSON
- 生成時機: 構建階段
- 簽章: Cosign
- 儲存: Artifact Registry

### 映像簽章

- 工具: Sigstore/Cosign
- 模式: Keyless 或 Key-based
- 驗證: 部署前驗證

### SLSA 合規

- 目標級別: SLSA Level 2+
- Provenance: 自動生成
- 建立可重現性: Dockerfile 固定

## 可觀測性

### 日誌

- 結構化日誌 (JSON)
- 追蹤 ID (Trace ID)
- 日誌級別: debug, info, warn, error
- 輸出: stdout/stderr

### 指標

- 端點: `/metrics`
- 格式: Prometheus
- 指標類型:
  - HTTP 請求計數
  - 請求延遲 (histogram)
  - 錯誤率
  - 資源使用

### 告警

- 平台: Prometheus/Alertmanager
- 規則: `deploy/alerts.yaml`
- 嚴重度:
  - `critical`: 服務不可用
  - `warning`: 效能下降

### 追蹤

- (待實施) OpenTelemetry
- Span 覆蓋: HTTP 請求、外部呼叫

## 部署策略

### 發布策略

- 滾動更新 (Rolling Update)
- maxSurge: 1
- maxUnavailable: 0
- 零停機部署

### 自動擴展

- 指標: CPU (70%), 記憶體 (80%)
- 最小副本: 3
- 最大副本: 10
- 穩定視窗: 300s (縮減)

### 高可用性

- 副本數: 3+
- Pod 反親和性: 避免單點故障
- PodDisruptionBudget: 最小可用 2

## 資源配置

### 預設資源

```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

### 環境變數

- `NODE_ENV`: 環境 (production/development)
- `PORT`: 服務端口 (3000)
- `LOG_LEVEL`: 日誌級別 (info)
- `SERVICE_NAME`: 服務名稱

## 外部依賴

### 必要依賴

- Kubernetes API (健康檢查、配置)
- DNS 服務 (服務發現)

### 可選依賴

- Sigstore (簽章驗證)
- 容器登錄 (映像拉取)
- Prometheus (指標收集)

## 災難恢復

### 備份策略

- 配置: Git 版本控制
- 資料: (如適用)

### 恢復步驟

1. 從 Git 恢復配置
2. 重新部署服務
3. 驗證健康檢查
4. 監控指標與日誌

## 效能指標

### SLA 目標

- 可用性: 99.95%
- P99 延遲: < 100ms
- 錯誤率: < 0.05%

### 容量規劃

- 單 Pod QPS: ~100
- 3 副本總 QPS: ~300
- 擴展閾值: CPU > 70%

## 開發與測試

### 本地開發

```bash
npm install
npm run dev
```

### 測試

```bash
npm run lint
npm run typecheck
npm test
```

### 構建

```bash
npm run build
docker build -t contracts-service:local .
```

## 治理與合規

### 標籤規範

- `namespace.io/team`: 團隊標識
- `namespace.io/environment`: 環境標識
- `namespace.io/lifecycle`: 生命週期狀態
- `namespace.io/managed-by`: 管理工具

### 政策驗證

- 工具: Conftest/OPA
- 政策: `policy/manifest-policies.rego`
- 驗證時機: CI/CD Pipeline

## 未來規劃

- [ ] 實施分散式追蹤 (OpenTelemetry)
- [ ] 增加快取層 (Redis)
- [ ] Grafana 儀表板
- [ ] 自動化效能測試
- [ ] A/B 測試支援
- [ ] Canary 部署

## 相關文件

- [運維手冊](./runbook.zh.md)
- [API 文件](../README.md)
- [SBOM](../sbom/README.md)
- [政策定義](../policy/)

## 變更歷史

- 2025-11-24: 初始架構文件建立
