# 基础示例 / Basic Examples

> **路径**: `src/代码圣殿/基础示例/`  
> **难度**: 入门级 (Beginner)  
> **前置知识**: 基本编程知识

---

## 📋 概述

基础示例提供系统最基本的使用方式，适合初学者快速上手。所有示例都经过验证，可以直接运行。

---

## 🎯 示例分类

### 1. Hello World 示例

最简单的入门示例，帮助您快速了解系统基本操作。

#### 简单工作流 (Simple Workflow)

```typescript
// examples/hello-world/simple-workflow.ts
import { IntelligentAutomation } from '@machinenativeops/automation-sdk';

async function simpleWorkflow() {
  const automation = new IntelligentAutomation({
    apiKey: process.env.API_KEY,
    baseUrl: process.env.BASE_URL
  });

  const workflow = await automation.createWorkflow({
    name: "示例工作流",
    description: "最简单的工作流示例",
    steps: [
      {
        name: "step1",
        type: "task",
        action: "echo",
        params: { message: "Hello, World!" }
      }
    ]
  });

  await workflow.execute();
  console.log("工作流执行完成！");
}

simpleWorkflow().catch(console.error);
```

**运行方式**:
```bash
npm run example:simple-workflow
```

#### 基础自动化 (Basic Automation)

展示如何创建基础的自动化任务。

📂 [查看示例代码](./examples/hello-world/basic-automation.ts)

#### 数据处理 (Data Processing)

展示基础的数据处理流程。

📂 [查看示例代码](./examples/hello-world/data-processing.ts)

#### API使用 (API Usage)

展示如何使用系统API进行基本操作。

📂 [查看示例代码](./examples/hello-world/api-usage.ts)

---

### 2. 核心概念示例

展示系统核心概念的实际应用。

#### 工作流定义 (Workflow Definition)

```yaml
# examples/core-concepts/workflow-definition.yaml
apiVersion: automation.io/v1
kind: Workflow
metadata:
  name: example-workflow
  description: 工作流定义示例
spec:
  triggers:
    - type: schedule
      cron: "0 */6 * * *"
  steps:
    - name: fetch-data
      type: http-request
      config:
        method: GET
        url: "https://api.example.com/data"
    
    - name: process-data
      type: transform
      config:
        script: |
          return data.map(item => ({
            ...item,
            processed: true
          }));
    
    - name: save-results
      type: database
      config:
        operation: insert
        table: results
```

#### 任务创建 (Task Creation)

展示如何创建和管理任务。

📂 [查看示例代码](./examples/core-concepts/task-creation.ts)

#### 事件处理 (Event Handling)

展示如何处理系统事件。

📂 [查看示例代码](./examples/core-concepts/event-handling.ts)

#### 状态管理 (State Management)

展示如何管理工作流和任务的状态。

📂 [查看示例代码](./examples/core-concepts/state-management.ts)

---

### 3. 常见模式示例

展示开发中常用的设计模式。

#### 重试模式 (Retry Pattern)

```typescript
// examples/common-patterns/retry-pattern.ts
import { IntelligentAutomation, RetryPolicy } from '@machinenativeops/automation-sdk';

async function retryPatternExample() {
  const automation = new IntelligentAutomation();

  const retryPolicy: RetryPolicy = {
    maxAttempts: 3,
    backoff: 'exponential',
    initialDelay: 1000,
    maxDelay: 10000,
    retryOn: ['NETWORK_ERROR', 'TIMEOUT']
  };

  const result = await automation.executeWithRetry(
    async () => {
      // 可能失败的操作
      return await fetchData();
    },
    retryPolicy
  );

  console.log('操作成功完成:', result);
}
```

#### 熔断器模式 (Circuit Breaker)

防止故障级联，提高系统稳定性。

📂 [查看示例代码](./examples/common-patterns/circuit-breaker.ts)

#### 批量处理 (Bulk Processing)

展示如何高效处理大量数据。

📂 [查看示例代码](./examples/common-patterns/bulk-processing.ts)

#### 异步处理 (Async Processing)

展示异步任务的处理方式。

📂 [查看示例代码](./examples/common-patterns/async-processing.ts)

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
npm install

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入您的 API Key 等信息
```

### 2. 运行示例

```bash
# 运行所有基础示例
npm run examples:basic:all

# 运行特定示例
npm run example:simple-workflow
npm run example:retry-pattern
npm run example:task-creation
```

### 3. 查看结果

示例运行后，结果将输出到控制台和 `logs/` 目录。

---

## 📚 示例列表

| 示例名称 | 文件路径 | 语言 | 难度 |
|---------|---------|------|------|
| 简单工作流 | `examples/hello-world/simple-workflow.ts` | TypeScript | ⭐ |
| 基础自动化 | `examples/hello-world/basic-automation.ts` | TypeScript | ⭐ |
| 数据处理 | `examples/hello-world/data-processing.ts` | TypeScript | ⭐ |
| API使用 | `examples/hello-world/api-usage.ts` | TypeScript | ⭐ |
| 工作流定义 | `examples/core-concepts/workflow-definition.yaml` | YAML | ⭐⭐ |
| 任务创建 | `examples/core-concepts/task-creation.ts` | TypeScript | ⭐⭐ |
| 事件处理 | `examples/core-concepts/event-handling.ts` | TypeScript | ⭐⭐ |
| 状态管理 | `examples/core-concepts/state-management.ts` | TypeScript | ⭐⭐ |
| 重试模式 | `examples/common-patterns/retry-pattern.ts` | TypeScript | ⭐⭐ |
| 熔断器 | `examples/common-patterns/circuit-breaker.ts` | TypeScript | ⭐⭐ |
| 批量处理 | `examples/common-patterns/bulk-processing.ts` | TypeScript | ⭐⭐ |
| 异步处理 | `examples/common-patterns/async-processing.ts` | TypeScript | ⭐⭐ |

---

## 🔍 深入学习

完成基础示例后，您可以继续学习：

1. **集成示例** - 学习如何集成外部系统
2. **最佳实践** - 了解生产环境的最佳实践
3. **高级用法** - 掌握系统的高级特性

📂 [查看所有示例类别](../README.md)

---

## 🤝 贡献

欢迎贡献新的基础示例！提交前请确保：

- ✅ 代码简洁易懂
- ✅ 包含详细注释
- ✅ 可以独立运行
- ✅ 通过所有测试

---

## 📞 获取帮助

- 📖 [完整文档](../../docs/README.md)
- 💬 [开发者论坛](https://forum.machinenativeops.com)
- 🐛 [报告问题](https://github.com/MachineNativeOps/MachineNativeOps/issues)

---

**最后更新**: 2025-12-19
