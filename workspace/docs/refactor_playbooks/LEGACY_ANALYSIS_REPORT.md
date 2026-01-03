# Legacy Scratch Refactor Playbook System - Analysis Report

# \_legacy_scratch 重構劇本系統 - 完整分析報告


**Generated:** 2025-12-06  
**Source:** `docs/refactor_playbooks/_legacy_scratch/refactor_readme.txt` (已移除 / Removed)  
**Status:** Integration Complete - Legacy Files Removed (2025-12-07)

---

## 📋 Executive Summary（執行摘要）

本報告完整分析 `_legacy_scratch/refactor_readme.txt` 中描述的三階段重構劇本系統架構，並將其邏輯提取、解構並整合到現有專案結構中。該系統是 Unmanned Island System 語言治理與架構重構的核心控制平面。

**注意**: 原始舊檔案 (`README.md`, `refactor_readme.txt`) 已於 2025-12-07 從 `_legacy_scratch/` 目錄中移除，因為內容已完全遷移到正式結構。`_legacy_scratch/` 目錄本身保留作為未來重構過程中的暫存區域。

### 核心發現

1. **三階段重構流程已實現**：01_deconstruction → 02_integration → 03_refactor 目錄結構已存在
2. **自動化工具已部署**：`tools/generate-refactor-playbook.py` 提供 AI 驅動的劇本生成
3. **需要補強的部分**：
   - `legacy_assets_index.yaml` 結構定義
   - `index.yaml` 機器可讀索引完整實現
   - 模板系統的標準化
   - CI/CD 整合文檔

---

## 🏗️ Architecture Analysis（架構分析）

### 1. Three-Phase Refactor System（三階段重構系統）

#### Phase 1: Deconstruction（解構）

**目的**：分析舊世界的架構、程式碼、語言堆疊和反模式

```
01_deconstruction/
├── README.md                           # 解構階段說明
├── legacy_assets_index.yaml            # 舊資產索引：ID → 來源/描述
├── core__architecture_deconstruction.md
├── services__gateway_deconstruction.md
└── ...
```

**關鍵概念**：

- 舊資產不保留實體檔案，只保留索引記錄
- 每個舊資產有唯一 ID，記錄來源、描述、原因
- 解構劇本描述「為什麼」需要重構

#### Phase 2: Integration（集成）

**目的**：設計新世界的組合方式

```
02_integration/
├── README.md                          # 集成階段說明
├── core__architecture_integration.md
├── services__gateway_integration.md
└── ...
```

**關鍵概念**：

- 定義語言層級策略
- 設計模組邊界與 API 契約
- 規劃跨 cluster 的接線方案
- 建立目標架構藍圖

#### Phase 3: Refactor（重構）

**目的**：將設計轉換為可執行的重構計畫

```
03_refactor/
├── README.md                          # 重構階段說明（本目錄）
├── INDEX.md                           # 人類可讀索引
├── index.yaml                         # 機器可讀索引
├── templates/                         # 劇本模板系統
│   ├── REFRACTOR_PLAYBOOK_TEMPLATE.md
│   ├── SECTION_SNIPPETS.md
│   ├── META_CONVENTIONS.md
│   └── README.md
├── core/                              # 按領域分組的重構劇本
├── services/
├── automation/
├── apps/
├── governance/
├── infra/
├── knowledge/
└── meta/                              # 系統整合說明
    ├── CI_INTEGRATION.md
    └── AI_PROMPTS.md
```

**關鍵概念**：

- P0/P1/P2 優先級行動清單
- 明確 Auto-Fix Bot 可處理範圍
- 驗收條件與成功指標
- 目錄結構交付視圖

### 2. Legacy Asset Management（舊資產管理）

#### 生命週期管理

```
暫存階段（Staging）
    ↓
_legacy_scratch/ 中暫存實體檔案
    ↓
索引階段（Indexing）
    ↓
legacy_assets_index.yaml 記錄 ID/來源/描述
    ↓
引用階段（Reference）
    ↓
重構劇本通過 ID 引用
    ↓
清理階段（Cleanup）
    ↓
新實作完成後刪除舊檔
    ↓
追溯階段（Traceability）
    ↓
透過索引與劇本保留知識
```

#### 核心原則

1. **實體隔離**：舊資產實體檔案只存在於 `_legacy_scratch/`，受 `.gitignore` 保護
2. **知識保留**：透過 YAML 索引記錄來源、描述、原因
3. **引用透明**：劇本使用 asset ID 引用，不嵌入舊程式碼
4. **自動清理**：新實作完成後必須刪除對應舊檔
5. **審計追溯**：保留決策歷史，不保留原始碼

### 3. Index System（索引系統）

#### index.yaml 結構

```yaml
clusters:
  - cluster_id: "core/architecture-stability"
    domain: "core"
    priority: "P0"                          # P0/P1/P2
    status: "in_progress"                   # draft/in_progress/completed/blocked
    
    # 重構劇本位置
    refactor_file: "core/core__architecture_refactor.md"
    
    # 來源劇本（必須存在）
    deconstruction_file: "../01_deconstruction/core__architecture_deconstruction.md"
    integration_file: "../02_integration/core__architecture_integration.md"
    
    # 舊資產引用（指向 legacy_assets_index.yaml 中的 ID）
    legacy_assets:
      - "core-v1-legacy-modules"
      - "architecture-old-contracts"
    
    # 涉及的實際目錄
    involved_dirs:
      - "core/unified_integration/"
      - "core/mind_matrix/"
      - "core/architecture-stability/"
    
    # 語言治理狀態
    governance_status:
      violations: 15                        # 當前違規數
      threshold: 5                          # 目標門檻
      auto_fixable: 8                       # Auto-Fix 可處理數量
```

#### legacy_assets_index.yaml 結構

```yaml
legacy_assets:
  - id: "core-v1-legacy-modules"
    source_repo: "git@github.com:old-repo/core.git"
    source_ref: "v1.0.0"
    description: "舊版 core 模組（TypeScript）"
    reason: "語言混用、缺乏類型安全、架構邊界不清"
    deprecated_date: "2024-11-01"
    
  - id: "architecture-old-contracts"
    source_repo: "git@github.com:old-repo/contracts.git"
    source_ref: "main@abc1234"
    description: "舊版 gRPC 合約定義"
    reason: "Protocol Buffer v2 已廢棄，缺乏 API 版本管理"
    deprecated_date: "2024-10-15"
```

---

## 📋 Playbook Template Structure（劇本模板結構）

### 標準重構劇本必備內容

每個 `*_refactor.md` 必須包含以下區塊：

#### 1. 檔頭 YAML（Front Matter）

```yaml
---
cluster_id: "core/architecture-stability"
domain: "core"
priority: "P0"
status: "in_progress"

# 來源劇本（必填）
deconstruction: "../01_deconstruction/core__architecture_deconstruction.md"
integration: "../02_integration/core__architecture_integration.md"

# 舊資產引用（必填）
legacy_assets:
  - id: "core-v1-legacy-modules"
    description: "舊版 core 模組（TypeScript）"
  - id: "architecture-old-contracts"
    description: "舊版 gRPC 合約定義"

# 涉及目錄（必填）
involved_dirs:
  - "core/unified_integration/"
  - "core/mind_matrix/"
  - "core/architecture-stability/"
---
```

#### 2. 必備章節

1. **Cluster 概覽**
   - 角色與邊界
   - 語言組成
   - 當前狀態

2. **問題盤點**
   - 語言治理違規
   - Hotspot 檔案
   - Semgrep 安全問題
   - Flow 問題

3. **語言與結構重構策略**
   - 語言層級調整
   - 目錄結構優化
   - 集成對齊方案

4. **分級重構計畫（P0/P1/P2）**
   - P0（24-48 小時內必須處理）
   - P1（一週內）
   - P2（持續改進）

5. **Auto-Fix Bot 可以處理的項目**
   - 自動化範圍
   - 人工審查範圍

6. **驗收條件與成功指標**
   - 語言治理目標
   - 安全指標
   - 架構指標

7. **檔案與目錄結構（交付視圖）**
   - 受影響目錄清單
   - 完整結構圖
   - 檔案註解說明

8. **集成對齊與回滾策略**
   - 上下游依賴
   - 步驟順序
   - 失敗回滾

---

## 🤖 CI/CD Integration（CI/CD 整合）

### CI Pipeline 使用方式

```yaml
# .github/workflows/language-governance.yml

- name: Map violations to refactor playbooks
  run: |
    # 讀取 index.yaml
    python scripts/map_violations_to_playbooks.py \
      --violations language-governance-report.json \
      --index docs/refactor_playbooks/03_refactor/index.yaml \
      --output violation-playbook-map.json
    
    # 產生 GitHub Issue（按 cluster 分組）
    python scripts/create_refactor_issues.py \
      --map violation-playbook-map.json
```

### Auto-Fix Bot 工作流程

```
1. 觸發：語言治理發現違規
    ↓
2. 查詢：讀取 index.yaml 找到對應 refactor_file
    ↓
3. 解析：讀取 *_refactor.md 的 "Auto-Fix 可以處理的項目" 章節
    ↓
4. 執行：只修改 auto_fixable 範圍內的檔案
    ↓
5. PR：產生 PR，標題引用 cluster_id 與 refactor_file
    ↓
6. 審查：必須由人類審查「人工審查範圍」的變更
```

### Dashboard 展示

```typescript
interface ClusterView {
  clusterId: string;
  domain: string;
  priority: 'P0' | 'P1' | 'P2';
  status: 'draft' | 'in_progress' | 'completed' | 'blocked';
  
  refactorPlaybook: string;  // Markdown 內容
  governanceStatus: {
    violations: number;
    threshold: number;
    autoFixable: number;
  };
  
  actions: {
    viewPlaybook: () => void;
    triggerAutoFix: () => void;
    viewDeconstruction: () => void;
    viewIntegration: () => void;
  };
}
```

---

## 🎯 Best Practices（最佳實務）

### 絕對禁止（DO NOT）

❌ 將舊資產實體檔案 commit 到 git  
❌ 在重構劇本中貼上大段舊程式碼  
❌ 建立沒有對應 deconstruction/integration 的劇本  
❌ 修改 `index.yaml` 但不同步更新 `INDEX.md`

### 強烈建議（DO）

✅ 每個重構劇本對應一個明確的 cluster  
✅ P0/P1/P2 行動清單具體到檔案層級  
✅ Auto-Fix 邊界寫清楚（讓 Bot 不會越界）  
✅ 驗收條件可量化（違規數/覆蓋率/指標門檻）

### 維護原則

1. **增量式**：一次只改一個 cluster，完成後再改下一個
2. **雙向追溯**：重構劇本 ↔ 解構/集成劇本 互相引用
3. **狀態同步**：`index.yaml` 狀態與實際進度保持一致
4. **定期檢視**：每週 review 所有 `in_progress` 狀態的劇本

---

## 📊 Success Metrics（成功指標）

### 系統層級指標

- ✅ 所有 P0 cluster 的劇本已完成並執行
- ✅ 語言治理違規數降到各 cluster 門檻以下
- ✅ Semgrep HIGH severity 問題 = 0
- ✅ 所有 `index.yaml` 條目都有對應實體檔案

### 流程層級指標

- ✅ CI 能自動 map 違規到對應劇本
- ✅ Auto-Fix Bot 成功率 > 80%（不引入新問題）
- ✅ Dashboard 能正確展示所有 cluster 狀態
- ✅ 新成員能在 30 分鐘內理解整個系統

---

## 🔄 Integration Status（整合狀態）

### Phase 1: Documentation（已完成）

- [x] 創建本分析報告
- [x] 提取架構設計原則
- [x] 記錄索引系統結構
- [x] 文檔化最佳實務

### Phase 2: Implementation（進行中）

- [ ] 創建/驗證 `01_deconstruction/legacy_assets_index.yaml`
- [ ] 創建/驗證 `03_refactor/index.yaml`
- [ ] 補充 `03_refactor/INDEX.md`
- [ ] 驗證所有模板文件完整性

### Phase 3: Tool Enhancement（待進行）

- [ ] 更新 `generate-refactor-playbook.py` 支援 index.yaml 生成
- [ ] 新增索引驗證腳本
- [ ] 整合 CI/CD 工作流

### Phase 4: Validation（待進行）

- [ ] 執行完整系統驗證
- [ ] 生成整合測試報告
- [ ] 更新主文檔引用

---

## 📚 Related Documentation（相關文檔）

- [docs/refactor_playbooks/README.md](./README.md) - Refactor Playbooks 使用指南
- [docs/refactor_playbooks/ARCHITECTURE.md](./ARCHITECTURE.md) - 系統架構設計
- [docs/refactor_playbooks/IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) - 實作摘要
- [docs/refactor_playbooks/03_refactor/README.md](./03_refactor/README.md) - 重構層說明
- [docs/refactor_playbooks/03_refactor/templates/](./03_refactor/templates/) - 劇本模板

---

## 🎓 Learning Resources（學習資源）

### 必讀文件順序

1. 本分析報告（理解整體架構）
2. `03_refactor/templates/REFRACTOR_PLAYBOOK_TEMPLATE.md`（劇本標準格式）
3. `03_refactor/templates/META_CONVENTIONS.md`（命名與風格規範）
4. `03_refactor/meta/CI_INTEGRATION.md`（CI 整合指南）

### 示範劇本

- `03_refactor/core/core__architecture_refactor.md` - Core Platform 完整示範
- `03_refactor/services/services__gateway_refactor.md` - Services Layer 示範
- `03_refactor/automation/automation__autonomous_refactor.md` - Automation System 示範

---

## 🚀 Next Steps（下一步行動）

### 立即行動

1. **補充索引系統**：創建完整的 `index.yaml` 和 `legacy_assets_index.yaml`
2. **驗證模板**：確保所有模板文件完整且一致
3. **工具升級**：增強 Python 工具支援索引生成與驗證

### 短期目標（1-2 週）

1. **CI/CD 整合**：實現自動化違規映射到劇本
2. **Dashboard 整合**：在 Language Governance Dashboard 展示劇本狀態
3. **Auto-Fix Bot 整合**：實現劇本驅動的自動修復

### 長期願景（1-3 個月）

1. **完整 P0 重構**：完成所有 P0 優先級的重構計畫
2. **自動化測試**：建立劇本執行的自動化測試框架
3. **知識累積**：持續更新劇本，形成活體知識庫

---

**Last Updated:** 2025-12-06  
**Maintainer:** Unmanned Island Architecture Team  
**Status:** ✅ Analysis Complete - Ready for Implementation
