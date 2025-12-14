# 📂 {{TARGET_DIRECTORY}} 目錄深度分析與重構策略

**Generated:** {{TIMESTAMP}}
**Analyzer:** Refactor Engine v1.0
**Asset ID:** {{ASSET_ID}}
**Status:** {{STATUS}}

---

## 📊 目錄現況總覽

### 基本資訊

| 屬性 | 值 |
|------|-----|
| **目標目錄** | `{{TARGET_DIRECTORY}}` |
| **總檔案數** | {{TOTAL_FILES}} |
| **目錄數** | {{TOTAL_DIRECTORIES}} |
| **主要語言** | {{PRIMARY_LANGUAGES}} |
| **目錄深度** | {{MAX_DEPTH}} 層 |
| **最後修改** | {{LAST_MODIFIED}} |

### 檔案類型分布

```
📁 檔案類型分布
{{FILE_TYPE_DISTRIBUTION}}
```

### 當前目錄結構

```
{{CURRENT_STRUCTURE_ASCII}}
```

---

## 🚨 識別的問題

### 問題 1: {{PROBLEM_1_TITLE}}

**描述：** {{PROBLEM_1_DESCRIPTION}}

**影響：**
- {{PROBLEM_1_IMPACT_1}}
- {{PROBLEM_1_IMPACT_2}}
- {{PROBLEM_1_IMPACT_3}}

**分類：** {{PROBLEM_1_CATEGORY}}
- [ ] 結構問題
- [ ] 命名問題
- [ ] 依賴問題
- [ ] 冗餘問題
- [ ] 安全問題

**阻抗/衝突：**
- {{PROBLEM_1_BLOCKER}}

---

### 問題 2: {{PROBLEM_2_TITLE}}

**描述：** {{PROBLEM_2_DESCRIPTION}}

**影響：**
- {{PROBLEM_2_IMPACT_1}}
- {{PROBLEM_2_IMPACT_2}}

**分類：** {{PROBLEM_2_CATEGORY}}

**阻抗/衝突：**
- {{PROBLEM_2_BLOCKER}}

---

### 問題 3: {{PROBLEM_3_TITLE}}

**描述：** {{PROBLEM_3_DESCRIPTION}}

**影響：**
- {{PROBLEM_3_IMPACT_1}}

**分類：** {{PROBLEM_3_CATEGORY}}

**阻抗/衝突：**
- {{PROBLEM_3_BLOCKER}}

---

### 問題 4: {{PROBLEM_4_TITLE}}

**描述：** {{PROBLEM_4_DESCRIPTION}}

**結構內容：**
```
{{PROBLEM_4_STRUCTURE}}
```

**分類：** {{PROBLEM_4_CATEGORY}}

---

### 問題 5: {{PROBLEM_5_TITLE}}

**描述：** {{PROBLEM_5_DESCRIPTION}}

**阻抗：**
- {{PROBLEM_5_IMPEDANCE}}

---

## 🔄 重構設計：目標結構

### 設計原則

1. **結構清晰度** - 目錄深度 ≤ {{TARGET_MAX_DEPTH}} 層
2. **功能內聚性** - 相關功能集中在同一目錄
3. **依賴最小化** - 明確的依賴方向
4. **命名一致性** - 統一使用 {{NAMING_CONVENTION}}

### 目標結構圖譜

```
{{TARGET_STRUCTURE_ASCII}}
```

### Mermaid 流程圖

```mermaid
{{TARGET_STRUCTURE_MERMAID}}
```

### 變更摘要

| 變更類型 | 數量 | 說明 |
|---------|------|------|
| 新建目錄 | {{NEW_DIRS_COUNT}} | {{NEW_DIRS_DESC}} |
| 移動檔案 | {{MOVED_FILES_COUNT}} | {{MOVED_FILES_DESC}} |
| 合併檔案 | {{MERGED_FILES_COUNT}} | {{MERGED_FILES_DESC}} |
| 刪除檔案 | {{DELETED_FILES_COUNT}} | {{DELETED_FILES_DESC}} |
| 重命名 | {{RENAMED_COUNT}} | {{RENAMED_DESC}} |

---

## 📋 執行計畫：正確順序

### Phase 1: 建立/更新目錄結構 (P1)

**優先級：** P1 - 緊急處理 (24-48 小時)

**目標：** 建立新的目錄骨架，為後續遷移做準備

| 步驟 | 操作 | 目標 | 說明 |
|------|------|------|------|
| 1.1 | 建立目錄 | `{{P1_STEP_1_TARGET}}` | {{P1_STEP_1_DESC}} |
| 1.2 | 建立目錄 | `{{P1_STEP_2_TARGET}}` | {{P1_STEP_2_DESC}} |
| 1.3 | 建立目錄 | `{{P1_STEP_3_TARGET}}` | {{P1_STEP_3_DESC}} |

**驗證：**
```bash
{{P1_VALIDATION_COMMAND}}
```

---

### Phase 2: 核心檔案遷移 (P1)

**優先級：** P1 - 緊急處理

**目標：** 遷移核心檔案到新位置

| 步驟 | 操作 | 來源 | 目標 |
|------|------|------|------|
| 2.1 | 移動 | `{{P1_MOVE_1_SOURCE}}` | `{{P1_MOVE_1_TARGET}}` |
| 2.2 | 移動 | `{{P1_MOVE_2_SOURCE}}` | `{{P1_MOVE_2_TARGET}}` |
| 2.3 | 移動 | `{{P1_MOVE_3_SOURCE}}` | `{{P1_MOVE_3_TARGET}}` |

**驗證：**
- [ ] 所有檔案已移動到正確位置
- [ ] 無遺漏檔案

---

### Phase 3: 輔助檔案遷移 (P1)

**優先級：** P1 - 緊急處理

**目標：** 遷移輔助檔案和配置

| 步驟 | 操作 | 來源 | 目標 |
|------|------|------|------|
| 3.1 | 移動 | `{{P1_MOVE_4_SOURCE}}` | `{{P1_MOVE_4_TARGET}}` |
| 3.2 | 移動 | `{{P1_MOVE_5_SOURCE}}` | `{{P1_MOVE_5_TARGET}}` |

---

### Phase 4: 更新引用路徑 (P2)

**優先級：** P2 - 重要重構 (1 週內)

**目標：** 更新所有內部引用路徑

| 步驟 | 檔案 | 舊路徑 | 新路徑 |
|------|------|--------|--------|
| 4.1 | `{{P2_REF_1_FILE}}` | `{{P2_REF_1_OLD}}` | `{{P2_REF_1_NEW}}` |
| 4.2 | `{{P2_REF_2_FILE}}` | `{{P2_REF_2_OLD}}` | `{{P2_REF_2_NEW}}` |

**自動化腳本：**
```bash
{{P2_UPDATE_SCRIPT}}
```

---

### Phase 5: 更新索引檔案 (P2)

**優先級：** P2 - 重要重構

**目標：** 同步更新所有索引檔案

| 步驟 | 索引檔案 | 操作 |
|------|---------|------|
| 5.1 | `index.yaml` | 更新 cluster 路徑 |
| 5.2 | `INDEX.md` | 更新連結 |
| 5.3 | `README.md` | 更新目錄結構說明 |

---

### Phase 6: 合併/整理重複內容 (P2)

**優先級：** P2 - 重要重構

**目標：** 處理重複或重疊的內容

| 步驟 | 操作 | 說明 |
|------|------|------|
| 6.1 | 合併 | {{P2_MERGE_1_DESC}} |
| 6.2 | 合併 | {{P2_MERGE_2_DESC}} |

---

### Phase 7: 清理舊檔案 (P3)

**優先級：** P3 - 持續優化 (長期)

**目標：** 清理已遷移的舊檔案

| 步驟 | 操作 | 目標 | 前提條件 |
|------|------|------|----------|
| 7.1 | 刪除 | `{{P3_DELETE_1}}` | 確認新位置正常運作 |
| 7.2 | 刪除 | `{{P3_DELETE_2}}` | 確認無引用 |

**安全檢查：**
```bash
{{P3_SAFETY_CHECK}}
```

---

### Phase 8: 歸檔舊資產 (P3)

**優先級：** P3 - 持續優化

**目標：** 將僅有歷史價值的檔案歸檔

| 步驟 | 操作 | 來源 | 歸檔位置 |
|------|------|------|----------|
| 8.1 | 歸檔 | `{{P3_ARCHIVE_1_SOURCE}}` | `_legacy_scratch/archive/` |
| 8.2 | 歸檔 | `{{P3_ARCHIVE_2_SOURCE}}` | `_legacy_scratch/archive/` |

---

### Phase 9: 驗證與文檔更新 (P3)

**優先級：** P3 - 持續優化

**目標：** 完成最終驗證並更新文檔

| 步驟 | 操作 | 說明 |
|------|------|------|
| 9.1 | 驗證 | 執行完整結構驗證 |
| 9.2 | 測試 | 執行相關測試套件 |
| 9.3 | 更新 | 更新 CHANGELOG |
| 9.4 | 更新 | 更新相關文檔連結 |

---

## ✅ 驗收條件

### 結構驗收

| 條件 | 當前 | 目標 | 狀態 |
|------|------|------|------|
| 根層級 .md 檔案數 | {{CURRENT_ROOT_MD}} | ≤ {{TARGET_ROOT_MD}} | ⬜ |
| 最大目錄深度 | {{CURRENT_DEPTH}} | ≤ {{TARGET_DEPTH}} | ⬜ |
| 孤立檔案數 | {{CURRENT_ORPHANS}} | 0 | ⬜ |
| 重複檔案數 | {{CURRENT_DUPLICATES}} | 0 | ⬜ |

### 引用驗收

| 條件 | 說明 | 狀態 |
|------|------|------|
| 無損壞連結 | 所有 Markdown 連結有效 | ⬜ |
| 無舊路徑引用 | 沒有指向舊位置的引用 | ⬜ |
| 索引同步 | index.yaml 與實際結構一致 | ⬜ |

### 品質驗收

| 條件 | 說明 | 狀態 |
|------|------|------|
| YAML 語法正確 | 所有 YAML 檔案可解析 | ⬜ |
| 命名一致 | 統一使用 {{NAMING_CONVENTION}} | ⬜ |
| 測試通過 | 相關測試套件全部通過 | ⬜ |

---

## 📊 風險評估

### 高風險項目

| 風險 | 影響 | 緩解措施 |
|------|------|----------|
| {{HIGH_RISK_1}} | {{HIGH_RISK_1_IMPACT}} | {{HIGH_RISK_1_MITIGATION}} |
| {{HIGH_RISK_2}} | {{HIGH_RISK_2_IMPACT}} | {{HIGH_RISK_2_MITIGATION}} |

### 中風險項目

| 風險 | 影響 | 緩解措施 |
|------|------|----------|
| {{MED_RISK_1}} | {{MED_RISK_1_IMPACT}} | {{MED_RISK_1_MITIGATION}} |

### 回滾計畫

如果重構失敗，執行以下步驟：

1. 停止所有進行中的遷移操作
2. 從 `_legacy_scratch/_backups/` 恢復備份
3. 還原索引檔案
4. 驗證恢復後的結構
5. 記錄失敗原因

```bash
{{ROLLBACK_SCRIPT}}
```

---

## 📚 相關文件

- [主 README](../README.md)
- [架構設計](../ARCHITECTURE.md)
- [重構引擎配置](../config/refactor-engine-config.yaml)
- [暫存區處理器](../config/legacy-scratch-processor.yaml)
- [集成處理器](../config/integration-processor.yaml)

---

## 📝 附錄

### A. 完整檔案清單

<details>
<summary>點擊展開完整檔案清單</summary>

```
{{FULL_FILE_LIST}}
```

</details>

### B. 依賴關係圖

<details>
<summary>點擊展開依賴關係圖</summary>

```mermaid
{{DEPENDENCY_GRAPH_MERMAID}}
```

</details>

### C. 變更日誌

| 時間 | 操作 | 說明 | 執行者 |
|------|------|------|--------|
| {{CHANGELOG_1_TIME}} | {{CHANGELOG_1_OP}} | {{CHANGELOG_1_DESC}} | {{CHANGELOG_1_BY}} |

---

**Last Updated:** {{TIMESTAMP}}
**Generated By:** Refactor Engine v1.0
**Status:** {{STATUS}}
