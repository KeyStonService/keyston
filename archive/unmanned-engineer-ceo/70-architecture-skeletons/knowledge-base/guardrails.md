# Knowledge Base Guardrails

1. **禁止跨租戶的知識洩漏**
   - 查詢必須包含 tenant_id 過濾

2. **禁止未清理的原始資料寫入**
   - 必須經過 sanitization

3. **禁止無版本追蹤的知識更新**
