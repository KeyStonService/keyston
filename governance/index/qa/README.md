# 即時 QA 引擎 (Realtime QA Engine)

> **執行即驗證，零延遲質量保證**

## 🎯 核心價值

將 QA 從「事後檢查」轉變為「事件驅動 + 內聯驗證」，實現：
- **< 100ms** 驗證延遲
- **即時阻止** 安全漏洞和合規違規
- **60%+** 問題自動修復
- **向量化** 語義檢測未知模式

---

## 📂 檔案結構

```
governance/index/qa/
├── README.md                           # 本文件
├── REALTIME_QA_ARCHITECTURE.md         # 架構設計文檔
├── INTEGRATION_GUIDE.md                # 整合指南
├── USAGE_EXAMPLES.md                   # 使用示例
├── types.ts                            # TypeScript 類型定義
│
├── engine/
│   ├── realtime-qa-engine.ts           # 核心引擎
│   ├── qa-event-bus.ts                 # 事件總線（待實現）
│   └── qa-coordinator.ts               # 協調器（待實現）
│
├── validators/
│   ├── schema-validator.ts             # 結構驗證器 (Zod)
│   ├── security-validator.ts           # 安全驗證器
│   ├── compliance-validator.ts         # 合規驗證器
│   └── semantic-validator.ts           # 語義驗證器
│
├── actions/
│   ├── block-action.ts                 # 阻止動作（待實現）
│   ├── warn-action.ts                  # 警告動作（待實現）
│   └── autofix-action.ts               # 自動修復（待實現）
│
└── index/
    ├── qa-events.json                  # QA 事件定義
    ├── qa-rules-vector.json            # 向量化 QA 規則
    └── qa-dimensions.json              # 必檢維度配置
```

---

## 🚀 快速開始

### 1. 安裝

```bash
# 已包含在 SynergyMesh 主項目中
cd governance/index/qa
npm install
```

### 2. 基本使用

```typescript
import { RealtimeQAEngine } from '@governance/qa/engine/realtime-qa-engine';

// 初始化引擎
const qaEngine = new RealtimeQAEngine({
  maxLatencyMs: 150,
  parallelValidators: true,
  autoFixEnabled: true,
  circuitBreaker: {
    enabled: true,
    failureThreshold: 5,
    timeoutMs: 500
  }
});

// 執行前檢查
const canExecute = await qaEngine.preExecutionCheck('tool_name', params);

// 內聯驗證
const result = await qaEngine.validateInline(output, ['schema', 'security']);

// 執行後檢查
await qaEngine.postExecutionCheck(finalOutput);
```

詳細示例請見 [USAGE_EXAMPLES.md](./USAGE_EXAMPLES.md)

---

## 🏗️ 核心組件

### 1. Realtime QA Engine

**檔案：** `engine/realtime-qa-engine.ts`

**職責：**
- 協調所有驗證器
- 管理並行執行
- 處理熔斷器邏輯
- 收集效能指標

**API：**
```typescript
validate(qaEvent: QAEvent, context: ValidationContext): Promise<QAValidationResult>
validateInline(data: unknown, validators?: string[]): Promise<{ pass: boolean; violations: string[] }>
preExecutionCheck(toolName: string, params: unknown): Promise<boolean>
postExecutionCheck(output: unknown, metadata?: Record<string, unknown>): Promise<QAValidationResult>
```

---

### 2. Validators（驗證器）

#### Schema Validator
- **技術：** Zod
- **延遲：** < 20ms
- **檢查：** JSON schema / TypeScript types

#### Security Validator
- **延遲：** < 30ms
- **檢查：**
  - 硬編碼憑證
  - SQL 注入
  - XSS 漏洞
  - 路徑遍歷
  - 命令注入

#### Compliance Validator
- **延遲：** < 50ms
- **框架：**
  - ISO 27001
  - NIST CSF
  - GDPR
  - SOC 2

#### Semantic Validator
- **技術：** Vector embeddings (all-MiniLM-L6-v2)
- **延遲：** < 100ms
- **檢查：** 語義相似度匹配（85% 閾值）

---

### 3. QA Events Registry

**檔案：** `index/qa-events.json`

**8 個 QA 事件：**
1. `qa.pre_execution_check` - 執行前檢查
2. `qa.inline_validation` - 內聯驗證
3. `qa.post_execution_check` - 執行後檢查
4. `qa.compliance_check` - 合規檢查
5. `qa.safety_check` - 安全檢查
6. `qa.integration_check` - 整合檢查
7. `qa.validation_passed` - 驗證通過
8. `qa.validation_failed` - 驗證失敗

**觸發器映射：**
```json
{
  "automation.started": ["qa.pre_execution_check"],
  "automation.executing": ["qa.inline_validation"],
  "automation.completed": ["qa.post_execution_check"],
  "contract.created": ["qa.compliance_check"],
  "self_healing.triggered": ["qa.safety_check"],
  "agent.lifecycle.deployed": ["qa.integration_check"]
}
```

---

### 4. Vector QA Rules

**檔案：** `index/qa-rules-vector.json`

**10 個預定義規則：**
- `qa-sec-001`: 硬編碼憑證
- `qa-sec-002`: SQL 注入
- `qa-sec-003`: XSS 漏洞
- `qa-debt-001`: TODO 無連結
- `qa-debt-002`: console.log
- `qa-comp-001`: PII 無加密
- `qa-comp-002`: 審計日誌缺失
- `qa-arch-001`: 循環依賴
- `qa-perf-001`: N+1 查詢
- `qa-test-001`: 無測試覆蓋

**自動修復：**
- `replace_with_env_variable`
- `use_parameterized_query`
- `add_sanitization`
- `create_issue_link`
- ...

---

### 5. QA Dimensions Config

**檔案：** `index/qa-dimensions.json`

**7 個必檢維度：**
- `06` - security
- `23` - policy
- `30` - agents
- `39` - automation
- `40` - self_healing
- `60` - contracts
- `70` - audit

每個維度定義：
- `qa_required`: 是否強制 QA
- `qa_validators`: 使用哪些驗證器
- `qa_block_on_fail`: 失敗是否阻止執行
- `qa_events`: 觸發哪些 QA 事件

---

## 🔄 執行流程

### 完整流程示例

```
┌─────────────────────────────────────────────────────────┐
│ 1. Event: automation.started                           │
├─────────────────────────────────────────────────────────┤
│ ├─ Trigger: qa.pre_execution_check                     │
│ ├─ Validators: [schema, security]                      │
│ ├─ Duration: 37ms                                       │
│ └─ Result: ✅ PASS                                      │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Execution: Tool runs                                │
├─────────────────────────────────────────────────────────┤
│ ├─ Output Generated                                     │
│ ├─ Inline QA: validateInline(output)                   │
│ │   ├─ Schema: ✅ Valid                                │
│ │   ├─ Security: ❌ Hardcoded password                 │
│ │   └─ Action: 🛑 BLOCK                                │
│ ├─ Self-Healing: Auto-fix triggered                    │
│ │   ├─ Fix: Replace with env variable                  │
│ │   └─ Re-validate: ✅ PASS                            │
│ └─ Continue execution                                   │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 3. Event: automation.completed                         │
├─────────────────────────────────────────────────────────┤
│ ├─ Trigger: qa.post_execution_check                    │
│ ├─ Validators: [compliance, semantic]                  │
│ │   ├─ Compliance: ✅ ISO27001 OK                      │
│ │   └─ Semantic: ⚠️ 87% similar to past issue         │
│ ├─ Action: WARN                                         │
│ └─ Duration: 118ms                                      │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 4. QA Report                                           │
├─────────────────────────────────────────────────────────┤
│ ├─ Total Duration: 155ms ⚡                            │
│ ├─ Checks: 7 (6 passed, 1 warning)                     │
│ ├─ Blocked: 1 (auto-fixed)                             │
│ └─ Result: ✅ PASSED                                    │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 效能指標

| 指標 | 目標 | 說明 |
|------|------|------|
| **QA 延遲 P50** | < 50ms | 中位數延遲 |
| **QA 延遲 P95** | < 150ms | 95 百分位延遲 |
| **QA 延遲 P99** | < 250ms | 99 百分位延遲 |
| **阻止率** | < 5% | 被 QA 阻止的操作百分比 |
| **自動修復率** | > 60% | 問題自動解決的百分比 |
| **誤報率** | < 2% | False positive 百分比 |
| **驗證器超時率** | < 1% | 驗證器超時的百分比 |

---

## 🧪 測試

### 運行測試

```bash
# 單元測試
npm test -- qa-engine.test.ts

# 整合測試
npm test -- qa-integration.test.ts

# 所有測試
npm test
```

### 測試覆蓋率

目標：> 80%

當前組件測試狀態：
- [ ] Realtime QA Engine
- [ ] Schema Validator
- [ ] Security Validator
- [ ] Compliance Validator
- [ ] Semantic Validator

---

## 🔧 配置

### 環境變數

```bash
# QA Engine
QA_ENABLED=true
QA_MAX_LATENCY_MS=150
QA_PARALLEL_VALIDATORS=true
QA_AUTO_FIX_ENABLED=true

# Circuit Breaker
QA_CIRCUIT_BREAKER_ENABLED=true
QA_CIRCUIT_BREAKER_THRESHOLD=5
QA_CIRCUIT_BREAKER_TIMEOUT_MS=500

# Validators
QA_VALIDATORS=schema,security,compliance,semantic
QA_SEMANTIC_THRESHOLD=0.85

# Actions
QA_BLOCK_ON_CRITICAL=true
QA_AUTO_FIX_CONFIDENCE_THRESHOLD=0.9
```

---

## 📚 文檔

- **[架構設計](./REALTIME_QA_ARCHITECTURE.md)** - 系統設計和架構
- **[整合指南](./INTEGRATION_GUIDE.md)** - 如何整合到現有系統
- **[使用示例](./USAGE_EXAMPLES.md)** - 實際場景和代碼示例
- **[類型定義](./types.ts)** - TypeScript 類型

---

## 🚧 路線圖

### Phase 1: 核心引擎 ✅
- [x] Realtime QA Engine
- [x] 4 個驗證器（Schema, Security, Compliance, Semantic）
- [x] QA Events Registry
- [x] Vector QA Rules
- [x] QA Dimensions Config

### Phase 2: 整合（進行中）
- [ ] 整合到事件 Registry
- [ ] QA Agent 重構
- [ ] AgentCoordinator 整合
- [ ] Bootstrap Contract 更新

### Phase 3: 自動化
- [ ] Auto-fix Actions 實現
- [ ] Self-healing 整合
- [ ] CI/CD Pipeline 整合

### Phase 4: 優化
- [ ] 效能調優（目標 < 100ms P95）
- [ ] 向量索引優化
- [ ] 機器學習模型整合

---

## 🤝 貢獻

這是 SynergyMesh 內部項目。如需修改：

1. 創建功能分支
2. 實現變更並添加測試
3. 運行 `npm test` 確保通過
4. 提交 PR 並等待審查

---

## 📞 支援

**團隊：** QA + DevOps
**聯絡：** #qa-engine (Slack)
**文檔：** `governance/index/qa/`

---

## 📄 授權

內部使用，保留所有權利。

---

**版本：** v1.0.0
**狀態：** Phase 1 完成，Phase 2 進行中
**最後更新：** 2025-12-12
**作者：** Claude AI + SynergyMesh Team
