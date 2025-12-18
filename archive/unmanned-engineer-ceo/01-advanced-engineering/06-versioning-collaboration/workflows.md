# Versioning & Collaboration Workflows

## Git Flow vs Trunk vs GitHub Flow

- **Git Flow**：適用長期發版（infrastructure 等）。
- **Trunk Based**：core/contract_service、agents；以短分支 + feature flags。
- **GitHub Flow**：docs/、config/ 小改動。

## Branch Policies

- 命名：`feature/<scope>`、`fix/<scope>`、`exp/<scope>`。
- 最少 2 位 Reviewer + 1 位自動審查（Auto-Fix Bot）。

## Release Tags

- `v<major>.<minor>.<patch>`；對應 config/system-manifest 版本。
- 需更新 CHANGELOG.md、docs/KNOWLEDGE_HEALTH.md。

## Tools

- gh cli、自動 PR 模板（.github/pull_request_template.md）。
