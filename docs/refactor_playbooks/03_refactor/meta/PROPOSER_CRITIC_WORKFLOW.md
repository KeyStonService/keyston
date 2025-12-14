# Proposer/Critic 雙層 AI 重構工作流程
# Proposer/Critic Dual-Layer AI Refactor Workflow

**Date:** 2025-12-06  
**Purpose:** 定義重構的雙角色 AI 驗證流程  
**Status:** ✅ Active

---

## 📋 概述

傳統重構流程：單一 AI → 產生 patch → CI 檢查 → Merge

**增強版流程**（Proposer/Critic）：

```
Proposer (建議者) → 產生重構方案
    ↓
Critic (審查者) → 用架構規則嚴格審查
    ↓
修正循環 (如有違規)
    ↓
CI 驗證 → Quality Gates
    ↓
Human Review → Merge
```

---

## 🎭 角色定義

### Role A: Proposer（建議者）

**職責**：產生重構方案與具體 patch

**輸入資料**：
1. `language-governance-report.md` - 語言違規清單
2. `hotspot.json` - 高風險檔案列表
3. `cluster-heatmap.json` - Cluster 健康狀態
4. `docs/refactor_playbooks/03_refactor/{{cluster}}/*_refactor.md` - 重構劇本
5. `config/system-module-map.yaml` - Module 定義與 refactor 規則

**輸出**：
1. **架構設計方案**
   - 新的目錄結構
   - 新的 interface / API 定義
   - 模組依賴關係圖
   
2. **具體 Patch**
   - 檔案移動計畫
   - 程式碼修改 (diff)
   - import/require 路徑更新
   
3. **理由說明**
   - 為什麼這樣改？
   - 解決了哪些問題？
   - 影響評估

### Role B: Critic（審查者）

**職責**：用架構骨架與 refactor 規則嚴格審查 Proposer 的方案

**角色定位**：
- 首席架構師（Chief Architect）
- 安全顧問（Security Advisor）
- 品質守門員（Quality Gatekeeper）

**審查依據**：
1. `config/system-module-map.yaml` 中的 `refactor.architecture_constraints`
2. `automation/architecture-skeletons/` 中的骨架規則
3. `governance/policies/` 中的治理政策
4. Anti-pattern 清單

**審查項目**：

#### 1. 架構約束檢查
- ✅ 依賴方向是否正確？
  - core → apps? ❌
  - services → core? ✅
  
- ✅ 是否違反模組邊界？
  - 直接跨 domain import? ❌
  - 透過 interface 呼叫? ✅

#### 2. 語言策略檢查
- ✅ 是否使用 preferred languages？
- ❌ 是否引入 banned languages？
- ✅ 語言混用是否減少？

#### 3. 品質指標檢查
- ✅ 複雜度是否降低？
- ✅ 測試覆蓋率是否維持/提升？
- ❌ 是否引入新的安全問題？

#### 4. 可維護性檢查
- ✅ 命名是否清晰？
- ✅ 是否符合專案風格？
- ✅ 是否有充分文檔？

**輸出**：
1. **Approved** - 通過審查，可進入 CI
2. **Rejected with Reasons** - 列出具體違規項目，要求 Proposer 修正
3. **Conditional Approved** - 需要額外人工審查的部分

---

## 🔄 工作流程詳細步驟

### Phase 1: Proposer 產生方案

**Step 1.1: 收集輸入資料**

```bash
# 讀取 cluster 的重構劇本
cluster_id="core/architecture-stability"
playbook_file="docs/refactor_playbooks/03_refactor/core/core__architecture_refactor.md"

# 讀取 module 的 refactor 配置
module_config=$(yq '.directory_categories.core_platform.modules.unified_integration.refactor' \
                   config/system-module-map.yaml)

# 讀取治理資料
governance_report="governance/language-governance-report.md"
hotspot_data="apps/web/public/data/hotspot.json"
semgrep_report="governance/semgrep-report.json"
```

**Step 1.2: 分析問題**

Proposer 分析：
- 語言違規有哪些？
- Hotspot 檔案在哪裡？
- 依賴關係是否混亂？
- 有哪些安全問題？

**Step 1.3: 產生重構方案**

```markdown
## Proposer 輸出範例

### 方案概述
將 `core/unified_integration/` 中的 5 個 JavaScript 檔案遷移為 TypeScript。

### 架構變更
1. 新增 `core/unified_integration/interfaces/` 目錄
2. 定義明確的 TypeScript interfaces
3. 移除對 `apps/` 的直接依賴

### 具體 Patch
- `cognitive_processor.js` → `cognitive_processor.ts`
- 新增 `interfaces/ICognitiveProcessor.ts`
- 更新 35 處 import 路徑

### 預期效果
- 語言違規數：15 → 3
- Semgrep HIGH: 2 → 0
- Type safety: 40% → 95%

### 風險評估
- 中等風險：需要更新 5 個下游服務的 import
- 緩解措施：先保留舊檔案，逐步切換
```

### Phase 2: Critic 審查方案

**Step 2.1: 載入審查規則**

```python
# 從 module map 讀取架構約束
architecture_constraints = module_config['architecture_constraints']
quality_thresholds = module_config['quality_thresholds']

# 從 skeleton 讀取規則
skeleton_rules = load_skeleton_rules(['architecture-stability', 'api-governance'])
```

**Step 2.2: 執行審查**

```markdown
## Critic 審查結果範例

### ✅ 通過項目
1. 依賴方向正確
   - 移除了對 apps/ 的依賴 ✅
   - 只依賴 core/ 內部模組 ✅

2. 語言策略符合
   - JavaScript → TypeScript ✅
   - 沒有引入 banned languages ✅

3. 品質指標改善
   - 違規數減少 80% ✅
   - Semgrep HIGH 清零 ✅

### ❌ 違規項目
1. 架構邊界問題
   - `cognitive_processor.ts` 第 42 行仍然 import 了 `apps/web/utils`
   - **要求**：必須移除，或改用 core 內部實作

2. 複雜度問題
   - `system_orchestrator.ts` 的 Cyclomatic Complexity = 23 (閾值: 15)
   - **建議**：拆分為多個小函數

3. 測試覆蓋率
   - 新的 interfaces/ 目錄沒有對應測試
   - **要求**：補充單元測試，覆蓋率 ≥ 75%

### 🔄 要求修正
請 Proposer 修正上述 3 個違規項目後重新提交。
```

**Step 2.3: 修正循環**

如果 Critic 發現違規：
1. 將審查結果返回給 Proposer
2. Proposer 修正方案
3. 重新提交給 Critic
4. 重複直到通過審查（或達到最大循環次數）

### Phase 3: CI 驗證

**通過 Critic 審查後**，進入 CI 流程：

```yaml
# .github/workflows/refactor-validation.yml
- name: Architecture Constraints Check
  run: python3 tools/validate-architecture-constraints.py
  
- name: Quality Metrics Check
  run: python3 tools/check-refactor-metrics.py --before --after
  
- name: Language Governance Check
  run: npm run governance:check
  
- name: Semgrep Security Scan
  run: semgrep --config auto
  
- name: Test Coverage Check
  run: npm run test:coverage
```

### Phase 4: Human Review

**即使通過 CI**，仍需人工審查：
- P0 級別的重構
- 涉及安全邊界的變更
- 跨服務的 API 變更

---

## 💻 System Prompt 範例

### For Proposer

```markdown
你是 Unmanned Island System 的「重構建議者（Proposer）」。

## 你的任務
根據語言治理報告、Hotspot 分析和重構劇本，產生具體的重構方案與 patch。

## 輸入資料
你會收到：
1. Cluster ID 和對應的重構劇本
2. `config/system-module-map.yaml` 中該 module 的 refactor 配置
3. 語言治理報告和安全掃描結果

## 輸出格式
你必須產生：

### 1. 方案概述
- 簡述要做什麼重構
- 預期解決哪些問題

### 2. 架構變更
- 目錄結構變化
- 新增/刪除的檔案
- Interface 定義

### 3. 具體 Patch
- 每個檔案的修改（unified diff 格式）
- Import/require 路徑更新

### 4. 預期效果
- Before/After 指標比對
- 風險評估

### 5. 驗證計畫
- 如何測試這些變更？
- 回滾策略是什麼？

## 約束條件
- 只能在 `target_roots` 定義的目錄中修改
- 不得使用 `banned_languages`
- 必須遵守 `architecture_constraints` 中的依賴規則
- 語言違規數必須減少，不得增加

## 成功標準
你的方案必須通過 Critic 的審查，包括：
- 架構約束檢查
- 語言策略檢查
- 品質指標檢查
- 可維護性檢查
```

### For Critic

```markdown
你是 Unmanned Island System 的「重構審查者（Critic）」。

## 你的角色
- 首席架構師：確保架構一致性
- 安全顧問：防止安全問題
- 品質守門員：維持程式碼品質

## 你的任務
嚴格審查 Proposer 提出的重構方案，確保符合所有規則。

## 審查依據
1. `config/system-module-map.yaml` 中的 `refactor.architecture_constraints`
2. `automation/architecture-skeletons/` 中的骨架規則
3. `governance/policies/` 中的治理政策
4. 專案的 Anti-pattern 清單

## 審查清單

### 架構約束
- [ ] 依賴方向是否正確？
- [ ] 是否違反模組邊界？
- [ ] 是否符合 skeleton 規則？

### 語言策略
- [ ] 是否使用 preferred languages？
- [ ] 是否避免 banned languages？
- [ ] 語言混用是否減少？

### 品質指標
- [ ] 語言違規數是否減少？
- [ ] Semgrep HIGH 是否 = 0？
- [ ] 複雜度是否在閾值內？
- [ ] 測試覆蓋率是否維持？

### 可維護性
- [ ] 命名是否清晰？
- [ ] 是否符合專案風格？
- [ ] 是否有充分文檔？

## 輸出格式

### 如果通過審查
```
## ✅ 審查通過

所有檢查項目均已通過，方案可進入 CI 驗證階段。

### 通過項目
1. 依賴方向正確 ✅
2. 語言策略符合 ✅
3. 品質指標改善 ✅
...

### 建議（非強制）
- 可以考慮進一步優化 XXX
- 建議補充 YYY 的文檔
```

### 如果發現違規
```
## ❌ 審查未通過

發現 {{N}} 個必須修正的問題。

### 違規項目
1. **架構邊界問題** (嚴重)
   - 檔案：`path/to/file.ts` 第 42 行
   - 問題：違反依賴規則，core 不可依賴 apps
   - 修正：移除對 apps/ 的 import

2. **複雜度超標** (中等)
   - 函數：`processData()`
   - Cyclomatic Complexity: 23 (閾值: 15)
   - 修正：拆分為多個小函數

...

### 要求修正
請 Proposer 修正上述問題後重新提交。
```

## 嚴格度設定
- 架構約束違規：**零容忍**，必須修正
- 語言策略違規：**零容忍**，必須修正
- 品質指標不達標：**要求改進**，可有條件通過
- 風格問題：**建議改進**，不阻擋 merge
```

---

## 📊 實際使用範例

### 範例 1: Core Architecture 重構

**Proposer Input:**
```
Cluster: core/architecture-stability
Playbook: docs/refactor_playbooks/03_refactor/core/core__architecture_refactor.md
Violations: 15 language governance issues
Hotspots: 8 files with score > 80
```

**Proposer Output:**
```markdown
## 重構方案：Core Architecture TypeScript 遷移

### 目標
將 core/unified_integration/ 中的 8 個 JS 檔案遷移為 TS

### 變更清單
1. cognitive_processor.js → cognitive_processor.ts
2. 新增 interfaces/ICognitiveProcessor.ts
3. 更新 47 處 import 路徑

### 預期效果
- 違規數：15 → 2
- Type safety: 45% → 98%
```

**Critic Review:**
```markdown
## ✅ 初步審查通過

### 發現 1 個需修正問題
1. cognitive_processor.ts 第 89 行仍 import apps/web/utils
   → 必須移除，改用 core 內部實作

請修正後重新提交。
```

**Proposer Revised:**
```markdown
已修正：
- 移除對 apps/web/utils 的依賴
- 在 core/unified_integration/utils/ 實作對應功能
- 新增單元測試

重新提交審查。
```

**Critic Final:**
```markdown
## ✅ 審查通過

所有架構約束檢查通過，可進入 CI 驗證。
```

---

## 🛠️ 工具整合

### 1. 架構約束驗證腳本

```python
# tools/validate-architecture-constraints.py
import yaml
from pathlib import Path

def validate_constraints(cluster_id, changed_files):
    # Load module config
    module_config = load_module_config(cluster_id)
    constraints = module_config['refactor']['architecture_constraints']
    
    violations = []
    
    for file in changed_files:
        # Check banned dependencies
        imports = extract_imports(file)
        for imp in imports:
            if matches_pattern(imp, constraints['banned_dependencies']):
                violations.append({
                    'file': file,
                    'line': find_line(file, imp),
                    'issue': f'Banned dependency: {imp}',
                    'severity': 'critical'
                })
    
    return violations
```

### 2. 品質指標比對腳本

```python
# tools/check-refactor-metrics.py
def check_metrics(before_commit, after_commit):
    before = collect_metrics(before_commit)
    after = collect_metrics(after_commit)
    
    results = {
        'language_violations': {
            'before': before['violations'],
            'after': after['violations'],
            'passed': after['violations'] <= before['violations']
        },
        'semgrep_high': {
            'before': before['semgrep_high'],
            'after': after['semgrep_high'],
            'passed': after['semgrep_high'] == 0
        },
        # ... more metrics
    }
    
    return results
```

---

## 📝 維護與更新

### 何時更新此工作流程

1. **新增架構骨架**
   - 更新 Critic 的審查清單
   - 補充對應的驗證邏輯

2. **調整品質閾值**
   - 更新 `system-module-map.yaml` 中的 `quality_thresholds`
   - 同步更新 CI 檢查腳本

3. **新增 Anti-pattern**
   - 記錄在 `governance/anti-patterns.md`
   - 加入 Critic 的審查規則

---

## 🎯 成功指標

### 流程層面
- Proposer 提出的方案，70% 能一次通過 Critic 審查
- Critic 發現的問題，90% 能在第二輪修正
- 通過 Critic 審查的方案，95% 能通過 CI

### 品質層面
- 重構後的語言違規數平均減少 80%
- 重構後的 Semgrep HIGH 問題 = 0
- 重構後的測試覆蓋率平均提升 10%

### 效率層面
- Proposer/Critic 循環平均 < 3 輪
- 整個重構流程（含 CI）< 2 小時
- 人工審查時間平均 < 30 分鐘

---

**Last Updated:** 2025-12-06  
**Maintainer:** Unmanned Island Architecture Team  
**Status:** ✅ Production Ready
