# Security & Observability Skeleton

## 目的

本 skeleton 定義整個平台的安全模型與可觀測性標準，包括：

- **身份驗證與授權**：OAuth2, RBAC, ABAC 策略
- **審計日誌**：所有敏感操作的記錄要求
- **可觀測性三支柱**：Logs, Metrics, Traces 的標準格式與採集策略
- **安全掃描**：靜態/動態安全測試的整合點

## AI 在進行以下操作時必須使用本 skeleton

- 設計新的 API endpoint 或服務
- 新增資料存取邏輯
- 修改認證/授權流程
- 規劃監控與告警策略

## 核心問題

- 這個操作需要什麼權限？
- 如何記錄此操作以便審計？
- 如何觀測此服務的健康狀態與性能？
- 是否存在安全漏洞風險？

## 非目標

- 不負責具體的身份提供者實作（交由 identity-tenancy）
- 不負責成本優化（交由 cost-management）
