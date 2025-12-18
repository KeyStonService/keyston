# Security Model

## 認證 (Authentication)

### 支援的認證方式

1. **OAuth 2.0 / OpenID Connect**
   - 標準流程: Authorization Code Flow (with PKCE)
   - 用於: Web 應用、Mobile 應用

2. **API Keys**
   - 用於: Service-to-Service, CLI 工具
   - 格式: `sk_live_<random>` 或 `sk_test_<random>`
   - 存儲: Hash with bcrypt

3. **Service Account**
   - 用於: 內部服務間調用
   - 機制: JWT with RS256

### Token 管理
