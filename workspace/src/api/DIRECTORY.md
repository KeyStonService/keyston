# api

## 目錄職責

此目錄為 MachineNativeOps 的 **API 層**，定義系統對外的 API 端點，包含 REST、GraphQL 和 WebSocket 三種協議的實現骨架。

## 子目錄說明

| 子目錄 | 職責 |
|--------|------|
| `rest/` | REST API 端點定義 |
| `graphql/` | GraphQL API schema 和 resolver |
| `websocket/` | WebSocket 實時通訊端點 |

## API 類型說明

### REST API

- **用途**：標準 CRUD 操作、資源管理
- **特性**：RESTful 設計原則、HTTP 動詞語義

### GraphQL API

- **用途**：彈性查詢、複雜數據獲取
- **特性**：型別安全、單一端點、按需獲取

### WebSocket API

- **用途**：實時通訊、事件推送
- **特性**：雙向通訊、低延遲、持久連接

## 目前狀態

此目錄為骨架結構，API 實現待補充。

## 設計原則

1. **協議分離**：不同協議的 API 獨立實現
2. **統一認證**：所有 API 使用統一的認證機制
3. **版本控制**：API 版本透過 URL 或 header 區分
4. **文檔自動生成**：從代碼生成 OpenAPI/GraphQL schema

## 依賴規則

**可以依賴**：

- `src/services/` - 調用業務服務
- `src/shared/` - 共用工具和類型

**不可依賴**：

- `src/core/` - API 層不應直接調用核心引擎
- `src/automation/` - API 層不應直接調用自動化

## 與其他目錄的關係

- **src/services/**：API 層調用服務層處理業務邏輯
- **contracts/**：API 合約定義在根目錄 contracts/
- **config/**：讀取 API 配置
