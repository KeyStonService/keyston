# 🤖 AI Module

此目錄定義 Unmanned Island 的「AI 執行層」，負責：

- 機器學習 / LLM 推論
- 語意搜尋與向量操作
- AI 自動化與編排（Refactor / 建議 / 分析）
- 與 Core Engine 的認知層（mind_matrix）對接

---

## 1. 模組範圍（Scope）

AI Module 聚焦在「AI 能力本身」，不負責：

- 前端 UI / HTTP API（由 `apps/` 或 `services/` 承擔）
- 基礎設施部署（由 `infrastructure/` 承擔）
- 系統全域 orchestrator（由 `core.unified_integration` 承擔）

主要子模組（未來將逐步填滿）：

- `runtime/` — 推論執行環境（LLM / embedding / 模型容器）
- `pipelines/` — AI 工作流與多步推理（例如：Refactor → Review → Plan）
- `agents/` — 長生命週期 AI Agent（Code Refactor、Auto-Fix、Analyzer）
- `adapters/` — 與 core.mind_matrix / services.mcp / 外部 API 的橋接層
- `tests/` — 測試與驗證（回歸測試、品質評估）

---

## 2. 技術堆疊（Language & Framework）

- **主要語言**：Python
  - 所有核心 AI / 推理 / pipeline 邏輯必須以 Python 實作
- **可能輔助**：TypeScript（只做 API adapter，不放演算法）

**框架：**

- 模型 / LLM：
  - HuggingFace（Transformers / pipelines）
  - OpenAI SDK（GPT / Embeddings）
- 編排：
  - LangChain 或等價框架（可替換）
- 測試與評估：
  - pytest
  - 自定義 eval pipeline

**用途：**

- 模型訓練（僅限必要部分，建議放在獨立 pipeline）
- 線上推論（inference）
- 語言治理 / Refactor 建議
- 其他需要推理能力的高階服務

---

## 3. 語言與架構約束（Governance）

- 本模組的 **事實語言為 Python**：
  - `.py` 為主，禁止在此目錄新增：
    - PHP / Ruby / Go / C++ 等非 AI 相關語言
- 如需 TypeScript：
  - 僅能放在 `adapters/`，作為呼叫 AI Module 的薄層 API / client
  - 不得在 TS 中實作 AI 推理邏輯

跨模組依賴規則（建議）：

- ✅ 可以依賴：
  - `core.mind_matrix`（透過定義良好的介面）
  - `services.mcp`（工具列舉 / 調用）
- ⛔ 不可直接依賴：
  - `apps/web`（避免 UI → AI Module 的緊耦合）
  - `infrastructure/`（由 Core 或 infra 層注入執行環境）

---

## 4. 對外接口（Integration Points）

AI Module 預期提供下列能力給其他層使用：

- `core.mind_matrix`：
  - LLM 推論入口（completion / chat）
  - 模型評估（metrics / regression test）
  - 語意查詢（向量搜索）

- `services.*`：
  - 透過 API 或 RPC 呼叫特定任務（例如：Refactor Plan 生成、架構建議）

- `automation.*`：
  - 作為 AI-based decision/plan provider（例如 hyperautomation 的決策建議）

未來會以：

- Python package (`ai` 或 `unmanned_ai`)
- HTTP/gRPC API（由 services 層封裝）

的形式暴露出去。

---

## 5. 參考文件

- 語言堆疊與治理：
  - `docs/architecture/language-stack.md`
  - `config/system-module-map.yaml`（AI module 相關段落）
- AI 整合：
  - `docs/AI/`（整體 AI 策略與整合指南）
  - `docs/refactor_playbooks/03_refactor/`（AI Refactor 劇本）
