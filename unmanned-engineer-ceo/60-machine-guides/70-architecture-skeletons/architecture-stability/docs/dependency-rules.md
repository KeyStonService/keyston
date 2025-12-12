# Dependency Rules (依賴規則)

## 直接依賴規則

### DR-001: Import 路徑規範

**規則**: 使用絕對路徑 import，禁止相對路徑跨層級

```typescript
// ✅ 正確
import { User } from '@core/domain/user';
import { AuthService } from '@platform/foundation/security';

// ❌ 錯誤
import { User } from '../../../core/domain/user';
```

### DR-002: 循環依賴禁止

**規則**: 任何層級不得形成循環依賴 **檢測**: 使用 `madge` 或
`dependency-cruiser`

### DR-003: 外部依賴審查

**規則**: 新增外部依賴需要在 ADR 中說明理由 **審查點**:
package.json 變更時自動觸發檢查

## 網路依賴規則

### DR-004: API 依賴聲明

**規則**: 跨服務依賴必須在 `dependencies.yaml` 中聲明

```yaml
service: billing-api
dependencies:
  - service: user-api
    type: http
    endpoints:
      - GET /v1/users/{id}
      - POST /v1/users/validate
```

### DR-005: Event 依賴聲明

**規則**: Event 訂閱必須在 `event-subscriptions.yaml` 中聲明

```yaml
service: billing-api
subscriptions:
  - topic: user.created
    version: v1
    handler: handleUserCreated
```

## 共享庫規則

### DR-006: 共享庫範圍

**允許的共享庫**:

- `platform/foundation/types` - 通用型別定義
- `platform/foundation/utils` - 純函數工具
- `platform/governance/api/client-sdk` - API 客戶端

**禁止的共享**:

- 業務邏輯
- 有狀態的類別
- 資料庫連接

### DR-007: 版本管理

**規則**: 共享庫必須語意化版本管理 **破壞性變更**: 必須發布新的 major 版本

```json
{
  "name": "@platform/foundation-types",
  "version": "2.0.0"
}
```
