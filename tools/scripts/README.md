# Scripts Directory

本目錄包含 SynergyMesh 專案的自動化腳本，主要用於 GitHub Advanced Security
(GHAS) 功能的實施和管理。

## 📋 腳本清單

### 1. generate-directory-tree.sh

**用途**: 產生完整專案目錄結構圖譜

**功能**:

- 自動掃描整個專案目錄結構
- 產生樹狀結構圖譜（使用 tree 或 find 命令）
- 統計專案檔案和目錄數量
- 分析檔案類型分布
- 標註特殊目錄（.git、.github、node_modules 等）
- 提供各目錄用途說明

**使用方法**:

```bash
# 基本用法（輸出到終端）
./scripts/generate-directory-tree.sh

# 輸出到檔案
./scripts/generate-directory-tree.sh > DIRECTORY_STRUCTURE.md

```

**輸出內容**:

- 完整目錄樹結構（排除 node_modules、.git、dist 等）
- 特殊目錄清單與說明
- 專案統計資訊（檔案數、目錄數）
- 檔案類型分布表
- 最大的目錄清單
- 主要目錄用途說明

**特性**:

- 雙語輸出（繁體中文 / English）
- Markdown 格式，便於閱讀和分享
- 自動排除建置產物和依賴目錄
- 支援 tree 命令（若可用）或使用 find 作為備選
- 提供詳細的統計分析

**範例輸出**:

```markdown
# SynergyMesh 專案目錄結構圖譜

## 📂 完整目錄結構 / Complete Directory Structure

...

## 📋 特殊目錄說明 / Special Directories

- `.git/`: Git 版本控制目錄
- `.github/`: GitHub 設定與工作流程 ...

## 📊 專案統計 / Project Statistics

- 總檔案數: 828
- 總目錄數: 222 ...
```

---

### 2. build-matrix.sh

**用途**: 多語言建置腳本，支援 CodeQL 分析

**支援語言**:

- JavaScript/TypeScript
- Python
- Java (Gradle/Maven)
- C# (.NET)
- Go
- C/C++ (CMake/Makefile)
- Ruby
- Swift

**使用方法**:

```bash
# 基本用法
./build-matrix.sh <language> [build_mode]

# 範例
./build-matrix.sh javascript
./build-matrix.sh python
./build-matrix.sh java standard
```

**建置模式**:

- `standard` (預設): 標準建置
- 可擴展自定義模式

**特性**:

- 自動檢測建置工具
- 支援多種包管理器
- 錯誤處理和日誌記錄
- 並行建置支援（如 C/C++）

---

### 2. advanced-push-protection.sh

**用途**: 高級推送保護腳本，檢測和阻止秘密洩露

**檢測模式**:

- `staged`: 檢查暫存的變更
- `commits`: 檢查最近的 commits
- `full`: 完整倉庫掃描
- `strict`: 嚴格模式（預設，檢查暫存和 commits）

**使用方法**:

```bash
# 安裝 pre-push hook
./advanced-push-protection.sh install

# 執行掃描
./advanced-push-protection.sh scan

# 指定檢查模式
./advanced-push-protection.sh "" "" staged
./advanced-push-protection.sh "" "" commits
./advanced-push-protection.sh "" "" full
```

**檢測的秘密類型**:

- GitHub Tokens (PAT, OAuth)
- OpenAI API Keys
- AWS Access Keys
- Azure Secrets
- Database Passwords
- Private Keys (RSA, SSH)
- JWT Tokens
- Connection Strings
- Third-party Service Keys

**特性**:

- 即時秘密檢測
- 上下文顯示（已編輯）
- Git hook 整合
- 可配置的模式
- 詳細的錯誤報告

---

### 3. manage-secret-patterns.py

**用途**: GitHub Secret Scanning 自定義模式管理工具

**功能**:

- 列出組織的自定義模式
- 建立新的秘密掃描模式
- 更新現有模式
- 刪除模式
- 部署企業級模式集
- 導出/導入模式

**環境要求**:

- Python 3.7+
- requests 庫

**安裝依賴**:

```bash
pip install requests
```

**使用方法**:

#### 基本操作

```bash
# 設定環境變數
export GITHUB_TOKEN="your_github_token"

# 列出所有模式
./manage-secret-patterns.py list --org your-org

# 建立新模式
./manage-secret-patterns.py create \
  --org your-org \
  --name "Custom API Key" \
  --regex "custom_[0-9a-f]{32}" \
  --secret-type "custom_api_key"

# 更新模式
./manage-secret-patterns.py update \
  --org your-org \
  --pattern-id 123 \
  --name "Updated Name"

# 刪除模式
./manage-secret-patterns.py delete \
  --org your-org \
  --pattern-id 123
```

#### 批量操作

```bash
# 部署企業級模式集
./manage-secret-patterns.py deploy --org your-org

# 導出模式到 JSON
./manage-secret-patterns.py export \
  --org your-org \
  --file patterns-backup.json

# 從 JSON 導入模式
./manage-secret-patterns.py import \
  --org your-org \
  --file patterns-backup.json
```

#### 命令行參數

| 參數            | 說明                                                      | 必需 |
| --------------- | --------------------------------------------------------- | ---- |
| `action`        | 操作類型 (list/create/update/delete/deploy/export/import) | 是   |
| `--org`         | GitHub 組織名稱                                           | 是   |
| `--token`       | GitHub Token (或使用 GITHUB_TOKEN 環境變數)               | 否\* |
| `--pattern-id`  | 模式 ID (用於 update/delete)                              | 條件 |
| `--name`        | 模式名稱                                                  | 條件 |
| `--regex`       | 正則表達式模式                                            | 條件 |
| `--secret-type` | 秘密類型標識                                              | 條件 |
| `--file`        | 文件路徑 (用於 export/import)                             | 條件 |

\*如果未提供 `--token`，將使用 `GITHUB_TOKEN` 環境變數

**企業級模式範例**:

腳本內建以下企業級模式：

- Enterprise Database Password
- Internal Service Token
- Enterprise API Key
- Master Encryption Key
- JWT Signing Secret

**錯誤處理**:

- 連接失敗時提供詳細錯誤信息
- API 錯誤時顯示響應內容
- 失敗時返回適當的退出碼

---

## 🔧 安裝與配置

### 權限設定

所有腳本需要執行權限：

```bash
chmod +x generate-directory-tree.sh
chmod +x build-matrix.sh
chmod +x advanced-push-protection.sh
chmod +x manage-secret-patterns.py
```

### 環境變數

建議設定以下環境變數：

```bash
# GitHub 認證
export GITHUB_TOKEN="your_personal_access_token"

# 組織資訊
export GITHUB_ORG="your-organization"

# Elasticsearch (如使用)
export ELASTICSEARCH_ENDPOINT="http://elasticsearch:9200"
export ELASTICSEARCH_PASSWORD="your_password"

# 其他配置
export LOG_LEVEL="info"
```

### Git Hooks

要啟用 pre-push 保護：

```bash
# 執行安裝命令
./advanced-push-protection.sh install

# 驗證安裝
cat .git/hooks/pre-push
```

---

## 📖 使用場景

### 場景 1: 專案文檔

```bash
# 產生最新的目錄結構文檔
./scripts/generate-directory-tree.sh > DIRECTORY_STRUCTURE.md

# 將結果提交到 repository
git add DIRECTORY_STRUCTURE.md
git commit -m "docs: update directory structure"
git push
```

### 場景 2: CI/CD 整合

```yaml
# 在 GitHub Actions 中使用
- name: Generate Directory Structure
  run: ./scripts/generate-directory-tree.sh > DIRECTORY_STRUCTURE.md

- name: Build Project
  run: ./scripts/build-matrix.sh javascript

- name: Scan for Secrets
  run: ./scripts/advanced-push-protection.sh scan
```

### 場景 3: 本地開發

```bash
# 檢視專案結構
./scripts/generate-directory-tree.sh | less

# 開發前設定
./scripts/advanced-push-protection.sh install

# 推送前會自動檢查
git push origin main
```

### 場景 4: 批量管理

```bash
# 導出現有模式
./scripts/manage-secret-patterns.py export \
  --org prod-org \
  --file prod-patterns.json

# 導入到測試環境
./scripts/manage-secret-patterns.py import \
  --org test-org \
  --file prod-patterns.json
```

---

## 🔍 疑難排解

### build-matrix.sh

**問題**: 找不到建置工具

**解決**:

```bash
# 確認工具已安裝
which gradle
which npm
which dotnet

# 安裝缺失的工具
```

**問題**: 權限拒絕

**解決**:

```bash
# 對於 gradlew
chmod +x ./gradlew

# 對於腳本本身
chmod +x scripts/build-matrix.sh
```

### advanced-push-protection.sh

**問題**: Hook 未觸發

**解決**:

```bash
# 檢查 hook 是否存在
ls -la .git/hooks/pre-push

# 檢查執行權限
chmod +x .git/hooks/pre-push

# 重新安裝
./scripts/advanced-push-protection.sh install
```

**問題**: 誤報太多

**解決**:

- 調整 SECRET_PATTERNS 陣列
- 添加排除規則
- 使用更精確的正則表達式

### manage-secret-patterns.py

**問題**: 認證失敗

**解決**:

```bash
# 檢查 token 權限
gh auth status

# 重新設定 token
export GITHUB_TOKEN="new_token"

# 驗證權限
./scripts/manage-secret-patterns.py list --org your-org
```

**問題**: API 速率限制

**解決**:

- 使用認證的請求（更高的速率限制）
- 添加延遲在批量操作之間
- 使用企業級 GitHub 帳號

---

## 🚀 最佳實踐

### 1. 定期更新

```bash
# 定期檢查和更新腳本
git pull origin main

# 更新自定義模式
./scripts/manage-secret-patterns.py deploy --org your-org
```

### 2. 測試環境驗證

```bash
# 在測試環境先驗證
./scripts/build-matrix.sh javascript
# 檢查結果...

# 確認無誤後再部署到生產
```

### 3. 監控和日誌

```bash
# 保存執行日誌
./scripts/advanced-push-protection.sh scan 2>&1 | tee scan.log

# 定期審查日誌
grep "detected" scan.log
```

### 4. 團隊協作

- 將腳本和配置提交到版本控制
- 文檔化自定義修改
- 共享最佳實踐
- 定期團隊培訓

---

## 📚 相關資源

### 文檔

- [GHAS 完整指南](../docs/GHAS_COMPLETE_GUIDE.md)
- [CodeQL 設定](../docs/CODEQL_SETUP.md)
- [Secret Scanning 指南](../docs/SECRET_SCANNING.md)

### 外部資源

- [GitHub CLI 文檔](https://cli.github.com/manual/)
- [CodeQL 查詢語言](https://codeql.github.com/docs/ql-language-reference/)
- [Secret Scanning API](https://docs.github.com/en/rest/secret-scanning)

---

## 🤝 貢獻

歡迎改進這些腳本！請：

1. Fork 專案
2. 建立功能分支
3. 提交變更
4. 開啟 Pull Request

### 編碼規範

- Bash: 遵循
  [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
- Python: 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- 添加適當的錯誤處理
- 包含使用範例和註釋

---

**維護者**: SynergyMesh Security Team  
**最後更新**: 2025-11-22

# Scripts Directory

This directory contains utility scripts for SynergyMesh.

## Structure

```
scripts/
├── migration/    # Migration tools
├── generation/   # Code generation tools
└── utilities/    # General utility scripts
```

## Migration Scripts

Scripts for migrating to the new directory topology.

## Generation Scripts

Tools for generating:

- Boilerplate code
- Configuration files
- Documentation

## See Also

- [Migration Guide](../docs/MIGRATION.md)
- [Build Compatibility](../docs/BUILD_COMPAT.md)
