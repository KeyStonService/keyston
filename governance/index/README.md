# Governance Index System

> **治理閉環的入口** - 機器讀取即可立即啟動，無需等待，無需人工介入

## 🚀 即時可用 (Immediate Ready)

這個 Index 系統是**完整的生產系統**，不是藍圖或計畫：

| 傳統思維 ❌ | 本系統 ✅ |
|------------|----------|
| 短期/中期/長期 | **現在就能用** |
| `execution: optional` | `execution: required` |
| 分階段交付 | **即時完整** |
| RAG 是「未來」 | **RAG 現在可用** |
| 向量是「計畫」 | **向量已生成** |
| 代理失憶 | **事件持久化** |

---

## 🧠 事件持久化系統 (解決代理失憶)

### 問題
每個代理在新對話框裡像「失憶症患者」，因為沒有持續的上下文索引。

### 解決方案

```
events/
├── registry.json        # 事件索引 - 代理必讀
├── current-session.json # 當前會話 - 共享記憶
├── vector-index.json    # 事件向量 - 語意檢索
├── bootstrap-contract.json # 入口協定 - 強制讀取
├── logs/                # 日誌存儲
└── compressed/          # 壓縮事件
```

### Bootstrap Contract (入口協定)

所有代理啟動前**必須**：
1. 讀取 `events/registry.json` - 獲取事件索引
2. 讀取 `events/current-session.json` - 獲取當前上下文
3. 讀取 `events/vector-index.json` - 獲取向量檢索
4. 寫入產生的事件到 session

```bash
# 代理啟動時執行 bootstrap
python index/scripts/event-writer.py bootstrap
# 輸出: ✓ Bootstrap complete! Context injected. Agent ready to execute.
```

### 事件 DAG (因果關係)

事件不再無限堆疊，而是形成閉環：

```
policy.created → policy.validated → policy.enforced → audit.logged
                                                           ↓
                                                    feedback.collected
                                                           ↓
                                                    (閉環回到 policy.created)
```

---

## 📂 Index 的核心功能

### 1. 治理地圖 (Governance Map)
Index 是整個系統的「**單一真相來源 (SSOT)**」。機器讀取 Index 就能立即知道如何組合和執行。

### 2. 依賴解析 (Dependency Resolution)
81 個維度的 **DAG (Directed Acyclic Graph)** 已驗證無循環依賴，可直接用於拓撲排序。

### 3. 策略執行 (Execution Control)
所有維度標記為 `execution: required`，沒有「可選」的概念 — 存在即必須運作。

### 4. 合規與審計 (Compliance & Audit)
六大合規框架 (ISO-42001, NIST-AI-RMF, EU-AI-Act, SLSA, SOX, GDPR) 已完整映射。

### 5. 事件驅動 (Event-driven)
`trigger → event → agent` 配置完整，延遲限制 (<=30s) 已定義。

### 6. RAG 檢索 (Immediate)
向量嵌入**已生成**，語意搜尋**現在可用**。

### 7. 事件持久化 (Memory)
所有事件**持久化存儲**，代理**不會失憶**。

---

## 📁 目錄結構

```
governance/
├── governance-index.json      # Root SSOT - 立即可用
└── index/
    ├── README.md              # 本文件
    ├── dimensions.json        # 81 維度 DAG - 已驗證
    ├── shared.json            # 橫切資源 - 生產就緒
    ├── compliance.json        # 合規映射 - 完整
    ├── events.json            # 事件驅動配置
    ├── tech-debt.json         # 債務追蹤 - 運作中
    ├── vectors.json           # 向量索引 - 嵌入已生成
    ├── observability.json     # 觀測配置 - 完整
    ├── events/                # 事件持久化系統 ← 新增
    │   ├── registry.json      # 事件索引
    │   ├── current-session.json # 當前會話
    │   ├── vector-index.json  # 事件向量
    │   └── bootstrap-contract.json # 入口協定
    └── scripts/
        ├── rag-query.py           # RAG 查詢 - 立即可用
        ├── index-validator.py     # DAG 驗證 - 生產工具
        ├── generate-embeddings.py # 嵌入生成器
        └── event-writer.py        # 事件寫入器 ← 新增
```

---

## 🛠️ 立即使用

### 事件系統 (新增)

```bash
# 代理啟動 - 載入事件上下文
python governance/index/scripts/event-writer.py bootstrap

# 寫入事件
python governance/index/scripts/event-writer.py write \
  --type "policy.created" \
  --data '{"policy": "security-policy-001"}' \
  --source "my-agent"

# 查詢事件
python governance/index/scripts/event-writer.py query "security"

# 壓縮舊事件
python governance/index/scripts/event-writer.py compress --threshold 100

# 關閉事件迴圈
python governance/index/scripts/event-writer.py close-loop \
  --start evt-001 --end evt-002 --type policy-flow
```

### RAG 查詢

```bash
# 語意搜尋
python governance/index/scripts/rag-query.py "security policies"

# 互動模式
python governance/index/scripts/rag-query.py --interactive
```

### 驗證 Index

```bash
python governance/index/scripts/index-validator.py
# 輸出: ✓ All validations passed! Index is ready for use.
```

---

## 🔄 七層治理閉環 (含事件層)

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  [EVENTS] ──► 事件持久化 (所有代理必須先讀取)                 │
│      │                                                      │
│      ▼                                                      │
│    10-policy ──► 20-intent ──► 30-agents ──► 39-automation │
│         ▲                                        │          │
│         │                                        ▼          │
│         │              40-self-healing ◄─────────┘          │
│         │                     │                             │
│         │                     ▼                             │
│         │              60-contracts                         │
│         │                     │                             │
│         │                     ▼                             │
│         │               70-audit ──► [EVENT LOGGED]         │
│         │                     │                             │
│         │                     ▼                             │
│         └──────────── 80-feedback                           │
│                    (閉環回到 10-policy)                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 索引檔案狀態

| 檔案 | 狀態 | 說明 |
|------|------|------|
| `governance-index.json` | ✅ Production | Root SSOT |
| `dimensions.json` | ✅ Production | 81 維度 DAG，無循環 |
| `shared.json` | ✅ Production | 8 個共享資源 (含 events) |
| `compliance.json` | ✅ Production | 6 個合規框架 |
| `events.json` | ✅ Production | 8 類事件，32+ 事件定義 |
| `tech-debt.json` | ✅ Production | 債務追蹤，CI 閘門就緒 |
| `vectors.json` | ✅ Production | 嵌入已生成，RAG 可用 |
| `observability.json` | ✅ Production | 指標、SLO、告警 |
| `events/registry.json` | ✅ Production | 事件索引 |
| `events/current-session.json` | ✅ Production | 當前會話上下文 |
| `events/vector-index.json` | ✅ Production | 事件向量索引 |
| `events/bootstrap-contract.json` | ✅ Production | 入口協定 |

---

## ⚡ 性能指標

| 操作 | 延遲限制 |
|------|---------|
| 事件讀取 (Bootstrap) | <=5s |
| 事件寫入 | <=1s |
| Policy 驗證 | <=5s |
| Intent 映射 | <=10s |
| Agent 部署 | <=30s |
| 事件處理 | <=1s (critical) |
| RAG 查詢 | <=1s |
| 完整部署 | <=180s |

---

## 🔗 相關文件

- [governance.yaml](../governance.yaml) - 全域治理配置
- [governance-map.yaml](../governance-map.yaml) - 依賴結構映射
- [30-agents/framework.yaml](../30-agents/framework.yaml) - Agent 治理框架
- [10-policy/framework.yaml](../10-policy/framework.yaml) - Policy as Code 框架
- [80-feedback/README.md](../80-feedback/README.md) - 閉環回饋系統

---

## ✅ 結論

Index 是**生產就緒的系統**：

- ✓ 機器讀取 → 立即啟動
- ✓ 向量嵌入 → 已生成
- ✓ RAG 檢索 → 現在可用
- ✓ DAG 驗證 → 已通過
- ✓ 合規映射 → 完整
- ✓ 事件驅動 → 已配置
- ✓ **事件持久化 → 代理不失憶**

**沒有「未來計畫」，只有「現在就能用」。**
**沒有「失憶症」，只有「共享記憶」。**
