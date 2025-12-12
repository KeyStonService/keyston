# UAV/AD 範例模板

本目錄包含符合 UAV/AD 治理規範的 Kubernetes 資源範例。

## 範例清單

### namespace.yaml

定義 UAV 和 AD 系統的命名空間，包含所有必要標籤：

- `namespace.io/*` 標準標籤
- `uav.io/system` UAV/AD 系統標識

### uav-deployment.yaml

UAV 控制器部署範例，展示：

- ✅ 完整的標籤集（標準 + UAV 特定）
- ✅ 安全等級標註（L4 - 高風險）
- ✅ 使用 SHA256 digest 的容器映像
- ✅ 資源限制配置
- ✅ 安全上下文設定
- ✅ 健康檢查配置
- ✅ 環境變數從 ConfigMap 讀取

### uav-configmap.yaml

UAV 地理圍欄配置範例：

- ✅ `geo.fence.enabled` 設定
- ✅ `geo.fence.regions` 區域定義
- ✅ 安全參數（高度、速度、電量）
- ✅ 緊急設定
- ✅ 通訊設定

### ad-deployment.yaml

自動駕駛控制器部署範例：

- ✅ AD 系統標籤
- ✅ 安全等級 L3（中等風險）
- ✅ 較高的資源配置（1-2 CPU, 1-2Gi 記憶體）
- ✅ CAN-bus 通訊端口
- ✅ 感測器資料掛載

## 使用方法

### 驗證範例

使用 Conftest 驗證範例是否符合策略：

```bash
# 驗證所有範例
conftest test examples/*.yaml \
  -p ../../policies/rego/

# 驗證特定檔案
conftest test examples/uav-deployment.yaml \
  -p ../../policies/rego/uav_ad.rego
```

### 部署範例

```bash
# 創建命名空間
kubectl apply -f examples/namespace.yaml

# 部署 UAV 系統
kubectl apply -f examples/uav-configmap.yaml
kubectl apply -f examples/uav-deployment.yaml

# 部署 AD 系統
kubectl apply -f examples/ad-deployment.yaml
```

### Dry-run 測試

在實際部署前進行 dry-run：

```bash
kubectl apply -f examples/ --dry-run=server
```

## 標籤說明

### 必要標籤

所有資源必須包含以下標籤：

#### 標準命名空間標籤

- `namespace.io/managed-by`: 管理者（如 "platform-team"）
- `namespace.io/domain`: 業務領域（"uav" 或 "ad"）
- `namespace.io/team`: 負責團隊
- `namespace.io/environment`: 環境（dev/staging/production）
- `namespace.io/lifecycle`: 生命週期（experimental/stable/deprecated）

#### UAV/AD 特定標籤（用於 Deployment）

- `uav.io/system`: 系統類型（"uav" 或 "ad"）
- `uav.io/safety-level`: 安全等級（L0-L5）
- `uav.io/risk-category`: 風險類別（low/medium/high）

## 安全等級說明

### UAV/AD 自動化等級

- **L0**: 無自動化，完全手動控制
- **L1**: 輔助駕駛/飛行，人類主導
- **L2**: 部分自動化，需人類監督
- **L3**: 有條件自動化，特定場景自動
- **L4**: 高度自動化，大部分場景自動
- **L5**: 完全自動化，無需人類介入

### 風險等級對應

- **L0-L2**: low（低風險）
- **L3**: medium（中風險）
- **L4-L5**: high（高風險）

## 地理圍欄配置

UAV 系統必須配置地理圍欄：

```yaml
data:
  geo.fence.enabled: 'true' # 或 "false"
  geo.fence.regions: 'TW-Taipei, TW-Taichung, JP-Tokyo'
```

### 區域格式

- 格式：`XX-RegionName`
- XX: 兩個大寫字母的國家/地區代碼
- RegionName: 區域名稱（可包含字母、數字、底線、連字符）
- 多個區域用逗號分隔

## 資源要求

### UAV 系統建議配置

```yaml
resources:
  requests:
    cpu: '500m'
    memory: '256Mi'
  limits:
    cpu: '1'
    memory: '512Mi'
```

### AD 系統建議配置

```yaml
resources:
  requests:
    cpu: '1'
    memory: '1Gi'
  limits:
    cpu: '2'
    memory: '2Gi'
```

## 安全最佳實踐

### 容器映像

✅ 使用 SHA256 digest 而非 tag

```yaml
image: registry.example.com/app@sha256:abc123...
```

❌ 避免使用可變標籤

```yaml
image: registry.example.com/app:latest # 不建議
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

### 健康檢查

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

## 故障排除

### 策略驗證失敗

**問題**: 缺少必要標籤

```
FAIL - Missing label uav.io/system
```

**解決**: 添加缺失的標籤到 metadata.labels

**問題**: 地理圍欄格式錯誤

```
FAIL - Invalid geo-fence regions format
```

**解決**: 確保格式為 `XX-RegionName`，如 `TW-Taipei`

### 部署失敗

**問題**: 資源不足

```
FailedScheduling: Insufficient cpu/memory
```

**解決**: 調整 requests/limits 或增加節點資源

**問題**: 映像拉取失敗

```
ImagePullBackOff
```

**解決**: 確認映像存在且有權限存取

## 進階配置

### 多環境部署

使用 Kustomize 管理多環境：

```bash
intelligent-hyperautomation/templates/impl/
├── base/                 # 基礎配置
├── overlays/
│   ├── dev/             # 開發環境
│   ├── staging/         # 預生產環境
│   └── production/      # 生產環境（當前範例）
```

### GitOps 整合

與 ArgoCD/Flux 整合：

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: uav-system
spec:
  source:
    path: intelligent-hyperautomation/templates/impl/examples
  destination:
    namespace: uav-production
```

## 參考資料

- [核心理念與定位](../../docs/core-principles.md)
- [UAV/AD 治理規範](../../docs/uav-autonomous-driving-governance.md)
- [使用說明](../../docs/usage-notes.md)
- [CI/CD 策略](../../docs/ci-cd-strategy.md)

---

**版本**: 2.0.0  
**最後更新**: 2025-11-25
