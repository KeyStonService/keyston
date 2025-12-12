# 無人機自治系統 API 文檔

## 概述

本文檔描述無人機/無人駕駛自治系統的 API 介面，包括飛行控制、安全監控、感測器融合等服務。

## API 端點

### 基礎 URL

```
http://localhost:8080/api/v1
```

### 認證

所有 API 請求需要包含認證令牌：

```bash
Authorization: Bearer <token>
```

---

## 1. 飛行控制 API

### 1.1 發送控制命令

**端點**: `POST /flight/control/command`

**描述**: 向飛行控制器發送控制命令

**請求體**:

```json
{
  "target_altitude": 10.0,
  "target_velocity": [1.0, 2.0, 3.0],
  "control_mode": "position"
}
```

**響應**:

```json
{
  "status": "executing",
  "motor_commands": [0.6, 0.6, 0.6, 0.6],
  "timestamp": "2025-11-26T01:57:00Z",
  "trace_id": "trace_1732514340000000001"
}
```

**狀態碼**:

- `200`: 成功
- `400`: 無效參數
- `503`: 服務不可用

### 1.2 查詢控制狀態

**端點**: `GET /flight/control/status`

**響應**:

```json
{
  "current_altitude": 9.8,
  "current_velocity": [0.9, 1.8, 2.7],
  "motor_status": "normal",
  "battery_level": 85.5,
  "timestamp": "2025-11-26T01:57:00Z"
}
```

---

## 2. 安全監控 API

### 2.1 驗證安全性

**端點**: `POST /safety/check/validate`

**描述**: 驗證當前狀態和控制命令是否安全

**請求體**:

```json
{
  "current_state": {
    "altitude": 10.0,
    "velocity": [1.0, 2.0, 3.0],
    "orientation": [0.0, 0.0, 0.0, 1.0]
  },
  "control_command": {
    "target_altitude": 15.0,
    "target_velocity": [2.0, 3.0, 4.0]
  }
}
```

**響應**:

```json
{
  "is_safe": true,
  "violation_reason": null,
  "checks": {
    "altitude_ok": true,
    "velocity_ok": true,
    "battery_ok": true
  },
  "timestamp": "2025-11-26T01:57:00Z"
}
```

### 2.2 獲取安全報告

**端點**: `GET /safety/report`

**響應**:

```json
{
  "total_violations": 5,
  "sensor_errors": 2,
  "control_errors": 1,
  "recent_violations": [
    {
      "timestamp": "2025-11-26T01:56:00Z",
      "category": "safety_violation",
      "severity": "CRITICAL",
      "message": "Altitude exceeded: 150.00 > 100.00"
    }
  ]
}
```

---

## 3. 感測器融合 API

### 3.1 獲取融合數據

**端點**: `GET /sensor/fusion/data`

**響應**:

```json
{
  "orientation": [0.0, 0.0, 0.0, 1.0],
  "velocity": [1.0, 2.0, 3.0],
  "acceleration": [0.1, 0.2, 9.8],
  "position": [100.0, 200.0, 10.0],
  "timestamp": "2025-11-26T01:57:00Z",
  "sensors_status": {
    "imu": "active",
    "gps": "active",
    "compass": "active"
  }
}
```

---

## 4. 事件日誌 API

### 4.1 查詢事件

**端點**: `GET /events/query`

**查詢參數**:

- `category`: 事件分類 (sensor_error, control_error, safety_violation, etc.)
- `severity`: 嚴重性 (INFO, WARN, ERROR, CRITICAL)
- `start_time`: 開始時間 (ISO 8601)
- `end_time`: 結束時間 (ISO 8601)
- `limit`: 返回數量限制 (預設: 100)

**響應**:

```json
{
  "total": 150,
  "events": [
    {
      "timestamp": "2025-11-26T01:57:00Z",
      "category": "sensor_error",
      "module": "sensor_fusion",
      "severity": "WARN",
      "message": "IMU calibration drift detected",
      "trace_id": "trace_1732514341000000002",
      "metadata": {
        "drift_value": 0.05,
        "threshold": 0.03
      }
    }
  ]
}
```

### 4.2 導出日誌

**端點**: `GET /events/export`

**查詢參數**:

- `format`: 導出格式 (json, csv)
- `start_time`: 開始時間
- `end_time`: 結束時間

**響應**: 文件下載

---

## 5. 治理 API

### 5.1 驗證 API 契約

**端點**: `POST /governance/validate`

**請求體**:

```json
{
  "module_name": "flight_controller",
  "input_data": {
    "target_altitude": 10.0,
    "target_velocity": [1.0, 2.0, 3.0]
  }
}
```

**響應**:

```json
{
  "valid": true,
  "errors": [],
  "warnings": []
}
```

### 5.2 獲取治理報告

**端點**: `GET /governance/report`

**響應**:

```json
{
  "total_modules": 5,
  "modules": {
    "flight_controller": {
      "role": "flight_control",
      "max_latency_ms": 10.0,
      "dependencies": ["sensor_fusion", "safety_monitor"],
      "error_categories": ["sensor_error", "control_error"]
    }
  }
}
```

---

## 錯誤處理

所有 API 錯誤響應遵循以下格式：

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "target_altitude",
      "reason": "Value must be between 0 and 100"
    },
    "trace_id": "trace_1732514342000000003"
  }
}
```

### 錯誤碼

| 錯誤碼               | HTTP 狀態 | 描述         |
| -------------------- | --------- | ------------ |
| VALIDATION_ERROR     | 400       | 參數驗證失敗 |
| AUTHENTICATION_ERROR | 401       | 認證失敗     |
| AUTHORIZATION_ERROR  | 403       | 無權限       |
| NOT_FOUND            | 404       | 資源不存在   |
| RATE_LIMIT_EXCEEDED  | 429       | 請求過於頻繁 |
| INTERNAL_ERROR       | 500       | 內部錯誤     |
| SERVICE_UNAVAILABLE  | 503       | 服務不可用   |

---

## 速率限制

| 端點           | 限制        |
| -------------- | ----------- |
| 飛行控制 API   | 100 請求/秒 |
| 安全監控 API   | 50 請求/秒  |
| 感測器融合 API | 200 請求/秒 |
| 事件日誌 API   | 20 請求/秒  |
| 治理 API       | 10 請求/秒  |

---

## WebSocket API

### 實時事件訂閱

**端點**: `ws://localhost:8080/ws/events`

**訂閱消息**:

```json
{
  "action": "subscribe",
  "categories": ["sensor_error", "safety_violation"],
  "severity": ["WARN", "ERROR", "CRITICAL"]
}
```

**事件消息**:

```json
{
  "type": "event",
  "data": {
    "timestamp": "2025-11-26T01:57:00Z",
    "category": "safety_violation",
    "severity": "CRITICAL",
    "message": "Altitude exceeded"
  }
}
```

---

## SDK 範例

### Python SDK

```python
from autonomy_client import AutonomyClient

# 創建客戶端
client = AutonomyClient(
    base_url="http://localhost:8080",
    api_key="your_api_key"
)

# 發送控制命令
response = client.flight_control.send_command(
    target_altitude=10.0,
    target_velocity=[1.0, 2.0, 3.0]
)

# 驗證安全性
is_safe = client.safety.validate(
    current_state={...},
    control_command={...}
)

# 查詢事件
events = client.events.query(
    category="sensor_error",
    severity="WARN"
)
```

### JavaScript SDK

```javascript
import { AutonomyClient } from '@synergymesh/autonomy-client';

// 創建客戶端
const client = new AutonomyClient({
  baseUrl: 'http://localhost:8080',
  apiKey: 'your_api_key',
});

// 發送控制命令
const response = await client.flightControl.sendCommand({
  targetAltitude: 10.0,
  targetVelocity: [1.0, 2.0, 3.0],
});

// 訂閱實時事件
client.events.subscribe({
  categories: ['sensor_error', 'safety_violation'],
  onEvent: (event) => {
    console.log('Received event:', event);
  },
});
```

---

## 測試環境

測試環境 URL: `https://test.autonomy.synergymesh.com/api/v1`

測試 API 密鑰請聯繫：<team@synergymesh.com>

---

## 更新日誌

### v1.0.0 (2025-11-26)

- 初始版本發布
- 基礎飛行控制 API
- 安全監控 API
- 事件日誌 API
- 治理 API

---

## 支援

如有問題或建議，請聯繫：

- Email: <team@synergymesh.com>
- GitHub Issues: <https://github.com/we-can-fix/synergymesh/issues>
