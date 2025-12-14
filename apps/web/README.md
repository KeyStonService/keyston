# Web Application - Enterprise Frontend & APIs

## 🚀 Unmanned Island System Web Platform

### 📋 概述

企業級 Web 應用，提供 SynergyMesh 平台的前端介面、FastAPI 後端服務，以及語言治理儀表板。

#### 主要功能
- **React + TypeScript 前端**：現代化 SPA，使用 esbuild 建構
- **FastAPI 後端**：高效能 Python API 服務（需要獨立部署）
- **語言治理儀表板**：實時政策合規性監控與可視化

> **⚠️ 部署注意事項**
> 
> - **靜態部署**（前端）：僅需要 Node.js 和 npm，執行 `npm run build` 生成靜態文件到 `dist/` 目錄
> - **後端服務部署**：需要 Python 3.11+，依賴 `requirements.txt` 中的套件（FastAPI、uvicorn 等）
> - 如果只需要靜態前端，不需要安裝 Python 依賴或執行後端服務
> - 對於完整功能，建議使用「自動擴充」或「預留虛擬機器」部署類型以支持後端 API

---

## 🎯 Language Governance Dashboard（語言治理儀表板）⭐ **NEW**

### 功能概覽

```yaml
dashboard:
  route: "/#/language-governance"
  current_health_score: "85/100 (Grade B)"
  target_health_score: "90/100 (Grade A-)"
  
visualizations:
  - name: "Language Layer Model"
    type: "Mermaid 流程圖"
    layers: [L0, L1, L2, L3, L4, L5]
    description: "六層架構圖：L0 (C++/ROS) → L5 (TypeScript/React)"
    
  - name: "Sankey Flow Diagram"
    type: "Mermaid Sankey"
    flow: "來源層 → 違規類型 → 修復目標"
    paths: 3
    
  - name: "Hotspot Heatmap"
    type: "Canvas Treemap"
    algorithm: "(Forbidden×5) + (CrossLayer×3) + (Security×2) + (Repeated×4)"
    color_coding:
      critical: "70-100 (🔴)"
      high: "40-69 (🟠)"
      moderate: "1-39 (🟡)"
    
  - name: "Migration Flow Model"
    type: "Mermaid Sankey"
    flow: "來源叢集:語言 → 目標叢集:語言"
    types: ["✓ Historical", "→ Suggested"]

metrics:
  total_violations: 2
  security_findings: 1
  fix_success_rate: "87%"
  hotspots: 4
  critical_hotspots: 1
  migration_flows: 9
```

### 快速開始

```bash
# 安裝依賴
npm install

# 啟動開發伺服器（Vite 預設在 port 8000，已配置）
npm run dev
# 瀏覽器開啟: http://localhost:8000/#/language-governance

# 建構生產版本
npm run build

# 啟動 FastAPI 後端（獨立，從專案根目錄執行）
cd services
python -m uvicorn api:app --reload --port 8000
# 或直接執行（已配置為 port 8000）：
python api.py
# API: http://localhost:8000/api/v1/language-governance
```

### 前端組件

| 組件檔案                              | 說明                         | 路徑                                        |
| ------------------------------------- | ---------------------------- | ------------------------------------------- |
| `src/pages/LanguageGovernance.tsx`    | 主儀表板頁面                 | `/#/language-governance`                    |
| `src/components/Mermaid.tsx`          | Mermaid 圖表渲染器           | 用於層級模型                                |
| `src/components/SankeyDiagram.tsx`    | Sankey 違規流向圖            | 顯示來源→類型→修復                          |
| `src/components/HotspotHeatmap.tsx`   | Canvas 熱力圖 Treemap        | 互動式違規強度可視化                        |
| `src/components/MigrationFlow.tsx`    | 叢集遷移流程圖               | 顯示歷史與建議的遷移路徑                    |
| `src/components/layout/Navbar.tsx`    | 導航列（已更新）             | 新增「語言治理」連結                        |

### 後端 API

#### 端點：`GET /api/v1/language-governance`

**回應範例：**
```json
{
  "health_score": 85,
  "grade": "B",
  "violations": [
    {
      "file": "apps/web/src/legacy-code.js",
      "layer": "L5: Applications",
      "severity": "warning",
      "issue": "JavaScript file in TypeScript project"
    }
  ],
  "semgrep": {
    "findings": 1,
    "rules": ["javascript.lang.security.audit.xss"]
  },
  "history": [
    {
      "timestamp": "2025-12-06T03:26:36",
      "event": "auto-fix applied",
      "details": "Fixed 3 TypeScript violations in core module"
    }
  ],
  "sankeyData": {
    "flows": [...]
  },
  "hotspotData": {
    "hotspots": [...]
  },
  "migrationData": {
    "edges": [...],
    "statistics": {...}
  }
}
```

**資料來源：**
- `governance/language-governance-report.md`
- `governance/semgrep-report.json`
- `governance/sankey-data.json`
- `governance/hotspot-data.json`
- `governance/migration-flow.json`
- `knowledge/language-history.yaml`
- `docs/KNOWLEDGE_HEALTH.md`

### 資料產生器

| 工具                                   | 產出檔案                                                      | 功能                     |
| -------------------------------------- | ------------------------------------------------------------- | ------------------------ |
| `tools/generate-sankey-data.py`        | `governance/sankey-data.json`                                 | 違規流向分析             |
| `tools/generate-hotspot-heatmap.py`    | `governance/hotspot-data.json`, `docs/HOTSPOT_HEATMAP.md`     | 違規強度計算             |
| `tools/generate-migration-flow.py`     | `governance/migration-flow.json`, `docs/MIGRATION_FLOW.md`    | 叢集遷移追蹤             |

```bash
# 手動執行產生器
python3 tools/generate-sankey-data.py
python3 tools/generate-hotspot-heatmap.py
python3 tools/generate-migration-flow.py
```

### CI/CD 自動化

**工作流：** `.github/workflows/language-governance-dashboard.yml`

- **觸發**：每日 00:00 UTC、push/PR 到 main/develop
- **步驟**：
  1. 語言分佈分析
  2. Semgrep 安全掃描
  3. 產生 Sankey 資料
  4. 產生 Hotspot 資料
  5. 產生 Migration Flow 資料
  6. 計算健康分數
  7. 自動提交更新的報告

### 開發與測試

```bash
# 型別檢查
npm run type-check
# 或
tsc --noEmit

# Lint
npm run lint

# 建構
npm run build

# 預覽生產版本
npm run preview
```

### 相關文檔

- [完整實作指南](../docs/LANGUAGE_GOVERNANCE_IMPLEMENTATION.md)
- [Hotspot 演算法](../docs/HOTSPOT_HEATMAP.md)
- [遷移流模型](../docs/MIGRATION_FLOW.md)
- [PR 分析與行動計劃](../docs/PR_ANALYSIS_AND_ACTION_PLAN.md)

---

## 🚀 Legacy: Enterprise Code Intelligence Platform v2.0

### 📋 概述（Phase 2）

這是 SynergyMesh 平台的 Phase 2 核心服務開發，實現了企業級代碼分析服務，支持多語言、多策略的智能代碼分析。

### 🏗️ 架構

```
advanced-system-src/
├── services/
│   └── code_analyzer.py    # 代碼分析服務核心
├── tests/
│   ├── __init__.py
│   └── test_code_analyzer.py  # 完整測試套件
├── requirements.txt        # Python 依賴
├── pytest.ini             # 測試配置
└── README.md              # 本文檔
```

### 🔧 安裝

#### 1. 安裝 Python 依賴

```bash
# 創建虛擬環境（推薦）
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r requirements.txt
```

#### 2. 驗證安裝

```bash
python -c "import services.code_analyzer; print('OK')"
```

### 🧪 測試

#### 運行所有測試

```bash
pytest
```

#### 運行特定測試

```bash
# 單元測試
pytest -m unit

# 集成測試
pytest -m integration

# 性能測試
pytest -m performance

# 特定文件
pytest tests/test_code_analyzer.py

# 特定測試
pytest tests/test_code_analyzer.py::TestStaticAnalyzer::test_detect_hardcoded_secrets
```

#### 查看測試覆蓋率

```bash
pytest --cov=services --cov-report=html
# 打開 htmlcov/index.html 查看詳細報告
```

### 📊 功能特性

#### 1. 多語言支持

- ✅ Python
- ✅ JavaScript/TypeScript
- ✅ Go
- ✅ Rust
- ✅ Java
- ✅ C++

#### 2. 分析策略

- **QUICK** - 快速分析 (< 1 分鐘)
- **STANDARD** - 標準分析 (1-5 分鐘)
- **DEEP** - 深度分析 (5-30 分鐘)
- **COMPREHENSIVE** - 全面分析 (30+ 分鐘)

#### 3. 檢測能力

**安全漏洞 (6 類)**:

- 硬編碼密鑰
- SQL 注入
- XSS 漏洞
- CSRF 漏洞
- 不安全的反序列化
- 密碼學弱點

**代碼質量**:

- 圈複雜度
- 代碼重複率
- 類型註解缺失

**性能問題**:

- N+1 查詢
- 低效循環

**可維護性**:

- 文件長度
- 函數複雜度

**依賴管理**:

- 過時的依賴
- 安全漏洞

**可訪問性**:

- 缺少 alt 屬性

**合規性**:

- 許可證聲明

### 💻 使用示例

#### 基本用法

```python
import asyncio
from services.code_analyzer import (
    CodeAnalysisEngine,
    AnalysisStrategy
)

async def main():
    # 創建分析引擎
    config = {'max_workers': 4}
    engine = CodeAnalysisEngine(config)
    
    # 分析代碼庫
    result = await engine.analyze_repository(
        repo_path="/path/to/repo",
        commit_hash="abc123",
        strategy=AnalysisStrategy.STANDARD
    )
    
    # 查看結果
    print(f"Total issues: {result.total_issues}")
    print(f"Critical issues: {result.critical_issues}")
    print(f"Quality score: {result.quality_score}")
    print(f"Risk level: {result.risk_level}")
    
    # 查看問題詳情
    for issue in result.issues:
        print(f"[{issue.severity.value}] {issue.message}")
        print(f"  File: {issue.file}:{issue.line}")
        print(f"  Suggestion: {issue.suggestion}")

if __name__ == '__main__':
    asyncio.run(main())
```

#### 分析單個文件

```python
import asyncio
from services.code_analyzer import (
    CodeAnalysisEngine,
    AnalysisStrategy
)

async def analyze_file():
    config = {'max_workers': 2}
    engine = CodeAnalysisEngine(config)
    
    # 分析文件
    issues = await engine.analyze_file(
        file_path="example.py",
        strategy=AnalysisStrategy.DEEP
    )
    
    print(f"Found {len(issues)} issues")
    for issue in issues:
        print(f"- {issue.message}")

asyncio.run(analyze_file())
```

#### 使用緩存

```python
import redis
from services.code_analyzer import (
    CodeAnalysisEngine,
    StaticAnalyzer
)

# 創建 Redis 客戶端
redis_client = redis.Redis(host='localhost', port=6379)

# 使用緩存的分析器
config = {'cache_enabled': True}
analyzer = StaticAnalyzer(config, cache_client=redis_client)

# 後續分析會使用緩存
```

### 📈 性能指標

- **分析速度**: 1000-5000 行/秒
- **準確率**: > 95%
- **測試覆蓋率**: > 80%
- **記憶體使用**: < 512 MB
- **並發處理**: 支持多線程

### 🔒 安全性

- ✅ 無硬編碼密鑰
- ✅ 輸入驗證
- ✅ 安全的依賴版本
- ✅ CodeQL 掃描通過（0 警告）

### 📚 API 文檔

詳細的 API 文檔請參考代碼中的 docstring。主要類和函數：

- `CodeAnalysisEngine` - 主分析引擎
- `StaticAnalyzer` - 靜態代碼分析器
- `BaseAnalyzer` - 分析器基類
- `CodeIssue` - 代碼問題數據模型
- `AnalysisResult` - 分析結果數據模型
- `CodeMetrics` - 代碼指標數據模型

### 🛠️ 開發

#### 代碼格式化

```bash
# 格式化代碼
black services/ tests/

# 檢查代碼風格
flake8 services/ tests/

# 類型檢查
mypy services/
```

#### 運行 Linter

```bash
pylint services/code_analyzer.py
```

### 🤝 貢獻

1. Fork 本項目
2. 創建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

### 📝 變更日誌

#### v2.0.0 (2025-11-25)

- ✅ 實現完整的代碼分析服務
- ✅ 支持 6 種編程語言
- ✅ 實現 4 種分析策略
- ✅ 添加完整的測試套件（80%+ 覆蓋率）
- ✅ 支持緩存機制
- ✅ 企業級錯誤處理和日誌記錄

### 📄 許可證

MIT License - 詳見 LICENSE 文件

### 👥 作者

SynergyMesh Team - Enterprise Code Intelligence Platform v2.0

### 🔗 相關鏈接

- [PHASE1_IMPLEMENTATION_SUMMARY.md](../PHASE1_IMPLEMENTATION_SUMMARY.md)
- [PRODUCTION_READINESS.md](../PRODUCTION_READINESS.md)
- [項目主頁](https://github.com/we-can-fix/synergymesh)
