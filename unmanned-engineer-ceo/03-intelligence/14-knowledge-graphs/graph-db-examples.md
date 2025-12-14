# Graph DB Examples

## Neo4j
```cypher
MATCH (s:Service {name: 'contract'})-[:DEPENDS_ON]->(c:Config)
RETURN s, c;
```

## ArangoDB
```
FOR v, e IN 1..2 OUTBOUND 'services/contract'
GRAPH 'unmanned'
RETURN {vertex: v, edge: e}
```

## Tips
- 使用 pipelines/ 產出的 JSON 匯入圖資料庫。
- 建立測試資料以支援 knowledge-fusion.md 的流程。
