# 即時 QA 引擎整合指南

## 🎯 整合目標

將即時 QA 引擎整合到 SynergyMesh 現有的事件驅動架構中，實現「執行即驗證」。

---

## 📋 整合清單

### Phase 1: 事件註冊 ✅

#### 1.1 更新主事件 Registry

**檔案：** `governance/index/events/registry.json`

**操作：** 添加 QA 事件類別

```json
{
  "event_categories": [
    {
      "id": "qa",
      "name": "Quality Assurance",
      "events_file": "governance/index/qa/index/qa-events.json",
      "priority": "critical",
      "enabled": true
    }
  ]
}
```

#### 1.2 註冊 QA 觸發器

**修改現有事件：**

```json
{
  "id": "automation.started",
  "trigger": "automation_trigger",
  "agents": ["task-scheduler", "monitor-agent"],
  "qa_hooks": {
    "pre": ["qa.pre_execution_check"],
    "inline": ["qa.inline_validation"],
    "post": ["qa.post_execution_check"]
  }
}
```

**適用於的事件：**
- `automation.started` / `automation.completed`
- `contract.created` / `contract.validated`
- `self_healing.triggered` / `self_healing.completed`
- `agent.lifecycle.deployed`

---

### Phase 2: 維度增強 ✅

#### 2.1 為關鍵維度添加 QA 標記

**檔案：** `governance/index/dimensions.json`

**修改示例：**

```json
{
  "id": "06",
  "name": "security",
  "execution": "required",
  "priority": 1,
  "qa_required": true,
  "qa_validators": ["schema", "security", "compliance"],
  "qa_block_on_fail": true
}
```

**需要修改的維度：**
- `06` - security
- `23` - policy
- `30` - agents
- `39` - automation
- `40` - self_healing
- `60` - contracts
- `70` - audit

#### 2.2 自動應用腳本

```bash
# 運行腳本自動添加 qa_required 標記
node governance/scripts/enhance-dimensions-with-qa.js
```

---

### Phase 3: Agent 協作整合 ✅

#### 3.1 QA Agent 重構

**檔案：** `island-ai/src/agents/qa/index.ts`

**從：** 事後驗證模式
**到：** 事件驅動 + 內聯驗證

**修改步驟：**

1. 導入即時 QA 引擎：
```typescript
import { RealtimeQAEngine } from '@governance/qa/engine/realtime-qa-engine';
```

2. 初始化引擎：
```typescript
private qaEngine: RealtimeQAEngine;

constructor() {
  super('qa-agent');
  this.qaEngine = new RealtimeQAEngine({
    maxLatencyMs: 150,
    parallelValidators: true,
    autoFixEnabled: true,
    circuitBreaker: { enabled: true, failureThreshold: 5, timeoutMs: 500 }
  });
}
```

3. 替換現有 `run()` 方法：
```typescript
async run(context: AgentContext): Promise<AgentInsight[]> {
  // Pre-execution check
  await this.qaEngine.preExecutionCheck('qa_agent', context.payload);

  // Run existing QA logic with inline validation
  const result = await this.qaEngine.postExecutionCheck(context.payload);

  return this.convertToInsights(result);
}
```

#### 3.2 AgentCoordinator 整合

**檔案：** `island-ai/src/collaboration/agent-coordinator.ts`

**添加 QA Hooks：**

```typescript
async orchestrate(collaboration: AgentCollaboration, context: AgentContext) {
  // Before execution
  if (context.qa_required) {
    await this.runQACheck('pre', context);
  }

  // During execution (existing code)
  const results = await this.executeStrategy(collaboration, context);

  // After execution
  if (context.qa_required) {
    await this.runQACheck('post', { ...context, results });
  }

  return results;
}

private async runQACheck(phase: 'pre' | 'post', context: AgentContext) {
  const qaEngine = new RealtimeQAEngine(defaultConfig);

  if (phase === 'pre') {
    const pass = await qaEngine.preExecutionCheck(context.agentId, context.payload);
    if (!pass) throw new QABlockError('Pre-execution QA failed');
  } else {
    await qaEngine.postExecutionCheck(context.payload);
  }
}
```

---

### Phase 4: 自動化工具整合

#### 4.1 為自動化工具添加內聯 QA

**示例：自動修復工具**

**檔案：** `island-ai/src/tools/auto-fixer.ts`

```typescript
import { RealtimeQAEngine } from '@governance/qa/engine/realtime-qa-engine';

export class AutoFixer {
  private qaEngine: RealtimeQAEngine;

  async applyFix(code: string, fix: CodeFix): Promise<string> {
    // Apply fix
    const modifiedCode = this.applyPatch(code, fix);

    // Inline QA validation
    const qaResult = await this.qaEngine.validateInline(modifiedCode, [
      'schema',
      'security',
      'semantic'
    ]);

    if (!qaResult.pass) {
      console.error('QA failed:', qaResult.violations);
      throw new Error(`Fix violated QA: ${qaResult.violations.join(', ')}`);
    }

    return modifiedCode;
  }
}
```

**適用於所有工具：**
- Auto-fixer
- Code generator
- Config updater
- Deployment automation

---

### Phase 5: Bootstrap Contract 整合

#### 5.1 更新啟動協議

**檔案：** `governance/index/events/bootstrap-contract.json`

**添加 QA 驗證規則：**

```json
{
  "must_read": [
    "events/registry.json",
    "events/current-session.json",
    "events/vector-index.json",
    "qa/index/qa-events.json",
    "qa/index/qa-rules-vector.json"
  ],
  "validation_rules": {
    "qa-engine-ready": "context.qaEngine !== undefined",
    "qa-validators-loaded": "context.qaValidators.length >= 4",
    "qa-events-registered": "context.events.qa !== undefined"
  }
}
```

---

## 🔄 執行流程示例

### 完整流程：自動化任務執行

```
1. Event: automation.started
   ├─ Bootstrap Contract: Load QA config
   └─ Trigger: qa.pre_execution_check
       ├─ Schema Validator (15ms) ✅
       ├─ Security Validator (22ms) ✅
       └─ Result: PASS

2. Execution: Run automation task
   ├─ Tool: Auto-fixer applies patch
   ├─ Inline QA: validateInline(patch)
   │   ├─ Schema: ✅ Valid structure
   │   ├─ Security: ❌ Found "password='test'"
   │   └─ Action: 🛑 BLOCK
   ├─ Self-Healing: Auto-fix triggered
   │   ├─ Fix: Replace with process.env.PASSWORD
   │   ├─ Re-validate: ✅ PASS
   │   └─ Continue

3. Event: automation.completed
   └─ Trigger: qa.post_execution_check
       ├─ Compliance Validator (38ms)
       │   └─ [ISO27001] ⚠️ Missing audit log
       ├─ Semantic Validator (87ms)
       │   └─ ✅ No similar violations
       └─ Action: WARN (log warning, continue)

4. QA Report
   ├─ Total Duration: 162ms ⚡
   ├─ Checks: 7 (6 passed, 1 warning)
   ├─ Blocked: 1 (auto-fixed)
   └─ Result: ✅ PASSED
```

---

## 🧪 測試計劃

### 單元測試

```typescript
// tests/qa-engine.test.ts

import { RealtimeQAEngine } from '@governance/qa/engine/realtime-qa-engine';

describe('RealtimeQAEngine', () => {
  let engine: RealtimeQAEngine;

  beforeEach(() => {
    engine = new RealtimeQAEngine({
      maxLatencyMs: 150,
      parallelValidators: true,
      autoFixEnabled: false,
      circuitBreaker: { enabled: false, failureThreshold: 5, timeoutMs: 500 }
    });
  });

  test('should pass valid code', async () => {
    const result = await engine.validateInline({ code: 'const x = 1;' });
    expect(result.pass).toBe(true);
  });

  test('should block hardcoded password', async () => {
    const code = `const password = "admin123";`;
    const result = await engine.validateInline(code);

    expect(result.pass).toBe(false);
    expect(result.violations).toContain('Hardcoded Password');
  });

  test('should complete within latency SLA', async () => {
    const start = Date.now();
    await engine.validateInline({ code: 'const x = 1;' });
    const duration = Date.now() - start;

    expect(duration).toBeLessThan(150);
  });
});
```

### 整合測試

```typescript
// tests/qa-integration.test.ts

import { AgentCoordinator } from '@island-ai/collaboration/agent-coordinator';
import { QAAgent } from '@island-ai/agents/qa';

describe('QA Integration', () => {
  test('should block execution on critical security violation', async () => {
    const coordinator = new AgentCoordinator();
    const context = {
      agentId: 'test-agent',
      qa_required: true,
      payload: { code: 'eval(userInput)' }
    };

    await expect(
      coordinator.orchestrate({ strategy: 'sequential' }, context)
    ).rejects.toThrow('QA validation failed');
  });
});
```

---

## 📊 監控與指標

### 關鍵指標

**檔案：** `governance/monitoring/qa-metrics.json`

```json
{
  "metrics": {
    "qa_latency_p50_ms": { "target": 50, "alert": 100 },
    "qa_latency_p95_ms": { "target": 150, "alert": 250 },
    "qa_block_rate_percent": { "target": "< 5%", "alert": "> 10%" },
    "qa_auto_fix_success_rate": { "target": "> 60%", "alert": "< 40%" },
    "validator_timeout_rate": { "target": "< 1%", "alert": "> 5%" }
  },
  "dashboards": {
    "grafana": "governance/monitoring/dashboards/qa-dashboard.json",
    "datadog": "governance/monitoring/datadog/qa-metrics.yaml"
  }
}
```

### 日誌格式

```json
{
  "timestamp": "2025-12-12T10:30:00Z",
  "event": "qa.validation_completed",
  "eventId": "automation.started",
  "result": "passed",
  "duration_ms": 87,
  "validators": ["schema", "security"],
  "violations": [],
  "metadata": {
    "dimensionId": "39",
    "agentId": "task-scheduler"
  }
}
```

---

## 🚀 部署步驟

### 1. 準備階段

```bash
# 1. 安裝依賴
npm install zod

# 2. 編譯 TypeScript
cd governance/index/qa
npx tsc

# 3. 運行測試
npm test -- qa-engine.test.ts
```

### 2. 配置階段

```bash
# 1. 更新事件 Registry
node scripts/merge-qa-events.js

# 2. 增強維度索引
node scripts/enhance-dimensions-with-qa.js

# 3. 驗證配置
node scripts/validate-qa-config.js
```

### 3. 啟用階段

```bash
# 1. 重啟 Island AI
pm2 restart island-ai

# 2. 驗證 QA 引擎
curl http://localhost:3000/health/qa-engine

# 3. 監控日誌
tail -f logs/qa-engine.log
```

---

## 🔧 故障排除

### 常見問題

#### Q1: QA 驗證總是超時

**原因：** 語義驗證器加載向量索引失敗

**解決：**
```bash
# 檢查向量索引檔案
ls -lh governance/index/qa/index/qa-rules-vector.json

# 禁用語義驗證作為臨時措施
# 在 qa-events.json 中移除 "semantic" validator
```

#### Q2: 過多的誤報（false positives）

**原因：** 安全驗證器過於嚴格

**解決：**
```typescript
// 調整驗證器配置
{
  "security": {
    "checks": ["injection", "secrets"], // 減少檢查項
    "fail_mode": "warn" // 改為警告模式
  }
}
```

#### Q3: 性能下降

**原因：** 並行驗證被禁用

**解決：**
```typescript
const qaEngine = new RealtimeQAEngine({
  parallelValidators: true, // 確保開啟並行
  maxLatencyMs: 200 // 增加超時時間
});
```

---

## ✅ 驗證清單

部署後檢查：

- [ ] QA 事件已註冊到主 Registry
- [ ] 關鍵維度已標記 `qa_required: true`
- [ ] QA Agent 使用即時引擎
- [ ] AgentCoordinator 整合 QA hooks
- [ ] 自動化工具添加內聯驗證
- [ ] Bootstrap Contract 載入 QA 配置
- [ ] 監控指標正常收集
- [ ] 測試覆蓋率 > 80%
- [ ] 文檔已更新

---

**整合版本：** v1.0
**狀態：** 待執行
**預計完成時間：** 1-2 小時
**負責人：** DevOps + QA Team
