# API 治理骨架 / API Governance Skeleton

## 簡介

定義 API 設計標準、版本管理策略、合約驗證、向後相容性。AI 在設計 API 或管理 API 生命週期時查詢此骨架。

## 責任

- ✅ API 設計規範、版本管理、合約驗證、向後相容
- ❌ 認證授權 ← Identity & Tenancy
- ❌ 性能優化 ← Performance & Reliability

## 核心原則

- **OpenAPI 優先**：所有 API 必須有 OpenAPI 規範
- **語義版本**：遵循 Semantic Versioning
- **長期支持**：至少 2 個版本的並行支持
- **可演進性**：設計易於擴展的 API
