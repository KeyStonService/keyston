# Layering Rules (分層規則)

## 層級定義

### Layer 1: core/
**職責**: 領域核心邏輯、基礎設施抽象
**允許依賴**: 標準庫、少數明確的第三方庫
**禁止依賴**: platform, services, agents, applications
**範例模組**: 
- `core/domain` - 領域模型
- `core/orchestrator` - 編排引擎
- `core/knowledge-base` - 知識庫核心

### Layer 2: platform/
**職責**: 平台能力、基礎設施實作
**允許依賴**: core, 標準庫, 基礎設施庫
**禁止依賴**: services, agents, applications
**子分層**:
- `platform/foundation` - 架構、安全、身份
- `platform/governance` - API/資料/測試治理
- `platform/application` - 應用平台能力
- `platform/operations` - 運維能力
- `platform/knowledge` - 知識管理

### Layer 3: services/
**職責**: 業務服務實作
**允許依賴**: core, platform, 標準庫
**禁止依賴**: 其他 services (同層), agents, applications
**通訊方式**: HTTP API, gRPC, Message Queue

### Layer 4: agents/
**職責**: AI Agent 實作
**允許依賴**: core, platform, services (透過 API), 標準庫
**禁止依賴**: 其他 agents (同層), applications
**通訊方式**: MCP, HTTP API

### Layer 5: applications/
**職責**: 使用者介面、應用編排
**允許依賴**: 所有下層
**禁止依賴**: 無 (最外層)

## 依賴規則矩陣

|        | core | platform | services | agents | apps |
|--------|------|----------|----------|--------|------|
| core   | ✅   | ❌       | ❌       | ❌     | ❌   |
| platform| ✅  | ✅       | ❌       | ❌     | ❌   |
| services| ✅  | ✅       | 🔄*      | ❌     | ❌   |
| agents | ✅   | ✅       | 🌐**     | 🔄*    | ❌   |
| apps   | ✅   | ✅       | 🌐**     | 🌐**   | ✅   |

- ✅ 允許直接依賴 (import/require)
- ❌ 禁止依賴
- 🔄 同層有限依賴 (僅限明確的共享庫)
- 🌐 僅透過網路 API 依賴