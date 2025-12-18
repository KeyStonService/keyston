# API Governance Skeleton

## 目的

本 skeleton 定義 API 的設計、版本管理與相容性策略，包括：

- **API 設計原則**：RESTful/gRPC 設計規範、命名慣例
- **版本管理**：兼容性政策、遷移策略、棄用流程
- **文件與契約**：OpenAPI/gRPC proto 定義、自動驗證
- **向後相容**：破壞性變更檢測、客戶端支援政策

## AI 在進行以下操作時必須使用本 skeleton

- 設計新 API 或端點
- 修改既有 API 契約
- 規劃 API 版本升級
- 定義跨服務 API 依賴

## 核心問題

- 這個 API 變更是否破壞了相容性？
- 是否需要開新版本？
- 客戶端需要多久時間適配？
- 如何優雅地棄用舊版本？

## 非目標

- 不負責 API 安全（交由 security-observability）
- 不負責資料模型（交由 data-governance）
- 不負責效能優化（交由 performance-reliability）
