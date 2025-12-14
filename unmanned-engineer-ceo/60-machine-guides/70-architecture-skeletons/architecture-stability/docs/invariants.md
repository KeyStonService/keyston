# Architecture Invariants (架構不變條件)

## 分層不變條件

### INV-001: 單向依賴原則
**規則**: 依賴關係必須由外向內，禁止反向依賴
**層級順序**: applications → agents → services → platform → core

**示例**:
- ✅ 允許: `services/billing` → `platform/foundation/security`
- ❌ 禁止: `platform/foundation/security` → `services/billing`

### INV-002: 同層隔離原則
**規則**: 同一層級的模組不得直接依賴，必須通過 API/Event
**適用層級**: services, agents

**示例**:
- ❌ 禁止: `services/billing` 直接 import `services/user`
- ✅ 允許: `services/billing` 通過 HTTP API 調用 `services/user`

### INV-003: Core 穩定性原則
**規則**: core 層只能依賴標準庫和明確聲明的外部依賴
**禁止**: core 依賴 platform/services/agents/applications

## 資料存取不變條件

### INV-004: 資料所有權原則
**規則**: 每個 service 擁有自己的資料庫，其他 service 不得直接存取
**例外**: 通過明確定義的 Read Model 或 Event Store

### INV-005: 共享資料原則
**規則**: 跨服務共享資料必須通過以下方式之一：
- API 調用
- Event 訂閱
- 專用的 Read Model (CQRS)

## 整合不變條件

### INV-006: 非同步優先原則
**規則**: 跨服務的資料變更必須使用 Event，同步 API 僅用於查詢
**例外**: 關鍵路徑的即時查詢 (需要在 ADR 中說明)

### INV-007: 向後相容原則
**規則**: 所有公開介面 (API/Event Schema) 必須維持向後相容
**破壞性變更**: 必須開啟新版本並維護遷移期

## 安全不變條件

### INV-008: 零信任原則
**規則**: 所有跨邊界調用必須驗證身份與權限
**邊界定義**: service 邊界、tenant 邊界、network 邊界
