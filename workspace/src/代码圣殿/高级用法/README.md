# 高级用法 / Advanced Usage Examples

> **路径**: `src/代码圣殿/高级用法/`  
> **难度**: 高级 (Advanced)  
> **前置知识**: 系统架构、分布式系统、高级编程概念

---

## 📋 概述

高级用法示例展示系统的高级特性和复杂场景的实现方案，适合有经验的开发者探索系统的深层能力。

---

## 🎯 高级特性类别

### 1. 自定义扩展 (`custom-extensions/`)

#### 自定义任务

```typescript
// examples/custom-extensions/custom-tasks.ts

import { Task, TaskContext, TaskResult } from '@machinenativeops/automation-sdk';

/**
 * 自定义数据转换任务
 */
class DataTransformTask extends Task {
  name = 'data-transform';
  version = '1.0.0';

  // 定义任务配置schema
  configSchema = {
    type: 'object',
    properties: {
      transformType: {
        type: 'string',
        enum: ['map', 'filter', 'reduce']
      },
      transformer: {
        type: 'string',
        description: 'JavaScript转换函数代码'
      }
    },
    required: ['transformType', 'transformer']
  };

  async execute(context: TaskContext): Promise<TaskResult> {
    const { transformType, transformer } = context.config;
    const inputData = context.input;

    try {
      // 动态执行转换函数（沙箱环境）
      const transformFn = this.createSafeFunction(transformer);
      let result;

      switch (transformType) {
        case 'map':
          result = inputData.map(transformFn);
          break;
        case 'filter':
          result = inputData.filter(transformFn);
          break;
        case 'reduce':
          result = inputData.reduce(transformFn);
          break;
        default:
          throw new Error(`Unknown transform type: ${transformType}`);
      }

      return {
        success: true,
        data: result,
        metadata: {
          itemsProcessed: inputData.length,
          outputSize: result.length
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  private createSafeFunction(code: string): Function {
    // 使用 VM2 或 isolated-vm 创建安全的执行环境
    const vm = require('vm2');
    const sandbox = new vm.NodeVM({
      timeout: 5000,
      sandbox: {
        console: console
      }
    });
    
    return sandbox.run(`module.exports = ${code}`);
  }

  async validate(config: any): Promise<boolean> {
    // 验证配置
    const Ajv = require('ajv');
    const ajv = new Ajv();
    const validate = ajv.compile(this.configSchema);
    return validate(config);
  }
}

// 注册自定义任务
const automation = new IntelligentAutomation();
automation.registerTask(new DataTransformTask());

// 使用自定义任务
const workflow = await automation.createWorkflow({
  name: "使用自定义任务",
  steps: [
    {
      type: 'data-transform',
      config: {
        transformType: 'map',
        transformer: '(item) => ({ ...item, processed: true })'
      }
    }
  ]
});
```

📂 **其他自定义扩展**:

- 自定义工作流: `examples/custom-extensions/custom-workflows.ts`
- 插件开发: `examples/custom-extensions/plugins-development.ts`
- API扩展: `examples/custom-extensions/api-extensions.ts`

---

### 2. 复杂场景 (`complex-scenarios/`)

#### 分布式工作流

```typescript
// examples/complex-scenarios/distributed-workflows.ts

import { 
  DistributedWorkflow,
  WorkflowOrchestrator,
  WorkflowNode
} from '@machinenativeops/automation-sdk';

/**
 * 分布式数据处理工作流
 * 
 * 架构：
 * - Coordinator: 协调器，分配任务
 * - Workers: 工作节点，执行任务
 * - Result Aggregator: 结果聚合器
 */
class DistributedDataProcessing extends DistributedWorkflow {
  constructor() {
    super({
      name: 'distributed-data-processing',
      coordinatorConfig: {
        maxWorkers: 10,
        taskTimeout: 30000,
        retryAttempts: 3
      }
    });
  }

  async defineTopology() {
    // 定义工作流拓扑
    return {
      nodes: [
        {
          id: 'coordinator',
          type: 'coordinator',
          config: {
            splitStrategy: 'round-robin',
            chunkSize: 1000
          }
        },
        {
          id: 'worker-pool',
          type: 'worker-pool',
          instances: 5,
          config: {
            taskHandler: this.processChunk.bind(this)
          }
        },
        {
          id: 'aggregator',
          type: 'aggregator',
          config: {
            aggregationStrategy: 'merge',
            outputFormat: 'json'
          }
        }
      ],
      edges: [
        { from: 'coordinator', to: 'worker-pool' },
        { from: 'worker-pool', to: 'aggregator' }
      ]
    };
  }

  async processChunk(chunk: any[]): Promise<any> {
    // 处理数据块
    return chunk.map(item => ({
      ...item,
      processed: true,
      timestamp: new Date(),
      workerId: process.pid
    }));
  }

  async execute(data: any[]) {
    const orchestrator = new WorkflowOrchestrator(this);
    
    // 启动工作流
    await orchestrator.start();
    
    try {
      // 提交数据
      const result = await orchestrator.submit(data);
      
      console.log(`处理完成：
        - 总数据量: ${data.length}
        - 处理耗时: ${result.duration}ms
        - Worker数量: ${result.workersUsed}
      `);
      
      return result.data;
    } finally {
      await orchestrator.stop();
    }
  }
}

// 使用分布式工作流
const workflow = new DistributedDataProcessing();
const largeDataset = generateLargeDataset(100000);
const result = await workflow.execute(largeDataset);
```

#### 长运行流程（Saga模式）

```typescript
// examples/complex-scenarios/saga-pattern.ts

import { Saga, SagaStep } from '@machinenativeops/automation-sdk';

/**
 * 订单处理Saga
 * 
 * 流程：
 * 1. 创建订单
 * 2. 扣减库存
 * 3. 处理支付
 * 4. 发送通知
 * 
 * 每步都有补偿操作，失败时自动回滚
 */
class OrderProcessingSaga extends Saga {
  async defineSteps(): Promise<SagaStep[]> {
    return [
      {
        name: 'create-order',
        action: async (context) => {
          const order = await orderService.create(context.orderData);
          return { orderId: order.id };
        },
        compensation: async (context) => {
          await orderService.delete(context.orderId);
          console.log('已回滚：删除订单');
        }
      },
      {
        name: 'reserve-inventory',
        action: async (context) => {
          const reservation = await inventoryService.reserve(
            context.orderData.items,
            context.orderId
          );
          return { reservationId: reservation.id };
        },
        compensation: async (context) => {
          await inventoryService.release(context.reservationId);
          console.log('已回滚：释放库存');
        }
      },
      {
        name: 'process-payment',
        action: async (context) => {
          const payment = await paymentService.charge(
            context.orderData.amount,
            context.orderData.paymentMethod
          );
          return { paymentId: payment.id };
        },
        compensation: async (context) => {
          await paymentService.refund(context.paymentId);
          console.log('已回滚：退款');
        }
      },
      {
        name: 'send-notification',
        action: async (context) => {
          await notificationService.sendOrderConfirmation(
            context.orderData.email,
            context.orderId
          );
          return {};
        },
        compensation: async (context) => {
          // 通知不需要补偿
          console.log('已回滚：取消通知（可选）');
        }
      }
    ];
  }

  async execute(orderData: any) {
    try {
      const result = await this.run({ orderData });
      console.log('订单处理成功:', result);
      return result;
    } catch (error) {
      console.error('订单处理失败，已执行补偿操作:', error);
      throw error;
    }
  }
}

// 使用Saga
const saga = new OrderProcessingSaga();
await saga.execute({
  items: [{ sku: 'ITEM-001', quantity: 2 }],
  amount: 99.99,
  paymentMethod: 'credit-card',
  email: 'customer@example.com'
});
```

📂 **其他复杂场景**:

- 事件溯源: `examples/complex-scenarios/event-sourcing.ts`
- CQRS模式: `examples/complex-scenarios/cqrs-pattern.ts`

---

### 3. 优化技术 (`optimization-techniques/`)

#### 性能调优

```typescript
// examples/optimization-techniques/performance-tuning.ts

/**
 * 批量操作优化
 */
class BatchProcessor {
  private batchSize: number;
  private flushInterval: number;
  private buffer: any[] = [];
  private timer: NodeJS.Timeout | null = null;

  constructor(
    private processFn: (items: any[]) => Promise<void>,
    options: {
      batchSize?: number;
      flushInterval?: number;
    } = {}
  ) {
    this.batchSize = options.batchSize || 100;
    this.flushInterval = options.flushInterval || 5000;
  }

  async add(item: any): Promise<void> {
    this.buffer.push(item);

    if (this.buffer.length >= this.batchSize) {
      await this.flush();
    } else if (!this.timer) {
      this.timer = setTimeout(() => this.flush(), this.flushInterval);
    }
  }

  async flush(): Promise<void> {
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }

    if (this.buffer.length === 0) return;

    const items = this.buffer.splice(0, this.buffer.length);
    await this.processFn(items);
  }

  async close(): Promise<void> {
    await this.flush();
  }
}

// 使用批量处理器
const processor = new BatchProcessor(
  async (items) => {
    await db.batchInsert('logs', items);
    console.log(`批量插入 ${items.length} 条记录`);
  },
  {
    batchSize: 100,
    flushInterval: 5000
  }
);

// 添加数据（会自动批量处理）
for (let i = 0; i < 1000; i++) {
  await processor.add({ message: `Log ${i}` });
}

await processor.close();
```

#### 可扩展性解决方案

```typescript
// examples/optimization-techniques/scalability-solutions.ts

/**
 * 水平扩展 - 负载均衡器
 */
class LoadBalancer {
  private workers: Worker[] = [];
  private currentIndex = 0;

  constructor(private workerCount: number) {
    this.initializeWorkers();
  }

  private initializeWorkers(): void {
    for (let i = 0; i < this.workerCount; i++) {
      this.workers.push(new Worker(`worker-${i}`));
    }
  }

  // 轮询策略
  getNextWorker(): Worker {
    const worker = this.workers[this.currentIndex];
    this.currentIndex = (this.currentIndex + 1) % this.workers.length;
    return worker;
  }

  // 最少连接策略
  getLeastBusyWorker(): Worker {
    return this.workers.reduce((least, worker) => 
      worker.activeConnections < least.activeConnections ? worker : least
    );
  }

  // 加权轮询
  getWeightedWorker(): Worker {
    // 实现加权负载均衡
    const totalWeight = this.workers.reduce((sum, w) => sum + w.weight, 0);
    let random = Math.random() * totalWeight;

    for (const worker of this.workers) {
      random -= worker.weight;
      if (random <= 0) return worker;
    }

    return this.workers[0];
  }

  async execute(task: any): Promise<any> {
    const worker = this.getLeastBusyWorker();
    return worker.execute(task);
  }
}
```

📂 **其他优化技术**:

- 弹性模式: `examples/optimization-techniques/resilience-patterns.ts`
- 成本优化: `examples/optimization-techniques/cost-optimization.ts`

---

## 📚 高级用法清单

| 类别 | 示例名称 | 难度 | 适用场景 |
|------|---------|------|---------|
| 扩展 | 自定义任务 | ⭐⭐⭐ | 特殊业务逻辑 |
| 扩展 | 插件开发 | ⭐⭐⭐⭐ | 系统功能扩展 |
| 场景 | 分布式工作流 | ⭐⭐⭐⭐ | 大规模数据处理 |
| 场景 | Saga模式 | ⭐⭐⭐⭐ | 分布式事务 |
| 场景 | 事件溯源 | ⭐⭐⭐⭐⭐ | 审计、回溯 |
| 优化 | 批量处理 | ⭐⭐⭐ | 高吞吐量 |
| 优化 | 负载均衡 | ⭐⭐⭐⭐ | 水平扩展 |
| 优化 | 弹性模式 | ⭐⭐⭐⭐ | 高可用性 |

---

## 🔗 相关资源

- [架构设计文档](../../docs/ARCHITECTURE.md)
- [分布式系统指南](../../docs/DISTRIBUTED_SYSTEMS.md)
- [性能优化指南](../../docs/PERFORMANCE_OPTIMIZATION.md)

---

**最后更新**: 2025-12-19
