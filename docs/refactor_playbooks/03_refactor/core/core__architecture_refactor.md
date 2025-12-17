# core/architecture-stability 重構劇本（Refactor Playbook）

- **Cluster ID**: `core/architecture-stability`
- **對應目錄**:
  - `core/unified_integration/`
  - `core/island_ai_runtime/`
  - `core/safety_mechanisms/`
  - `core/slsa_provenance/`
  - Root level: `core/*.py` (AI engines, detectors)
- **對應集成劇本**: `docs/refactor_playbooks/02_integration/core/core__architecture_integration.md`
- **對應解構劇本**: `docs/refactor_playbooks/01_deconstruction/core/core__architecture_deconstruction.md`
- **Legacy Assets**:
  - `core-toplevel-engines-v2.5`
  - `advisory-db-javascript-legacy`
  - `mind-matrix-hypergraph-v1`
  - `unified-integration-monolithic-v2`
- **執行狀態**: 🟡 執行中（Phase 1 of 4）
- **最後更新**: 2025-12-07

---

## 1. Cluster 概覽

### 角色說明

本 cluster 是 **Unmanned Island System 的核心引擎層**，在系統中扮演以下角色：

- **MachineNativeOps Core Engine** 的主要實作
- 提供認知處理、服務管理、AI 決策引擎
- 實作安全機制（斷路器、緊急停止、回滾系統）
- 管理 SLSA 溯源與證明系統
- 作為 services/ 與 apps/ 層的基礎平台

### 主要語言組成與健康狀態

當前語言分佈：

- **Python** (70%)：AI 引擎、認知處理器、自主系統核心
- **TypeScript** (25%)：Contract Service L1、介面定義
- **Go** (3%)：高效能元件、溯源驗證
- **其他** (2%)：Shell scripts、配置檔案

健康狀態：

- ✅ 核心業務邏輯穩定
- ⚠️ 存在部分 JavaScript 舊程式碼需遷移
- ⚠️ Python 型別註解覆蓋率不足
- ✅ TypeScript 部分符合嚴格模式

---

## 2. 問題盤點（來源：語言治理 / Hotspot / Semgrep / Flow）

### 語言治理問題彙總

根據 `apps/web/public/data/hotspot.json` 的實際掃描結果：

| 檔案 | Score | 嚴重性 | 問題描述 |
|------|-------|--------|----------|
| `core/legacy_module/old_api.php` | 95 | CRITICAL | 禁用語言 PHP + 高複雜度 |
| `core/mind_matrix/brain.js` | 75 | MEDIUM | 應使用 TypeScript 而非 JavaScript |

主要問題類型：

- **禁用語言**：PHP 檔案存在於 core/（必須立即移除）
- **語言不一致**：JavaScript 檔案存在於 core/（應遷移至 TypeScript）
- **技術債**：Legacy module 含有高複雜度程式碼

### Hotspot 檔案

根據實際掃描數據，core/ 下的高風險檔案：

1. **`core/legacy_module/old_api.php`** (score: 95, CRITICAL)
   - 問題：Forbidden language + high complexity
   - 影響：阻塞 CI，違反語言治理政策
   - 建議：立即刪除或移至 _legacy_scratch/

2. **`core/mind_matrix/brain.js`** (score: 75, MEDIUM)
   - 問題：Should use TypeScript instead of JavaScript
   - 影響：型別安全性不足，維護困難
   - 建議：改寫為 TypeScript，補充型別定義

### Semgrep 安全問題

根據 `governance/semgrep-report.json` 掃描結果：

✅ **目前無 Semgrep 報告的安全問題**

持續關注點：

- 密鑰管理（確保無硬編碼密鑰）
- 輸入驗證（API 邊界檢查）
- 依賴安全性（定期更新依賴）

### Migration Flow 觀察

根據 `apps/web/public/data/migration-flow.json` 分析：

**Outgoing Flows（從 core/ 流出）**：

1. `core:php` → `removed` (建議移除)
   - 行動：刪除 `core/legacy_module/old_api.php`

2. `core:javascript` → `core:typescript` (建議遷移)
   - 行動：將 `core/mind_matrix/brain.js` 改寫為 TypeScript

**角色定位**：

- core/ 是語言違規的**來源**之一（有 PHP 和 JavaScript 違規）
- **優先處理**：避免違規語言擴散到其他模組
- **目標狀態**：成為純 Python + TypeScript 的核心層

---

## 3. 語言與結構重構策略

### 語言層級策略

#### 統一主語言

- **Python**：保持為核心 AI/認知處理的主要語言
- **TypeScript**：用於 Contract Service 與公開 API 定義
- **Go**：保留用於高效能元件（如 SLSA 驗證）

#### 遷出/移除語言

- **JavaScript** → **TypeScript**：遷移所有 .js 檔案
- **Shell Scripts**：評估是否可改寫為 Python/TypeScript

### 目錄與模組邊界調整

#### 當前結構問題

1. 頂層 Python 檔案過多（`ai_decision_engine.py`, `auto_bug_detector.py` 等）
2. `modules/` 目錄結構不夠清晰
3. Contract Service 是否應獨立？

#### 建議調整

```text
core/
├─ unified_integration/        # 統一整合層（保持）
├─ mind_matrix/                # 心智矩陣（保持）
├─ safety_mechanisms/          # 安全機制（保持）
├─ slsa_provenance/            # SLSA 溯源（保持）
├─ ai_engines/                 # 新增：整合所有 AI 引擎
│  ├─ decision/                # 決策引擎
│  ├─ hallucination_detection/ # 幻覺偵測
│  └─ context_understanding/   # 上下文理解
├─ cognitive_processing/       # 新增：認知處理層
│  ├─ perception/              # 感知層
│  ├─ reasoning/               # 推理層
│  ├─ execution/               # 執行層
│  └─ proof/                   # 證明層
└─ contract_service/           # 考慮：是否移至 services/contracts
```

### 與集成方案的對齊

必須符合 `02_integration/core__architecture_integration.md` 中定義的：

- 公開 API 介面規範
- 與 services/ 的邊界約定
- 與 governance/ 的整合方式

---

## 4. 分級重構計畫（P0 / P1 / P2）

### P0（24–48 小時內必須處理）

- 目標：清除 CRITICAL 級別違規，確保 CI 通過
- 行動項目（檔案層級）：
  - ✅ **行動 1**：`core/legacy_module/old_api.php` (score: 95, CRITICAL)
    - **操作**：刪除此檔案（PHP 為禁用語言）
    - **備份**：如需保留參考，移動至 `docs/refactor_playbooks/_legacy_scratch/`
    - **影響評估**：檢查是否有其他檔案 import 此模組
    - **預估時間**：2 小時（含影響評估）
  
  - ✅ **行動 2**：`core/mind_matrix/brain.js` (score: 75, MEDIUM → P0 因為影響範圍大)
    - **操作**：改寫為 TypeScript (`brain.ts`)
    - **步驟**：
      1. 複製 `brain.js` → `brain.ts`
      2. 新增型別定義與 interface
      3. 更新所有 import 路徑
      4. 執行 TypeScript 編譯驗證
      5. 刪除原始 `brain.js`
    - **預估時間**：6-8 小時

- 驗收條件：
  - ✅ core/ 目錄下無 PHP 檔案
  - ✅ core/ 目錄下無 JavaScript 檔案（除了配置檔）
  - ✅ 語言治理 CRITICAL severity = 0
  - ✅ CI 語言治理檢查通過
  - ✅ 所有相關單元測試通過

### P1（一週內完成）

- 目標：語言統一與架構清晰化
- 行動項目：
  - 遷移所有 JavaScript 檔案至 TypeScript
  - 為 Python 核心模組新增型別註解（使用 mypy）
  - 重構頂層 Python 檔案到對應子目錄
    - `ai_decision_engine.py` → `ai_engines/decision/`
    - `context_understanding_engine.py` → `ai_engines/context_understanding/`
    - `hallucination_detector.py` → `ai_engines/hallucination_detection/`
  - 更新所有 import 路徑
- 驗收條件：
  - core/ 目錄下 JavaScript 檔案數 = 0
  - Python 型別註解覆蓋率 > 85%
  - 目錄結構符合新設計

### P2（持續重構）

- 目標：技術債清理與品質提升
- 行動項目：
  - 補充單元測試（目標覆蓋率 > 80%）
  - 重構高複雜度函式（Cyclomatic Complexity > 10）
  - 建立 core/ 各子模組的 README.md
  - 評估 Contract Service 是否移至 services/
  - 統一錯誤處理與日誌格式
- 驗收條件：
  - 測試覆蓋率 > 80%
  - 平均函式 Complexity < 8
  - 所有子目錄有 README.md

---

## 5. Auto-Fix Bot 可以處理的項目

### 適合 Auto-Fix 的變更

以下項目可以安全地交給 Auto-Fix Bot：

1. **型別註解補強**
   - 為 Python 函式新增型別提示
   - 為 TypeScript 變數補充型別定義

2. **Import 路徑修正**
   - 更新模組移動後的 import 路徑
   - 統一使用絕對路徑或相對路徑

3. **格式化與風格**
   - 執行 Black (Python) / Prettier (TypeScript)
   - 修正 Flake8 / ESLint 可自動修復的問題

4. **簡單重構**
   - 移除未使用的 import
   - 重新命名變數以符合命名規範

### 必須人工審查的變更

以下項目必須由人類工程師審查：

1. **核心業務邏輯變更**
   - 修改 AI 決策演算法
   - 調整認知處理流程
   - 變更安全機制邏輯

2. **API 合約變更**
   - 修改公開 API 簽名
   - 變更與 services/ 的介面
   - 調整與 governance/ 的整合點

3. **安全相關變更**
   - 修改 SLSA 溯源邏輯
   - 變更密鑰管理方式
   - 調整安全邊界

4. **架構決策**
   - 模組的拆分或合併
   - 新增或移除依賴
   - 變更目錄結構

---

## 6. 驗收條件與成功指標

### 語言治理指標

| 指標 | 當前值 | 目標值 | 驗證方式 |
|------|--------|--------|----------|
| 語言違規數 | **2** (1 CRITICAL + 1 MEDIUM) | <= 2 | `npm run governance:check` |
| PHP 檔案數 | **1** (`core/legacy_module/old_api.php`) | **0** | `find core/ -name "*.php" \| wc -l` |
| JavaScript 檔案數 | **1** (`core/mind_matrix/brain.js`) | **0** | `find core/ -name "*.js" \| wc -l` |
| Python 型別覆蓋率 | 待測量 | > 85% | `mypy --html-report core/` |
| Hotspot Score | **Max: 95** (core/legacy_module/old_api.php) | < 80 | Review hotspot.json |

### 安全指標

| 嚴重性 | 當前數量 | 目標數量 | 驗證方式 |
|--------|----------|----------|----------|
| CRITICAL | **0** ✅ | 0 | Semgrep 掃描 |
| HIGH | **0** ✅ | 0 | Semgrep 掃描 |
| MEDIUM | **0** ✅ | <= 3 | Semgrep 掃描 |
| LOW | **0** ✅ | <= 10 | Semgrep 掃描 |

### 架構指標

- **模組邊界清晰**：所有子目錄有明確的 README.md 說明職責
- **依賴方向正確**：services/ 只依賴 core/ 的公開介面
- **測試覆蓋率**：核心模組測試覆蓋率 > 80%
- **文件完整性**：所有公開 API 有 docstring/JSDoc

---

## 7. 檔案與目錄結構（交付視圖）

### 受影響目錄

- `core/` - 整個核心引擎目錄
- `core/unified_integration/`
- `core/mind_matrix/`
- `core/safety_mechanisms/`
- `core/slsa_provenance/`
- `core/contract_service/`

### 結構示意（重構後目標）

```text
core/
├─ README.md                              # 核心引擎總覽
├─ unified_integration/                   # 統一整合層
│  ├─ src/
│  │  ├─ cognitive_processor.py           # 認知處理器主入口
│  │  ├─ service_registry.py              # 服務註冊表
│  │  └─ config_optimizer.py              # 配置優化器
│  ├─ tests/
│  └─ README.md
├─ mind_matrix/                           # 心智矩陣
│  ├─ src/
│  │  ├─ ceo_system.py                    # CEO 執行長系統
│  │  └─ multi_agent_hypergraph.py        # 多代理超圖
│  ├─ tests/
│  └─ README.md
├─ safety_mechanisms/                     # 安全機制
│  ├─ src/
│  │  ├─ circuit_breaker.py               # 斷路器
│  │  ├─ emergency_stop.py                # 緊急停止
│  │  └─ rollback_system.py               # 回滾系統
│  ├─ tests/
│  └─ README.md
├─ slsa_provenance/                       # SLSA 溯源
│  ├─ src/
│  │  ├─ provenance_manager.py            # 證明管理
│  │  └─ signature_verifier.go            # 簽名驗證（Go）
│  ├─ tests/
│  └─ README.md
├─ ai_engines/                            # AI 引擎集合（新增）
│  ├─ decision/                           # 決策引擎
│  │  ├─ __init__.py
│  │  ├─ decision_engine.py
│  │  └─ README.md
│  ├─ hallucination_detection/            # 幻覺偵測
│  │  ├─ __init__.py
│  │  ├─ detector.py
│  │  └─ README.md
│  └─ context_understanding/              # 上下文理解
│     ├─ __init__.py
│     ├─ engine.py
│     └─ README.md
└─ contract_service/                      # 合約服務（考慮遷移）
   └─ contracts-L1/
      └─ contracts/                       # TypeScript Contract Service
```

### 關鍵檔案說明

- **cognitive_processor.py** - 四層認知架構的核心實作（感知→推理→執行→證明）
- **service_registry.py** - 服務發現、健康監控、依賴解析的統一入口
- **ceo_system.py** - CEO 執行長決策系統，整合決策引擎與幻覺偵測
- **circuit_breaker.py** - 保護機制，防止級聯失效
- **provenance_manager.py** - SLSA 證明的生成、管理與驗證

---

## 8. 集成對齊（Integration Alignment）

### 上游依賴

本 cluster 依賴以下基礎設施：

| 服務 | 介面類型 | 用途 |
|------|----------|------|
| `governance/schemas` | JSON Schema | 型別定義與驗證 |
| `shared/utils` | Python/TypeScript Module | 共用工具函式 |
| External: Sigstore | HTTP API | 簽名與驗證 |

### 下游使用者

本 cluster 被以下服務使用：

| 服務 | 介面類型 | 使用方式 |
|------|----------|----------|
| `services/agents` | Python Import | 呼叫 AI 引擎與認知處理 |
| `services/mcp` | gRPC/REST | 透過 Contract Service 互動 |
| `apps/web` | REST API | 前端呼叫分析與決策功能 |
| `automation/*` | Direct Import | 自動化系統使用核心能力 |

### 集成步驟摘要

重構需按以下順序進行：

1. **Phase 1**：整理公開介面（不破壞現有 API）
   - 確定哪些是公開 API，哪些是內部實作
   - 建立 `core/__init__.py` 明確 export
   - 部署到測試環境並執行整合測試

2. **Phase 2**：內部重構（保持 API 相容）
   - 重組目錄結構
   - 遷移 JavaScript 到 TypeScript
   - 重構高複雜度模組

3. **Phase 3**：更新使用方（漸進式）
   - 通知下游服務新介面位置
   - 提供遷移指南
   - 設定 deprecation timeline

### 回滾策略

若重構失敗，按以下步驟回滾：

1. **Feature Flag 切換**：
   - `ENABLE_NEW_CORE_STRUCTURE=false`
   - 使用環境變數控制載入舊/新模組

2. **Git 回滾**：
   - 識別穩定版本 tag：`git tag -l "core-stable-*"`
   - 回滾：`git checkout {stable_tag}`

3. **通知下游**：
   - 在 Slack 通知所有依賴 core/ 的團隊
   - 更新 status page

4. **驗證**：
   - 執行完整的整合測試套件
   - 確認所有下游服務正常運作

### 風險管控

- **Branch 策略**：使用 feature branch，PR review 後合併
- **Feature Flag**：所有 breaking changes 需有 feature flag 保護
- **段階部署**：先部署到 dev → staging → production
- **監控告警**：設定關鍵指標告警（error rate, API latency）

---

## 9. Proposer/Critic AI 工作流程整合

### 9.1 工作流程概述

根據 `docs/refactor_playbooks/03_refactor/meta/PROPOSER_CRITIC_WORKFLOW.md`，本重構採用雙角色 AI 驗證流程：

```text
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

### 9.2 Proposer 角色實施

**職責**: 產生具體重構方案與 patch

**輸入資料**:

1. `docs/refactor_playbooks/01_deconstruction/core/core__architecture_deconstruction.md` - 解構分析
2. `docs/refactor_playbooks/02_integration/core/core__architecture_integration.md` - 集成設計
3. `config/system-module-map.yaml` - 模組定義與約束
4. `apps/web/public/data/hotspot.json` - 高風險檔案
5. 本重構劇本 - 執行計畫

**輸出**:

1. **架構設計方案**
   - 新的目錄結構（已在 Integration 定義）
   - API 邊界定義（已在 Integration 定義）
   - 模組依賴關係圖

2. **具體 Patch**
   - 檔案移動計畫（Phase A-G）
   - 程式碼修改（重構、型別註解）
   - Import 路徑更新（shim layer）

3. **理由說明**
   - 為什麼這樣改？→ 基於解構分析的問題
   - 解決了哪些問題？→ 語言純度、架構清晰、循環依賴
   - 影響評估 → 下游服務影響矩陣（見 Integration Section 5.3）

**實施範例** (Phase A: 基礎建設):

```yaml
proposer_output:
  phase: "Phase A - 基礎建設"
  tasks:
    - task_id: "A1"
      action: "建立目錄結構"
      commands:
        - "mkdir -p core/{interfaces,ai_engines,governance,quality_assurance}"
        - "mkdir -p core/unified_integration/{configuration,orchestration}"
      rationale: "建立新架構骨架，為後續遷移做準備"
      
    - task_id: "A2"
      action: "建立介面定義"
      files:
        - path: "core/interfaces/service_interface.py"
          content: |
            # 見 Integration Section 4.2
            from abc import ABC, abstractmethod
            ...
      rationale: "定義契約層，打破循環依賴"
      
    - task_id: "A3"
      action: "建立 README 文檔"
      files:
        - path: "core/ai_engines/README.md"
          content: "AI Engines 模組說明..."
      rationale: "文檔先行，幫助團隊理解新結構"
```

### 9.3 Critic 角色實施

**職責**: 用架構規則嚴格審查 Proposer 的方案

**審查依據**:

1. `config/system-module-map.yaml` → `refactor.architecture_constraints`
2. `automation/architecture-skeletons/` → 骨架規則
3. `governance/policies/` → 治理政策
4. Anti-pattern 清單（來自解構分析）

**審查項目**:

#### 1. 架構約束檢查

```yaml
critic_checklist:
  architecture_constraints:
    - question: "依賴方向是否正確？"
      check: "core/* 是否依賴 apps/** 或 services/**"
      expected: "❌ MUST NOT"
      status: "✅ PASS"
      evidence: "grep -r 'from apps\\.' core/ 返回空"
      
    - question: "是否違反模組邊界？"
      check: "是否跨 domain 直接 import？"
      expected: "透過 interfaces/ 或公開 API"
      status: "✅ PASS"
      evidence: "所有跨模組依賴都透過 core/interfaces/"
      
    - question: "是否引入新的循環依賴？"
      check: "tools/dependency-graph.py --check-cycles"
      expected: "0 cycles"
      status: "✅ PASS"
      evidence: "執行結果：No cycles detected"
```

#### 2. 語言策略檢查

```yaml
language_strategy:
  - question: "是否使用 preferred languages？"
    check: "新檔案是否為 Python/TypeScript"
    expected: "100%"
    status: "✅ PASS"
    evidence: "所有新檔案均為 .py 或 .ts"
    
  - question: "是否引入 banned languages？"
    check: "是否有 PHP/Perl/Ruby 檔案"
    expected: "0 檔案"
    status: "✅ PASS"
    evidence: "find core/ -name '*.php' -o -name '*.pl' -o -name '*.rb' 返回空"
    
  - question: "語言混用是否減少？"
    check: "JavaScript 檔案數量"
    baseline: 7
    target: 0
    status: "🟡 IN_PROGRESS"
    evidence: "Phase E 將遷移所有 .js → .ts"
```

#### 3. 品質指標檢查

```yaml
quality_metrics:
  - metric: "複雜度是否降低？"
    baseline: 8.5
    target: "≤ 8.0"
    status: "🟡 IN_PROGRESS"
    evidence: "cognitive_processor.py 複雜度 18 → 需重構至 ≤ 15"
    
  - metric: "測試覆蓋率是否維持/提升？"
    baseline: 55%
    target: "≥ 80%"
    status: "🟡 IN_PROGRESS"
    evidence: "Phase C-D 將補充測試，目標達 80%"
    
  - metric: "是否引入新的安全問題？"
    check: "semgrep --config auto core/"
    expected: "HIGH=0"
    status: "✅ PASS"
    evidence: "Semgrep 掃描：0 HIGH, 0 MEDIUM, 0 LOW"
```

#### 4. 可維護性檢查

```yaml
maintainability:
  - question: "命名是否清晰？"
    check: "目錄與檔案命名符合慣例"
    expected: "snake_case for Python, lowercase for dirs"
    status: "✅ PASS"
    
  - question: "是否符合專案風格？"
    check: "black --check core/ && mypy core/"
    expected: "0 violations"
    status: "🟡 IN_PROGRESS"
    evidence: "mypy 檢查尚未全部通過（型別註解補充中）"
    
  - question: "是否有充分文檔？"
    check: "每個新模組/類別有 docstring"
    expected: "100% coverage"
    status: "✅ PASS"
    evidence: "所有公開 API 均有 docstring"
```

### 9.4 Proposer/Critic 循環範例

**Iteration 1**: Proposer 提議 → Critic 發現問題

```yaml
proposer_iteration_1:
  proposal: "移動 ai_decision_engine.py 到 ai_engines/decision/"
  patch: |
    git mv core/ai_decision_engine.py core/ai_engines/decision/engine.py

critic_feedback:
  status: "❌ REJECT"
  issues:
    - issue_id: "C1"
      severity: "HIGH"
      description: "未建立 shim layer，會破壞下游服務"
      evidence: "grep -r 'from core.ai_decision_engine' services/agents/"
      required_fix: "在舊位置建立 shim 並發出 deprecation warning"
    
    - issue_id: "C2"
      severity: "MEDIUM"
      description: "缺少單元測試"
      evidence: "core/ai_engines/decision/tests/ 目錄不存在"
      required_fix: "移動對應測試或建立新測試"
```

**Iteration 2**: Proposer 修正 → Critic 通過

```yaml
proposer_iteration_2:
  proposal: "移動 ai_decision_engine.py + 建立 shim + 測試"
  patches:
    - action: "move_with_tests"
      commands:
        - "git mv core/ai_decision_engine.py core/ai_engines/decision/engine.py"
        - "git mv tests/core/test_ai_decision_engine.py tests/core/ai_engines/decision/test_engine.py"
    
    - action: "create_shim"
      file: "core/ai_decision_engine.py"
      content: |
        import warnings
        from core.ai_engines.decision import DecisionEngine
        
        warnings.warn(
            "core.ai_decision_engine is deprecated. Use core.ai_engines.decision instead.",
            DeprecationWarning, stacklevel=2
        )
        __all__ = ['DecisionEngine']
    
    - action: "update_imports"
      affected_files:
        - "core/unified_integration/cognitive_processor.py"
      changes: "from core.ai_engines.decision import DecisionEngine"

critic_feedback:
  status: "✅ APPROVED"
  validation:
    - check: "Shim layer exists"
      result: "✅ PASS"
    - check: "Tests moved"
      result: "✅ PASS"
    - check: "Imports updated"
      result: "✅ PASS"
  proceed_to: "CI_VALIDATION"
```

### 9.5 自動化工具支援

**依賴掃描**:

```bash
# 找出所有依賴舊路徑的檔案
tools/scan-dependencies.sh core.ai_decision_engine

# 輸出:
# services/agents/decision_agent.py:15
# automation/intelligent/analyzer.py:22
```

**批次重構**:

```bash
# 自動更新 import 路徑
tools/batch-refactor.py \
  --from "core.ai_decision_engine" \
  --to "core.ai_engines.decision" \
  --target "services/" "automation/"
```

**Critic 自動檢查**:

```bash
# 執行完整 Critic 檢查
tools/critic-check.py \
  --phase "Phase B" \
  --config config/system-module-map.yaml \
  --output critic-report.yaml
```

---

## 10. 質量度量追蹤

### 10.1 Before/After 比對表

| 指標 | 重構前 (v2.5) | 目標值 (v3.0) | 當前進度 | 狀態 |
|------|---------------|---------------|----------|------|
| **語言治理** |||||
| JavaScript 檔案數 | 7 | 0 | 7 (0%) | 🔴 未開始 |
| Python 型別覆蓋率 | 50% | 85% | 50% (0%) | 🔴 未開始 |
| 語言違規總數 | 7 | 0 | 7 (0%) | 🔴 未開始 |
| **安全指標** |||||
| Semgrep HIGH | 0 | 0 | 0 (100%) | ✅ 達標 |
| Semgrep MEDIUM | 0 | ≤3 | 0 (100%) | ✅ 達標 |
| Semgrep LOW | 0 | ≤10 | 0 (100%) | ✅ 達標 |
| **架構指標** |||||
| 頂層散落檔案 | 11 | 0 | 11 (0%) | 🔴 未開始 |
| 循環依賴數 | 1 | 0 | 1 (0%) | 🔴 未開始 |
| API 邊界明確度 | 30% | 100% | 30% (0%) | 🔴 未開始 |
| **複雜度指標** |||||
| 平均 CC | 8.5 | ≤8.0 | 8.5 (0%) | 🔴 未開始 |
| Max CC (單函式) | 22 | ≤15 | 22 (0%) | 🔴 未開始 |
| Hotspot 檔案數 (>80) | 3 | 0 | 3 (0%) | 🔴 未開始 |
| **測試指標** |||||
| 整體覆蓋率 | 55% | 80% | 55% (0%) | 🔴 未開始 |
| unified_integration/ | 55% | 80% | 55% (0%) | 🔴 未開始 |
| safety_mechanisms/ | 70% | 85% | 70% (21%) | 🟡 部分達標 |
| island_ai_runtime/ | 50% | 75% | 50% (0%) | 🔴 未開始 |
| 頂層 AI engines | 30% | 70% | 30% (0%) | 🔴 未開始 |

**圖例**:

- ✅ 達標: 已達成目標
- 🟢 良好: 進度 ≥ 80%
- 🟡 進行中: 進度 50-79%
- 🟠 落後: 進度 20-49%
- 🔴 未開始: 進度 < 20%

### 10.2 階段性里程碑

| Phase | 目標 | 預期完成日期 | 關鍵指標 | 狀態 |
|-------|------|-------------|----------|------|
| **Phase A** | 基礎建設 | Week 1 | 目錄結構+介面定義完成 | 🔴 未開始 |
| **Phase B** | 頂層檔案遷移 | Week 2 | 11 個檔案遷移完成 | 🔴 未開始 |
| **Phase C** | unified_integration 重組 | Week 2 | 子模組化+複雜度降低 | 🔴 未開始 |
| **Phase D** | Runtime 改進 | Week 3 | 循環依賴打破+測試 ≥75% | 🔴 未開始 |
| **Phase E** | TypeScript 遷移 | Week 3 | JS檔案=0 | 🔴 未開始 |
| **Phase F** | 公開 API 定義 | Week 4 | API 文檔+遷移指南 | 🔴 未開始 |
| **Phase G** | 驗證與監控 | Week 4 | 所有指標達標 | 🔴 未開始 |

### 10.3 實時追蹤儀表板

**命令**:

```bash
# 生成實時進度報告
tools/refactor-dashboard.py \
  --cluster core/architecture-stability \
  --output docs/refactor_playbooks/_dashboard/core-progress.html
```

**儀表板內容**:

- 📊 指標達成率（視覺化進度條）
- 📈 趨勢圖（每日指標變化）
- 🎯 里程碑時間軸
- ⚠️ 風險警報（偏離計畫的指標）
- 📝 變更日誌（每個 Phase 的變更摘要）

### 10.4 持續監控

**CI 整合**:

```yaml
# .github/workflows/refactor-quality-check.yml
name: Refactor Quality Check

on:
  push:
    branches:
      - 'refactor/core-architecture-*'
  pull_request:
    paths:
      - 'core/**'

jobs:
  quality-metrics:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: 測試覆蓋率檢查
        run: |
          pytest core/ --cov=core --cov-report=json
          python tools/check-coverage-target.py --target 80 --current coverage.json
      
      - name: 複雜度檢查
        run: |
          radon cc core/ -a -nb --json > complexity.json
          python tools/check-complexity-target.py --target 8.0 --current complexity.json
      
      - name: 語言治理檢查
        run: |
          npm run governance:check
          python tools/check-language-violations.py --max 0
      
      - name: 架構約束檢查
        run: |
          python tools/validate-architecture-constraints.py \
            --config config/system-module-map.yaml \
            --cluster core/architecture-stability
      
      - name: 更新進度儀表板
        if: github.ref == 'refs/heads/main'
        run: |
          python tools/refactor-dashboard.py --cluster core/architecture-stability
          git add docs/refactor_playbooks/_dashboard/
          git commit -m "Update refactor progress dashboard"
          git push
```

---

## 11. 驗收條件與檢查清單

### 11.1 Phase 級別驗收

#### Phase A 驗收清單

- [ ] **目錄結構**
  - [ ] `core/interfaces/` 目錄建立
  - [ ] `core/ai_engines/` 目錄建立
  - [ ] `core/governance/` 目錄建立
  - [ ] `core/quality_assurance/` 目錄建立
  - [ ] `core/unified_integration/{configuration,orchestration}/` 建立

- [ ] **介面定義**
  - [ ] `core/interfaces/service_interface.py` 完成
  - [ ] `core/interfaces/processor_interface.py` 完成
  - [ ] `core/interfaces/runtime_interface.py` 完成
  - [ ] `core/interfaces/safety_interface.py` 完成
  - [ ] 所有介面通過 `mypy --strict` 檢查

- [ ] **文檔**
  - [ ] `core/README.md` 更新
  - [ ] `core/ai_engines/README.md` 建立
  - [ ] `core/governance/README.md` 建立
  - [ ] `core/quality_assurance/README.md` 建立

- [ ] **驗證**
  - [ ] CI 通過
  - [ ] 無破壞性變更
  - [ ] Git tag: `phase-a-complete`

#### Phase B 驗收清單

- [ ] **檔案遷移** (11 個)
  - [ ] `auto_bug_detector.py` → `quality_assurance/bug_detector.py`
  - [ ] `hallucination_detector.py` → `ai_engines/hallucination_detection/detector.py`
  - [ ] `context_understanding_engine.py` → `ai_engines/context_understanding/engine.py`
  - [ ] `ai_decision_engine.py` → `ai_engines/decision/engine.py`
  - [ ] `autonomous_trust_engine.py` → `governance/trust_engine.py`
  - [ ] `auto_governance_hub.py` → `governance/hub.py`
  - [ ] (其餘 5 個檔案...)

- [ ] **Shim Layer**
  - [ ] 所有舊路徑保留 shim
  - [ ] Deprecation warning 正常運作
  - [ ] 下游服務無破壞性影響

- [ ] **測試**
  - [ ] 所有遷移檔案有對應測試
  - [ ] 測試覆蓋率 ≥ 70%
  - [ ] 回歸測試通過

- [ ] **驗證**
  - [ ] `tools/scan-dependencies.sh` 確認無遺漏
  - [ ] CI 通過
  - [ ] Git tag: `phase-b-complete`

#### Phase C-G 驗收清單

*(類似結構，省略詳細內容)*

### 11.2 全局驗收條件

**必須滿足** (MUST):

1. **語言治理**
   - ✅ JavaScript 檔案 = 0
   - ✅ Python 型別覆蓋率 ≥ 85%
   - ✅ 無 banned languages

2. **安全指標**
   - ✅ Semgrep HIGH = 0
   - ✅ Semgrep MEDIUM ≤ 3
   - ✅ 無硬編碼密鑰

3. **架構合規**
   - ✅ 無循環依賴
   - ✅ 依賴方向正確（core 不依賴 services/apps）
   - ✅ 公開 API 明確定義

4. **品質指標**
   - ✅ 測試覆蓋率 ≥ 80%
   - ✅ 平均複雜度 ≤ 8.0
   - ✅ Max 函式複雜度 ≤ 15

5. **文檔完整性**
   - ✅ 所有公開 API 有 docstring
   - ✅ 所有模組有 README.md
   - ✅ 遷移指南完成

**建議滿足** (SHOULD):

1. **效能基準**
   - 🟡 效能下降 ≤ 10%
   - 🟡 記憶體增加 ≤ 10%

2. **可觀測性**
   - 🟡 關鍵路徑有 tracing
   - 🟡 監控指標完整

### 11.3 最終驗收流程

```text
1. Self-Check（開發者）
   ↓
2. Automated Checks（CI）
   ├─ 語言治理掃描
   ├─ Semgrep 安全掃描
   ├─ 複雜度分析
   ├─ 測試覆蓋率
   ├─ 架構約束驗證
   └─ 效能基準測試
   ↓
3. Code Review（團隊）
   ├─ 架構設計評審
   ├─ 程式碼品質檢視
   └─ 文檔完整性確認
   ↓
4. Staging Deployment
   ├─ 整合測試
   ├─ 效能測試
   └─ 48 小時穩定性觀察
   ↓
5. Final Approval
   ├─ Tech Lead 簽核
   ├─ Security Team 簽核
   └─ QA Team 簽核
   ↓
6. Production Deployment
   ├─ 漸進式部署
   ├─ 監控告警
   └─ Rollback 準備
```

### 11.4 驗收報告範本

```markdown
# Core Architecture Refactor 驗收報告

**日期**: 2025-XX-XX  
**版本**: v3.0.0  
**執行者**: [Name]  
**審核者**: [Name]

## 執行摘要

本次重構完成 core/architecture-stability cluster 的架構優化，達成以下目標：
- ✅ 語言純度：JavaScript 檔案從 7 → 0
- ✅ 架構清晰：頂層檔案從 11 → 0（重組至子目錄）
- ✅ 循環依賴：從 1 → 0（透過 interfaces/ 打破）
- ✅ 測試覆蓋率：55% → 82%

## 指標達成情況

| 類別 | 指標 | 目標 | 達成 | 狀態 |
|------|------|------|------|------|
| 語言治理 | JS 檔案數 | 0 | 0 | ✅ |
| 語言治理 | Python 型別覆蓋率 | ≥85% | 87% | ✅ |
| 安全 | Semgrep HIGH | 0 | 0 | ✅ |
| 架構 | 循環依賴 | 0 | 0 | ✅ |
| 複雜度 | 平均 CC | ≤8.0 | 7.8 | ✅ |
| 測試 | 覆蓋率 | ≥80% | 82% | ✅ |

## 驗收結論

✅ **通過驗收**

所有必要條件均已滿足，建議進行 Production 部署。

## 遺留問題

無

## 簽核

- Tech Lead: __________ (Date: ______)
- Security: __________ (Date: ______)
- QA: __________ (Date: ______)
```

---

## 12. 治理狀態與索引更新

### 12.1 Governance Status

**當前狀態**: `in_progress`

**狀態定義**:

- `draft`: 劇本草稿階段
- `in_progress`: 正在執行重構
- `completed`: 重構完成並驗收通過
- `archived`: 已歸檔（不再維護）

**更新**:

```yaml
# 在 03_refactor/index.yaml 中更新
clusters:
  - cluster_id: "core/architecture-stability"
    playbook: "core/core__architecture_refactor.md"
    governance_status: "in_progress"  # 更新此欄位
    last_updated: "2025-12-07"
    priority: "P0"
    progress:
      current_phase: "Phase A"
      completion_pct: 5
      blocking_issues: []
```

### 12.2 索引交叉引用

**向後引用**:

- ← `01_deconstruction/core/core__architecture_deconstruction.md`
  - 依賴：解構分析提供問題清單
- ← `02_integration/core/core__architecture_integration.md`
  - 依賴：集成設計提供目標架構

**向前引用**:

- → `config/system-module-map.yaml`
  - 更新：完成後更新模組定義
- → `docs/api/core-v3.md`
  - 建立：新 API 文檔
- → `docs/migration/v2-to-v3.md`
  - 建立：遷移指南

### 12.3 相關文檔

**必讀**:

1. `docs/refactor_playbooks/NEXT_STEPS_PLAN.md` - 整體計畫
2. `docs/refactor_playbooks/03_refactor/meta/PROPOSER_CRITIC_WORKFLOW.md` - 工作流程
3. `docs/refactor_playbooks/03_refactor/templates/REFRACTOR_PLAYBOOK_TEMPLATE.md` - 範本

**參考**:

1. `.github/copilot-instructions.md` - 技術指南
2. `.github/AI-BEHAVIOR-CONTRACT.md` - 行為準則
3. `config/system-module-map.yaml` - 模組定義

---

**狀態**: 🟡 執行中（Phase 1 of 4: 解構→集成→重構→驗證）  
**最後更新**: 2025-12-07  
**下一步**:

1. ✅ 解構劇本完成
2. ✅ 集成劇本完成
3. 🔄 本重構劇本強化完成
4. 🔜 開始執行 Phase A（基礎建設）

---

*此重構劇本整合了 Proposer/Critic 工作流程、質量度量追蹤、與全面的驗收條件，為 core/architecture-stability cluster 重構提供具體執行指導。*
