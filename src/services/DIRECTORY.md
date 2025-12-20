# services

## 目錄職責

此目錄為 MachineNativeOps 的**服務層**，包含所有微服務、智能代理（Agents）和 MCP 伺服器，負責業務邏輯的實現與系統自動化能力。

## 子目錄說明

### 智能代理服務

| 子目錄 | 職責 |
|--------|------|
| `agents/` | 智能代理集合（7 個代理） |
| `agents/auto-repair/` | 自動修復代理 - CI/CD 失敗自動恢復、缺陷自動補丁 |
| `agents/code-analyzer/` | 程式碼分析代理 - 品質分析、複雜度評估、效能瓶頸檢測 |
| `agents/dependency-manager/` | 依賴管理代理 - 版本更新、安全漏洞掃描、相容性檢查 |
| `agents/orchestrator/` | 編排代理 - 多代理協調、工作流管理、資源分配 |
| `agents/vulnerability-detector/` | 漏洞檢測代理 - 安全掃描、風險評估、修復建議 |
| `agents/architecture-reasoner/` | 架構推理代理 - 架構分析與決策 |
| `agents/recovery/` | 恢復代理 - 系統恢復與回滾 |

### 基礎服務

| 子目錄 | 職責 |
|--------|------|
| `api-gateway/` | API 閘道 - 統一入口、路由、認證、限流 |
| `auth-service/` | 認證服務 - 用戶認證、JWT Token、OAuth2 |
| `user-service/` | 用戶服務 - 用戶管理、權限控制 |
| `business-service/` | 業務服務 - 核心業務邏輯 |

### 排程與監控

| 子目錄 | 職責 |
|--------|------|
| `scheduler/` | 排程器核心 |
| `scheduler-service/` | 排程服務 - 定時任務、工作流排程 |
| `watchdog/` | 看門狗服務 - 系統監控、健康檢查、自動重啟 |

### MCP 與其他

| 子目錄 | 職責 |
|--------|------|
| `mcp/` | MCP 伺服器 - 與 Claude、Copilot 等 AI 工具整合 |
| `_scratch/` | 實驗性代碼 |

## 根目錄檔案說明

### __init__.py
- **職責**：Python 模組初始化
- **功能**：定義服務層的 Python 模組導出

### index.ts
- **職責**：TypeScript 主入口
- **功能**：服務層的主要入口點，整合各子服務

### routes.ts
- **職責**：路由定義
- **功能**：定義應用程式的 HTTP 路由規則

### static.ts
- **職責**：靜態資源處理
- **功能**：處理靜態文件服務

### storage.ts
- **職責**：儲存抽象層
- **功能**：定義 CRUD 操作介面，抽象底層儲存實現

### vite.ts
- **職責**：Vite 配置
- **功能**：開發伺服器與構建工具配置

## 代理生命週期

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

## 通訊協議

代理間使用 JSON 格式通訊：

```json
{
  "agent_id": "repair-agent-1",
  "task_id": "task-123",
  "action": "repair",
  "payload": { "issue": "...", "context": "..." },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## 設計原則

1. **微服務架構**：每個服務獨立部署、獨立擴展
2. **代理模式**：智能代理自主執行任務，減少人工介入
3. **統一閘道**：所有 API 請求通過 api-gateway 統一處理
4. **健康檢查**：每個服務提供 /health 端點

## 與其他目錄的關係

- **src/core/**：調用核心引擎的 AI 決策能力
- **src/autonomous/**：自主系統框架使用這些服務
- **config/**：讀取服務配置
- **tests/**：對應的測試代碼在 tests/unit/test_services/

