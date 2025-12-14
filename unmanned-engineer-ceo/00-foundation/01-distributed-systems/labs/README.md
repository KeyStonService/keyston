# Labs: 分布式實作 / Distributed Labs

| Lab | 目標 | 對接模組 |
| --- | ---- | -------- |
| Lab 01 | 實作最小 Raft 複製與日誌壓縮 | core/contract_service/state | 
| Lab 02 | 故障注入：模擬 30% 延遲尖峰與網路分割 | automation/autonomous/architecture-stability |
| Lab 03 | 混沌測試：leader election oscillation | infrastructure/monitoring | 

## 執行說明
1. 使用 `npm exec --workspace core/contract_service/contracts-L1/contracts ts-node scripts/raft-lab.ts` 啟動 Raft 模擬。
2. 以 `python automation/architect/fault_injector.py --scenario network-partition` 觸發混沌。
3. 將結果寫入 docs/KNOWLEDGE_HEALTH.md → Distributed Systems Panel。
