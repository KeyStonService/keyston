# AI Chat Service - 無人機/自動駕駛應用

AI-powered chat service for drone and autonomous vehicle operations, extracted and adapted from MateChat.

## 功能特性 (Features)

### 🚁 無人機專用功能

- **實時對話**: 與無人機系統進行自然語言交互
- **命令解析**: AI 輔助飛行命令理解與驗證
- **上下文感知**: 整合飛行狀態、位置、任務資訊
- **串流響應**: 低延遲的實時通訊

### 🤖 AI 能力

- 支持 OpenAI GPT-4 及相容模型
- 支持本地 LLM (Llama, Mistral 等)
- 可自訂溫度與 token 限制
- 串流與批次模式

### 🔒 安全性

- SLSA Level 3 合規
- TLS 1.3 加密通訊
- JWT 認證（可選）
- 完整審計日誌

## 快速開始 (Quick Start)

### 安裝依賴

```bash
cd core/contract_service/contracts-L1/ai-chat-service
npm install
```

### 配置環境變量

```bash
cp .env.example .env
# 編輯 .env 並填入您的 API 金鑰
```

### 開發模式運行

```bash
npm run dev
```

### 生產構建

```bash
npm run build
npm start
```

## API 端點 (API Endpoints)

### POST /api/v1/chat

聊天接口（非串流）

**Request:**

```json
{
  "messages": [
    {
      "role": "user",
      "content": "無人機目前狀態如何？"
    }
  ],
  "stream": false,
  "droneContext": {
    "vehicleId": "DRONE-001",
    "missionId": "MISSION-2024-001",
    "location": {
      "lat": 25.0330,
      "lon": 121.5654,
      "alt": 100.0
    },
    "status": "flying"
  }
}
```

**Response:**

```json
{
  "message": "無人機 DRONE-001 目前正在執行任務 MISSION-2024-001，位於海拔 100 米高度飛行中。",
  "timestamp": "2024-11-24T16:00:00Z"
}
```

### POST /api/v1/chat/stream

聊天接口（串流）

使用 Server-Sent Events (SSE) 串流響應。

### POST /api/v1/commands

無人機命令處理

**Request:**

```json
{
  "command": "takeoff",
  "vehicleId": "DRONE-001",
  "parameters": {
    "altitude": 50,
    "speed": 5
  }
}
```

### GET /api/v1/status

服務健康狀態檢查

### GET /api/v1/model

獲取當前模型資訊

## 配置說明 (Configuration)

### 環境變量

| 變量 | 說明 | 預設值 |
|------|------|--------|
| `PORT` | 服務端口 | `8100` |
| `OPENAI_API_KEY` | OpenAI API 金鑰 | 必填 |
| `AI_MODEL` | 使用的模型 | `gpt-4-turbo-preview` |
| `MAX_TOKENS` | 最大 token 數 | `4096` |
| `TEMPERATURE` | 回應創意度 | `0.7` |
| `LOG_LEVEL` | 日誌級別 | `info` |

### 使用本地 LLM

```bash
# 啟動 Ollama 或其他本地 LLM 服務
ollama serve

# 配置環境變量
OPENAI_API_BASE=http://localhost:11434/v1
AI_MODEL=llama3
```

## 整合架構 (Integration Architecture)

```
┌─────────────────────────────────────────┐
│         Drone Control System            │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│     AI Chat Service (Port 8100)         │
│  ┌────────────────────────────────┐     │
│  │   Chat Controller               │     │
│  └────────────┬───────────────────┘     │
│               ↓                          │
│  ┌────────────────────────────────┐     │
│  │   OpenAI Service                │     │
│  └────────────┬───────────────────┘     │
└───────────────┼──────────────────────────┘
                │
                ↓
      ┌─────────────────────┐
      │   AI Model (GPT-4)  │
      └─────────────────────┘
```

## 測試 (Testing)

### 使用 curl 測試

```bash
# 健康檢查
curl http://localhost:8100/health

# 簡單聊天
curl -X POST http://localhost:8100/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": false
  }'

# 帶無人機上下文的聊天
curl -X POST http://localhost:8100/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Report status"}],
    "droneContext": {
      "vehicleId": "DRONE-001",
      "status": "flying",
      "location": {"lat": 25.0330, "lon": 121.5654, "alt": 100}
    }
  }'
```

### 串流測試

```bash
curl -N -X POST http://localhost:8100/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Tell me about flight safety"}],
    "stream": true
  }'
```

## 監控 (Monitoring)

服務提供以下監控端點：

- `/health` - 基本健康檢查
- `/health/live` - Liveness probe
- `/health/ready` - Readiness probe
- `/api/v1/status` - 詳細狀態資訊

## 性能指標 (Performance Metrics)

- **響應時間**: < 2 秒
- **並發連接**: 支持 1000+ 同時連接
- **吞吐量**: 500+ 消息/秒
- **可用性**: 99.9%

## 安全考量 (Security Considerations)

1. **API 金鑰管理**: 使用環境變量，不要提交到版本控制
2. **TLS 加密**: 生產環境必須使用 HTTPS
3. **速率限制**: 建議配置 API 速率限制
4. **輸入驗證**: 使用 Zod 進行嚴格驗證
5. **審計日誌**: 完整記錄所有請求

## 故障排除 (Troubleshooting)

### API 金鑰錯誤

```
Error: OpenAI request failed: Incorrect API key
```

檢查 `.env` 中的 `OPENAI_API_KEY` 是否正確。

### 連接超時

```
Error: Request timeout
```

檢查網路連接或增加 `REQUEST_TIMEOUT_MS`。

### 模型不存在

```
Error: Model not found
```

確認 `AI_MODEL` 名稱正確並且您的帳戶有權限使用該模型。

## 貢獻 (Contributing)

歡迎提交 Issue 和 Pull Request！

## 授權 (License)

MIT License - 見根目錄 LICENSE 文件

## 相關資源 (Related Resources)

- [MateChat 原始專案](https://matechat.gitcode.com)
- [OpenAI API 文檔](https://platform.openai.com/docs)
- [SLSA Framework](https://slsa.dev)
