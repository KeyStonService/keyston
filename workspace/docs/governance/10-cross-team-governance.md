# 跨团队治理 (Cross-Team Governance)

> **治理模块**: 跨团队协作与治理 (Cross-Team Collaboration and Governance)
> **版本**: v1.0.0
> **状态**: 已批准 (Approved)
> **最后更新**: 2025-01-15

## 概述

跨团队治理模块定义了多个团队之间如何协调治理实践、共享知识和解决冲突。在大型组织中，有效的跨团队治理对于保持一致性和促进协作至关重要。

## 目标

- 🤝 **统一标准**: 跨团队的一致性治理标准
- 🔄 **知识共享**: 最佳实践和经验交流
- ⚖️ **冲突解决**: 明确的冲突解决机制
- 📊 **透明度**: 跨团队的可见性和问责
- 🚀 **规模化**: 治理实践能够随组织扩展

## 组织结构

### 治理委员会 (Governance Board)

**职责**:

- 制定和维护治理策略
- 审批高风险例外
- 解决跨团队冲突
- 推动治理文化
- 定期审查治理有效性

**组成**:

| 角色 | 职责 | 人数 |
|------|------|------|
| **主席** | 主持会议，最终决策 | 1 (CTO/VP Engineering) |
| **技术代表** | 技术标准和架构 | 2-3 (Tech Leads/Architects) |
| **安全代表** | 安全和合规 | 1 (CISO/Security Lead) |
| **运维代表** | 运维和可靠性 | 1-2 (SRE Lead) |
| **产品代表** | 业务需求和优先级 | 1-2 (Product Managers) |
| **质量代表** | 质量和测试 | 1 (QA Lead) |

**会议频率**:

- 常规会议: 每月一次（2 小时）
- 紧急会议: 按需召开
- 季度回顾: 每季度一次（半天）

**会议议程**:

```yaml
月度会议议程:
  1. 上月回顾 (15分钟):
     - 关键指标回顾
     - 重要事件总结

  2. 例外审批 (45分钟):
     - 审查新的例外请求
     - 审查即将到期的例外
     - 决策批准/拒绝/延期

  3. 策略讨论 (30分钟):
     - 现有策略的问题和反馈
     - 新策略提案讨论
     - 跨团队标准协调

  4. 审计和合规 (20分钟):
     - 审计发现审查
     - 合规状态更新
     - 改进行动跟踪

  5. 其他议题 (10分钟):
     - 开放讨论
     - 下次会议准备
```

### 治理工作组 (Governance Working Groups)

**专项工作组**:

```yaml
命名标准工作组:
  职责:
    - 维护命名标准文档
    - 评估命名相关的例外
    - 开发和维护验证工具
    - 处理命名相关的咨询

  成员:
    - 各团队代表（1-2人/团队）
    - 治理团队成员
    - SRE 代表

  会议: 每月一次

变更管理工作组:
  职责:
    - 优化变更流程
    - 组织 CAB 会议
    - 分析变更趋势
    - 改进变更工具

  成员:
    - Team Leads
    - SRE 代表
    - 产品经理

  会议: 每两周一次

安全合规工作组:
  职责:
    - 维护安全标准
    - 审查安全扫描结果
    - 协调合规审计
    - 安全培训和意识

  成员:
    - 安全团队
    - 合规专员
    - 各团队安全联络人

  会议: 每月一次
```

### 团队角色

**团队治理联络人 (Team Governance Liaison)**:

```yaml
职责:
  - 作为团队和治理委员会的桥梁
  - 参与治理工作组
  - 在团队内推广治理实践
  - 收集团队反馈和建议
  - 协助团队解决治理问题

资格:
  - 对治理框架有深入理解
  - 在团队中有一定影响力
  - 良好的沟通能力
  - 持有专业级以上认证

时间投入:
  - 约 20% 的工作时间
```

## 跨团队协作模式

### 1. 共享服务模式

**场景**: 多个团队使用同一个共享服务

```yaml
示例: 共享的认证服务

所有权:
  - 主要所有者: Auth Team
  - 贡献者: 所有使用团队
  - 治理责任: Auth Team

协作机制:
  1. Auth Team 维护服务和治理标准
  2. 使用团队通过 PR 贡献改进
  3. Auth Team 审查并合并 PR
  4. 变更通过标准 CAB 流程
  5. SLO 由 Auth Team 负责

治理要求:
  - Auth Team 确保服务符合所有治理标准
  - 使用团队遵循 Auth Team 的贡献指南
  - 所有变更通过 Auth Team 审查
  - 定期跨团队回顾会议
```

### 2. 平台团队模式

**场景**: 平台团队为产品团队提供基础设施和工具

```yaml
示例: Kubernetes 平台团队

角色划分:
  平台团队:
    - 提供标准化的 K8s 集群
    - 提供治理工具和模板
    - 定义平台级别的策略
    - 提供技术支持和培训

  产品团队:
    - 在平台上部署应用
    - 遵循平台定义的标准
    - 反馈平台问题和需求
    - 参与平台改进

治理协调:
  - 平台团队定义"护栏"策略
  - 产品团队在护栏内自主决策
  - 平台团队提供自动化验证
  - 定期的平台用户组会议
```

### 3. 功能团队模式

**场景**: 独立的功能团队拥有端到端服务

```yaml
示例: Payment Team, User Team, Order Team

自主性:
  - 每个团队完全拥有自己的服务
  - 独立的技术栈选择（在治理范围内）
  - 独立的发布节奏

治理协调:
  - 所有团队遵循统一的治理标准
  - 跨团队依赖通过 API 契约管理
  - 共享治理最佳实践
  - 定期的 Tech Leads 同步会议

边界和接口:
  - API 契约测试
  - 服务级别协议（SLA）
  - 监控和告警标准
  - 文档要求
```

## 跨团队标准

### API 契约管理

**OpenAPI/Swagger 规范**:

```yaml
# API 契约要求
requirements:
  - [ ] 所有 API 必须有 OpenAPI 规范
  - [ ] 规范版本化（与 API 版本对应）
  - [ ] 包含完整的请求/响应示例
  - [ ] 包含错误响应定义
  - [ ] 契约测试覆盖

# 示例: payment-api-contract.yaml
openapi: 3.0.0
info:
  title: Payment API
  version: v1.3.0
  description: 支付处理 API
  contact:
    name: Payment Team
    email: payment-team@example.com

servers:
  - url: https://api.example.com/v1
    description: Production

paths:
  /payments:
    post:
      summary: 创建支付
      operationId: createPayment
      tags:
        - payments
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PaymentRequest'
      responses:
        '201':
          description: 支付创建成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaymentResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '500':
          $ref: '#/components/responses/InternalError'

components:
  schemas:
    PaymentRequest:
      type: object
      required:
        - amount
        - currency
        - method
      properties:
        amount:
          type: number
          format: double
          minimum: 0.01
        currency:
          type: string
          enum: [USD, EUR, CNY]
        method:
          type: string
          enum: [credit_card, debit_card, paypal]
```

**契约测试**:

```yaml
# CI/CD 中验证 API 契约
- name: Contract Testing
  run: |
    # Provider 端测试
    pact-verifier verify \
      --provider payment-api \
      --pact-url ./contracts/payment-api.json

    # Consumer 端测试
    pact-stub-server \
      --file ./contracts/payment-api.json \
      --port 8080
```

### 服务级别协议 (SLA)

**跨团队 SLA 定义**:

```yaml
# Payment API SLA
sla:
  service: payment-api
  provider: Payment Team
  consumers:
    - Order Team
    - Subscription Team

  commitments:
    availability:
      target: 99.9%
      measurement: "成功请求比例（非 5xx）"
      window: "30 天滚动窗口"

    latency:
      p95: 500ms
      p99: 1000ms
      measurement: "端到端请求延迟"

    throughput:
      minimum: 1000 TPS
      peak: 5000 TPS

  support:
    response_time:
      p0: "15 分钟"  # 服务完全中断
      p1: "1 小时"    # 严重性能降级
      p2: "4 小时"    # 部分功能不可用
      p3: "1 天"      # 其他问题

    escalation:
      - level_1: "Team on-call"
      - level_2: "Team Lead"
      - level_3: "Engineering Manager"

  monitoring:
    dashboard: "https://grafana.example.com/d/payment-api"
    alerts: "#payment-alerts"
    status_page: "https://status.example.com"
```

### 依赖管理

**依赖注册表**:

```yaml
# dependencies.yaml - 跨团队依赖映射
dependencies:
  - service: order-service
    team: Order Team
    dependencies:
      - service: payment-api
        team: Payment Team
        type: synchronous
        sla_ref: "payment-api-sla.yaml"
        criticality: high
        fallback: "队列异步处理"

      - service: inventory-api
        team: Inventory Team
        type: synchronous
        sla_ref: "inventory-api-sla.yaml"
        criticality: high
        fallback: "无，订单失败"

      - service: notification-service
        team: Platform Team
        type: asynchronous
        criticality: low
        fallback: "稍后重试"
```

**依赖可视化**:

```bash
# 生成依赖图
python tools/governance/python/generate_dependency_graph.py \
  --input dependencies.yaml \
  --output dependency-graph.svg

# 检测循环依赖
python tools/governance/python/detect_circular_dependencies.py \
  --input dependencies.yaml
```

## 知识共享机制

### 1. 治理知识库

```yaml
知识库结构:
  docs/governance/:
    - 官方文档（本系列文档）

  wiki/governance/:
    - FAQ
    - 最佳实践
    - 案例研究
    - Troubleshooting 指南
    - 团队特定的指南

  src/governance/dimensions/:
    - 代码示例
    - 配置模板
    - 脚本和工具
```

### 2. 社区活动

```yaml
月度治理分享会:
  时间: 每月最后一个周五下午
  时长: 1 小时
  形式: 技术分享 + Q&A
  主题示例:
    - "Payment Team 的命名治理实践"
    - "如何处理遗留系统的治理迁移"
    - "自动化验证工具深度解析"

季度治理峰会:
  时间: 每季度一次
  时长: 半天
  形式: 主题演讲 + 工作坊
  内容:
    - 治理框架更新
    - 成功案例分享
    - 跨团队协作讨论
    - 未来规划

Slack 社区:
  #governance: 通用治理讨论
  #governance-help: 问题咨询
  #governance-announcements: 重要公告
  #governance-wg-*: 各工作组频道
```

### 3. 内部博客

```yaml
治理博客:
  平台: 内部技术博客
  频率: 每月至少 1 篇
  内容类型:
    - 新功能介绍
    - 最佳实践分享
    - 案例分析
    - 工具使用指南
  作者: 治理团队 + 团队贡献
```

## 冲突解决

### 冲突类型

#### 1. 标准冲突

**场景**: 不同团队对标准的理解或需求不同

```yaml
示例:
  问题: Frontend Team 认为命名标准太长，影响 URL 可读性

解决流程:
  1. Frontend Team 向治理委员会提出问题
  2. 治理委员会组织相关方讨论
  3. 评估影响和替代方案:
     - 选项 A: 为 Frontend 创建例外
     - 选项 B: 调整标准以适应 Frontend 需求
     - 选项 C: 使用别名/短链接解决
  4. 治理委员会做出决策
  5. 更新文档和通知所有团队

决策原则:
  - 整体利益优先于局部利益
  - 寻求双赢解决方案
  - 必要时进行权衡取舍
  - 决策透明化和文档化
```

#### 2. 优先级冲突

**场景**: 治理要求与业务交付时间冲突

```yaml
示例:
  问题: 产品发布期限紧张，没有时间完成所有治理要求

解决流程:
  1. 团队提出例外请求，说明业务紧迫性
  2. 评估哪些要求可以延后，哪些必须满足
  3. 制定分阶段计划:
     - 发布前: 必须满足的最小安全和合规要求
     - 发布后 2 周: 补充完整的文档和测试
     - 发布后 1 月: 全面符合所有治理要求
  4. 批准例外并严格跟踪补救进度

决策原则:
  - 安全和合规不能妥协
  - 可以阶段性满足其他要求
  - 必须有明确的补救计划和时间表
  - 不能成为常态
```

#### 3. 资源冲突

**场景**: 多个团队竞争有限的资源（如 CAB 时间、治理团队支持）

```yaml
示例:
  问题: CAB 会议时间有限，无法审查所有变更请求

解决流程:
  1. 建立优先级标准:
     - P0: 紧急安全修复
     - P1: 生产问题修复
     - P2: 重要功能上线
     - P3: 优化和改进
  2. 根据优先级分配 CAB 时间
  3. 低优先级请求可能延后到下次 CAB
  4. 必要时召开额外的 CAB 会议

长期解决:
  - 增加 CAB 会议频率
  - 扩大 CAB 规模
  - 自动批准更多标准变更
```

### 升级路径

```yaml
冲突升级流程:
  Level 1 - 团队级别:
    - 团队内部讨论
    - 团队治理联络人协调
    - 时限: 2 个工作日

  Level 2 - 工作组级别:
    - 提交到相关治理工作组
    - 工作组讨论和建议
    - 时限: 1 周

  Level 3 - 治理委员会:
    - 治理委员会审议
    - 做出正式决策
    - 时限: 2 周

  Level 4 - 管理层:
    - 提交到高级管理层
    - 战略级决策
    - 时限: 按需
```

## 跨团队指标

### 协作健康指标

```yaml
跨团队协作指标:
  - 跨团队变更请求数量
  - 跨团队例外请求数量
  - 跨团队冲突数量和解决时间
  - 依赖服务的 SLA 遵守率
  - 知识共享活动参与度

团队治理成熟度:
  - 各团队的命名合规率
  - 各团队的变更成功率
  - 各团队的审计通过率
  - 培训完成率
```

### 可视化

```yaml
# Grafana 跨团队仪表板
panels:
  - 各团队治理健康分数对比
  - 跨团队依赖可用性矩阵
  - 治理指标趋势（按团队）
  - 跨团队协作活动统计
```

## 最佳实践

### ✅ DO

1. **建立清晰的所有权**: 每个服务和标准都有明确的所有者
2. **定期同步**: 通过会议和异步沟通保持对齐
3. **文档化决策**: 所有重要决策都要记录和分享
4. **包容性**: 让所有相关团队参与决策
5. **透明度**: 决策过程和结果公开透明
6. **灵活性**: 在标准化和团队自主性间平衡
7. **庆祝成功**: 表彰优秀的治理实践

### ❌ DON'T

1. **自上而下强推**: 不考虑团队实际情况
2. **一刀切**: 忽视团队的特殊需求
3. **信息孤岛**: 决策和信息不共享
4. **忽视反馈**: 不听取团队的意见
5. **过度集中**: 所有决策都要治理委员会批准
6. **缺少跟进**: 决策后不跟踪执行

## 工具和资源

### 协作工具

- Confluence/Notion - 知识库
- Slack - 实时沟通
- Jira - 问题跟踪
- GitHub - 代码和文档协作
- Miro - 协作白板

### 模板

- `templates/governance/forms/cross-team-sla.template.yaml` - SLA 模板
- `templates/governance/forms/dependency-registry.template.yaml` - 依赖注册模板

## 参考资料

### 团队拓扑

- [Team Topologies](https://teamtopologies.com/) - 团队组织模式
- [Spotify Model](https://blog.crisp.se/wp-content/uploads/2012/11/SpotifyScaling.pdf) - Squads, Tribes, Chapters, Guilds

### 跨团队协作

- [The Phoenix Project](https://itrevolution.com/the-phoenix-project/) - DevOps 协作
- [Google's SRE Book - Collaboration](https://sre.google/workbook/organizing-sre/)

## FAQ

### Q: 如何处理团队自主性和标准化的矛盾？

A: 采用"护栏"而非"检查点"的思路。定义必须遵守的边界，边界内团队自主决策。

### Q: 新团队如何快速融入治理框架？

A:

1. 指定一位经验丰富的治理联络人
2. 提供 onboarding 清单和培训
3. 安排 buddy 团队提供帮助
4. 初期提供更多支持和宽容

### Q: 如何避免治理委员会成为瓶颈？

A:

1. 授权团队和工作组处理常见问题
2. 自动批准标准化场景
3. 明确升级标准，不是所有事都需要委员会
4. 增加会议频率或委员会规模

### Q: 跨地域团队如何协调？

A:

1. 使用异步沟通（文档、论坛）
2. 轮换会议时间照顾不同时区
3. 录制会议供缺席者观看
4. 强化文档化，减少口头沟通依赖

## 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| v1.0.0 | 2025-01-15 | 初始版本，定义跨团队治理机制 | Governance Team |

---

**完成**: 这是治理框架核心文档的最后一个模块。建议接下来查看 [README.md](./README.md) 开始学习之旅。
