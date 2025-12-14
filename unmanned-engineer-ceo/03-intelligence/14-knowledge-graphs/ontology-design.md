# Ontology Design / 本體設計

## 層級
1. **Entity**：Service, Agent, Document, Simulation。
2. **Relation**：DependsOn, Produces, Observes, Governs。
3. **Event**：Build, Deploy, Incident, Review。

## Schema
- 與 docs/knowledge-graph.yaml 對齊，並依 governance/schemas/ontology.schema.json 驗證。
- 以 YAML/JSON-LD 表達，利於 pipelines。

## 指南
- 新節點必須參照 config/system-module-map。
- Trait/Skill 需鏈接至 30-assessment 的 YAML。
