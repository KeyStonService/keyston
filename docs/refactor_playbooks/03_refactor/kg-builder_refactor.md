# Knowledge Graph Builder - Refactor Action Plan

# 知識圖譜構建器 - 重構行動計畫

**計畫日期 (Plan Date)**: 2025-12-07  
**前置文檔 (Previous Documents)**:

- `01_deconstruction/kg-builder_deconstruction.md` ✅
- `02_integration/kg-builder_integration.md` ✅  
  **執行範圍 (Execution Scope)**: P0/P1/P2 prioritized file operations  
  **預估總工作量 (Estimated Total Effort)**: ~16-24 人時

---

## 🎯 1. 執行摘要 (Executive Summary)

本重構計畫將 `_legacy_scratch/README.md`
中的知識圖譜構建器插件規範，系統化地整合到 Unmanned
Island 系統的正式目錄結構中。整合遵循「最小變更原則」，優先利用現有目錄，避免引入新的頂層結構。

### 關鍵指標 (Key Metrics)

- **新建文件數**: 25 個
- **擴展文件數**: 5 個
- **刪除文件數**: 0 個（legacy_scratch/README.md 標記為棄用但保留）
- **受影響目錄**: 6 個 (docs/, config/, governance/, infrastructure/,
  knowledge/, tools/)
- **零破壞性變更**: 所有變更向後兼容

---

## 📊 2. P0 / P1 / P2 行動清單 (Prioritized Action List)

### 🔴 P0: 關鍵規則與文檔遷移（24-48 小時內完成）

#### P0-1: 架構文檔創建 (Architecture Documentation)

| 優先級 | 目標檔案路徑                                       | 動作類型 | 簡短理由                               |
| ------ | -------------------------------------------------- | -------- | -------------------------------------- |
| **P0** | `docs/ARCHITECTURE/plugin-architecture-pattern.md` | 新建     | 插件模式是系統擴展的基礎，需立即文檔化 |
| **P0** | `docs/ARCHITECTURE/knowledge-graph-processing.md`  | 新建     | 知識處理流程是核心邏輯，需優先說明     |
| **P0** | `docs/ARCHITECTURE/storage-architecture.md`        | 新建     | 三層存儲架構影響數據持久化策略         |

**詳細行動**:

```bash
# P0-1.1: 創建插件架構模式文檔
CREATE docs/ARCHITECTURE/plugin-architecture-pattern.md
內容來源: _legacy_scratch/README.md (Lines 51-82: plugin_specification)
抽象內容: 插件註冊機制、依賴管理、向量對齊策略
移除內容: AXIOM 特定術語（axiom.io namespace, quantum_timestamp）

# P0-1.2: 創建知識圖譜處理文檔
CREATE docs/ARCHITECTURE/knowledge-graph-processing.md
內容來源: _legacy_scratch/README.md (Lines 83-112: processing_pipeline)
抽象內容: 6 階段處理流水線、實體抽取、關係分類、本體對齊
移除內容: 硬編碼模型名稱（改為配置引用）

# P0-1.3: 創建存儲架構文檔
CREATE docs/ARCHITECTURE/storage-architecture.md
內容來源: _legacy_scratch/README.md (Lines 114-129: storage_architecture)
抽象內容: Primary (Neo4j) + Cache (Redis) + Backup 三層架構
移除內容: 特定版本號（改為範圍約束）
```

**預估時間**: 4-6 小時  
**驗收標準**:

- ✅ 所有文檔通過 Markdown lint (`npm run docs:lint`)
- ✅ 文檔包含 Mermaid 圖表
- ✅ 文檔被添加到 `DOCUMENTATION_INDEX.md`

---

#### P0-2: 治理規則與 Schema 創建 (Governance Rules & Schemas)

| 優先級 | 目標檔案路徑                                          | 動作類型 | 簡短理由                             |
| ------ | ----------------------------------------------------- | -------- | ------------------------------------ |
| **P0** | `governance/schemas/plugin-specification.schema.json` | 新建     | 插件規範驗證的基礎，影響所有插件開發 |
| **P0** | `governance/policies/plugin-quality-gates.yaml`       | 新建     | 質量門檻定義，確保插件質量           |
| **P0** | `governance/policies/data-privacy-policy.yaml`        | 新建     | 數據隱私合規，法律要求               |

**詳細行動**:

```bash
# P0-2.1: 創建插件規範 JSON Schema
CREATE governance/schemas/plugin-specification.schema.json
內容來源: _legacy_scratch/README.md (Lines 1-564: 完整結構)
抽象內容: 定義 plugin_specification, dependencies, architecture, observability 結構
移除內容: 示例值（改為 schema 約束）

# P0-2.2: 創建插件質量門檻策略
CREATE governance/policies/plugin-quality-gates.yaml
內容來源: _legacy_scratch/README.md (Lines 363-381: performance_targets)
抽象內容: 準確率門檻、性能門檻、資源使用門檻
對齊現有: config/system-module-map.yaml quality_thresholds

# P0-2.3: 創建數據隱私策略
CREATE governance/policies/data-privacy-policy.yaml
內容來源: _legacy_scratch/README.md (Lines 444-451: data_privacy)
抽象內容: PII 檢測、K-匿名化、GDPR 合規要求
對齊現有: governance/policies/base-policy.yaml
```

**預估時間**: 4-5 小時  
**驗收標準**:

- ✅ JSON Schema 通過 `ajv validate` 驗證
- ✅ YAML 策略通過 `yamllint` 驗證
- ✅ Schema 被引用在 `governance/schemas/README.md`

---

#### P0-3: 配置模板創建 (Configuration Templates)

| 優先級 | 目標檔案路徑                                          | 動作類型 | 簡短理由                       |
| ------ | ----------------------------------------------------- | -------- | ------------------------------ |
| **P0** | `config/templates/plugin-specification-template.yaml` | 新建     | 插件開發者模板，立即可用       |
| **P0** | `config/system-module-map.yaml`                       | 擴展     | 註冊 knowledge_processing 模組 |

**詳細行動**:

```bash
# P0-3.1: 創建插件規範模板
CREATE config/templates/plugin-specification-template.yaml
內容來源: _legacy_scratch/README.md (Lines 1-564: 清理後的完整規範)
抽象內容: 保留結構，移除 AXIOM 特定值，添加註釋說明
移除內容: quantum_timestamp, axiom-specific namespaces

# P0-3.2: 擴展系統模組地圖
EXTEND config/system-module-map.yaml
添加位置: directory_categories.core_platform.modules
新增模組:
  knowledge_processing:
    path: "core/knowledge_processing/"
    description: "知識圖譜構建與語義處理"
    components: [triple_extractor, ontology_builder, entity_resolver]
    dependencies: [unified_integration.service_registry]
```

**預估時間**: 3-4 小時  
**驗收標準**:

- ✅ 模板 YAML 通過 `yamllint` 驗證
- ✅ system-module-map.yaml 通過 schema 驗證
- ✅ 模板包含完整的註釋說明

---

### 🟡 P1: 工具與腳本遷移（一週內完成）

#### P1-1: 驗證工具創建 (Validation Tools)

| 優先級 | 目標檔案路徑                    | 動作類型 | 簡短理由                         |
| ------ | ------------------------------- | -------- | -------------------------------- |
| **P1** | `tools/validate-plugin-spec.py` | 新建     | 自動化驗證插件規範，提升開發效率 |
| **P1** | `tools/validate-ontology.py`    | 新建     | OWL 本體一致性驗證               |

**詳細行動**:

```bash
# P1-1.1: 創建插件規範驗證工具
CREATE tools/validate-plugin-spec.py
功能:
  - 驗證 YAML 語法
  - 驗證符合 governance/schemas/plugin-specification.schema.json
  - 檢查必填欄位（id, name, version, provides, requires）
  - 檢查依賴版本格式（semantic versioning）
使用庫: PyYAML, jsonschema, click (CLI framework)
測試: 包含單元測試（tools/tests/test_validate_plugin_spec.py）

# P1-1.2: 創建本體驗證工具
CREATE tools/validate-ontology.py
功能:
  - 驗證 OWL 語法
  - 檢查本體一致性（使用 HermiT/Fact++ reasoner）
  - 檢查類層次結構深度（max_depth <= 6）
使用庫: owlready2, rdflib
測試: 包含示例 OWL 文件測試
```

**預估時間**: 6-8 小時  
**驗收標準**:

- ✅ 工具通過 `pytest` 測試（覆蓋率 >= 70%）
- ✅ 工具通過 `pylint` 和 `mypy` 檢查
- ✅ 包含 `--help` 文檔和使用示例

---

#### P1-2: CLI 工具創建 (CLI Tools)

| 優先級 | 目標檔案路徑                       | 動作類型 | 簡短理由                 |
| ------ | ---------------------------------- | -------- | ------------------------ |
| **P1** | `tools/cli/plugin-registry-cli.py` | 新建     | 插件註冊、查詢、更新 CLI |

**詳細行動**:

```bash
# P1-2.1: 創建插件註冊 CLI
CREATE tools/cli/plugin-registry-cli.py
功能:
  - plugin register <spec-file>: 註冊插件到系統
  - plugin list: 列出所有已註冊插件
  - plugin show <plugin-id>: 顯示插件詳情
  - plugin update <plugin-id> <spec-file>: 更新插件規範
  - plugin validate <spec-file>: 驗證插件規範
使用庫: click, rich (CLI formatting), PyYAML
配置: 使用 config/system-module-map.yaml 作為註冊表
測試: 包含集成測試
```

**預估時間**: 6-8 小時  
**驗收標準**:

- ✅ CLI 通過功能測試（register, list, show, update, validate）
- ✅ CLI 包含豐富的錯誤提示與幫助信息
- ✅ CLI 支持 `--json` 輸出格式

---

#### P1-3: 架構文檔補充 (Additional Architecture Docs)

| 優先級 | 目標檔案路徑                                     | 動作類型 | 簡短理由             |
| ------ | ------------------------------------------------ | -------- | -------------------- |
| **P1** | `docs/ARCHITECTURE/batch-stream-processing.md`   | 新建     | 批流混合處理模式文檔 |
| **P1** | `docs/ARCHITECTURE/vector-alignment-strategy.md` | 新建     | 向量嵌入策略文檔     |

**詳細行動**:

```bash
# P1-3.1: 創建批流處理文檔
CREATE docs/ARCHITECTURE/batch-stream-processing.md
內容來源: _legacy_scratch/README.md (Lines 306-327: processing configuration)
抽象內容: 批處理配置、流處理配置、混合模式設計
架構圖: 包含批流處理流程圖

# P1-3.2: 創建向量對齊策略文檔
CREATE docs/ARCHITECTURE/vector-alignment-strategy.md
內容來源: _legacy_scratch/README.md (Lines 36-49: vector_alignment_map)
抽象內容: 向量嵌入維度選擇、相似度閾值策略、模型選擇
架構圖: 包含向量空間示意圖
```

**預估時間**: 4-5 小時  
**驗收標準**:

- ✅ 文檔包含清晰的架構圖
- ✅ 文檔通過 Markdown lint
- ✅ 文檔被添加到 `DOCUMENTATION_INDEX.md`

---

#### P1-4: 配置文件補充 (Additional Configuration Files)

| 優先級 | 目標檔案路徑                                    | 動作類型 | 簡短理由         |
| ------ | ----------------------------------------------- | -------- | ---------------- |
| **P1** | `config/ai-models/vector-alignment-config.yaml` | 新建     | 向量嵌入模型配置 |
| **P1** | `config/processing/pipeline-config.yaml`        | 新建     | 處理管線配置     |
| **P1** | `config/quality/quality-control-config.yaml`    | 新建     | 質量控制配置     |

**詳細行動**:

```bash
# P1-4.1: 創建向量對齊配置
CREATE config/ai-models/vector-alignment-config.yaml
內容來源: _legacy_scratch/README.md (Lines 36-49)
抽象內容: embedding_model, dimension, similarity_threshold
配置化: 支持多模型配置，移除硬編碼

# P1-4.2: 創建處理管線配置
CREATE config/processing/pipeline-config.yaml
內容來源: _legacy_scratch/README.md (Lines 83-112)
抽象內容: 6 階段處理器配置、模型路徑、置信度門檻
配置化: 支持動態增減處理階段

# P1-4.3: 創建質量控制配置
CREATE config/quality/quality-control-config.yaml
內容來源: _legacy_scratch/README.md (Lines 318-327)
抽象內容: triple_validation, confidence_scoring
對齊: config/system-module-map.yaml quality_thresholds
```

**預估時間**: 4-5 小時  
**驗收標準**:

- ✅ 所有 YAML 通過 `yamllint` 驗證
- ✅ 配置文件包含完整的註釋
- ✅ 配置文件在 `config/README.md` 中註冊

---

### 🟢 P2: 基礎設施與優化（持續改進）

#### P2-1: Kubernetes 模板創建 (Kubernetes Templates)

| 優先級 | 目標檔案路徑                                                              | 動作類型 | 簡短理由           |
| ------ | ------------------------------------------------------------------------- | -------- | ------------------ |
| **P2** | `infrastructure/kubernetes/templates/knowledge-processor-deployment.yaml` | 新建     | 知識處理器部署模板 |
| **P2** | `infrastructure/kubernetes/templates/neo4j-statefulset.yaml`              | 新建     | Neo4j 部署模板     |
| **P2** | `infrastructure/kubernetes/templates/redis-cluster-config.yaml`           | 新建     | Redis 集群配置     |

**詳細行動**:

```bash
# P2-1.1: 創建知識處理器部署模板
CREATE infrastructure/kubernetes/templates/knowledge-processor-deployment.yaml
內容來源: _legacy_scratch/README.md (Lines 132-243)
抽象內容: Deployment, Service, ConfigMap, Secret
參數化: 使用 Helm values 或 Kustomize overlays
移除: 硬編碼的 image digest 和 secret keys

# P2-1.2: 創建 Neo4j StatefulSet 模板
CREATE infrastructure/kubernetes/templates/neo4j-statefulset.yaml
內容來源: _legacy_scratch/README.md (Lines 115-119)
抽象內容: StatefulSet, PVC, Headless Service
配置: 3-replica cluster, persistent storage

# P2-1.3: 創建 Redis 集群配置
CREATE infrastructure/kubernetes/templates/redis-cluster-config.yaml
內容來源: _legacy_scratch/README.md (Lines 121-124)
抽象內容: Redis Cluster ConfigMap, StatefulSet
配置: LRU eviction policy, 1h TTL
```

**預估時間**: 6-8 小時  
**驗收標準**:

- ✅ 所有模板通過 `kubectl apply --dry-run=client`
- ✅ 模板通過 `kubeval` 或 `kubeconform` 驗證
- ✅ 模板包含 README 說明如何使用

---

#### P2-2: 知識庫目錄創建 (Knowledge Base Directories)

| 優先級 | 目標檔案路徑                                                   | 動作類型 | 簡短理由          |
| ------ | -------------------------------------------------------------- | -------- | ----------------- |
| **P2** | `knowledge/processing-workflows/kg-construction-workflow.yaml` | 新建     | KG 構建工作流定義 |
| **P2** | `knowledge/semantic-patterns/relation-patterns.json`           | 新建     | 關係模式庫        |
| **P2** | `knowledge/entity-resolution-rules/similarity-rules.yaml`      | 新建     | 實體解析規則      |

**詳細行動**:

```bash
# P2-2.1: 創建 KG 構建工作流
CREATE knowledge/processing-workflows/kg-construction-workflow.yaml
內容來源: _legacy_scratch/README.md (Lines 83-112: processing_pipeline)
抽象內容: 工作流 DAG、階段依賴、輸入輸出
格式: 使用 Argo Workflows 或自定義 YAML 格式

# P2-2.2: 創建關係模式庫
CREATE knowledge/semantic-patterns/relation-patterns.json
內容來源: _legacy_scratch/README.md (Lines 267-273: rule_patterns)
抽象內容: (SUBJECT) (PREDICATE) (OBJECT) 模式
擴展: 添加更多領域特定模式

# P2-2.3: 創建實體解析規則
CREATE knowledge/entity-resolution-rules/similarity-rules.yaml
內容來源: _legacy_scratch/README.md (Lines 281-292: similarity_metrics)
抽象內容: Jaccard, Levenshtein, Cosine 相似度配置
擴展: 添加領域特定解析規則
```

**預估時間**: 5-6 小時  
**驗收標準**:

- ✅ 工作流通過驗證器驗證
- ✅ 模式庫包含至少 10 個示例模式
- ✅ 規則庫包含完整的註釋說明

---

#### P2-3: CI/CD 集成 (CI/CD Integration)

| 優先級 | 目標檔案路徑                                                 | 動作類型 | 簡短理由             |
| ------ | ------------------------------------------------------------ | -------- | -------------------- |
| **P2** | `.github/workflows/knowledge-processing-ci.yml`              | 新建     | 知識處理 CI workflow |
| **P2** | `docs/refactor_playbooks/03_refactor/meta/CI_INTEGRATION.md` | 擴展     | 添加插件驗證 CI 說明 |

**詳細行動**:

```bash
# P2-3.1: 創建知識處理 CI workflow
CREATE .github/workflows/knowledge-processing-ci.yml
功能:
  - 驗證插件規範（tools/validate-plugin-spec.py）
  - 運行三元組質量測試
  - 檢查本體一致性（tools/validate-ontology.py）
  - 性能基準測試
觸發: PR 修改 config/templates/, knowledge/, governance/schemas/

# P2-3.2: 擴展 CI 集成文檔
EXTEND docs/refactor_playbooks/03_refactor/meta/CI_INTEGRATION.md
添加章節: "Knowledge Processing Plugin CI"
內容: workflow 說明、驗證步驟、失敗處理
```

**預估時間**: 4-5 小時  
**驗收標準**:

- ✅ Workflow 在測試 PR 中成功運行
- ✅ Workflow 正確檢測到插件規範錯誤
- ✅ CI_INTEGRATION.md 更新完成

---

#### P2-4: 性能測試與文檔 (Performance Testing & Docs)

| 優先級 | 目標檔案路徑                                                               | 動作類型 | 簡短理由         |
| ------ | -------------------------------------------------------------------------- | -------- | ---------------- |
| **P2** | `tools/benchmark-knowledge-processor.py`                                   | 新建     | 性能基準測試工具 |
| **P2** | `docs/refactor_playbooks/03_refactor/meta/PLUGIN_ARCHITECTURE_EXAMPLES.md` | 新建     | 插件架構示例     |

**詳細行動**:

```bash
# P2-4.1: 創建性能基準測試工具
CREATE tools/benchmark-knowledge-processor.py
功能:
  - 測試 triple 提取速率（目標: >= 1000/min）
  - 測試處理延遲（目標: P95 <= 30s）
  - 測試內存使用（目標: <= 100MB/doc）
  - 生成性能報告（JSON/Markdown 格式）
使用: 生成測試數據集、模擬處理流程

# P2-4.2: 創建插件架構示例文檔
CREATE docs/refactor_playbooks/03_refactor/meta/PLUGIN_ARCHITECTURE_EXAMPLES.md
內容:
  - 完整插件規範示例
  - 最小插件示例
  - 插件依賴管理示例
  - 插件 CI/CD 集成示例
```

**預估時間**: 6-8 小時  
**驗收標準**:

- ✅ 基準測試工具能成功運行
- ✅ 基準測試報告格式清晰
- ✅ 示例文檔包含至少 3 個完整示例

---

#### P2-5: 治理規則補充 (Additional Governance Policies)

| 優先級 | 目標檔案路徑                                          | 動作類型 | 簡短理由              |
| ------ | ----------------------------------------------------- | -------- | --------------------- |
| **P2** | `governance/policies/compliance-attestation.yaml`     | 新建     | 語義 Web 標準合規聲明 |
| **P2** | `governance/policies/knowledge-processing-rules.yaml` | 新建     | 知識處理質量規則      |

**詳細行動**:

```bash
# P2-5.1: 創建合規聲明策略
CREATE governance/policies/compliance-attestation.yaml
內容來源: _legacy_scratch/README.md (Lines 538-552)
抽象內容: RDF 1.1, OWL 2, SPARQL 1.1 合規
添加: 數據治理、審計日誌、版權尊重

# P2-5.2: 創建知識處理規則
CREATE governance/policies/knowledge-processing-rules.yaml
內容來源: _legacy_scratch/README.md (Lines 318-327)
抽象內容: 三元組驗證、信心評分、質量控制
對齊: governance/policies/plugin-quality-gates.yaml
```

**預估時間**: 3-4 小時  
**驗收標準**:

- ✅ 策略通過 `yamllint` 驗證
- ✅ 策略在 `governance/policies/README.md` 中註冊
- ✅ 策略包含完整的註釋說明

---

#### P2-6: 擴展現有工具 (Extend Existing Tools)

| 優先級 | 目標檔案路徑                                             | 動作類型 | 簡短理由               |
| ------ | -------------------------------------------------------- | -------- | ---------------------- |
| **P2** | `tools/ai-auto-fix.py`                                   | 擴展     | 添加三元組質量分析功能 |
| **P2** | `docs/refactor_playbooks/03_refactor/meta/AI_PROMPTS.md` | 擴展     | 添加 KG 相關 AI 提示   |

**詳細行動**:

```bash
# P2-6.1: 擴展 AI 自動修復工具
EXTEND tools/ai-auto-fix.py
添加功能:
  - analyze_triple_quality(): 分析三元組一致性
  - detect_entity_duplicates(): 檢測重複實體
  - suggest_ontology_improvements(): 建議本體改進
集成: 使用 knowledge/semantic-patterns/

# P2-6.2: 擴展 AI 提示文檔
EXTEND docs/refactor_playbooks/03_refactor/meta/AI_PROMPTS.md
添加章節: "Knowledge Graph Construction Prompts"
內容:
  - 實體提取提示模板
  - 關係分類提示模板
  - 本體構建提示模板
  - 質量評估提示模板
```

**預估時間**: 5-6 小時  
**驗收標準**:

- ✅ 新功能通過單元測試
- ✅ AI 提示模板可直接使用
- ✅ 文檔包含使用示例

---

## 📋 3. 行動清單總結 (Action Summary)

### 3.1 按文件操作類型統計 (By Operation Type)

| 操作類型                 | 數量 | P0  | P1  | P2  |
| ------------------------ | ---- | --- | --- | --- |
| **新建 (CREATE)**        | 23   | 7   | 9   | 7   |
| **擴展 (EXTEND)**        | 4    | 1   | 0   | 3   |
| **移動 (MOVE)**          | 0    | 0   | 0   | 0   |
| **刪除 (DELETE)**        | 0    | 0   | 0   | 0   |
| **標記棄用 (DEPRECATE)** | 1    | 0   | 0   | 1   |
| **總計**                 | 28   | 8   | 9   | 11  |

### 3.2 按目錄統計 (By Directory)

| 目錄                                        | 新建文件數 | 擴展文件數 |
| ------------------------------------------- | ---------- | ---------- |
| `docs/ARCHITECTURE/`                        | 5          | 0          |
| `docs/refactor_playbooks/03_refactor/meta/` | 1          | 2          |
| `config/templates/`                         | 1          | 0          |
| `config/ai-models/`                         | 1          | 0          |
| `config/processing/`                        | 1          | 0          |
| `config/quality/`                           | 1          | 0          |
| `config/kubernetes/`                        | 1          | 0          |
| `config/` (root)                            | 0          | 1          |
| `governance/schemas/`                       | 1          | 0          |
| `governance/policies/`                      | 5          | 0          |
| `infrastructure/kubernetes/templates/`      | 5          | 0          |
| `knowledge/processing-workflows/`           | 1          | 0          |
| `knowledge/semantic-patterns/`              | 2          | 0          |
| `knowledge/entity-resolution-rules/`        | 1          | 0          |
| `tools/`                                    | 3          | 1          |
| `tools/cli/`                                | 1          | 0          |
| `.github/workflows/`                        | 1          | 0          |

### 3.3 工作量估算 (Effort Estimation)

| 優先級   | 任務數           | 預估時間（小時） | 預估時間（人天） |
| -------- | ---------------- | ---------------- | ---------------- |
| **P0**   | 3 組（8 文件）   | 11-15            | 1.5-2 天         |
| **P1**   | 4 組（9 文件）   | 20-26            | 2.5-3.5 天       |
| **P2**   | 6 組（11 文件）  | 29-37            | 3.5-5 天         |
| **總計** | 13 組（28 文件） | 60-78            | 7.5-10 天        |

註：以 8 小時工作日計算

---

## 🗺️ 4. legacy_scratch 清理計畫 (Legacy Scratch Cleanup Plan)

### 4.1 清理條件 (Cleanup Conditions)

#### 階段 1: P0 完成後（立即可清理）

```yaml
可清理內容:
  - ✅ 架構概念（已遷移到 docs/ARCHITECTURE/）
  - ✅ 插件規範結構（已遷移到 governance/schemas/）
  - ✅ 質量門檻（已遷移到 governance/policies/）

清理操作:
  - 在 _legacy_scratch/README.md 頂部添加棄用警告:
    "⚠️ DEPRECATED: 本文檔內容已遷移到正式位置，請參考：
     - 架構文檔: docs/ARCHITECTURE/
     - 配置模板: config/templates/
     - 治理規則: governance/policies/ & schemas/
     詳細映射請參考: docs/refactor_playbooks/03_refactor/kg-builder_refactor.md"
```

#### 階段 2: P1 完成後（可部分清理）

```yaml
可清理內容:
  - ✅ 處理管線配置（已遷移到 config/processing/）
  - ✅ 向量嵌入策略（已遷移到 config/ai-models/）
  - ✅ 工具與腳本概念（已實現為 tools/*.py）

清理操作:
  - 在 _legacy_scratch/README.md 添加遷移完成章節列表
  - 創建 _legacy_scratch/MIGRATION_COMPLETE.md 記錄遷移歷史
```

#### 階段 3: P2 完成後（完全標記為歷史）

```yaml
可清理內容:
  - ✅ Kubernetes 部署配置（已遷移到 infrastructure/kubernetes/）
  - ✅ 知識處理工作流（已遷移到 knowledge/processing-workflows/）
  - ✅ 所有可復用內容（已完全整合）

清理操作:
  - 將 _legacy_scratch/README.md 移至
    _legacy_scratch/ARCHIVED_kg-builder-spec.yaml
  - 創建 _legacy_scratch/README.md 僅包含歷史說明與遷移指引
  - 在 .gitattributes 標記為 linguist-documentation
```

### 4.2 永久保留內容 (Permanent Retention)

```yaml
保留理由:
  - 📜 歷史追溯: 保留原始規範以供未來參考
  - 🔍 變更審計: Git 歷史記錄整合前的完整狀態
  - 📚 學習資源: 作為插件規範設計的示例

保留位置:
  - _legacy_scratch/ARCHIVED_kg-builder-spec.yaml (原始內容)
  - _legacy_scratch/MIGRATION_COMPLETE.md (遷移記錄)
  - _legacy_scratch/README.md (歷史說明)

文件大小: ~56KB (可接受)
```

### 4.3 清理驗證檢查清單 (Cleanup Verification Checklist)

```yaml
清理前驗證:
  - ✅ 所有 P0/P1/P2 行動項目已完成
  - ✅ 所有新建文件已通過 CI 驗證
  - ✅ DOCUMENTATION_INDEX.md 已更新
  - ✅ config/system-module-map.yaml 已更新
  - ✅ 無破壞性變更引入

清理後驗證:
  - ✅ _legacy_scratch/README.md 包含棄用警告
  - ✅ 所有引用已更新（無指向 legacy_scratch 的內部鏈接）
  - ✅ Git 歷史保留完整
  - ✅ 清理操作記錄在 CHANGELOG.md
```

---

## 🎯 5. 驗收條件與成功指標 (Acceptance Criteria & Success Metrics)

### 5.1 功能性驗收 (Functional Acceptance)

| 驗收項            | 標準                           | 驗證方法                                                                                 |
| ----------------- | ------------------------------ | ---------------------------------------------------------------------------------------- |
| **文檔完整性**    | 所有 P0/P1 架構文檔創建完成    | 檢查 docs/ARCHITECTURE/ 目錄                                                             |
| **配置有效性**    | 所有 YAML 配置通過語法驗證     | 運行 `yamllint config/`                                                                  |
| **Schema 正確性** | JSON Schema 能正確驗證示例規範 | 運行 `tools/validate-plugin-spec.py config/templates/plugin-specification-template.yaml` |
| **工具可用性**    | 所有驗證工具可執行並通過測試   | 運行 `pytest tools/tests/`                                                               |
| **CLI 功能性**    | 插件註冊 CLI 所有命令可用      | 運行 `python tools/cli/plugin-registry-cli.py --help`                                    |

### 5.2 質量性驗收 (Quality Acceptance)

| 質量指標                     | 門檻            | 當前狀態 |
| ---------------------------- | --------------- | -------- |
| **Markdown Lint**            | 0 errors        | 待驗證   |
| **YAML Lint**                | 0 errors        | 待驗證   |
| **Python Lint (Pylint)**     | >= 8.0/10       | 待驗證   |
| **Python Type Check (Mypy)** | 0 errors        | 待驗證   |
| **Test Coverage**            | >= 70%          | 待驗證   |
| **Semgrep HIGH**             | 0 violations    | 待驗證   |
| **Semgrep MEDIUM**           | <= 5 violations | 待驗證   |

### 5.3 整合性驗收 (Integration Acceptance)

| 整合項           | 標準                                               | 驗證方法                                                                      |
| ---------------- | -------------------------------------------------- | ----------------------------------------------------------------------------- |
| **模組註冊**     | knowledge_processing 模組在 system-module-map.yaml | 檢查 config/system-module-map.yaml                                            |
| **文檔索引**     | 所有新文檔在 DOCUMENTATION_INDEX.md                | 檢查 DOCUMENTATION_INDEX.md                                                   |
| **Schema 引用**  | 插件 Schema 在 governance/schemas/README.md        | 檢查 governance/schemas/README.md                                             |
| **K8s 模板驗證** | 所有模板通過 kubectl dry-run                       | 運行 `kubectl apply --dry-run=client -f infrastructure/kubernetes/templates/` |
| **CI 集成**      | 新 workflow 成功運行                               | 檢查 GitHub Actions 運行結果                                                  |

### 5.4 效能性驗收 (Performance Acceptance)

| 效能指標             | 目標    | 測試方法                                          |
| -------------------- | ------- | ------------------------------------------------- |
| **插件規範驗證速度** | < 1s    | 運行 `time tools/validate-plugin-spec.py <spec>`  |
| **本體驗證速度**     | < 5s    | 運行 `time tools/validate-ontology.py <owl>`      |
| **CLI 響應速度**     | < 500ms | 運行 `time tools/cli/plugin-registry-cli.py list` |

### 5.5 最終驗收檢查清單 (Final Acceptance Checklist)

```yaml
Phase 0:
  準備 - ✅ 解構分析完成 (01_deconstruction/kg-builder_deconstruction.md) - ✅
  集成設計完成 (02_integration/kg-builder_integration.md) - ✅ 重構計畫完成
  (本文檔)

Phase 1:
  P0 執行 - [ ] 3 個架構文檔創建完成 - [ ] 3 個治理規則創建完成 - [ ] 2
  個配置文件創建完成 - [ ] P0 所有驗收標準通過

Phase 2:
  P1 執行 - [ ] 2 個驗證工具創建完成 - [ ] 1 個 CLI 工具創建完成 - [ ] 2
  個架構文檔創建完成 - [ ] 3 個配置文件創建完成 - [ ] P1 所有驗收標準通過

Phase 3:
  P2 執行 - [ ] 5 個 Kubernetes 模板創建完成 - [ ] 3 個知識庫文件創建完成 - [ ]
  1 個 CI workflow 創建完成 - [ ] 2 個文檔擴展完成 - [ ] 2 個治理規則創建完成 -
  [ ] P2 所有驗收標準通過

Phase 4:
  清理與驗證 - [ ] legacy_scratch/README.md 標記棄用 - [ ] MIGRATION_COMPLETE.md
  創建完成 - [ ] DOCUMENTATION_INDEX.md 更新完成 - [ ] CHANGELOG.md 更新完成 - [
  ] 最終回歸測試通過
```

---

## 📊 6. 風險管理與回滾策略 (Risk Management & Rollback Strategy)

### 6.1 風險識別 (Risk Identification)

| 風險類別          | 風險等級 | 影響範圍                      | 緩解措施                     |
| ----------------- | -------- | ----------------------------- | ---------------------------- |
| **配置衝突**      | 🟡 中    | config/system-module-map.yaml | 使用 Git 分支隔離，PR review |
| **Schema 不兼容** | 🟢 低    | governance/schemas/           | 使用語義化版本，向後兼容     |
| **CI 失敗**       | 🟡 中    | .github/workflows/            | 獨立 workflow，不影響現有 CI |
| **文檔過時**      | 🟢 低    | docs/                         | 使用 dead-link checker       |
| **工具缺陷**      | 🟡 中    | tools/                        | 充分單元測試，逐步上線       |

### 6.2 回滾計畫 (Rollback Plan)

#### P0 回滾

```bash
# 如果 P0 出現問題，回滾步驟:
git revert <P0-commit-sha>
# 影響: 移除新建的架構文檔、治理規則、配置模板
# 風險: 無，所有 P0 文件獨立於運行時
```

#### P1 回滾

```bash
# 如果 P1 工具出現缺陷，回滾步驟:
git revert <P1-commit-sha>
# 影響: 移除驗證工具和 CLI 工具
# 風險: 無，工具未集成到關鍵路徑
```

#### P2 回滾

```bash
# 如果 P2 CI 集成出現問題，回滾步驟:
# 1. 禁用新 workflow
git revert <P2-workflow-commit-sha>
# 2. 保留文檔與模板（無運行時影響）
# 影響: 僅 CI workflow 禁用
# 風險: 無，現有 CI 不受影響
```

### 6.3 故障恢復檢查清單 (Failure Recovery Checklist)

```yaml
出現問題時:
  1. [ ] 識別問題範圍（P0/P1/P2 哪個階段） 2. [ ]
  評估影響範圍（文檔/配置/工具/CI） 3. [ ] 決定修復或回滾 4. [ ]
  執行回滾操作（使用 git revert） 5. [ ] 驗證系統恢復正常 6. [ ]
  記錄問題與解決方案 7. [ ] 更新本重構計畫（調整策略）
```

---

## 🔗 7. 依賴與引用 (Dependencies & References)

### 7.1 上游依賴 (Upstream Dependencies)

- `docs/refactor_playbooks/01_deconstruction/kg-builder_deconstruction.md` ✅
- `docs/refactor_playbooks/02_integration/kg-builder_integration.md` ✅
- `config/system-module-map.yaml` (現有)
- `governance/policies/base-policy.yaml` (現有)
- `docs/ARCHITECTURE/` (現有目錄)

### 7.2 下游產出 (Downstream Outputs)

- 28 個新建/擴展文件（詳見行動清單）
- `_legacy_scratch/MIGRATION_COMPLETE.md` (遷移記錄)
- `DOCUMENTATION_INDEX.md` (更新)
- `CHANGELOG.md` (更新)

### 7.3 交叉引用 (Cross-References)

```yaml
文檔引用關係:
  plugin-architecture-pattern.md:
    - 引用: config/templates/plugin-specification-template.yaml
    - 引用: governance/schemas/plugin-specification.schema.json

  knowledge-graph-processing.md:
    - 引用: config/processing/pipeline-config.yaml
    - 引用: knowledge/processing-workflows/kg-construction-workflow.yaml

  storage-architecture.md:
    - 引用: infrastructure/kubernetes/templates/neo4j-statefulset.yaml
    - 引用: infrastructure/kubernetes/templates/redis-cluster-config.yaml
```

---

## 🎬 8. 執行時間表 (Execution Timeline)

### 8.1 理想時間表 (Ideal Timeline)

```
Week 1:
  Day 1-2: P0 執行（架構文檔、治理規則、配置模板）
  Day 3:   P0 驗收與修正
  Day 4-5: P1 執行開始（驗證工具、CLI 工具）

Week 2:
  Day 1-2: P1 執行繼續（架構文檔補充、配置文件）
  Day 3:   P1 驗收與修正
  Day 4-5: P2 執行開始（Kubernetes 模板、知識庫）

Week 3:
  Day 1-2: P2 執行繼續（CI 集成、性能測試）
  Day 3:   P2 驗收與修正
  Day 4:   清理 legacy_scratch
  Day 5:   最終驗收與文檔更新
```

### 8.2 關鍵里程碑 (Key Milestones)

| 里程碑           | 預計完成日期 | 驗收標準                       |
| ---------------- | ------------ | ------------------------------ |
| **M1: P0 完成**  | Day 3        | 8 個 P0 文件創建，通過所有驗證 |
| **M2: P1 完成**  | Week 2 Day 3 | 9 個 P1 文件創建，工具可用     |
| **M3: P2 完成**  | Week 3 Day 3 | 11 個 P2 文件創建，CI 集成成功 |
| **M4: 最終交付** | Week 3 Day 5 | 所有驗收標準通過，文檔更新完成 |

---

## 📚 9. 附錄 (Appendix)

### 9.1 文件創建模板參考 (File Creation Template Reference)

#### 架構文檔模板

```markdown
# [Component Name] Architecture

# [組件名稱] 架構設計

**創建日期**: YYYY-MM-DD **作者**: [Team Name] **狀態**: Draft / Review /
Approved

## 1. 概述 (Overview)

## 2. 架構設計 (Architecture Design)

## 3. 關鍵決策 (Key Decisions)

## 4. 權衡與限制 (Trade-offs & Constraints)

## 5. 替代方案 (Alternatives Considered)

## 6. 安全考量 (Security Considerations)

## 7. 性能考量 (Performance Considerations)

## 8. 運維考量 (Operational Considerations)

## 9. 未來工作 (Future Work)

## 10. 參考資料 (References)
```

#### 治理策略模板

```yaml
# ===================================================================
# [Policy Name]
# [策略名稱]
# ===================================================================

policy_metadata:
  id: '[policy-id]'
  version: '1.0.0'
  created_date: 'YYYY-MM-DD'
  last_updated: 'YYYY-MM-DD'
  status: 'active' # active / draft / deprecated
  enforcement_level: 'mandatory' # mandatory / recommended / optional

policy_scope:
  applies_to: []
  excludes: []

policy_rules: {}

enforcement:
  validation_method: ''
  ci_integration: true
  violation_severity: '' # critical / high / medium / low

compliance:
  standards: []
  certifications: []

exceptions:
  allowed_exceptions: []
  approval_required: true
```

### 9.2 工具腳本模板參考 (Tool Script Template Reference)

```python
#!/usr/bin/env python3
"""
[Tool Name] - [Brief Description]

Usage:
    python [tool-name].py [options]

Example:
    python [tool-name].py --input file.yaml
"""

import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, help='Input file path')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Tool logic here
    logger.info(f"Processing {args.input}...")

if __name__ == '__main__':
    main()
```

### 9.3 Kubernetes 模板參考 (Kubernetes Template Reference)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: { { .ComponentName } }
  namespace: { { .Namespace | default "default" } }
  labels:
    app: { { .ComponentName } }
    version: { { .Version } }
  annotations:
    description: { { .Description } }
spec:
  replicas: { { .Replicas | default 3 } }
  selector:
    matchLabels:
      app: { { .ComponentName } }
  template:
    metadata:
      labels:
        app: { { .ComponentName } }
    spec:
      containers:
        - name: { { .ComponentName } }
          image: { { .Image } }
          ports:
            - containerPort: { { .Port } }
          resources:
            requests:
              cpu: { { .ResourceRequests.CPU } }
              memory: { { .ResourceRequests.Memory } }
            limits:
              cpu: { { .ResourceLimits.CPU } }
              memory: { { .ResourceLimits.Memory } }
```

---

## 🎯 10. 總結 (Conclusion)

本重構計畫提供了從 `_legacy_scratch/README.md` 到 Unmanned
Island 系統正式結構的完整遷移路徑。透過 P0/P1/P2 三級優先順序，確保關鍵內容優先遷移，同時保持系統穩定性。

### 關鍵成功因素 (Key Success Factors)

1. ✅ **最小變更原則**: 所有變更向後兼容，無破壞性變更
2. ✅ **充分測試**: 每個階段都有明確的驗收標準
3. ✅ **可回滾性**: 每個階段都有獨立的回滾計畫
4. ✅ **文檔優先**: 先建立文檔與規範，再實現工具與基礎設施
5. ✅ **持續驗證**: 通過 CI/CD 持續驗證整合結果

### 下一步行動 (Next Actions)

1. ⏭️ **審查重構計畫**: 團隊 review 本文檔，確認可行性
2. ⏭️ **創建執行分支**: 創建 `refactor/kg-builder-integration` 分支
3. ⏭️ **開始 P0 執行**: 按照 P0-1, P0-2, P0-3 順序執行
4. ⏭️ **持續集成驗證**: 每完成一個 P0 任務，立即 commit 並驗證

---

**重構計畫完成時間 (Refactor Plan Completed)**: 2025-12-07T10:19:24Z  
**前置文檔 (Previous)**:

- `01_deconstruction/kg-builder_deconstruction.md` ✅
- `02_integration/kg-builder_integration.md` ✅  
  **執行狀態 (Execution Status)**: ⏳ Ready for P0 Execution  
  **總體狀態 (Overall Status)**: ✅ Refactor Planning Complete - Awaiting
  Execution Approval
