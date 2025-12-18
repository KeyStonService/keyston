# 治理框架整合说明

## 概述

治理框架已成功整合到现有的 MachineNativeOps 仓库中，作为一个**治理层 (Governance Layer)** 与现有的产品/平台代码和平共存。

## 整合原则

1. **非侵入性**: 不修改现有的产品代码和目录结构
2. **分层清晰**: 治理层组件明确标注和组织
3. **易于发现**: 通过 `governance-manifest.yaml` 作为入口点
4. **即插即用**: CI/CD 模板和工具可直接使用

## 新增的治理层组件

### 根目录新增

- `governance-manifest.yaml` - 治理总纲和机器可读入口
- `schemas/` - 机器可验证的 JSON/YAML schemas
- `policies/` - 标准化的治理策略
- `references/` - 外部参考资料索引
- `GOVERNANCE_FRAMEWORK.md` - 完整框架文档

### 现有目录中的治理子目录

- `docs/governance/` - 治理文档
- `templates/governance/` - 治理专用模板（表单、CI、K8s）
- `tools/governance/` - 治理专用工具（命名生成器、验证器）
- `examples/governance/` - 治理案例示例

## 与现有结构的关系

### 保留不变

以下现有目录**完全保持不变**：

- `agent/`, `ai/`, `apps/`, `automation/`, `autonomous/`
- `bridges/`, `client/`, `config/`, `contracts/`, `core/`
- `deploy/`, `deployment/`, `infra/`, `infrastructure/`
- `ops/`, `services/`, `server/`, `runtime/`
- `governance/` (原有的 23 维度治理矩阵)
- 等等...

这些是被治理的对象，不是治理框架本身。

### 治理与被治理的关系

```
治理层 (Governance Layer)
├── schemas/ + policies/          定义规则
├── templates/governance/         提供模板
├── tools/governance/             提供工具
└── examples/governance/          提供示例

         ↓ 应用于 ↓

被治理对象 (Governed Objects)
├── deploy/k8s/                   K8s manifests 遵循命名规范
├── infrastructure/               IaC 代码遵循命名规范
├── services/                     服务名称遵循命名规范
└── ... (所有产品/平台代码)
```

## 使用方式

### 1. 查看治理总纲

```bash
cat governance-manifest.yaml
```

### 2. 生成符合规范的资源名称

```bash
./tools/governance/bash/generate_resource_name.sh \
  -e prod -a payment -r deploy -v v1.0.0
```

### 3. 验证现有资源的命名

```bash
python tools/governance/python/validate_naming.py \
  --files deploy/k8s/production/*.yaml \
  --policies policies/naming/ \
  --schemas schemas/
```

### 4. 在 CI/CD 中集成

```yaml
# .github/workflows/naming-check.yml
- uses: actions/checkout@v4
  with:
    repository: MachineNativeOps/MachineNativeOps
    path: governance

- name: Validate Naming
  run: |
    python governance/tools/governance/python/validate_naming.py \
      --changed-files-only \
      --policies governance/policies/naming/ \
      --schemas governance/schemas/
```

### 5. 提交变更请求

```bash
cp templates/governance/forms/change-request.template.yaml CHG-2025-XXX.yaml
# 填写变更详情
vim CHG-2025-XXX.yaml
git add CHG-2025-XXX.yaml
git commit -m "chore: add change request CHG-2025-XXX"
```

## 关键文件位置速查

| 类型 | 位置 | 说明 |
|------|------|------|
| **入口** | `governance-manifest.yaml` | 治理总纲，机器可读 |
| **文档** | `GOVERNANCE_FRAMEWORK.md` | 完整框架说明 |
| **Schema** | `schemas/*.schema.yaml` | 验证规则定义 |
| **策略** | `policies/naming/*.yaml` | 命名规范策略 |
| **模板** | `templates/governance/forms/*.yaml` | 表单模板 |
| **CI模板** | `templates/governance/ci/*.yml` | CI/CD 集成模板 |
| **工具** | `tools/governance/bash/*.sh` | Bash 工具 |
| **工具** | `tools/governance/python/*.py` | Python 工具 |
| **示例** | `examples/governance/naming/*.yaml` | 命名示例 |
| **示例** | `examples/governance/change-management/*.yaml` | 变更示例 |
| **文档** | `docs/governance/*.md` | 详细文档 |
| **参考** | `references/references.yaml` | 外部参考资料 |

## 后续步骤

1. **团队培训**: 使用 `docs/governance/03-role-based-training.md`
2. **CI集成**: 参考 `templates/governance/ci/` 下的模板
3. **策略定制**: 根据组织需求调整 `policies/` 下的策略
4. **工具使用**: 开始使用 `tools/governance/` 下的工具
5. **监控设置**: 应用 `templates/governance/k8s/prometheus-rule-naming-alert.template.yaml`

## 相关链接

- [完整框架文档](./GOVERNANCE_FRAMEWORK.md)
- [治理总纲](./governance-manifest.yaml)
- [使用文档](./docs/governance/README.md)
- [参考资料索引](./references/references.yaml)

---

**版本**: 1.0.0
**最后更新**: 2025-12-17
**维护者**: MachineNativeOps 治理团队
