# Intelligent Hyperautomation - 智能超自動化模板套件

## 概述

Intelligent Hyperautomation 是一個整合「核心理念與定位」與「無人機/自動駕駛核心規範」的平台中立模板套件，提供治理、驗證與自動化準則。

## 特點

- ✅ **平台中立**：可移植至任意 Kubernetes/GitOps 平台
- ✅ **嚴格結構**：Kubernetes 1.30 對齊，無未知欄位
- ✅ **安全第一**：SHA3-512 + BLAKE3 雙重雜湊
- ✅ **可追溯性**：完整審計鏈與 SBOM 支援
- ✅ **UAV/AD 治理**：專門的無人機與自動駕駛安全規範

## 目錄結構

```
intelligent-hyperautomation/
├── README.md                        # 本文件
├── docs/                            # 文檔目錄
│   ├── core-principles.md          # 核心理念與定位
│   ├── uav-autonomous-driving-governance.md  # UAV/AD 治理規範
│   ├── usage-notes.md              # 使用說明
│   ├── ci-cd-strategy.md           # CI/CD 策略
│   └── sbom-placeholder.json       # SBOM 佔位文件
├── policies/                        # 策略目錄
│   ├── rego/                       # OPA/Conftest 策略
│   │   └── uav_ad.rego            # UAV/AD 驗證策略
│   └── gatekeeper/                 # Gatekeeper 約束
│       ├── uav-ad-labels.yaml     # 標籤驗證約束
│       └── geo-fencing.yaml       # 地理圍欄約束
├── contracts/                       # 契約目錄
│   └── file-contract.json          # 文件契約與雜湊
└── templates/                       # 模板目錄
    └── impl/                       # 實作模板（預留）
```

## 快速開始

### 1. 複製模板

```bash
# 複製整個目錄到您的專案
cp -r intelligent-hyperautomation /path/to/your/project/
```

### 2. 配置資源標籤

為您的 Kubernetes 資源添加必要標籤：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: uav-controller
  labels:
    # 標準標籤
    namespace.io/managed-by: "platform-team"
    namespace.io/domain: "uav"
    namespace.io/environment: "production"
    namespace.io/lifecycle: "stable"
    # UAV/AD 特定標籤
    uav.io/system: "uav"
    uav.io/safety-level: "L4"
    uav.io/risk-category: "high"
spec:
  # ... deployment spec
```

### 3. 配置地理圍欄（僅 UAV 系統）

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: uav-geo-config
  labels:
    uav.io/system: "uav"
data:
  geo.fence.enabled: "true"
  geo.fence.regions: "TW-Taipei, TW-Taichung, JP-Tokyo"
```

### 4. 驗證策略

```bash
# 使用 Conftest 驗證
conftest test your-deployment.yaml -p policies/rego/

# 使用 Gatekeeper（需要集群）
kubectl apply -f policies/gatekeeper/ --dry-run=server
```

## 核心文檔

### [核心理念與定位](docs/core-principles.md)

定義技術助手的能力框架、互動原則、技術棧專長與最佳實踐。

### [UAV/AD 治理規範](docs/uav-autonomous-driving-governance.md)

無人機與自動駕駛系統的安全、合規與可追溯準則。

### [使用說明](docs/usage-notes.md)

詳細的使用指南、配置範例與故障排除。

### [CI/CD 策略](docs/ci-cd-strategy.md)

持續整合與持續部署的自動化策略與最佳實踐。

## 策略驗證

### OPA/Conftest 策略

位於 `policies/rego/uav_ad.rego`，包含以下驗證規則：

- ✅ UAV/AD 系統必須標註系統類型（uav.io/system）
- ✅ 必須標註安全等級（uav.io/safety-level: L0-L5）
- ✅ 高風險操作需標註風險類別（uav.io/risk-category）
- ✅ UAV 系統需配置地理圍欄
- ✅ 容器必須設置資源限制
- ✅ Namespace 需包含標準標籤

### Gatekeeper 約束

#### uav-ad-labels.yaml

驗證資源包含必要標籤：

- namespace.io/* 標準標籤
- uav.io/* UAV/AD 特定標籤

#### geo-fencing.yaml

驗證 UAV 系統的地理圍欄配置：

- geo.fence.enabled 必須為 "true" 或 "false"
- 啟用時必須指定 geo.fence.regions
- 區域格式：XX-RegionName（如 TW-Taipei）

## 標籤規範

### 標準命名空間標籤

| 標籤 | 說明 | 範例值 |
|------|------|--------|
| namespace.io/managed-by | 管理者 | platform-team |
| namespace.io/domain | 業務領域 | uav, ad |
| namespace.io/team | 負責團隊 | robotics |
| namespace.io/environment | 環境 | dev, staging, production |
| namespace.io/region | 地理區域 | asia-east1 |
| namespace.io/lifecycle | 生命週期 | experimental, stable, deprecated |

### UAV/AD 特定標籤

| 標籤 | 說明 | 範例值 |
|------|------|--------|
| uav.io/system | 系統類型 | uav, ad |
| uav.io/safety-level | 安全等級 | L0-L5 |
| uav.io/risk-category | 風險類別 | low, medium, high |
| uav.io/geo-fence-enabled | 地理圍欄狀態 | true, false |
| uav.io/emergency-stop | 緊急停止狀態 | enabled, disabled |

## 安全與合規

### 雙重雜湊

在 CI 中計算文件雜湊：

```bash
# BLAKE3
b3sum docs/core-principles.md

# SHA3-512
openssl dgst -sha3-512 policies/rego/uav_ad.rego
```

### SBOM 生成

使用 Syft 或 CycloneDX 生成 SBOM：

```bash
syft packages dir:. -o cyclonedx-json > docs/sbom.json
```

### 簽章驗證

使用 Cosign 簽署和驗證：

```bash
# 簽署
cosign sign-blob --key cosign.key docs/sbom.json > sbom.sig

# 驗證
cosign verify-blob --key cosign.pub --signature sbom.sig docs/sbom.json
```

## CI/CD 整合

### GitHub Actions 範例

```yaml
name: Validate Policies

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Conftest
        run: |
          curl -L https://github.com/open-policy-agent/conftest/releases/download/v0.47.0/conftest_0.47.0_Linux_x86_64.tar.gz | tar xz
          sudo mv conftest /usr/local/bin/
      
      - name: Validate policies
        run: conftest test manifests/ -p intelligent-hyperautomation/policies/rego/
```

## GitOps 部署

### ArgoCD

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: intelligent-hyperautomation
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/your-repo
    targetRevision: v2.0.0
    path: intelligent-hyperautomation
  destination:
    server: https://kubernetes.default.svc
    namespace: uav-production
```

### Flux

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: intelligent-hyperautomation
spec:
  interval: 1m
  url: https://github.com/your-org/your-repo
  ref:
    tag: v2.0.0
```

## 驗證清單

部署前檢查：

- [ ] 所有資源包含必要標籤
- [ ] UAV 系統配置地理圍欄
- [ ] 風險等級正確分類
- [ ] 策略驗證通過（Conftest + Gatekeeper）
- [ ] SBOM 已生成
- [ ] 雙重雜湊已計算
- [ ] 容器使用 SHA256 digest

## 故障排除

### 策略驗證失敗

```bash
# 查看詳細錯誤
conftest test deployment.yaml -p policies/rego/ --output json

# 驗證特定策略
conftest test deployment.yaml -p policies/rego/uav_ad.rego
```

### Gatekeeper 約束問題

```bash
# 檢查約束狀態
kubectl get constraints

# 查看約束詳情
kubectl describe constraint uav-ad-required-labels
```

## 版本歷史

### v2.0.0 (2025-11-25)

- ✨ 初始版本發布
- ✨ 整合核心理念與定位
- ✨ 添加 UAV/AD 治理規範
- ✨ 實作 OPA/Conftest 策略
- ✨ 實作 Gatekeeper 約束
- ✨ 完整 CI/CD 策略文檔

## 貢獻

歡迎貢獻！請遵循以下步驟：

1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 發起 Pull Request

## 授權

本專案採用 MIT 授權 - 詳見 LICENSE 文件。

## 聯繫方式

- **維護團隊**：Platform Team
- **電子郵件**：<platform-team@example.com>
- **問題回報**：GitHub Issues

## 致謝

感謝所有貢獻者和社群成員對本專案的支持。

---

**版本**：2.0.0  
**最後更新**：2025-11-25  
**狀態**：穩定版
