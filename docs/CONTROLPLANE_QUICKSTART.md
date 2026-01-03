# Controlplane 快速入門指南

## 🎯 目標

本指南將幫助您快速開始使用 Controlplane 配置系統，讓它從「華麗的擺設」變成「實用的工具」。

## 📚 什麼是 Controlplane？

Controlplane 是我們的配置治理系統，採用 **Baseline + Overlay + Active** 架構：

- **Baseline**: 不可變的治理真相（配置、規範、註冊表）
- **Overlay**: 可寫的運行時狀態（擴展、證據、日誌）
- **Active**: 合成的統一視圖（Baseline + Overlay）

## 🚀 快速開始

### 1. 使用 CLI 工具

最簡單的方式是使用 `cp-cli` 命令行工具：

```bash
# 查看 controlplane 狀態
./bin/cp-cli status

# 獲取配置值
./bin/cp-cli get metadata.version

# 列出模組
./bin/cp-cli list modules

# 列出命名空間
./bin/cp-cli list namespaces

# 驗證文件名
./bin/cp-cli check-name my-file.yaml --type file

# 運行完整驗證
./bin/cp-cli validate

# 合成 active 視圖
./bin/cp-cli synthesize
```

### 2. 在 Shell 腳本中使用

```bash
#!/usr/bin/env bash

# 載入 controlplane 庫
source lib/controlplane.sh

# 顯示狀態
cp_show_status

# 驗證文件名
if cp_validate_name "my-file.yaml" "file"; then
    echo "✅ Valid file name"
else
    echo "❌ Invalid file name"
    exit 1
fi

# 獲取配置值
version=$(cp_get_baseline_config "root.config.yaml" "metadata.version")
echo "Version: $version"

# 運行驗證
cp_run_validation

# 導出環境變量
cp_export_env
echo "Config path: $CP_BASELINE_CONFIG"
```

### 3. 在 Python 腳本中使用

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, 'lib')

from controlplane import ControlplaneConfig, get_config

# 方式 1: 創建實例
config = ControlplaneConfig()

# 獲取配置
root_config = config.get_baseline_config("root.config.yaml")
print(f"Name: {root_config['metadata']['name']}")

# 驗證名稱
is_valid, error = config.validate_name("my-file.yaml", "file")
if is_valid:
    print("✅ Valid name")
else:
    print(f"❌ Invalid: {error}")

# 獲取模組列表
modules = config.get_modules()
print(f"Modules: {len(modules)}")

# 方式 2: 使用全局實例
from controlplane import get_config, validate_name

config = get_config()
is_valid, error = validate_name("my-file.yaml", "file")
```

## 💡 實際應用案例

### 案例 1: 自動驗證文件命名

在創建新文件之前驗證名稱：

```bash
#!/usr/bin/env bash
source lib/controlplane.sh

new_file="$1"

if cp_validate_name "$new_file" "file"; then
    touch "$new_file"
    echo "✅ Created: $new_file"
else
    echo "❌ Invalid file name: $new_file"
    echo "Please use kebab-case (e.g., my-file.yaml)"
    exit 1
fi
```

### 案例 2: 在 CI/CD 中使用

```yaml
# .github/workflows/my-workflow.yml
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Validate file naming
        run: |
          source lib/controlplane.sh
          
          for file in $(git diff --name-only HEAD~1); do
            filename=$(basename "$file")
            if ! cp_validate_name "$filename" "file"; then
              echo "❌ Invalid: $file"
              exit 1
            fi
          done
```

### 案例 3: 讀取配置進行自動化

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, 'lib')
from controlplane import get_config

config = get_config()

# 獲取治理策略
governance = config.get_governance_policy()
approval_required = governance.get('spec', {}).get('approval_required', False)

if approval_required:
    print("⚠️  This change requires governance approval")
    # 發送通知或創建審批請求
else:
    print("✅ No approval required, proceeding...")
    # 繼續自動化流程
```

### 案例 4: Pre-commit Hook

已經為您準備好了 pre-commit hook：

```bash
# 安裝 git hooks
git config core.hooksPath .githooks

# 現在每次 commit 都會自動驗證文件名
git add my-new-file.yaml
git commit -m "Add new file"
# 🔍 Running pre-commit validation with controlplane...
# ✅ All file names are valid!
```

## 🛠️ 可用工具

### CLI 工具 (`bin/cp-cli`)

| 命令 | 說明 |
|------|------|
| `status` | 顯示 controlplane 狀態 |
| `get <key>` | 獲取配置值（支持點號路徑） |
| `list modules` | 列出所有模組 |
| `list namespaces` | 列出所有命名空間 |
| `validate` | 運行完整驗證 |
| `check-name <name>` | 檢查名稱是否符合規範 |
| `synthesize` | 合成 active 視圖 |

### Shell 庫 (`lib/controlplane.sh`)

| 函數 | 說明 |
|------|------|
| `cp_check_exists` | 檢查 controlplane 是否存在 |
| `cp_show_status` | 顯示狀態 |
| `cp_get_baseline_config` | 獲取 baseline 配置 |
| `cp_get_specification` | 獲取規範 |
| `cp_get_registry` | 獲取註冊表 |
| `cp_validate_name` | 驗證名稱格式 |
| `cp_run_validation` | 運行驗證 |
| `cp_synthesize_active` | 合成 active 視圖 |
| `cp_export_env` | 導出環境變量 |

### Python 庫 (`lib/controlplane.py`)

| 類/函數 | 說明 |
|---------|------|
| `ControlplaneConfig` | 主配置類 |
| `get_config()` | 獲取全局配置實例 |
| `get_modules()` | 快速獲取模組列表 |
| `get_namespaces()` | 快速獲取命名空間列表 |
| `validate_name()` | 快速驗證名稱 |

## 📋 命名規範

Controlplane 強制執行以下命名規範：

### 文件名

- ✅ `my-file.yaml` (kebab-case)
- ✅ `root.config.yaml` (符合 `root.*.yaml` 特例模式)
- ❌ `MyFile.yaml` (不是 kebab-case)
- ❌ `my_file.yaml` (使用下劃線)
- ❌ `my.file.backup.yaml` (不屬於 `root.*.yaml` 允許模式的雙重擴展名，例如備份副檔名)

### 目錄名

- ✅ `my-directory` (kebab-case)
- ✅ `controlplane` (小寫)
- ❌ `MyDirectory` (不是 kebab-case)
- ❌ `my_directory` (使用下劃線)

### 命名空間

- ✅ `machinenativeops` (單一單詞)
- ✅ `my-namespace` (kebab-case)
- ❌ `machinenativeops.core` (包含點號)
- ❌ `MyNamespace` (不是 kebab-case)

### 模組名

- ✅ `core-validator` (kebab-case)
- ✅ `automation-engine` (kebab-case)
- ❌ `CoreValidator` (不是 kebab-case)
- ❌ `core_validator` (使用下劃線)

## 🔄 工作流程整合

### GitHub Actions

我們提供了完整的 GitHub Actions 整合示例：

```yaml
# 使用 controlplane 驗證
- name: Validate with controlplane
  run: |
    source lib/controlplane.sh
    cp_run_validation
```

查看完整示例：`.github/workflows/controlplane-integration.yml`

### Pre-commit Hooks

```bash
# 安裝 hooks
git config core.hooksPath .githooks

# 測試 hook
git add test-file.yaml
git commit -m "Test"
```

### 本地開發

```bash
# 在開發前驗證
./bin/cp-cli validate

# 檢查新文件名
./bin/cp-cli check-name my-new-file.yaml

# 查看配置
./bin/cp-cli get metadata
```

## 📊 驗證報告

運行驗證後，報告會生成在：

```
controlplane/overlay/evidence/validation/
├── validation.report.json    # 機器可讀格式
├── validation.report.md      # 人類可讀格式
└── controlplane.manifest.json # 驗證清單
```

查看報告：

```bash
# Markdown 格式
cat controlplane/overlay/evidence/validation/validation.report.md

# JSON 格式
cat controlplane/overlay/evidence/validation/validation.report.json | jq .

# 檢查是否通過
cat controlplane/overlay/evidence/validation/validation.report.json | jq .pass
```

## 🎓 進階使用

### 創建 Overlay 擴展

```python
from controlplane import get_config

config = get_config()

# 創建 overlay 擴展
extension_file = config.create_overlay_extension(
    name="my-extension",
    extends="baseline/config/root.config.yaml",
    config={
        "custom_setting": "value",
        "feature_flags": {
            "new_feature": True
        }
    }
)

print(f"Created: {extension_file}")
```

### 合成 Active 視圖

```bash
# 使用 CLI
./bin/cp-cli synthesize

# 使用 Shell 庫
source lib/controlplane.sh
cp_synthesize_active

# 查看結果
ls -la controlplane/active/
```

### 自定義驗證規則

編輯 `controlplane/baseline/validation/validate-root-specs.py` 添加自定義驗證邏輯。

## 🐛 故障排除

### 問題：找不到 controlplane

```bash
# 檢查路徑
./bin/cp-cli status

# 確認目錄存在
ls -la controlplane/baseline/
```

### 問題：驗證失敗

```bash
# 查看詳細報告
cat controlplane/overlay/evidence/validation/validation.report.md

# 運行詳細驗證
./bin/cp-cli validate --verbose
```

### 問題：文件名驗證失敗

```bash
# 檢查具體錯誤
./bin/cp-cli check-name "MyFile.yaml" --type file

# 正確的格式
./bin/cp-cli check-name "my-file.yaml" --type file
```

## 📚 更多資源

- **完整文檔**: `controlplane/CONTROLPLANE_USAGE.md`
- **架構文檔**: `controlplane/baseline/documentation/BASELINE_ARCHITECTURE.md`
- **驗證系統**: `controlplane/baseline/validation/`
- **GitHub Actions 示例**: `.github/workflows/controlplane-integration.yml`

## 💬 常見問題

### Q: 為什麼需要 controlplane？

A: Controlplane 提供統一的配置治理，確保整個儲存庫的一致性、可追溯性和自動化能力。

### Q: 我可以修改 baseline 配置嗎？

A: Baseline 是不可變的，需要通過 PR 和治理流程修改。運行時修改應該寫入 overlay。

### Q: 如何添加新的配置？

A: 創建 overlay 擴展而不是修改 baseline：

```python
from controlplane import get_config
config = get_config()
config.create_overlay_extension("my-config", "baseline/config/root.config.yaml", {...})
```

### Q: 驗證失敗怎麼辦？

A: 查看驗證報告，修復問題後重新運行驗證。不要使用 `--no-verify` 繞過驗證。

## 🎉 開始使用

現在您已經了解了 controlplane 的基本用法，開始在您的工作流程中使用它吧！

```bash
# 第一步：查看狀態
./bin/cp-cli status

# 第二步：運行驗證
./bin/cp-cli validate

# 第三步：在腳本中使用
source lib/controlplane.sh
cp_validate_name "my-new-file.yaml" "file"

# 第四步：整合到 CI/CD
# 查看 .github/workflows/controlplane-integration.yml
```

---

**版本**: 1.0.0  
**最後更新**: 2025-12-25  
**維護者**: MachineNativeOps Team
