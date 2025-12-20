# ai

## 目錄職責

此目錄為 MachineNativeOps 的 **AI 執行層**，負責機器學習/LLM 推論、語意搜尋與向量操作、AI 自動化與編排。作為系統的智能能力核心，它與 `src/core/`（mind_matrix 認知層）和 `src/services/mcp/`（MCP 工具調用）緊密協作。

## 子目錄說明

### AI 代理集合 (agents/)

| 子目錄 | 職責 |
|--------|------|
| `agents/auto-repair/` | 自動修復代理 - 代碼缺陷自動修復 |
| `agents/code-analyzer/` | 程式碼分析代理 - 代碼品質與複雜度分析 |
| `agents/vulnerability-detector/` | 漏洞檢測代理 - 安全漏洞掃描 |
| `agents/dependency-manager/` | 依賴管理代理 - 依賴更新與安全檢查 |
| `agents/orchestrator/` | 編排代理 - 多代理協調與工作流管理 |
| `agents/architect/` | 架構師代理 - 架構分析與設計建議 |
| `agents/data-scientist/` | 資料科學家代理 - 數據分析與建模 |
| `agents/devops/` | DevOps 代理 - 部署與運維自動化 |
| `agents/product-manager/` | 產品經理代理 - 需求分析與規劃 |
| `agents/qa/` | QA 代理 - 測試自動化與品質保證 |
| `agents/security/` | 安全代理 - 安全策略與合規檢查 |
| `agents/examples/` | 代理使用範例 |
| `agents/scripts/` | 代理腳本工具 |

### 其他子目錄

| 子目錄 | 職責 |
|--------|------|
| `collaboration/` | AI 協作模組 - 多代理協作框架 |
| `examples/` | 使用範例 |
| `__tests__/` | 測試套件 |

## 根目錄檔案說明

### index.ts
- **職責**：TypeScript 主入口
- **功能**：AI 模組的統一導出點

### types.ts
- **職責**：TypeScript 類型定義
- **功能**：AI 模組的共用類型定義

### island-ai-README.md
- **職責**：Island AI 文檔
- **功能**：Island AI 子系統說明

## 技術堆疊

| 技術 | 用途 |
|------|------|
| Python | 核心 AI/推理/pipeline 邏輯 |
| TypeScript | API adapter（僅薄層封裝） |
| HuggingFace | 模型/LLM (Transformers/pipelines) |
| OpenAI SDK | GPT/Embeddings |
| LangChain | AI 編排框架 |

## 模組範圍 (Scope)

**本模組負責**：
- 機器學習 / LLM 推論
- 語意搜尋與向量操作
- AI 自動化與編排（Refactor / 建議 / 分析）
- 與 Core Engine 的認知層對接

**本模組不負責**：
- 前端 UI / HTTP API（由 apps/ 或 services/ 承擔）
- 基礎設施部署（由 infrastructure/ 承擔）
- 系統全域 orchestrator（由 core.unified_integration 承擔）

## 依賴規則

**可以依賴**：
- `src/core/` - mind_matrix 認知層
- `src/services/mcp/` - MCP 工具調用

**不可依賴**：
- `apps/` - 避免 UI → AI Module 的緊耦合
- `infrastructure/` - 由 Core 或 infra 層注入執行環境

## 設計原則

1. **Python 優先**：所有核心 AI 邏輯必須以 Python 實作
2. **TypeScript 僅作 Adapter**：不在 TS 中實作 AI 推理邏輯
3. **模組化代理**：每個 AI 代理獨立運作，可單獨部署
4. **可擴展架構**：支援新增自定義代理類型

## 與其他目錄的關係

- **src/core/**：提供 mind_matrix 認知層介面
- **src/services/mcp/**：透過 MCP 調用外部工具
- **src/automation/**：作為 AI-based decision provider
- **config/**：讀取 AI 配置參數

