# 故障排除 / Troubleshooting Examples

> **路径**: `src/代码圣殿/故障排除/`  
> **难度**: 中级 (Intermediate)  
> **前置知识**: 系统运维基础、日志分析、调试技能

---

## 📋 概述

故障排除示例提供常见问题的诊断方法和解决方案，帮助您快速定位和解决生产环境中的问题。

---

## 🎯 问题类别

### 1. 常见错误 (`common-errors/`)

#### 连接错误解决

```typescript
// examples/common-errors/connection-errors.ts

import { retry } from '../utils/retry';

// 问题：数据库连接失败
// 错误信息：ECONNREFUSED 127.0.0.1:5432

// ✅ 解决方案1：添加重试机制
async function connectWithRetry() {
  const maxRetries = 3;
  const retryDelay = 1000;

  return retry(
    async () => {
      return await pool.connect();
    },
    {
      maxAttempts: maxRetries,
      delay: retryDelay,
      backoff: 'exponential',
      onRetry: (attempt, error) => {
        console.log(`连接失败 (尝试 ${attempt}/${maxRetries}):`, error.message);
      }
    }
  );
}

// ✅ 解决方案2：健康检查
async function waitForDatabase(timeout: number = 30000) {
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    try {
      const client = await pool.connect();
      await client.query('SELECT 1');
      client.release();
      return true;
    } catch (error) {
      console.log('等待数据库就绪...');
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }

  throw new Error('数据库连接超时');
}

// ✅ 解决方案3：连接池配置优化
const pool = new Pool({
  host: process.env.DB_HOST,
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  
  // 连接池配置
  min: 2,
  max: 10,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 5000,
  
  // 重连配置
  keepAlive: true,
  keepAliveInitialDelayMillis: 10000
});
```

**诊断步骤**:

1. 检查服务是否运行
2. 验证网络连接
3. 检查防火墙规则
4. 验证凭证
5. 查看服务日志

📂 [查看完整示例](./examples/common-errors/connection-errors.ts)

#### 超时错误解决

```typescript
// examples/common-errors/timeout-errors.ts

// 问题：API请求超时
// 错误信息：Request timeout of 5000ms exceeded

// ✅ 解决方案1：增加超时时间
const axios = require('axios');

const client = axios.create({
  baseURL: 'https://api.example.com',
  timeout: 30000, // 30秒
  headers: {
    'Content-Type': 'application/json'
  }
});

// ✅ 解决方案2：实现超时控制
async function fetchWithTimeout<T>(
  promise: Promise<T>,
  timeoutMs: number
): Promise<T> {
  return Promise.race([
    promise,
    new Promise<T>((_, reject) =>
      setTimeout(() => reject(new Error('Operation timeout')), timeoutMs)
    )
  ]);
}

// 使用
try {
  const result = await fetchWithTimeout(
    fetch('https://api.example.com/data'),
    10000
  );
} catch (error) {
  if (error.message === 'Operation timeout') {
    console.error('请求超时，请稍后重试');
  }
}

// ✅ 解决方案3：分页处理大数据
async function fetchLargeDataset(pageSize: number = 100) {
  let page = 0;
  let hasMore = true;
  const allData = [];

  while (hasMore) {
    const response = await client.get('/data', {
      params: {
        page,
        pageSize
      }
    });

    allData.push(...response.data.items);
    hasMore = response.data.hasMore;
    page++;

    // 避免过快请求
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  return allData;
}
```

📂 **其他常见错误**:

- 内存错误: `examples/common-errors/memory-errors.ts`
- 权限错误: `examples/common-errors/permission-errors.ts`

---

### 2. 性能问题 (`performance-issues/`)

#### 慢查询优化

```sql
-- examples/performance-issues/slow-queries.sql

-- 问题：查询速度慢
-- 原因：缺少索引、全表扫描

-- ❌ 慢查询
SELECT u.*, COUNT(p.id) as post_count
FROM users u
LEFT JOIN posts p ON p.user_id = u.id
WHERE u.status = 'active'
  AND u.created_at > '2024-01-01'
GROUP BY u.id
ORDER BY post_count DESC
LIMIT 10;

-- 执行计划分析
EXPLAIN ANALYZE
SELECT ...;

-- ✅ 优化1：添加索引
CREATE INDEX idx_users_status_created 
ON users(status, created_at);

CREATE INDEX idx_posts_user_id 
ON posts(user_id);

-- ✅ 优化2：使用物化视图（频繁查询）
CREATE MATERIALIZED VIEW user_post_counts AS
SELECT 
  u.id,
  u.name,
  u.email,
  COUNT(p.id) as post_count
FROM users u
LEFT JOIN posts p ON p.user_id = u.id
WHERE u.status = 'active'
GROUP BY u.id, u.name, u.email;

CREATE INDEX idx_user_post_counts_count 
ON user_post_counts(post_count DESC);

-- 刷新物化视图
REFRESH MATERIALIZED VIEW CONCURRENTLY user_post_counts;

-- ✅ 优化3：使用查询缓存
-- 在应用层实现
```

```typescript
// examples/performance-issues/query-cache.ts
import Redis from 'ioredis';

const redis = new Redis();

async function getCachedUserPosts(userId: string) {
  const cacheKey = `user:${userId}:posts`;
  
  // 尝试从缓存获取
  const cached = await redis.get(cacheKey);
  if (cached) {
    return JSON.parse(cached);
  }
  
  // 从数据库查询
  const posts = await db.query(
    'SELECT * FROM posts WHERE user_id = $1',
    [userId]
  );
  
  // 缓存结果（5分钟）
  await redis.setex(cacheKey, 300, JSON.stringify(posts));
  
  return posts;
}
```

📂 **其他性能问题**:

- 高延迟: `examples/performance-issues/high-latency.ts`
- 资源泄漏: `examples/performance-issues/resource-leaks.ts`
- 瓶颈识别: `examples/performance-issues/bottleneck-identification.ts`

---

### 3. 集成问题 (`integration-issues/`)

#### API兼容性问题

```typescript
// examples/integration-issues/api-compatibility.ts

// 问题：第三方API版本变更导致不兼容

// ✅ 解决方案1：API版本管理
class ApiClient {
  private version: string;

  constructor(version: string = 'v2') {
    this.version = version;
  }

  async fetchUser(userId: string) {
    if (this.version === 'v1') {
      return this.fetchUserV1(userId);
    } else if (this.version === 'v2') {
      return this.fetchUserV2(userId);
    }
    throw new Error(`Unsupported API version: ${this.version}`);
  }

  private async fetchUserV1(userId: string) {
    // V1 API 实现
    const response = await fetch(`/api/v1/users/${userId}`);
    return response.json();
  }

  private async fetchUserV2(userId: string) {
    // V2 API 实现（不同的响应格式）
    const response = await fetch(`/api/v2/users/${userId}`);
    const data = await response.json();
    
    // 转换为统一格式
    return {
      id: data.userId,
      name: data.fullName,
      email: data.emailAddress
    };
  }
}

// ✅ 解决方案2：适配器模式
interface UserData {
  id: string;
  name: string;
  email: string;
}

class ApiV1Adapter {
  async getUser(userId: string): Promise<UserData> {
    const response = await fetch(`/api/v1/users/${userId}`);
    const data = await response.json();
    return data; // V1格式已经匹配
  }
}

class ApiV2Adapter {
  async getUser(userId: string): Promise<UserData> {
    const response = await fetch(`/api/v2/users/${userId}`);
    const data = await response.json();
    
    // 转换V2格式到统一接口
    return {
      id: data.userId,
      name: data.fullName,
      email: data.emailAddress
    };
  }
}

// ✅ 解决方案3：Feature Flag
const apiAdapter = process.env.USE_API_V2 === 'true'
  ? new ApiV2Adapter()
  : new ApiV1Adapter();
```

📂 **其他集成问题**:

- 数据格式问题: `examples/integration-issues/data-format-issues.ts`
- 版本冲突: `examples/integration-issues/version-conflicts.ts`
- 网络问题: `examples/integration-issues/network-issues.ts`

---

## 🔍 诊断工具

### 日志分析

```bash
# 查看应用日志
tail -f /var/log/app/error.log

# 过滤错误日志
grep -i "error\|exception\|failed" /var/log/app/app.log

# 统计错误类型
awk '{print $7}' /var/log/app/error.log | sort | uniq -c | sort -rn
```

### 性能分析

```bash
# Node.js 性能分析
node --prof app.js
node --prof-process isolate-*.log > profile.txt

# 内存分析
node --inspect app.js
# 在 Chrome 中访问 chrome://inspect
```

### 网络诊断

```bash
# 测试连接
nc -zv api.example.com 443

# DNS查询
nslookup api.example.com

# 追踪路由
traceroute api.example.com

# 测试HTTP请求
curl -v https://api.example.com/health
```

---

## 📚 故障排除清单

| 问题类型 | 常见原因 | 解决方案 | 文档 |
|---------|---------|---------|------|
| 连接错误 | 服务未启动、网络问题 | 重试机制、健康检查 | [链接](./examples/common-errors/connection-errors.ts) |
| 超时错误 | 请求过慢、超时设置过短 | 增加超时、分页处理 | [链接](./examples/common-errors/timeout-errors.ts) |
| 内存错误 | 内存泄漏、数据过大 | 流式处理、垃圾回收 | [链接](./examples/common-errors/memory-errors.ts) |
| 慢查询 | 缺少索引、全表扫描 | 添加索引、查询优化 | [链接](./examples/performance-issues/slow-queries.sql) |
| API不兼容 | 版本变更 | 版本管理、适配器 | [链接](./examples/integration-issues/api-compatibility.ts) |

---

## 🔗 相关资源

- [系统监控指南](../../docs/MONITORING.md)
- [日志最佳实践](../../docs/LOGGING_BEST_PRACTICES.md)
- [性能调优指南](../../docs/PERFORMANCE_TUNING.md)

---

**最后更新**: 2025-12-19
