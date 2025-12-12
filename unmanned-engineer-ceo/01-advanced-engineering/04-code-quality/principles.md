# Code Quality Principles / 代碼品質原則

## 核心理念

- **SOLID**：以 TypeScript/Go/Python 具體範例說明；強調接口分離保障代理互操作。
- **Hexagonal
  Architecture**：核心邏輯 + 边界 adapter，對應 core/contract_service 的 controller/service 分層。
- **Clean Architecture**：Entities → Use Cases → Interface，支援多語言模組。
- **可觀測性優先**：每個邏輯單元必須輸出可追蹤事件。

## 對接規範

- 在 `.github/island-ai-instructions.md` 定義的 TypeScript 規則為質量閘。
- 靜態分析（ESLint, Pyright, golangci-lint）需在 `static-analysis/` 中定義。
