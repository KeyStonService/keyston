# 生產環境部署指南

## 概述

本指南說明 SynergyMesh 專案的企業級生產環境部署架構，包含 GitOps、供應鏈安全、政策驗證與自動化治理。

## 架構特點

### 核心原則

- ✅ **最小化變更**: 保留既有功能，僅做必要擴充
- ✅ **去 AXIOM 化**: 使用標準化的 `namespace.io/*` 標籤
- ✅ **平台中立**: 支援 ArgoCD/Flux、Gatekeeper/Kyverno
- ✅ **供應鏈安全**: SBOM、Provenance、SLSA、Cosign
- ✅ **中文優先**: 文件與註解以繁體中文為主

### 技術棧

- **容器化**: Docker (多階段構建、Debian-based)
- **編排**: Kubernetes 1.30+
- **CI/CD**: GitHub Actions (可重用 workflows)
- **簽章**: Sigstore/Cosign
- **SBOM**: CycloneDX、Syft
- **政策**: OPA/Rego、Conftest
- **監控**: Prometheus、Alertmanager
- **追蹤**: (規劃中) OpenTelemetry

## 目錄結構

```
synergymesh/
├── .github/
│   └── workflows/
│       ├── project-cd.yml          # 可重用 CD workflow
│       ├── contracts-cd.yml        # Contracts service CD
│       └── monorepo-dispatch.yml   # Monorepo CI dispatcher
│
├── core/
│   └── contracts/
│       └── contracts-L1/
│           └── contracts/          # Contracts Service
│               ├── src/            # 原始碼
│               ├── deploy/         # Kubernetes manifests
│               │   ├── deployment.yaml
│               │   ├── service.yaml
│               │   ├── rbac.yaml
│               │   ├── networkpolicy.yaml
│               │   ├── hpa.yaml
│               │   ├── pdb.yaml
│               │   ├── monitoring.yaml
│               │   └── alerts.yaml
│               ├── docs/           # 文件
│               │   ├── architecture.zh.md
│               │   └── runbook.zh.md
│               ├── policy/         # 政策定義
│               │   └── manifest-policies.rego
│               ├── sbom/           # SBOM 相關
│               ├── Dockerfile      # 容器映像定義
│               └── package.json
│
├── .config/
│   └── conftest/
│       └── policies/
│           └── naming_policy.rego  # 命名規範政策
│
├── governance/
│   ├── policies.yaml               # 治理政策配置
│   └── registry.yaml               # 模組註冊表
│
├── scripts/
│   ├── naming/
│   │   ├── check-naming.sh         # 命名規範檢查
│   │   └── suggest-name.mjs        # 命名建議工具
│   └── artifacts/
│       └── build.sh                # Artifact 構建
│
├── artifacts/
│   └── reports/
│       └── schema/
│           ├── compliance.schema.json
│           └── sla.schema.json
│
└── docs/
    └── production-deployment-guide.zh.md  # 本文件
```

## 快速開始

### 先決條件

1. **必要工具**:
   - Docker 20.10+
   - kubectl 1.30+
   - Node.js 18+
   - Conftest 0.54+

2. **可選工具**:
   - Cosign（映像簽章）
   - Syft（SBOM 生成）
   - ajv-cli（schema 驗證）

### 本地開發

```bash
# 進入 contracts service 目錄
cd core/contract_service/contracts-L1/contracts

# 安裝依賴
npm install

# 開發模式
npm run dev

# 構建
npm run build

# 測試
npm test

# 類型檢查
npm run typecheck

# Lint
npm run lint
```

### 本地構建 Docker 映像

```bash
cd core/contract_service/contracts-L1/contracts

# 構建映像
docker build -t contracts-service:local .

# 運行容器
docker run -p 3000:3000 contracts-service:local

# 健康檢查
curl http://localhost:3000/healthz
```

### 驗證 Kubernetes Manifests

```bash
# 使用 Conftest 驗證
cd core/contract_service/contracts-L1/contracts
conftest test deploy/*.yaml --policy ../../../../../../governance/policies/conftest

# 使用命名檢查腳本
../../../../../../scripts/naming/check-naming.sh
```

## CI/CD Pipeline

### Workflow 觸發

**自動觸發**:

- Push 到 `main` 或 `develop` 分支
- 修改 `core/contract_service/contracts-L1/contracts/**` 路徑下的檔案

**手動觸發**:

```bash
# 透過 GitHub CLI
gh workflow run contracts-cd.yml -f environment=dev

# 或透過 GitHub UI
# Actions -> Contracts Service CD -> Run workflow
```

### Pipeline 階段

#### 1. 構建與推送 (build-and-push)

- ✅ Docker Buildx 多平台構建
- ✅ 映像標籤策略（branch, PR, semver, SHA）
- ✅ GHCR 推送
- ✅ SBOM 生成（Syft/CycloneDX）
- ✅ Cosign 簽章（keyless 或 key-based）
- ✅ Cache 優化（GitHub Actions cache）

#### 2. 政策檢查 (policy-check)

- ✅ Kubernetes manifests 驗證
- ✅ Conftest/OPA 政策執行
- ✅ SBOM 驗證

#### 3. 部署 (deploy)

- ✅ Kubernetes 部署（可選）
- ✅ Rolling update 策略
- ✅ Rollout 狀態驗證

### 環境變數與 Secrets

需要在 GitHub Repository Settings -> Secrets 中配置：

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

## 供應鏈安全

### SBOM (Software Bill of Materials)

**生成方式**:

```bash
# 使用 CycloneDX
npx @cyclonedx/cyclonedx-npm --output-file sbom.json

# 使用 Syft（從映像）
syft packages docker:contracts-service:latest -o cyclonedx-json=sbom.json
```

**簽章**:

```bash
# 使用 Cosign 簽章 SBOM
cosign sign-blob --key cosign.key sbom.json > sbom.json.sig

# 驗證簽章
cosign verify-blob --key cosign.pub --signature sbom.json.sig sbom.json
```

**CI/CD 整合**:

- SBOM 在構建階段自動生成
- 作為 artifact 上傳到 GitHub Actions
- 保留 90 天

### 映像簽章

**Keyless Signing（推薦）**:

```bash
# 使用 OIDC 身份
cosign sign \
  -a "repo=$GITHUB_REPOSITORY" \
  -a "workflow=$GITHUB_WORKFLOW" \
  ghcr.io/we-can-fix/synergymesh/contracts-service:latest
```

**Key-based Signing**:

```bash
# 生成金鑰對
cosign generate-key-pair

# 簽章
cosign sign --key cosign.key \
  ghcr.io/we-can-fix/synergymesh/contracts-service:latest

# 驗證
cosign verify --key cosign.pub \
  ghcr.io/we-can-fix/synergymesh/contracts-service:latest
```

### SLSA Provenance

- **Level 2+** 合規
- Docker buildx 自動生成 provenance
- 包含構建環境與參數
- 可追溯到原始碼 commit

## 政策驗證

### Conftest 政策

**位置**: `governance/policies/conftest/` 和 `policy/`

**驗證項目**:

- ✅ 資源限制（requests/limits）
- ✅ 安全上下文（runAsNonRoot, allowPrivilegeEscalation）
- ✅ 健康檢查（livenessProbe, readinessProbe）
- ✅ 標籤規範（namespace.io/*）
- ✅ 映像標籤（禁止 :latest）
- ✅ 特權容器（禁止）
- ✅ Port 命名

**執行方式**:

```bash
# 驗證單一檔案
conftest test deploy/deployment.yaml --policy governance/policies/conftest

# 驗證所有 manifests
conftest test deploy/*.yaml --policy governance/policies/conftest --all-namespaces

# 生成 JSON 報告
conftest test deploy/*.yaml --policy governance/policies/conftest --output json
```

### 命名規範

**模式**:

- Namespace: `^(team|tenant|feature)-[a-z0-9-]+$`
- Deployment/Service: `^[a-z0-9]([-a-z0-9]*[a-z0-9])?$`
- 最大長度: 63 字元

**必要標籤**:

- `namespace.io/team`: 團隊標識
- `namespace.io/environment`: 環境（dev/staging/prod）
- `namespace.io/lifecycle`: 生命週期（active/deprecated）

**檢查工具**:

```bash
# 自動檢查
./scripts/naming/check-naming.sh

# 命名建議
./scripts/naming/suggest-name.mjs my-service deployment contracts-team production
```

## Kubernetes 部署

### 部署清單

1. **deployment.yaml**: 主要部署配置
   - 3 副本（高可用）
   - 資源限制（CPU: 100m-500m, Memory: 128Mi-512Mi）
   - 安全上下文（非 root, 只讀根文件系統）
   - 健康檢查（liveness, readiness, startup）
   - Pod 反親和性

2. **service.yaml**: 服務暴露
   - ClusterIP 類型
   - Port 80 -> 3000

3. **rbac.yaml**: 權限管理
   - ServiceAccount
   - Role（最小權限）
   - RoleBinding

4. **networkpolicy.yaml**: 網路隔離
   - 入站白名單（Ingress, 同 namespace, Prometheus）
   - 出站限制（DNS, K8s API, HTTPS）

5. **hpa.yaml**: 水平自動擴展
   - 最小 3 副本，最大 10 副本
   - CPU 70%, Memory 80% 觸發

6. **pdb.yaml**: Pod 中斷預算
   - 最小可用 2 副本

### 部署命令

```bash
cd core/contract_service/contracts-L1/contracts/deploy

# 應用所有配置
kubectl apply -f .

# 或逐一應用
kubectl apply -f rbac.yaml
kubectl apply -f service.yaml
kubectl apply -f deployment.yaml
kubectl apply -f hpa.yaml
kubectl apply -f pdb.yaml
kubectl apply -f networkpolicy.yaml
kubectl apply -f monitoring.yaml
kubectl apply -f alerts.yaml

# 驗證部署
kubectl rollout status deployment/contracts-service
kubectl get pods -l app=contracts-service
```

### 更新映像

```bash
# 更新映像標籤
kubectl set image deployment/contracts-service \
  contracts-service=ghcr.io/we-can-fix/synergymesh/contracts-service:v1.2.3

# 或編輯 deployment
kubectl edit deployment contracts-service
```

### 回滾

```bash
# 查看歷史
kubectl rollout history deployment/contracts-service

# 回滾到上一個版本
kubectl rollout undo deployment/contracts-service

# 回滾到特定版本
kubectl rollout undo deployment/contracts-service --to-revision=3
```

## 監控與告警

### Prometheus 監控

**ServiceMonitor** (如果使用 Prometheus Operator):

```bash
kubectl apply -f deploy/monitoring.yaml
```

**指標端點**: `/metrics`

**關鍵指標**:

- `http_requests_total`: 總請求數
- `http_request_duration_seconds`: 請求延遲
- `process_cpu_seconds_total`: CPU 使用
- `process_resident_memory_bytes`: 記憶體使用

### 告警規則

**PrometheusRule**:

```bash
kubectl apply -f deploy/alerts.yaml
```

**告警項目**:

- `ContractsServicePodDown`: Pod 不可用 (critical)
- `ContractsServiceHighErrorRate`: 錯誤率 > 5% (warning)
- `ContractsServiceHighLatency`: P99 延遲 > 1s (warning)
- `ContractsServiceFrequentRestarts`: Pod 頻繁重啟 (warning)
- `ContractsServiceHighMemoryUsage`: 記憶體使用 > 90% (warning)
- `ContractsServiceHighCPUUsage`: CPU 使用 > 90% (warning)
- `ContractsServicePodNotReady`: Pod 不就緒 > 10 分鐘 (warning)

### Grafana 儀表板

（待建立）

預計包含:

- 請求量與錯誤率
- 延遲分佈（P50, P95, P99）
- 資源使用（CPU, 記憶體）
- Pod 狀態與副本數
- 依賴健康度

## 故障排查

詳細故障排查步驟請參考：

- [運維手冊 (Runbook)](../core/contract_service/contracts-L1/contracts/docs/runbook.zh.md)
- [架構文件](../core/contract_service/contracts-L1/contracts/docs/architecture.zh.md)

### 快速診斷

```bash
# 檢查 Pod 狀態
kubectl get pods -l app=contracts-service

# 查看日誌
kubectl logs -l app=contracts-service --tail=100 -f

# 查看事件
kubectl get events --sort-by='.lastTimestamp' | grep contracts-service

# 查看資源使用
kubectl top pod -l app=contracts-service

# 進入 Pod
kubectl exec -it <pod-name> -- /bin/sh
```

## Artifact 與報告

### 構建 Artifacts

```bash
cd core/contract_service/contracts-L1/contracts
OUTPUT_DIR=artifacts/reports ../../../../scripts/artifacts/build.sh
```

**生成內容**:

- `manifests/manifests-inventory.json`: Kubernetes 資源清單
- `sbom/sbom-summary.json`: SBOM 摘要
- `compliance/compliance-report.json`: 合規報告
- `sla/sla-report.json`: SLA 報告
- `index.json`: 主索引

### 驗證報告 Schema

```bash
# 安裝 ajv-cli
npm install -g ajv-cli

# 驗證合規報告
ajv validate \
  -s artifacts/reports/schema/compliance.schema.json \
  -d artifacts/reports/compliance/compliance-report.json

# 驗證 SLA 報告
ajv validate \
  -s artifacts/reports/schema/sla.schema.json \
  -d artifacts/reports/sla/sla-report.json
```

## 安全最佳實踐

### 容器安全

- ✅ 使用非 root 使用者 (UID 1001)
- ✅ 只讀根文件系統
- ✅ Drop ALL capabilities
- ✅ 禁用權限提升
- ✅ SeccompProfile: RuntimeDefault

### 網路安全

- ✅ NetworkPolicy 限制流量
- ✅ 僅必要的入站/出站規則
- ✅ TLS 加密（Ingress 層）

### 供應鏈安全

- ✅ SBOM 生成與簽章
- ✅ 映像簽章與驗證
- ✅ Provenance 追溯
- ✅ 固定版本（避免 :latest）

### 運行時安全

- ✅ 最小權限 RBAC
- ✅ 資源限制
- ✅ 健康檢查
- ✅ 審計日誌

## 效能調優

### 資源配置

**預設值**（適合大多數場景）:

```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

**高負載場景**:

```yaml
resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: 1000m
    memory: 1Gi
```

### 水平擴展

```bash
# 手動擴展
kubectl scale deployment contracts-service --replicas=5

# 調整 HPA
kubectl edit hpa contracts-service-hpa
```

### Node.js 調優

```yaml
env:
- name: NODE_OPTIONS
  value: "--max-old-space-size=512 --optimize-for-size"
```

## 貢獻指南

請參考 [CONTRIBUTING.md](../CONTRIBUTING.md)

## 授權

MIT License - 詳見 [LICENSE](../LICENSE)

## 聯絡資訊

- **團隊**: contracts-team
- **Repository**: <https://github.com/we-can-fix/synergymesh>
- **問題回報**: <https://github.com/we-can-fix/synergymesh/issues>

## 變更歷史

- 2025-11-24: 初始版本建立
