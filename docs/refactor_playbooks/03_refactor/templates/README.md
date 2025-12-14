# Templates - 重構劇本模板

> 本目錄包含所有重構劇本系統使用的標準模板與規範。

---

## 📋 可用模板

### 1. REFRACTOR_PLAYBOOK_TEMPLATE.md

**用途**：建立新的重構劇本（Refactor Playbook）

**使用時機**：
- 為新的 cluster 建立重構計畫
- 需要完整的 P0/P1/P2 行動清單
- 需要定義 Auto-Fix 範圍與驗收條件

**使用方法**：
```bash
# 複製模板
cp docs/refactor_playbooks/03_refactor/templates/REFRACTOR_PLAYBOOK_TEMPLATE.md \
   docs/refactor_playbooks/03_refactor/core/core__new_cluster_refactor.md

# 或使用工具生成
python tools/generate-refactor-playbook.py \
  --cluster "core/new-cluster" \
  --domain "core"
```

**必填欄位**：
- Cluster ID
- 對應目錄
- 對應集成劇本
- 8 個標準章節

---

### 2. SCRATCH_NOTES_TEMPLATE.md

**用途**：建立設計草稿、探索筆記、方案比較

**使用時機**：
- 探索多個設計方案
- 記錄架構思考過程
- 進行技術實驗與驗證
- 會議討論筆記

**使用方法**：
```bash
# 全域草稿
cp docs/refactor_playbooks/03_refactor/templates/SCRATCH_NOTES_TEMPLATE.md \
   docs/scratch/scratch-your-topic.md

# Domain 專屬草稿
cp docs/refactor_playbooks/03_refactor/templates/SCRATCH_NOTES_TEMPLATE.md \
   core/_scratch/scratch-ai-engine-redesign.md

# 實驗記錄
cp docs/refactor_playbooks/03_refactor/templates/SCRATCH_NOTES_TEMPLATE.md \
   experiments/poc-feature/notes.md
```

**特點**：
- 輕量級格式
- 支援多方案比較
- 包含實驗結果記錄
- 標註升級路徑

---

### 3. SECTION_SNIPPETS.md

**用途**：常用章節的可重複使用片段

**內容**：
- P0/P1/P2 行動模板
- Auto-Fix 範圍範例
- 驗收條件表格
- 常見語言遷移場景

**使用方法**：
直接複製需要的 snippet 到你的劇本中。

---

### 4. META_CONVENTIONS.md

**用途**：命名規則與結構規範

**內容**：
- 檔名命名規則
- Cluster ID 格式
- 目錄結構對應
- 檔頭格式規範
- 檔案類型策略（**包含 scratch 空間規則**）
- 版本控制規範
- 驗證檢查清單

**使用時機**：
- 建立新劇本前參考
- 進行 code review 時驗證
- 設定 CI 檢查規則

---

## 🆕 Scratch 空間擴展

根據最新策略（參見 META_CONVENTIONS.md 第 11 節），scratch 空間已擴展：

### 可用的 Scratch 位置

1. **`docs/scratch/`** - 全域架構與設計草稿
2. **`experiments/`** - 原型程式與實驗
3. **Domain 專屬**：
   - `core/_scratch/`
   - `services/_scratch/`
   - `automation/_scratch/`
   - `apps/_scratch/`
   - `governance/_scratch/`
   - `infra/_scratch/`
   - `tools/_scratch/`

### 與 Legacy Scratch 的區別

| 特性 | Scratch Notes | Legacy Scratch |
|------|---------------|----------------|
| 位置 | `docs/scratch/`, `*/_scratch/` | `docs/refactor_playbooks/_legacy_scratch/` |
| 內容 | 設計草稿、筆記、探索 | 舊程式碼、舊模板 |
| Git | ✅ 可進 git | ❌ 不進 git (.gitignore) |
| 用途 | 創作與思考空間 | 臨時程式碼暫存 |
| 生命週期 | 升級為正式文件或歸檔 | 重構完成後刪除 |

---

## 📊 使用流程建議

### 新功能開發流程

```
1. 在 docs/scratch/ 或 domain/_scratch/ 建立草稿
   → 使用 SCRATCH_NOTES_TEMPLATE.md

2. 探索與實驗階段
   → 記錄想法、比較方案、實驗結果

3. 方案確定後，建立重構劇本
   → 使用 REFRACTOR_PLAYBOOK_TEMPLATE.md
   → 放在 03_refactor/{domain}/

4. 執行重構
   → 按照劇本的 P0/P1/P2 執行

5. 清理 scratch
   → 升級為正式文件或歸檔
```

---

## 🔄 模板更新

當模板需要更新時：

1. 修改對應的 `*_TEMPLATE.md` 檔案
2. 更新 `META_CONVENTIONS.md`（如影響規範）
3. 通知團隊（透過 PR 說明）
4. 考慮是否需要更新現有劇本

---

## 🎯 最佳實踐

1. **選對模板**：
   - 探索階段 → SCRATCH_NOTES_TEMPLATE
   - 確定計畫 → REFRACTOR_PLAYBOOK_TEMPLATE

2. **保持一致性**：
   - 從模板開始，不要從空白開始
   - 遵循 META_CONVENTIONS 的規則

3. **適時升級**：
   - Scratch 成熟後要升級為正式文件
   - 不要讓 scratch 無限累積

4. **記錄過程**：
   - 失敗的嘗試也有價值
   - 保留設計決策的脈絡

---

最後更新：2025-12-06
