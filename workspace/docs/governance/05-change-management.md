# 变更管理 (Change Management)

> **治理模块**: 变更管理 (Change Management)
> **版本**: v1.0.0
> **状态**: 已批准 (Approved)
> **最后更新**: 2025-01-15

## 概述

变更管理模块定义了组织中所有技术变更的标准化流程。通过结构化的变更管理，我们确保变更的可控性、可追溯性和成功率。

## 目标

- ✅ **降低风险**: 通过评估和审查减少变更失败
- 📋 **标准化流程**: 所有变更遵循一致的流程
- 🔍 **可追溯性**: 记录所有变更的完整历史
- 🤝 **跨团队协作**: 明确角色和责任
- 📊 **持续改进**: 通过指标和回顾不断优化

## 变更类型

### 1. 标准变更 (Standard Change)

**定义**: 预先批准的低风险、常规性变更，遵循标准操作程序。

**特征**:

- 风险低，影响可预测
- 已有详细的执行文档
- 不需要 CAB 审批（预先批准）
- 可以自动化执行

**示例**:

```yaml
- 应用配置更新（非功能性）
- SSL 证书续期
- 常规安全补丁
- 日志级别调整
- 资源配额增加（在限额内）
```

**流程**:

```
提交请求 → 自动验证 → 自动批准 → 实施 → 验证 → 关闭
```

**SLA**:

- 审批时间: 自动（< 5 分钟）
- 总完成时间: 1 个工作日

### 2. 常规变更 (Regular Change)

**定义**: 需要评估和审批的正常变更，通过 CAB (Change Advisory Board) 评审。

**特征**:

- 中等风险和影响
- 需要详细的实施和回滚计划
- 必须通过 CAB 审批
- 需要变更窗口

**示例**:

```yaml
- 应用版本升级
- 数据库 schema 变更
- 架构重构
- 新功能部署
- 第三方服务集成
```

**流程**:

```
提交请求 → 风险评估 → CAB 审查 → 批准 → 计划实施 → 执行 → 验证 → 审查 → 关闭
```

**SLA**:

- CAB 审查: 2-5 个工作日
- 总完成时间: 5-10 个工作日

### 3. 紧急变更 (Emergency Change)

**定义**: 必须立即执行以解决生产问题或安全漏洞的高优先级变更。

**特征**:

- 响应生产事故或严重安全问题
- 简化审批流程但不省略
- 事后补充完整文档
- 需要快速决策

**示例**:

```yaml
- 关键安全漏洞修复
- 生产系统故障修复
- 数据丢失恢复
- 紧急回滚
```

**流程**:

```
紧急请求 → 快速风险评估 → 紧急审批（简化的 CAB） → 立即执行 → 验证 → 事后审查 → 关闭
```

**SLA**:

- 紧急审批: < 2 小时
- 总完成时间: < 4 小时

## 变更请求结构

所有变更请求使用标准化的机器可读格式：

```yaml
apiVersion: governance.machinenativeops.io/v1alpha1
kind: ChangeRequest
metadata:
  # 唯一标识符 (CHG-YYYY-NNN)
  id: "CHG-2025-001"
  title: "升级 Payment Service 到 v2.0.0"
  createdAt: "2025-01-15T10:00:00Z"
  updatedAt: "2025-01-15T14:30:00Z"

spec:
  # 变更类型
  type: "常规变更"  # 标准变更 | 常规变更 | 紧急变更

  # 请求人
  requester:
    name: "张三"
    team: "Backend Team"
    email: "zhangsan@example.com"

  # 风险级别
  riskLevel: "中"  # 低 | 中 | 高

  # 影响评估
  impactAssessment:
    scope: ["production"]
    affectedSystems:
      - "payment-service"
      - "order-service"
    estimatedDowntime: "5 minutes"
    userImpact: "用户支付功能短暂不可用"
    rollbackComplexity: "低"

  # 批准记录
  approval:
    cab:
      required: true
      status: "approved"
      approvers:
        - name: "李四"
          role: "Technical Lead"
          approvedAt: "2025-01-16T09:00:00Z"
        - name: "王五"
          role: "Security Lead"
          approvedAt: "2025-01-16T09:15:00Z"

    business:
      required: false

  # 实施计划
  implementationPlan:
    plannedStart: "2025-01-20T02:00:00Z"
    plannedEnd: "2025-01-20T04:00:00Z"
    changeWindow: "production-maintenance"

    steps:
      - order: 1
        description: "备份当前配置和数据"
        duration: "10m"
        responsible: "SRE Team"

      - order: 2
        description: "在 staging 环境验证部署"
        duration: "20m"
        responsible: "Backend Team"

      - order: 3
        description: "部署到生产环境"
        duration: "15m"
        responsible: "Backend Team"

      - order: 4
        description: "运行健康检查和烟雾测试"
        duration: "10m"
        responsible: "QA Team"

      - order: 5
        description: "监控关键指标 30 分钟"
        duration: "30m"
        responsible: "SRE Team"

  # 回滚计划
  rollbackPlan:
    estimatedTime: "10m"

    triggers:
      - "错误率超过 1%"
      - "响应时间超过 2 秒"
      - "健康检查连续失败 3 次"

    steps:
      - order: 1
        description: "回滚到前一版本"
        command: "kubectl rollout undo deployment/prod-payment-deploy"

      - order: 2
        description: "恢复配置"
        command: "kubectl apply -f backup/payment-config.yaml"

      - order: 3
        description: "验证回滚成功"
        command: "kubectl get pods -l app=payment"

  # 测试计划
  testingPlan:
    - type: "单元测试"
      status: "passed"
      coverage: "85%"

    - type: "集成测试"
      status: "passed"
      environments: ["dev", "staging"]

    - type: "性能测试"
      status: "passed"
      benchmark: "响应时间 < 500ms, 吞吐量 > 1000 TPS"

  # 沟通计划
  communicationPlan:
    - audience: "Development Team"
      channel: "Slack #releases"
      timing: "24 小时前通知"

    - audience: "Customer Support"
      channel: "Email"
      timing: "12 小时前通知"

    - audience: "End Users"
      channel: "Status Page"
      timing: "1 小时前通知"

  # 执行记录
  execution:
    status: "completed"  # draft | scheduled | in-progress | completed | failed | rolled-back
    actualStart: "2025-01-20T02:05:00Z"
    actualEnd: "2025-01-20T03:45:00Z"

    notes: |
      变更按计划顺利完成。
      实际停机时间: 3 分钟（比预估少 2 分钟）
      所有健康检查通过，无需回滚。

  # 审查
  postImplementationReview:
    conductedAt: "2025-01-21T10:00:00Z"

    outcome: "成功"  # 成功 | 失败 | 部分成功

    successCriteria:
      - criterion: "零停机部署"
        met: false
        note: "有 3 分钟短暂停机，但在可接受范围内"

      - criterion: "性能指标正常"
        met: true
        note: "所有性能指标符合预期"

    lessonsLearned:
      - "下次应提前预热缓存以减少停机时间"
      - "回滚脚本执行良好，可以作为标准模板"

    improvementActions:
      - description: "创建自动化缓存预热脚本"
        owner: "SRE Team"
        dueDate: "2025-02-01"
```

## CAB (Change Advisory Board)

### CAB 组成

| 角色 | 职责 | 人员 |
|------|------|------|
| **主席** | 主持会议，最终决策 | CTO / Engineering Manager |
| **技术代表** | 技术可行性评估 | Tech Lead / Architect |
| **安全代表** | 安全风险评估 | Security Lead / CISO |
| **运维代表** | 运维影响评估 | SRE Lead / Ops Manager |
| **业务代表** | 业务影响评估 | Product Manager |
| **质量代表** | 质量风险评估 | QA Lead |

### CAB 会议

**频率**: 每周二和周四 10:00-11:00

**议程**:

1. 上周变更回顾 (10 分钟)
2. 审查新变更请求 (30 分钟)
3. 风险讨论和决策 (15 分钟)
4. 行动项跟踪 (5 分钟)

**决策标准**:

- ✅ **批准**: 风险可接受，计划完善
- ⏸️ **延期**: 需要更多信息或准备
- ❌ **拒绝**: 风险过高或不必要

### 紧急 CAB (Emergency CAB)

对于紧急变更，启动快速决策流程：

```bash
# Slack 通知所有 CAB 成员
/emergency-change "关键安全漏洞需要立即修复"

# 15 分钟内在线决策
# 2 个核心成员同意即可批准
```

## 风险评估

### 风险级别定义

| 级别 | 影响 | 概率 | 审批要求 | 变更窗口 |
|------|------|------|----------|----------|
| **低** | 单个服务，非生产 | 极低 | 团队主管 | 任何时间 |
| **中** | 多个服务，生产环境 | 中等 | CAB | 维护窗口 |
| **高** | 核心服务，全平台 | 较高 | CAB + 管理层 | 特殊维护窗口 |

### 风险矩阵

```
          影响
          低    中    高
概率 低    低    低    中
    中    低    中    高
    高    中    高    高
```

### 风险评估清单

```yaml
# 技术风险
- [ ] 是否在 staging 环境测试？
- [ ] 是否有完整的回滚计划？
- [ ] 是否有数据备份？
- [ ] 依赖服务是否准备就绪？

# 安全风险
- [ ] 是否通过安全审查？
- [ ] 是否涉及敏感数据？
- [ ] 是否符合合规要求？

# 业务风险
- [ ] 是否影响关键业务流程？
- [ ] 是否在业务高峰期？
- [ ] 用户影响范围多大？

# 运维风险
- [ ] 是否有足够的监控？
- [ ] 是否有值班人员？
- [ ] 是否准备好事故响应？
```

## 变更窗口

### 生产环境变更窗口

| 窗口类型 | 时间 | 适用变更 |
|----------|------|----------|
| **标准维护窗口** | 每周二、周四 02:00-04:00 UTC | 常规变更 |
| **紧急窗口** | 任何时间 | 紧急变更 |
| **黑色窗口** | 黑五、双十一等 | 禁止非紧急变更 |

### 变更冻结期

以下期间禁止常规变更：

- 重大促销活动前 3 天
- 重大发布后 2 天
- 法定节假日
- 已知高流量期

## 自动化工具

### 1. 变更请求提交

```bash
# 使用模板创建变更请求
cp templates/governance/forms/change-request.template.yaml changes/CHG-2025-001.yaml

# 编辑文件后提交
git add changes/CHG-2025-001.yaml
git commit -m "feat: 提交变更请求 CHG-2025-001"
git push origin change/CHG-2025-001
```

### 2. 自动验证

CI 流程自动验证变更请求：

```yaml
# .github/workflows/change-request-validation.yml
- name: Validate Change Request
  run: |
    python tools/governance/python/validate_change_request.py \
      --file changes/CHG-2025-001.yaml \
      --schema schemas/change-request.schema.yaml
```

### 3. CAB 决策记录

```yaml
# 在变更请求中记录 CAB 决策
spec:
  approval:
    cab:
      status: "approved"
      approvers:
        - name: "张三"
          role: "Technical Lead"
          approvedAt: "2025-01-16T09:00:00Z"
          comment: "技术方案合理，批准实施"
```

### 4. 自动化通知

```bash
# Slack 通知
./tools/governance/bash/notify_change.sh \
  --change-id CHG-2025-001 \
  --status approved \
  --channel "#releases"

# Email 通知
./tools/governance/bash/send_change_notification.sh \
  --change-id CHG-2025-001 \
  --template approval \
  --recipients team@example.com
```

## 指标与 KPI

### 关键指标

| 指标 | 定义 | 目标 |
|------|------|------|
| **变更成功率** | 成功变更 / 总变更 | > 95% |
| **平均交付时间** | 从提交到完成的平均时间 | < 5 个工作日 |
| **回滚率** | 需要回滚的变更比例 | < 5% |
| **紧急变更比例** | 紧急变更 / 总变更 | < 5% |
| **未批准变更数** | 发现的未经批准的变更 | 0 |

### Prometheus 指标

```promql
# 变更成功率
(sum(rate(governance_changes_successful_total[24h])) /
 sum(rate(governance_changes_total[24h]))) * 100

# 紧急变更比例
(sum(rate(governance_changes_total{type="紧急变更"}[7d])) /
 sum(rate(governance_changes_total[7d]))) * 100
```

### 告警规则

```yaml
# 变更成功率低
- alert: ChangeSuccessRateLow
  expr: |
    (sum(rate(governance_changes_successful_total[24h])) /
     sum(rate(governance_changes_total[24h]))) * 100 < 95
  for: 1h
  labels:
    severity: warning

# 未批准的变更
- alert: UnapprovedChangeDetected
  expr: governance_changes_unapproved_total > 0
  labels:
    severity: critical
```

## 审计与合规

### 变更日志

所有变更必须记录在版本控制系统中：

```bash
# 查看所有变更历史
git log --grep="CHG-" --oneline

# 查看特定变更
git show $(git log --grep="CHG-2025-001" --format="%H" -n 1)
```

### 月度审计

每月生成变更管理审计报告：

```bash
python tools/governance/python/generate_change_audit.py \
  --period 2025-01 \
  --output reports/audit/AUD-2025-01-changes.yaml
```

审计报告包含：

- 总变更数和成功率
- 按类型、风险级别分类统计
- 回滚分析
- 趋势对比
- 改进建议

## 培训与入职

### 新团队成员培训

1. **理论学习** (1 小时):
   - 阅读本文档
   - 理解变更类型和流程
   - 学习风险评估方法

2. **实践操作** (2 小时):
   - 创建标准变更请求
   - 参与 CAB 会议观摩
   - 模拟回滚演练

3. **认证**:
   - 独立完成一次变更请求
   - 通过知识测试

### 定期培训

- **频率**: 每季度
- **内容**: 流程更新、案例分析、工具培训
- **形式**: 在线培训 + 实操演练

## 最佳实践

### ✅ DO

1. **详细文档化**: 每个变更都要有完整的计划和回滚方案
2. **充分测试**: 在低环境充分验证后再到生产
3. **小步快跑**: 将大变更拆分为小的增量变更
4. **监控就绪**: 确保有足够的监控和告警
5. **清晰沟通**: 提前通知所有相关方
6. **事后审查**: 每次变更后都要回顾和总结

### ❌ DON'T

1. **跳过审批**: 即使紧急也要走简化流程
2. **生产实验**: 不要在生产环境尝试未测试的变更
3. **高峰期变更**: 避免在业务高峰期执行变更
4. **缺少回滚**: 必须有明确的回滚方案
5. **单打独斗**: 关键变更必须有多人参与
6. **忽略监控**: 变更后必须持续监控

## 案例分析

### 成功案例：数据库迁移

```yaml
变更: CHG-2024-156
描述: 从 PostgreSQL 11 升级到 15
结果: 成功

关键成功因素:
  - 在 staging 环境完整演练 3 次
  - 详细的 100 步实施计划
  - 5 分钟快速回滚方案
  - 24 小时监控周期
  - 跨团队协作（DB + SRE + Dev）
```

### 失败案例：配置错误

```yaml
变更: CHG-2024-089
描述: 更新 Nginx 配置
结果: 回滚

失败原因:
  - 配置未在 staging 测试
  - 语法错误导致服务启动失败
  - 监控告警延迟

改进措施:
  - 添加 Nginx 配置 lint 检查
  - staging 环境强制验证
  - 加强实时监控
```

## 工具和模板

### 变更请求模板

- `templates/governance/forms/change-request.template.yaml`

### 验证工具

- `tools/governance/python/validate_change_request.py`
- `tools/governance/bash/check_change_compliance.sh`

### CI/CD 集成

- `templates/governance/ci/github-actions-change-check.yml`
- `templates/governance/ci/gitlab-ci-change-check.yml`

### 示例

- `src/governance/dimensions/03-change/examples/CHG-2025-001.yaml` - 常规变更示例
- `src/governance/dimensions/03-change/examples/rollback-scenario.md` - 回滚场景

## 参考资料

### 外部标准

- [ITIL Change Management](https://www.axelos.com/certifications/itil-service-management/itil-4-foundation)
- [Google SRE Book - Managing Releases](https://sre.google/sre-book/release-engineering/)
- [DevOps Change Management Best Practices](https://www.atlassian.com/devops/devops-tools/change-management)

### 内部资源

- `schemas/change-request.schema.yaml` - 变更请求 Schema
- `policies/change-management/change-policy.yaml` - 变更管理策略
- `references/references.yaml` - 完整参考资料列表

## FAQ

### Q: 所有代码提交都需要变更请求吗？

A: 不需要。日常开发的代码提交通过 PR 流程管理。变更请求用于影响生产环境的部署和配置变更。

### Q: 如果紧急情况等不及 CAB 审批怎么办？

A: 启动紧急 CAB 流程，通过 Slack 快速联系核心成员，15 分钟内做出决策。

### Q: 变更失败必须回滚吗？

A: 不一定。如果可以快速向前修复（< 5 分钟），优先考虑 forward fix。否则立即回滚。

### Q: 如何处理第三方服务的变更？

A: 第三方变更也需要走变更流程，评估影响并准备应急预案。

## 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| v1.0.0 | 2025-01-15 | 初始版本，定义变更管理流程 | Governance Team |

---

**下一步**: 阅读 [07-exception-handling.md](./07-exception-handling.md) 了解如何处理治理例外。
