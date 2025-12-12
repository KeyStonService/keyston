# 自動化專責負責人員系統 API 文檔

# Auto-Assignment System API Documentation

## 概述 (Overview)

自動化專責負責人員系統提供智慧化的問題分派與責任管理功能，支援多維度分析、負載平衡、SLA 監控與自動升級機制。

The Auto-Assignment System provides intelligent problem assignment and
responsibility management with multi-dimensional analysis, load balancing, SLA
monitoring, and automatic escalation.

## 基礎 URL (Base URL)

```
http://localhost:3000/api/v1/assignment
```

## 認證 (Authentication)

目前版本不需要認證。未來版本將支援 JWT 令牌認證。

Current version does not require authentication. Future versions will support
JWT token authentication.

---

## API 端點 (Endpoints)

### 1. 創建分派 (Create Assignment)

自動分析問題並分派給最適合的負責人。

Automatically analyzes the incident and assigns to the most suitable owner.

**端點 (Endpoint):** `POST /api/v1/assignment/assign`

**請求體 (Request Body):**

```json
{
  "type": "BACKEND_API",
  "priority": "HIGH",
  "description": "API endpoint returning 500 errors",
  "errorMessage": "Internal Server Error in /api/users",
  "affectedFiles": ["src/api/users.ts"]
}
```

**參數說明 (Parameters):**

| 參數 (Field)    | 類型 (Type)   | 必填 (Required) | 說明 (Description)                                                                                       |
| --------------- | ------------- | --------------- | -------------------------------------------------------------------------------------------------------- |
| `type`          | `ProblemType` | Yes             | 問題類型：`FRONTEND_ERROR`, `BACKEND_API`, `DATABASE_ISSUE`, `PERFORMANCE`, `SECURITY`, `INFRASTRUCTURE` |
| `priority`      | `Priority`    | Yes             | 優先級：`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`                                                              |
| `description`   | `string`      | Yes             | 問題描述 (Incident description)                                                                          |
| `errorMessage`  | `string`      | No              | 錯誤訊息 (Error message)                                                                                 |
| `affectedFiles` | `string[]`    | No              | 受影響的檔案 (Affected files)                                                                            |

**回應 (Response):**

```json
{
  "success": true,
  "data": {
    "assignment": {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "incidentId": "incident-1732491234567",
      "primaryOwner": {
        "id": "david.zhang",
        "name": "David Zhang",
        "email": "david.zhang@synergymesh.dev",
        "specialties": ["node.js", "python", "api", "database"],
        "timezone": "Asia/Taipei"
      },
      "secondaryOwner": {
        "id": "eva.wu",
        "name": "Eva Wu",
        "email": "eva.wu@synergymesh.dev",
        "specialties": ["node.js", "database", "performance"],
        "timezone": "Asia/Taipei"
      },
      "status": "ASSIGNED",
      "assignedAt": "2025-11-24T23:30:00.000Z",
      "slaTarget": {
        "responseTime": 15,
        "resolutionTime": 240
      }
    },
    "incident": {
      "id": "incident-1732491234567",
      "type": "BACKEND_API",
      "priority": "HIGH",
      "description": "API endpoint returning 500 errors",
      "errorMessage": "Internal Server Error in /api/users",
      "affectedFiles": ["src/api/users.ts"],
      "createdAt": "2025-11-24T23:30:00.000Z"
    }
  }
}
```

**SLA 目標時間 (SLA Target Times):**

| 優先級 (Priority) | 回應時間 (Response Time) | 解決時間 (Resolution Time) |
| ----------------- | ------------------------ | -------------------------- |
| CRITICAL          | 5 分鐘                   | 60 分鐘                    |
| HIGH              | 15 分鐘                  | 240 分鐘                   |
| MEDIUM            | 60 分鐘                  | 480 分鐘                   |
| LOW               | 240 分鐘                 | 1440 分鐘                  |

---

### 2. 查詢分派狀態 (Get Assignment Status)

查詢特定分派的詳細狀態。

Get detailed status of a specific assignment.

**端點 (Endpoint):** `GET /api/v1/assignment/status/:id`

**路徑參數 (Path Parameters):**

- `id`: 分派 ID (Assignment ID)

**回應 (Response):**

```json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "incidentId": "incident-1732491234567",
    "primaryOwner": {
      "id": "david.zhang",
      "name": "David Zhang",
      "email": "david.zhang@synergymesh.dev",
      "specialties": ["node.js", "python", "api", "database"],
      "timezone": "Asia/Taipei"
    },
    "status": "IN_PROGRESS",
    "assignedAt": "2025-11-24T23:30:00.000Z",
    "acknowledgedAt": "2025-11-24T23:32:00.000Z",
    "startedAt": "2025-11-24T23:35:00.000Z",
    "slaTarget": {
      "responseTime": 15,
      "resolutionTime": 240
    }
  }
}
```

---

### 3. 更新分派狀態 (Update Assignment Status)

更新分派的處理狀態。

Update the processing status of an assignment.

**端點 (Endpoint):** `POST /api/v1/assignment/status/:id`

**路徑參數 (Path Parameters):**

- `id`: 分派 ID (Assignment ID)

**請求體 (Request Body):**

```json
{
  "status": "IN_PROGRESS"
}
```

**可用狀態 (Available Statuses):**

- `ASSIGNED`: 已分派 (Assigned)
- `ACKNOWLEDGED`: 已確認 (Acknowledged)
- `IN_PROGRESS`: 處理中 (In Progress)
- `ESCALATED`: 已升級 (Escalated)
- `RESOLVED`: 已解決 (Resolved)

**回應 (Response):**

```json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "status": "IN_PROGRESS",
    "startedAt": "2025-11-24T23:35:00.000Z"
  }
}
```

---

### 4. 查詢工作負載 (Get Workload Statistics)

查詢所有團隊成員的工作負載統計。

Get workload statistics for all team members.

**端點 (Endpoint):** `GET /api/v1/assignment/workload`

**回應 (Response):**

```json
{
  "success": true,
  "data": [
    {
      "memberId": "david.zhang",
      "activeAssignments": 3,
      "totalAssignments": 15,
      "averageResolutionTime": 120,
      "successRate": 0.92
    },
    {
      "memberId": "eva.wu",
      "activeAssignments": 2,
      "totalAssignments": 12,
      "averageResolutionTime": 95,
      "successRate": 0.95
    }
  ]
}
```

---

### 5. 重新分派責任 (Reassign Responsibility)

將分派重新指派給其他團隊成員。

Reassign the assignment to a different team member.

**端點 (Endpoint):** `POST /api/v1/assignment/reassign/:id`

**路徑參數 (Path Parameters):**

- `id`: 分派 ID (Assignment ID)

**請求體 (Request Body):**

```json
{
  "newOwnerId": "eva.wu"
}
```

**可用成員 ID (Available Member IDs):**

**Frontend Team:**

- `alice.chen`, `bob.wang`, `carol.liu`

**Backend Team:**

- `david.zhang`, `eva.wu`, `frank.lin`

**DevOps Team:**

- `grace.huang`, `henry.chen`

**Security Team:**

- `iris.lee`, `jack.yang`

**回應 (Response):**

```json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "primaryOwner": {
      "id": "eva.wu",
      "name": "Eva Wu",
      "email": "eva.wu@synergymesh.dev",
      "specialties": ["node.js", "database", "performance"],
      "timezone": "Asia/Taipei"
    },
    "status": "ASSIGNED",
    "assignedAt": "2025-11-24T23:40:00.000Z"
  }
}
```

---

### 6. 升級分派 (Escalate Assignment)

將分派升級至更高層級處理。

Escalate the assignment to a higher level.

**端點 (Endpoint):** `POST /api/v1/assignment/escalate/:id`

**路徑參數 (Path Parameters):**

- `id`: 分派 ID (Assignment ID)

**回應 (Response):**

```json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "status": "ESCALATED"
  },
  "message": "Assignment escalated successfully"
}
```

---

### 7. 獲取所有分派 (Get All Assignments)

獲取系統中所有的分派記錄。

Get all assignment records in the system.

**端點 (Endpoint):** `GET /api/v1/assignment/all`

**回應 (Response):**

```json
{
  "success": true,
  "data": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "incidentId": "incident-1732491234567",
      "primaryOwner": { "id": "david.zhang", "name": "David Zhang" },
      "status": "RESOLVED",
      "assignedAt": "2025-11-24T23:30:00.000Z",
      "resolvedAt": "2025-11-24T23:45:00.000Z"
    }
  ],
  "count": 1
}
```

---

### 8. 獲取效能報告 (Get Performance Report)

獲取分派系統的整體效能統計報告。

Get overall performance statistics report.

**端點 (Endpoint):** `GET /api/v1/assignment/report`

**回應 (Response):**

```json
{
  "success": true,
  "data": {
    "totalAssignments": 50,
    "resolved": 45,
    "averageResponseTime": 12.5,
    "averageResolutionTime": 135.8,
    "slaCompliance": 92.5
  }
}
```

**指標說明 (Metrics Description):**

| 指標 (Metric)           | 說明 (Description)                                       |
| ----------------------- | -------------------------------------------------------- |
| `totalAssignments`      | 總分派數量 (Total number of assignments)                 |
| `resolved`              | 已解決數量 (Number of resolved assignments)              |
| `averageResponseTime`   | 平均回應時間（分鐘）(Average response time in minutes)   |
| `averageResolutionTime` | 平均解決時間（分鐘）(Average resolution time in minutes) |
| `slaCompliance`         | SLA 達成率（%）(SLA compliance percentage)               |

---

## 錯誤處理 (Error Handling)

### 錯誤回應格式 (Error Response Format)

```json
{
  "success": false,
  "error": "Error message description"
}
```

### 常見錯誤碼 (Common Error Codes)

| 狀態碼 (Status Code) | 說明 (Description)                                          |
| -------------------- | ----------------------------------------------------------- |
| 400                  | 驗證錯誤或參數錯誤 (Validation error or invalid parameters) |
| 404                  | 找不到指定的資源 (Resource not found)                       |
| 500                  | 伺服器內部錯誤 (Internal server error)                      |

---

## 使用範例 (Usage Examples)

### 範例 1：創建並處理分派 (Create and Process Assignment)

```bash
# 1. 創建分派
curl -X POST http://localhost:3000/api/v1/assignment/assign \
  -H "Content-Type: application/json" \
  -d '{
    "type": "BACKEND_API",
    "priority": "HIGH",
    "description": "API timeout issue",
    "errorMessage": "Gateway timeout"
  }'

# 2. 確認分派（使用回應中的 assignment.id）
curl -X POST http://localhost:3000/api/v1/assignment/status/ASSIGNMENT_ID \
  -H "Content-Type: application/json" \
  -d '{"status": "ACKNOWLEDGED"}'

# 3. 開始處理
curl -X POST http://localhost:3000/api/v1/assignment/status/ASSIGNMENT_ID \
  -H "Content-Type: application/json" \
  -d '{"status": "IN_PROGRESS"}'

# 4. 完成解決
curl -X POST http://localhost:3000/api/v1/assignment/status/ASSIGNMENT_ID \
  -H "Content-Type: application/json" \
  -d '{"status": "RESOLVED"}'
```

### 範例 2：查詢工作負載並重新分派 (Check Workload and Reassign)

```bash
# 1. 查詢工作負載
curl http://localhost:3000/api/v1/assignment/workload

# 2. 重新分派給工作量較低的成員
curl -X POST http://localhost:3000/api/v1/assignment/reassign/ASSIGNMENT_ID \
  -H "Content-Type: application/json" \
  -d '{"newOwnerId": "eva.wu"}'
```

### 範例 3：監控效能 (Monitor Performance)

```bash
# 獲取效能報告
curl http://localhost:3000/api/v1/assignment/report
```

---

## 團隊結構 (Team Structure)

### Frontend Team (前端團隊)

- **Alice Chen** (`alice.chen`): React, Vue, TypeScript, UI/UX
- **Bob Wang** (`bob.wang`): React, TypeScript, Performance
- **Carol Liu** (`carol.liu`): Vue, UI/UX, Accessibility

### Backend Team (後端團隊)

- **David Zhang** (`david.zhang`): Node.js, Python, API, Database
- **Eva Wu** (`eva.wu`): Node.js, Database, Performance
- **Frank Lin** (`frank.lin`): Python, API, Microservices

### DevOps Team (維運團隊)

- **Grace Huang** (`grace.huang`): Docker, Kubernetes, AWS, CI/CD
- **Henry Chen** (`henry.chen`): Kubernetes, Monitoring, Infrastructure

### Security Team (安全團隊)

- **Iris Lee** (`iris.lee`): Authentication, Encryption, Audit
- **Jack Yang** (`jack.yang`): Penetration Testing, Security Review, Compliance

---

## 智慧分派規則 (Intelligent Assignment Rules)

### 分派評分因素 (Assignment Scoring Factors)

1. **專業匹配度 (Expertise Match)** - 40%
   - 根據問題類型和成員專業技能計算匹配度

2. **可用性 (Availability)** - 30%
   - 根據時區和工作時間評估可用性

3. **當前工作負載 (Current Workload)** - 20%
   - 評估成員當前的活動任務數量

4. **歷史表現 (Historical Performance)** - 10%
   - 參考成員過往的成功率和解決時間

### 自動升級規則 (Auto-Escalation Rules)

根據優先級自動觸發升級：

- **無回應超時 (No Response Timeout)**: 主要負責人未確認時自動分派給備援負責人
- **無進展超時 (No Progress Timeout)**: 確認後未開始處理時升級給團隊主管
- **未解決超時 (Unresolved Timeout)**: 超過解決時間仍未完成時觸發緊急處理流程

---

## 整合建議 (Integration Recommendations)

### 與 CI/CD 整合 (CI/CD Integration)

```javascript
// 在 CI/CD 流程中自動創建分派
const response = await fetch('http://localhost:3000/api/v1/assignment/assign', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    type: 'INFRASTRUCTURE',
    priority: 'HIGH',
    description: 'Build pipeline failure',
    errorMessage: error.message,
    affectedFiles: changedFiles,
  }),
});
```

### 與監控系統整合 (Monitoring Integration)

```javascript
// 從監控告警自動創建分派
const createAssignmentFromAlert = async (alert) => {
  const incident = {
    type: mapAlertToType(alert.type),
    priority: mapSeverityToPriority(alert.severity),
    description: alert.message,
    errorMessage: alert.details,
  };

  return await assignmentClient.create(incident);
};
```

---

## 版本歷史 (Version History)

- **v1.0.0** (2025-11-24): 初始版本，包含核心分派功能
  - 智慧責任分派
  - 工作負載平衡
  - SLA 監控
  - 自動升級機制
  - 效能報告

---

## 支援與回饋 (Support & Feedback)

如有問題或建議，請聯繫：

For questions or suggestions, please contact:

- **Email**: <support@synergymesh.dev>
- **GitHub Issues**: <https://github.com/we-can-fix/synergymesh/issues>
- **Documentation**: <https://docs.synergymesh.dev>

---

**最後更新 (Last Updated)**: 2025-11-24  
**維護者 (Maintainer)**: SynergyMesh Team
