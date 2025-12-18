# Knowledge Fusion Guide

## Pipeline

1. **Ingest**：收集 docs/, config/, governance/ 指標。
2. **Normalize**：使用 schema 定義將資料轉換為統一結構。
3. **Link**：建立 entity ↔ document ↔ metric 邊。
4. **Publish**：輸出至 docs/knowledge-graph.yaml + knowledge-index.yaml。

## Tools

- Python ETL（runtime/knowledge-base）
- Graph ETL（memgraph, neptune）
- Validation（tools/docs/validate_index.py）

## Output

- 提供 API 供 agents/ 使用。
- 更新 metrics-and-roi 的洞察摘要。
