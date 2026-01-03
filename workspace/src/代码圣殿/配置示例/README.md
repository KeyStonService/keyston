# 配置示例 / Configuration Examples

> **路径**: `src/代码圣殿/配置示例/`  
> **难度**: 中级 (Intermediate)  
> **前置知识**: YAML/JSON基础、环境配置概念

---

## 📋 概述

配置示例提供各种环境和场景下的配置文件模板，帮助您快速配置系统以满足不同需求。

---

## 🎯 配置类别

### 1. 环境配置 (`environment-configs/`)

#### 开发环境配置

```yaml
# examples/environment-configs/development.yaml
apiVersion: automation.io/v1
kind: EnvironmentConfig
metadata:
  name: development
  environment: dev
spec:
  api:
    baseUrl: "http://localhost:3000"
    timeout: 30000
    retryAttempts: 3
  
  database:
    host: "localhost"
    port: 5432
    database: "automation_dev"
    pool:
      min: 2
      max: 10
  
  logging:
    level: "debug"
    format: "pretty"
    destination: "console"
  
  features:
    enableDebugMode: true
    enableHotReload: true
    enableMockServices: true
  
  monitoring:
    enabled: false
    sampleRate: 1.0
```

📂 **其他环境配置**:

- 预发布环境: `examples/environment-configs/staging.yaml`
- 生产环境: `examples/environment-configs/production.yaml`
- 测试环境: `examples/environment-configs/testing.yaml`

---

### 2. 安全配置 (`security-configs/`)

#### 认证配置

```yaml
# examples/security-configs/authentication.yaml
apiVersion: security.automation.io/v1
kind: AuthenticationConfig
metadata:
  name: auth-config
spec:
  providers:
    - name: jwt
      type: jwt
      config:
        secret: "${JWT_SECRET}"
        algorithm: "HS256"
        expiresIn: "24h"
        issuer: "automation-system"
    
    - name: oauth2
      type: oauth2
      config:
        clientId: "${OAUTH_CLIENT_ID}"
        clientSecret: "${OAUTH_CLIENT_SECRET}"
        authorizationUrl: "https://auth.example.com/oauth/authorize"
        tokenUrl: "https://auth.example.com/oauth/token"
        scopes: ["read", "write", "admin"]
    
    - name: api-key
      type: api-key
      config:
        header: "X-API-Key"
        queryParam: "api_key"
        validateAgainst: "database"
  
  session:
    type: "redis"
    ttl: 86400
    redis:
      host: "${REDIS_HOST}"
      port: 6379
      db: 0
  
  passwordPolicy:
    minLength: 12
    requireUppercase: true
    requireLowercase: true
    requireNumbers: true
    requireSpecialChars: true
    maxAge: 90 # days
```

📂 **其他安全配置**:

- 授权配置: `examples/security-configs/authorization.yaml`
- 加密配置: `examples/security-configs/encryption.yaml`
- 网络策略: `examples/security-configs/network-policies.yaml`

---

### 3. 性能配置 (`performance-configs/`)

#### 缓存配置

```yaml
# examples/performance-configs/caching.yaml
apiVersion: performance.automation.io/v1
kind: CachingConfig
metadata:
  name: cache-config
spec:
  providers:
    - name: redis-cache
      type: redis
      config:
        host: "${REDIS_HOST}"
        port: 6379
        db: 1
        keyPrefix: "cache:"
        ttl: 3600 # 1 hour default
        maxMemory: "2gb"
        evictionPolicy: "allkeys-lru"
    
    - name: memory-cache
      type: memory
      config:
        maxSize: 100 # MB
        ttl: 300 # 5 minutes
        checkPeriod: 60
  
  strategies:
    - pattern: "/api/users/*"
      provider: redis-cache
      ttl: 1800
      invalidateOn: ["user:updated", "user:deleted"]
    
    - pattern: "/api/config/*"
      provider: memory-cache
      ttl: 600
      staleWhileRevalidate: true
    
    - pattern: "/api/stats/*"
      provider: redis-cache
      ttl: 60
      tags: ["statistics", "dashboard"]
  
  compression:
    enabled: true
    threshold: 1024 # bytes
    algorithm: "gzip"
```

📂 **其他性能配置**:

- 连接池配置: `examples/performance-configs/connection-pooling.yaml`
- 线程池配置: `examples/performance-configs/thread-pooling.yaml`
- 内存优化: `examples/performance-configs/memory-optimization.yaml`

---

### 4. 监控配置 (`monitoring-configs/`)

#### 指标配置

```yaml
# examples/monitoring-configs/metrics.yaml
apiVersion: monitoring.automation.io/v1
kind: MetricsConfig
metadata:
  name: metrics-config
spec:
  exporters:
    - name: prometheus
      type: prometheus
      config:
        port: 9090
        path: "/metrics"
        prefix: "automation_"
        labels:
          service: "intelligent-automation"
          environment: "${ENVIRONMENT}"
    
    - name: datadog
      type: datadog
      config:
        apiKey: "${DATADOG_API_KEY}"
        site: "datadoghq.com"
        flushInterval: 10000
  
  metrics:
    system:
      - name: "cpu_usage"
        type: gauge
        unit: "percent"
        tags: ["system", "resource"]
      
      - name: "memory_usage"
        type: gauge
        unit: "bytes"
        tags: ["system", "resource"]
      
      - name: "disk_io"
        type: counter
        unit: "operations"
        tags: ["system", "io"]
    
    application:
      - name: "request_count"
        type: counter
        tags: ["http", "requests"]
      
      - name: "request_duration"
        type: histogram
        unit: "milliseconds"
        buckets: [10, 50, 100, 250, 500, 1000, 2500, 5000]
        tags: ["http", "performance"]
      
      - name: "error_rate"
        type: gauge
        unit: "percent"
        tags: ["errors", "reliability"]
    
    business:
      - name: "workflow_executions"
        type: counter
        tags: ["workflow", "business"]
      
      - name: "task_completions"
        type: counter
        tags: ["task", "business"]
  
  collection:
    interval: 10000 # 10 seconds
    batchSize: 100
```

📂 **其他监控配置**:

- 日志配置: `examples/monitoring-configs/logging.yaml`
- 告警配置: `examples/monitoring-configs/alerting.yaml`
- 追踪配置: `examples/monitoring-configs/tracing.yaml`

---

## 🚀 使用指南

### 应用配置

```bash
# 复制配置模板
cp examples/environment-configs/development.yaml config/environment.yaml

# 编辑配置
vim config/environment.yaml

# 验证配置
npm run config:validate

# 应用配置
npm run config:apply
```

### 环境变量替换

配置文件支持环境变量替换：

```yaml
database:
  host: "${DB_HOST}"           # 必需的环境变量
  port: "${DB_PORT:-5432}"     # 带默认值的环境变量
  password: "${DB_PASSWORD}"   # 敏感信息使用环境变量
```

### 配置合并

系统支持配置文件分层：

```bash
# 基础配置
config/base.yaml

# 环境特定配置（覆盖基础配置）
config/development.yaml
config/production.yaml

# 本地配置（覆盖所有，不提交到版本控制）
config/local.yaml
```

---

## 📚 配置清单

| 配置类型 | 配置名称 | 文件路径 | 难度 |
|---------|---------|---------|------|
| 环境 | 开发环境 | `environment-configs/development.yaml` | ⭐ |
| 环境 | 预发布环境 | `environment-configs/staging.yaml` | ⭐⭐ |
| 环境 | 生产环境 | `environment-configs/production.yaml` | ⭐⭐⭐ |
| 环境 | 测试环境 | `environment-configs/testing.yaml` | ⭐⭐ |
| 安全 | 认证 | `security-configs/authentication.yaml` | ⭐⭐⭐ |
| 安全 | 授权 | `security-configs/authorization.yaml` | ⭐⭐⭐ |
| 安全 | 加密 | `security-configs/encryption.yaml` | ⭐⭐⭐ |
| 安全 | 网络策略 | `security-configs/network-policies.yaml` | ⭐⭐⭐ |
| 性能 | 缓存 | `performance-configs/caching.yaml` | ⭐⭐ |
| 性能 | 连接池 | `performance-configs/connection-pooling.yaml` | ⭐⭐ |
| 性能 | 线程池 | `performance-configs/thread-pooling.yaml` | ⭐⭐ |
| 监控 | 指标 | `monitoring-configs/metrics.yaml` | ⭐⭐ |
| 监控 | 日志 | `monitoring-configs/logging.yaml` | ⭐⭐ |
| 监控 | 告警 | `monitoring-configs/alerting.yaml` | ⭐⭐⭐ |

---

## 🔒 安全最佳实践

1. **敏感信息**: 永远不要在配置文件中硬编码敏感信息
2. **环境变量**: 使用环境变量或密钥管理服务
3. **权限控制**: 配置文件应该设置适当的文件权限
4. **版本控制**: 不要将包含敏感信息的配置提交到版本控制

```bash
# 设置配置文件权限
chmod 600 config/production.yaml

# 添加到 .gitignore
echo "config/local.yaml" >> .gitignore
echo "config/*.secret.yaml" >> .gitignore
```

---

## 🔗 相关资源

- [环境配置指南](../../docs/configuration/ENVIRONMENT_SETUP.md)
- [安全配置指南](../../docs/SECURITY.md)
- [性能调优指南](../../docs/PERFORMANCE_TUNING.md)

---

**最后更新**: 2025-12-19
