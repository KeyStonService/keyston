# 治理決策層 (Governance Layer)

## 概述

治理決策層是 DAR-First 架構的**第一層**，負責定義「目標」和「約束」。所有 DAR 推理都基於這一層的規則和索引。

## 核心文件

### 1. index.json - 全局治理索引

這是知識庫的「心臟」，記錄所有 artifacts 及其治理元數據。

**用途：**

- DAR 讀取全局狀態
- 向量索引層獲取向量 ID
- RAG 獲取上下文和標籤

**關鍵字段：**

- `artifacts[]`: 所有資產列表
- `governance_dag`: 治理關係圖
- `statistics`: 統計信息

### 2. dag.graphml - 治理 DAG

定義資源之間的治理關係（誰管誰、誰依賴誰）。

**用途：**

- 檢測循環依賴
- 分析影響範圍
- 可視化治理結構

**關係類型：**

- `governs`: 治理關係（policy → artifact）
- `depends_on`: 依賴關係
- `defines`: 定義關係
- `relates_to`: 關聯關係

### 3. policies.rego - 合規規則

所有 OPA 策略的聚合文件（引用自 `../../policy.rego`）。

**包含：**

- 命名規範
- 元數據完整性
- 血緣完整性
- 溯源要求

### 4. trust-chain.json - 證據鏈

記錄所有治理事件的審計軌跡。

**用途：**

- 完整的審計追蹤
- 合規證據
- 事件溯源

## 使用示例

### 查詢 Artifact 治理信息

```bash
# 查詢特定 artifact
jq '.artifacts[] | select(.id == "schema:entity-base")' index.json

# 查詢所有 policy
jq '.artifacts[] | select(.type == "policy")' index.json

# 統計信息
jq '.statistics' index.json
```

### 分析治理 DAG

```bash
# 使用 Python NetworkX 分析
python3 << 'EOF'
import networkx as nx

G = nx.read_graphml('dag.graphml')
print(f"Nodes: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")

# 檢測循環
try:
    cycles = list(nx.simple_cycles(G))
    if cycles:
        print(f"⚠️ Cycles detected: {cycles}")
    else:
        print("✅ No cycles (valid DAG)")
except:
    print("✅ No cycles (valid DAG)")
EOF
```

### 查詢審計軌跡

```bash
# 最近的審計事件
jq '.trust_chain | sort_by(.timestamp) | reverse | .[0:5]' trust-chain.json

# 特定類型的事件
jq '.trust_chain[] | select(.event_type == "policy_enforced")' trust-chain.json
```

## 與其他層的集成

- **→ Reasoning Layer**: 提供治理規則和約束
- **→ Retrieval Layer**: 提供 artifact 索引供向量化
- **→ Artifacts Layer**: 治理所有資產
- **→ Automation Layer**: 觸發自動化任務

## 維護指南

### 更新 index.json

每次添加新 artifact 時：

1. 添加 artifact 記錄
2. 更新 `governance_dag`
3. 更新 `statistics`
4. 記錄到 `trust-chain.json`

### 更新 DAG

每次修改依賴關係時：

1. 更新 `dag.graphml`
2. 驗證無循環依賴
3. 同步更新 `index.json`

---

**版本**: 1.0.0  
**維護者**: governance-bot  
**最後更新**: 2025-12-19
