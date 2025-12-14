# 分布式系統能力概覽 / Distributed Systems Overview

## 為何重要 Why It Matters
- SynergyMesh 核心（core/unified_integration、core/mind_matrix）在多服務拓撲下運作，需要一致性的決策與複製策略。
- Autonomous Framework 內的無人機/自駕模組要求 100Hz 控制回路與容錯，分布式理論是安全閥。
- Island AI Runtime (core/island_ai_runtime) 的治理訊號需在 event-driven 管道中維持順序與溫度。

## 能力構面 Capability Pillars
1. **共識**：Paxos / Raft / Multi-Paxos / EPaxos，對應合約服務與 registry 的狀態流。
2. **一致性模型**：強一致、最終一致、因果一致，映射到 config/system-module-map 中的資料寫入策略。
3. **複寫與分片**：sharding、range/哈希分片、leader/follower 與 quorum 調整。
4. **容錯設計**：網路分割、延遲尖峰、clock drift、故障注入。
5. **觀測**：將遙測/trace 指標映射至 infrastructure/monitoring。

## 使用指南 How To Consume
- 從 `syllabus.md` 取得課程/閱讀順序。
- `labs/` 內提供 Raft 實作與混沌測試腳本，建議接入 automation/autonomous 的模擬環境。
- `patterns/` 提供常用設計模式，搭配 `references/` 內部/外部資源進行 traceability。
