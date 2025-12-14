# {{CLUSTER_ID}} 重構劇本（Refactor Playbook）

- Cluster ID：`{{CLUSTER_ID}}`             # 例如：core/architecture-stability
- 對應目錄：`{{INVOLVED_DIRS}}`           # 例如：core/unified_integration/, core/mind_matrix/
- 對應集成劇本：
  - `docs/refactor_playbooks/02_integration/{{INTEGRATION_FILE}}`

---

## 1. Cluster 概覽

- 角色說明：
  - 本 cluster 在 Unmanned Island System 中的責任與邊界。
- 主要語言組成與健康狀態：
  - 現在使用的語言（TS / Py / Go / C++ ...）與治理狀況簡短描述。

---

## 2. 問題盤點（來源：語言治理 / Hotspot / Semgrep / Flow）

- 語言治理問題彙總：
  - 來自 `language-governance-report.md` 的主要違規類型。
- Hotspot 檔案：
  - 來自 `hotspot.json`，依分數排序的高風險檔案列表。
- Semgrep 安全問題：
  - 依 severity (HIGH → MEDIUM → LOW) 簡要列出。
- Migration Flow 觀察：
  - 本 cluster 在 `migration-flow.json` 中是語言違規的「來源」還是「接收端」。

---

## 3. 語言與結構重構策略（Language & Architecture Optimization Strategy）

> **⚠️ REQUIRED**: 本區塊必須遵守 `.github/AI-BEHAVIOR-CONTRACT.md` Section 9 的「Global Optimization First」原則。
> 所有提案必須包含：**Global Optimization View → Local Plan → Self-Check**

### 3.1 全局優化目標（Global Optimization Targets）

**本 Cluster 的優化目標：**
- **語言純度**：將本 cluster 從混合 {{CURRENT_LANGS}} 優化為 {{TARGET_LANGS}}
  - 當前狀態：{{CURRENT_LANG_DISTRIBUTION}}
  - 目標狀態：{{TARGET_LANG_DISTRIBUTION}}
  - 預期改善：語言違規 {{BASELINE_VIOLATIONS}} → {{TARGET_VIOLATIONS}}

- **安全態勢**：消除所有 HIGH severity 安全問題
  - 當前狀態：{{SEMGREP_HIGH_COUNT}} HIGH, {{SEMGREP_MEDIUM_COUNT}} MEDIUM
  - 目標狀態：0 HIGH, ≤{{TARGET_MEDIUM_COUNT}} MEDIUM
  - 預期改善：安全分數提升 {{SECURITY_IMPROVEMENT}}%

- **架構合規性**：糾正所有依賴方向違規
  - 當前狀態：{{ARCH_VIOLATIONS_COUNT}} 個架構違規
  - 目標狀態：0 個違規
  - 預期改善：100% 架構合規

**系統級硬約束（Hard Constraints）：**
1. **MUST NOT** 創建新的反向依賴（apps → core, services → apps）
2. **MUST NOT** 引入禁用語言（PHP, Perl）
3. **MUST** 維持測試覆蓋率 ≥ 當前值 - 2%
4. **MUST** 遵守 skeleton 規則定義在 `config/system-module-map.yaml`
5. **MUST** 確保 Semgrep HIGH findings = 0 after refactor

### 3.2 語言策略（Language Strategy）

#### 3.2.1 保留語言（Languages to Keep）

**{{PRIMARY_LANG}}**（主要語言）：
- **用途**：所有業務邏輯、API 實現、核心功能
- **當前文件數**：{{PRIMARY_CURRENT_COUNT}} files ({{PRIMARY_CURRENT_PCT}}%)
- **目標文件數**：{{PRIMARY_TARGET_COUNT}} files ({{PRIMARY_TARGET_PCT}}%)
- **淨變化**：{{PRIMARY_NET_CHANGE}} files
- **理由**：類型安全、工具鏈成熟、團隊熟悉度高

**{{SECONDARY_LANG}}**（次要語言）：
- **用途**：{{SECONDARY_USE_CASE}}（如：工具腳本、AI pipeline、數據處理）
- **當前文件數**：{{SECONDARY_CURRENT_COUNT}} files ({{SECONDARY_CURRENT_PCT}}%)
- **目標文件數**：{{SECONDARY_TARGET_COUNT}} files ({{SECONDARY_TARGET_PCT}}%)
- **淨變化**：{{SECONDARY_NET_CHANGE}} files
- **理由**：特定領域優勢、生態系統支持

#### 3.2.2 應遷出的語言（Languages to Migrate Out）

**{{MIGRATE_LANG_1}}** → 遷移至 {{TARGET_LANG_1}}：
- **當前文件數**：{{MIGRATE_1_CURRENT_COUNT}} files ({{MIGRATE_1_CURRENT_PCT}}%)
- **目標文件數**：0 files (0%)
- **淨變化**：{{MIGRATE_1_NET_CHANGE}} files
- **優先級**：P0（原因：{{MIGRATE_1_REASON}}）
- **具體檔案清單**：
  - `{{FILE_1}}` → {{ACTION_1}}
  - `{{FILE_2}}` → {{ACTION_2}}
  - ...

**{{MIGRATE_LANG_2}}** → 遷移至 {{TARGET_LANG_2}} 或移除：
- **當前文件數**：{{MIGRATE_2_CURRENT_COUNT}} files ({{MIGRATE_2_CURRENT_PCT}}%)
- **目標文件數**：{{MIGRATE_2_TARGET_COUNT}} files ({{MIGRATE_2_TARGET_PCT}}%)
- **淨變化**：{{MIGRATE_2_NET_CHANGE}} files
- **優先級**：P1（原因：{{MIGRATE_2_REASON}}）
- **例外保留**：{{EXCEPTION_FILES}}（原因：{{EXCEPTION_REASON}}）

### 3.3 架構邊界優化（Architecture Boundary Optimization）

#### 3.3.1 當前問題診斷

**檢測到的反向依賴（Reverse Dependencies）：**
1. `{{VIOLATING_PATH_1}}` 直接 import `{{VIOLATED_MODULE_1}}`
   - **違反**：apps → core 反向依賴
   - **風險等級**：HIGH
   - **修復優先級**：P0
   - **修復方案**：{{SOLUTION_1}}

2. `{{VIOLATING_PATH_2}}` 跳過邊界直接調用 `{{VIOLATED_MODULE_2}}`
   - **違反**：services 內部繞過 API 邊界
   - **風險等級**：MEDIUM
   - **修復優先級**：P1
   - **修復方案**：{{SOLUTION_2}}

**檢測到的循環依賴（Circular Dependencies）：**
- ❌ `{{MODULE_A}} ↔ {{MODULE_B}}` (circular)
  - **解決方案**：引入 `{{SHARED_INTERFACE_MODULE}}` 作為共享契約層
  - **實施步驟**：{{CIRCULAR_FIX_STEPS}}

#### 3.3.2 調整後的依賴方向（Target Dependency Flow）

```text
infrastructure/ (底層基礎設施)
  ↑ ✅ 無依賴
  ↓ ❌ MUST NOT depend on: any application layer

core/ (核心業務邏輯)
  ↑ ✅ depends on: infrastructure/
  ↓ ❌ MUST NOT depend on: services/, apps/

services/ (服務層/API 層)
  ↑ ✅ depends on: core/, infrastructure/
  ↓ ❌ MUST NOT depend on: apps/

apps/ (應用層/前端)
  ↑ ✅ depends on: services/, infrastructure/
  ↓ ❌ MUST NOT depend on: core/ (必須通過 services/)

automation/ (自動化/工具)
  ↑ ✅ depends on: infrastructure/, core/safety_mechanisms/
  ↓ ❌ 獨立運行，避免與 apps/services 耦合
```

#### 3.3.3 邊界修復計畫（Boundary Fix Plan）

**P0 修復項目：**
- 移除 `{{VIOLATION_1}}` (預期改善：-1 架構違規)
- 修復 `{{VIOLATION_2}}` (預期改善：-1 架構違規)

**P1 加固項目：**
- 添加 `services/api/` facade 層供 apps 使用
- 實施 dependency linter 規則防止未來違規
- 更新 `config/system-module-map.yaml` 約束定義

**P2 監控項目：**
- 設置 CI 自動檢測反向依賴
- 建立架構健康儀表板
- 定期 review 依賴圖變化

### 3.4 避免循環依賴與橫向耦合（Prevent Cycles & Lateral Coupling）

**策略：**
1. **契約層分離**：引入 `interfaces/` 或 `contracts/` 目錄存放共享定義
2. **Dependency Injection**：使用 DI 容器管理跨模組依賴
3. **Event-Driven**：通過事件總線解耦強依賴
4. **API Gateway**：services 間通訊必須通過定義的 API contract

**檢查清單：**
- [ ] 所有模組間通訊通過明確定義的介面
- [ ] 無直接檔案系統路徑引用（使用模組解析）
- [ ] 事件發布者不依賴訂閱者
- [ ] 使用 tools/dependency-graph.py 定期驗證

### 3.5 全局影響評估（Global Impact Assessment）

**對系統級指標的預期影響：**

| Metric | Baseline | Target | P0 Impact | P1 Impact | P2 Impact | Net Change |
|--------|----------|--------|-----------|-----------|-----------|------------|
| Language Violations | {{LV_BASELINE}} | {{LV_TARGET}} | {{LV_P0}} | {{LV_P1}} | {{LV_P2}} | {{LV_NET}} |
| Semgrep HIGH | {{SH_BASELINE}} | 0 | {{SH_P0}} | {{SH_P1}} | {{SH_P2}} | {{SH_NET}} |
| Semgrep MEDIUM | {{SM_BASELINE}} | {{SM_TARGET}} | {{SM_P0}} | {{SM_P1}} | {{SM_P2}} | {{SM_NET}} |
| Architecture Violations | {{AV_BASELINE}} | 0 | {{AV_P0}} | {{AV_P1}} | {{AV_P2}} | {{AV_NET}} |
| Test Coverage | {{TC_BASELINE}}% | ≥{{TC_TARGET}}% | {{TC_P0}}% | {{TC_P1}}% | {{TC_P2}}% | {{TC_NET}}% |
| Cyclomatic Complexity (Avg) | {{CC_BASELINE}} | {{CC_TARGET}} | {{CC_P0}} | {{CC_P1}} | {{CC_P2}} | {{CC_NET}} |

**Net Assessment**（淨評估）：
- ✅ **POSITIVE IMPACT**: 所有步驟都朝向全局優化目標前進
- ⚠️ **ACCEPTABLE TRADEOFFS**: {{TRADEOFF_DESCRIPTION}}
- ❌ **CONCERNS**: {{CONCERN_DESCRIPTION}}（if any）

### 3.6 與集成方案的對齊（Integration Alignment）

- 必須符合 `02_integration/{{INTEGRATION_FILE}}` 中定義的邊界與 API 約束
- API 契約版本：{{API_VERSION}}
- 兼容性要求：{{COMPATIBILITY_REQUIREMENTS}}
- 集成測試覆蓋：{{INTEGRATION_TEST_COVERAGE}}

### 3.7 Self-Check（自我檢查）

**Q1: 是否違反任何架構骨架規則？**
- **答**: {{SELF_CHECK_ARCH_ANSWER}}
- **證據**: {{SELF_CHECK_ARCH_EVIDENCE}}

**Q2: 是否創建新的語言依賴反向問題？**
- **答**: {{SELF_CHECK_LANG_DEP_ANSWER}}
- **證據**: {{SELF_CHECK_LANG_DEP_EVIDENCE}}

**Q3: 是否只是將問題從一個模組推到另一個模組？**
- **答**: {{SELF_CHECK_PROBLEM_SHIFT_ANSWER}}
- **證據**: {{SELF_CHECK_PROBLEM_SHIFT_EVIDENCE}}

**Q4: 局部變更如何影響全局指標？**
- **正面影響**: {{POSITIVE_IMPACTS}}
- **中性影響**: {{NEUTRAL_IMPACTS}}
- **負面影響**: {{NEGATIVE_IMPACTS}}
- **淨評估**: {{NET_ASSESSMENT}}

---

### 3.8 架構約束（Architecture Invariants）

**來源**：`config/system-module-map.yaml` 中對應 module 的 `refactor.architecture_constraints`

- **允許依賴方向**：
  - 本 cluster 可以依賴哪些 domain？
  - 例如：core → infrastructure ✅，core → apps ❌
  
- **禁止依賴**：
  - 明確列出不可 import / require 的路徑模式
  - 例如：禁止 `core/` 直接 import `apps/**`
  
- **架構骨架規則**：
  - 必須遵守的 skeleton 規則（從 `automation/architecture-skeletons/`）
  - 例如：`architecture-stability`, `api-governance`, `security-observability`
  
- **語言策略**：
  - Preferred languages: TypeScript, Python, Go
  - Banned languages: PHP, Perl, Ruby
  
**驗證方式**：
- 使用 `tools/validate-architecture-constraints.py` 檢查
- CI 中必須通過架構約束檢查才能 merge

---

## 4. 分級重構計畫（P0 / P1 / P2）

### P0（24–48 小時內必須處理）

- 目標：清掉最高風險、阻塞 CI 的問題。
- 行動項目（檔案層級）：
  - `path/to/file1` — 動作（刪除 / 改寫為 TS / 移動到 X）
  - ...
- 驗收條件：
  - 語言治理違規數從 X 降到 Y 以下。
  - Semgrep HIGH severity = 0。

### P1（一週內完成）

- 目標：清晰化架構邊界與語言層級。
- 行動項目：
  - ...

### P2（持續重構）

- 目標：技術債清理與最佳化。
- 行動項目：
  - ...

---

## 5. Auto-Fix Bot 可以處理的項目

- 適合 Auto-Fix 的變更：
  - 型別註解補強
  - import/路徑修正
  - 明確 forbidden 語言 → stub / adapter
- 必須人工審查的變更：
  - 影響核心業務邏輯
  - 變更跨服務的 API 合約
  - 安全邊界相關的邏輯

---

## 6. 驗收條件與成功指標

### 6.1 重構成功指標（Refactor Success Metrics）

**來源**：`config/system-module-map.yaml` 中對應 module 的 `refactor.quality_thresholds`

**Before/After 比對必須滿足**：

| 指標 | 重構前 | 目標值 | 驗證方式 |
|------|--------|--------|----------|
| 語言治理違規數 | {{BEFORE_VIOLATIONS}} | ≤ {{MAX_VIOLATIONS}} | `language-governance-report.md` |
| Semgrep HIGH severity | {{BEFORE_HIGH}} | = 0 | `semgrep-report.json` |
| Semgrep MEDIUM severity | {{BEFORE_MEDIUM}} | ≤ {{MAX_MEDIUM}} | `semgrep-report.json` |
| 平均 Cyclomatic Complexity | {{BEFORE_CC}} | ≤ {{MAX_CC}} | CodeQL / 靜態分析 |
| 測試覆蓋率 | {{BEFORE_COV}}% | ≥ {{MIN_COV}}% | Jest / pytest coverage |
| Hotspot 檔案數 (score > 80) | {{BEFORE_HOTSPOTS}} | 減少 50% | `hotspot.json` |

**強制要求**：
- ✅ 語言違規數必須 **減少**，不得增加
- ✅ Semgrep HIGH severity 必須 = 0
- ✅ 測試覆蓋率不得下降超過 2%
- ✅ 不得引入新的 banned languages
- ✅ 架構約束檢查必須通過

### 6.2 傳統驗收條件

- 語言治理指標：
  - 本 cluster 的違規數門檻（例如：<= 2）。
- 安全指標：
  - Semgrep HIGH = 0，MEDIUM <= N。
- 架構指標：
  - 是否完全符合 integration 劇本中的邊界與依賴關係。

---

## 7. 檔案與目錄結構（交付視圖）

受影響目錄與檔案結構（只需涵蓋此次重構範圍）：

```text
{{CLUSTER_ROOT}}/
  ├─ {{FILE_A}}    # 一行說明
  ├─ {{FILE_B}}    # 一行說明
  └─ subdir/
      └─ {{FILE_C}}  # 一行說明
```

* 說明：

  * `{{FILE_A}}` — 主要入口 / API 層 / Adapter 等說明。
  * `{{FILE_B}}` — 補充說明。
  * ...

---

## 8. 集成對齊（Integration Alignment）

* 上游依賴：

  * 例如：core/contract_service（gRPC）、governance/schemas（型別）
* 下游使用者：

  * 例如：apps/web 前端、mcp-servers/xxx
* 集成步驟摘要：

  * 重構順序 + 每步驟需要通過的測試 / CI。
* 回滾策略：

  * 若此 cluster 重構失敗，如何切回舊版組合？
