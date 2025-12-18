# Patterns: 分布式設計模式

## 模式列表

- **Leader Election Tiers**：利用 etcd/Consul + Island AI registry 做多層選主。
- **Command Query Replication**：CQRS + Event Sourcing，對應 core/mind_matrix。
- **Geo-Sharding Gateway**：根據 config/topology-mind-matrix.yaml 進行地理分片。
- **Hybrid Clock Reconciliation**：以 HLC 對齊事件順序，連動 docs/knowledge-graph.yaml。

## 使用建議

1. 依照 manifest.yaml 的 depends_on 欄位確認與其他模組的連結。
2. 每次將模式套入新服務時，更新此清單並在 references/ 追加案例。
