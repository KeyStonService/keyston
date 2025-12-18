# Identity & Tenancy Skeleton

## 目的

本 skeleton 定義身份模型與多租戶架構，包括：

- **身份類型**：User, Service Account, API Key
- **租戶模型**：Tenant, Project, Organization 層級結構
- **隔離策略**：資料隔離、資源配額、網路隔離
- **身份聯邦**：SSO, SAML, OAuth2 整合

## AI 在進行以下操作時必須使用本 skeleton

- 設計多租戶資料模型
- 規劃身份驗證流程
- 配置資源隔離策略
- 設計跨租戶協作機制

## 核心問題

- 這個資源屬於哪個租戶？
- 如何防止租戶間資料洩漏？
- 如何處理跨租戶的協作場景？
