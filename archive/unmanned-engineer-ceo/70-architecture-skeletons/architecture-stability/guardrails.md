# Architecture Stability Guardrails

## 硬性邊界

1. **禁止反向依賴**
   - 核心層不得依賴上層任何模組
   - 依賴方向必須嚴格單向：applications ← agents ← services ← platform ← core

2. **禁止同層直接依賴**
   - services 間禁止直接 import，必須透過 HTTP/gRPC/Event
   - agents 間禁止直接 import，必須透過 MCP/HTTP

3. **禁止循環依賴**
   - 任何層級不得形成依賴環
   - 自動化工具檢測，違規阻止合併

4. **禁止混合資料所有權**
   - 每個 service 擁有自己的資料庫
   - 跨服務資料存取只能透過 API/Event/Read Model
   - 禁止 service A 直接寫入 service B 的資料庫
