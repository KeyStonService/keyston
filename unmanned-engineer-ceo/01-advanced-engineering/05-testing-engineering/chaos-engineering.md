# Chaos Engineering Guide

## 目標

- 驗證核心工作流（contract service、autonomous stack、knowledge
  base）在失效條件下的穩健度。

## 框架

1. **定義穩態**：與 observability-model.md 對齊 KPI。
2. **設計實驗**：延遲注入、節點失聯、資料庫 failover。
3. **執行**：使用 automation/architect/fault_injector.py 或 litmus chaos。
4. **學習**：更新 docs/KNOWLEDGE_HEALTH.md 與 incident 日誌。

## Recommended Scenarios

- API Gateway latency spike (HTTP 503)
- Drone coordinator process crash
- Knowledge graph storage corruption (simulate via snapshot rollback)
