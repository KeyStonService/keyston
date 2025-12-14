# Experiments - 實驗與原型空間

> **用途**：此目錄用於存放原型程式、實驗性腳本、技術驗證等可執行的試驗性內容。

---

## 🔬 這裡適合放什麼？

✅ **適合的內容**：

- 技術原型與 PoC（Proof of Concept）
- 實驗性腳本與工具
- 效能測試與基準測試
- 新技術的學習範例
- API 整合測試
- 資料處理實驗
- 演算法驗證程式

❌ **不適合的內容**：

- 正式的生產程式碼（應放各 domain 主目錄）
- 已確定的工具腳本（應放 `tools/`）
- 單元測試（應放對應模組的 `tests/` 目錄）
- 文件與設計草稿（應放 `docs/scratch/`）

---

## 📁 建議的目錄結構

```text
experiments/
├─ poc-{feature}/           # 特定功能的 PoC
│  ├─ README.md             # 說明實驗目的與結果
│  ├─ prototype.py          # 原型程式
│  └─ test-data/            # 測試資料
├─ benchmark-{topic}/       # 效能測試
│  ├─ benchmark.py
│  └─ results.md            # 測試結果
├─ learning-{tech}/         # 技術學習範例
│  └─ examples/
└─ README.md                # 本檔案
```

---

## 🏗️ 建議的命名慣例

### 目錄命名

- `poc-{feature-name}` - Proof of Concept
- `benchmark-{topic}` - 效能基準測試
- `test-{integration}` - 整合測試實驗
- `learning-{technology}` - 技術學習

**範例**：
- `poc-autonomous-failover/`
- `benchmark-gateway-routing/`
- `test-ros2-python-integration/`
- `learning-gorilla-mux/`

### 檔案命名

- 保持描述性
- 使用小寫與短橫線
- 包含版本或日期（如適用）

**範例**：
- `prototype-v1.py`
- `benchmark-2025-12-06.py`
- `test-integration.sh`

---

## 🔄 實驗生命週期

### 實驗 → 生產

當實驗成功並準備進入生產：

1. **程式碼重構**：
   - 清理實驗性程式碼
   - 補充錯誤處理
   - 新增完整測試
   - 符合專案程式碼標準

2. **移動到正式目錄**：
   - 工具 → `tools/`
   - 核心功能 → `core/`
   - 服務 → `services/`
   - 自動化 → `automation/`

3. **更新文件**：
   - 新增到相關 README
   - 更新架構文件
   - 記錄決策過程（ADR）

4. **清理實驗目錄**：
   - 更新實驗的 README，標註「已整合到 X」
   - 保留或刪除實驗程式碼

### 實驗失敗

如果實驗結果不理想：

1. **記錄結果**：
   - 在實驗的 README 中記錄：
     - 為什麼失敗？
     - 學到什麼？
     - 有什麼替代方案？

2. **決定保留或刪除**：
   - 有價值的失敗經驗可以保留
   - 完全無用的可以刪除
   - 或移到 `experiments/archive/`

---

## ⚙️ Git 管理策略

### 可選擇的策略

**選項 A：進 git（推薦）**
- 優點：保留實驗歷史，團隊可見
- 適用：大多數實驗與原型

**選項 B：不進 git（.gitignore）**
- 優點：保持 repo 乾淨
- 適用：包含敏感資料、大型資料集、臨時測試

### 配置 .gitignore

如果特定實驗不應進 git：

```gitignore
# In .gitignore
experiments/poc-sensitive/
experiments/*/test-data/large-dataset/
experiments/*/*.log
```

---

## 📊 實驗記錄模板

每個實驗目錄應包含 README.md：

```markdown
# [實驗名稱]

## 目的
<!-- 為什麼做這個實驗？ -->

## 假設
<!-- 你想驗證什麼假設？ -->

## 方法
<!-- 如何執行這個實驗？ -->

## 結果
<!-- 實驗結果如何？ -->

## 結論
<!-- 學到什麼？下一步是什麼？ -->

## 狀態
🟡 進行中 / ✅ 成功 / ❌ 失敗 / 🗄️ 已歸檔
```

---

## 🎯 原則

1. **快速迭代**：不需要完美，專注驗證假設
2. **記錄過程**：失敗也是有價值的經驗
3. **及時清理**：成功的實驗要整合，失敗的要記錄或刪除
4. **隔離環境**：實驗程式不影響生產環境

---

最後更新：2025-12-06
