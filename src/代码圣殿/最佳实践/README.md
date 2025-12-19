# 最佳实践 / Best Practices

> **路径**: `src/代码圣殿/最佳实践/`  
> **难度**: 中高级 (Intermediate to Advanced)  
> **前置知识**: 系统架构、设计模式、生产环境经验

---

## 📋 概述

最佳实践展示生产环境中经过验证的代码规范、设计模式和架构方案，帮助您构建高质量、可维护的系统。

---

## 🎯 实践类别

### 1. 编码标准 (`coding-standards/`)

#### 整洁代码示例

```typescript
// examples/coding-standards/clean-code.ts

// ❌ 不好的实践
function proc(d: any) {
  let r = [];
  for (let i = 0; i < d.length; i++) {
    if (d[i].s === 'active') {
      r.push(d[i]);
    }
  }
  return r;
}

// ✅ 好的实践
interface User {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: Date;
}

function filterActiveUsers(users: User[]): User[] {
  return users.filter(user => user.status === 'active');
}

// ✅ 更好的实践 - 使用函数式编程
const isActiveUser = (user: User): boolean => user.status === 'active';

const filterActiveUsers = (users: User[]): User[] => 
  users.filter(isActiveUser);
```

**核心原则**:
- 使用有意义的命名
- 函数职责单一
- 避免深层嵌套
- 使用类型系统
- 写自解释的代码

📂 [查看完整示例](./examples/coding-standards/clean-code.ts)

#### 设计模式示例

```typescript
// examples/coding-standards/design-patterns.ts

// 策略模式 (Strategy Pattern)
interface PaymentStrategy {
  processPayment(amount: number): Promise<PaymentResult>;
}

class CreditCardPayment implements PaymentStrategy {
  async processPayment(amount: number): Promise<PaymentResult> {
    // 信用卡支付逻辑
    return { success: true, transactionId: generateId() };
  }
}

class PayPalPayment implements PaymentStrategy {
  async processPayment(amount: number): Promise<PaymentResult> {
    // PayPal支付逻辑
    return { success: true, transactionId: generateId() };
  }
}

class PaymentProcessor {
  constructor(private strategy: PaymentStrategy) {}

  async process(amount: number): Promise<PaymentResult> {
    return this.strategy.processPayment(amount);
  }

  setStrategy(strategy: PaymentStrategy): void {
    this.strategy = strategy;
  }
}

// 使用
const processor = new PaymentProcessor(new CreditCardPayment());
await processor.process(100);

processor.setStrategy(new PayPalPayment());
await processor.process(100);
```

📂 **其他设计模式**:
- 工厂模式: `examples/coding-standards/factory-pattern.ts`
- 单例模式: `examples/coding-standards/singleton-pattern.ts`
- 观察者模式: `examples/coding-standards/observer-pattern.ts`

#### 错误处理最佳实践

```typescript
// examples/coding-standards/error-handling.ts

// 自定义错误类
class WorkflowExecutionError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly details?: unknown
  ) {
    super(message);
    this.name = 'WorkflowExecutionError';
  }
}

// 结果类型（替代抛出异常）
type Result<T, E = Error> = 
  | { success: true; data: T }
  | { success: false; error: E };

async function executeWorkflow(
  workflowId: string
): Promise<Result<WorkflowResult, WorkflowExecutionError>> {
  try {
    const workflow = await loadWorkflow(workflowId);
    const result = await workflow.execute();
    
    return { success: true, data: result };
  } catch (error) {
    if (error instanceof ValidationError) {
      return {
        success: false,
        error: new WorkflowExecutionError(
          'Workflow validation failed',
          'VALIDATION_ERROR',
          error
        )
      };
    }
    
    return {
      success: false,
      error: new WorkflowExecutionError(
        'Workflow execution failed',
        'EXECUTION_ERROR',
        error
      )
    };
  }
}

// 使用
const result = await executeWorkflow('workflow-123');
if (result.success) {
  console.log('Success:', result.data);
} else {
  console.error('Error:', result.error.code, result.error.message);
}
```

---

### 2. 性能优化 (`performance-optimization/`)

#### 数据库优化

```typescript
// examples/performance-optimization/database-optimization.ts

// ❌ N+1 查询问题
async function getUsersWithPostsBad() {
  const users = await db.query('SELECT * FROM users');
  
  for (const user of users) {
    user.posts = await db.query(
      'SELECT * FROM posts WHERE user_id = ?',
      [user.id]
    );
  }
  
  return users;
}

// ✅ 使用 JOIN 优化
async function getUsersWithPostsGood() {
  return db.query(`
    SELECT 
      u.*,
      json_agg(p.*) as posts
    FROM users u
    LEFT JOIN posts p ON p.user_id = u.id
    GROUP BY u.id
  `);
}

// ✅ 使用数据加载器（DataLoader）
import DataLoader from 'dataloader';

const postLoader = new DataLoader(async (userIds: string[]) => {
  const posts = await db.query(
    'SELECT * FROM posts WHERE user_id = ANY($1)',
    [userIds]
  );
  
  return userIds.map(userId =>
    posts.filter(post => post.user_id === userId)
  );
});

async function getUsersWithPostsBest() {
  const users = await db.query('SELECT * FROM users');
  
  await Promise.all(
    users.map(async user => {
      user.posts = await postLoader.load(user.id);
    })
  );
  
  return users;
}
```

📂 **其他性能优化**:
- API优化: `examples/performance-optimization/api-optimization.ts`
- 内存管理: `examples/performance-optimization/memory-management.ts`
- 并发处理: `examples/performance-optimization/concurrency.ts`

---

### 3. 安全实践 (`security-practices/`)

#### 安全编码

```typescript
// examples/security-practices/secure-coding.ts

import crypto from 'crypto';
import { sanitize } from 'validator';

// ✅ 输入验证和清理
function validateAndSanitizeInput(input: unknown): string {
  if (typeof input !== 'string') {
    throw new ValidationError('Input must be a string');
  }
  
  // 清理 HTML
  const sanitized = sanitize(input);
  
  // 长度限制
  if (sanitized.length > 1000) {
    throw new ValidationError('Input too long');
  }
  
  // 格式验证
  const pattern = /^[a-zA-Z0-9\s\-_.]+$/;
  if (!pattern.test(sanitized)) {
    throw new ValidationError('Invalid characters in input');
  }
  
  return sanitized;
}

// ✅ 密码哈希
import bcrypt from 'bcrypt';

async function hashPassword(password: string): Promise<string> {
  const saltRounds = 12;
  return bcrypt.hash(password, saltRounds);
}

async function verifyPassword(
  password: string,
  hash: string
): Promise<boolean> {
  return bcrypt.compare(password, hash);
}

// ✅ 安全的随机数生成
function generateSecureToken(length: number = 32): string {
  return crypto.randomBytes(length).toString('hex');
}

// ✅ SQL注入防护
import { Pool } from 'pg';

async function secureQuery(pool: Pool, userId: string) {
  // ❌ 不安全 - SQL注入风险
  // const query = `SELECT * FROM users WHERE id = '${userId}'`;
  
  // ✅ 安全 - 使用参数化查询
  const query = 'SELECT * FROM users WHERE id = $1';
  const result = await pool.query(query, [userId]);
  
  return result.rows;
}
```

📂 **其他安全实践**:
- 数据保护: `examples/security-practices/data-protection.ts`
- 访问控制: `examples/security-practices/access-control.ts`
- 审计日志: `examples/security-practices/audit-logging.ts`

---

### 4. 部署实践 (`deployment-practices/`)

#### CI/CD流水线

```yaml
# examples/deployment-practices/ci-cd-pipeline.yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Lint
        run: npm run lint
      
      - name: Type check
        run: npm run type-check
      
      - name: Run tests
        run: npm run test:ci
      
      - name: Build
        run: npm run build
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Snyk
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      
      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          severity: 'CRITICAL,HIGH'

  deploy:
    needs: [test, security-scan]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        run: |
          echo "Deploying to production..."
          npm run deploy:prod
```

📂 **其他部署实践**:
- 容器化: `examples/deployment-practices/containerization/`
- 基础设施即代码: `examples/deployment-practices/infrastructure-as-code/`
- 蓝绿部署: `examples/deployment-practices/blue-green-deployment.md`

---

## 📚 最佳实践清单

| 类别 | 实践名称 | 难度 | 优先级 |
|------|---------|------|--------|
| 编码 | 整洁代码 | ⭐⭐ | P0 |
| 编码 | 设计模式 | ⭐⭐⭐ | P1 |
| 编码 | 错误处理 | ⭐⭐ | P0 |
| 编码 | 测试策略 | ⭐⭐⭐ | P0 |
| 性能 | 数据库优化 | ⭐⭐⭐ | P1 |
| 性能 | API优化 | ⭐⭐ | P1 |
| 性能 | 内存管理 | ⭐⭐⭐ | P2 |
| 性能 | 并发处理 | ⭐⭐⭐ | P2 |
| 安全 | 安全编码 | ⭐⭐⭐ | P0 |
| 安全 | 数据保护 | ⭐⭐⭐ | P0 |
| 安全 | 访问控制 | ⭐⭐⭐ | P0 |
| 安全 | 审计日志 | ⭐⭐ | P1 |
| 部署 | CI/CD | ⭐⭐⭐ | P0 |
| 部署 | 容器化 | ⭐⭐ | P1 |
| 部署 | IaC | ⭐⭐⭐ | P1 |

---

## 🔗 相关资源

- [代码规范指南](../../docs/CODE_STYLE_GUIDE.md)
- [架构设计文档](../../docs/ARCHITECTURE.md)
- [安全指南](../../docs/SECURITY.md)

---

**最后更新**: 2025-12-19
