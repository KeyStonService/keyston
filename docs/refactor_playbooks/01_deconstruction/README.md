# 01_deconstruction：解構劇本層（Deconstruction Playbook Layer）

> 本目錄是 **Unmanned Island
> System 重構系統的第一層**，專門用於分析和記錄「舊世界」的架構、設計決策與歷史包袱。

---

## 角色與定位

`01_deconstruction/` 是重構流程的**起點**，負責：

1. **考古挖掘**：理解舊程式碼的設計意圖與演化歷程
2. **模式識別**：找出 anti-patterns、技術債與架構問題
3. **依賴分析**：繪製模組間的依賴關係圖
4. **知識萃取**：記錄有價值的設計決策供後續參考
5. **風險評估**：識別重構過程中可能的風險點

---

## 與其他層的關係

```text
01_deconstruction (分析舊世界)
    ↓
02_integration (設計新世界)
    ↓
03_refactor (執行重構)
```

- **輸入**：舊程式碼、歷史文件、團隊訪談
- **輸出**：解構劇本（\*\_deconstruction.md）、legacy_assets_index.yaml
- **使用者**：02_integration 和 03_refactor 作為參考依據

---

## 目錄結構

```text
01_deconstruction/
├─ README.md                                # 本說明文件
├─ legacy_assets_index.yaml                # 舊資產索引（ID → 來源 → 描述）
├─ core__architecture_deconstruction.md    # core/ 的解構劇本
├─ services__gateway_deconstruction.md     # services/gateway 的解構劇本
└─ ...                                     # 其他 cluster 的解構劇本
```

---

## legacy_assets_index.yaml 說明

`legacy_assets_index.yaml` 是舊資產的**知識層索引**，記錄：

- **asset_id**：唯一識別碼
- **description**：舊資產的簡短描述
- **source_repo** / **source_ref**：來源位置（repo + tag/branch）
- **related_clusters**：相關的 cluster 列表
- **notes**：額外註解

### 重要原則

1. **實體檔案不進 git**：真實的舊程式碼只暫存在 `_legacy_scratch/`，受
   `.gitignore` 保護
2. **知識保留**：透過 index 保留「為什麼有這個舊資產」的脈絡
3. **可追溯**：任何時候都能從 source_repo + source_ref 重新取得舊資產

---

## 解構劇本必備內容

每個 `*_deconstruction.md` 應包含：

1. **歷史脈絡**
   - 這個 cluster 的演化歷程
   - 為什麼當初這樣設計？

2. **問題盤點**
   - 現在為什麼需要改？
   - 有哪些 anti-patterns？
   - 技術債清單

3. **依賴關係**
   - 誰依賴誰？
   - 拆掉會影響誰？
   - 依賴關係圖

4. **遷移風險**
   - 改動的風險點在哪裡？
   - 哪些使用者會受影響？
   - 需要特別注意的地方

5. **有價值的設計**
   - 哪些設計決策值得保留？
   - 哪些經驗教訓要記錄？

---

## 如何新增解構劇本

1. **調查與訪談**
   - 閱讀舊程式碼與文件
   - 訪談原始開發者（如可能）
   - 分析 git history 和 PR 討論

2. **記錄發現**
   - 建立 `{domain}__{cluster}_deconstruction.md`
   - 按照標準格式填寫各章節

3. **登記舊資產**（如需要）
   - 在 `legacy_assets_index.yaml` 新增條目
   - 將實體檔案暫存在 `_legacy_scratch/`
   - 確保 `.gitignore` 有保護

4. **關聯到後續層**
   - 在 `02_integration/` 引用本解構劇本
   - 在 `03_refactor/` 引用本解構劇本與舊資產 ID

---

## 最佳實踐

### ✅ 應該做的

- 保持客觀：記錄事實而非評判
- 追根溯源：找出「為什麼」而非僅「是什麼」
- 完整記錄：包含成功經驗與失敗教訓
- 追蹤依賴：畫出完整的依賴關係圖

### ❌ 不應該做的

- 不要只記錄問題而忽略好的設計
- 不要將大量舊程式碼 commit 進 git
- 不要孤立分析（要考慮整個系統脈絡）
- 不要省略風險評估

---

## 範例參考

查看 `03_refactor/templates/` 中的範例，了解：

- 如何結構化解構劇本
- 如何記錄依賴關係
- 如何評估遷移風險

---

最後更新：2025-12-06
