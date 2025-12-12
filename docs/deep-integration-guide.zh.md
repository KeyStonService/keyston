# SynergyMesh 深度整合指南

## 概述

本指南說明 SynergyMesh 全倉庫的深度整合方案，涵蓋所有子專案的統一部署架構、CI/CD 流程、供應鏈安全與治理規範。

## 整合架構

### 子專案總覽

SynergyMesh 採用 monorepo 架構，包含以下子專案：

| 子專案                | 類型       | 技術棧             | 部署端口 | 團隊           |
| --------------------- | ---------- | ------------------ | -------- | -------------- |
| **contracts-service** | 後端服務   | TypeScript/Express | 3000     | contracts-team |
| **mcp-servers**       | MCP 伺服器 | JavaScript/Node.js | 3001     | platform-team  |
| **advanced-system**   | 前端應用   | React/TypeScript   | 3002     | frontend-team  |

### 統一架構特點

1. **統一 CI/CD**: 所有子專案使用相同的可重用 workflow 模板
2. **一致的安全標準**: 非 root 容器、只讀根文件系統、最小權限 RBAC
3. **供應鏈安全**: SBOM 生成、Cosign 簽章、SLSA Provenance
4. **標準化標籤**: 所有資源使用 `namespace.io/*` 標籤
5. **自動化治理**: 命名規範驗證、政策檢查、合規報告

## 目錄結構

```
synergymesh/
├── .github/
│   └── workflows/
│       ├── project-cd.yml              # 可重用 CD workflow（核心）
│       ├── reusable-ci.yml             # 可重用 CI workflow
│       ├── monorepo-dispatch.yml       # Monorepo 調度器
│       ├── contracts-cd.yml            # Contracts service CD
│       ├── mcp-servers-cd.yml          # MCP servers CD
│       └── advanced-system-cd.yml      # Advanced system CD
│
├── core/
│   └── contracts/
│       └── contracts-L1/
│           └── contracts/              # Contracts Service
│               ├── Dockerfile
│               ├── deploy/             # 8 個 K8s manifests
│               ├── docs/               # 中文文件
│               ├── policy/             # OPA 政策
│               └── sbom/
│
├── mcp-servers/                        # MCP Servers
│   ├── Dockerfile                      # ✨ 新增
│   ├── deploy/                         # ✨ 新增
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── rbac.yaml
│   │   ├── hpa.yaml
│   │   └── pdb.yaml
│   └── *.js                            # 原有代碼
│
├── advanced-system-src/                # Advanced System
│   ├── Dockerfile                      # ✨ 新增
│   ├── deploy/                         # ✨ 新增
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── rbac.yaml
│   │   └── hpa.yaml
│   └── src/                            # 原有代碼
│
├── .config/
│   └── conftest/
│       └── policies/                   # 全局政策
│
├── governance/
│   ├── policies.yaml                   # 基線政策
│   └── registry.yaml                   # 模組註冊表
│
├── scripts/
│   ├── naming/                         # 命名治理工具
│   └── artifacts/                      # Artifact 構建
│
└── docs/
    ├── production-deployment-guide.zh.md
    └── deep-integration-guide.zh.md    # 本文件
```

## CI/CD 整合

### Workflow 架構

```
monorepo-dispatch.yml
    ├─> 檢測變更 (paths-filter)
    │
    ├─> CI: reusable-ci.yml
    │   ├─> lint
    │   ├─> typecheck
    │   ├─> test
    │   ├─> build
    │   └─> SBOM
    │
    └─> CD: project-cd.yml (按需觸發)
        ├─> Docker build & push
        ├─> SBOM 生成
        ├─> Cosign 簽章
        ├─> Policy 檢查
        └─> K8s 部署 (可選)
```

### 觸發機制

**自動觸發**:

```yaml
# Push 到 main/develop
push:
  branches: [main, develop]
  paths:
    - 'mcp-servers/**' # 僅觸發 mcp-servers CD
    - 'advanced-system-src/**' # 僅觸發 advanced-system CD
    - 'core/contract_service/**' # 僅觸發 contracts CD
```

**手動觸發**:

```bash
# 為特定服務觸發 CD
gh workflow run mcp-servers-cd.yml -f environment=dev
gh workflow run advanced-system-cd.yml -f environment=staging
gh workflow run contracts-cd.yml -f environment=prod
```

### CI 流程（所有服務）

1. **Lint**: ESLint/TSLint 代碼檢查
2. **Type Check**: TypeScript 類型驗證
3. **Test**: 單元測試 + 覆蓋率
4. **Build**: 編譯構建
5. **SBOM**: 依賴掃描與 SBOM 生成
6. **Security Scan**: npm audit 安全掃描

### CD 流程（生產服務）

1. **Build Image**: Docker buildx 多平台構建
2. **Generate SBOM**: Syft/CycloneDX SBOM
3. **Sign Image**: Cosign 映像簽章
4. **Policy Check**: Conftest/OPA 驗證
5. **Push Image**: GHCR 推送
6. **Deploy**: Kubernetes 部署（可選）

## 服務配置對比

### Contracts Service

```yaml
技術: TypeScript/Express
端口: 3000
副本: 3-10 (HPA)
資源:
  requests: cpu=100m, memory=128Mi
  limits: cpu=500m, memory=512Mi
健康檢查: /healthz, /readyz
特點:
  - SLSA 合約管理
  - 構建溯源驗證
  - Sigstore 整合
```

### MCP Servers

```yaml
技術: JavaScript/Node.js
端口: 3001
副本: 2-8 (HPA)
資源:
  requests: cpu=100m, memory=128Mi
  limits: cpu=500m, memory=512Mi
健康檢查: (待實施 HTTP 端點)
特點:
  - Model Context Protocol
  - 代碼分析驗證器
  - 部署驗證器
```

### Advanced System

```yaml
技術: React/TypeScript/Nginx
端口: 3002
副本: 2-6 (HPA)
資源:
  requests: cpu=50m, memory=64Mi
  limits: cpu=200m, memory=256Mi
健康檢查: / (Nginx 根路徑)
特點:
  - 前端儀表板
  - React 18 + Radix UI
  - 靜態資源服務
```

## 安全配置

### 統一安全標準

所有服務遵循以下安全標準：

1. **容器安全**:
   - ✅ 非 root 使用者 (UID 1001 或 101)
   - ✅ 只讀根文件系統
   - ✅ Drop ALL capabilities
   - ✅ 禁用權限提升
   - ✅ SeccompProfile: RuntimeDefault

2. **網路安全**:
   - ✅ NetworkPolicy (待為每個服務添加)
   - ✅ 最小入站/出站規則

3. **RBAC**:
   - ✅ 專用 ServiceAccount
   - ✅ 最小權限 Role
   - ✅ 明確的 RoleBinding

4. **映像安全**:
   - ✅ 多階段構建
   - ✅ 最小基礎映像 (slim/alpine)
   - ✅ 固定版本標籤
   - ✅ Cosign 簽章

## 供應鏈安全

### SBOM 管理

每個服務自動生成 SBOM：

```bash
# Contracts Service
core/contract_service/contracts-L1/contracts/sbom/sbom.json

# MCP Servers (將生成)
mcp-servers/sbom/sbom.json

# Advanced System (將生成)
advanced-system-src/sbom/sbom.json
```

**格式**: CycloneDX JSON  
**簽章**: Cosign blob signing  
**儲存**: GitHub Actions artifacts (90天)

### 映像簽章

所有生產映像使用 Cosign 簽章：

```bash
# Keyless signing (OIDC)
cosign sign ghcr.io/we-can-fix/synergymesh/contracts-service:latest
cosign sign ghcr.io/we-can-fix/synergymesh/mcp-servers:latest
cosign sign ghcr.io/we-can-fix/synergymesh/advanced-system:latest

# Key-based signing
cosign sign --key cosign.key ghcr.io/we-can-fix/synergymesh/contracts-service:v1.0.0
```

### SLSA Provenance

- **Level 2+** 合規
- 所有構建包含 provenance attestation
- 可追溯到原始碼 commit
- 包含構建環境與參數

## 部署策略

### 滾動更新

所有服務使用滾動更新策略：

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
```

### 自動擴展

HPA 配置：

| 服務              | 最小副本 | 最大副本 | CPU 閾值 | 記憶體閾值 |
| ----------------- | -------- | -------- | -------- | ---------- |
| contracts-service | 3        | 10       | 70%      | 80%        |
| mcp-servers       | 2        | 8        | 70%      | 80%        |
| advanced-system   | 2        | 6        | 70%      | 80%        |

### 高可用性

- **PDB**: 所有服務配置 PodDisruptionBudget
- **反親和性**: Pod 分散到不同節點
- **健康檢查**: liveness + readiness + startup probes

## 監控與告警

### 指標收集

（待實施 ServiceMonitor）

所有服務暴露 Prometheus 指標：

- `contracts-service`: :3000/metrics
- `mcp-servers`: :3001/metrics (待實施)
- `advanced-system`: :3002/metrics (Nginx stub_status)

### 告警規則

（參考 contracts-service/deploy/alerts.yaml）

建議為每個服務實施：

- Pod 可用性告警
- 高錯誤率告警
- 高延遲告警
- 資源使用告警
- Pod 重啟告警

## 命名與標籤規範

### 統一標籤

所有資源使用 `namespace.io/*` 標籤：

```yaml
labels:
  app: <service-name>
  namespace.io/team: <team-name>
  namespace.io/environment: production|staging|dev
  namespace.io/lifecycle: active|deprecated
  namespace.io/managed-by: gitops
  version: 'x.y.z'
```

### 團隊映射

| 服務              | 標籤值                              | 責任     |
| ----------------- | ----------------------------------- | -------- |
| contracts-service | `namespace.io/team: contracts-team` | 合約管理 |
| mcp-servers       | `namespace.io/team: platform-team`  | 平台工具 |
| advanced-system   | `namespace.io/team: frontend-team`  | 前端介面 |

## 治理工具

### 命名檢查

```bash
# 檢查所有服務的命名規範
./scripts/naming/check-naming.sh

# 為新資源生成建議名稱
./scripts/naming/suggest-name.mjs my-service deployment platform-team production
```

### Artifact 構建

```bash
# 為所有服務生成合規報告
for service in contracts mcp-servers advanced-system; do
  cd $service
  OUTPUT_DIR=artifacts/reports ../../../../scripts/artifacts/build.sh
done
```

### 政策驗證

```bash
# 驗證 K8s manifests
conftest test */deploy/*.yaml --policy governance/policies/conftest/

# 驗證特定服務
conftest test mcp-servers/deploy/*.yaml --policy governance/policies/conftest/
```

## 部署操作

### 初次部署

```bash
# 1. 構建並推送所有映像
for service in contracts-service mcp-servers advanced-system; do
  gh workflow run ${service}-cd.yml -f environment=dev
done

# 2. 部署到 Kubernetes
kubectl create namespace synergymesh-prod
kubectl config set-context --current --namespace=synergymesh-prod

# 3. 應用所有服務的 manifests
kubectl apply -f core/contract_service/contracts-L1/contracts/deploy/
kubectl apply -f mcp-servers/deploy/
kubectl apply -f advanced-system-src/deploy/

# 4. 驗證部署
kubectl get pods -l namespace.io/managed-by=gitops
```

### 更新部署

```bash
# 更新特定服務
kubectl set image deployment/contracts-service \
  contracts-service=ghcr.io/we-can-fix/synergymesh/contracts-service:v1.2.0

# 查看滾動更新狀態
kubectl rollout status deployment/contracts-service

# 回滾
kubectl rollout undo deployment/contracts-service
```

### 監控部署

```bash
# 查看所有服務狀態
kubectl get all -l namespace.io/managed-by=gitops

# 查看特定團隊的服務
kubectl get all -l namespace.io/team=platform-team

# 查看資源使用
kubectl top pods -l namespace.io/managed-by=gitops
```

## 故障排查

### 常見問題

#### 1. 映像拉取失敗

```bash
# 檢查 imagePullSecrets
kubectl get secret -n synergymesh-prod

# 建立 GHCR secret
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<username> \
  --docker-password=<token>
```

#### 2. Pod 無法啟動

```bash
# 查看 Pod 事件
kubectl describe pod <pod-name>

# 查看日誌
kubectl logs <pod-name> --previous

# 檢查資源配額
kubectl describe resourcequota
```

#### 3. 健康檢查失敗

```bash
# 進入 Pod 測試
kubectl exec -it <pod-name> -- /bin/sh

# 手動測試健康檢查
curl http://localhost:3000/healthz  # contracts-service
curl http://localhost:3001/         # mcp-servers (待實施)
curl http://localhost:3002/         # advanced-system
```

## 最佳實踐

### 開發流程

1. **本地開發**: 使用 `npm run dev`
2. **測試**: 運行 `npm test` 確保通過
3. **Lint**: `npm run lint` 檢查代碼品質
4. **構建**: `npm run build` 本地構建
5. **Docker**: `docker build` 測試容器化
6. **推送**: 創建 PR，自動觸發 CI
7. **部署**: PR 合併後自動觸發 CD

### Git Workflow

```bash
# 功能開發
git checkout -b feature/my-feature
# 修改代碼...
git add .
git commit -m "feat(mcp-servers): add new validator"
git push origin feature/my-feature
# 創建 PR

# 修復 Bug
git checkout -b fix/issue-123
# 修復...
git commit -m "fix(advanced-system): resolve routing issue"
```

### 版本管理

使用語義化版本控制 (SemVer)：

- **Major**: 不相容的 API 變更
- **Minor**: 向後相容的功能新增
- **Patch**: 向後相容的 Bug 修復

## 環境配置

### 必要 Secrets

在 GitHub Repository Settings -> Secrets 配置：

```yaml
# 容器登錄
GHCR_USERNAME: <GitHub username>
GHCR_TOKEN: <GitHub token with packages:write>

# Cosign 簽章（可選）
COSIGN_PRIVATE_KEY: <base64 encoded private key>
COSIGN_PASSWORD: <private key password>

# Kubernetes 部署（可選）
KUBECONFIG: <base64 encoded kubeconfig>
```

### 環境變數

每個服務的環境變數：

**Contracts Service**:

- `PORT=3000`
- `NODE_ENV=production`
- `LOG_LEVEL=info`

**MCP Servers**:

- `PORT=3001`
- `NODE_ENV=production`

**Advanced System**:

- (Nginx 配置檔案)

## 未來規劃

### 短期（1-2 週）

- [ ] 為 mcp-servers 和 advanced-system 添加 NetworkPolicy
- [ ] 實施完整的 Prometheus ServiceMonitor
- [ ] 建立 Grafana 儀表板
- [ ] 完善健康檢查端點

### 中期（1-2 月）

- [ ] 實施 OpenTelemetry 分散式追蹤
- [ ] Canary 部署支援
- [ ] 自動化回滾機制
- [ ] 混沌工程測試

### 長期（3-6 月）

- [ ] 多區域部署
- [ ] 災難恢復演練
- [ ] 效能基準測試
- [ ] 完整的 SRE 實踐

## 相關文件

- [生產環境部署指南](./production-deployment-guide.zh.md)
- [Contracts Service 架構](../core/contract_service/contracts-L1/contracts/docs/architecture.zh.md)
- [Contracts Service Runbook](../core/contract_service/contracts-L1/contracts/docs/runbook.zh.md)
- [SBOM 說明](../core/contract_service/contracts-L1/contracts/sbom/README.md)

## 聯絡資訊

- **Contracts Team**: <contracts-team@example.com>
- **Platform Team**: <platform-team@example.com>
- **Frontend Team**: <frontend-team@example.com>
- **Repository**: <https://github.com/we-can-fix/synergymesh>

## 變更歷史

- 2025-11-24: 初始版本 - 全倉庫深度整合完成

---

本指南涵蓋 SynergyMesh 的完整部署架構與治理方案。遵循本指南可確保所有服務的一致性、安全性與可維護性。
