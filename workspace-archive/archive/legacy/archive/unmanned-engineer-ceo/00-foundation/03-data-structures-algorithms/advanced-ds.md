# Advanced Data Structures

## Storage-Oriented

- **B-Tree/B+Tree**：適用於 transactional
  state；對應 PostgreSQL/SQLite 嵌入式模組。
=======

- **B-Tree/B+Tree**：適用於 transactional state；對應 PostgreSQL/SQLite 嵌入式模組。

>>>>>>> origin/copilot/sub-pr-402

- **LSM Tree**：寫優化儲存（e.g., RocksDB）；建議用於 event log。
- **Skip List**：核心 registry 的內存索引，簡化複製。

## Graph / Hypergraph

- **Property Graph**：支援 docs/knowledge-graph.yaml。
- **Hypergraph**：映射多代理與任務依賴（core/mind_matrix）。

## Probabilistic Structures

- **Bloom Filter**：API 快速判斷重複。
- **Count-Min Sketch**：流量熱點偵測。

## Implementation Notes

- 使用 TypeScript + Rust FFI（wasm-pack）實作高性能結構。
- 在 `tests/` 內建立基準測試，並記錄於 10-performance-engineering。
