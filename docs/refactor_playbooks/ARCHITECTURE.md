# AI Refactor Playbook Generator - Architecture

**AI 重構 Playbook 生成器 - 架構設計**

---

## 🏗️ 系統架構

```
┌─────────────────────────────────────────────────────────────────┐
│                    Governance Data Sources                        │
│  (語言治理、安全掃描、熱點分析、遷移流向、AI 建議)                │
└────────────┬────────────────────────────────────────────────────┘
             │
             ├─► governance/language-governance-report.md
             ├─► governance/semgrep-report.json
             ├─► governance/ai-refactor-suggestions.md
             ├─► apps/web/public/data/hotspot.json
             ├─► apps/web/public/data/cluster-heatmap.json
             └─► apps/web/public/data/migration-flow.json
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│          RefactorPlaybookGenerator (Python Class)                │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  1. load_governance_data()                               │  │
│  │     • 載入所有治理資料                                    │  │
│  │     • 解析 Markdown, JSON, YAML                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  2. Cluster Analysis & Filtering                         │  │
│  │     • _get_cluster_violations()                          │  │
│  │     • _get_cluster_hotspots()                            │  │
│  │     • _get_cluster_semgrep()                             │  │
│  │     • _get_migration_flows()                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│              ┌────────────┴────────────┐                        │
│              ▼                         ▼                         │
│  ┌────────────────────┐   ┌────────────────────┐               │
│  │  LLM Mode          │   │  Stub Mode         │               │
│  │  (--use-llm)       │   │  (Default)         │               │
│  └────────────────────┘   └────────────────────┘               │
│              │                         │                         │
│              ▼                         ▼                         │
│  ┌────────────────────┐   ┌────────────────────┐               │
│  │ Generate Prompts   │   │ Generate Stub      │               │
│  │ • System Prompt    │   │ • Basic Structure  │               │
│  │ • User Prompt      │   │ • Data Summary     │               │
│  └────────────────────┘   └────────────────────┘               │
└───────────────┬────────────────────┬────────────────────────────┘
                │                    │
                ▼                    ▼
    ┌──────────────────┐   ┌──────────────────┐
    │  LLM Processing  │   │  Direct Output   │
    │  (External)      │   │  (Markdown)      │
    └──────────────────┘   └──────────────────┘
                │                    │
                └────────┬───────────┘
                         ▼
        ┌─────────────────────────────────┐
        │  docs/refactor_playbooks/       │
        │  • core__playbook.md            │
        │  • services__playbook.md        │
        │  • automation__playbook.md      │
        │  • ... (8 clusters total)       │
        └─────────────────────────────────┘
                         │
                         ▼
        ┌─────────────────────────────────┐
        │  CI/CD Automation               │
        │  (.github/workflows/)           │
        │  • Daily auto-update            │
        │  • Commit & push changes        │
        └─────────────────────────────────┘
```

## 🔄 資料流程

### 1. 資料載入階段

```python
load_governance_data()
├── Parse language-governance-report.md
│   └── Extract violations: [{file, reason}, ...]
├── Load hotspot.json
│   └── Parse hotspot list: [{file, score, reason}, ...]
├── Load cluster-heatmap.json
│   └── Build cluster map: {cluster_name: {score, ...}, ...}
├── Load migration-flow.json
│   └── Parse flows: [{source, target, count}, ...]
├── Load semgrep-report.json
│   └── Parse security issues: [{path, severity, message}, ...]
└── Load ai-refactor-suggestions.md
    └── Read global recommendations
```

### 2. Cluster 分析階段

```python
For each cluster in clusters:
    ├── Filter violations by cluster path
    ├── Filter hotspots by cluster path
    ├── Filter semgrep issues by cluster path
    ├── Extract incoming flows (target = cluster)
    └── Extract outgoing flows (source = cluster)
```

### 3. 生成階段

#### Stub Mode (Default)

```python
generate_playbook_stub(cluster_name, cluster_score)
├── Build Markdown template
├── Insert cluster overview
├── Insert violation list
├── Insert hotspot list (top 5)
├── Insert semgrep issues (top 5)
├── Add placeholder sections (P0/P1/P2)
└── Return complete Markdown
```

#### LLM Mode (--use-llm)

```python
generate_cluster_prompt(cluster_name, cluster_score)
├── Build System Prompt (role definition)
├── Build User Prompt
│   ├── Format cluster info
│   ├── Format violations
│   ├── Format hotspots
│   ├── Format semgrep issues
│   ├── Format migration flows
│   └── Add global suggestions excerpt
└── Return prompt for LLM processing
```

## 🧩 核心組件

### RefactorPlaybookGenerator Class

```python
class RefactorPlaybookGenerator:
    """Main generator class"""

    # Properties
    repo_root: Path              # Repository root directory
    clusters: Dict               # {cluster_name: {score, ...}}
    violations: List[Dict]       # [{file, reason}, ...]
    hotspots: List[Dict]        # [{file, score, reason}, ...]
    semgrep_results: List[Dict] # [{path, severity, message}, ...]
    migration_flows: Dict       # {flows: [{source, target}, ...]}
    global_suggestions: str     # Full AI suggestions text

    # Main Methods
    load_governance_data()      # Load all data sources
    generate_cluster_prompt()   # Generate LLM prompt
    generate_playbook_stub()    # Generate stub playbook
    generate_all_playbooks()    # Batch generate

    # Helper Methods
    _parse_governance_report()  # Parse Markdown report
    _get_cluster_violations()   # Filter violations
    _get_cluster_hotspots()     # Filter hotspots
    _get_cluster_semgrep()      # Filter security issues
    _get_migration_flows()      # Extract flows
    _detect_clusters()          # Auto-detect clusters
```

### Prompt Templates

#### System Prompt Structure

```
角色定義
├── 首席軟體架構師
├── 語言治理負責人
└── 安全與品質顧問

專案背景
├── 專案名稱: Unmanned Island System
├── 語言策略: TypeScript/Python (高層) + Go/C++/ROS2 (低層)
└── 治理系統: Language Governance, Hotspot, Migration Flow, Auto-Fix Bot

工作目標
├── 產生可執行的 Refactor Playbook
├── 符合既有語言政策與架構
├── 具體、可落地、有明確優先順序
└── 區分自動化與人工審查範圍
```

#### User Prompt Structure

```
[1] Cluster 基本資訊
    ├── Cluster 名稱
    └── Cluster Score

[2] 語言治理違規
    └── 違規檔案列表

[3] Hotspot 檔案
    └── 高風險檔案列表

[4] Semgrep 安全問題
    └── 安全問題列表

[5] Migration Flow Model
    ├── Incoming Flows
    └── Outgoing Flows

[6] 全局 AI 建議
    └── 建議摘要
```

### Output Format

```markdown
# Refactor Playbook: {cluster_name}

## 1. Cluster 概覽

├── 角色說明 └── 健康狀態

## 2. 問題盤點

├── 語言治理違規 ├── Hotspot 檔案 ├── Semgrep 安全問題 └── Migration Flow 觀察

## 3. 語言與結構重構策略

├── 語言層級策略 ├── 目錄結構策略 └── 語言遷移建議

## 4. 分級重構計畫

├── P0（24-48 小時）├── P1（一週內）└── P2（持續重構）

## 5. 適合交給 Auto-Fix Bot 的項目

├── 可自動修復 └── 需人工審查

## 6. 驗收條件與成功指標

├── 語言治理 CI 期望值 ├── Hotspot / Cluster Score 改善 └── 開發流程改善方向
```

## 🔌 整合點

### 1. 與 Living Knowledge Base 整合

```
Governance Data → RefactorPlaybookGenerator → Playbooks
                                                   ↓
                                    Living Knowledge Base
                                    (docs/knowledge-graph.yaml)
```

### 2. 與 Auto-Fix Bot 整合

```
Playbooks → Auto-Fix Bot
    ├── Parse P0/P1 items
    ├── Identify auto-fixable issues
    ├── Generate fix patches
    └── Create PR
```

### 3. 與 Language Governance Pipeline 整合

```
Language Governance Analyzer
    ↓ (generates)
language-governance-report.md
    ↓ (consumed by)
RefactorPlaybookGenerator
    ↓ (generates)
Playbooks
    ↓ (guides)
Refactoring Actions
    ↓ (improves)
Language Governance Score
```

## 📊 資料模型

### Violation

```python
{
    "file": "path/to/file.ext",
    "reason": "Language not allowed in this layer"
}
```

### Hotspot

```python
{
    "file": "path/to/file.ext",
    "score": 85,
    "reason": "High complexity + security issues",
    "severity": "HIGH"
}
```

### Semgrep Issue

```python
{
    "path": "path/to/file.ext",
    "rule_id": "security.sql-injection",
    "severity": "HIGH",
    "message": "Potential SQL injection detected",
    "line": 42,
    "column": 10
}
```

### Migration Flow

```python
{
    "source": "services:cpp",
    "target": "autonomous:cpp",
    "count": 3,
    "type": "suggested"
}
```

### Cluster Info

```python
{
    "score": 75,
    "violations": 3,
    "hotspots": 2,
    "languages": ["TypeScript", "Python", "PHP"]
}
```

## 🎯 設計決策

### 1. 為什麼使用 Python？

- ✅ 豐富的資料處理能力（JSON, YAML, Markdown）
- ✅ 與現有工具鏈一致（language-governance-analyzer.py）
- ✅ 易於擴展和整合 LLM API
- ✅ 良好的檔案系統操作支援

### 2. 為什麼分離 LLM 與 Stub 模式？

- ✅ 可在無 LLM API 情況下運行
- ✅ 降低 API 成本
- ✅ Stub 提供結構化模板
- ✅ 靈活整合外部 LLM（ChatGPT, Claude）

### 3. 為什麼使用 Markdown 輸出？

- ✅ 人類可讀、易於編輯
- ✅ 支援版本控制（Git diff）
- ✅ 易於轉換為其他格式（HTML, PDF）
- ✅ GitHub 原生支援

### 4. 為什麼設計 P0/P1/P2 優先級？

- ✅ 明確執行順序
- ✅ 資源分配優化
- ✅ 風險管理
- ✅ 符合敏捷開發實踐

## 🔍 擴展性設計

### 新增資料源

```python
def load_governance_data(self):
    # 現有資料源
    self._load_existing_sources()

    # 新增資料源（範例：測試覆蓋率）
    coverage_path = self.repo_root / "reports" / "coverage.json"
    if coverage_path.exists():
        with open(coverage_path, 'r') as f:
            self.coverage_data = json.load(f)
```

### 新增 Prompt 元素

```python
USER_PROMPT_TEMPLATE = """
...existing sections...

[7] 測試覆蓋率分析
該 cluster 的測試覆蓋率如下：
{coverage_text}

...rest of template...
"""
```

### 新增輸出格式

```python
def generate_playbook_json(self, cluster_name: str) -> Dict:
    """Generate JSON format playbook"""
    return {
        "cluster": cluster_name,
        "score": self.clusters.get(cluster_name, {}).get('score', 0),
        "violations": self._get_cluster_violations(cluster_name),
        "hotspots": self._get_cluster_hotspots(cluster_name),
        # ... more fields
    }
```

## 📈 效能考量

### 載入優化

- 延遲載入：只在需要時載入檔案
- 快取機制：避免重複解析
- 批次處理：一次載入所有資料

### 生成優化

- 平行處理：可並行生成多個 playbooks
- 增量更新：只重新生成變更的 clusters
- 模板快取：重用 Markdown 模板

### 記憶體管理

- 流式處理大檔案
- 及時釋放不需要的資料
- 使用 generator 減少記憶體占用

## 🛡️ 錯誤處理

```python
# 檔案不存在
if not gov_report_path.exists():
    print(f"⚠️  Governance report not found: {gov_report_path}")
    # Continue with empty data

# JSON 解析錯誤
try:
    data = json.load(f)
except json.JSONDecodeError as e:
    print(f"❌ Error parsing JSON: {e}")
    data = {}

# YAML 解析錯誤
try:
    data = yaml.safe_load(f)
except yaml.YAMLError as e:
    print(f"❌ Error parsing YAML: {e}")
    data = {}
```

---

**版本:** 1.0.0  
**日期:** 2025-12-06  
**維護:** SynergyMesh Development Team
