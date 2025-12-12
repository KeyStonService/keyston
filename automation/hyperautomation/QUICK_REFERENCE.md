# Intelligent Hyperautomation - 快速參考卡

## 📋 必要標籤速查

### 標準命名空間標籤

```yaml
namespace.io/managed-by: 'platform-team'
namespace.io/domain: 'uav' # 或 "ad"
namespace.io/team: 'your-team'
namespace.io/environment: 'production' # dev/staging/production
namespace.io/region: 'asia-east1'
namespace.io/lifecycle: 'stable' # experimental/stable/deprecated
```

### UAV/AD 特定標籤（Deployment）

```yaml
uav.io/system: 'uav' # 或 "ad"
uav.io/safety-level: 'L4' # L0-L5
uav.io/risk-category: 'high' # low/medium/high (L4-L5 必須)
```

## 🎯 安全等級對照表

| 等級 | 說明         | 風險   | 範例           |
| ---- | ------------ | ------ | -------------- |
| L0   | 無自動化     | low    | 完全手動控制   |
| L1   | 輔助系統     | low    | 定速巡航       |
| L2   | 部分自動化   | low    | 車道保持 + ACC |
| L3   | 有條件自動化 | medium | 特定場景自動   |
| L4   | 高度自動化   | high   | 大部分場景自動 |
| L5   | 完全自動化   | high   | 完全無人       |

## 🌍 地理圍欄配置（UAV 必須）

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: uav-geo-config
  labels:
    uav.io/system: 'uav'
data:
  geo.fence.enabled: 'true' # 或 "false"
  geo.fence.regions: 'TW-Taipei, TW-Taichung, JP-Tokyo'
```

**區域格式**: `XX-RegionName`

- XX: 兩位大寫國家/地區代碼
- RegionName: 可含字母、數字、底線、連字符
- 多個區域用逗號+空格分隔

## ⚙️ 資源要求

### UAV 系統

```yaml
resources:
  requests:
    cpu: '500m'
    memory: '256Mi'
  limits:
    cpu: '1'
    memory: '512Mi'
```

### AD 系統

```yaml
resources:
  requests:
    cpu: '1'
    memory: '1Gi'
  limits:
    cpu: '2'
    memory: '2Gi'
```

## 🔒 安全最佳實踐

### 容器映像

```yaml
# ✅ 推薦：使用 SHA256 digest
image: registry.example.com/app@sha256:abc123...

# ❌ 避免：可變標籤
image: registry.example.com/app:latest
```

### 安全上下文

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop:
      - ALL
```

## 🔍 驗證命令

### Conftest

```bash
# 驗證單一檔案
conftest test deployment.yaml -p policies/rego/

# 驗證目錄
conftest test manifests/ -p policies/rego/

# JSON 輸出
conftest test deployment.yaml -p policies/rego/ --output json
```

### Kubectl Dry-run

```bash
# Server-side dry-run
kubectl apply -f deployment.yaml --dry-run=server

# 驗證所有檔案
kubectl apply -f manifests/ --dry-run=server
```

### YAML Lint

```bash
yamllint -c .yamllint manifests/
```

## 📦 SBOM 生成

```bash
# 使用 Syft
syft packages dir:. -o cyclonedx-json > docs/sbom.json

# 使用 CycloneDX npm
cyclonedx-npm --output-file docs/sbom.json
```

## #️⃣ 雜湊計算

```bash
# BLAKE3
b3sum file.yaml

# SHA3-512
openssl dgst -sha3-512 file.yaml
```

## 🚀 快速部署

```bash
# 1. 驗證策略
conftest test manifests/ -p intelligent-hyperautomation/policies/rego/

# 2. Dry-run
kubectl apply -f manifests/ --dry-run=server

# 3. 部署
kubectl apply -f manifests/

# 4. 檢查狀態
kubectl get pods -n your-namespace
kubectl get events -n your-namespace
```

## 🔄 GitOps 部署

### ArgoCD

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: uav-system
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/repo
    targetRevision: v2.0.0
    path: intelligent-hyperautomation/templates/impl/examples
  destination:
    server: https://kubernetes.default.svc
    namespace: uav-production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### Flux

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: intelligent-hyperautomation
spec:
  interval: 1m
  url: https://github.com/your-org/repo
  ref:
    tag: v2.0.0
```

## 🐛 常見錯誤與解決

### 錯誤 1: Missing label uav.io/system

**原因**: 缺少系統類型標籤  
**解決**: 添加 `uav.io/system: "uav"` 或 `"ad"`

### 錯誤 2: Invalid safety-level

**原因**: 安全等級格式錯誤  
**解決**: 使用 `L0`, `L1`, `L2`, `L3`, `L4`, 或 `L5`

### 錯誤 3: Missing geo.fence.enabled

**原因**: UAV ConfigMap 缺少地理圍欄配置  
**解決**: 添加 `geo.fence.enabled: "true"` 或 `"false"`

### 錯誤 4: Invalid geo-fence regions format

**原因**: 區域格式錯誤  
**解決**: 使用格式 `XX-RegionName`，如 `TW-Taipei`

### 錯誤 5: Container must set memory/cpu limits

**原因**: UAV/AD 系統容器缺少資源限制  
**解決**: 設定 `resources.limits.memory` 和 `resources.limits.cpu`

## 📚 文檔索引

| 文檔        | 說明             | 路徑                                      |
| ----------- | ---------------- | ----------------------------------------- |
| 核心理念    | 技術助手能力框架 | docs/core-principles.md                   |
| UAV/AD 治理 | 安全與合規規範   | docs/uav-autonomous-driving-governance.md |
| 使用說明    | 詳細使用指南     | docs/usage-notes.md                       |
| CI/CD 策略  | 自動化流程       | docs/ci-cd-strategy.md                    |
| 範例說明    | 模板使用指南     | templates/impl/examples/README.md         |
| 變更日誌    | 版本歷史         | CHANGELOG.md                              |
| 快速參考    | 本文件           | QUICK_REFERENCE.md                        |

## 🆘 獲取協助

1. 查看文檔：[README.md](README.md)
2. 檢查範例：[templates/impl/examples/](templates/impl/examples/)
3. 提交 Issue：GitHub Issues
4. 聯繫團隊：<platform-team@example.com>

## ⚡ 小技巧

💡 使用 `--output json` 獲取結構化驗證結果  
💡 啟用 GitOps 自動同步以簡化部署  
💡 使用 Kustomize overlays 管理多環境  
💡 定期更新 SBOM 以追蹤依賴變化  
💡 在 CI 中計算雜湊確保檔案完整性

---

**版本**: 2.0.0  
**最後更新**: 2025-11-25  
**維護者**: Platform Team
