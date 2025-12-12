# Multi-Team Collaboration Models

## 模式

1. **Platform + Product Pods**：Platform 維護基礎建設；Product 擁有垂直能力。
2. **Guild / Chapter**：跨團隊能力群（Architecture Guild, Reliability Guild）。
3. **Embedded SRE**：SRE 進駐高風險產品線。

## CODEOWNERS 策略

- 依 core/、automation/、docs/ 區塊分 ownership。
- 重要檔案（synergymesh.yaml, config/\*）必須由 Governance 團隊審核。

## 工具

- CODEOWNERS
- GitHub Teams + Slack 通知
- services/agents/orchestrator 自動派工
