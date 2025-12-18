# Tenancy Model

## 多租戶架構

### 隔離層級

#### 1. Shared (共享)

- **適用**: Free tier 用戶
- **資料庫**: 共享資料庫,用 tenant_id 區分
- **運算**: 共享容器/Pod
- **儲存**: 共享儲存,路徑前綴區分
- **成本**: 最低
- **隔離性**: 低

#### 2. Dedicated (專用)

- **適用**: Standard tier 用戶
- **資料庫**: 專用資料庫 schema
- **運算**: 專用容器 pool
- **儲存**: 專用儲存桶
- **成本**: 中等
- **隔離性**: 中

#### 3. Isolated (隔離)

- **適用**: Enterprise tier 用戶
- **資料庫**: 專用資料庫實例
- **運算**: 專用 Kubernetes namespace
- **儲存**: 專用儲存帳號
- **網路**: VPC peering 或 private link
- **成本**: 最高
- **隔離性**: 高

## Tenant Schema
