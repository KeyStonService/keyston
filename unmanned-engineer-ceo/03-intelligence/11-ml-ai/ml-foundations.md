# ML Foundations / 機器學習基礎

## Paradigms
- **Supervised**：Regression, Classification，應用於 Auto-Fix Bot。
- **Unsupervised**：Clustering, Dimensionality Reduction，用於 drift 偵測。
- **Reinforcement**：Policy gradients，應用於 autonomous 升級決策。

## Pipeline
1. Data → ingestion via monitoring/logs。
2. Feature Store → config/dependencies.yaml 管控。
3. Training → applications/ml-pipeline。
4. Serving → services/agents/intelligent。

## Quality Gates
- Data validation (Great Expectations)
- Model metrics (AUC, F1, RMSE)
- Bias/Fairness review
