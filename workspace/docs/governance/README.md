# 治理框架文档

## 概述

本目录包含 MachineNativeOps 治理框架的完整文档，涵盖组织采用生命周期、命名规范、变更管理、例外处理等核心模块。

## 📚 文档结构

本治理框架包含以下核心文档：

### 1. [组织采用生命周期](./02-org-adoption-lifecycle.md)

- 意识阶段 (Awareness)
- 试点阶段 (Pilot)
- 推广阶段 (Rollout)
- 成熟阶段 (Maturity)

### 2. [角色化培训与学习](./03-role-based-training.md)

- 开发人员学习路径
- 运维人员学习路径
- 架构师学习路径
- 管理层培训

### 3. [命名治理标准](./04-naming-standards.md)

- Kubernetes 资源命名
- API 端点命名
- CI/CD Pipeline 命名
- 命名验证工具

### 4. [变更管理流程](./05-change-management.md)

- 变更类型定义
- 风险评估
- 审批流程
- 实施和回滚

### 5. [指标与审计](./06-metrics-and-audit.md)

- KPI 定义
- 合规指标
- 审计报告
- 持续改进

### 7. [例外处理机制](./07-exception-handling.md)

- 例外类型
- 审批流程
- 监控和复审
- 补救计划

### 8. [可观测性与验证](./08-observability-validation.md)

- Prometheus 规则
- Grafana 仪表板
- 告警配置
- 验证流程

### 9. [安全与合规](./09-security-compliance.md)

- 信息安全策略集成
- 数据分类
- 合规性映射
- 审计要求

### 10. [跨团队治理协作](./10-cross-team-governance.md)

- 治理委员会
- 决策机制
- 沟通协作
- 冲突解决

## 🚀 快速开始

### 对于开发者

1. 阅读 [命名治理标准](./04-naming-standards.md)
2. 使用 [命名生成工具](../../tools/bash/generate_resource_name.sh)
3. 在 CI/CD 中集成 [命名验证](../../templates/ci/github-actions-naming-check.yml)
4. 查看 [良好vs不良命名示例](../../src/governance/dimensions/27-templates/examples/good-vs-bad-naming.yaml)

### 对于运维人员

1. 阅读 [变更管理流程](./05-change-management.md)
2. 使用 [变更请求模板](../../templates/forms/change-request.template.yaml)
3. 配置 [Prometheus 告警](../../templates/k8s/prometheus-rule-naming-alert.template.yaml)
4. 查看 [变更请求示例](../../src/governance/dimensions/03-change/examples/CHG-2025-001.yaml)

### 对于架构师

1. 阅读 [组织采用生命周期](./02-org-adoption-lifecycle.md)
2. 阅读 [跨团队治理协作](./10-cross-team-governance.md)
3. 审查 [治理总纲](../../governance-manifest.yaml)
4. 制定团队采用计划

### 对于管理层

1. 阅读 [指标与审计](./06-metrics-and-audit.md)
2. 审查 [合规性映射](./09-security-compliance.md)
3. 了解 [例外处理机制](./07-exception-handling.md)
4. 参与治理委员会决策

## 🔧 实践指南

### 命名规范实践

```bash
# 生成标准化资源名称
./tools/bash/generate_resource_name.sh \
  --environment prod \
  --app payment \
  --resource-type deploy \
  --version v1.0.0

# 输出: prod-payment-deploy-v1.0.0
```

### CI/CD 集成

```yaml
# .github/workflows/naming-check.yml
- name: Validate Naming
  uses: ./.github/actions/naming-validation
  with:
    policies: governance-framework/policies/naming/
    schemas: governance-framework/schemas/
```

### 变更管理实践

```bash
# 1. 复制变更请求模板
cp templates/forms/change-request.template.yaml CHG-2025-XXX.yaml

# 2. 填写变更详情
vim CHG-2025-XXX.yaml

# 3. 提交审批
git add CHG-2025-XXX.yaml
git commit -m "chore: add change request CHG-2025-XXX"
```

## 📊 治理指标

关键绩效指标：

- **命名合规率**: > 95%
- **变更成功率**: > 98%
- **平均变更交付时间**: < 3 天
- **紧急变更比例**: < 5%
- **例外数量**: 最小化

## 🛠️ 工具与自动化

### 命名验证工具

- **Bash 脚本**: `tools/bash/generate_resource_name.sh`
- **Python 验证器**: `tools/python/validate_naming.py`
- **GitHub Actions**: `templates/ci/github-actions-naming-check.yml`
- **GitLab CI**: `templates/ci/gitlab-ci-naming-check.yml`

### Kubernetes 集成

- **Deployment 模板**: `templates/k8s/deployment.template.yaml`
- **Prometheus 规则**: `templates/k8s/prometheus-rule-naming-alert.template.yaml`
- **Admission Controller**: 使用 OPA Gatekeeper

## 📖 参考资料

完整的外部参考资料索引请查看 [references.yaml](../../references/references.yaml)

关键参考：

- [Kubernetes 命名约定](https://kubernetes.io/docs/concepts/overview/working-with-objects/names/)
- [语义化版本](https://semver.org/)
- [RESTful API 设计](https://restfulapi.net/)
- [ITIL 变更管理](https://www.axelos.com/certifications/itil-service-management)
- [Google SRE Book](https://sre.google/sre-book/)

## 🤝 贡献指南

欢迎贡献改进建议！

1. Fork 本仓库
2. 创建特性分支
3. 提交改进
4. 创建 Pull Request

贡献类型：

- 文档改进
- 工具增强
- 新的策略模板
- 示例和最佳实践

## 📞 支持与联系

- **文档**: <https://machinenativeops.github.io/docs>
- **Issues**: <https://github.com/MachineNativeOps/MachineNativeOps/issues>
- **Discussions**: <https://github.com/MachineNativeOps/MachineNativeOps/discussions>
- **Email**: <governance@machinenativeops.io>

## 📝 许可证

本治理框架采用 MIT 许可证。详见 [LICENSE](../../LICENSE)。

---

**开始您的治理之旅！** 🎯
