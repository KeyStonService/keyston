# 分布式系統課綱 / Distributed Systems Syllabus

## 模組結構 Modules

1. **時鐘與時間**
   - Lamport Clock, Vector Clock, Hybrid Logical Clock
   - 實作：將 HLC 套用到 core/contract_service 的審計事件
2. **一致性理論**
   - CAP, PACELC, BASE, Brewer's conjecture
   - 決策：SynergyMesh 服務在不同 domain 選擇何種一致性
3. **共識演算法**
   - Paxos, Raft, Viewstamped Replication
   - 實作：Raft 日誌複製與 snapshotting
4. **複寫與分片**
   - Leader/Follower, Multi-leader, Sharding, Consistent Hashing
   - 實作：在 config/system-module-map 對不同服務標註分片策略
5. **容錯與混沌**
   - 故障模式分類、網路分割、故障注入設計
   - 實作：automation/architect 測試腳本
6. **觀測與調優**
   - 分布式追蹤、指標、日誌聚合
   - 實作：infrastructure/monitoring dashboards

## 評估方式 Assessment

- 期中：設計一個支援 Multi-Region 的 registry，提交架構圖 + failure matrix。
- 期末：完成 labs/raft-playground.md 所列全部任務並生成報告。
- Bonus：提出 SynergyMesh 新的 consensus
  plug-in，寫入 docs/KNOWLEDGE_HEALTH.md。
