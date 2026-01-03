# mcp-servers

## 目錄職責

此目錄 `mcp-servers/` 為 MachineNativeOps 的 **MCP 伺服器層**，負責提供 LLM 可調用的工具端點（Model Context Protocol）。包含代碼分析、測試生成、文檔生成、SLSA 驗證、安全掃描和性能優化等企業級 MCP 伺服器；目錄名稱採用 kebab-case（`mcp-servers`）以符合 Node.js / JavaScript 工作空間慣例，而本文檔中統一以「MCP 伺服器層」與「MCP 伺服器」指稱此層與其服務。

## 子目錄說明

| 子目錄 | 職責 |
|--------|------|
| `deploy/` | MCP 伺服器部署配置 |

## MCP 伺服器說明

### code-analyzer.js

- **職責**：程式碼分析 MCP 伺服器
- **功能**：
  - `analyze-code` - 代碼品質與複雜度分析
  - `detect-issues` - 問題檢測與嚴重性過濾
  - `suggest-improvements` - AI 驅動的改進建議
- **特性**：循環複雜度、認知複雜度、安全漏洞、效能問題檢測

### test-generator.js

- **職責**：測試生成 MCP 伺服器
- **功能**：
  - `generate-unit-tests` - 單元測試生成
  - `generate-integration-tests` - API 整合測試生成
  - `generate-e2e-tests` - 端對端測試場景生成
- **特性**：支援 Jest, Mocha, Vitest, Playwright, Cypress

### doc-generator.js

- **職責**：文檔生成 MCP 伺服器
- **功能**：
  - `generate-jsdoc` - JSDoc 文檔生成
  - `generate-api-docs` - API 文檔生成（Markdown, OpenAPI）
  - `generate-guides` - 綜合指南生成
- **特性**：多種文檔風格、自動 API 參考、多種輸出格式

### slsa-validator.js

- **職責**：SLSA 驗證 MCP 伺服器
- **功能**：
  - `validate-provenance` - 驗證 SLSA 溯源數據
  - `check-slsa-compliance` - 檢查 SLSA 等級合規性
  - `generate-compliance-report` - 生成合規報告
- **特性**：SLSA Level 1-4 驗證、差距分析、修復建議

### security-scanner.js

- **職責**：安全掃描 MCP 伺服器
- **功能**：
  - `scan-vulnerabilities` - 安全漏洞掃描
  - `check-dependencies` - 依賴 CVE 檢查
  - `analyze-secrets` - 暴露的密鑰檢測
- **特性**：SQL 注入、XSS、命令注入、硬編碼密鑰檢測

### performance-analyzer.js

- **職責**：效能分析 MCP 伺服器
- **功能**：
  - `analyze-performance` - 代碼效能指標分析
  - `identify-bottlenecks` - 效能瓶頸識別
  - `suggest-optimizations` - 效能優化建議
- **特性**：複雜度分析、記憶體使用、非同步效能分析

## 驗證器說明

### comprehensive-validator.js

- **職責**：綜合驗證器
- **功能**：組合所有驗證器，提供整體品質評分與等級

### deployment-validator.js

- **職責**：部署配置驗證器
- **功能**：必需檔案檢查、package.json 結構驗證、安全配置驗證

### logic-validator.js

- **職責**：邏輯驗證器
- **功能**：真實性檢查、混淆檢測、完整性雜湊、邏輯驗證

## 配置檔案說明

| 檔案 | 職責 |
|------|------|
| `package.json` | Node.js 套件配置與腳本定義 |
| `.eslintrc.json` | ESLint 代碼品質規則 |
| `tsconfig.json` | TypeScript 編譯配置 |
| `Dockerfile` | Docker 容器化配置 |

## 依賴規則

**可以依賴**：

- `src/core/` - 調用平台級 AI 能力
- `src/shared/` - 共用工具和配置

**不可依賴**：

- `agent/` - MCP 端點不應依賴業務代理
- `automation/intelligent/` - MCP 端點不應依賴 pipeline

## 執行模式

```
1. 伺服器初始化 - 創建 MCP 伺服器與能力
2. 工具註冊 - 註冊可用工具與 schema
3. 請求處理 - 處理工具調用與驗證
4. 回應生成 - 返回結構化結果
5. 錯誤處理 - 綜合錯誤處理與驗證
```

## 設計原則

1. **標準化協議**：所有工具遵循 MCP 協議標準
2. **輸入驗證**：使用 Zod 進行嚴格的輸入驗證
3. **最小權限**：遵循最小權限原則
4. **快速回應**：大多數操作 <100ms 回應時間

## 與其他目錄的關係

- **src/core/**：調用平台級 AI 能力
- **src/ai/**：AI 模組透過 MCP 調用工具
- **src/services/**：服務層可封裝 MCP 端點為 HTTP API
- **.github/agents/**：Agent 配置引用 MCP 伺服器
