# /docs/ 目錄結構分析報告

> **生成日期**: 2025-12-10  
> **分析範圍**: `/docs/` 子專案完整結構  
> **狀態**: 🔴 發現嚴重結構性問題

---

## 📊 執行摘要 (Executive Summary)

**結論**: `/docs/` 目錄結構存在**嚴重的組織性問題**，主要是：

1. ❌ **治理目錄重複** - 違反「治理統一管理」原則
2. ❌ **大小寫目錄衝突** - 7組重複目錄造成混淆
3. ⚠️ **根目錄文件過多** - 106個文件缺乏分類
4. ⚠️ **生成文件散落** - 自動生成檔案未集中管理

**建議**: 需要進行結構性重組，優先處理治理目錄問題。

---

## 🔍 詳細分析

### 問題 1: 治理目錄重複與混淆 🚨 最嚴重

#### 現狀

```
SynergyMesh/
├── docs/
│   └── GOVERNANCE/          # ❌ 6個治理說明文件（錯誤位置）
│       ├── overview.md
│       ├── policies.md
│       ├── schema.md
│       ├── decision_levels.md
│       ├── l0_policy.md
│       └── slsa.md
│
└── governance/              # ✅ 23維度治理矩陣（正確位置）
    ├── 00-vision-strategy/
    ├── 01-architecture/
    ├── 02-decision/
    ├── ...
    └── 37-behavior-contracts/
```

#### 問題診斷

- **根本矛盾**: 專案已完成「治理統一遷移到 `./governance/`」，但
  `docs/GOVERNANCE/` 仍存在
- **造成混淆**: 開發者不清楚治理文檔應該放在哪裡
- **違反原則**: 違反了「統一映射、引用、依賴、執行操作統一管理」的架構原則

#### 影響範圍

找到 **24 處引用** 指向 `docs/GOVERNANCE/`:

- `tools/cli/README.md` - 4 處
- `docs/generated-index.yaml` - 6 處
- 其他自動生成文件

#### 推薦方案

**方案 A（強烈推薦）**: 遷移到 governance/29-docs/

```bash
# 1. 將治理文檔遷移到治理目錄內
mkdir -p governance/29-docs
mv docs/GOVERNANCE/* governance/29-docs/

# 2. 刪除舊目錄
rmdir docs/GOVERNANCE

# 3. 更新所有引用路徑
sed -i 's|docs/GOVERNANCE/|governance/29-docs/|g' tools/cli/README.md
# ... 更新其他引用
```

**理由**:

- ✅ 符合「治理統一管理」原則
- ✅ 治理相關文檔應該在治理目錄內
- ✅ 與23維度治理矩陣結構一致

---

### 問題 2: 大小寫目錄重複

#### 衝突清單

| UPPERCASE 目錄  | lowercase 目錄  | 文件數對比 | 內容重疊    |
| --------------- | --------------- | ---------- | ----------- |
| `ARCHITECTURE/` | `architecture/` | 6 vs 23    | ❌ 不同內容 |
| `AGENTS/`       | `agents/`       | 4 vs 1     | ❌ 不同內容 |
| `AUTONOMY/`     | -               | 3          | -           |
| `COMPONENTS/`   | -               | 4          | -           |
| `COPILOT/`      | -               | 4          | -           |
| `DEPLOYMENT/`   | -               | 4          | -           |
| `GOVERNANCE/`   | -               | 6          | -           |

#### 內容差異分析

**ARCHITECTURE/ vs architecture/**:

- `ARCHITECTURE/`: 知識圖譜處理、插件架構、存儲架構、多語言策略等
- `architecture/`: 系統架構、代碼質量檢查、部署基礎設施、執行模型等
- **結論**: 兩者職責不同，需要合併或重新分類

**AGENTS/ vs agents/**:

- `AGENTS/`: CLI、生命週期、MCP、虛擬專家等
- `agents/`: 僅雲端代理角色
- **結論**: 應合併到 `agents/` 並分子目錄

#### 推薦方案

**方案 B**: 統一到 lowercase 並分類

```bash
# 1. 合併 AGENTS/ 到 agents/
mkdir -p agents/cli agents/mcp agents/virtual-experts
mv AGENTS/CLI.md agents/cli/
mv AGENTS/MCP.md agents/mcp/
mv AGENTS/VIRTUAL_EXPERTS.md agents/virtual-experts/
mv AGENTS/LIFECYCLE.md agents/

# 2. 合併 ARCHITECTURE/ 到 architecture/
mv ARCHITECTURE/knowledge-graph-processing.md architecture/
mv ARCHITECTURE/plugin-architecture-pattern.md architecture/
mv ARCHITECTURE/storage-architecture.md architecture/
mv ARCHITECTURE/MULTILANG_STRATEGY.md architecture/

# 3. 處理其他 UPPERCASE 目錄
# AUTONOMY/ → automation/autonomous/
# COMPONENTS/ → 根據內容分散到 architecture/, automation/ 等
# COPILOT/ → tools/cli/ 或新建 copilot/
# DEPLOYMENT/ → operations/deployment/
```

---

### 問題 3: 根目錄文件過多

#### 統計數據

- **根目錄 .md 文件數**: 106 個
- **建議閾值**: ≤ 20 個
- **超標**: 5.3 倍

#### 分類建議

根據文件名稱模式，建議分類如下：

| 模式                | 數量 | 建議目錄                 |
| ------------------- | ---- | ------------------------ |
| `CI_*.md`           | ~10  | `ci-cd/`                 |
| `AUTO_*.md`         | ~8   | `automation/`            |
| `ARCHITECTURE_*.md` | ~5   | `architecture/`          |
| `DEPLOYMENT_*.md`   | ~4   | `operations/deployment/` |
| `WORKFLOW_*.md`     | ~5   | `ci-cd/workflows/`       |
| `AGENT_*.md`        | ~3   | `agents/`                |
| `SECURITY_*.md`     | ~3   | `security/`              |
| `*_GUIDE.md`        | ~6   | `guides/` (新建)         |
| `*_SUMMARY.md`      | ~8   | `reports/summaries/`     |
| 其他                | ~48  | 依內容分類               |

#### 推薦方案

**方案 C**: 分階段整理

```bash
# 階段 1: 處理明確分類（CI/CD、Automation）
mkdir -p ci-cd/analysis automation/guides

# 階段 2: 建立新分類目錄
mkdir -p guides reports/summaries

# 階段 3: 逐步遷移文件
# (需要人工檢查每個文件內容)
```

---

### 問題 4: 生成文件散落

#### 現狀

```
docs/
├── generated-index.yaml        # 217KB
├── generated-mndoc.yaml        # 9KB
├── knowledge-graph.yaml        # 430KB
├── superroot-entities.yaml     # 466KB
└── ... (其他106個.md)
```

#### 推薦方案

**方案 D**: 集中管理

```bash
# 1. 建立 generated/ 目錄
mkdir -p docs/generated

# 2. 移動生成文件
mv docs/generated-*.yaml docs/generated/
mv docs/knowledge-graph.yaml docs/generated/
mv docs/superroot-entities.yaml docs/generated/

# 3. 添加 .gitignore
echo "# Auto-generated files" > docs/generated/.gitignore
echo "*.yaml" >> docs/generated/.gitignore
echo "!.gitignore" >> docs/generated/.gitignore

# 4. 保留 knowledge_index.yaml 在根目錄（手動維護）
```

---

## 📋 優先級排序

| 優先級 | 問題               | 影響         | 建議時程   |
| ------ | ------------------ | ------------ | ---------- |
| P0     | 治理目錄重複       | 違反架構原則 | 立即處理   |
| P1     | UPPERCASE 目錄衝突 | 造成開發混淆 | 1週內      |
| P2     | 生成文件散落       | 影響可維護性 | 2週內      |
| P3     | 根目錄文件過多     | 導航困難     | 分階段處理 |

---

## 🎯 推薦行動計劃

### 階段 1: 緊急修復（1-2天）

1. **治理目錄整合**

   ```bash
   # 執行方案 A
   mkdir -p governance/29-docs
   mv docs/GOVERNANCE/* governance/29-docs/
   rmdir docs/GOVERNANCE
   ```

2. **更新引用**
   - tools/cli/README.md
   - docs/generated-index.yaml
   - 其他引用文件

3. **驗證**

   ```bash
   python3 tools/docs/validate_index.py --verbose
   make all-kg  # 重新生成知識圖譜
   ```

### 階段 2: 結構優化（1週）

1. **合併重複目錄**（方案 B）
   - AGENTS/ → agents/
   - ARCHITECTURE/ → architecture/
   - 其他 UPPERCASE 目錄依內容處理

2. **隔離生成文件**（方案 D）
   - 建立 docs/generated/
   - 更新 .gitignore

### 階段 3: 持續整理（2-4週）

1. **根目錄文件分類**（方案 C）
   - 依模式批次處理
   - 人工審查每個文件
   - 逐步遷移

2. **文檔索引更新**
   - 更新 knowledge_index.yaml
   - 更新 DOCUMENTATION_INDEX.md
   - 更新 README.md

---

## ✅ 驗收標準

完成後，/docs/ 目錄應符合：

1. ✅ **零治理重複**: 所有治理文檔在 governance/ 目錄
2. ✅ **命名一致**: 全部使用 lowercase-with-hyphens
3. ✅ **根目錄清爽**: ≤20 個文件
4. ✅ **生成文件隔離**: 全部在 generated/ 子目錄
5. ✅ **索引有效**: `validate_index.py` 全部通過
6. ✅ **引用正確**: 無斷鏈或錯誤路徑

---

## 📚 參考文檔

- [Architecture Governance Matrix](../governance/ARCHITECTURE_GOVERNANCE_MATRIX.md)
- [Repository Map](./architecture/repo-map.md)
- [AI Behavior Contract](../.github/AI-BEHAVIOR-CONTRACT.md)
- [Living Knowledge Base](./LIVING_KNOWLEDGE_BASE.md)

---

**報告結束**

_此報告由 GitHub Copilot 自動生成，遵循 AI Behavior Contract 規範_
