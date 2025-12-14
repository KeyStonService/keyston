# 🧬 Services - 服務層 / Service Layer

## 概述 / Overview

`services/` 目錄包含所有微服務、代理和 MCP 伺服器，負責各種業務邏輯的實現。

The `services/` directory contains all microservices, agents, and MCP servers, responsible for implementing various business logic.

---

## 📁 目錄結構 / Directory Structure

```
services/
├── README.md                           # 服務層總說明
│
├── 🤖 agents/                          # 智能代理
│   ├── README.md
│   ├── auto-repair-agent/              # 自動修復代理
│   │   ├── index.ts
│   │   ├── repair_engine.ts
│   │   └── ...
│   │
│   ├── code-analyzer-agent/            # 程式碼分析代理
│   │   ├── index.ts
│   │   ├── analyzer.ts
│   │   └── ...
│   │
│   ├── dependency-manager-agent/       # 依賴管理代理
│   │   ├── index.ts
│   │   ├── dependency_resolver.ts
│   │   └── ...
│   │
│   ├── orchestrator-agent/             # 編排代理
│   │   ├── index.ts
│   │   ├── orchestration_engine.ts
│   │   └── ...
│   │
│   ├── vulnerability-detector-agent/   # 漏洞檢測代理
│   │   ├── index.ts
│   │   ├── detector.ts
│   │   └── ...
│   │
│   └── shared/                         # 共用工具
│       ├── base-agent.ts
│       └── utils.ts
│
├── 🔌 mcp/                             # MCP 伺服器
│   ├── README.md
│   ├── contract-analysis-mcp/          # 合約分析 MCP
│   ├── code-intelligence-mcp/          # 程式碼智能 MCP
│   ├── system-health-mcp/              # 系統健康 MCP
│   └── ...
│
└── api/                                # API 服務
    ├── rest-api/                       # REST API
    ├── graphql-api/                    # GraphQL API (可選)
    └── websocket-api/                  # WebSocket API (可選)
```

---

## 🔑 核心服務 / Core Services

### 代理服務 (Agent Services)

#### 1. 自動修復代理 (Auto-Repair Agent)
- 自動檢測和修復程式碼問題
- CI/CD 失敗自動恢復
- 缺陷自動補丁

#### 2. 程式碼分析代理 (Code Analyzer Agent)
- 程式碼品質分析
- 複雜度評估
- 效能瓶頸檢測

#### 3. 依賴管理代理 (Dependency Manager)
- 依賴版本更新
- 安全漏洞掃描
- 相容性檢查

#### 4. 編排代理 (Orchestrator)
- 多代理協調
- 工作流管理
- 資源分配

#### 5. 漏洞檢測代理 (Vulnerability Detector)
- 安全漏洞掃描
- 風險等級評估
- 修復建議

### MCP 伺服器 (MCP Servers)

提供與 Claude、Copilot 等 AI 工具集成的接口。

---

## 🚀 使用指南 / Usage Guide

### 啟動代理 / Starting Agents

```bash
# 啟動所有代理
npm start --workspace services/agents

# 或啟動特定代理
npm start --workspace services/agents/auto-repair-agent
npm start --workspace services/agents/code-analyzer-agent
```

### 啟動 MCP 伺服器 / Starting MCP Servers

```bash
cd mcp-servers
npm install
npm start

# 或啟動特定 MCP 伺服器
npm start --workspace mcp-servers/contract-analysis
```

### API 調用 / API Calls

```bash
# 自動修復請求
curl -X POST http://localhost:3001/api/agents/repair \
  -H "Content-Type: application/json" \
  -d '{"issue": "...", "repo": "..."}'

# 程式碼分析請求
curl -X POST http://localhost:3001/api/agents/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "...", "language": "typescript"}'
```

---

## 🔄 代理生命週期 / Agent Lifecycle

```
初始化 (Init)
    ↓
監聽任務 (Listen for Tasks)
    ↓
執行任務 (Execute Task)
    ↓
報告結果 (Report Results)
    ↓
清理資源 (Cleanup)
```

---

## 📊 代理通訊協議 / Agent Communication Protocol

### 消息格式 (Message Format)
```json
{
  "agent_id": "repair-agent-1",
  "task_id": "task-123",
  "action": "repair",
  "payload": {
    "issue": "...",
    "context": "..."
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### 回應格式 (Response Format)
```json
{
  "status": "success|failure",
  "result": "...",
  "metrics": {
    "duration_ms": 1234,
    "operations": 5
  }
}
```

---

## 🔒 安全 & 認證 / Security & Authentication

### API 金鑰認證
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:3001/api/agents/repair
```

### OAuth2 (可選)
支持 GitHub、Google、Microsoft 登錄。

### JWT Token
```bash
# 獲取 Token
POST /auth/login
Content-Type: application/json

{
  "username": "user",
  "password": "password"
}
```

---

## 📈 監控 & 日誌 / Monitoring & Logging

### 代理度量 (Agent Metrics)
```
agent_requests_total        # 總請求數
agent_requests_duration_ms  # 請求耗時
agent_success_rate          # 成功率
agent_errors_total          # 錯誤總數
```

### 查看日誌 / View Logs
```bash
# Docker
docker logs -f synergymesh-agents

# Kubernetes
kubectl logs -f deployment/synergymesh-agents -n synergymesh
```

---

## 🧪 測試 / Testing

### 單元測試 / Unit Tests
```bash
npm test --workspace services/agents
```

### 整合測試 / Integration Tests
```bash
npm run test:integration --workspace services/agents
```

### 端到端測試 / E2E Tests
```bash
npm run test:e2e --workspace services/agents
```

---

## 📦 部署 / Deployment

### Docker 部署
```bash
docker build -t synergymesh-services:latest .
docker-compose up -d
```

### Kubernetes 部署
```bash
kubectl apply -f services/k8s/

# 驗證部署
kubectl get pods -n synergymesh
kubectl get svc -n synergymesh
```

### 伸縮 / Scaling
```bash
# 手動伸縮
kubectl scale deployment synergymesh-agents --replicas=3 -n synergymesh

# 自動伸縮
kubectl autoscale deployment synergymesh-agents --min=2 --max=10 -n synergymesh
```

---

## 🔄 健康檢查 / Health Check

```bash
# 檢查代理狀態
curl http://localhost:3001/health

# 檢查特定代理
curl http://localhost:3001/health/repair-agent
```

---

## 📖 詳細文檔 / Detailed Documentation

- [代理文檔](./agents/README.md)
- [MCP 伺服器](./mcp/README.md)
- [API 參考](./api/README.md)

---

## 🤝 貢獻指南 / Contributing

在添加新服務時：

1. 遵循代理框架
2. 實現完整測試
3. 添加健康檢查
4. 更新文檔

---

## 📞 支援 / Support

- 📖 [服務文檔](./README.md)
- 🐛 [報告問題](https://github.com/SynergyMesh-admin/Unmanned-Island/issues)
- 💬 [討論](https://github.com/SynergyMesh-admin/Unmanned-Island/discussions)

