# governance

## 目錄職責

此目錄為 MachineNativeOps 的**治理框架**，包含治理政策、規則、安全配置和合規資源。採用分層閉環治理架構，整合 GitOps、Policy as Code、Intent-based Orchestration、AI Agent Governance 與 Feedback Loop。

## 分層治理架構 (Layered Governance Framework)

```
策略層 (Strategy)     → 10-policy: Policy as Code Framework
協調層 (Orchestration) → 20-intent: Intent-based Orchestration
執行層 (Execution)    → 30-agents, 39-automation, 40-self-healing
觀測層 (Observability) → 60-contracts, 70-audit
回饋層 (Feedback)     → 80-feedback: Closed-Loop Optimization
```

## 子目錄分類

### 核心維度 (00-09)

| 子目錄 | 職責 |
|--------|------|
| `00-vision-strategy/` | 願景與策略 |
| `01-architecture/` | 架構定義 |
| `02-decision/` | 決策記錄 |
| `03-change/` | 變更管理 |
| `04-risk/` | 風險管理 |
| `05-compliance/` | 合規管理 |
| `06-security/` | 安全管理 |
| `07-audit/` | 審計配置 |
| `08-process/` | 流程定義 |
| `09-performance/` | 效能指標 |

### 策略與意圖 (10-22)

| 子目錄 | 職責 |
|--------|------|
| `10-policy/` | Policy as Code Framework |
| `11-tools-systems/` | 工具與系統整合 |
| `12-culture-capability/` | 文化與能力建設 |
| `13-metrics-reporting/` | 指標與報告 |
| `14-improvement/` | 持續改進 |
| `15-economic/` | 經濟模型 |
| `16-psychological/` | 心理學維度 |
| `17-sociological/` | 社會學維度 |
| `18-complex-system/` | 複雜系統 |
| `19-evolutionary/` | 演化維度 |
| `20-intent/` | Intent-based Orchestration |
| `21-ecological/` | 生態維度 |
| `22-aesthetic/` | 美學維度 |

### 規則與資源 (23-38)

| 子目錄 | 職責 |
|--------|------|
| `23-policies/` | 治理政策（主要） |
| `24-registry/` | 模組註冊表 |
| `25-principles/` | 設計原則 |
| `26-tools/` | 治理工具 |
| `27-templates/` | 模板 |
| `28-tests/` | 測試套件 |
| `29-docs/` | 文檔 |
| `30-agents/` | AI Agent 治理 |
| `31-schemas/` | Schema 定義（主要） |
| `32-rules/` | 治理規則 |
| `33-common/` | 共用工具 |
| `34-config/` | 配置 |
| `35-scripts/` | 自動化腳本（主要） |
| `36-modules/` | 模組規範 |
| `37-behavior-contracts/` | 行為契約 |
| `38-sbom/` | 軟體物料清單 |

### 自動化與自我修復 (39-40)

| 子目錄 | 職責 |
|--------|------|
| `39-automation/` | 自動化引擎 |
| `40-self-healing/` | 自我修復框架 |

### 契約與審計 (60-80)

| 子目錄 | 職責 |
|--------|------|
| `60-contracts/` | 契約註冊表 |
| `70-audit/` | 審計與追蹤 |
| `80-feedback/` | 閉環回饋 |

### 支援目錄

| 子目錄 | 職責 |
|--------|------|
| `dimensions/` | 治理維度定義 |
| `index/` | 索引 |
| `packages/` | 套件 |
| `ci/` | CI 整合 |
| `_legacy/` | 已廢棄資源 |
| `_scratch/` | 實驗性資源 |

## 核心配置檔案

| 檔案 | 職責 |
|------|------|
| `governance.yaml` | 主治理配置 |
| `governance-map.yaml` | 治理映射 |
| `governance-index.json` | 治理索引 |
| `PHASE4_STATE.yaml` | Phase 4 狀態 |
| `PHASE5_STATE.yaml` | Phase 5 狀態 |

## 依賴規則

**可被依賴於**：

- CI/CD workflows - 策略驗證和合規檢查
- `src/core/` - 讀取 AI 憲法和倫理規則
- Security tools - SBOM 和安全策略

**不應依賴**：

- 任何實作代碼 - 治理應獨立於實作
- `runtime/` - 治理定義不應依賴運行時

## 設計原則

1. **Policy as Code**：所有策略以程式碼形式定義
2. **分層解耦**：策略、執行、觀測、回饋分層
3. **閉環治理**：策略—執行—監控—回饋閉環
4. **可審計性**：完整的審計追蹤
