# DAR-First 知識庫架構 (DAR-First Knowledge Base Architecture)

## 核心洞察：從「資產索引」到「治理宇宙」

本文檔定義 **DAR-first** (Decision, Action, Reasoning) 知識庫架構，將知識庫從傳統的「資產中心」重新定位為「治理中心」。

### 架構演進

```
舊思路：schema → graph → inference → policy → ...（線性堆積）
新思路：governance（決策層） ← DAR（推理層） ← [RAG + Vector + 結構索引]（工具層）
```

---

## 🏗️ 五層架構（治理優先）

### 層級概覽

| 層級 | 目錄 | 職責 | 優先級原因 |
|------|------|------|-----------|
| **1** | `governance/` | 決策、規則、信任 | DAR 的「目標」和「約束」都在這裡 |
| **2** | `reasoning/` | DAR 任務、推理規則 | DAR 的「大腦」—— 知道怎麼推理 |
| **3** | `retrieval/` | 向量索引、RAG 配置 | DAR 的「工具」—— 用來查資料、生文本 |
| **4** | `artifacts/` | schema、config、模型 | 被 DAR 治理的「對象」 |
| **5** | `automation/` | 事件、守護欄、回滾 | DAR 輸出的「執行層」 |

---

## 📁 完整目錄結構

```
src/governance/dimensions/99-metadata/
├── knl-pack/                          # Knowledge Pack (DAR-First)
│   │
│   ├── governance/                    ⭐ 層級 1：治理決策層
│   │   ├── index.json                 # 全局治理索引（向量+結構+治理元數據）
│   │   ├── dag.graphml                # 治理 DAG（誰管誰、誰依賴誰）
│   │   ├── policies.rego              # 所有合規規則
│   │   ├── trust-chain.json           # 證據鏈 + 審計
│   │   └── README.md                  # 治理層說明
│   │
│   ├── reasoning/                     ⭐ 層級 2：DAR 推理層
│   │   ├── dar-protocol.json          # DAR 任務定義 & 工具清單
│   │   ├── tasks/                     # 推理任務模板
│   │   │   ├── diagnose.yaml          # 診斷：缺陷、不一致、drift
│   │   │   ├── refactor.yaml          # 重構：結構優化、命名統一
│   │   │   ├── repair.yaml            # 修復：產生 patch & PR
│   │   │   └── align.yaml             # 對齐：治理合規檢查
│   │   ├── rules/                     # 推理規則庫
│   │   │   ├── structural.rego        # 結構規則（DAG、依賴）
│   │   │   ├── semantic.rego          # 語意規則（一致性、命名）
│   │   │   └── governance.rego        # 治理規則（責任、生命週期）
│   │   └── README.md                  # 推理層說明
│   │
│   ├── retrieval/                     ⭐ 層級 3：RAG + 向量工具層
│   │   ├── vector-index/              # 向量索引（多維度）
│   │   │   ├── content-vectors.db     # 內容向量（文件、說明）
│   │   │   ├── structure-vectors.db   # 結構向量（schema、DAG）
│   │   │   └── governance-vectors.db  # 治理向量（policy、tag）
│   │   ├── rag-config.json            # RAG 提示詞 & 檢索策略
│   │   ├── semantic-search.yaml       # 多模態搜尋規則
│   │   └── README.md                  # 檢索層說明
│   │
│   ├── artifacts/                     ⭐ 層級 4：資料平面（被動層）
│   │   ├── schema/                    # 本體、關係、約束
│   │   ├── config/                    # 推理引擎、模型配置
│   │   ├── models/                    # 評測、基準
│   │   ├── pipelines/                 # 推理流程圖
│   │   ├── cognition/                 # 五層認知配置
│   │   ├── experiments/               # A/B 試驗
│   │   └── README.md                  # 資料層說明
│   │
│   ├── automation/                    ⭐ 層級 5：閉環執行層
│   │   ├── events.yaml                # 事件驅動規則
│   │   ├── guardians.yaml             # 守護欄（pre-flight check）
│   │   ├── rollback.yaml              # 回滾策略
│   │   ├── active-learning.yaml       # 活性學習迴圈
│   │   ├── ci-integration.yaml        # CI/GitOps 鉤子
│   │   └── README.md                  # 執行層說明
│   │
│   ├── state/                         # 系統狀態快照
│   │   └── snapshots/                 # 狀態快照存儲
│   │
│   ├── telemetry/                     # 可觀測性
│   │   ├── metrics.yaml               # 指標定義
│   │   └── dashboards/                # 儀表板配置
│   │
│   ├── traces/                        # 審計軌跡
│   │   └── audit-logs/                # 審計日誌
│   │
│   └── manifest/                      # 資產清單 + 版本
│       └── version-manifest.yaml      # 版本清單
```

---

## 🎯 層級 1：治理決策層 (Governance Layer)

### governance/index.json

這是知識庫的「心臟」。每個 artifact 都掛在這裡，提供全局視圖。

```json
{
  "version": "1.0.0",
  "timestamp": "2025-12-19T10:12:00Z",
  "artifacts": [
    {
      "id": "schema:entity-base",
      "type": "schema",
      "path": "artifacts/schema/entity-base.json",
      "metadata": {
        "owner": "platform-team",
        "domain": "core",
        "lifecycle": "active",
        "compliance": "compliant"
      },
      "vectors": {
        "content_vector_id": "vec_c_12345",
        "structure_vector_id": "vec_s_67890",
        "governance_vector_id": "vec_g_11111"
      },
      "structure": {
        "depends_on": ["schema:constraint-base"],
        "governs": ["config:inference-engine"],
        "mirrors": ["schema:entity-v2"],
        "extends": []
      },
      "governance": {
        "responsible_team": "platform-team",
        "sla": "P1",
        "review_cycle": "quarterly",
        "last_audit": "2025-12-15"
      },
      "rag_context": {
        "summary": "Base entity schema with 12 core attributes",
        "tags": ["foundational", "immutable", "high-impact"]
      }
    },
    {
      "id": "policy:naming-convention",
      "type": "policy",
      "path": "artifacts/governance/policies.rego",
      "metadata": {
        "owner": "governance-team",
        "domain": "governance",
        "lifecycle": "active",
        "compliance": "compliant"
      },
      "vectors": {
        "content_vector_id": "vec_c_22222"
      },
      "structure": {
        "governs": ["schema:*", "config:*"],
        "depends_on": []
      }
    }
  ],
  "governance_dag": {
    "nodes": ["schema:*", "policy:*", "config:*"],
    "edges": [
      {"from": "policy:naming-convention", "to": "schema:*", "type": "governs"}
    ]
  }
}
```

**用途：**
- DAR 讀這個索引 → 知道全局狀態
- 向量索引層用這個 → 知道每個 artifact 的向量 ID
- RAG 用這個 → 知道上下文、所有者、標籤

### governance/dag.graphml

治理 DAG（有向無環圖）定義資源之間的治理關係。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <graph id="GovernanceDAG" edgedefault="directed">
    <!-- Nodes: Artifacts -->
    <node id="policy:naming-convention">
      <data key="type">policy</data>
      <data key="owner">governance-team</data>
    </node>
    <node id="schema:entity-base">
      <data key="type">schema</data>
      <data key="owner">platform-team</data>
    </node>
    
    <!-- Edges: Governance Relationships -->
    <edge source="policy:naming-convention" target="schema:entity-base">
      <data key="relationship">governs</data>
    </edge>
  </graph>
</graphml>
```

---

## 🧠 層級 2：DAR 推理層 (Reasoning Layer)

### reasoning/dar-protocol.json

定義 DAR 能做什麼、怎麼做、產出什麼。

```json
{
  "version": "1.0.0",
  "dar_capabilities": [
    {
      "task_type": "diagnose",
      "description": "偵測結構/語意/治理問題",
      "triggers": [
        "artifact_changed",
        "scheduled_audit",
        "manual_request"
      ],
      "tools": [
        "vector_search",
        "rag_answer",
        "dag_analyzer",
        "policy_checker"
      ],
      "output_format": {
        "type": "object",
        "properties": {
          "issues": {
            "type": "array",
            "items": {
              "severity": "enum(critical, high, medium, low)",
              "type": "enum(missing_metadata, naming_inconsistency, circular_dependency, drift, compliance_violation)",
              "affected_artifacts": "array",
              "evidence": "string"
            }
          }
        }
      }
    },
    {
      "task_type": "repair",
      "description": "產生修復 patch 和 PR",
      "tools": ["rag_answer", "git_patch", "ci_trigger"],
      "output_format": {
        "type": "object",
        "properties": {
          "patches": {
            "type": "array",
            "items": {
              "file": "string",
              "operation": "enum(create, update, delete)",
              "diff": "string",
              "rationale": "string"
            }
          },
          "pr_body": "string",
          "estimated_impact": "string"
        }
      }
    },
    {
      "task_type": "align",
      "description": "檢查治理對齐",
      "tools": ["policy_checker", "rag_answer"],
      "output_format": {
        "type": "object",
        "properties": {
          "alignment_score": "number(0-100)",
          "violations": "array",
          "recommendations": "array"
        }
      }
    }
  ],
  "tool_definitions": {
    "vector_search": {
      "description": "多維度向量搜尋",
      "parameters": {
        "query": "string",
        "dimensions": "enum(content, structure, governance)",
        "top_k": "integer"
      },
      "returns": "array of {artifact_id, similarity_score, context}"
    },
    "rag_answer": {
      "description": "從 context 生成答案/建議",
      "parameters": {
        "question": "string",
        "context": "array of artifacts",
        "style": "enum(technical, executive, patch)"
      }
    },
    "dag_analyzer": {
      "description": "分析治理 DAG 結構",
      "parameters": {
        "check_type": "enum(cycles, orphans, coverage)"
      },
      "returns": "object with {issues, recommendations}"
    },
    "policy_checker": {
      "description": "檢查策略合規性",
      "parameters": {
        "artifact_id": "string",
        "policies": "array"
      },
      "returns": "object with {compliant, violations}"
    },
    "git_patch": {
      "description": "產生 git-compatible patch",
      "parameters": {
        "files": "array",
        "changes": "object"
      }
    }
  }
}
```

### reasoning/tasks/repair.yaml

DAR 執行修復時的具體流程。

```yaml
task_type: repair
name: "Auto-Repair Governance Artifacts"
description: "偵測問題 → 生成 patch → 提交 PR"

steps:
  - step: 1
    name: "Diagnose"
    action: "run_dar_task"
    task_ref: "diagnose"
    output_var: "issues"

  - step: 2
    name: "Retrieve Context"
    action: "vector_search"
    query_template: "For each issue, find similar artifacts and best practices"
    output_var: "context"

  - step: 3
    name: "Generate Patches"
    action: "rag_answer"
    prompt_template: |
      Given these issues: {{ issues }}
      And this context: {{ context }}
      Generate a JSON patch for each affected artifact.
      Format: single-line JSON per patch.
    output_var: "patches"

  - step: 4
    name: "Pre-flight Check"
    action: "guardian_check"
    checks:
      - "no_breaking_changes"
      - "all_policies_compliant"
      - "impact_radius < 50 artifacts"
    output_var: "guardian_pass"

  - step: 5
    name: "Create PR"
    action: "git_patch"
    if: "guardian_pass == true"
    patches: "{{ patches }}"
    pr_template: |
      ## Auto-Repair: {{ issue_summary }}
      
      **Issues Fixed:**
      {{ issues | format_list }}
      
      **Changes:**
      {{ patches | format_diff }}
      
      **Evidence:**
      {{ context | format_evidence }}
    output_var: "pr_url"

  - step: 6
    name: "Audit Log"
    action: "log_to_trust_chain"
    event: "repair_task_completed"
    metadata:
      issues_fixed: "{{ issues | length }}"
      pr_url: "{{ pr_url }}"
      timestamp: "now()"
```

---

## 🔍 層級 3：RAG + 向量工具層 (Retrieval Layer)

### retrieval/rag-config.json

RAG 配置，定義提示詞和檢索策略。

```json
{
  "version": "1.0.0",
  "retrieval_strategy": {
    "default": {
      "method": "hybrid",
      "vector_weight": 0.7,
      "keyword_weight": 0.3,
      "top_k": 10,
      "rerank": true
    },
    "by_task": {
      "diagnose": {
        "method": "vector_only",
        "dimensions": ["structure", "governance"],
        "top_k": 20
      },
      "repair": {
        "method": "hybrid",
        "context_window": 5,
        "include_history": true
      }
    }
  },
  "prompt_templates": {
    "diagnose": {
      "system": "You are a governance expert analyzing artifacts for issues.",
      "user_template": "Analyze {{artifact_id}} for:\n- Naming inconsistencies\n- Missing metadata\n- Policy violations\n\nContext:\n{{context}}"
    },
    "repair": {
      "system": "You are a code repair assistant. Generate minimal, precise patches.",
      "user_template": "Fix these issues:\n{{issues}}\n\nBased on context:\n{{context}}\n\nGenerate patches in JSON format."
    }
  }
}
```

---

## 📦 層級 4：資料平面 (Artifacts Layer)

這一層包含所有被治理的資產：schema、config、models 等。

結構保持現有的 `examples/` 目錄內容，但添加元數據連接到治理索引。

---

## ⚡ 層級 5：閉環執行層 (Automation Layer)

### automation/events.yaml

事件驅動規則定義。

```yaml
version: "1.0.0"
event_handlers:
  - event: "artifact.created"
    triggers:
      - task: "diagnose"
        delay: "immediate"
      - task: "update_governance_index"
        delay: "immediate"
  
  - event: "artifact.updated"
    triggers:
      - task: "diagnose"
        delay: "5m"
      - task: "check_alignment"
        delay: "10m"
  
  - event: "policy.violated"
    triggers:
      - task: "repair"
        condition: "auto_fix_enabled == true"
        delay: "immediate"
      - task: "notify_owner"
        delay: "immediate"
```

### automation/guardians.yaml

守護欄（pre-flight checks）定義。

```yaml
version: "1.0.0"
guardians:
  - name: "no_breaking_changes"
    description: "確保變更不會破壞現有依賴"
    checks:
      - type: "dependency_impact"
        max_affected: 50
      - type: "api_compatibility"
        check_versions: true
  
  - name: "all_policies_compliant"
    description: "所有策略必須合規"
    checks:
      - type: "policy_check"
        policies: ["naming-convention", "metadata-completeness"]
        severity: "error"
  
  - name: "impact_radius"
    description: "變更影響範圍限制"
    checks:
      - type: "radius_check"
        max_artifacts: 50
        max_depth: 3
```

---

## 🚀 實戰場景：自動修復命名不一致

### 完整流程

```
1. 事件觸發：新 schema 上傳
   ↓
2. DAR.diagnose() 執行
   - 讀 governance/index.json
   - 用向量索引找「語意相似」的 schema
   - 檢查命名規則：policy:naming-convention
   - 輸出：[{artifact: "schema:user-entity", issue: "should be UserEntity"}]
   ↓
3. DAR.repair() 執行
   - 用 RAG：「根據命名規則，生成統一的命名方案」
   - 產出 patch：schema:user-entity → schema:UserEntity
   - 更新 governance/index.json 中的 id 和 path
   ↓
4. Guardian 檢查
   - 檢查：有沒有其他地方引用 schema:user-entity？
   - 檢查：修改會不會違反政策？
   ↓
5. 提交 PR
   - 檔案：schema/UserEntity.json（重命名）
   - 檔案：governance/index.json（更新 id）
   - 檔案：governance/dag.graphml（更新引用）
   ↓
6. CI 驗證 + 審計
   - 跑 policy checker
   - 記錄到 trust-chain.json
```

---

## 📊 優先場景建議

| 優先級 | 場景 | 複雜度 | 收益 | 實施建議 |
|-------|------|--------|------|---------|
| 🔴 P0 | 自動補全 metadata（owner、domain、sla） | ⭐ 低 | ⭐⭐⭐ 高 | 先做！最快看到成果 |
| 🟠 P1 | 自動修復命名不一致 | ⭐⭐ 中 | ⭐⭐ 中 | 驗證完整 DAR 流程 |
| 🟡 P2 | 自動偵測治理 DAG 循環 | ⭐⭐⭐ 高 | ⭐ 低 | 結構驗證價值高 |

**建議：先做 P0（metadata 補全）**，因為：

1. 最快看到成果
2. 直接支撐後續的 DAR 推理
3. 可以驗證「向量索引 + RAG + DAR」的完整閉環

---

## 🔗 與 99-metadata 現有結構的整合

DAR-First 架構與現有 99-metadata 維度完全兼容：

- **現有的 `examples/`** → 移至 `knl-pack/artifacts/`
- **現有的 `policy.rego`** → 整合至 `knl-pack/governance/policies.rego`
- **現有的 `schema.json`** → 作為 `knl-pack/artifacts/schema/` 的基礎
- **Living Knowledge Base 4層** → 對應到 DAR 的 governance + reasoning + retrieval 層

---

## 📝 下一步行動

1. **創建 knl-pack/ 目錄結構**
2. **實現 P0 場景**：metadata 自動補全
3. **建立第一個 DAR pipeline**：diagnose → repair → PR
4. **集成向量索引**：使用現有的知識圖譜數據
5. **部署 Guardian 檢查**：確保變更安全

---

**版本**: 1.0.0  
**最後更新**: 2025-12-19  
**維護者**: governance-bot  
**狀態**: 🟢 Active - Ready for Implementation
