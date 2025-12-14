# RCA Playbook / 根因分析手冊

## 流程
1. **檢測 Detect**：警報觸發（PagerDuty, Slack）。
2. **穩定 Stabilize**: 啟動 incident commander，參考 incident-game-days 模板。
3. **診斷 Diagnose**: 收集 log/metrics/trace，繪製時間線。
4. **修復 Remediate**: 套用 canary-rollback 或 feature flag。
5. **學習 Learn**: 更新 docs/KNOWLEDGE_HEALTH.md，錄入 metrics-and-roi。

## 工具
- OpenTelemetry Collector
- Grafana Incident
- ChatOps Bot（services/agents/devops）
