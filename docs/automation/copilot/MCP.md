# 模型上下文協定 (Model Context Protocol - MCP)

> **版本**: 1.0.0  
> **最後更新**: 2025-12-02

本文件描述 MCP（Model Context Protocol）整合，說明如何將 Copilot 編碼代理連接到其他工具和服務。

---

## 概述

MCP 是一種開放標準，定義了應用程式如何與大型語言模型 (LLM) 共享上下文。它提供標準化方法將 AI 模型連接到不同的資料來源和工具，使它們能夠更有效地協同工作。

```
┌─────────────────────────────────────────────────────────────────┐
│                    MCP 架構概覽                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    MCP 協議    ┌─────────────────────────────┐ │
│  │   Copilot   │◄──────────────►│     MCP Servers             │ │
│  │   Agent     │                │  • code-analyzer            │ │
│  │             │                │  • test-generator           │ │
│  │             │                │  • doc-generator            │ │
│  └─────────────┘                │  • slsa-validator           │ │
│         │                       │  • security-scanner         │ │
│         │                       │  • performance-analyzer     │ │
│         ▼                       └─────────────────────────────┘ │
│  ┌─────────────┐                                                │
│  │   GitHub    │                                                │
│  │   MCP Server│                                                │
│  └─────────────┘                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## MCP 服務器

系統提供多個專門的 MCP 服務器，每個提供特定功能：

### 可用的 MCP 服務器

| 服務器 | 路徑 | 功能 |
|--------|------|------|
| **Code Analyzer** | `mcp-servers/code-analyzer.js` | 代碼品質和複雜度分析 |
| **Test Generator** | `mcp-servers/test-generator.js` | 自動生成測試 |
| **Doc Generator** | `mcp-servers/doc-generator.js` | 文檔自動生成 |
| **SLSA Validator** | `mcp-servers/slsa-validator.js` | SLSA 溯源驗證 |
| **Security Scanner** | `mcp-servers/security-scanner.js` | 安全漏洞掃描 |
| **Performance Analyzer** | `mcp-servers/performance-analyzer.js` | 性能分析 |

---

## MCP 服務器詳解

### 1. Code Analyzer（代碼分析器）

**能力：**
- `analyze-code` - 綜合代碼品質和複雜度分析
- `detect-issues` - 問題檢測與嚴重性篩選
- `suggest-improvements` - AI 驅動的改進建議

**功能：**
- 循環複雜度和認知複雜度計算
- 安全漏洞偵測
- 性能問題識別
- 最佳實踐驗證
- 代碼異味偵測

```javascript
// 使用範例
const request = {
  name: 'analyze-code',
  arguments: {
    code: 'function example() { ... }',
    language: 'javascript',
    options: {
      checkComplexity: true,
      checkSecurity: true
    }
  }
};
```

### 2. Test Generator（測試生成器）

**能力：**
- `generate-unit-tests` - 為函數和類別生成單元測試
- `generate-integration-tests` - 生成 API 整合測試
- `generate-e2e-tests` - 生成端到端測試場景

**支援框架：**
- Jest, Mocha, Vitest (單元測試)
- Playwright, Cypress (E2E 測試)

### 3. Doc Generator（文檔生成器）

**能力：**
- `generate-jsdoc` - 生成 JSDoc 文檔
- `generate-api-docs` - 生成 API 文檔 (Markdown, OpenAPI)
- `generate-guides` - 生成綜合指南

### 4. SLSA Validator（SLSA 驗證器）

**能力：**
- `validate-provenance` - 驗證 SLSA 溯源數據
- `check-slsa-compliance` - 檢查目標 SLSA 等級合規性
- `generate-compliance-report` - 生成綜合合規報告

**支援等級：** SLSA Level 1-4

### 5. Security Scanner（安全掃描器）

**能力：**
- `scan-vulnerabilities` - 掃描安全漏洞
- `check-dependencies` - 檢查依賴項的已知 CVE
- `analyze-secrets` - 偵測暴露的密鑰和憑證

**偵測類型：**
- SQL 注入
- XSS 漏洞
- 命令注入
- 硬編碼密鑰

### 6. Performance Analyzer（性能分析器）

**能力：**
- `analyze-performance` - 分析代碼性能指標
- `identify-bottlenecks` - 識別性能瓶頸
- `suggest-optimizations` - 建議性能優化

---

## JSON MCP 配置指南

本節詳細說明如何編寫 MCP JSON 配置文件。

### 配置文件位置

MCP 配置文件通常位於：
- VS Code: `.vscode/mcp.json`
- 專案根目錄: `mcp.json`

### 配置結構

```json
{
  "servers": {
    "<server-id>": {
      "type": "<transport-type>",
      "command": "<executable>",
      "args": ["<arg1>", "<arg2>"],
      "env": {
        "<ENV_VAR>": "<value>"
      },
      "version": "<version>"
    }
  },
  "inputs": [
    {
      "id": "<input-id>",
      "type": "<input-type>",
      "description": "<description>",
      "password": <boolean>
    }
  ]
}
```

### 配置欄位說明

| 欄位 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `servers` | object | ✅ | 服務器定義集合 |
| `servers.<id>` | string | ✅ | 服務器唯一識別符 |
| `type` | string | ✅ | 傳輸類型: `stdio`, `sse`, `websocket` |
| `command` | string | ✅ | 執行命令 (如 `node`, `docker`, `python`) |
| `args` | array | ❌ | 命令參數陣列 |
| `env` | object | ❌ | 環境變數 |
| `version` | string | ❌ | 服務器版本 |
| `inputs` | array | ❌ | 用戶輸入定義（如密碼、令牌） |

### 完整配置範例

#### 1. GitHub MCP Server (Docker)

```json
{
  "servers": {
    "io.github.github/github-mcp-server": {
      "type": "stdio",
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "GITHUB_PERSONAL_ACCESS_TOKEN=${input:token}",
        "ghcr.io/github/github-mcp-server:0.21.0"
      ],
      "gallery": "https://api.mcp.github.com",
      "version": "0.21.0"
    }
  },
  "inputs": [
    {
      "id": "token",
      "type": "promptString",
      "description": "GitHub Personal Access Token",
      "password": true
    }
  ]
}
```

#### 2. 本地 Node.js MCP Server

```json
{
  "servers": {
    "synergymesh/code-analyzer": {
      "type": "stdio",
      "command": "node",
      "args": ["./mcp-servers/code-analyzer.js"],
      "env": {
        "NODE_ENV": "production",
        "LOG_LEVEL": "info"
      },
      "version": "1.0.0"
    }
  }
}
```

#### 3. 多服務器配置

```json
{
  "servers": {
    "synergymesh/code-analyzer": {
      "type": "stdio",
      "command": "node",
      "args": ["./mcp-servers/code-analyzer.js"],
      "version": "1.0.0"
    },
    "synergymesh/security-scanner": {
      "type": "stdio",
      "command": "node",
      "args": ["./mcp-servers/security-scanner.js"],
      "version": "1.0.0"
    },
    "synergymesh/test-generator": {
      "type": "stdio",
      "command": "node",
      "args": ["./mcp-servers/test-generator.js"],
      "version": "1.0.0"
    }
  }
}
```

#### 4. Python MCP Server

```json
{
  "servers": {
    "custom/python-analyzer": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "my_mcp_server"],
      "env": {
        "PYTHONPATH": "./src"
      }
    }
  }
}
```

#### 5. 帶輸入提示的配置

```json
{
  "servers": {
    "api-server": {
      "type": "stdio",
      "command": "node",
      "args": ["./server.js"],
      "env": {
        "API_KEY": "${input:apiKey}",
        "API_SECRET": "${input:apiSecret}"
      }
    }
  },
  "inputs": [
    {
      "id": "apiKey",
      "type": "promptString",
      "description": "API Key",
      "password": false
    },
    {
      "id": "apiSecret",
      "type": "promptString",
      "description": "API Secret",
      "password": true
    }
  ]
}
```

### 傳輸類型

| 類型 | 說明 | 使用場景 |
|------|------|----------|
| `stdio` | 標準輸入/輸出 | 本地進程通信（最常用） |
| `sse` | Server-Sent Events | HTTP 長連接 |
| `websocket` | WebSocket | 雙向實時通信 |

### 環境變數引用

在配置中引用環境變數：

```json
{
  "env": {
    "TOKEN": "${input:token}",      // 從 inputs 引用
    "PATH": "${env:PATH}",           // 從系統環境引用
    "HOME": "${env:HOME}"
  }
}
```

### 最佳實踐

1. **使用語義化的服務器 ID**
   ```json
   // ✅ Good
   "synergymesh/code-analyzer": { ... }
   
   // ❌ Avoid
   "server1": { ... }
   ```

2. **敏感資訊使用 inputs**
   ```json
   // ✅ Good - 使用 inputs
   "env": { "TOKEN": "${input:token}" }
   
   // ❌ Bad - 硬編碼
   "env": { "TOKEN": "sk-xxxxx" }
   ```

3. **指定版本號**
   ```json
   "version": "1.0.0"
   ```

4. **適當設置環境變數**
   ```json
   "env": {
     "NODE_ENV": "production",
     "LOG_LEVEL": "warn"
   }
   ```

---

## VS Code 整合

### 配置文件位置

在專案根目錄創建 `.vscode/mcp.json`：

```json
{
  "servers": {
    "io.github.github/github-mcp-server": {
      "type": "stdio",
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN=${input:token}",
        "ghcr.io/github/github-mcp-server:0.21.0"
      ],
      "version": "0.21.0"
    }
  },
  "inputs": [
    {
      "id": "token",
      "type": "promptString",
      "description": "GitHub Personal Access Token",
      "password": true
    }
  ]
}
```

### 代理配置

MCP 服務器可在代理配置中引用。參考 `mcp-servers/README.md` 中的整合說明：

```yaml
# 範例配置（參考用）
mcp-servers:
  - name: code-analyzer
    command: node
    args: ["./mcp-servers/code-analyzer.js"]
    capabilities:
      - analyze-code
      - detect-issues
      - suggest-improvements
```

實際代理配置請參考 `.github/agents/` 目錄中的 `.agent.md` 文件。

---

## 安裝與使用

### 安裝

```bash
cd mcp-servers
npm install
```

### 運行服務器

```bash
# 運行特定服務器
node code-analyzer.js
node test-generator.js
node security-scanner.js
```

### 環境變數

```bash
# SLSA 驗證器
export SLSA_LEVELS="1,2,3,4"

# 通用設定
export NODE_ENV="production"
export LOG_LEVEL="info"
```

---

## MCP 協議基礎

### 工具調用流程

```
1. Agent 發送工具調用請求
2. MCP Server 接收並驗證請求
3. MCP Server 執行工具邏輯
4. MCP Server 返回結構化結果
5. Agent 處理結果並繼續任務
```

### 請求格式

```javascript
{
  "name": "tool-name",
  "arguments": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

### 響應格式

```javascript
{
  "result": {
    "status": "success",
    "data": { ... }
  },
  "errors": [],
  "warnings": []
}
```

---

## 驗證工具

系統提供企業級驗證工具：

```bash
# ESLint 代碼品質檢查
npm run lint

# 部署配置驗證
npm run validate:deployment

# 邏輯和真實性驗證
npm run validate:logic

# 綜合驗證（所有檢查）
npm run validate:comprehensive

# 完整嚴格驗證套件
npm run check:strict
```

---

## 擴展 MCP

### 創建自定義 MCP 服務器

```javascript
const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');

const server = new Server({
  name: 'custom-server',
  version: '1.0.0'
}, {
  capabilities: {
    tools: {}
  }
});

// 註冊工具
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'custom-tool',
      description: 'A custom tool',
      inputSchema: {
        type: 'object',
        properties: {
          input: { type: 'string' }
        }
      }
    }
  ]
}));

// 處理調用
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  // 處理邏輯
  return { content: [{ type: 'text', text: 'Result' }] };
});

// 啟動服務器
const transport = new StdioServerTransport();
await server.connect(transport);
```

---

## 安全考量

- 所有服務器使用 Zod 進行輸入驗證
- 無明確許可不進行外部網路調用
- 密鑰在分析輸出中被遮蔽
- 遵循最小權限原則

---

## 相關資源

- [MCP 官方文檔](https://modelcontextprotocol.io/)
- [GitHub MCP Server](https://github.com/github/github-mcp-server)
- [MCP 服務器 README](../../mcp-servers/README.md)
- [Admin Copilot CLI](./CLI.md)
- [Prompt 系統](./PROMPT_SYSTEM.md)
