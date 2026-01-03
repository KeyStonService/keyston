# 🔍 高階代碼掃描系統

## 概述

高階代碼掃描系統提供全面的安全檢測、根因分析和自動修復功能，幫助您：

- 🔍 **深度掃描** - 多層次安全、依賴、質量、性能和合規性檢測
- 🎯 **根因分析** - 智能識別漏洞根本原因和影響鏈
- 🔧 **自動修復** - 一鍵修復可自動修復的問題
- 📊 **可視化報告** - Web 儀表板和詳細報告

## 功能特性

### 1. 高階深度掃描 (Advanced Deep Scanner)

**掃描類型：**
- 🛡️ **安全掃描** - 檢測 SQL 注入、XSS、硬編碼密碼等安全漏洞
- 📦 **依賴掃描** - 檢查未固定版本、已知漏洞依賴
- ⭐ **代碼質量** - 檢測長函數、大文件、代碼風格問題
- ⚡ **性能掃描** - 識別潛在性能瓶頸
- ✅ **合規性** - 檢查文檔、許可證等合規要求

**支持的掃描工具：**
- Bandit (Python 安全)
- Semgrep (多語言安全規則)
- 自定義安全規則

### 2. 根因分析引擎 (Root Cause Analyzer)

**分析能力：**
- 漏洞分類（注入、認證、加密、配置等）
- 影響鏈追蹤
- 受影響組件識別
- 風險評分計算
- 修復建議生成

**根因類型：**
- 邏輯錯誤
- 缺少驗證
- 不安全操作
- 資源洩漏
- 競態條件
- 注入攻擊
- 加密問題
- 認證問題
- 配置問題

### 3. 一鍵自動修復 (Auto Fixer)

**可修復的問題類型：**
- ✅ 硬編碼密碼 → 環境變量
- ✅ 未固定版本依賴 → 固定版本
- ✅ 過長代碼行 → 自動拆分
- ⚠️ SQL 注入 → 生成修復建議（需審查）
- ⚠️ XSS 攻擊 → 生成修復建議（需審查）

**修復流程：**
1. 自動修復高置信度問題
2. 標記需要人工審查的問題
3. 生成修復補丁
4. 創建修復報告

### 4. Web 儀表板 (Dashboard)

**功能：**
- 實時掃描結果查看
- 根因分析可視化
- 修復狀態追蹤
- 詳細發現列表
- 報告下載

## 使用方法

### 本地使用

#### 1. 安裝依賴

```bash
pip install bandit flask
```

#### 2. 執行掃描

```bash
# 執行完整掃描
python .github/code-scanning/tools/advanced_scanner.py

# 執行根因分析
python .github/code-scanning/tools/root_cause_analyzer.py scan-results.json

# 執行自動修復
python .github/code-scanning/tools/auto_fixer.py scan-results.json

# 啟動儀表板
python .github/code-scanning/tools/dashboard.py
```

#### 3. 查看結果

掃描結果保存在 `.github/code-scanning/reports/` 目錄：
- `scan-results-YYYYMMDD-HHMMSS.json` - 掃描結果
- `root-cause-analysis.json` - 根因分析
- `fix-report-YYYYMMDD-HHMMSS.json` - 修復報告

訪問 `http://localhost:5000` 查看 Web 儀表板。

**安全配置：**
- 預設情況下，儀表板僅監聽 `127.0.0.1`（本機訪問），確保安全性
- 支援通過環境變數配置：
  - `DASHBOARD_HOST`: 監聽地址（預設：127.0.0.1）
  - `DASHBOARD_PORT`: 監聽端口（預設：5000）
  - `DASHBOARD_DEBUG`: Flask 除錯模式（預設：false）
  
**開發環境允許外部訪問：**
```bash
# 僅限受信任的開發環境使用
DASHBOARD_HOST=0.0.0.0 python .github/code-scanning/tools/dashboard.py
```

⚠️ **安全警告：** 切勿在生產或共享環境中將儀表板綁定到 `0.0.0.0` 或啟用除錯模式

### GitHub Actions 集成

工作流自動在以下情況觸發：
- 推送到 `main` 或 `develop` 分支
- 創建 Pull Request
- 每天凌晨 2:00 UTC (定時掃描)
- 手動觸發 (workflow_dispatch)

#### 手動觸發掃描

1. 前往 GitHub Actions 頁面
2. 選擇 "Advanced Code Scanning" 工作流
3. 點擊 "Run workflow"
4. 選擇是否執行自動修復

#### 查看掃描結果

掃描結果會顯示在：
- GitHub Actions 工作流日誌
- Pull Request 摘要
- Actions Artifacts (下載詳細報告)

## 工作流配置

### 工作流文件

`.github/workflows/advanced-code-scanning.yml`

### 可配置參數

```yaml
env:
  PYTHON_VERSION: '3.11'  # Python 版本
```

### 工作流輸入

- `run_auto_fix`: 是否執行自動修復 (true/false)

## 輸出格式

### 掃描結果 JSON

```json
{
  "metadata": {
    "scan_time": "2024-01-01T00:00:00Z",
    "repo_path": "/path/to/repo",
    "scanner_version": "1.0.0"
  },
  "security": [...],
  "dependencies": [...],
  "code_quality": [...],
  "performance": [...],
  "compliance": [...],
  "summary": {
    "total_findings": 10,
    "critical": 1,
    "high": 2,
    "medium": 3,
    "low": 4
  }
}
```

### 根因分析 JSON

```json
{
  "metadata": {
    "analysis_time": "2024-01-01T00:00:00Z"
  },
  "root_causes": [...],
  "impact_chain": {...},
  "affected_components": [...],
  "risk_assessment": {
    "total_risk_score": 25.5,
    "risk_level": "high"
  },
  "recommendations": {...}
}
```

## 自定義規則

### 添加自定義安全規則

編輯 `advanced_scanner.py` 中的 `_custom_security_rules()` 方法：

```python
def _custom_security_rules(self) -> List[Dict]:
    findings = []
    
    # 添加您的自定義規則
    patterns = {
        "my_pattern": ["pattern1", "pattern2"]
    }
    
    return findings
```

### 添加自定義修復器

創建新的修復器類：

```python
class MyCustomFixer(VulnerabilityFixer):
    def can_fix(self, vulnerability: Dict) -> bool:
        # 判斷是否可以修復
        return True
    
    def fix(self, file_path: str, vulnerability: Dict) -> Tuple[bool, str, str]:
        # 修復邏輯
        return True, original, fixed
    
    def get_description(self) -> str:
        return "我的自定義修復器"
```

然後在 `AutoFixer` 中註冊：

```python
self.fixers = [
    # ... 現有修復器
    MyCustomFixer(),
]
```

## 最佳實踐

### 1. 定期掃描

- 每次提交代碼時自動執行掃描
- 每周執行完整深度掃描
- 發布前進行全面檢查

### 2. 修復優先級

**立即修復 (Critical/High)：**
- SQL 注入、XSS 等安全漏洞
- 硬編碼密碼和憑證
- 關鍵資源洩漏

**計劃修復 (Medium)：**
- 代碼質量問題
- 依賴版本固定
- 性能優化

**持續改進 (Low)：**
- 代碼風格
- 文檔完整性
- 小型優化

### 3. 人工審查

對於標記為 "需要審查" 的修復：
1. 查看自動生成的修復建議
2. 在測試環境驗證
3. 代碼審查後合併

### 4. 持續監控

- 定期查看儀表板
- 設置風險警戒線
- 建立響應計劃

## 故障排除

### 掃描失敗

**問題：** Bandit 掃描失敗
```bash
# 檢查 Python 文件語法
python -m py_compile your_file.py

# 單獨運行 Bandit 調試
bandit -r . -v
```

**問題：** 找不到文件
```bash
# 確保在儲存庫根目錄執行
cd /path/to/repo
python .github/code-scanning/tools/advanced_scanner.py
```

### 修復失敗

**問題：** 修復後代碼無法運行
```bash
# 查看修復報告中的失敗項目
cat .github/code-scanning/reports/fix-report-*.json

# 手動審查修復內容
git diff
```

**問題：** 自動修復引入新問題
```bash
# 回滾修復
git checkout -- .

# 重新掃描驗證
python .github/code-scanning/tools/advanced_scanner.py
```

### 儀表板無法訪問

```bash
# 檢查端口是否被佔用
lsof -i :5000

# 使用不同端口啟動
DASHBOARD_PORT=8080 python .github/code-scanning/tools/dashboard.py

# 開發環境允許外部訪問（切勿用於生產）
DASHBOARD_HOST=0.0.0.0 python .github/code-scanning/tools/dashboard.py

# 啟用除錯模式（僅限開發環境）
DASHBOARD_DEBUG=true python .github/code-scanning/tools/dashboard.py
```

**安全最佳實踐：**
- ✅ **開發環境：** 可使用 `DASHBOARD_HOST=0.0.0.0` 方便團隊訪問
- ❌ **生產/共享環境：** 切勿綁定到 `0.0.0.0`，保持預設的 `127.0.0.1`
- ❌ **除錯模式：** 切勿在生產環境啟用，會暴露敏感資訊和安全漏洞
- ✅ **建議：** 使用反向代理（如 nginx）並配置適當的身份驗證

## 貢獻指南

歡迎貢獻！請：

1. Fork 儲存庫
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

## 許可證

本項目使用與主儲存庫相同的許可證。

## 支援

如有問題或建議，請：
- 開啟 Issue
- 聯繫維護者
- 查看文檔

## 更新日誌

### v1.0.0 (2024-01-01)
- ✅ 初始版本發布
- ✅ 高階深度掃描
- ✅ 根因分析引擎
- ✅ 一鍵自動修復
- ✅ Web 儀表板
- ✅ GitHub Actions 集成

---

**🚀 讓代碼更安全、更可靠！**