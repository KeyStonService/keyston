# 命名标准 (Naming Standards)

> **治理模块**: 命名治理 (Naming Governance)
> **版本**: v1.0.0
> **状态**: 已批准 (Approved)
> **最后更新**: 2025-01-15

## 概述

命名标准是治理框架的基础模块，定义了整个组织中所有资源的标准化命名约定。标准化的命名对于自动化、可追溯性和团队协作至关重要。

## 目标

- 🎯 **一致性**: 跨所有环境和团队的统一命名模式
- 🤖 **自动化**: 使 CI/CD 和自动化工具能够解析和验证名称
- 📊 **可追溯性**: 通过名称识别资源的环境、版本和所有者
- 🔍 **可发现性**: 轻松查找和识别相关资源
- 🛡️ **合规性**: 符合 DNS-1123、Kubernetes 等技术标准

## 核心命名模式

### 1. Kubernetes 资源命名

#### 格式

```
{environment}-{app}-{resource-type}-{version}
```

#### 组件说明

| 组件 | 描述 | 允许值 | 示例 |
|------|------|--------|------|
| environment | 部署环境 | `dev`, `staging`, `prod` | `prod` |
| app | 应用名称 | 小写字母、数字、连字符 (3-30 字符) | `payment-api` |
| resource-type | 资源类型简写 | `deploy`, `svc`, `ing`, `cm`, `secret`, `pvc`, `sa`, `job`, `cronjob`, `hpa` | `deploy` |
| version | 语义化版本 | `vX.Y.Z[-PRERELEASE]` | `v1.3.0` |

#### 示例

**正确命名** ✅

```yaml
# Deployment
prod-payment-api-deploy-v1.3.0

# Service
prod-payment-api-svc-v1.3.0

# ConfigMap
staging-user-service-cm-v2.0.0-beta1

# Secret
prod-auth-service-secret-v1.0.0

# Ingress
prod-api-gateway-ing-v2.1.0
```

**错误命名** ❌

```yaml
# 不遵循模式
production_Payment_Service_1.3.0

# 使用大写字母
Prod-Payment-Service

# 缺少版本
prod-payment-deploy

# 使用下划线
prod_payment_deploy_v1.3.0

# 版本格式错误
prod-payment-deploy-1.3
```

#### 长度限制

- **Kubernetes 资源名称**: 最大 63 字符 (DNS-1123 子域规范)
- **最佳实践**: 保持在 50 字符以内以提高可读性

### 2. API 端点命名

#### RESTful API 约定

```
/api/v{version}/{resource}[/{id}][/{sub-resource}]
```

#### 规则

1. **复数名词**: 使用复数形式表示集合

   ```
   ✅ /api/v1/users
   ❌ /api/v1/user
   ```

2. **小写与连字符**: 使用小写字母和连字符分隔

   ```
   ✅ /api/v1/payment-methods
   ❌ /api/v1/paymentMethods
   ❌ /api/v1/payment_methods
   ```

3. **层次结构**: 使用路径表示资源关系

   ```
   /api/v1/users/{userId}/orders
   /api/v1/orders/{orderId}/items
   ```

4. **HTTP 方法语义**:
   - `GET /api/v1/users` - 获取用户列表
   - `GET /api/v1/users/{id}` - 获取单个用户
   - `POST /api/v1/users` - 创建用户
   - `PUT /api/v1/users/{id}` - 更新用户
   - `DELETE /api/v1/users/{id}` - 删除用户

#### 示例

```
✅ GET /api/v1/payment-transactions
✅ POST /api/v2/user-profiles
✅ GET /api/v1/orders/{orderId}/shipping-address

❌ GET /api/v1/getPayments
❌ POST /api/v1/CreateUser
❌ GET /api/UserProfile
```

### 3. CI/CD Pipeline 命名

#### 格式

```
{repository}-{action}-{target}
```

#### 组件说明

| 组件 | 描述 | 示例 |
|------|------|------|
| repository | 代码仓库名称 | `payment-service` |
| action | Pipeline 操作 | `build`, `test`, `deploy`, `release` |
| target | 目标环境/产物 | `staging`, `prod`, `docker`, `helm` |

#### 示例

```yaml
# GitHub Actions / GitLab CI
✅ payment-service-build-docker
✅ user-api-deploy-staging
✅ auth-service-test-unit
✅ frontend-deploy-prod
✅ platform-release-helm

# Jenkins
✅ payment-service/build-docker
✅ user-api/deploy-staging
```

### 4. Git 分支命名

#### 格式

```
{type}/{ticket-id}-{short-description}
```

#### 分支类型

| 类型 | 用途 | 示例 |
|------|------|------|
| `feature/` | 新功能开发 | `feature/JIRA-123-add-payment-method` |
| `bugfix/` | Bug 修复 | `bugfix/JIRA-456-fix-login-timeout` |
| `hotfix/` | 生产环境紧急修复 | `hotfix/JIRA-789-fix-critical-security-issue` |
| `release/` | 发布分支 | `release/v1.3.0` |
| `refactor/` | 代码重构 | `refactor/JIRA-234-improve-error-handling` |
| `docs/` | 文档更新 | `docs/update-api-documentation` |

### 5. 数据库命名

#### 表名

```
{domain}_{entity}
```

```sql
-- ✅ 正确
users
payment_transactions
order_items
customer_addresses

-- ❌ 错误
User
PaymentTransactions
tbl_order_items
```

#### 列名

```
-- ✅ 正确: snake_case
user_id
created_at
payment_method
total_amount

-- ❌ 错误: camelCase 或其他
userId
CreatedAt
PaymentMethod
```

## 验证工具

### 自动化验证

所有命名标准都通过自动化工具强制执行：

#### 1. Bash 生成器

```bash
./tools/governance/bash/generate_resource_name.sh \
  --environment prod \
  --app payment-api \
  --resource-type deploy \
  --version v1.3.0
```

**输出**: `prod-payment-api-deploy-v1.3.0`

#### 2. Python 验证器

```bash
python tools/governance/python/validate_naming.py \
  --files k8s/deployment.yaml \
  --policies policies/naming/ \
  --schemas schemas/
```

#### 3. CI/CD 集成

GitHub Actions 示例：

```yaml
- name: Validate Naming
  uses: ./.github/workflows/naming-check.yml
  with:
    changed-files-only: true
```

## JSON Schema 验证

所有命名模式都定义在 `schemas/resource-name.schema.yaml` 中，可被自动化工具消费：

```yaml
# schemas/resource-name.schema.yaml
properties:
  environment:
    type: string
    pattern: "^(dev|staging|prod)$"
  app:
    type: string
    pattern: "^[a-z0-9-]{3,30}$"
  resourceType:
    type: string
    enum: ["deploy", "svc", "ing", "cm", "secret"]
  version:
    type: string
    pattern: "^v\\d+\\.\\d+\\.\\d+(-[a-zA-Z0-9]+)?$"
```

## 策略与执行

### 执行级别

| 级别 | 描述 | 行为 |
|------|------|------|
| **advisory** | 建议性 | 警告但不阻止 |
| **warning** | 警告 | 记录违规，通知团队 |
| **error** | 错误 | 阻止 PR 合并或部署 |

### 策略配置

策略定义在 `policies/naming/` 目录：

```yaml
# policies/naming/k8s-deployment-naming.yaml
apiVersion: governance.machinenativeops.io/v1alpha1
kind: NamingPolicy
metadata:
  name: k8s-deployment-standard
spec:
  pattern: "{{ .environment }}-{{ .app }}-deploy-{{ .version }}"
  enforcement:
    level: "error"
    scope: ["production", "staging"]
```

## 例外处理

如果必须偏离命名标准，必须提交例外请求：

### 例外请求流程

1. **提交请求**: 使用 `templates/governance/forms/exception-request.template.yaml`
2. **风险评估**: 评估命名偏离的影响
3. **批准流程**:
   - 低风险: 团队主管批准
   - 中风险: 经理 + 治理委员会
   - 高风险: VP + 治理委员会
4. **时间限制**: 例外必须有明确的到期日期
5. **补救计划**: 必须有迁移到标准命名的计划

### 例外示例

```yaml
# src/governance/dimensions/examples/exception/EXC-2025-001.yaml
metadata:
  id: "EXC-2025-001"
  title: "Legacy System 命名例外"
spec:
  policyViolated: "k8s-deployment-standard"
  item:
    resourceName: "old-payment-system"
    expectedPattern: "prod-payment-legacy-deploy-v1.0.0"
  reason: "历史遗留系统，重命名会影响多个依赖服务"
  riskEvaluation:
    riskLevel: "中"
    impact: "需要手动维护，自动化工具可能无法识别"
  requestedExpire: "2025-12-31"
  remediation:
    plan: "在 2025 Q4 迁移到新系统并采用标准命名"
```

## 监控与告警

### Prometheus 指标

```promql
# 命名合规率
(governance_naming_compliant_resources / governance_naming_total_resources) * 100

# 命名违规数量
governance_naming_violations_total
```

### 告警规则

```yaml
# templates/governance/k8s/prometheus-rule-naming-alert.template.yaml
- alert: NamingComplianceRateLow
  expr: |
    (sum(governance_naming_compliant_resources) /
     sum(governance_naming_total_resources)) * 100 < 90
  for: 15m
  labels:
    severity: warning
```

### Grafana 仪表板

查看命名合规性仪表板：

```
http://grafana.example.com/d/governance-naming-compliance
```

## 培训与入职

### 新团队成员

1. **阅读本文档**: 理解命名标准和原理
2. **完成练习**: 使用生成器工具创建符合规范的名称
3. **通过验证**: 首次 PR 必须通过命名验证检查

### 团队培训

- **频率**: 每季度回顾
- **内容**: 常见错误、新增模式、工具更新
- **评估**: 通过代码审查验证掌握程度

## 审计与报告

### 月度审计

每月生成命名合规性审计报告：

```bash
python tools/governance/python/audit_naming_compliance.py \
  --period 2025-01 \
  --output reports/audit/AUD-2025-01-naming.yaml
```

### 审计指标

- **合规率**: 符合标准的资源百分比
- **违规类型**: 按违规类型分类统计
- **趋势分析**: 与上月对比
- **热点资源**: 违规最多的资源类型

## 参考资料

### 外部标准

- [DNS-1123 规范](https://tools.ietf.org/html/rfc1123)
- [Kubernetes 命名约定](https://kubernetes.io/docs/concepts/overview/working-with-objects/names/)
- [语义化版本](https://semver.org/)
- [RESTful API 设计最佳实践](https://restfulapi.net/)

### 内部资源

- `schemas/resource-name.schema.yaml` - 命名 Schema 定义
- `policies/naming/` - 所有命名策略
- `tools/governance/bash/generate_resource_name.sh` - 名称生成器
- `tools/governance/python/validate_naming.py` - 名称验证器
- `src/governance/dimensions/27-templates/examples/` - 示例和参考

## FAQ

### Q: 为什么使用连字符而不是下划线？

A: Kubernetes DNS-1123 规范要求使用连字符。下划线不被允许。

### Q: 可以省略版本号吗？

A: 不可以。版本号对于追溯性和回滚至关重要。必须始终包含语义化版本。

### Q: 如何处理超过 63 字符的名称？

A: 缩短应用名称或使用缩写。如果确实无法满足，提交例外请求。

### Q: 预发布版本如何命名？

A: 使用语义化版本的预发布标识符，例如 `v1.3.0-beta1`, `v2.0.0-rc2`。

### Q: 多区域部署如何命名？

A: 可以在应用名称中包含区域信息，例如 `prod-payment-api-us-east-deploy-v1.3.0`，或使用命名空间隔离不同区域。

## 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| v1.0.0 | 2025-01-15 | 初始版本，定义核心命名标准 | Governance Team |

---

**下一步**: 阅读 [05-change-management.md](./05-change-management.md) 了解如何管理命名变更。
