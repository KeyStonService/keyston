# Intelligent Hyperautomation - 使用說明

## 概述

本模板套件整合了「核心理念與定位」與「無人機/自動駕駛核心規範」，提供平台中立、可移植的治理與驗證準則。

## 文檔結構

### 核心文檔

- **core-principles.md**：核心理念與定位，定義技術助手的能力框架與互動原則
- **uav-autonomous-driving-governance.md**：UAV/AD 治理規範，提供安全、合規與可追溯的實施準則
- **usage-notes.md**（本文件）：使用說明與最佳實踐
- **ci-cd-strategy.md**：CI/CD 策略與自動化流程
- **sbom-placeholder.json**：SBOM 佔位文件，需在 CI 中生成實際 SBOM

### 策略文件

- **policies/rego/uav_ad.rego**：OPA/Conftest 策略，用於驗證 UAV/AD 配置
- **policies/gatekeeper/uav-ad-labels.yaml**：Gatekeeper 約束，驗證必要標籤
- **policies/gatekeeper/geo-fencing.yaml**：地理圍欄策略約束

### 契約文件

- **contracts/file-contract.json**：文件契約與雜湊佔位符

## 快速開始

### 1. 整合到現有專案

```bash
# 複製模板到您的專案
cp -r intelligent-hyperautomation /path/to/your/project/

# 根據需求調整配置
cd /path/to/your/project/intelligent-hyperautomation
```

### 2. 配置標籤

確保您的 Kubernetes 資源包含必要標籤：

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: uav-production
  labels:
    namespace.io/managed-by: "platform-team"
    namespace.io/domain: "uav"
    namespace.io/team: "robotics"
    namespace.io/environment: "production"
    namespace.io/lifecycle: "stable"
```

### 3. 啟用地理圍欄

為 UAV 系統配置地理圍欄：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: uav-geo-config
  labels:
    uav.io/system: "uav"
data:
  geo.fence.enabled: "true"
  geo.fence.regions: "TW-Taipei, TW-Taichung, TW-Kaohsiung"
```

### 4. 設置風險等級

根據操作風險設置安全等級：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: uav-controller
  labels:
    uav.io/system: "uav"
    uav.io/safety-level: "L4"
    uav.io/risk-category: "high"
spec:
  # ... deployment spec
```

## 策略驗證

### Conftest 驗證

在 CI 中使用 Conftest 驗證配置：

```bash
# 安裝 Conftest
brew install conftest  # macOS
# 或
curl -L https://github.com/open-policy-agent/conftest/releases/download/v0.47.0/conftest_0.47.0_Linux_x86_64.tar.gz | tar xz

# 驗證配置
conftest test your-deployment.yaml -p policies/rego/
```

### Gatekeeper 約束

將 Gatekeeper 約束應用到集群：

```bash
# 應用標籤驗證約束
kubectl apply -f policies/gatekeeper/uav-ad-labels.yaml

# 應用地理圍欄約束
kubectl apply -f policies/gatekeeper/geo-fencing.yaml

# 驗證約束狀態
kubectl get constraints
```

### Dry-run 測試

在應用前進行 dry-run 測試：

```bash
kubectl apply -f your-deployment.yaml --dry-run=server
```

## CI/CD 整合

### Pre-commit 階段

```yaml
# .github/workflows/pre-commit.yml
- name: Validate YAML
  run: yamllint -c .yamllint .

- name: Validate Kubernetes manifests
  run: kubeconform -strict -summary your-manifests/

- name: Run Conftest policies
  run: conftest test your-manifests/ -p policies/rego/
```

### CI 階段

```yaml
# .github/workflows/ci.yml
- name: Gatekeeper dry-run
  run: |
    kubectl apply -f policies/gatekeeper/ --dry-run=server
    
- name: Calculate file hashes
  run: |
    b3sum docs/core-principles.md > hashes.txt
    openssl dgst -sha3-512 policies/rego/uav_ad.rego >> hashes.txt
```

### CD 階段

使用 ArgoCD 或 Flux 進行聲明式部署：

```yaml
# argocd-application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: uav-system
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/your-repo
    targetRevision: v2.0.0
    path: intelligent-hyperautomation
  destination:
    server: https://kubernetes.default.svc
    namespace: uav-production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

## 安全最佳實踐

### 1. 雙重雜湊驗證

在 CI 中計算並驗證文件雜湊：

```bash
# 使用 BLAKE3
b3sum docs/core-principles.md

# 使用 SHA3-512
openssl dgst -sha3-512 docs/uav-autonomous-driving-governance.md
```

### 2. SBOM 生成

使用 CycloneDX 生成 SBOM：

```bash
# 使用 npm
npm install -g @cyclonedx/cyclonedx-npm
cyclonedx-npm --output-file docs/sbom.json

# 使用 Syft (支援多種語言)
syft packages dir:. -o cyclonedx-json > docs/sbom.json
```

### 3. 簽章驗證

使用 Cosign 簽署和驗證：

```bash
# 簽署 SBOM
cosign sign-blob --key cosign.key docs/sbom.json > sbom.sig

# 驗證簽章
cosign verify-blob --key cosign.pub --signature sbom.sig docs/sbom.json
```

## 命名規範

### 平台中立標籤

使用 `namespace.io/*` 作為通用標籤前綴：

- `namespace.io/managed-by`：管理者或團隊
- `namespace.io/domain`：業務領域
- `namespace.io/team`：負責團隊
- `namespace.io/environment`：環境（dev/staging/production）
- `namespace.io/region`：地理區域
- `namespace.io/lifecycle`：生命週期階段

### UAV/AD 特定標籤

使用 `uav.io/*` 作為 UAV/AD 專用標籤前綴：

- `uav.io/system`：系統類型（uav 或 ad）
- `uav.io/safety-level`：安全等級（L0-L5）
- `uav.io/risk-category`：風險類別（low/medium/high）
- `uav.io/geo-fence-enabled`：地理圍欄狀態
- `uav.io/emergency-stop`：緊急停止狀態

## 故障排除

### 策略驗證失敗

如果 Conftest 驗證失敗：

1. 檢查資源是否包含所有必要標籤
2. 驗證標籤值格式是否正確
3. 確認策略文件路徑正確

### Gatekeeper 約束無法應用

如果約束無法應用：

1. 確認 Gatekeeper 已安裝在集群中
2. 檢查 ConstraintTemplate 是否存在
3. 查看約束狀態：`kubectl describe constraint <name>`

### 地理圍欄配置錯誤

如果地理圍欄配置被拒絕：

1. 確認 `geo.fence.enabled` 設為 "true" 或 "false"
2. 驗證 `geo.fence.regions` 格式：`XX-RegionName` (如 TW-Taipei)
3. 多個區域用逗號分隔

## 進階配置

### 自定義策略

擴展 `policies/rego/uav_ad.rego`：

```rego
# 自定義規則：檢查資源限制
deny[msg] {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  not container.resources.limits.memory
  msg := sprintf("容器 '%s' 必須設置記憶體限制", [container.name])
}
```

### 多環境支援

為不同環境創建變體：

```bash
intelligent-hyperautomation/
├── base/           # 基礎配置
├── overlays/
│   ├── dev/       # 開發環境
│   ├── staging/   # 預生產環境
│   └── production/ # 生產環境
```

## 更新與維護

### 版本管理

使用 Git 標籤管理版本：

```bash
# 創建新版本
git tag -a v2.0.1 -m "Update policies for new safety requirements"
git push origin v2.0.1
```

### 回滾流程

如需回滾到前一版本：

```bash
# Git 回滾
git revert <commit-id>
git tag v2.0.2
git push --tags

# Kubernetes 回滾
kubectl rollout undo deployment/uav-controller

# GitOps 回滾
argocd app rollback uav-system <revision>
```

## 支援與貢獻

### 取得協助

- 查看文檔：[docs/](docs/)
- 提交 Issue：GitHub Issues
- 聯繫團隊：<platform-team@example.com>

### 貢獻指南

1. Fork 專案
2. 創建功能分支
3. 提交變更
4. 發起 Pull Request

## 授權

本模板套件採用 MIT 授權。

---

**版本**：2.0.0  
**最後更新**：2025-11-25  
**維護者**：Platform Team
