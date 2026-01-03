# API Examples | API 範例

HTTP request examples for the Unmanned Island System API.

Unmanned Island System API 的 HTTP 請求範例。

---

## 📖 Usage | 使用方法

### Using VS Code REST Client Extension

1. Install the [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) extension
2. Open any `.http` file
3. Click "Send Request" above the request definition
4. View response in the side panel

### Using curl

Convert the HTTP examples to curl commands:

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password"}'

# Create Resource (replace TOKEN with actual JWT)
curl -X POST http://localhost:8000/api/v1/resources \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"name":"Database Server","type":"postgresql"}'
```

### Using Postman

1. Import the OpenAPI spec from: `http://localhost:8000/api/docs`
2. Or manually create requests using these examples as reference

---

## 📚 Available Examples | 可用範例

### 1. Authentication | 認證

**File**: `login.http`

Examples:

- Login (get JWT token)
- Register new user
- Refresh token
- Logout

### 2. Resource Management | 資源管理

**File**: `create-resource.http`

Examples:

- Create resource
- Get resource by ID
- Update resource
- Delete resource
- List all resources with pagination

### 3. Task Scheduling | 任務排程

**File**: `schedule-job.http`

Examples:

- Schedule cron job (daily backup)
- Schedule one-time task
- Schedule interval task (every 5 minutes)
- Get task details
- List tasks with filtering
- Get task execution logs
- Cancel running task

### 4. Monitoring & Metrics | 監控與指標

**File**: `monitoring.http`

Examples:

- Basic health check (no auth)
- Detailed system health
- System metrics
- Time series data
- Query logs
- List system events
- Get active alerts
- System configuration
- Restart service (admin)

---

## 🔐 Authentication | 認證

Most API endpoints require authentication using JWT tokens.

大多數 API 端點需要使用 JWT token 進行認證。

### Getting a Token | 獲取 Token

```http
POST http://localhost:8000/api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "password"
}
```

### Using the Token | 使用 Token

Add the `Authorization` header to subsequent requests:

```http
GET http://localhost:8000/api/v1/resources
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 🌐 Base URLs | 基礎 URL

| Environment | URL |
|-------------|-----|
| Development | <http://localhost:8000> |
| Production | <https://api.synergymesh.io> |

---

## 📝 Request Format | 請求格式

All requests use JSON format:

```http
POST /api/v1/endpoint
Content-Type: application/json

{
  "key": "value"
}
```

---

## 📊 Response Format | 回應格式

### Success Response | 成功回應

```json
{
  "data": { ... },
  "message": "Success",
  "timestamp": "2025-12-16T23:00:00.000Z"
}
```

### Error Response | 錯誤回應

```json
{
  "error": "Error message",
  "message": "Detailed description",
  "statusCode": 400,
  "timestamp": "2025-12-16T23:00:00.000Z"
}
```

---

## 🔗 Additional Resources | 其他資源

- **Interactive Swagger UI**: <http://localhost:8000/api/docs/ui>
- **OpenAPI JSON**: <http://localhost:8000/api/docs>
- **Setup Guide**: `docs/PHASE1_SETUP_GUIDE.md`
- **API Architecture**: `docs/PHASE1_ARCHITECTURE.md`

---

## ⚠️ Important Notes | 重要提示

1. **Development Credentials**: The default admin credentials are for development only
2. **Token Expiration**: JWT tokens expire after 1 hour by default
3. **Rate Limiting**: API is rate-limited to 100 requests per 15 minutes per IP
4. **CORS**: Configured for `*` in development, restrict in production

---

**Version**: 1.0.0  
**Last Updated**: 2025-12-16  
**Status**: Phase 1 Complete
