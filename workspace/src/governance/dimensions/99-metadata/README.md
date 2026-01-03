# 99-metadata: 元數據管理中心 (Metadata Management Center)

[![URN](https://img.shields.io/badge/URN-urn%3Amachinenativeops%3Agovernance%3Ametadata%3Av1-blue)](.)
[![Layer](https://img.shields.io/badge/Layer-Meta--Specification%20(90--99)-purple)](.)
[![Status](https://img.shields.io/badge/Status-Active-green)](.)

## 概述 (Overview)

元數據管理中心是 MachineNativeOps 治理框架的**元規範層核心組件**，負責整個平台的元數據治理、溯源和生命周期管理，為AI治理和合規提供數據基礎。

本維度整合了**活體知識庫（Living Knowledge Base）**，讓系統具備自我感知、自我建模、自我診斷和自我回饋的能力，實現完整的知識循環。

### 核心目標

1. **元數據治理**: 統一管理技術、業務、操作和治理元數據
2. **數據溯源**: 追蹤數據的來源、變更歷史和傳播路徑
3. **血緣追蹤**: 端到端數據血緣追踪和影響分析
4. **活體知識**: 系統自我感知、建模、診斷和回饋循環

---

## 🧬 活體知識庫 (Living Knowledge Base)

> 讓系統自己感知變化、重建自身結構、自我檢查，並主動回報狀態。

活體知識庫不是AI助理、不是命令列工具、不是Copilot或聊天機器人。它的唯一目的，是讓一個程式碼倉庫**知道自己現在長怎樣、哪裡有問題**，並用**機器可讀的方式**表達出來。

### 📜 合約規範（機器可讀合約）

活體知識庫遵守以下合約：

- ❌ 不是 AI 助理 / Chatbot
- ❌ 不是 CLI 工具，不提供任何命令列參數說明
- ❌ 不主打「AI 程式碼分析」或「程式碼副駕駛」
- ✅ 專注在：**感知 → 建模 → 自我診斷 → 行動** 的知識循環

對應的機器可讀合約會放在：

- `knowledge/contracts/living-knowledge-contract.yaml`

### 🧩 知識庫的四個層次

#### 1. 感知層（Perception Layer）

**回答的問題**: 最近發生了什麼變化？

**資料來源**:

- Git 提交紀錄（新增 / 修改 / 刪除）
- GitHub Actions 工作流結果（成功 / 失敗）
- 定期排程掃描（就算沒人動，也做一次體檢）

**職責**: 只負責觸發後續流程，不做分析

#### 2. 建模層（Modeling Layer）

**回答的問題**: 現在這個系統長什麼樣子？

每次感知到變化後，建模層會重新生成三個機器可讀產物：

1. **`docs/generated-mndoc.yaml`**  
   - 系統「說明書」：名稱、版本、子系統、關鍵文件等

2. **`docs/knowledge-graph.yaml`**  
   - 系統「神經連結圖」：  
     - 節點：系統、子系統、元件、設定、文件、工作流…  
     - 關係：隸屬、依賴、覆蓋範圍、文件連結…

3. **`docs/superroot-entities.yaml`**  
   - 使用 SuperRoot 風格的 ontology 描述：  
     - `Component`（元件）
     - `ConfigParam`（設定）
   - 讓外部治理系統可以直接讀取與推理

#### 3. 自我診斷層（Self-diagnosis Layer）

**回答的問題**: 現在這個系統健康嗎？哪裡有問題？

自我診斷層會基於 `knowledge-graph.yaml` 和 `superroot-entities.yaml` 做檢查：

- **孤兒元件 (Orphan Components)**  
  - 沒有任何工作流負責建置或測試的 Component

- **死設定 (Dead Configs)**  
  - 不再被任何元件使用的 Config

- **重疊工作流 (Overlapping Workflows)**  
  - 負責相同範圍（scope）、屬於相同建置線（lineage_group）的 workflow

- **斷鏈文件 (Broken Links)**  
  - 文檔中指向已不存在路徑的連結

**診斷結果輸出**:

- `docs/knowledge-health-report.yaml` - 機器可讀的健康報告

#### 4. 行動 / 回饋層（Action / Feedback Layer）

**回答的問題**: 發現問題之後，要怎麼讓人類知道？

行動層不直接修改業務程式碼，而是透過以下方式回饋：

- **更新儀表板**  
  - `docs/KNOWLEDGE_HEALTH.md` 或對應 YAML，顯示：  
    - 節點數 / 邊數  
    - 孤兒元件數量  
    - 重疊工作流數量  
    - 斷鏈文件數量  

- **通知維護者**  
  - 在必要情況下，自動建立 GitHub Issue（中文說明問題和建議負責人）

---

## 核心功能 (Core Functions)

### 1. 元數據分類 (Metadata Classification)

元數據按照以下四大類型進行管理：

#### 技術元數據 (Technical Metadata)

- **描述**: 數據源、格式、結構、依賴關係
- **屬性**:
  - `data_source`: 數據來源
  - `format`: 數據格式
  - `schema`: 數據結構
  - `dependencies`: 依賴關係
  - `constraints`: 約束條件

#### 業務元數據 (Business Metadata)

- **描述**: 業務術語、數據所有者、數據質量規則
- **屬性**:
  - `business_terms`: 業務術語
  - `data_owner`: 數據所有者
  - `quality_rules`: 質量規則
  - `criticality`: 重要程度
  - `sensitivity`: 敏感度

#### 操作元數據 (Operational Metadata)

- **描述**: 數據血緣、變更歷史、訪問日誌
- **屬性**:
  - `lineage`: 血緣關係
  - `change_history`: 變更歷史
  - `access_logs`: 訪問日誌
  - `performance_metrics`: 性能指標

#### 治理元數據 (Governance Metadata)

- **描述**: 策略、合規要求、審計記錄
- **屬性**:
  - `policies`: 治理策略
  - `compliance_requirements`: 合規要求
  - `audit_records`: 審計記錄
  - `certification_status`: 認證狀態

### 2. 元數據溯源 (Metadata Provenance)

追蹤元數據的來源、變更歷史和傳播路徑。

#### 溯源配置示例

```yaml
# 數據溯源配置
provenance:
  enabled: true
  sources:
    - type: git
      repository: "https://github.com/org/repo"
      branch: main
    - type: build
      pipeline: "ci-cd-pipeline"
      artifacts:
        - sbom.json
        - attestation.json
    - type: runtime
      events:
        - deployment
        - scaling
        - failure
```

### 3. 元數據血緣 (Data Lineage)

端到端數據血緣追踪、影響分析、變更傳播分析和合規追踪。

#### 血緣追踪配置示例

```yaml
lineage:
  enabled: true
  tracking:
    - source: "data-ingestion"
      target: "data-warehouse"
      transformation: "etl-process"
    - source: "ml-training"
      target: "model-registry"
      transformation: "model-build"
    - source: "api-gateway"
      target: "service-mesh"
      transformation: "request-routing"
```

---

## 目錄結構 (Directory Structure)

### DAR-First 知識庫架構 🆕

99-元數據採用 **DAR-First** (Decision, Action, Reasoning) 架構，將知識庫從「資產中心」重新定位為「治理中心」，並完整整合**活體知識庫（Living Knowledge Base）**的四層架構。

**核心特色：紀錄功能** 📝

- 倉庫一有變動，立刻偵測並同步更新知識圖譜
- 自動找到此次變動的相關內容和高度相關內容
- 完整記錄每次變動，包含影響分析和依賴追蹤

詳細架構文檔請參閱：

- [DAR_FIRST_ARCHITECTURE.md](./DAR_FIRST_ARCHITECTURE.md) - DAR-First 完整架構
- [knl-pack/LIVING_KNOWLEDGE_INTEGRATION.md](./knl-pack/LIVING_KNOWLEDGE_INTEGRATION.md) - 活體知識庫整合說明

```
src/governance/dimensions/99-metadata/
├── knl-pack/                          # Knowledge Pack (DAR-First) 🆕
│   │
│   ├── governance/                    ⭐ 層級 1：治理決策層
│   │   ├── index.json                 # 全局治理索引
│   │   ├── dag.graphml                # 治理 DAG
│   │   ├── policies.rego              # 合規規則
│   │   └── trust-chain.json           # 證據鏈 + 審計
│   │
│   ├── reasoning/                     ⭐ 層級 2：DAR 推理層
│   │   ├── dar-protocol.json          # DAR 任務定義
│   │   ├── tasks/                     # 推理任務模板
│   │   │   ├── diagnose.yaml          # 診斷問題
│   │   │   ├── refactor.yaml          # 結構優化
│   │   │   ├── repair.yaml            # 自動修復
│   │   │   └── align.yaml             # 治理對齊
│   │   └── rules/                     # 推理規則庫
│   │
│   ├── retrieval/                     ⭐ 層級 3：RAG + 向量工具層
│   │   ├── vector-index/              # 多維向量索引
│   │   ├── rag-config.json            # RAG 配置
│   │   └── semantic-search.yaml       # 語義搜尋
│   │
│   ├── artifacts/                     ⭐ 層級 4：資料平面
│   │   ├── schema/                    # 本體、約束
│   │   ├── config/                    # 配置
│   │   ├── models/                    # 模型
│   │   └── pipelines/                 # 流程圖
│   │
│   └── automation/                    ⭐ 層級 5：閉環執行層
│       ├── events.yaml                # 事件驅動規則
│       ├── guardians.yaml             # 守護欄
│       ├── rollback.yaml              # 回滾策略
│       └── ci-integration.yaml        # CI/GitOps 集成
│
├── examples/                          # 使用範例（整合至 artifacts/）
├── tests/                             # OPA 測試
└── README.md                          # 本文檔
```

**五層架構優先級：**

1. **Governance**: 決策、規則、信任鏈（DAR 的目標和約束）
2. **Reasoning**: DAR 任務、推理規則（DAR 的大腦）
3. **Retrieval**: 向量索引、RAG 配置（DAR 的工具）
4. **Artifacts**: Schema、Config、Models（被治理的對象）
5. **Automation**: 事件、守護欄、回滾（DAR 的執行層）

---

## 配置說明 (Configuration)

### 元數據收集配置

```yaml
metadata:
  collection:
    enabled: true
    sources:
      - type: kubernetes
        resources:
          - pods
          - services
          - configmaps
      - type: database
        connection: "postgresql://localhost:5432"
        schemas:
          - public
          - audit
      - type: filesystem
        paths:
          - /src
          - /config
          - /docs
```

### 血緣追踪配置

```yaml
lineage:
  enabled: true
  tracking:
    - source: "data-ingestion"
      target: "data-warehouse"
      transformation: "etl-process"
    - source: "ml-training"
      target: "model-registry"
      transformation: "model-build"
```

---

## 使用指南 (Usage Guide)

### 1. 元數據註冊

```bash
# 註冊新的數據源
./scripts/register-datasource.sh \
  --name "customer-data" \
  --type "postgresql" \
  --owner "data-team" \
  --sensitivity "pii"
```

### 2. 血緣分析

```bash
# 分析數據血緣
./scripts/analyze-lineage.sh \
  --dataset "sales-records" \
  --depth 3
```

### 3. 元數據查詢

```bash
# 查詢元數據
curl -X GET "http://metadata-service/v1/datasets?owner=data-team"
```

### 4. 活體知識庫更新

```bash
# 手動觸發知識庫更新
python knowledge/pipelines/update_knowledge_layer.py

# 查看知識健康報告
cat docs/knowledge-health-report.yaml
```

---

## 最佳實踐 (Best Practices)

### 1. 元數據質量

- ✅ 實施元數據驗證規則
- ✅ 定期進行元數據質量檢查
- ✅ 建立元數據血緣完整性檢查
- ✅ 使用自動化工具維護元數據一致性

### 2. 數據溯源

- ✅ 為所有數據資產建立完整的溯源鏈
- ✅ 記錄數據變更歷史
- ✅ 實施數據血緣可視化
- ✅ 定期審計溯源記錄完整性

### 3. 治理集成

- ✅ 與策略引擎集成
- ✅ 實現自動化的元數據治理
- ✅ 建立元數據驅動的合規檢查
- ✅ 實施持續的元數據監控

### 4. 活體知識庫維護

- ✅ 定期檢查知識圖譜完整性
- ✅ 及時修復孤兒元件和死設定
- ✅ 保持文檔連結的有效性
- ✅ 建立自動化的健康檢查流程

---

## 監控指標 (Monitoring Metrics)

### 元數據覆蓋率

```prometheus
# 元數據收集成功率
metadata_collection_success_rate{source="kubernetes"} 0.98
metadata_collection_success_rate{source="database"} 0.95

# 元數據覆蓋率
metadata_coverage_ratio{classification="technical"} 0.92
metadata_coverage_ratio{classification="business"} 0.85
```

### 血緣完整性

```prometheus
# 血緣完整性比率
lineage_completeness_ratio{dataset="*"} 0.90

# 血緣深度
lineage_depth{dataset="sales-records"} 5
```

### 數據質量指標

```prometheus
# 數據質量得分
data_quality_score{dataset="*", dimension="completeness"} 0.88
data_quality_score{dataset="*", dimension="accuracy"} 0.92
data_quality_score{dataset="*", dimension="consistency"} 0.95
```

### 知識庫健康指標

```prometheus
# 知識庫健康得分
knowledge_health_score 0.87

# 孤兒元件數量
orphan_components_count 3

# 死設定數量
dead_configs_count 5

# 斷鏈文件數量
broken_links_count 2
```

---

## 驗證 (Validation)

### OPA/Rego 驗證

```bash
# 驗證元數據配置
conftest test metadata/ --policy src/governance/dimensions/99-metadata/policy.rego

# 驗證血緣配置
conftest test lineage/ --policy src/governance/dimensions/99-metadata/policy.rego
```

### 快速檢查

```bash
# 檢查元數據完整性
./tools/check-metadata-completeness.sh

# 檢查血緣完整性
./tools/check-lineage-integrity.sh

# 檢查知識庫健康
python knowledge/runtime/diagnose_health.py
```

---

## 依賴關係 (Dependencies)

```yaml
dependencies:
  required:
    - 61-lineage          # 數據血緣追踪基礎
    - 62-provenance       # 數據溯源基礎
    - 07-audit            # 審計記錄
    - 24-registry         # 資源註冊
  optional:
    - 38-sbom             # 軟體物料清單
    - 63-evidence         # 證據收集
    - 64-attestation      # 證明和認證
```

---

## 元規範約束 (Meta-Specification Constraints)

作為元規範層維度，99-metadata：

- ✅ 可被其他維度依賴
- ❌ 不可依賴下游模組（防止循環）
- ✅ 定義元數據管理的基礎標準
- ✅ 提供活體知識庫的實現框架

---

## 相關鏈接 (Related Links)

### 核心架構文檔

- **[DAR-First 架構](./DAR_FIRST_ARCHITECTURE.md)** 🆕 - 完整的 DAR-First 知識庫架構說明
- **[整合指南](./INTEGRATION.md)** - 與其他維度和系統的整合方法
- [活體知識庫設計](/docs/architecture/components/LIVING_KNOWLEDGE_BASE.md) - 架構設計文檔
- [知識庫文檔](/docs/LIVING_KNOWLEDGE_BASE.md) - 詳細文檔

### 相關治理維度

- [數據治理框架](../10-policy/README.md) - 策略管理中心
- [血緣治理](../61-lineage/README.md) - 血緣追踪維度
- [溯源治理](../62-provenance/README.md) - 溯源管理維度
- [審計軌跡](../70-audit-trail/README.md) - 審計追踪維度

### DAR 實戰場景

- **P0 優先**: 自動補全 metadata（owner、domain、sla）- 最快見效
- **P1 推薦**: 自動修復命名不一致 - 驗證完整 DAR 流程
- **P2 進階**: 自動偵測治理 DAG 循環 - 結構驗證

---

## ⚠️ 明確排除的範圍 (Explicitly Excluded Scope)

本維度刻意**不**提供：

- ❌ 命令列工具（CLI）介面與參數說明
- ❌ Chatbot / Copilot / AI 助理式互動
- ❌ 「AI 驅動程式碼分析工具」的產品功能描述

如果未來需要這些能力，會以「外部系統」的方式接入，而不是混進元數據管理中心的核心設計中。

---

## 版本信息 (Version Information)

- **當前版本**: 1.0.0
- **建立日期**: 2025-12-19
- **URN**: `urn:machinenativeops:governance:metadata:v1`
- **狀態**: Active

---

## 貢獻指南 (Contributing)

如需為元數據管理中心貢獻代碼或文檔，請遵循以下原則：

1. 保持機器可讀性優先
2. 遵循 99-naming-convention 命名規範
3. 確保所有變更都有對應的測試
4. 更新相關的文檔和示例
5. 通過所有 OPA 策略驗證

---

**文檔生成時間**: 2025-12-19  
**維護者**: governance-bot  
**聯繫方式**: 通過 GitHub Issue 或 PR 與我們聯繫
