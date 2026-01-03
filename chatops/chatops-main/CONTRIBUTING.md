# Contributing to Machine Native Ops

感謝您對 Machine Native Ops 專案的貢獻！本文檔說明如何參與專案開發。

## 開發流程

### 1. 分支策略

我們採用 GitHub Flow 模型：

```
main (生產分支)
├── feature/your-feature-name
├── bugfix/issue-description
└── hotfix/critical-fix
```

- **main**：永遠保持可部署狀態
- **feature/***：新功能開發
- **bugfix/***：錯誤修復
- **hotfix/***：緊急修復（直接合併到 main）

### 2. 開始開發

```bash
# 1. Fork 並克隆倉庫
git clone https://github.com/YOUR_USERNAME/machine-native-ops.git
cd machine-native-ops

# 2. 新增遠端 upstream
git remote add upstream https://github.com/MachineNativeOps/machine-native-ops.git

# 3. 建立功能分支
git checkout -b feature/your-feature-name

# 4. 安裝開發工具
make setup-tools  # 或手動安裝

# 5. 開發與測試
# 編寫程式碼...
make all          # 執行完整驗證

# 6. 提交變更
git add .
git commit -m "feat: add new governance module"

# 7. 推送到您的 fork
git push origin feature/your-feature-name

# 8. 建立 Pull Request
```

### 3. 提交規範

我們使用 [Conventional Commits](https://www.conventionalcommits.org/) 規範：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### Type 類型：
- `feat`: 新功能
- `fix`: 錯誤修復
- `docs`: 文件更新
- `style`: 程式碼格式（不影響功能）
- `refactor`: 重構
- `test`: 測試相關
- `chore`: 建置過程或輔助工具變動

#### 範例：
```
feat(governance): add role-based access control

Implement RBAC for the governance module with the following changes:
- Add admin/operator/viewer roles
- Implement permission checking
- Update documentation

Closes #123
```

## 程式碼規範

### 1. YAML 規範

```yaml
# 使用 2 個空格縮排
apiVersion: root.platform.io/v1
kind: RootConfig
metadata:
  name: example-config
  version: "1.0.0"
  owners:
    - platform-team@example.com
  description: "Example configuration"
spec:
  # 具體配置...
```

### 2. Python 規範

- 遵循 PEP 8
- 使用 4 個空格縮排
- 行長限制 88 字元（Black 預設）
- 函數和類別需要 docstring

```python
def validate_root_config(config_path: str) -> bool:
    """Validate root configuration file.
    
    Args:
        config_path: Path to the root config YAML file.
        
    Returns:
        True if valid, False otherwise.
        
    Raises:
        FileNotFoundError: If config file doesn't exist.
        ValidationError: If config is invalid.
    """
    # 實作...
```

### 3. Shell 腳本規範

```bash
#!/bin/bash
# 使用嚴格模式
set -euo pipefail

# 函數命名使用駝峰式
validateSchema() {
    local file="$1"
    
    if [[ ! -f "$file" ]]; then
        echo "ERROR: File not found: $file" >&2
        return 1
    fi
    
    # 驗證邏輯...
}
```

## 測試要求

### 1. 本地測試

提交前必須通過所有測試：

```bash
# 完整測試流程
make all

# 個別測試
make fmt-check    # 格式檢查
make lint         # 代碼檢查  
make schema       # Schema 驗證
make test-vectors # 測試向量
make render       # 產生 manifests
make policy       # 政策檢查
make evidence     # 證據鏈
```

### 2. 測試向量

新增或修改 `.root.*.yaml` 時，必須更新測試向量：

```bash
# 新增測試案例
cp root/.root.config.yaml root/tests/vectors/valid/valid-config.yaml

# 新增失敗案例（故意破壞）
cp root/.root.config.yaml root/tests/vectors/invalid/missing-version.yaml
# 然後移除 version 欄位

# 重新測試
make test-vectors
```

### 3. Schema 驗證

所有 YAML 檔案必須通過對應的 JSON Schema 驗證：

```bash
# 驗證所有 root 檔案
python root/scripts/schema_validate.py

# 驗證特定檔案
python root/scripts/schema_validate.py root/.root.config.yaml
```

## 安全要求

### 1. 禁止提交密鑰

❌ **絕對禁止**：
- API keys、tokens、passwords
- 憑證檔案（*.key, *.pem, *.crt）
- 私密資料

✅ **正確做法**：
- 使用環境變數
- 提供 `.env.example` 範本
- 使用 secrets management 工具

### 2. 安全掃描

```bash
# 秘密掃描
make secret-scan

# 依賴掃描（如果有）
make vulnerability-scan
```

## Pull Request 流程

### 1. PR 檢查清單

建立 PR 前確認：

- [ ] 程式碼通過所有測試（`make all`）
- [ ] 更新相關文件
- [ ] 新增測試案例（如需要）
- [ ] 遵循提交規範
- [ ] 沒有提交敏感資料
- [ ] 檔案大小符合規範（< 256KB）

### 2. PR 模板

使用提供的 PR 模板，包含：

- 變更描述
- 測試結果
- 影響評估
- 相關 Issue

### 3. 審查流程

1. **自動檢查**：CI/CD 會自動執行所有驗證
2. **程式碼審查**：至少需要一位維護者審查
3. **安全審查**：涉及安全變更需要額外審查

## 特殊檔案處理

### 1. root/ 目錄變更

任何 `root/` 目錄下的變更都需要特別注意：

- 必須更新對應的 JSON Schema
- 必須更新測試向量
- 必須檢查對下游系統的影響

### 2. Policy 變更

修改 `deploy/policies/` 時：

- 測試政策影響範圍
- 確保不會破壞現有部署
- 更新政策文件

### 3. CI/CD 變更

修改工作流程時：

- 測試在本地可執行
- 確保不會影響其他 PR
- 文件化變更原因

## 發布流程

### 1. 版本管理

我們使用語意化版本（Semantic Versioning）：

```
MAJOR.MINOR.PATCH
```

- **MAJOR**：不相容的 API 變更
- **MINOR**：向後相容的功能新增
- **PATCH**：向後相容的錯誤修復

### 2. 發布步驟

```bash
# 1. 更新版本號
echo "0.2.0" > VERSION

# 2. 更新 CHANGELOG.md
git add CHANGELOG.md VERSION
git commit -m "chore: bump version to 0.2.0"

# 3. 建立標籤
git tag -a v0.2.0 -m "Release version 0.2.0"

# 4. 推送
git push upstream main --tags
```

## 社群指南

### 1. 溝通管道

- **GitHub Issues**：錯誤報告和功能請求
- **GitHub Discussions**：一般討論
- **Email**：security@machine-native-ops.org（安全問題）

### 2. 行為準則

我們致力於友善、歡迎的社群環境：

- 尊重不同觀點和經驗
- 接受建設性批評
- 專注於對社群最有利的事情
- 對其他社群成員表示同理心

## 問題回報

### 1. 錯誤報告

使用 GitHub Issues 回告錯誤，包含：

- 清晰的標題
- 重現步驟
- 預期行為 vs 實際行為
- 環境資訊
- 相關日誌

### 2. 功能請求

提出新功能時：

- 描述使用案例
- 說明解決的問題
- 提供實作建議（如有）
- 考慮對現有系統的影響

## 協助資源

### 1. 文件

- [專案 README](README.md)
- [安全政策](SECURITY.md)
- [架構文件](docs/)

### 2. 工具

- [Makefile 目標](./Makefile#L1)
- [Schema 定義](root/schemas/)
- [測試向量](root/tests/vectors/)

---

再次感謝您的貢獻！有任何問題請隨時提問。