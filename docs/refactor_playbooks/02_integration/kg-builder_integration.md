# Knowledge Graph Builder - Integration Planning
# 知識圖譜構建器 - 集成規劃設計

**規劃日期 (Planning Date)**: 2025-12-07  
**前置文檔 (Previous Document)**: `01_deconstruction/kg-builder_deconstruction.md`  
**後續文檔 (Next Document)**: `03_refactor/kg-builder_refactor.md`  
**規劃範圍 (Planning Scope)**: Legacy content → Unmanned Island system integration

---

## 🎯 1. 集成目標 (Integration Objectives)

### 1.1 主要目標 (Primary Goals)

1. **去 AXIOM 化 (De-AXIOM-ization)**: 移除供應商特定術語，抽象為通用概念
2. **關注點分離 (Separation of Concerns)**: 將單一 564 行 YAML 拆分為邏輯模組
3. **系統融合 (System Integration)**: 將 KG Builder 概念融入 Unmanned Island 架構
4. **可復用性 (Reusability)**: 提取通用模式供其他插件使用
5. **治理合規 (Governance Compliance)**: 符合現有語言治理與安全策略

### 1.2 非目標 (Non-Goals)

- ❌ 不實現完整的知識圖譜構建器（僅整合規範與模式）
- ❌ 不修改現有運行中的服務邏輯
- ❌ 不引入新的外部依賴（除非明確必要）

---

## 🧩 2. 邏輯 → 目標位置對應表 (Logic → Target Location Mapping)

### 2.1 架構文檔類 (Architecture Documentation)

| 邏輯名稱 | 說明 | 建議目標路徑 | 檔案角色 |
|---------|-----|-------------|---------|
| **Knowledge Graph Processing Flow** | 6 階段處理流水線設計 | `docs/ARCHITECTURE/knowledge-graph-processing.md` | 架構設計文檔 |
| **Plugin Architecture Pattern** | 插件註冊、依賴管理、向量對齊模式 | `docs/ARCHITECTURE/plugin-architecture-pattern.md` | 架構模式文檔 |
| **Storage Architecture Design** | 三層存儲架構（Primary/Cache/Backup） | `docs/ARCHITECTURE/storage-architecture.md` | 存儲設計文檔 |
| **Hybrid Batch-Stream Processing** | 批流混合處理模式 | `docs/ARCHITECTURE/batch-stream-processing.md` | 處理模式文檔 |
| **Vector Alignment Strategy** | 向量嵌入維度與相似度閾值策略 | `docs/ARCHITECTURE/vector-alignment-strategy.md` | AI/ML 架構文檔 |

### 2.2 配置文件類 (Configuration Files)

| 邏輯名稱 | 說明 | 建議目標路徑 | 檔案角色 |
|---------|-----|-------------|---------|
| **Plugin Specification Template** | 通用插件規範模板 | `config/templates/plugin-specification-template.yaml` | 配置模板 |
| **Vector Alignment Config** | 向量嵌入模型配置 | `config/ai-models/vector-alignment-config.yaml` | AI 模型配置 |
| **Processing Pipeline Config** | NLP 處理管線配置 | `config/processing/pipeline-config.yaml` | 處理配置 |
| **Quality Control Config** | 質量門檻與信心評分配置 | `config/quality/quality-control-config.yaml` | 質量配置 |
| **Resource Quota Template** | Kubernetes 資源配額模板 | `config/kubernetes/resource-quota-template.yaml` | K8s 配置 |

### 2.3 治理規則類 (Governance Policies)

| 邏輯名稱 | 說明 | 建議目標路徑 | 檔案角色 |
|---------|-----|-------------|---------|
| **Plugin Specification Schema** | 插件規範 JSON Schema | `governance/schemas/plugin-specification.schema.json` | JSON Schema 定義 |
| **Plugin Quality Gates** | 插件質量門檻（準確率、延遲、資源使用） | `governance/policies/plugin-quality-gates.yaml` | 質量策略 |
| **Data Privacy Policy** | PII 檢測、K-匿名化、GDPR 合規規則 | `governance/policies/data-privacy-policy.yaml` | 隱私策略 |
| **Compliance Attestation** | 語義 Web 標準合規聲明（RDF, OWL, SPARQL） | `governance/policies/compliance-attestation.yaml` | 合規策略 |
| **Knowledge Processing Rules** | 知識處理質量與驗證規則 | `governance/policies/knowledge-processing-rules.yaml` | 處理策略 |

### 2.4 基礎設施模板類 (Infrastructure Templates)

| 邏輯名稱 | 說明 | 建議目標路徑 | 檔案角色 |
|---------|-----|-------------|---------|
| **Knowledge Processor Deployment** | Kubernetes Deployment 模板 | `infrastructure/kubernetes/templates/knowledge-processor-deployment.yaml` | K8s 部署模板 |
| **Neo4j StatefulSet** | Neo4j 集群部署模板 | `infrastructure/kubernetes/templates/neo4j-statefulset.yaml` | 數據庫部署 |
| **Redis Cluster Config** | Redis 集群配置 | `infrastructure/kubernetes/templates/redis-cluster-config.yaml` | 快取配置 |
| **Service & Ingress** | Service 與 Ingress 配置 | `infrastructure/kubernetes/templates/knowledge-processor-service.yaml` | K8s 網絡 |
| **Prometheus ServiceMonitor** | Prometheus 監控配置 | `infrastructure/kubernetes/templates/knowledge-processor-monitor.yaml` | 可觀測性 |

### 2.5 工具與腳本類 (Tools & Scripts)

| 邏輯名稱 | 說明 | 建議目標路徑 | 檔案角色 |
|---------|-----|-------------|---------|
| **Plugin Spec Validator** | 驗證插件規範格式與必填欄位 | `tools/validate-plugin-spec.py` | 驗證工具 |
| **Plugin Registry CLI** | 插件註冊、查詢、更新 CLI | `tools/cli/plugin-registry-cli.py` | CLI 工具 |
| **Knowledge Processor Benchmark** | 性能基準測試工具 | `tools/benchmark-knowledge-processor.py` | 測試工具 |
| **Triple Quality Analyzer** | 分析三元組質量與一致性 | `tools/ai-auto-fix.py` (擴展) | 質量分析 |
| **Ontology Validator** | OWL 本體一致性驗證 | `tools/validate-ontology.py` | 驗證工具 |

### 2.6 知識庫增強類 (Knowledge Base Enhancement)

| 邏輯名稱 | 說明 | 建議目標路徑 | 檔案角色 |
|---------|-----|-------------|---------|
| **KG Builder Module Entry** | 在系統模組地圖中添加 KG Builder | `config/system-module-map.yaml` (擴展) | 模組註冊 |
| **Knowledge Processing Workflow** | 知識處理工作流定義 | `knowledge/processing-workflows/` (新建目錄) | 工作流定義 |
| **Semantic Patterns Library** | 語義模式庫（relation patterns） | `knowledge/semantic-patterns/` (新建目錄) | 模式庫 |
| **Entity Resolution Rules** | 實體解析規則庫 | `knowledge/entity-resolution-rules/` (新建目錄) | 規則庫 |

### 2.7 重構 Playbook 元數據類 (Refactor Playbook Metadata)

| 邏輯名稱 | 說明 | 建議目標路徑 | 檔案角色 |
|---------|-----|-------------|---------|
| **AI Prompt Templates** | KG Builder 相關 AI 提示模板 | `docs/refactor_playbooks/03_refactor/meta/AI_PROMPTS.md` (擴展) | AI 提示集合 |
| **CI Integration Guide** | KG Builder 規範驗證 CI 集成 | `docs/refactor_playbooks/03_refactor/meta/CI_INTEGRATION.md` (擴展) | CI 集成指南 |
| **Plugin Architecture Examples** | 插件架構示例 | `docs/refactor_playbooks/03_refactor/meta/PLUGIN_ARCHITECTURE_EXAMPLES.md` (新建) | 示例文檔 |

---

## 🏗️ 3. 目錄與檔案整合藍圖 (Directory & File Integration Blueprint)

### 3.1 受影響目錄結構 (Affected Directory Structure)

```
unmanned-island/
├── docs/
│   ├── ARCHITECTURE/                              # [擴展] 架構文檔
│   │   ├── knowledge-graph-processing.md          # [新建] KG 處理流程設計
│   │   ├── plugin-architecture-pattern.md         # [新建] 插件架構模式
│   │   ├── storage-architecture.md                # [新建] 三層存儲架構
│   │   ├── batch-stream-processing.md             # [新建] 批流混合處理
│   │   └── vector-alignment-strategy.md           # [新建] 向量對齊策略
│   │
│   └── refactor_playbooks/                        # [擴展] 重構劇本
│       ├── 01_deconstruction/
│       │   └── kg-builder_deconstruction.md       # [已完成] 解構分析
│       ├── 02_integration/
│       │   └── kg-builder_integration.md          # [本文檔] 集成規劃
│       ├── 03_refactor/
│       │   ├── kg-builder_refactor.md             # [待建] 重構行動計畫
│       │   └── meta/
│       │       ├── AI_PROMPTS.md                  # [擴展] 添加 KG 相關提示
│       │       ├── CI_INTEGRATION.md              # [擴展] 添加插件驗證 CI
│       │       └── PLUGIN_ARCHITECTURE_EXAMPLES.md # [新建] 插件架構示例
│       └── _legacy_scratch/
│           └── README.md                          # [標記棄用] 原始文件
│
├── config/                                        # [擴展] 配置目錄
│   ├── system-module-map.yaml                     # [擴展] 添加 knowledge_processing 模組
│   ├── templates/                                 # [新建] 配置模板目錄
│   │   └── plugin-specification-template.yaml     # [新建] 插件規範模板
│   ├── ai-models/                                 # [新建] AI 模型配置目錄
│   │   └── vector-alignment-config.yaml           # [新建] 向量對齊配置
│   ├── processing/                                # [新建] 處理配置目錄
│   │   └── pipeline-config.yaml                   # [新建] 處理管線配置
│   ├── quality/                                   # [新建] 質量配置目錄
│   │   └── quality-control-config.yaml            # [新建] 質量控制配置
│   └── kubernetes/                                # [新建] K8s 配置目錄
│       └── resource-quota-template.yaml           # [新建] 資源配額模板
│
├── governance/                                    # [擴展] 治理目錄
│   ├── schemas/                                   # [擴展] Schema 目錄
│   │   └── plugin-specification.schema.json       # [新建] 插件規範 Schema
│   └── policies/                                  # [擴展] 策略目錄
│       ├── plugin-quality-gates.yaml              # [新建] 插件質量門檻
│       ├── data-privacy-policy.yaml               # [新建] 數據隱私策略
│       ├── compliance-attestation.yaml            # [新建] 合規聲明
│       └── knowledge-processing-rules.yaml        # [新建] 知識處理規則
│
├── infrastructure/                                # [擴展] 基礎設施目錄
│   └── kubernetes/
│       └── templates/                             # [新建] K8s 模板目錄
│           ├── knowledge-processor-deployment.yaml # [新建] 知識處理器部署
│           ├── neo4j-statefulset.yaml             # [新建] Neo4j 部署
│           ├── redis-cluster-config.yaml          # [新建] Redis 配置
│           ├── knowledge-processor-service.yaml   # [新建] Service 配置
│           └── knowledge-processor-monitor.yaml   # [新建] Prometheus 監控
│
├── knowledge/                                     # [擴展] 知識庫目錄
│   ├── processing-workflows/                      # [新建] 處理工作流目錄
│   │   └── kg-construction-workflow.yaml          # [新建] KG 構建工作流
│   ├── semantic-patterns/                         # [新建] 語義模式目錄
│   │   ├── relation-patterns.json                 # [新建] 關係模式庫
│   │   └── entity-patterns.json                   # [新建] 實體模式庫
│   └── entity-resolution-rules/                   # [新建] 實體解析規則目錄
│       └── similarity-rules.yaml                  # [新建] 相似度規則
│
└── tools/                                         # [擴展] 工具目錄
    ├── validate-plugin-spec.py                    # [新建] 插件規範驗證工具
    ├── validate-ontology.py                       # [新建] 本體驗證工具
    ├── benchmark-knowledge-processor.py           # [新建] 性能基準測試
    ├── ai-auto-fix.py                             # [擴展] 添加三元組質量分析
    └── cli/                                       # [擴展] CLI 工具目錄
        └── plugin-registry-cli.py                 # [新建] 插件註冊 CLI
```

### 3.2 檔案關係圖 (File Relationship Diagram)

```
[Legacy Source]
    └── _legacy_scratch/README.md
            │
            ├─[解構]─→ 01_deconstruction/kg-builder_deconstruction.md
            │
            ├─[集成]─→ 02_integration/kg-builder_integration.md (本文檔)
            │
            └─[重構]─→ 03_refactor/kg-builder_refactor.md
                        ↓
            ┌───────────┼───────────┬───────────┬───────────┐
            ↓           ↓           ↓           ↓           ↓
        [架構文檔]   [配置文件]   [治理規則]   [基礎設施]   [工具腳本]
            ↓           ↓           ↓           ↓           ↓
    docs/ARCHITECTURE/  config/   governance/  infrastructure/  tools/
```

---

## 🔗 4. 跨模組接線策略 (Cross-Module Wiring Strategy)

### 4.1 與現有模組的集成點 (Integration Points with Existing Modules)

#### 4.1.1 Core Platform Integration

```yaml
# config/system-module-map.yaml (擴展)
core_platform:
  modules:
    knowledge_processing:                          # [新增模組]
      path: "core/knowledge_processing/"
      description: "知識圖譜構建與語義處理"
      components:
        - id: "triple_extractor"
          provides: ["TripleExtraction", "EntityRecognition"]
        - id: "ontology_builder"
          provides: ["OntologyGeneration", "SchemaMapping"]
        - id: "entity_resolver"
          provides: ["EntityResolution", "FuzzyMatching"]
      dependencies:
        - "unified_integration.service_registry"
        - "unified_integration.configuration_manager"
```

#### 4.1.2 Automation Integration

```yaml
# automation/intelligent/ 整合
Knowledge Processing Automation:
  - Input: Documents from automation/intelligent/document-parser/
  - Processing: Triple extraction → Entity resolution → Ontology building
  - Output: Knowledge graphs to knowledge/ directory
  - Trigger: Event-driven via automation/intelligent/event-bus/
```

#### 4.1.3 Governance Integration

```yaml
# governance/policies/ 整合
Knowledge Quality Gates:
  - Pre-commit: Validate plugin spec against schema
  - CI Pipeline: Run triple quality checks
  - Post-deployment: Monitor accuracy metrics
```

### 4.2 數據流接線 (Data Flow Wiring)

```
[Upstream Data Sources]
    ├─ automation/intelligent/document-parser/    → 文檔解析
    ├─ core/contract_service/                     → 合約文檔
    └─ knowledge/                                 → 現有知識庫
            ↓
[Knowledge Processing Layer] (新增)
    ├─ Entity Extraction (NLP Pipeline)
    ├─ Relation Extraction (Dependency Parser)
    └─ Ontology Building (Schema Mapper)
            ↓
[Storage Layer]
    ├─ knowledge/ (Triples, Ontology, Entity Index)
    ├─ docs/knowledge-graph.yaml (更新)
    └─ docs/superroot-entities.yaml (更新)
            ↓
[Downstream Consumers]
    ├─ core/ai_decision_engine.py (語義推理)
    ├─ automation/intelligent/ (智能自動化)
    └─ docs/ (文檔生成與檢索)
```

---

## 🎨 5. 語言層級策略 (Language Tier Strategy)

### 5.1 語言選擇對齊 (Language Choice Alignment)

根據 `config/system-module-map.yaml` 的語言策略：

| 功能層 | 推薦語言 | 理由 | 對應組件 |
|-------|---------|-----|---------|
| **高層邏輯** | Python | AI/ML 處理、NLP 管線 | Entity Extraction, Relation Extraction |
| **類型安全邏輯** | TypeScript | 插件註冊、配置管理 | Plugin Registry CLI, Config Validator |
| **配置文件** | YAML | 聲明式配置 | 所有 config/ 下的配置文件 |
| **Schema 定義** | JSON Schema | 結構驗證 | Plugin Specification Schema |
| **基礎設施** | Go (可選) | 高性能 CLI 工具 | 未來可重寫 plugin-registry-cli |
| **部署配置** | Kubernetes YAML | 容器編排 | infrastructure/kubernetes/templates/ |

### 5.2 語言遷移策略 (Language Migration Strategy)

- ✅ **保留**: Python（NLP 處理）、YAML（配置）
- ⚠️ **新增**: TypeScript（插件註冊邏輯）、JSON Schema（結構驗證）
- ❌ **避免**: PHP, Perl, Ruby（根據全域禁用策略）

---

## 🛡️ 6. 安全與合規對齊 (Security & Compliance Alignment)

### 6.1 數據隱私對齊 (Data Privacy Alignment)

```yaml
# governance/policies/data-privacy-policy.yaml (新建)
data_privacy:
  pii_detection:
    enabled: true
    methods: ["regex", "ml-based"]
  anonymization:
    strategy: "k-anonymity"
    k_value: 5
  gdpr_compliance:
    data_minimization: true
    purpose_limitation: true
    consent_management: "external-service"
    right_to_erasure: true
```

### 6.2 SLSA Provenance 對齊 (SLSA Provenance Alignment)

```yaml
# core/slsa_provenance/ 整合
Knowledge Graph Artifacts:
  - Triples: Signed with Sigstore
  - Ontology: SLSA Level 3 provenance
  - Entity Index: Hash verification (sha3-256)
```

### 6.3 安全掃描對齊 (Security Scanning Alignment)

- ✅ Semgrep: 掃描 Python 知識處理代碼
- ✅ CodeQL: 掃描 TypeScript 插件註冊邏輯
- ✅ Trivy: 掃描 Kubernetes 部署模板
- ✅ OSV Scanner: 掃描 NLP 依賴包（spacy, transformers）

---

## 📊 7. 質量門檻對齊 (Quality Threshold Alignment)

### 7.1 插件質量門檻 (Plugin Quality Gates)

```yaml
# governance/policies/plugin-quality-gates.yaml (新建)
plugin_quality_gates:
  accuracy_thresholds:
    entity_extraction_precision: ">= 0.85"
    relation_extraction_recall: ">= 0.80"
    entity_resolution_accuracy: ">= 0.85"
    ontology_consistency_score: ">= 0.90"
  
  performance_thresholds:
    triple_extraction_rate: ">= 1000 triples/minute"
    processing_latency_p95: "<= 30 seconds"
    memory_per_document: "<= 100 MB"
  
  resource_thresholds:
    cpu_utilization_target: "70%"
    auto_scaling_threshold: "85%"
```

### 7.2 與現有質量門檻對齊 (Alignment with Existing Thresholds)

```yaml
# config/system-module-map.yaml (現有)
defaults:
  quality_thresholds:
    semgrep_high_max: 0                  # ✅ 應用於知識處理代碼
    test_coverage_min: 70                # ✅ 應用於插件工具
    cyclomatic_complexity_max: 15        # ✅ 應用於處理邏輯
```

---

## 🚀 8. 部署與運維對齊 (Deployment & Operations Alignment)

### 8.1 Kubernetes 部署對齊 (Kubernetes Deployment Alignment)

```yaml
# infrastructure/kubernetes/templates/knowledge-processor-deployment.yaml
# 對齊現有部署規範:
# - 使用 config/kubernetes/ 資源配額
# - 使用 governance/policies/ 安全策略
# - 使用 config/monitoring.yaml Prometheus 配置
```

### 8.2 CI/CD 對齊 (CI/CD Alignment)

```yaml
# .github/workflows/knowledge-processing-ci.yml (待建)
Knowledge Processing CI:
  - Validate plugin specs (tools/validate-plugin-spec.py)
  - Run triple quality tests
  - Check ontology consistency
  - Benchmark performance
  - Publish artifacts to knowledge/
```

---

## 📈 9. 可觀測性對齊 (Observability Alignment)

### 9.1 Metrics 對齊 (Metrics Alignment)

```yaml
# config/prometheus-rules.yml (擴展)
groups:
  - name: knowledge_processing_alerts
    rules:
      - alert: LowTripleExtractionRate
        expr: kg_triples_extracted_total < 1000
        for: 5m
      - alert: LowEntityResolutionAccuracy
        expr: kg_entity_resolution_accuracy < 0.85
        for: 10m
```

### 9.2 Logging 對齊 (Logging Alignment)

```yaml
# config/monitoring.yaml (擴展)
logging:
  knowledge_processing:
    level: "INFO"
    structured_fields:
      - document_id
      - processing_stage
      - confidence_score
      - entity_count
      - triple_count
```

---

## 🔄 10. 遷移與回滾策略 (Migration & Rollback Strategy)

### 10.1 遷移階段 (Migration Phases)

#### Phase 1: 文檔與配置遷移 (P0)
- 創建架構文檔 (`docs/ARCHITECTURE/`)
- 創建配置模板 (`config/templates/`)
- 創建治理規則 (`governance/policies/`, `governance/schemas/`)
- **回滾**: 刪除新建文件，無影響現有系統

#### Phase 2: 工具與腳本遷移 (P1)
- 創建驗證工具 (`tools/validate-plugin-spec.py`)
- 創建 CLI 工具 (`tools/cli/plugin-registry-cli.py`)
- **回滾**: 刪除工具文件，不影響運行時

#### Phase 3: 模組註冊遷移 (P1)
- 更新 `config/system-module-map.yaml`
- 創建知識處理工作流 (`knowledge/processing-workflows/`)
- **回滾**: Git revert `system-module-map.yaml` 變更

#### Phase 4: CI/CD 集成 (P2)
- 創建 GitHub Actions workflow
- 集成到現有 CI/CD pipeline
- **回滾**: 禁用新 workflow，現有 CI 不受影響

### 10.2 回滾檢查清單 (Rollback Checklist)

```yaml
Rollback Safety:
  - ✅ 所有新建文件獨立於現有運行時
  - ✅ 配置變更向後兼容
  - ✅ 無數據庫 schema 變更
  - ✅ 無 API 破壞性變更
  - ⚠️ 需回滾 system-module-map.yaml 如出現問題
```

---

## 🎯 11. 驗收條件 (Acceptance Criteria)

### 11.1 功能性驗收 (Functional Acceptance)

- ✅ 所有架構文檔創建完成並通過 Markdown lint
- ✅ 所有配置文件通過 YAML syntax 驗證
- ✅ 所有 JSON Schema 通過驗證器測試
- ✅ 所有工具腳本通過單元測試（覆蓋率 >= 70%）
- ✅ 插件規範驗證工具能正確驗證示例規範

### 11.2 質量性驗收 (Quality Acceptance)

- ✅ Semgrep: 0 HIGH, <= 5 MEDIUM violations
- ✅ CodeQL: 無安全漏洞
- ✅ 文檔完整性: 所有新建文件在 `DOCUMENTATION_INDEX.md` 中註冊
- ✅ 依賴安全: 所有 Python 依賴通過 OSV scanner

### 11.3 整合性驗收 (Integration Acceptance)

- ✅ `config/system-module-map.yaml` 通過 schema 驗證
- ✅ 知識圖譜工作流與現有 `automation/intelligent/` 無衝突
- ✅ 新建 Kubernetes 模板通過 `kubectl apply --dry-run`
- ✅ CI 管線成功運行新增驗證步驟

---

## 📚 12. 引用與依賴 (References & Dependencies)

### 12.1 上游依賴 (Upstream Dependencies)

- `docs/refactor_playbooks/01_deconstruction/kg-builder_deconstruction.md` (解構分析)
- `config/system-module-map.yaml` (系統模組映射)
- `governance/policies/base-policy.yaml` (基礎策略)
- `docs/ARCHITECTURE/` (現有架構文檔)

### 12.2 下游產出 (Downstream Outputs)

- `docs/refactor_playbooks/03_refactor/kg-builder_refactor.md` (重構行動計畫)
- 所有在「邏輯 → 目標位置對應表」中列出的新建文件

---

## 🎬 13. 下一步行動 (Next Steps)

1. ✅ **完成集成設計** - 本文檔（已完成）
2. ⏭️ **創建重構計畫** - `03_refactor/kg-builder_refactor.md`
3. ⏭️ **執行 P0 行動** - 創建關鍵架構文檔與配置模板
4. ⏭️ **執行 P1 行動** - 創建工具與腳本
5. ⏭️ **執行 P2 行動** - CI/CD 集成與優化

---

**集成設計完成時間 (Integration Planning Completed)**: 2025-12-07T10:19:24Z  
**前置文檔 (Previous)**: `01_deconstruction/kg-builder_deconstruction.md` ✅  
**下一步文檔 (Next)**: `03_refactor/kg-builder_refactor.md` ⏭️  
**狀態 (Status)**: ✅ Integration Planning Complete - Ready for Refactor Phase
