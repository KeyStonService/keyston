# Contract Service

# 合約管理服務

> 合約管理微服務（L1），提供合約生命週期管理功能。
> Contract management microservice (L1), providing contract lifecycle management functionality.

## 📋 Overview 概述

本目錄包含合約管理微服務的實作代碼，包括 L1 合約服務和 AI 聊天服務整合。

**⚠️ 重要區分 Important Distinction:**

| 目錄 Directory | 內容 Content | 說明 Description |
|----------------|--------------|------------------|
| `core/contract_service/` (本目錄) | 微服務程式碼 | 合約管理服務的**實作代碼** |
| `contracts/` (根目錄) | 合約定義資料 | 外部 API 合約**規格定義** (OpenAPI, JSON Schema) |

This directory contains implementation code for the contract management microservice, including L1 contract service and AI chat service integration.

## 📁 Directory Structure 目錄結構

```
contract_service/
└── contracts-L1/
    ├── ai-chat-service/     # AI 聊天服務整合
    └── contracts/           # L1 合約服務實作
        ├── src/
        │   ├── routes.ts        # 路由定義
        │   ├── server.ts        # 主服務器
        │   ├── controllers/     # 控制器
        │   └── middleware/      # 中介軟體
        ├── dist/               # 編譯輸出
        ├── package.json        # 依賴配置
        └── tsconfig.json       # TypeScript 配置
```

## 🎯 What This Directory Does 本目錄負責什麼

### ✅ Responsibilities 職責

1. **Contract Management Service 合約管理服務**
   - 合約的 CRUD 操作
   - 合約驗證和審核
   - 合約生命週期管理

2. **L1 Contract Service L1 合約服務**
   - Layer 1 合約處理
   - 與 AI 系統整合
   - Provenance 追蹤

3. **AI Chat Service Integration AI 聊天服務整合**
   - 智能合約助手
   - 自然語言合約查詢
   - 合約建議生成

### ❌ What This Directory Does NOT Do 本目錄不負責什麼

- **不定義外部 API 合約規格** - 使用根目錄 `contracts/`
- **不實作 AI 引擎** - 使用 `core/` 中的 AI 能力
- **不處理 MCP 協議** - 使用 `mcp-servers/`

## 🔗 Dependencies 依賴關係

### ✅ Allowed Dependencies 允許的依賴

| Dependency 依賴 | Purpose 用途 |
|----------------|--------------|
| `shared/` | 共用工具和配置 |
| `config/` | 服務配置 |
| `core/` 其他模組 | AI 能力、安全機制 |

### ❌ Prohibited Dependencies 禁止的依賴

| Should NOT depend on 不應依賴 | Reason 原因 |
|------------------------------|-------------|
| `contracts/` (根目錄) | 服務代碼不應依賴合約定義資料 |
| `agent/` | 避免循環依賴 |
| `frontend/` | 後端服務不應依賴前端 |

## 🚀 Usage 使用方式

### Starting the Service 啟動服務

```bash
cd core/contract_service/contracts-L1/contracts
npm install
npm run build
npm start
```

### Development 開發

```bash
# 運行開發模式
npm run dev

# 運行測試
npm test

# 運行 lint
npm run lint
```

## 📖 Related Documentation 相關文檔

- [Architecture Layers](../../docs/architecture/layers.md) - 架構分層視圖
- [Repository Map](../../docs/architecture/repo-map.md) - 倉庫語義邊界
- [External API Contracts](../../contracts/) - 外部 API 合約定義
- [L1 Deployment Plan](../../docs/TIER1_CONTRACTS_L1_DEPLOYMENT_PLAN.md) - L1 部署計畫

## ⚠️ Naming Convention Note 命名說明

此目錄原名為 `core/contracts/`，為避免與根目錄 `contracts/`（外部 API 合約定義）混淆，已重命名為 `core/contract_service/`。

This directory was originally named `core/contracts/`. It has been renamed to `core/contract_service/` to avoid confusion with the root-level `contracts/` directory (external API contract definitions).

## 📝 Document History 文檔歷史

| Date 日期 | Version 版本 | Changes 變更 |
|-----------|-------------|--------------|
| 2025-11-30 | 1.0.0 | Renamed from core/contracts/ to core/contract_service/ |

---

**Owner 負責人**: Contract Service Team  
**Last Updated 最後更新**: 2025-11-30
