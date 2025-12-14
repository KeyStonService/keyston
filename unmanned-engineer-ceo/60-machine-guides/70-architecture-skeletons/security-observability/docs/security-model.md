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
```yaml
access_token:
  lifetime: 1h
  refresh: true
  
refresh_token:
  lifetime: 30d
  rotation: true  # 每次使用後輪換
  
api_key:
  lifetime: never  # 不過期，但可撤銷
```

## 授權 (Authorization)

### RBAC (Role-Based Access Control)
```yaml
roles:
  - id: admin
    permissions:
      - "*"  # 所有權限
  
  - id: developer
    permissions:
      - "project:read"
      - "project:write"
      - "deployment:read"
      - "deployment:create"
  
  - id: viewer
    permissions:
      - "project:read"
      - "deployment:read"
```

### ABAC (Attribute-Based Access Control)
```yaml
policies:
  - name: tenant-isolation
    description: 用戶只能存取自己租戶的資源
    condition: |
      resource.tenant_id == user.tenant_id
  
  - name: project-member
    description: 只有專案成員可以存取專案資源
    condition: |
      user.id IN resource.project.members
```

## 審計 (Audit)

### 審計事件
所有以下操作必須記錄:
- 資源的 CREATE / UPDATE / DELETE
- 權限變更
- 敏感資料存取
- 認證失敗

### 審計日誌格式
```json
{
  "timestamp": "2024-12-04T10:30:00Z",
  "event_type": "resource.update",
  "actor": {
    "type": "user",
    "id": "usr_abc123",
    "ip": "203.0.113.1"
  },
  "resource": {
    "type": "project",
    "id": "prj_xyz789",
    "tenant_id": "tnt_def456"
  },
  "action": "update",
  "changes": {
    "name": {
      "old": "Old Project Name",
      "new": "New Project Name"
    }
  },
  "result": "success"
}
```
