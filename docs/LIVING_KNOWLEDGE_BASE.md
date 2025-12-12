# 🧬 活體知識庫（Living Knowledge Base）

> 讓系統自己感知變化、重建自身結構、自我檢查，並主動回報狀態。

本專案不是人工智慧助理、不是命令列工具、不是 Copilot 或聊天機器人。  
它的唯一目的，是讓一個程式碼倉庫「知道自己現在長怎樣、哪裡有問題」，並用**機器可讀的方式**表達出來。

---

## 📜 合約規範（機器可讀合約）

活體知識庫遵守以下合約：

- 不是 AI 助理 / Chatbot
- 不是 CLI 工具，不提供任何命令列參數說明
- 不主打「AI 程式碼分析」或「程式碼副駕駛」
- 專注在：感知 → 建模 → 自我診斷 → 行動 的知識循環

對應的機器可讀合約（YAML）會放在：

- `knowledge/contracts/living-knowledge-contract.yaml`（未來可加入）

---

## 🎯 目標

活體知識庫的核心目標：

1. **自我感知**
   - 知道倉庫內有什麼變化：檔案新增 / 修改 / 刪除、工作流成功或失敗。

2. **自我建模**
   - 把目前的系統結構轉成機器可讀的文件：元件、設定、文件、工作流之間的關係。

3. **自我診斷**
   - 找出孤兒元件、死設定、重疊工作流、斷鏈文件等問題。

4. **自我回饋**
   - 產生健康報告，必要時主動發出提醒（例如開 Issue），讓人類知道哪裡需要維護。

---

## 🧩 知識庫的四個層次

### 1. 感知層（Perception）

回答的問題是：

> 最近發生了什麼變化？

資料來源：

- Git 提交紀錄（新增 / 修改 / 刪除）
- GitHub Actions 工作流結果（成功 / 失敗）
- 定期排程掃描（就算沒人動，也做一次體檢）

感知層只負責觸發後續流程，不做分析。

---

### 2. 建模層（Modeling）

回答的問題是：

> 現在這個系統長什麼樣子？

每次感知到變化後，建模層會重新生成三個機器可讀產物：

1. `docs/generated-mndoc.yaml`
   - 系統「說明書」：名稱、版本、子系統、關鍵文件等。

2. `docs/knowledge-graph.yaml`
   - 系統「神經連結圖」：
     - 節點：系統、子系統、元件、設定、文件、工作流…
     - 關係：隸屬、依賴、覆蓋範圍、文件連結…

3. `docs/superroot-entities.yaml`
   - 使用 SuperRoot 風格的 ontology 描述：
     - `Component`（元件）
     - `ConfigParam`（設定）
   - 讓外部治理系統可以直接讀取與推理。

---

### 3. 自我診斷層（Self-diagnosis）

回答的問題是：

> 現在這個系統健康嗎？哪裡有問題？

自我診斷層會基於 `knowledge-graph.yaml` 和 `superroot-entities.yaml`
做檢查，例如：

- **孤兒元件**
  - 沒有任何工作流負責建置或測試的 Component。

- **死設定**
  - 不再被任何元件使用的 Config。

- **重疊工作流**
  - 負責相同範圍（scope）、屬於相同建置線（lineage_group）的 workflow。

- **斷鏈文件**
  - 文檔中指向已不存在路徑的連結。

診斷結果會輸出為：

- `docs/knowledge-health-report.yaml`
  - 機器可讀的健康報告（孤兒、死設定、重疊、斷鏈列表）。

---

### 4. 行動 / 回饋層（Action / Feedback）

回答的問題是：

> 發現問題之後，要怎麼讓人類知道？

行動層不直接修改業務程式碼，而是透過以下方式回饋：

- **更新儀表板**
  - `docs/KNOWLEDGE_HEALTH.md` 或對應 YAML，顯示：
    - 節點數 / 邊數
    - 孤兒元件數量
    - 重疊工作流數量
    - 斷鏈文件數量

- **通知維護者**
  - 在必要情況下，自動建立 GitHub Issue（中文說明問題和建議負責人）。

之後可以擴充「自動修補」行為，但預設只做提醒與標示。

---

## 🏗️ 目錄結構

活體知識庫預期的目錄佈局：

```text
living-knowledge-base/
│
├── knowledge/                   # 純「知識資料」，例如系統 / 子系統 / 工作流定義
│
├── runtime/                     # 操作知識的程式碼（載入、建模、診斷、輸出報告）
│   ├── build_mndoc.py
│   ├── build_knowledge_graph.py
│   ├── project_superroot.py
│   ├── diagnose_health.py
│   └── ...
│
├── pipelines/                   # 把 runtime 組合成一條完整活體流程
│   └── update_knowledge_layer.py
│
├── docs/                        # 給人類看的說明與報告
│   ├── LIVING_KNOWLEDGE_BASE.md
│   ├── generated-mndoc.yaml
│   ├── knowledge-graph.yaml
│   ├── superroot-entities.yaml
│   ├── knowledge-health-report.yaml
│   └── KNOWLEDGE_HEALTH.md
│
└── .github/workflows/           # 自動觸發活體流程
    └── living-knowledge.yml     # push / 排程時呼叫 pipelines/update_knowledge_layer.py
```

---

## ⚠️ 明確排除的範圍

本專案刻意**不**提供：

- 命令列工具（CLI）介面與參數說明
- Chatbot / Copilot / AI 助理式互動
- 「AI 驅動程式碼分析工具」的產品功能描述

如果未來需要這些能力，會以「外部系統」的方式接入，而不是混進活體知識庫本身的核心設計中。
