# ML in Unmanned Island Platform

## 角色 Role

- **Decision Assist**：輔助 core/ai_decision_engine.py。
- **Knowledge Fusion**：強化 docs/knowledge-graph.yaml。
- **Automation**：支援 automation/intelligent 與 zero_touch_deployment。

## 邊界 Boundaries

- 所有模型輸出需經 Structural Governance 驗證。
- 敏感決策（安全、隱私）必須保有人類審核。
- 資料來源須列於 config/data lineage（未來擴增）。

## 部署模式

- Batch inference → nightly jobs
- Streaming inference → event bus
- On-device inference → drone/autonomous stack
