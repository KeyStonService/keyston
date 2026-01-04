# ChatOps API 文檔

## 概述

本目錄包含 ChatOps Platform 的 API 文檔。

## 文件結構

```
api/
├── openapi.yaml      # OpenAPI 3.1 規範
├── README.md         # 本文件
└── examples/         # API 使用示例
```

## 查看文檔

### 使用 Swagger UI

```bash
# Docker 方式
docker run -p 8081:8080 \
  -e SWAGGER_JSON=/api/openapi.yaml \
  -v $(pwd)/docs/api:/api \
  swaggerapi/swagger-ui

# 訪問 http://localhost:8081
```

### 使用 Redoc

```bash
# Docker 方式
docker run -p 8082:80 \
  -v $(pwd)/docs/api/openapi.yaml:/usr/share/nginx/html/openapi.yaml \
  -e SPEC_URL=openapi.yaml \
  redocly/redoc

# 訪問 http://localhost:8082
```

### 使用 Stoplight Studio

1. 下載 [Stoplight Studio](https://stoplight.io/studio)
2. 打開 `docs/api/openapi.yaml`

## API 端點概覽

### 健康檢查
| 方法 | 端點 | 描述 |
|------|------|------|
| GET | `/health` | 健康檢查 |
| GET | `/ready` | 就緒檢查 |

### 消息管理
| 方法 | 端點 | 描述 |
|------|------|------|
| GET | `/api/v1/messages` | 列出消息 |
| POST | `/api/v1/messages` | 創建消息 |
| GET | `/api/v1/messages/{id}` | 獲取消息 |
| DELETE | `/api/v1/messages/{id}` | 刪除消息 |
| GET | `/api/v1/messages/{id}/status` | 獲取狀態 |

### 工作流
| 方法 | 端點 | 描述 |
|------|------|------|
| GET | `/api/v1/workflows` | 列出工作流 |
| POST | `/api/v1/workflows` | 創建工作流 |
| POST | `/api/v1/workflows/{id}/execute` | 執行工作流 |

### 通知
| 方法 | 端點 | 描述 |
|------|------|------|
| POST | `/api/v1/notifications` | 發送通知 |

### Webhooks
| 方法 | 端點 | 描述 |
|------|------|------|
| GET | `/api/v1/webhooks` | 列出 Webhooks |
| POST | `/api/v1/webhooks` | 創建 Webhook |

## 認證

API 使用 JWT Bearer Token 認證:

```bash
curl -X GET https://api.chatops.example.com/api/v1/messages \
  -H "Authorization: Bearer <your-token>"
```

## 速率限制

| 類型 | 限制 |
|------|------|
| 標準用戶 | 100 請求/分鐘 |
| 高級用戶 | 1000 請求/分鐘 |

響應頭:
- `X-RateLimit-Limit`: 總限制
- `X-RateLimit-Remaining`: 剩餘請求數
- `X-RateLimit-Reset`: 重置時間

## 錯誤處理

所有錯誤返回統一格式:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request",
    "details": [
      {
        "field": "content",
        "error": "required"
      }
    ]
  }
}
```

### 常見錯誤碼

| HTTP 狀態碼 | 錯誤碼 | 描述 |
|-------------|--------|------|
| 400 | BAD_REQUEST | 請求格式錯誤 |
| 401 | UNAUTHORIZED | 未認證 |
| 403 | FORBIDDEN | 無權限 |
| 404 | NOT_FOUND | 資源不存在 |
| 422 | VALIDATION_ERROR | 驗證失敗 |
| 429 | RATE_LIMITED | 請求過於頻繁 |
| 500 | INTERNAL_ERROR | 服務器錯誤 |

## 版本控制

API 使用 URL 路徑版本控制:
- v1: `/api/v1/*`
- v2: `/api/v2/*` (計劃中)

## SDK

官方 SDK:
- Python: `pip install chatops-sdk`
- Node.js: `npm install @chatops/sdk`
- Go: `go get github.com/chatops/sdk-go`

## 更新日誌

### v1.0.0 (2024-01-15)
- 初始版本
- 消息管理 API
- 工作流 API
- 通知 API
- Webhook 支持
