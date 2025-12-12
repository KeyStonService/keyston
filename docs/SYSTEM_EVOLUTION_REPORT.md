# 🧬 System Evolution Report

- 生成時間：2025-12-07T13:49:52.316425Z
- Config 版本：0.1.0
- 總體演化健康度：**100.0/100**

## 指標概覽

- `language_violations_total` = `0`
- `semgrep_high_total` = `0`
- `playbook_coverage_ratio` = `1.0`

## 目標與得分

### 語言治理健康度 (`language-governance`)

- 指標：`language_violations_total`
- 目前值：`0.0`，目標：`0`（lower_is_better）
- 權重：0.4
- 得分：**100.0/100**

### 安全掃描健康度 (`security`)

- 指標：`semgrep_high_total`
- 目前值：`0.0`，目標：`0`（lower_is_better）
- 權重：0.3
- 得分：**100.0/100**

### 重構劇本覆蓋率 (`refactor-playbook-coverage`)

- 指標：`playbook_coverage_ratio`
- 目前值：`1.0`，目標：`1.0`（higher_is_better）
- 權重：0.3
- 得分：**100.0/100**

## 下一步建議（高階）

> 以下是根據分數粗略給出的優先級建議，你可以再交給 AI 做更細的 Refactor
> Playbook。

- `language-governance`（語言治理健康度）：目前得分 100.0/100
  → 優先針對違規最多的 cluster（依 language-governance-report 排序），更新對應的 03_refactor 劇本並排入 P0 任務。
- `security`（安全掃描健康度）：目前得分 100.0/100 → 列出全部 Semgrep
  HIGH 問題，對應到 services/core 的 cluster，建立或更新這些區域的安全重構 Playbook。
- `refactor-playbook-coverage`（重構劇本覆蓋率）：目前得分 100.0/100
  → 找出 cluster-heatmap 中沒有對應 03_refactor
  Playbook 的 cluster，為其建立最小可用的重構劇本。

---

本報告由 `tools/evolution/generate_evolution_report.py` 自動生成。
