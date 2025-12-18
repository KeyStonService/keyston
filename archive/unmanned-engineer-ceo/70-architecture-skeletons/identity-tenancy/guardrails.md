# Identity & Tenancy Guardrails

1. **禁止跨租戶的未授權存取**
   - 查詢必須包含 tenant_id 過濾條件
   - 不得在應用層面"trust"用戶提供的 tenant_id

2. **禁止在共享資源中混合租戶資料**
   - 除非明確標記為"跨租戶協作"場景

3. **禁止繞過租戶配額限制**
