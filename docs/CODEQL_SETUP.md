# CodeQL 自動化掃描實現

## 概述

本文檔詳細說明如何在 SynergyMesh 專案中實現企業級 CodeQL 自動化掃描。CodeQL 是 GitHub Advanced Security 的核心組件，提供強大的靜態應用安全測試 (SAST) 功能。

## Advanced Setup 工作流程配置

### 基本 CodeQL 工作流程設定

企業級的 CodeQL 掃描工作流程已配置於 `.github/workflows/codeql-advanced.yml`，支援以下功能：

- **多語言支援**: JavaScript, Python, Java, C#, C++, Go
- **自動化觸發**: Push、Pull Request 和定時掃描
- **自定義建置**: 針對不同語言的專屬建置配置
- **結果上傳**: 自動上傳掃描結果到 Security 標籤

### 工作流程觸發條件

```yaml
on:
  push:
    branches: ["main", "develop", "release/*"]
  pull_request:
    branches: ["main", "develop"]
  schedule:
    - cron: '0 2 * * 1'  # 每週一凌晨 2 點執行
```

### 掃描策略

| 觸發方式 | 執行時機 | 用途 |
|---------|---------|------|
| Push | 推送到主要分支 | 持續監控主要代碼庫 |
| Pull Request | 建立或更新 PR | 在合併前檢測問題 |
| Schedule | 每週一凌晨 2 點 | 定期全面掃描 |

## 自定義 CodeQL 配置

### 企業級掃描配置檔案

配置檔案位於 `.github/codeql/codeql-config.yml`，包含以下設定：

#### 查詢集 (Query Suites)

- **security-extended**: 擴展的安全查詢
- **security-and-quality**: 安全和代碼品質查詢
- **custom-enterprise-queries**: 企業自定義查詢

#### 路徑配置

**包含的路徑**:

- `src/` - 主要源代碼
- `lib/` - 函式庫
- `app/` - 應用程式
- `core/` - 核心模組
- `mcp-servers/` - MCP 伺服器
- `advanced-system-src/` - 進階系統源碼

**排除的路徑**:

- `node_modules/` - Node.js 依賴
- `vendor/` - 第三方供應商代碼
- `**/*.test.js` - 測試文件
- `test/`, `tests/` - 測試目錄
- `**/dist/**`, `**/build/**` - 建置輸出

### 自定義查詢規則

#### 企業敏感資料暴露檢測

位於 `.github/codeql/custom-queries/enterprise-security.ql`，檢測以下敏感資料：

- `password` - 密碼
- `secret` - 密鑰
- `token` - 令牌
- `api_key` - API 金鑰
- `enterprise_id` - 企業識別碼
- `private_key` - 私鑰
- `access_token` - 存取令牌
- `auth` - 認證資訊

**嚴重程度**: Error (8.0)
**準確度**: High

#### 建立自定義查詢的步驟

1. **建立查詢檔案**

```bash
touch .github/codeql/custom-queries/my-query.ql
```

1. **編寫 CodeQL 查詢**

```ql
/**
 * @name My Custom Query
 * @description Description of what this query detects
 * @kind problem
 * @problem.severity warning
 * @security-severity 5.0
 * @precision medium
 * @id enterprise/my-query
 * @tags security
 *       custom
 */

import javascript

// Your query logic here
```

1. **更新 qlpack.yml**
確保您的查詢包含在 `.github/codeql/custom-queries/qlpack.yml` 中。

## Pull Request 整合機制

### PR 品質閘門實現

PR 安全閘門工作流程位於 `.github/workflows/pr-security-gate.yml`，提供以下功能：

#### 自動化安全檢查

1. **執行 CodeQL 分析**
2. **評估安全結果**
3. **根據嚴重程度採取行動**

#### 閘門規則

| 條件 | 動作 | 狀態 |
|------|------|------|
| Critical > 0 | 阻止合併 | ❌ Blocked |
| High > 3 | 要求審查 | ⚠️ Review Required |
| 其他 | 允許合併 | ✅ Passed |

#### PR 評論功能

工作流程會自動在 PR 中添加評論，顯示：

- 各嚴重程度的警報數量
- 當前狀態（通過/需要審查/阻止）
- 下一步行動建議
- Security 標籤連結

### 範例 PR 評論

```markdown
## 🔐 Security Scan Results

| Severity | Count |
|----------|--------|
| Critical | 0 |
| High     | 2 |
| Medium   | 5 |
| Low      | 3 |

✅ Security check passed

---

### Next Steps:
- Review high severity issues and consider fixing
- 📋 Consider addressing medium severity issues

For detailed information, check the Security tab.
```

## 多語言支援配置

### 語言特定建置腳本

建置腳本位於 `scripts/build-matrix.sh`，支援以下語言：

#### Java

- Gradle: `./gradlew clean build -x test --no-daemon`
- Maven: `mvn clean compile -DskipTests`

#### JavaScript/TypeScript

- npm: `npm ci --production=false && npm run build`
- Yarn: `yarn install --frozen-lockfile`
- pnpm: `pnpm install --frozen-lockfile`

#### Python

- requirements.txt: `pip install -r requirements.txt`
- setup.py: `pip install -e .`
- pyproject.toml: `pip install -e .`

#### C #

- `dotnet restore && dotnet build --configuration Release --no-restore`

#### Go

- `go mod download && go mod verify && go build ./...`

#### C/C++

- CMake: `cmake .. -DCMAKE_BUILD_TYPE=Release && make -j$(nproc)`
- Makefile: `make clean && make release`

### 使用建置腳本

```bash
# 基本用法
./scripts/build-matrix.sh <language>

# 範例
./scripts/build-matrix.sh javascript
./scripts/build-matrix.sh python
./scripts/build-matrix.sh java
```

## 最佳實踐

### 1. 定期更新 CodeQL

CodeQL 會定期更新以包含新的安全規則和改進。建議：

- 每月檢查一次 CodeQL 更新
- 測試新版本對現有掃描的影響
- 更新自定義查詢以利用新功能

### 2. 處理誤報

如果遇到誤報（False Positives）：

1. **在 GitHub UI 中處理**
   - 前往 Security > Code scanning alerts
   - 選擇警報
   - 點擊 "Dismiss alert"
   - 選擇原因（如 "False positive"）

2. **在代碼中抑制**

   ```javascript
   // codeql[js/insecure-randomness]
   const randomValue = Math.random();
   ```

### 3. 監控掃描效能

- 檢查工作流程執行時間
- 優化建置步驟
- 考慮分離長時間執行的掃描

### 4. 團隊協作

- 定義警報所有權
- 建立修復 SLA
- 定期審查開放的警報
- 分享最佳實踐

## 疑難排解

### CodeQL 初始化失敗

**問題**: CodeQL 無法初始化特定語言

**解決方案**:

```yaml
- name: Initialize CodeQL
  uses: github/codeql-action/init@v3
  with:
    languages: ${{ matrix.language }}
    # 添加調試選項
    debug: true
```

### 建置步驟失敗

**問題**: 自定義建置步驟失敗

**解決方案**:

1. 檢查建置依賴是否已安裝
2. 確認建置命令是否正確
3. 查看工作流程日誌以獲取詳細錯誤信息
4. 在本地環境中複製建置步驟

### 記憶體不足

**問題**: CodeQL 分析因記憶體不足而失敗

**解決方案**:

```yaml
- name: Perform CodeQL Analysis
  uses: github/codeql-action/analyze@v3
  env:
    # 增加可用記憶體
    CODEQL_RAM: 8192
```

### 掃描時間過長

**問題**: 掃描執行時間超過 timeout

**解決方案**:

```yaml
jobs:
  analyze:
    timeout-minutes: 480  # 增加到 8 小時
```

## 進階配置

### 矩陣構建優化

針對特定語言設定不同的 Runner：

```yaml
strategy:
  matrix:
    include:
      - language: javascript
        os: ubuntu-latest
      - language: swift
        os: macos-latest
      - language: cpp
        os: ubuntu-latest
        compiler: gcc-11
```

### 條件式掃描

只在特定條件下執行掃描：

```yaml
- name: Perform CodeQL Analysis
  if: github.event_name == 'push' || github.event.pull_request.base.ref == 'main'
  uses: github/codeql-action/analyze@v3
```

### 結果過濾

過濾特定類型的結果：

```yaml
- name: Filter Results
  run: |
    # 只顯示 high 和 critical 級別的警報
    gh api /repos/${{ github.repository }}/code-scanning/alerts \
      --jq '.[] | select(.rule.security_severity_level == "high" or .rule.security_severity_level == "critical")'
```

## 整合其他工具

### 與 SIEM 整合

將 CodeQL 結果發送到 SIEM 系統：

```yaml
- name: Send to SIEM
  run: |
    curl -X POST https://siem.example.com/api/events \
      -H "Content-Type: application/json" \
      -d @codeql-results.json
```

### 與 Jira 整合

自動為 critical 警報建立 Jira issue：

```yaml
- name: Create Jira Issue
  if: steps.evaluate.outputs.critical > 0
  run: |
    # 建立 Jira issue 的腳本
```

## 指標和報告

### 關鍵指標

追蹤以下指標以衡量安全狀況：

- **掃描覆蓋率**: 已掃描的代碼庫百分比
- **警報數量**: 按嚴重程度分類
- **平均修復時間**: 從發現到修復的時間
- **誤報率**: 被標記為誤報的警報百分比
- **趨勢分析**: 警報數量隨時間的變化

### 生成報告

定期生成 CodeQL 掃描報告：

```bash
# 獲取最近 30 天的警報統計
gh api /repos/{owner}/{repo}/code-scanning/alerts \
  --jq '[.[] | select(.created_at > (now - 2592000))] | group_by(.rule.security_severity_level) | map({severity: .[0].rule.security_severity_level, count: length})'
```

## 相關資源

- [CodeQL 官方文檔](https://codeql.github.com/docs/)
- [CodeQL 查詢語言參考](https://codeql.github.com/docs/ql-language-reference/)
- [GitHub Code Scanning 文檔](https://docs.github.com/en/code-security/code-scanning)
- [自定義 CodeQL 配置](https://docs.github.com/en/code-security/code-scanning/automatically-scanning-your-code-for-vulnerabilities-and-errors/configuring-code-scanning)

## 支援

如有問題或需要協助，請：

1. 查閱本文檔的疑難排解章節
2. 檢查 GitHub Actions 日誌
3. 聯繫安全團隊
4. 查看 GitHub Community 論壇

---

**最後更新**: 2025-11-22  
**維護者**: SynergyMesh Security Team
