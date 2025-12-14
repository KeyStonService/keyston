# 異常預測 / Anomaly & Forecasting

## Use Cases
- Observability：指標異常 → 觸發 Auto-Fix Bot。
- Supply Chain：建置時間預測 → 提前調整資源。
- Drone Ops：電池/感測器故障預警。

## 模型
- ARIMA / Prophet → 短期趨勢。
- LSTM / TCN → 長序列。
- Isolation Forest / DBSCAN → 異常偵測。

## Pipeline
1. 收集 metrics/logs → infrastructure/monitoring。
2. 特徵工程 → applications/ml-pipeline。
3. 模型訓練 → ML orchestration。
4. 推論結果 → docs/KNOWLEDGE_HEALTH.md Panel。
