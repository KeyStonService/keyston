# 活體知識庫設計

## 目標

- 讓系統具備自我感知能力
- 跨 Agent 共用的長期記憶
- 支援回放、對比、根因分析

## 架構

- **Ingress**：從代碼、日誌、指標、Issue 抽取片段
- **Storage**：向量資料庫 + 事件溯源存儲
- **Reasoning**：語義查詢 + 模式偵測
- **Egress**：提供 Agent 查詢、治理稽核、報表

## 數據模型

```yaml
entry:
  id: uuid
  source: git|ci|runtime|user
  embedding: vector
  annotations:
    - key: decision-level
      value: L3
  retention: 90d
```

## 同步策略

- 每次 PR、部署、告警皆觸發快照
- 大量改動以批次+TTL 控制
- 定期蒐集「遺忘候選」清單

## API

```bash
# 查詢知識片段
island-cli knowledge:search "Schema pipeline"

# 注入新知識
island-cli knowledge:ingest --file report.md
```

---

## 治理框架整合

活體知識庫已整合進 MachineNativeOps 治理框架的 **99-元數據管理中心**：

- **維度路徑**: [src/governance/dimensions/99-metadata/](../../../src/governance/dimensions/99-metadata/)
- **完整文檔**: [99-metadata README](../../../src/governance/dimensions/99-metadata/README.md)
- **主文檔**: [活體知識庫](../../LIVING_KNOWLEDGE_BASE.md)

此整合提供：

- 統一的元數據治理
- 完整的數據溯源和血緣追蹤
- 機器可讀的知識圖譜
- 自動化的健康診斷和回饋
