# 即時 QA 引擎使用示例

## 快速開始

### 基本用法

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
const canExecute = await qaEngine.preExecutionCheck('deployAgent', {
  agentId: 'security-01',
  config: { /* ... */ }
});

if (!canExecute) {
  console.error('Pre-execution QA failed');
  return;
}

// 內聯驗證（執行過程中）
const code = generateCode();
const inlineResult = await qaEngine.validateInline(code, ['schema', 'security']);

if (!inlineResult.pass) {
  console.error('Inline QA failed:', inlineResult.violations);
}

// 執行後檢查
const output = await runTool();
const postResult = await qaEngine.postExecutionCheck(output);

console.log(`QA passed: ${postResult.passed}`);
```

---

## 場景 1：自動化工具驗證

### 代碼自動修復工具

```typescript
import { RealtimeQAEngine } from '@governance/qa/engine/realtime-qa-engine';

export class AutoFixer {
  private qaEngine: RealtimeQAEngine;

  constructor() {
    this.qaEngine = new RealtimeQAEngine({
      maxLatencyMs: 100,
      parallelValidators: true,
      autoFixEnabled: true,
      circuitBreaker: { enabled: false, failureThreshold: 0, timeoutMs: 0 }
    });
  }

  async fixCode(filePath: string, issue: CodeIssue): Promise<FixResult> {
    // 1. Pre-execution: 檢查輸入
    const canFix = await this.qaEngine.preExecutionCheck('auto_fixer', {
      filePath,
      issue: issue.type
    });

    if (!canFix) {
      return { success: false, reason: 'Pre-check failed' };
    }

    // 2. 執行修復
    const originalCode = await fs.readFile(filePath, 'utf-8');
    const fixedCode = this.applyFix(originalCode, issue);

    // 3. Inline QA: 驗證修復結果
    const qaResult = await this.qaEngine.validateInline(fixedCode, [
      'schema',
      'security',
      'semantic'
    ]);

    if (!qaResult.pass) {
      console.error('❌ Fix introduced new issues:', qaResult.violations);

      // 嘗試自動修復 QA 違規
      const autoFixed = await this.attemptAutoFix(fixedCode, qaResult.violations);

      if (autoFixed) {
        return { success: true, code: autoFixed, autoFixed: true };
      }

      return { success: false, reason: 'QA validation failed', violations: qaResult.violations };
    }

    // 4. 寫入檔案
    await fs.writeFile(filePath, fixedCode);

    // 5. Post-execution: 最終驗證
    await this.qaEngine.postExecutionCheck({
      filePath,
      originalCode,
      fixedCode,
      issue: issue.type
    });

    return { success: true, code: fixedCode };
  }
}

// 使用
const fixer = new AutoFixer();
const result = await fixer.fixCode('src/auth.ts', {
  type: 'hardcoded_password',
  line: 42
});

if (result.success) {
  console.log('✅ Code fixed and validated');
} else {
  console.error('❌ Fix failed:', result.reason);
}
```

---

## 場景 2：Agent 部署驗證

### QA Agent 整合

```typescript
import { BaseAgent, AgentContext, AgentInsight } from '@island-ai/agents/base-agent';
import { RealtimeQAEngine } from '@governance/qa/engine/realtime-qa-engine';

export class QAAgent extends BaseAgent {
  private qaEngine: RealtimeQAEngine;

  constructor() {
    super('qa-agent');
    this.qaEngine = new RealtimeQAEngine({
      maxLatencyMs: 150,
      parallelValidators: true,
      autoFixEnabled: false, // QA agent doesn't auto-fix, only reports
      circuitBreaker: { enabled: true, failureThreshold: 3, timeoutMs: 500 }
    });
  }

  async run(context: AgentContext): Promise<AgentInsight[]> {
    const insights: AgentInsight[] = [];

    try {
      // 驗證 context payload
      const qaEvent = {
        id: 'qa.agent_validation',
        name: 'QA Agent Validation',
        validators: ['schema', 'security', 'compliance', 'semantic'],
        max_latency_ms: 200,
        block_on_fail: false,
        priority: 'high' as const
      };

      const result = await this.qaEngine.validate(qaEvent, {
        eventId: 'qa.agent_validation',
        dimensionId: context.dimensionId,
        data: context.payload
      });

      // 轉換為 AgentInsight
      if (!result.passed) {
        insights.push({
          title: 'QA Validation Failed',
          description: `Found ${result.failures.length} issue(s)`,
          signal: 'error',
          data: {
            failures: result.failures,
            timestamp: result.timestamp
          }
        });
      } else {
        insights.push({
          title: 'QA Validation Passed',
          description: 'All checks passed successfully',
          signal: 'info',
          data: {
            duration: result.metadata?.duration,
            validators: qaEvent.validators.length
          }
        });
      }

    } catch (error) {
      insights.push({
        title: 'QA Engine Error',
        description: error.message,
        signal: 'error',
        data: { error: error.stack }
      });
    }

    return insights;
  }
}
```

---

## 場景 3：合規框架檢查

### 契約創建驗證

```typescript
import { RealtimeQAEngine } from '@governance/qa/engine/realtime-qa-engine';

export class ContractService {
  private qaEngine: RealtimeQAEngine;

  constructor() {
    this.qaEngine = new RealtimeQAEngine({
      maxLatencyMs: 200,
      parallelValidators: true,
      autoFixEnabled: false,
      circuitBreaker: { enabled: false, failureThreshold: 0, timeoutMs: 0 }
    });
  }

  async createContract(contract: Contract): Promise<ContractResult> {
    // QA Event: 合規檢查
    const qaEvent = {
      id: 'qa.compliance_check',
      name: 'Contract Compliance Check',
      validators: ['schema', 'compliance'],
      max_latency_ms: 150,
      block_on_fail: true, // 合規失敗必須阻止
      priority: 'critical' as const
    };

    // 驗證合約
    const result = await this.qaEngine.validate(qaEvent, {
      eventId: 'contract.created',
      data: contract,
      metadata: {
        frameworks: ['ISO27001', 'GDPR', 'SOC2']
      }
    });

    // 如果 QA 失敗且設置了 block_on_fail，這裡會拋出異常
    if (!result.passed) {
      throw new ComplianceError('Contract violates compliance requirements', {
        violations: result.failures
      });
    }

    // 保存合約
    const saved = await this.db.contracts.save(contract);

    // Post-execution 審計日誌
    await this.qaEngine.postExecutionCheck({
      action: 'contract_created',
      contractId: saved.id,
      timestamp: new Date().toISOString()
    });

    return { success: true, contractId: saved.id };
  }
}

// 使用
const service = new ContractService();

try {
  const result = await service.createContract({
    contractId: 'cnt-001',
    type: 'sla',
    parties: ['client-a', 'provider-b'],
    terms: {
      uptime: 0.999,
      responseTime: 200
    }
  });
  console.log('✅ Contract created:', result.contractId);
} catch (error) {
  if (error instanceof ComplianceError) {
    console.error('❌ Compliance violation:', error.violations);
  }
}
```

---

## 場景 4：自我修復安全檢查

### Self-Healing Validator

```typescript
import { RealtimeQAEngine } from '@governance/qa/engine/realtime-qa-engine';

export class SelfHealingService {
  private qaEngine: RealtimeQAEngine;

  constructor() {
    this.qaEngine = new RealtimeQAEngine({
      maxLatencyMs: 50, // 自我修復需要極快響應
      parallelValidators: true,
      autoFixEnabled: false,
      circuitBreaker: { enabled: true, failureThreshold: 3, timeoutMs: 200 }
    });
  }

  async healSystem(issue: SystemIssue, action: HealingAction): Promise<HealResult> {
    // QA Event: 安全檢查（防止自我修復造成更大損害）
    const qaEvent = {
      id: 'qa.safety_check',
      name: 'Self-Healing Safety Check',
      validators: ['schema', 'security', 'semantic'],
      max_latency_ms: 50,
      block_on_fail: true, // 不安全的修復必須阻止
      priority: 'critical' as const
    };

    // 驗證修復動作
    const result = await this.qaEngine.validate(qaEvent, {
      eventId: 'self_healing.triggered',
      data: {
        issue: issue.type,
        action: action.type,
        target: action.target,
        params: action.params
      }
    });

    if (!result.passed) {
      console.error('🛑 Healing action blocked by QA:', result.failures);

      // 記錄到審計日誌
      await this.auditLog.record({
        event: 'self_healing_blocked',
        reason: result.failures,
        issue: issue.type
      });

      return { success: false, blocked: true, reason: result.failures };
    }

    // 執行修復
    console.log('✅ Safety check passed, executing healing action');
    const healed = await this.executeHealing(action);

    // Post-execution 驗證
    await this.qaEngine.postExecutionCheck({
      healingAction: action.type,
      result: healed ? 'success' : 'failed'
    });

    return { success: healed };
  }

  private async executeHealing(action: HealingAction): Promise<boolean> {
    switch (action.type) {
      case 'restart':
        return await this.restartService(action.target);
      case 'scale':
        return await this.scaleService(action.target, action.params);
      case 'failover':
        return await this.failover(action.target);
      default:
        return false;
    }
  }
}

// 使用
const healer = new SelfHealingService();

const result = await healer.healSystem(
  { type: 'high_memory_usage', severity: 'critical' },
  { type: 'restart', target: 'api-service', params: {} }
);

if (result.success) {
  console.log('✅ System healed');
} else if (result.blocked) {
  console.error('❌ Healing blocked by QA safety check');
}
```

---

## 場景 5：CI/CD Pipeline 整合

### GitHub Actions 整合

```yaml
# .github/workflows/qa-validation.yml

name: Real-time QA Validation

on: [push, pull_request]

jobs:
  qa-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install dependencies
        run: npm install

      - name: Run QA Engine
        run: |
          node scripts/run-qa-validation.js
        env:
          QA_MODE: ci
          QA_BLOCK_ON_FAIL: true
          QA_VALIDATORS: schema,security,compliance
```

**腳本：** `scripts/run-qa-validation.js`

```javascript
const { RealtimeQAEngine } = require('@governance/qa/engine/realtime-qa-engine');
const fs = require('fs');
const path = require('path');

async function runQAValidation() {
  const qaEngine = new RealtimeQAEngine({
    maxLatencyMs: 500, // CI 允許更長時間
    parallelValidators: true,
    autoFixEnabled: false,
    circuitBreaker: { enabled: false, failureThreshold: 0, timeoutMs: 0 }
  });

  // 讀取變更的檔案
  const changedFiles = execSync('git diff --name-only HEAD~1').toString().split('\n');

  let allPassed = true;
  const report = [];

  for (const file of changedFiles) {
    if (!file.endsWith('.ts') && !file.endsWith('.js')) continue;

    const content = fs.readFileSync(file, 'utf-8');

    // 驗證檔案內容
    const result = await qaEngine.validateInline(content, [
      'schema',
      'security',
      'compliance'
    ]);

    report.push({
      file,
      passed: result.pass,
      violations: result.violations
    });

    if (!result.pass) {
      allPassed = false;
      console.error(`❌ ${file}: ${result.violations.join(', ')}`);
    } else {
      console.log(`✅ ${file}: passed`);
    }
  }

  // 寫入報告
  fs.writeFileSync('qa-report.json', JSON.stringify(report, null, 2));

  // CI 模式：如果 QA 失敗，退出碼 1
  if (!allPassed && process.env.QA_BLOCK_ON_FAIL === 'true') {
    process.exit(1);
  }
}

runQAValidation().catch(console.error);
```

---

## 場景 6：向量化語義檢測

### 檢測未知安全模式

```typescript
import { SemanticValidator } from '@governance/qa/validators/semantic-validator';

const validator = new SemanticValidator(0.85); // 85% 相似度閾值

// 檢測與已知違規模式相似的代碼
const code = `
  const userQuery = "SELECT * FROM users WHERE email='" + userEmail + "'";
`;

const result = await validator.validate({
  eventId: 'qa.semantic_check',
  data: code
});

if (!result.passed) {
  console.log('🔍 Semantic similarity detected:');
  result.violations.forEach(v => console.log(`  - ${v}`));

  // 輸出：
  // Semantic match (89.2%): SQL injection vulnerability
}
```

---

## 高級配置

### 自定義驗證器

```typescript
import { BaseValidator, ValidationContext, ValidationResult } from '@governance/qa/types';

class CustomBusinessLogicValidator implements BaseValidator {
  async validate(context: ValidationContext): Promise<ValidationResult> {
    const { data } = context;

    // 自定義業務邏輯
    const violations = [];

    if (data.price && data.price < 0) {
      violations.push('Price cannot be negative');
    }

    if (data.quantity && data.quantity > 10000) {
      violations.push('Quantity exceeds maximum limit');
    }

    return {
      validatorName: 'business_logic',
      passed: violations.length === 0,
      violations,
      severity: 'medium'
    };
  }
}

// 註冊自定義驗證器
qaEngine.registerValidator('business_logic', new CustomBusinessLogicValidator());

// 使用
const result = await qaEngine.validateInline(orderData, ['business_logic']);
```

---

## 效能優化技巧

### 1. 選擇性驗證

```typescript
// 只在關鍵路徑啟用全部驗證器
if (context.dimensionId === '06') { // security
  validators = ['schema', 'security', 'compliance', 'semantic'];
} else {
  validators = ['schema']; // 其他維度只檢查結構
}
```

### 2. 並行驗證

```typescript
const qaEngine = new RealtimeQAEngine({
  parallelValidators: true, // 開啟並行
  maxLatencyMs: 150
});
```

### 3. 熔斷器

```typescript
const qaEngine = new RealtimeQAEngine({
  circuitBreaker: {
    enabled: true,
    failureThreshold: 5, // 5 次失敗後打開熔斷器
    timeoutMs: 500 // 500ms 後重試
  }
});
```

---

**文檔版本：** v1.0
**最後更新：** 2025-12-12
**維護者：** QA Team
