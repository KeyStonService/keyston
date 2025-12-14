# AI Prompts - 供 LLM / Agent 使用的提示詞集合

本文件包含專門設計給 LLM（如 ChatGPT、Claude）和 AI Agent 使用的提示詞，用於產生和更新 `03_refactor/` 中的重構劇本。

---

## 📚 System Prompts 參考

**完整的 System Prompt（Proposer/Critic 雙層 AI 工作流程）請參閱：**

👉 **[PROPOSER_CRITIC_WORKFLOW.md](./PROPOSER_CRITIC_WORKFLOW.md)**

該文件包含：
- 🎭 Proposer（提案者）角色定義與 System Prompt
- 🔍 Critic（審查者）角色定義與 System Prompt  
- 🔄 完整的 Proposer → Critic → Revision 循環流程
- 📋 架構約束、語言策略、品質閾值的使用方式
- ✅ 驗證檢查清單與品質閘門

**配置來源 (Configuration Sources)**：
- `config/system-module-map.yaml` - 模組定義、架構約束、品質閾值
- `docs/refactor_playbooks/03_refactor/index.yaml` - Cluster 對應與治理狀態
- Architecture skeletons (11 個) - 架構骨架規則

---

## 💡 快速參考：核心約束

所有 AI 重構提案都必須遵守以下約束（詳細規則見 `PROPOSER_CRITIC_WORKFLOW.md`）：

### 架構約束 (Architecture Constraints)
- ✅ **允許依賴**：從 `config/system-module-map.yaml` 讀取 `allowed_dependencies`
- ❌ **禁止依賴**：從 `config/system-module-map.yaml` 讀取 `banned_dependencies`
- 🏗️ **骨架規則**：遵守 `skeleton_rules` 連結的架構骨架

### 語言策略 (Language Strategy)
- ✅ **偏好語言**：`preferred_languages` (TypeScript, Python, Go, Rust, C++)
- ❌ **禁用語言**：`banned_languages` (PHP, Perl, Ruby)
- 📊 **語言違規**：必須減少或保持不變，不能增加

### 品質閾值 (Quality Thresholds)
- 🔴 **Semgrep HIGH**: `semgrep_high_max: 0` (零容忍)
- 🟡 **Semgrep MEDIUM**: 參考模組特定閾值
- 🧪 **測試覆蓋率**: 不得下降超過 2%
- 🌀 **圈複雜度**: 不得超過 `cyclomatic_complexity_max`

### 路徑治理 (Path Governance)
- 📂 **目標根目錄**：只能在 `target_roots` 中操作
- 🚫 **禁止新子目錄**：`allow_new_subdirs: false` (預設)
- 🔍 **檔案匹配**：遵守 `include_globs` 和 `exclude_globs`

---

## 1.5 高階最佳化推理（Global Optimization Reasoning）

**⚠️ CRITICAL REQUIREMENT**: All refactor playbook generation MUST follow the **Global Optimization First** principle defined in `.github/AI-BEHAVIOR-CONTRACT.md` Section 9.

### 三層回應結構（Three-Layer Response Structure）

Every playbook proposal MUST include:

#### 1. 全局優化視圖（Global Optimization View）

```yaml
optimization_targets:
  language_clarity:
    current: "Mixed TS/JS/Shell in this cluster"
    target: "Pure TypeScript + minimal Python utilities"
    metric: "Language violations count"
    baseline: 15
    goal: 5
    expected_improvement: "-67%"
    
  security_posture:
    current: "3 HIGH, 8 MEDIUM Semgrep findings"
    target: "0 HIGH, ≤2 MEDIUM"
    metric: "Semgrep severity score"
    baseline: 11
    goal: 2
    expected_improvement: "-82%"
    
  architecture_compliance:
    current: "2 reverse dependencies (apps → core)"
    target: "Zero architecture violations"
    metric: "Dependency direction violations"
    baseline: 2
    goal: 0
    expected_improvement: "-100%"

hard_constraints:
  - "MUST NOT create new dependencies from apps/ to core/"
  - "MUST NOT introduce forbidden languages (PHP, Perl)"
  - "MUST maintain test coverage ≥ current - 2%"
  - "MUST respect skeleton rules defined in config/"
  - "Semgrep HIGH findings MUST be 0 after refactor"
```

#### 2. 局部方案（Local Plan）

```yaml
scope:
  target_cluster: "core/architecture-stability"
  affected_modules: ["core/unified_integration", "core/mind_matrix"]
  affected_files: 23
  unchanged_areas: ["automation/*", "apps/web"]

refactor_steps:
  - step: 1
    phase: "P0"
    action: "Convert 8 JS files to TypeScript"
    files: ["src/integrator.js", "src/processor.js", ...]
    impact_on_global_metrics:
      language_violations: "-8"
      semgrep_high: "0 (no change)"
      architecture_compliance: "0 (no change)"
    risk: LOW
    rollback: "Git revert + npm install"
    
  - step: 2
    phase: "P0"
    action: "Fix 3 HIGH severity Semgrep findings"
    files: ["src/auth/validator.ts"]
    impact_on_global_metrics:
      language_violations: "0 (no change)"
      semgrep_high: "-3"
      architecture_compliance: "0 (no change)"
    risk: MEDIUM
    rollback: "Revert commit, mark as false positive if needed"

global_impact_summary:
  net_language_violations: "-8 (53% of target achieved in P0)"
  net_semgrep_high: "-3 (100% of target achieved)"
  net_architecture_violations: "-1 (50% of target achieved)"
  overall_assessment: "POSITIVE - moves significantly toward all goals"
```

#### 3. 自我檢查（Self-Check）

```yaml
architecture_violations:
  question: "Does this refactor violate skeleton rules?"
  answer: "NO"
  evidence: "All changes stay within core/ layer, no upward dependencies"
  
language_dependency_reversal:
  question: "Do we create new problematic language dependencies?"
  answer: "NO"
  evidence: "TS migration eliminates JS, doesn't add new languages"
  
problem_shifting:
  question: "Are problems moved or solved?"
  answer: "SOLVED"
  evidence: "Language violations reduce globally by 8, not shifted to other modules"
  
constraint_compliance:
  question: "Are all hard constraints maintained?"
  answer: "YES"
  checks:
    no_reverse_deps: "✅ No new apps → core dependencies"
    no_forbidden_langs: "✅ No PHP/Perl introduced"
    coverage_maintained: "✅ Coverage 76% → 75% (within tolerance)"
    skeleton_rules: "✅ architecture-stability rules followed"
    semgrep_zero_high: "✅ HIGH findings: 3 → 0"
```

### 在劇本中的應用（Application in Playbooks）

每份 03_refactor playbook 必須包含新的區塊：

**## 3. 語言與結構重構策略（高階優化視角）**

模板結構：

```markdown
## 3. 語言與結構重構策略（Language & Architecture Optimization Strategy）

### 3.1 全局目標（Global Optimization Targets）

**本 Cluster 的優化目標：**
- 將本 cluster 從混合 TS + JS + Shell 優化為純 TypeScript + 少量 Python 工具
- 降低跨邊界依賴：apps 不直接 import core
- 消除所有 HIGH severity 安全問題
- 將語言違規從 15 降至 5 以下

**系統級約束：**
- core/ 位於架構基礎層，不可依賴 services/ 或 apps/
- 禁止使用 PHP、Perl
- 測試覆蓋率不得下降超過 2%
- 必須遵守 architecture-stability skeleton 規則

### 3.2 語言策略（Language Strategy）

**保留語言（Languages to Keep）：**
- **TypeScript**: 主要語言，用於所有業務邏輯
  - 當前：45 files (60%)
  - 目標：68 files (90%)
  - 淨變化：+23 files

- **Python**: 僅限工具腳本和 AI pipeline
  - 當前：5 files (7%)
  - 目標：5 files (7%)
  - 淨變化：0 files

**應遷出的語言（Languages to Migrate Out）：**
- **JavaScript**: 遷移至 TypeScript
  - 當前：18 files (24%)
  - 目標：0 files (0%)
  - 淨變化：-18 files
  - 優先級：P0（安全與類型安全）

- **Shell**: 遷移至 TypeScript 或 Python
  - 當前：7 files (9%)
  - 目標：2 files (3%，僅限 docker-entrypoint）
  - 淨變化：-5 files
  - 優先級：P1（可維護性）

**目標主語言：**
- **Primary**: TypeScript (90% of codebase)
- **Secondary**: Python (10% - tools & AI only)

### 3.3 架構邊界優化（Architecture Boundary Optimization）

**當前問題：**
1. `apps/web/src/utils/core-helpers.ts` 直接 import `core/unified_integration`
   - 違反：apps → core 反向依賴
   - 風險：HIGH
   - 修復：P0

2. `services/gateway/router.ts` 跳過 services API 直接調用 core
   - 違反：services 內部繞過邊界
   - 風險：MEDIUM
   - 修復：P1

**調整後的依賴方向：**
```
core/ (foundation)
  ↑ ✅ depends on: infra/
  ↓ ❌ must not depend on: services/, apps/

services/ (mediation)
  ↑ ✅ depends on: core/, infra/
  ↓ ❌ must not depend on: apps/

apps/ (presentation)
  ↑ ✅ depends on: services/, infra/
  ↓ ❌ must not depend on: core/ (MUST go through services/)
```

**邊界修復計畫：**
- P0: 移除 `apps/web → core/` 直接依賴 (2 instances)
- P1: 加入 `services/api/` facade 給 apps 使用
- P2: 添加 dependency linter 防止未來違規

### 3.4 避免循環依賴與橫向耦合（Prevent Cycles & Lateral Coupling）

**檢測到的問題：**
- ❌ `core/unified_integration ↔ core/mind_matrix` (circular)
- ❌ `services/mcp ↔ services/gateway` (lateral coupling)

**解決方案：**
- 引入 `core/interfaces/` 作為共享契約層
- 使用 dependency injection 打破循環
- 建立清晰的 service 間通訊協議

### 3.5 全局影響評估（Global Impact Assessment）

**對系統級指標的預期影響：**

| Metric | Current | Target | P0 Impact | P1 Impact | P2 Impact |
|--------|---------|--------|-----------|-----------|-----------|
| Language Violations | 15 | ≤5 | -8 | -4 | -2 |
| Semgrep HIGH | 3 | 0 | -3 | 0 | 0 |
| Architecture Violations | 2 | 0 | -1 | -1 | 0 |
| Test Coverage | 76% | ≥74% | 75% | 75% | 76% |

**Net Assessment**: ✅ ALL steps move toward global optimization goals
```

### 整合進 Proposer-Critic 工作流程

在 `PROPOSER_CRITIC_WORKFLOW.md` 中，Proposer 必須在提案前產生：

1. **Global Optimization View** → 作為提案前置條件
2. **Local Plan** → 作為具體提案內容
3. **Self-Check** → 作為提交給 Critic 前的自我審查

Critic 審查時必須驗證：
- ✅ Global Optimization View 是否完整且合理
- ✅ Local Plan 是否真的推進全局目標
- ✅ Self-Check 是否誠實評估負面影響

---

## 2. 使用者提示詞（User Prompt）

用於提供具體的輸入資料與任務要求。

### 2.1 產生完整重構劇本

```markdown
# 任務：產生 {CLUSTER_ID} 的重構劇本

## 輸入資料

### Cluster 資訊
- Cluster ID: {CLUSTER_ID}
- 對應目錄: {DIRECTORIES}
- 主要語言: {LANGUAGES}

### 語言治理報告
\```
{LANGUAGE_GOVERNANCE_REPORT}
\```

### Hotspot 分析
\```json
{HOTSPOT_JSON}
\```

### Semgrep 安全掃描
\```json
{SEMGREP_REPORT}
\```

### Migration Flow
\```json
{MIGRATION_FLOW}
\```

### 現有解構劇本（參考）
\```markdown
{DECONSTRUCTION_PLAYBOOK}
\```

### 現有集成劇本（參考）
\```markdown
{INTEGRATION_PLAYBOOK}
\```

## 任務要求

請根據以上輸入資料，產生一份完整的重構劇本，包含：

1. **Cluster 概覽**
   - 描述此 cluster 在 Unmanned Island System 中的角色
   - 分析當前語言組成與健康狀態

2. **問題盤點**
   - 彙整語言治理違規（按嚴重性排序）
   - 列出 Hotspot 檔案（按分數排序）
   - 列出安全問題（按 severity 排序）
   - 分析 Migration Flow（是來源還是接收端）

3. **語言與結構重構策略**
   - 提出語言層級策略（移除/遷出/統一）
   - 提出目錄與模組邊界調整建議
   - 確保與集成劇本對齊

4. **分級重構計畫**
   - **P0**（24-48 小時）：列出具體檔案與操作
   - **P1**（一週內）：列出具體檔案與操作
   - **P2**（持續）：列出具體檔案與操作

5. **Auto-Fix Bot 範圍界定**
   - 明確列出可以自動化的項目
   - 明確列出必須人工審查的項目

6. **驗收條件**
   - 語言治理指標（具體數字）
   - 安全指標（具體數字）
   - 架構指標（可驗證的條件）

7. **檔案與目錄結構**
   - 畫出受影響的目錄 tree
   - 為關鍵檔案/目錄加上一行註解

8. **集成對齊**
   - 上游依賴列表
   - 下游使用者列表
   - 集成步驟摘要
   - 回滾策略

## 輸出格式

使用 Markdown 格式，遵循 `REFRACTOR_PLAYBOOK_TEMPLATE.md` 的結構。
```

### 2.2 更新現有劇本

```markdown
# 任務：更新 {CLUSTER_ID} 的重構劇本

## 當前劇本
\```markdown
{CURRENT_PLAYBOOK}
\```

## 新增資料
- 新的語言治理報告（日期：{DATE}）
- 新的 Hotspot 分析（日期：{DATE}）
- 新的 Semgrep 掃描（日期：{DATE}）

## 任務要求

請根據新增資料，更新劇本的以下部分：

1. 更新「問題盤點」章節，反映最新狀況
2. 調整 P0/P1/P2 任務清單（標註新增/移除/完成的項目）
3. 更新驗收條件的當前值
4. 在檔頭加上 `Last Updated: {DATE}`

## 更新原則

- 保持原有結構不變
- 僅更新有變動的章節
- 標註哪些任務已完成（使用 ~~刪除線~~ 或 ✅）
- 新增任務需說明原因
```

### 2.3 產生 P0 緊急修復清單

```markdown
# 任務：產生 {CLUSTER_ID} 的 P0 緊急修復清單

## 當前問題
- 語言治理違規數：{COUNT}
- Semgrep HIGH severity：{COUNT}
- Hotspot score > 90：{COUNT}

## 任務要求

產生一份簡潔的 P0 緊急修復清單，包含：

1. **移除禁用語言**（如有）
   - 列出所有禁用語言檔案
   - 建議刪除或移動至 _legacy_scratch/

2. **修復高嚴重性安全問題**（如有）
   - 列出所有 Semgrep HIGH severity
   - 給出具體修復建議

3. **處理極高風險 Hotspot**（如有）
   - 列出 score > 90 的檔案
   - 建議重構或拆分策略

## 輸出格式

使用 checklist 格式：
- [ ] {檔案路徑} - {操作} - {原因}

範例：
- [ ] core/legacy/old_api.php - 刪除 - PHP 為禁用語言
- [ ] services/auth.ts:42 - 修正 SQL injection - Semgrep HIGH
```

---

## 3. Few-Shot 範例

提供範例以提升 AI 輸出品質。

### 3.1 範例：完整劇本片段

```markdown
# core/architecture-stability 重構劇本（Refactor Playbook）

- Cluster ID：`core/architecture-stability`
- 對應目錄：`core/unified_integration/`, `core/mind_matrix/`, `core/safety_mechanisms/`
- 對應集成劇本：
  - `docs/refactor_playbooks/02_integration/core__architecture_integration.md`

---

## 1. Cluster 概覽

- 角色說明：
  - 本 cluster 是 Unmanned Island System 的核心引擎，負責 AI 決策、認知處理、服務註冊與安全機制。
  - 提供統一的整合層給上層服務（services/）與應用層（apps/）使用。
  
- 主要語言組成與健康狀態：
  - **TypeScript** (60%)：主要業務邏輯，健康狀況良好
  - **Python** (35%)：AI 引擎與數據處理，有部分型別註解缺失
  - **JavaScript** (5%)：舊程式碼遺留，需遷移至 TypeScript

---

## 2. 問題盤點（來源：語言治理 / Hotspot / Semgrep / Flow）

### 語言治理問題彙總

| 規則 | 違規數 | 嚴重性 |
|------|--------|--------|
| JavaScript not allowed in core/ | 8 | HIGH |
| Missing type annotations | 23 | MEDIUM |
| Deprecated API usage | 5 | LOW |

### Hotspot 檔案

1. `core/mind_matrix/brain.js` (score: 95) - 複雜度過高，需拆分
2. `core/unified_integration/legacy_adapter.js` (score: 88) - 舊適配器，建議重寫
3. `core/safety_mechanisms/circuit_breaker.ts` (score: 72) - 缺少測試覆蓋

### Semgrep 安全問題

- **HIGH** (2)：
  - `core/unified_integration/config.ts:45` - Hardcoded secret
  - `core/mind_matrix/executor.ts:112` - Unsafe eval usage
  
- **MEDIUM** (5)：
  - 缺少輸入驗證（3 處）
  - 使用 deprecated crypto 函式（2 處）

### Migration Flow 觀察

- 本 cluster 是語言違規的**來源**：有 8 個 .js 檔案被其他模組 import
- 需優先處理，避免違規擴散到 services/ 和 apps/

---

## 4. 分級重構計畫（P0 / P1 / P2）

### P0（24–48 小時內必須處理）

- 目標：移除高風險問題，確保 CI 通過
- 行動項目：
  - `core/unified_integration/config.ts:45` — **移除硬編碼 secret**，改用環境變數
  - `core/mind_matrix/executor.ts:112` — **移除 eval**，改用安全的 Function constructor
  - `core/mind_matrix/brain.js` — **拆分為 3 個模組**：decision.ts, reasoning.ts, execution.ts
- 驗收條件：
  - Semgrep HIGH severity = 0
  - Hotspot 最高分數 < 80
  - CI 通過

### P1（一週內完成）

- 目標：語言統一與型別安全
- 行動項目：
  - 將所有 .js 檔案改寫為 .ts（共 8 個檔案）
  - 為所有 Python 函式新增型別註解（使用 mypy）
  - 更新 deprecated API 使用（共 5 處）
- 驗收條件：
  - JavaScript 檔案數 = 0
  - Python type coverage > 90%
  - 無 deprecated API 使用

### P2（持續重構）

- 目標：技術債清理與品質提升
- 行動項目：
  - 補充單元測試（目標覆蓋率 > 80%）
  - 重構複雜函式（Cyclomatic Complexity > 10）
  - 統一錯誤處理機制
- 驗收條件：
  - 測試覆蓋率 > 80%
  - 平均 Complexity < 8
  - 所有公開 API 有 JSDoc

---
```

---

## 4. 進階應用

### 4.1 批次產生劇本

```bash
# 使用腳本批次產生所有 cluster 的劇本
for cluster in core/architecture-stability services/gateway automation/autonomous; do
  python3 tools/generate-refactor-playbook.py \
    --cluster "$cluster" \
    --use-llm \
    --output "docs/refactor_playbooks/03_refactor/$(echo $cluster | tr '/' '_')_refactor.md"
done
```

### 4.2 自動更新劇本

```yaml
# .github/workflows/update-playbooks.yml
name: Auto-Update Refactor Playbooks

on:
  schedule:
    - cron: '0 0 * * 1'  # 每週一更新
  workflow_dispatch:

jobs:
  update-playbooks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate Updated Playbooks
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python3 tools/auto-update-playbooks.py \
            --llm openai \
            --model gpt-4 \
            --index docs/refactor_playbooks/03_refactor/index.yaml
      
      - name: Create PR
        uses: peter-evans/create-pull-request@v6
        with:
          title: "chore: auto-update refactor playbooks"
          body: "自動更新重構劇本（基於最新治理資料）"
          branch: auto/update-playbooks
```

---

## 5. 提示詞最佳實踐

### 5.1 提供充足上下文

❌ **不好的提示詞**：
```
請幫我產生 core/ 的重構計畫
```

✅ **好的提示詞**：
```
請根據以下資料產生 core/architecture-stability 的重構劇本：
- 語言治理報告：{完整報告}
- Hotspot 分析：{JSON}
- 當前架構：{描述}
- 集成劇本：{連結}
```

### 5.2 明確輸出格式

❌ **模糊要求**：
```
給我一些建議
```

✅ **明確要求**：
```
產生 P0/P1/P2 分級清單，每個項目包含：
- 檔案路徑
- 操作（刪除/移動/改寫）
- 驗收條件（可量化）
```

### 5.3 使用結構化輸入

使用 YAML/JSON 而非純文字：

```yaml
cluster:
  id: "core/architecture-stability"
  directories:
    - "core/unified_integration/"
    - "core/mind_matrix/"
  languages:
    TypeScript: 60%
    Python: 35%
    JavaScript: 5%
  violations:
    - rule: "JavaScript not allowed"
      count: 8
      severity: HIGH
```

---

最後更新：2025-12-06
