# 指标与审计 (Metrics and Audit)

> **治理模块**: 指标与审计 (Metrics and Audit)
> **版本**: v1.0.0
> **状态**: 已批准 (Approved)
> **最后更新**: 2025-01-15

## 概述

指标与审计模块提供了衡量治理有效性的量化方法。通过持续监控关键指标和定期审计，我们确保治理框架被正确执行，并持续改进。

## 目标

- 📊 **可量化**: 将治理合规性转化为可衡量的指标
- 🔍 **可观测**: 实时监控治理健康状态
- 📈 **可改进**: 基于数据驱动持续优化
- 🔔 **主动告警**: 问题出现时及时发现
- 📋 **可审计**: 定期评估和报告合规性

## 核心指标体系

### 1. 命名合规指标

#### 指标定义

| 指标名称 | 计算方式 | 目标值 | 严重性 |
|---------|---------|--------|--------|
| **命名合规率** | (合规资源数 / 总资源数) × 100% | > 95% | 中 |
| **违规资源数** | count(不符合命名规范的资源) | < 10 | 高 |
| **生产环境违规** | count(生产环境违规资源) | 0 | 严重 |
| **遗留命名比例** | (遗留命名 / 总资源) × 100% | < 5% | 低 |

#### Prometheus 查询

```promql
# 命名合规率
(
  sum(governance_naming_compliant_resources) /
  sum(governance_naming_total_resources)
) * 100

# 按环境分类的违规数
sum(governance_naming_violations) by (environment)

# 按资源类型分类的违规数
sum(governance_naming_violations) by (resource_type)

# 生产环境违规（严重告警）
sum(governance_naming_violations{environment="production"})
```

#### 指标导出器

```python
# tools/governance/python/naming_metrics_exporter.py
from prometheus_client import Gauge, Counter

# 定义指标
naming_compliant = Gauge(
    'governance_naming_compliant_resources',
    'Number of resources compliant with naming standards',
    ['environment', 'resource_type']
)

naming_violations = Counter(
    'governance_naming_violations_total',
    'Total number of naming violations detected',
    ['environment', 'resource_type', 'policy']
)

# 收集指标
def collect_naming_metrics():
    # 扫描 Kubernetes 资源
    resources = get_k8s_resources()
    for resource in resources:
        if validate_naming(resource):
            naming_compliant.labels(
                environment=resource.env,
                resource_type=resource.type
            ).inc()
        else:
            naming_violations.labels(
                environment=resource.env,
                resource_type=resource.type,
                policy=resource.violated_policy
            ).inc()
```

### 2. 变更管理指标

#### 指标定义

| 指标名称 | 计算方式 | 目标值 | 严重性 |
|---------|---------|--------|--------|
| **变更成功率** | (成功变更 / 总变更) × 100% | > 95% | 高 |
| **平均交付时间** | avg(变更完成时间 - 变更提交时间) | < 5 天 | 中 |
| **回滚率** | (回滚数 / 总变更) × 100% | < 5% | 高 |
| **紧急变更比例** | (紧急变更 / 总变更) × 100% | < 5% | 中 |
| **未批准变更数** | count(未经批准的变更) | 0 | 严重 |
| **CAB 审批时间** | avg(批准时间 - 提交时间) | < 2 天 | 低 |

#### Prometheus 查询

```promql
# 变更成功率（24小时）
(
  sum(rate(governance_changes_successful_total[24h])) /
  sum(rate(governance_changes_total[24h]))
) * 100

# 紧急变更比例（7天）
(
  sum(rate(governance_changes_total{type="紧急变更"}[7d])) /
  sum(rate(governance_changes_total[7d]))
) * 100

# 平均交付时间（天）
avg(governance_change_lead_time_seconds / 86400)

# 未批准的变更（严重）
governance_changes_unapproved_total
```

### 3. 例外管理指标

#### 指标定义

| 指标名称 | 计算方式 | 目标值 | 严重性 |
|---------|---------|--------|--------|
| **活跃例外数** | count(状态=active的例外) | < 20 | 中 |
| **高风险例外数** | count(风险=高的例外) | < 5 | 高 |
| **过期例外数** | count(已过期但仍活跃的例外) | 0 | 严重 |
| **平均持续时间** | avg(到期日期 - 创建日期) | < 90 天 | 低 |
| **补救成功率** | (补救数 / 总到期数) × 100% | > 80% | 中 |

#### Prometheus 查询

```promql
# 活跃例外总数
governance_exception_active_total

# 按风险级别分类
sum(governance_exception_active_total) by (risk_level)

# 即将到期（7天内）
count(governance_exception_expiry_timestamp - time() < 7 * 24 * 3600)

# 已过期仍在使用（严重）
governance_exception_expired_active
```

### 4. 治理健康分数

综合指标，反映整体治理健康状况。

#### 计算公式

```
治理健康分数 = (
  命名合规率 × 0.3 +
  变更成功率 × 0.3 +
  例外管理得分 × 0.2 +
  审计通过率 × 0.2
)

其中:
- 例外管理得分 = 100 - (高风险例外数 × 5 + 过期例外数 × 10)
- 审计通过率 = (无高严重性发现的审计 / 总审计) × 100%
```

#### Prometheus 查询

```promql
# 治理健康分数
(
  (
    sum(governance_naming_compliant_resources) /
    sum(governance_naming_total_resources)
  ) * 30 +
  (
    sum(rate(governance_changes_successful_total[24h])) /
    sum(rate(governance_changes_total[24h]))
  ) * 30 +
  clamp_max(
    100 - (
      count(governance_exception_active{risk_level="高"}) * 5 +
      count(governance_exception_expired_active) * 10
    ), 100
  ) * 0.2 +
  governance_audit_pass_rate * 20
)
```

## 告警规则

### 告警级别定义

| 级别 | 描述 | 响应时间 | 示例 |
|------|------|----------|------|
| **critical** | 严重问题，立即处理 | < 15 分钟 | 生产环境违规、未批准变更 |
| **warning** | 需要关注，计划处理 | < 4 小时 | 合规率低、例外即将到期 |
| **info** | 信息性，记录跟踪 | < 1 天 | 遗留模式使用、趋势变化 |

### 命名合规告警

```yaml
# templates/governance/k8s/prometheus-rule-naming-alert.template.yaml
groups:
  - name: governance.naming_compliance
    interval: 5m
    rules:
      # 合规率低于阈值
      - alert: NamingComplianceRateLow
        expr: |
          (
            sum(governance_naming_compliant_resources) /
            sum(governance_naming_total_resources)
          ) * 100 < 90
        for: 15m
        labels:
          severity: warning
          category: governance
          component: naming
        annotations:
          summary: "命名合规率低于阈值"
          description: |
            合规率为 {{ $value | humanizePercentage }}，低于 90% 阈值。
            请审查并修复不合规资源。
          runbook_url: "https://docs.example.com/governance/naming-compliance"

      # 合规率严重低
      - alert: NamingComplianceRateCritical
        expr: |
          (
            sum(governance_naming_compliant_resources) /
            sum(governance_naming_total_resources)
          ) * 100 < 85
        for: 5m
        labels:
          severity: critical
          category: governance
          component: naming
        annotations:
          summary: "命名合规率严重低"
          description: |
            合规率为 {{ $value | humanizePercentage }}，低于 85% 严重阈值。
            立即采取行动！

      # 生产环境违规
      - alert: ProductionNamingViolation
        expr: |
          governance_naming_violations{environment="production"} > 0
        for: 1m
        labels:
          severity: critical
          category: governance
          component: naming
          environment: production
        annotations:
          summary: "生产环境命名违规"
          description: |
            检测到 {{ $value }} 个生产环境命名违规。
            资源类型: {{ $labels.resource_type }}
            命名空间: {{ $labels.namespace }}
```

### 变更管理告警

```yaml
groups:
  - name: governance.change_management
    interval: 5m
    rules:
      # 变更成功率低
      - alert: ChangeSuccessRateLow
        expr: |
          (
            sum(rate(governance_changes_successful_total[24h])) /
            sum(rate(governance_changes_total[24h]))
          ) * 100 < 95
        for: 1h
        labels:
          severity: warning
          category: governance
          component: change-management
        annotations:
          summary: "变更成功率低于阈值"
          description: |
            成功率为 {{ $value | humanizePercentage }}，低于 95% 阈值。
            请审查近期失败的变更。

      # 紧急变更比例过高
      - alert: EmergencyChangeRateHigh
        expr: |
          (
            sum(rate(governance_changes_total{type="紧急变更"}[7d])) /
            sum(rate(governance_changes_total[7d]))
          ) * 100 > 5
        for: 1d
        labels:
          severity: warning
          category: governance
          component: change-management
        annotations:
          summary: "紧急变更比例过高"
          description: |
            紧急变更占比 {{ $value | humanizePercentage }}，超过 5% 阈值。
            请审查变更规划流程。

      # 未批准的变更
      - alert: UnapprovedChangeDetected
        expr: governance_changes_unapproved_total > 0
        labels:
          severity: critical
          category: governance
          component: change-management
        annotations:
          summary: "检测到未批准的变更"
          description: |
            发现 {{ $value }} 个未批准的变更。
            变更ID: {{ $labels.change_id }}
            所有变更必须经过审批流程。
```

### 例外管理告警

```yaml
groups:
  - name: governance.exceptions
    interval: 5m
    rules:
      # 例外即将到期
      - alert: ExceptionExpiringSoon
        expr: |
          (governance_exception_expiry_timestamp - time()) < 7 * 24 * 3600
        labels:
          severity: warning
          category: governance
          component: exception-management
        annotations:
          summary: "例外即将到期"
          description: |
            例外 {{ $labels.exception_id }} 将在 7 天内到期。
            请审查是否需要续期或已完成补救。

      # 过期例外仍在使用
      - alert: ExpiredExceptionInUse
        expr: governance_exception_expired_active > 0
        labels:
          severity: critical
          category: governance
          component: exception-management
        annotations:
          summary: "过期例外仍在使用"
          description: |
            {{ $value }} 个过期例外仍然活跃。
            必须立即撤销或续期。

      # 高风险例外数量过多
      - alert: HighRiskExceptionCountHigh
        expr: count(governance_exception_risk_level{level="高"}) > 5
        for: 1d
        labels:
          severity: warning
          category: governance
          component: exception-management
        annotations:
          summary: "高风险例外数量过多"
          description: |
            当前有 {{ $value }} 个高风险例外。
            请审查并减少高风险例外。
```

## 审计流程

### 审计类型

| 类型 | 频率 | 范围 | 负责人 |
|------|------|------|--------|
| **日常监控** | 实时 | 所有指标 | 自动化系统 |
| **周度审查** | 每周 | 关键指标和告警 | 团队主管 |
| **月度审计** | 每月 | 所有治理模块 | 治理团队 |
| **季度深度审计** | 每季度 | 完整治理框架 | 治理委员会 |
| **年度审计** | 每年 | 战略对齐和改进 | 管理层 + 外部审计 |

### 月度审计流程

#### 1. 准备阶段（审计前 3 天）

```bash
# 生成审计数据
python tools/governance/python/generate_audit_data.py \
  --period 2025-01 \
  --output data/audit/2025-01-data.json

# 数据包含:
- 所有治理指标的月度统计
- 违规资源清单
- 变更请求记录
- 活跃例外列表
- 告警历史
```

#### 2. 执行阶段（审计日）

**审计清单**:

```yaml
命名治理审计:
  - [ ] 检查命名合规率是否达标 (> 95%)
  - [ ] 审查所有命名违规资源
  - [ ] 验证新资源是否遵循规范
  - [ ] 确认遗留系统迁移进展

变更管理审计:
  - [ ] 检查变更成功率 (> 95%)
  - [ ] 审查所有失败和回滚的变更
  - [ ] 确认所有变更都经过批准
  - [ ] 验证紧急变更比例 (< 5%)
  - [ ] 检查 CAB 审批时效

例外管理审计:
  - [ ] 审查所有活跃例外的合理性
  - [ ] 检查补救计划执行进度
  - [ ] 确认无过期例外仍在使用
  - [ ] 评估高风险例外的风险缓解

安全合规审计:
  - [ ] 验证数据分类标签完整性
  - [ ] 检查安全策略执行情况
  - [ ] 确认访问控制合规性

文档审计:
  - [ ] 验证治理文档是否最新
  - [ ] 检查 runbook 完整性
  - [ ] 确认培训材料更新
```

#### 3. 报告阶段（审计后 2 天）

使用标准模板生成审计报告：

```bash
# 生成审计报告
python tools/governance/python/generate_audit_report.py \
  --data data/audit/2025-01-data.json \
  --template templates/governance/forms/audit-report.template.yaml \
  --output reports/audit/AUD-2025-01.yaml
```

**审计报告结构**:

```yaml
apiVersion: governance.machinenativeops.io/v1alpha1
kind: AuditReport
metadata:
  id: "AUD-2025-01"
  title: "2025年1月治理审计报告"
  period:
    startDate: "2025-01-01"
    endDate: "2025-01-31"
  generatedAt: "2025-02-01T10:00:00Z"
  auditor: "governance-team"

spec:
  scope:
    modules:
      - naming-governance
      - change-management
      - exception-handling
    environments:
      - production
      - staging
    teams:
      - backend
      - frontend
      - platform

  complianceMetrics:
    namingCompliance:
      rate: 92.5
      total: 1250
      compliant: 1156
      nonCompliant: 94

    changeManagement:
      totalChanges: 87
      successRate: 96.5
      averageLeadTime: "4.2 days"

    exceptionManagement:
      activeExceptions: 15
      expiredExceptions: 0
      averageDuration: "65 days"

  findings:
    - id: "F-001"
      severity: "high"
      category: "policy-violation"
      description: |
        发现 12 个生产环境资源未遵循命名规范，
        主要集中在 payment-service 命名空间。
      evidence:
        - "prod/payment-service: 8 个不合规 Deployment"
        - "prod/payment-service: 4 个不合规 Service"
      impact: |
        影响自动化工具识别和监控配置，
        可能导致运维效率降低。
      recommendation: |
        创建变更请求进行重命名，
        或为遗留系统申请例外（含迁移计划）。
      owner: "backend-team"
      dueDate: "2025-02-28"
      status: "open"

    - id: "F-002"
      severity: "medium"
      category: "process-gap"
      description: |
        紧急变更比例为 7.8%，超过 5% 目标值。
      impact: |
        表明变更规划不足，可能增加系统风险。
      recommendation: |
        改进变更规划流程，
        提前识别和准备常见变更场景。
      owner: "sre-team"
      dueDate: "2025-03-15"
      status: "open"

  summary:
    overallAssessment: "good"

    keyTakeaways:
      - "命名合规率 92.5%，比上月提升 1.2%"
      - "变更成功率保持高水平 96.5%"
      - "例外管理良好，无过期例外"

    strengths:
      - "变更管理流程执行良好，成功率稳定"
      - "例外管理规范，及时审查和更新"
      - "监控和告警体系完善"

    improvements:
      - "提升命名合规率到 95% 以上"
      - "降低紧急变更比例"
      - "加强对 payment-service 的治理培训"

    trends: |
      过去三个月命名合规率稳步提升:
      - 2024-11: 90.1%
      - 2024-12: 91.3%
      - 2025-01: 92.5%

  actionPlan:
    - description: "修复 payment-service 命名违规"
      owner: "backend-team"
      priority: "P1"
      dueDate: "2025-02-28"
      relatedFindings: ["F-001"]

    - description: "改进变更规划流程"
      owner: "sre-team"
      priority: "P2"
      dueDate: "2025-03-15"
      relatedFindings: ["F-002"]

  previousAudit:
    id: "AUD-2024-12"
    improvementRate: 1.3
    resolvedFindings: 5
    newFindings: 2
```

#### 4. 跟踪阶段（持续）

```bash
# 跟踪行动项执行
python tools/governance/python/track_audit_actions.py \
  --audit-report reports/audit/AUD-2025-01.yaml \
  --output reports/audit/AUD-2025-01-tracking.yaml

# 每周更新进展
# 在下次审计中审查完成情况
```

## Grafana 仪表板

### 治理总览仪表板

**URL**: `http://grafana.example.com/d/governance-overview`

**面板**:

1. **治理健康分数** (Gauge)

   ```promql
   governance_health_score
   ```

2. **命名合规率趋势** (Graph)

   ```promql
   (
     sum(governance_naming_compliant_resources) /
     sum(governance_naming_total_resources)
   ) * 100
   ```

3. **变更成功率** (Graph)

   ```promql
   (
     sum(rate(governance_changes_successful_total[24h])) /
     sum(rate(governance_changes_total[24h]))
   ) * 100
   ```

4. **活跃例外** (Stat)

   ```promql
   sum(governance_exception_active_total) by (risk_level)
   ```

5. **告警分布** (Bar Chart)

   ```promql
   count(ALERTS{category="governance"}) by (severity)
   ```

6. **违规热点** (Table)
   - 按团队/命名空间分组的违规数
   - 最近 7 天新增违规
   - 待修复的高优先级问题

### 命名合规仪表板

**URL**: `http://grafana.example.com/d/governance-naming-compliance`

**面板**:

1. **合规率（按环境）**
2. **违规资源列表**
3. **违规趋势（7天）**
4. **按资源类型分类**
5. **遗留命名模式使用情况**

### 变更管理仪表板

**URL**: `http://grafana.example.com/d/governance-change-management`

**面板**:

1. **变更统计（按类型）**
2. **成功率趋势**
3. **平均交付时间**
4. **CAB 审批时效**
5. **回滚分析**

## 数据导出和集成

### Prometheus 集成

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'governance-metrics'
    static_configs:
      - targets: ['governance-exporter:8080']
    scrape_interval: 1m
```

### ELK Stack 集成

```bash
# 导出审计日志到 Elasticsearch
python tools/governance/python/export_audit_logs.py \
  --period 2025-01 \
  --elasticsearch-url http://elasticsearch:9200 \
  --index governance-audit-2025-01
```

### Slack 通知

```bash
# 每日摘要
./tools/governance/bash/send_daily_summary.sh \
  --channel "#governance" \
  --include-metrics \
  --include-alerts

# 告警通知
# 通过 Alertmanager 自动发送
```

## 工具和自动化

### 指标收集器

```bash
# 命名合规指标
python tools/governance/python/naming_metrics_exporter.py \
  --port 8080 \
  --interval 60

# 变更管理指标
python tools/governance/python/change_metrics_exporter.py \
  --port 8081 \
  --interval 60

# 例外管理指标
python tools/governance/python/exception_metrics_exporter.py \
  --port 8082 \
  --interval 60
```

### 审计报告生成器

```bash
# 月度审计报告
python tools/governance/python/generate_audit_report.py \
  --period 2025-01 \
  --output reports/audit/AUD-2025-01.yaml

# 季度审计报告
python tools/governance/python/generate_audit_report.py \
  --period 2025-Q1 \
  --type quarterly \
  --output reports/audit/AUD-2025-Q1.yaml
```

### CI/CD 集成

```yaml
# .github/workflows/governance-metrics.yml
name: Governance Metrics Collection
on:
  schedule:
    - cron: '0 0 * * *'  # 每天运行
jobs:
  collect-metrics:
    runs-on: ubuntu-latest
    steps:
      - name: Collect Naming Metrics
        run: |
          python tools/governance/python/collect_naming_metrics.py \
            --output metrics/naming-$(date +%Y-%m-%d).json

      - name: Push to Prometheus Pushgateway
        run: |
          cat metrics/naming-$(date +%Y-%m-%d).json | \
          curl --data-binary @- \
            http://pushgateway:9091/metrics/job/governance
```

## 最佳实践

### ✅ DO

1. **自动化优先**: 尽可能自动化指标收集和报告生成
2. **实时监控**: 使用 Prometheus + Grafana 实现实时可视化
3. **主动告警**: 配置告警规则，问题出现时立即发现
4. **定期审计**: 坚持月度审计，不要跳过
5. **数据驱动**: 基于指标数据做决策，而非主观判断
6. **趋势分析**: 关注指标趋势，而非单一数据点
7. **持续改进**: 根据审计发现持续优化流程

### ❌ DON'T

1. **手动收集**: 不要依赖手动统计，容易出错和遗漏
2. **忽视告警**: 告警触发后必须处理，不能长期忽略
3. **缺少基线**: 没有历史数据无法判断趋势
4. **过度优化**: 不要过分追求 100% 完美，关注关键指标
5. **数据孤岛**: 不同系统的指标应该整合到统一平台

## 参考资料

### 内部资源

- `schemas/metric-definition.schema.yaml` - 指标定义 Schema
- `schemas/audit-report.schema.yaml` - 审计报告 Schema
- `templates/governance/forms/audit-report.template.yaml` - 审计报告模板
- `templates/governance/k8s/prometheus-rule-naming-alert.template.yaml` - 告警规则
- `templates/governance/monitoring/grafana-dashboard-governance.json` - Grafana 仪表板

### 外部参考

- [Prometheus Best Practices](https://prometheus.io/docs/practices/naming/)
- [Google SRE Book - Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)
- [DORA Metrics](https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance)
- [ISO 19011 - Audit Guidelines](https://www.iso.org/standard/70017.html)

## FAQ

### Q: 指标收集会影响系统性能吗？

A: 指标收集设计为轻量级操作，对系统性能影响最小。使用 Prometheus 的 pull 模型，按需抓取指标。

### Q: 审计报告谁来审阅？

A: 月度审计报告由治理委员会审阅，团队主管和管理层收到副本。关键发现需要在下次会议讨论。

### Q: 如果指标达不到目标怎么办？

A: 首先分析根因，制定改进计划。如果目标不合理，可以通过治理委员会调整目标值。

### Q: 需要为每个指标都配置告警吗？

A: 不需要。只为关键指标和异常情况配置告警，避免告警疲劳。

## 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| v1.0.0 | 2025-01-15 | 初始版本，定义指标和审计流程 | Governance Team |

---

**下一步**: 阅读 [08-observability-validation.md](./08-observability-validation.md) 了解可观测性验证。
