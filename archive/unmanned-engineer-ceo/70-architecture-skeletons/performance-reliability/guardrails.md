# Performance & Reliability Guardrails

1. **禁止無重試機制的外部服務調用**

2. **禁止同步阻塞式的長時間操作**
   - 超過 5 秒的操作必須異步化

3. **禁止無限制的遞迴或循環**
