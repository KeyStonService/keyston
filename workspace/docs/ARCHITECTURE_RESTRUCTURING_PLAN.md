# 🏗️ MachineNativeOps 架構重構計劃 | Architecture Restructuring Plan

> **文件版本**: 1.0.0  
> **建立日期**: 2025-12-17  
> **狀態**: 📝 DRAFT - Awaiting Review & Approval  
> **優先級**: 🔴 P0 - Critical Technical Debt

---

## 📑 目錄 | Table of Contents

1. [執行摘要](#-執行摘要--executive-summary)
2. [現況分析](#-現況分析--current-state-analysis)
3. [識別的關鍵問題](#-識別的關鍵問題--identified-key-issues)
4. [整合與重構方案](#-整合與重構方案--restructuring-solution)
5. [實施路線圖](#-實施路線圖--implementation-roadmap)
6. [風險評估與緩解](#-風險評估與緩解--risk-assessment--mitigation)
7. [成功指標](#-成功指標--success-metrics)
8. [附錄](#-附錄--appendix)

---

## 🎯 執行摘要 | Executive Summary

### 專案概況

**MachineNativeOps** (無人島系統 / Unmanned Island System) 是一個企業級智能自動化平台，旨在實現零接觸運維。專案當前版本為 **v4.0.0**，擁有明確的願景和戰略目標，但其儲存庫結構面臨嚴重的架構混亂問題。

### 核心問題

```
🔴 52+ 個頂層目錄（應為 < 10 個）
🔴 命名規範不一致（PascalCase, kebab-case, 同義詞混用）
🔴 重複目錄（infra/infrastructure, deployment/deploy, script/scripts）
🔴 配置分散（.config/, config/, .devcontainer/）
🔴 版本管理不清晰（缺乏單一真實來源）
```

### 解決方案概要

實施一個 **5 步整合計劃**，建立標準化、模組化的目錄結構：

1. **建立清晰的根目錄結構** - 建立 `src/`, `config/`, `scripts/`, `docs/` 等語義化目錄
2. **解決命名不一致性** - 強制使用 kebab-case，消滅同義詞
3. **建立統一版本管理** - `machinenativeops.yaml` 作為單一真實來源 + Git tags
4. **重新組織代碼與配置** - 隔離應用代碼、配置文件、腳本
5. **透過文檔強化新結構** - 更新 README、CONTRIBUTING、創建遷移指南

### 預期效益

- ✅ **可維護性提升 70%** - 清晰的目錄結構降低認知負荷
- ✅ **新成員上手時間減少 60%** - 標準化命名與文檔
- ✅ **技術債務減少 80%** - 消除重複與混亂
- ✅ **協作效率提升 50%** - 統一規範與版本管理

---

## 🔍 現況分析 | Current State Analysis

### 當前目錄結構統計

```bash
# 頂層目錄數量
$ find . -maxdepth 1 -type d -not -path '.' -not -path './.git' | wc -l
52

# 重複目錄對比
infra/          ←→  infrastructure/
deployment/     ←→  deploy/
script/         ←→  scripts/
ai/             ←→  island-ai/
.config/        ←→  config/
```

### 三大核心子系統現況

根據 `README.md` 描述，系統應有三個核心子系統：

| 子系統 | 理想位置 | 當前位置 | 問題 |
|--------|---------|---------|------|
| **🔷 SynergyMesh Core** | `src/core/` | `core/` (頂層) | 與其他頂層目錄並列，缺乏層次 |
| **⚖️ Structural Governance** | `src/governance/` | `governance/` (頂層) | 同上 |
| **🚁 Autonomous Framework** | `src/autonomous/` | `autonomous/`, `deployment/`, `deploy/`, `automation/` | 功能分散在多個目錄 |

### 🛑 根目錄整合缺口（2025-12-18 更新）

前幾次 PR 承諾要整合的根目錄仍未落地，需以「先收斂、後優化」處理：

| 未整合根目錄 | 目標位置 | 狀態 | 說明 |
|--------------|----------|------|------|
| `ai/` | `src/ai/` | 🔴 未整合 | 與 `island-ai/` 並存，導致雙入口 |
| `island-ai/` | `src/ai/` | 🔴 未整合 | 同上 |
| `agent/` | `src/ai/agents/` | 🔴 未整合 | 智能代理與 AI 決策重疊 |
| `automation/` | `src/autonomous/automation/` | 🔴 未整合 | 應併入自主框架 |
| `autonomous/` | `src/autonomous/` | 🟠 部分 | 尚未與 `deployment/`、`deploy/` 對齊 |
| `deployment/` | `src/autonomous/deployment/` | 🔴 未整合 | Kubernetes/部署腳本分散 |
| `deploy/` | `src/autonomous/deployment/k8s/` | 🔴 未整合 | 與 `deployment/` 重複 |
| `infra/` | `src/autonomous/infrastructure/` | 🔴 未整合 | 與 `infrastructure/` 重複 |
| `infrastructure/` | `src/autonomous/infrastructure/` | 🔴 未整合 | 需與 `infra/` 合併 |
| `script/` | `scripts/` | 🔴 未整合 | 與 `scripts/` 並存，易混淆 |

**P0 行動（立即執行，<48h）：**

- 鎖定新增頂層目錄的 PR，僅允許移動到 `src/`, `config/`, `scripts/`, `docs/`
- 依上表批次 `git mv`（先 `ai`/`island-ai`，再部署與基礎設施目錄）
- 更新導入路徑與 CI 檢查腳本，確保 `machinenativeops.yaml` 為單一入口

### 配置文件分散情況

```
.config/               # 開發工具配置
config/                # 系統配置
.devcontainer/         # 開發容器配置
machinenativeops.yaml  # 主配置文件（正確）
governance-manifest.yaml
island.bootstrap.stage0.yaml
```

### 命名規範混亂統計

| 命名風格 | 範例 | 數量 (估計) |
|---------|------|------------|
| **PascalCase** | `NamespaceTutorial` | ~5 |
| **kebab-case** | `docker-templates`, `mcp-servers` | ~30 |
| **snake_case** | `v1-python-drones`, `v2-multi-islands` | ~10 |
| **其他** | `ai` (太短), `ops` (太短) | ~7 |

### 版本管理現況

```yaml
# machinenativeops.yaml (第 15 行)
version: "4.0.0"
vision_version: "1.0.0"
```

✅ **良好實踐**: `machinenativeops.yaml` 已定義版本號  
❌ **缺失**: 未與 Git tags 結合，缺乏發布流程文檔

---

## 🚨 識別的關鍵問題 | Identified Key Issues

### 1. 嚴重的架構混亂 (P0 - Critical)

#### 問題描述

當前儲存庫採用**過度扁平化**設計，52+ 個頂層目錄導致：

- 🔴 **導航困難** - 開發者需要記憶大量頂層目錄的用途
- 🔴 **邏輯脫節** - 相關模組（如 `agent`, `automation`, `autonomous`）物理分離
- 🔴 **模組化失效** - 違反「模組化設計」核心原則

#### 影響評估

| 影響維度 | 嚴重程度 | 具體表現 |
|---------|---------|---------|
| **新成員上手** | 🔴 High | 需 2-3 天理解目錄結構 |
| **協作效率** | 🔴 High | PR 審查時間增加 40% |
| **維護成本** | 🔴 High | 依賴關係難以追蹤 |
| **技術債務** | 🔴 High | 累積重構成本高 |

#### 根本原因

```
根本原因分析 (5 Whys):
1. 為何目錄過多？ → 缺乏初期架構規劃
2. 為何缺乏規劃？ → 快速迭代優先於結構化
3. 為何優先迭代？ → 市場壓力與功能交付
4. 為何未及時重構？ → 缺乏自動化治理機制
5. 為何缺乏機制？ → 技術債務管理流程不完善

→ 結論: 需要建立「Governance as Code」機制防止回退
```

### 2. 命名不一致 (P1 - High)

#### 問題描述

混用多種命名風格，缺乏統一詞典：

```bash
# 問題案例
NamespaceTutorial/          # PascalCase
docker-templates/           # kebab-case
v1-python-drones/           # kebab-case + version prefix
unmanned-engineer-ceo/      # kebab-case + long name
ai/                         # 過短，語義不明
island-ai/                  # 與 ai/ 功能重疊
```

#### 影響評估

- 🟡 **認知負荷增加** - 需要記憶多種命名規則
- 🟡 **搜索效率降低** - 難以預測目錄名稱
- 🟡 **工具兼容性** - 某些工具對命名大小寫敏感

#### 推薦標準

**強制使用 kebab-case**，理由：

1. ✅ 跨平台兼容（大小寫不敏感文件系統）
2. ✅ URL 友好（可直接用於 API 路徑）
3. ✅ 易於閱讀（單詞清晰分隔）
4. ✅ 業界標準（Kubernetes, Docker, npm 等）

### 3. 邏輯與配置混雜 (P1 - High)

#### 問題描述

違反「關注點分離」原則：

```
應用代碼 ←混雜→ 配置文件 ←混雜→ 構建腳本 ←混雜→ 開發工具配置
```

#### 具體案例

| 問題類型 | 當前位置 | 理想位置 |
|---------|---------|---------|
| **開發工具配置** | `.config/`, `.devcontainer/` | `config/dev/` |
| **系統配置** | `config/`, 根目錄 YAML | `config/` (統一) |
| **構建腳本** | `script/`, `scripts/`, 各目錄下 | `scripts/` (統一) |
| **部署配置** | `deployment/`, `deploy/`, `infra/` | `src/autonomous/deployment/` |

### 4. 版本管理不清晰 (P2 - Medium)

#### 問題描述

- ✅ 已在 `machinenativeops.yaml` 定義版本號
- ❌ 未與 Git tags 結合
- ❌ 缺乏語意化版本控制流程文檔
- ❌ 子模組版本未統一管理

#### 改進建議

1. **Git tags 整合** - 每次發布創建 `vX.Y.Z` tag
2. **自動化發布流程** - CI/CD 自動讀取 `machinenativeops.yaml` 版本
3. **子模組版本對齊** - 使用 `lerna` 或 `nx` 管理 monorepo 版本

---

## 🎯 整合與重構方案 | Restructuring Solution

### 目標架構 (Target Architecture)

```
/
├── src/                        # 應用程式主代碼 (NEW!)
│   ├── core/                   # SynergyMesh 核心引擎
│   │   ├── unified-integration/
│   │   ├── mind-matrix/
│   │   ├── safety-mechanisms/
│   │   ├── slsa-provenance/
│   │   └── contract-service/
│   ├── governance/             # 結構治理系統
│   │   ├── 00-vision-strategy/
│   │   ├── 10-policy/
│   │   ├── 20-registry/
│   │   ├── 30-agents/
│   │   └── ...
│   ├── autonomous/             # 自主系統框架 (MERGED!)
│   │   ├── architecture-stability/
│   │   ├── deployment/         # ← 合併 deployment/, deploy/
│   │   ├── infrastructure/     # ← 合併 infra/, infrastructure/
│   │   ├── automation/         # ← 移入 automation/
│   │   └── observability/
│   ├── ai/                     # AI 系統 (MERGED!)
│   │   ├── agents/             # ← 合併 agent/, island-ai/
│   │   ├── models/
│   │   └── virtual-experts/
│   ├── services/               # 微服務 (CONSOLIDATED)
│   │   ├── mcp-servers/
│   │   ├── contract-service/
│   │   └── ...
│   ├── apps/                   # 應用程式
│   │   ├── web/                # ← 移入 web/, frontend/
│   │   ├── cli/
│   │   └── admin-copilot/
│   └── shared/                 # 共享代碼庫
│       ├── types/
│       ├── utils/
│       └── constants/
│
├── config/                     # 所有配置文件 (UNIFIED!)
│   ├── dev/                    # 開發環境配置
│   │   ├── devcontainer.json   # ← 移入 .devcontainer/
│   │   └── vscode.json         # ← 移入 .vscode/
│   ├── staging/                # 測試環境配置
│   ├── prod/                   # 生產環境配置
│   ├── system-manifest.yaml
│   ├── system-module-map.yaml
│   └── unified-config-index.yaml
│
├── scripts/                    # 所有腳本 (UNIFIED!)
│   ├── dev/                    # 開發腳本
│   │   ├── start.sh
│   │   └── build.sh
│   ├── ci/                     # CI/CD 腳本
│   │   ├── test.sh
│   │   └── deploy.sh
│   ├── ops/                    # 運維腳本
│   │   ├── backup.sh
│   │   └── restore.sh
│   └── migration/              # 本次重構遷移腳本 (NEW!)
│       ├── migrate-dirs.sh
│       └── update-refs.sh
│
├── docs/                       # 文檔 (KEEP)
│   ├── architecture/
│   ├── api/
│   ├── operations/
│   └── guides/
│
├── tests/                      # 測試 (KEEP)
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── .github/                    # GitHub 配置 (KEEP)
│   ├── workflows/
│   ├── agents/
│   ├── AI-BEHAVIOR-CONTRACT.md
│   ├── copilot-instructions.md
│   └── island-ai-instructions.md
│
├── examples/                   # 範例代碼 (KEEP)
├── tools/                      # 開發工具 (KEEP)
│
├── machinenativeops.yaml       # 統一入口配置 (KEEP)
├── package.json                # Workspace 配置 (KEEP)
├── README.md                   # 主文檔 (KEEP)
├── CONTRIBUTING.md             # 貢獻指南 (UPDATE)
└── ...                         # 其他根目錄文件
```

### 關鍵改進點

#### 1. 建立 `src/` 主目錄

**理由**: 清晰區分應用代碼與配置、文檔、工具

```bash
# 遷移核心子系統
src/
├── core/          # ← 移入 core/
├── governance/    # ← 移入 governance/
└── autonomous/    # ← 移入 autonomous/ + 合併相關目錄
```

#### 2. 合併重複目錄

| 合併前 | 合併後 | 理由 |
|--------|--------|------|
| `infra/`, `infrastructure/` | `src/autonomous/infrastructure/` | 同義詞，功能重疊 |
| `deployment/`, `deploy/` | `src/autonomous/deployment/` | 同義詞，功能重疊 |
| `script/`, `scripts/` | `scripts/` | 標準化為複數形式 |
| `ai/`, `island-ai/` | `src/ai/` | 合併 AI 相關代碼 |
| `agent/`, `automation/` | `src/ai/agents/`, `src/autonomous/automation/` | 按職責分類 |

#### 3. 統一配置目錄

```
config/
├── dev/              # 開發環境配置
│   ├── devcontainer.json
│   ├── vscode-settings.json
│   └── local.env
├── staging/          # 測試環境配置
│   └── staging.env
├── prod/             # 生產環境配置
│   └── production.env
└── system-*.yaml     # 系統級配置
```

#### 4. 標準化命名

**命名規範 (Naming Convention)**:

```yaml
# 強制規則
directory_naming: kebab-case
file_naming: kebab-case  # 配置文件、腳本
code_naming: 
  typescript: camelCase (variables/functions), PascalCase (classes/interfaces)
  python: snake_case (variables/functions), PascalCase (classes)
  
# 禁止規則
forbidden:
  - 過短名稱 (如 ai/, ops/) - 必須語義清晰
  - 同義詞並存 (如 infra/ & infrastructure/)
  - 版本前綴在目錄名 (如 v1-python-drones/) - 使用 Git tags
```

---

## 🗓️ 實施路線圖 | Implementation Roadmap

### Phase 0: 準備階段 (1-2 天)

**目標**: 建立重構基礎設施與安全網

#### 任務清單

- [ ] **0.1 創建重構分支**

  ```bash
  git checkout -b refactor/architecture-restructuring
  ```

- [ ] **0.2 完整備份當前狀態**

  ```bash
  git tag -a v4.0.0-pre-refactor -m "Backup before restructuring"
  tar -czf ../machinenativeops-backup-$(date +%Y%m%d).tar.gz .
  ```

- [ ] **0.3 建立依賴關係圖**

  ```bash
  # 使用工具分析當前依賴
  npx madge --image deps-graph.png src/
  python tools/analyze-deps.py > docs/DEPENDENCY_GRAPH.md
  ```

- [ ] **0.4 凍結功能開發**
  - 通知團隊暫停合併新功能 PR
  - 只接受 bugfix 和文檔更新

- [ ] **0.5 準備遷移腳本**

  ```bash
  mkdir -p scripts/migration/
  # 創建自動化遷移腳本（見附錄）
  ```

### Phase 1: 文檔與規範更新 (2-3 天)

**目標**: 先建立新規範，再執行遷移

#### 任務清單

- [ ] **1.1 創建 ARCHITECTURE_RESTRUCTURING_PLAN.md** ✅ (當前文檔)

- [ ] **1.2 更新 CONTRIBUTING.md**

  ```markdown
  ## 目錄結構規範
  
  ### 新增代碼放置位置
  - 核心引擎代碼 → `src/core/`
  - 治理相關代碼 → `src/governance/`
  - 自主系統代碼 → `src/autonomous/`
  - AI 系統代碼 → `src/ai/`
  - 微服務 → `src/services/`
  - 應用程式 → `src/apps/`
  
  ### 命名規範
  - 目錄名稱：一律使用 kebab-case
  - 文件名稱：kebab-case（配置/腳本）
  - 代碼命名：遵循語言慣例（見 .github/island-ai-instructions.md）
  
  ### 配置文件放置
  - 開發環境配置 → `config/dev/`
  - 系統級配置 → `config/*.yaml`
  - 環境變數 → `config/{env}/*.env`
  ```

- [ ] **1.3 更新 README.md 專案結構章節**

  ```markdown
  ## 📂 專案結構
  
  本專案採用模組化、分層設計：
  
  - `src/` - 應用程式主代碼
    - `core/` - SynergyMesh 核心引擎
    - `governance/` - 結構治理系統
    - `autonomous/` - 自主系統框架
    - `ai/` - AI 決策與代理系統
  - `config/` - 所有配置文件
  - `scripts/` - 所有自動化腳本
  - `docs/` - 完整文檔
  - `tests/` - 測試套件
  
  詳見 [docs/ARCHITECTURE_RESTRUCTURING_PLAN.md](./docs/ARCHITECTURE_RESTRUCTURING_PLAN.md)
  ```

- [ ] **1.4 創建遷移指南 (MIGRATION_GUIDE.md)**

  ```markdown
  # 重構遷移指南
  
  ## 開發者行動項
  
  ### 更新本地分支
  1. 拉取最新 main 分支
  2. 更新 import 路徑（見下方映射表）
  3. 更新配置文件路徑
  4. 運行測試確保無誤
  
  ### 路徑映射表
  | 舊路徑 | 新路徑 |
  |--------|--------|
  | `core/` | `src/core/` |
  | `governance/` | `src/governance/` |
  | ... | ... |
  ```

- [ ] **1.5 更新版本管理文檔**

  ```markdown
  # 版本管理策略
  
  ## 單一真實來源
  `machinenativeops.yaml` 的 `version` 欄位為版本號唯一來源。
  
  ## 發布流程
  1. 更新 `machinenativeops.yaml` 版本號
  2. 更新 `CHANGELOG.md`
  3. 提交並創建 Git tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
  4. 推送 tag: `git push origin vX.Y.Z`
  5. CI/CD 自動觸發發布流程
  ```

### Phase 2: 目錄結構遷移 (3-5 天)

**目標**: 執行物理遷移，建立新結構

#### 任務分組

**2.1 建立新頂層目錄**

```bash
mkdir -p src/{core,governance,autonomous,ai,services,apps,shared}
mkdir -p config/{dev,staging,prod}
mkdir -p scripts/{dev,ci,ops,migration}
```

**2.2 遷移核心子系統**

```bash
# 遷移計劃（使用 git mv 保留歷史）
git mv core/ src/core/
git mv governance/ src/governance/

# 自主系統需合併多個目錄
mkdir -p src/autonomous
git mv autonomous/ src/autonomous/core/
git mv deployment/ src/autonomous/deployment/
git mv deploy/ src/autonomous/deployment/k8s/  # 合併
# ... 繼續合併其他相關目錄
```

**2.3 合併重複目錄**

```bash
# 基礎設施合併
mkdir -p src/autonomous/infrastructure
git mv infra/* src/autonomous/infrastructure/
git mv infrastructure/* src/autonomous/infrastructure/
# 解決衝突後
rmdir infra/ infrastructure/

# AI 系統合併
mkdir -p src/ai
git mv ai/* src/ai/
git mv island-ai/* src/ai/island-core/
git mv agent/ src/ai/agents/
rmdir ai/ island-ai/ agent/
```

**2.4 重組配置文件**

```bash
# 開發配置
git mv .devcontainer/* config/dev/devcontainer/
git mv .vscode/settings.json config/dev/vscode-settings.json
git mv .config/* config/dev/

# 系統配置
# config/ 目錄已經合理，只需整理
mv config/*.env config/dev/
```

**2.5 統一腳本目錄**

```bash
# 合併 script/ 和 scripts/
git mv script/* scripts/
rmdir script/

# 分類腳本
mkdir -p scripts/{dev,ci,ops}
# 手動分類現有腳本到對應子目錄
```

**2.6 清理與標準化命名**

```bash
# 重命名 PascalCase 目錄
git mv NamespaceTutorial/ docs/tutorials/namespace/

# 處理版本前綴目錄
git mv v1-python-drones/ legacy/python-drones-v1/
git mv v2-multi-islands/ legacy/multi-islands-v2/

# 處理過短或語義不清的目錄
# 這些需要根據內容決定去向
```

### Phase 3: 代碼引用更新 (2-3 天)

**目標**: 更新所有路徑引用，確保代碼可運行

#### 任務清單

- [ ] **3.1 更新 TypeScript import 路徑**

  ```bash
  # 使用 ts-morph 或手動全局替換
  find src/ -name "*.ts" -o -name "*.tsx" | xargs sed -i \
    -e 's|from "core/|from "src/core/|g' \
    -e 's|from "governance/|from "src/governance/|g'
  ```

- [ ] **3.2 更新 Python import 路徑**

  ```bash
  find src/ -name "*.py" | xargs sed -i \
    -e 's|from core\.|from src.core.|g'
  ```

- [ ] **3.3 更新配置文件路徑引用**

  ```bash
  # 更新 machinenativeops.yaml
  sed -i 's|config/|config/|g' machinenativeops.yaml
  
  # 更新 package.json workspaces
  # 手動編輯，更新路徑
  ```

- [ ] **3.4 更新 CI/CD 腳本**

  ```bash
  # 更新 .github/workflows/*.yml
  find .github/workflows/ -name "*.yml" | xargs sed -i \
    -e 's|scripts/|scripts/ci/|g'
  ```

- [ ] **3.5 更新文檔中的路徑**

  ```bash
  find docs/ -name "*.md" | xargs sed -i \
    -e 's|](core/|](src/core/|g' \
    -e 's|](governance/|](src/governance/|g'
  ```

### Phase 4: 測試與驗證 (2-3 天)

**目標**: 確保所有功能正常運作

#### 任務清單

- [ ] **4.1 運行單元測試**

  ```bash
  npm test
  ```

- [ ] **4.2 運行整合測試**

  ```bash
  npm run test:integration
  ```

- [ ] **4.3 運行 E2E 測試**

  ```bash
  npm run test:e2e
  ```

- [ ] **4.4 運行 Linters**

  ```bash
  npm run lint
  npm run lint:fix
  ```

- [ ] **4.5 驗證構建流程**

  ```bash
  npm run build
  ```

- [ ] **4.6 驗證部署流程**

  ```bash
  # 在 staging 環境測試部署
  npm run deploy:staging
  ```

- [ ] **4.7 手動功能測試**
  - 啟動開發環境: `npm run dev`
  - 測試核心功能
  - 測試 MCP 伺服器
  - 測試 Web 應用

### Phase 5: 文檔與發布 (1-2 天)

**目標**: 完成文檔更新，發布新版本

#### 任務清單

- [ ] **5.1 更新 CHANGELOG.md**

  ```markdown
  ## [5.0.0] - 2025-12-XX
  
  ### 💥 Breaking Changes
  - 重構目錄結構，建立 `src/` 主目錄
  - 合併重複目錄
  - 標準化命名為 kebab-case
  
  ### 📦 Migration
  - 所有 import 路徑需更新（見 MIGRATION_GUIDE.md）
  - 配置文件路徑已變更
  - 腳本路徑已統一
  
  ### 📚 Documentation
  - 新增 ARCHITECTURE_RESTRUCTURING_PLAN.md
  - 更新 CONTRIBUTING.md
  - 更新 README.md 專案結構章節
  ```

- [ ] **5.2 更新 machinenativeops.yaml 版本號**

  ```yaml
  version: "5.0.0"  # 主版本號遞增（重大變更）
  ```

- [ ] **5.3 創建 Git tag**

  ```bash
  git add .
  git commit -m "refactor: Restructure project architecture (v5.0.0)"
  git tag -a v5.0.0 -m "Release v5.0.0 - Architecture Restructuring"
  git push origin refactor/architecture-restructuring
  git push origin v5.0.0
  ```

- [ ] **5.4 創建 PR 並通知團隊**
  - 撰寫詳細的 PR 描述
  - 附上遷移指南連結
  - 安排團隊培訓會議

- [ ] **5.5 合併與發布**
  - 經過團隊 review 後合併到 main
  - CI/CD 自動發布新版本

---

## ⚠️ 風險評估與緩解 | Risk Assessment & Mitigation

### 風險矩陣

| 風險 | 可能性 | 影響 | 優先級 | 緩解策略 |
|------|--------|------|--------|---------|
| **路徑引用遺漏** | 🟡 Medium | 🔴 High | P0 | 自動化測試 + 手動審查 |
| **CI/CD 中斷** | 🟡 Medium | 🔴 High | P0 | 在 staging 環境先測試 |
| **團隊協作混亂** | 🟡 Medium | 🟡 Medium | P1 | 詳細遷移指南 + 培訓 |
| **第三方整合失效** | 🟢 Low | 🟡 Medium | P2 | 審查外部依賴配置 |
| **回退困難** | 🟢 Low | 🔴 High | P1 | Git tag 備份 + 回退計劃 |

### 具體緩解措施

#### 1. 路徑引用遺漏

**檢測機制**:

```bash
# 腳本: scripts/migration/verify-refs.sh
#!/bin/bash

# 檢測可能的舊路徑引用
echo "Checking for old path references..."
grep -r "from \"core/" src/ && echo "❌ Found old imports" || echo "✅ No old imports"
grep -r "from \"governance/" src/ && echo "❌ Found old imports" || echo "✅ No old imports"

# 檢測絕對路徑引用
grep -r "/home/runner/work/MachineNativeOps/MachineNativeOps/core" . \
  && echo "⚠️ Found absolute paths"
```

**緩解**:

- 使用自動化工具（codemod, ts-morph）批量更新
- 運行完整測試套件
- 手動審查關鍵路徑

#### 2. CI/CD 中斷

**預防措施**:

- 在 `refactor/architecture-restructuring` 分支上測試 CI/CD
- 更新 workflow 文件後先在分支上驗證
- 準備回退腳本

**回退計劃**:

```bash
# 如果發布後發現嚴重問題
git revert <commit-hash>
git tag -d v5.0.0
git push origin :refs/tags/v5.0.0
git push origin main
```

#### 3. 團隊協作混亂

**預防措施**:

- 提前 1 週通知團隊
- 提供詳細的 MIGRATION_GUIDE.md
- 舉辦團隊培訓會議
- 建立 Slack 頻道解答問題

**溝通計劃**:

```markdown
# 郵件模板

主旨: [重要] 專案架構重構計劃 - 需要您的行動

親愛的團隊成員，

我們將於 [日期] 執行專案架構重構，這將影響所有開發者的工作流程。

**重要日期**:
- [日期 - 1週]: 凍結功能開發
- [日期]: 開始重構遷移
- [日期 + 1週]: 完成遷移與驗證

**您需要做什麼**:
1. 閱讀 MIGRATION_GUIDE.md
2. 在重構完成後拉取最新代碼
3. 更新本地分支的 import 路徑
4. 運行測試確保無誤

詳細資訊: [連結到 ARCHITECTURE_RESTRUCTURING_PLAN.md]
```

---

## 📊 成功指標 | Success Metrics

### 量化指標

| 指標 | 當前 | 目標 | 測量方式 |
|------|------|------|---------|
| **頂層目錄數量** | 52+ | < 10 | `find . -maxdepth 1 -type d | wc -l` |
| **重複目錄對數** | 5+ | 0 | 手動審查 |
| **命名規範合規率** | ~60% | 100% | 自動化腳本檢測 |
| **配置文件集中度** | 分散 | 單一 `config/` 目錄 | 手動審查 |
| **版本管理規範** | 部分 | 完整流程 | 是否有 Git tags + 文檔 |
| **新成員上手時間** | 2-3 天 | 1 天 | 團隊調查 |
| **PR 審查時間** | 平均 4 小時 | 平均 2.5 小時 | GitHub Insights |

### 質化指標

- [ ] 開發者滿意度調查分數 > 4.5/5
- [ ] 新成員反饋「目錄結構清晰易懂」
- [ ] 技術債務積壓項目減少 50%
- [ ] 文檔完整性評分 > 90%

### 驗證檢查清單

#### 結構驗證

```bash
# 腳本: scripts/migration/verify-structure.sh
#!/bin/bash

echo "Verifying directory structure..."

# 檢查頂層目錄數量
TOP_LEVEL_COUNT=$(find . -maxdepth 1 -type d -not -path '.' -not -path './.git' | wc -l)
if [ $TOP_LEVEL_COUNT -gt 15 ]; then
  echo "❌ Too many top-level directories: $TOP_LEVEL_COUNT (should be < 15)"
  exit 1
else
  echo "✅ Top-level directory count OK: $TOP_LEVEL_COUNT"
fi

# 檢查必要目錄是否存在
REQUIRED_DIRS=("src" "config" "scripts" "docs" "tests" ".github")
for dir in "${REQUIRED_DIRS[@]}"; do
  if [ ! -d "$dir" ]; then
    echo "❌ Required directory missing: $dir"
    exit 1
  else
    echo "✅ Required directory exists: $dir"
  fi
done

# 檢查禁止的舊目錄
FORBIDDEN_DIRS=("infra" "infrastructure" "deployment" "deploy" "script")
for dir in "${FORBIDDEN_DIRS[@]}"; do
  if [ -d "$dir" ]; then
    echo "❌ Forbidden old directory still exists: $dir"
    exit 1
  fi
done
echo "✅ No forbidden old directories found"

echo "✅ Structure verification passed!"
```

#### 命名規範驗證

```bash
# 腳本: scripts/migration/verify-naming.sh
#!/bin/bash

echo "Verifying naming conventions..."

# 檢測 PascalCase 目錄
PASCAL_CASE=$(find src/ config/ scripts/ -type d | grep -E '[A-Z][a-z]+[A-Z]')
if [ -n "$PASCAL_CASE" ]; then
  echo "❌ Found PascalCase directories:"
  echo "$PASCAL_CASE"
  exit 1
else
  echo "✅ No PascalCase directories found"
fi

# 檢測 snake_case 目錄
SNAKE_CASE=$(find src/ config/ scripts/ -type d | grep -E '_')
if [ -n "$SNAKE_CASE" ]; then
  echo "⚠️ Found snake_case directories:"
  echo "$SNAKE_CASE"
fi

echo "✅ Naming convention verification passed!"
```

#### 功能驗證

```bash
# 完整驗證流程
npm install          # 安裝依賴
npm run lint         # Linting
npm run build        # 構建
npm test             # 單元測試
npm run test:e2e     # E2E 測試
npm run dev          # 啟動開發環境（手動測試）
```

---

## 📎 附錄 | Appendix

### A. 自動化遷移腳本

#### `scripts/migration/migrate-dirs.sh`

```bash
#!/bin/bash
set -e

echo "=== MachineNativeOps Architecture Migration Script ==="
echo "Starting migration at $(date)"

# 備份
echo "Creating backup..."
git tag -a v4.0.0-pre-migration -m "Backup before migration"

# Phase 2.1: 建立新目錄結構
echo "Phase 2.1: Creating new directory structure..."
mkdir -p src/{core,governance,autonomous,ai,services,apps,shared}
mkdir -p config/{dev,staging,prod}
mkdir -p scripts/{dev,ci,ops,migration}

# Phase 2.2: 遷移核心子系統
echo "Phase 2.2: Migrating core subsystems..."
git mv core/ src/core/
git mv governance/ src/governance/

# Phase 2.3: 合併重複目錄
echo "Phase 2.3: Merging duplicate directories..."

# 自主系統合併
mkdir -p src/autonomous/{core,deployment,infrastructure,automation}
git mv autonomous/* src/autonomous/core/
git mv deployment/* src/autonomous/deployment/
[ -d deploy/ ] && git mv deploy/* src/autonomous/deployment/k8s/
[ -d infra/ ] && git mv infra/* src/autonomous/infrastructure/
[ -d infrastructure/ ] && git mv infrastructure/* src/autonomous/infrastructure/

# AI 系統合併
mkdir -p src/ai/{agents,models,virtual-experts}
[ -d ai/ ] && git mv ai/* src/ai/
[ -d island-ai/ ] && git mv island-ai/* src/ai/island-core/
[ -d agent/ ] && git mv agent/* src/ai/agents/

# 清理空目錄
rmdir infra/ infrastructure/ deployment/ deploy/ ai/ island-ai/ agent/ 2>/dev/null || true

# Phase 2.4: 重組配置
echo "Phase 2.4: Reorganizing configurations..."
[ -d .devcontainer/ ] && git mv .devcontainer/ config/dev/devcontainer/
[ -f .vscode/settings.json ] && git mv .vscode/settings.json config/dev/vscode-settings.json

# Phase 2.5: 統一腳本
echo "Phase 2.5: Unifying scripts..."
[ -d script/ ] && git mv script/* scripts/ && rmdir script/

# 提交
git add .
git commit -m "refactor: Migrate directory structure (Phase 2 complete)"

echo "=== Migration completed at $(date) ==="
echo "Next: Run scripts/migration/update-refs.sh"
```

#### `scripts/migration/update-refs.sh`

```bash
#!/bin/bash
set -e

echo "=== Updating Path References ==="

# TypeScript imports
echo "Updating TypeScript imports..."
find src/ -name "*.ts" -o -name "*.tsx" | while read file; do
  sed -i.bak \
    -e 's|from ["'\'']\.\./\.\./core/|from "src/core/|g' \
    -e 's|from ["'\'']core/|from "src/core/|g' \
    -e 's|from ["'\'']governance/|from "src/governance/|g' \
    -e 's|from ["'\'']autonomous/|from "src/autonomous/|g' \
    "$file"
  rm "${file}.bak"
done

# Python imports
echo "Updating Python imports..."
find src/ -name "*.py" | while read file; do
  sed -i.bak \
    -e 's|from core\.|from src.core.|g' \
    -e 's|from governance\.|from src.governance.|g' \
    "$file"
  rm "${file}.bak"
done

# Configuration files
echo "Updating configuration files..."
sed -i.bak 's|path: core/|path: src/core/|g' machinenativeops.yaml
rm machinenativeops.yaml.bak

# Documentation
echo "Updating documentation..."
find docs/ -name "*.md" | while read file; do
  sed -i.bak \
    -e 's|](core/|](src/core/|g' \
    -e 's|](governance/|](src/governance/|g' \
    "$file"
  rm "${file}.bak"
done

# Commit
git add .
git commit -m "refactor: Update path references (Phase 3 complete)"

echo "=== Reference update completed ==="
echo "Next: Run tests and verify"
```

### B. 驗證腳本

#### `scripts/migration/verify-all.sh`

```bash
#!/bin/bash
set -e

echo "=== Running Full Verification Suite ==="

# 結構驗證
echo "1. Structure verification..."
bash scripts/migration/verify-structure.sh

# 命名驗證
echo "2. Naming convention verification..."
bash scripts/migration/verify-naming.sh

# 引用驗證
echo "3. Reference verification..."
bash scripts/migration/verify-refs.sh

# Linting
echo "4. Running linters..."
npm run lint

# 構建
echo "5. Building project..."
npm run build

# 測試
echo "6. Running tests..."
npm test

echo "✅ All verifications passed!"
```

### C. 路徑映射表 (完整版)

| 舊路徑 | 新路徑 | 說明 |
|--------|--------|------|
| `core/` | `src/core/` | SynergyMesh 核心引擎 |
| `governance/` | `src/governance/` | 結構治理系統 |
| `autonomous/` | `src/autonomous/core/` | 自主系統核心 |
| `deployment/` | `src/autonomous/deployment/` | 部署配置 |
| `deploy/` | `src/autonomous/deployment/k8s/` | K8s 部署 |
| `infra/` | `src/autonomous/infrastructure/` | 基礎設施 (合併) |
| `infrastructure/` | `src/autonomous/infrastructure/` | 基礎設施 (合併) |
| `automation/` | `src/autonomous/automation/` | 自動化系統 |
| `ai/` | `src/ai/` | AI 系統 (合併) |
| `island-ai/` | `src/ai/island-core/` | Island AI 核心 (合併) |
| `agent/` | `src/ai/agents/` | 智能代理 |
| `mcp-servers/` | `src/services/mcp-servers/` | MCP 伺服器 |
| `web/` | `src/apps/web/` | Web 應用 |
| `frontend/` | `src/apps/web/` | 前端 (合併) |
| `.devcontainer/` | `config/dev/devcontainer/` | 開發容器配置 |
| `.config/` | `config/dev/` | 開發工具配置 |
| `script/` | `scripts/` | 腳本 (合併) |
| `NamespaceTutorial/` | `docs/tutorials/namespace/` | 範例 (重命名) |
| `v1-python-drones/` | `legacy/python-drones-v1/` | 舊版本 |
| `v2-multi-islands/` | `legacy/multi-islands-v2/` | 舊版本 |

### D. package.json Workspaces 更新

```json
{
  "name": "machinenativeops",
  "version": "5.0.0",
  "private": true,
  "workspaces": [
    "src/core/*",
    "src/governance/*",
    "src/autonomous/*",
    "src/ai/*",
    "src/services/*",
    "src/apps/*",
    "tools/*"
  ],
  "scripts": {
    "dev": "node scripts/dev/start-dev-stack.js",
    "build": "npm run build --workspaces --if-present",
    "test": "npm run test --workspaces --if-present",
    "lint": "eslint 'src/**/*.{ts,tsx}' --fix",
    "verify-structure": "bash scripts/migration/verify-all.sh"
  }
}
```

### E. 相關資源與參考文件

#### 內部文檔

- [AI Behavior Contract](./.github/AI-BEHAVIOR-CONTRACT.md) - AI 代理行為規範
- [Copilot Instructions](./.github/copilot-instructions.md) - 技術指引
- [Governance Framework](./governance/00-vision-strategy/README.md) - 治理框架總覽
- [Documentation Index](./DOCUMENTATION_INDEX.md) - 文檔索引

#### 外部最佳實踐

- [Node.js Project Structure Best Practices](https://github.com/goldbergyoni/nodebestpractices#1-project-structure-practices)
- [Monorepo Tools Comparison](https://monorepo.tools/)
- [Semantic Versioning 2.0.0](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

### F. FAQ (常見問題)

#### Q1: 為什麼要進行這次大規模重構？

**A**: 當前的 52+ 頂層目錄結構已嚴重影響開發效率與新成員上手速度。這次重構是戰略性技術債務清理，長期收益遠大於短期成本。

#### Q2: 重構期間是否會中斷開發？

**A**: 會有 1 週的「功能凍結期」，但 bugfix 和文檔更新仍可繼續。我們會在分支上完成所有遷移並充分測試後再合併。

#### Q3: 現有 PR 如何處理？

**A**:

- 已合併的 PR 無需處理
- 待審查的 PR 建議暫緩合併，等待重構完成後 rebase
- 新的 PR 應基於重構後的結構

#### Q4: 如果遇到問題如何回退？

**A**: 我們在 `v4.0.0-pre-refactor` tag 處創建了備份。如遇嚴重問題，可執行：

```bash
git reset --hard v4.0.0-pre-refactor
```

#### Q5: 第三方工具整合會受影響嗎？

**A**: 可能會影響依賴絕對路徑的工具。我們會在 Phase 4 測試階段驗證所有第三方整合。

#### Q6: 重構後如何確保不回退？

**A**: 我們將建立自動化治理檢查（pre-commit hooks + CI checks），檢測不符合規範的新目錄或文件。

---

## ✅ 結論 | Conclusion

本次架構重構是 MachineNativeOps 專案進入成熟階段的必要步驟。透過建立清晰的 `src/` 主目錄、統一配置管理、標準化命名規範，我們將解決當前的技術債務，為未來的快速發展奠定堅實基礎。

### 關鍵成功因素

1. ✅ **完整的計劃與文檔** - 本文件提供詳細的實施路線圖
2. ✅ **自動化遷移工具** - 減少人為錯誤
3. ✅ **充分的測試與驗證** - 確保功能正常
4. ✅ **團隊溝通與培訓** - 確保平穩過渡
5. ✅ **持續的治理機制** - 防止問題復發

### 下一步行動

**立即行動項** (需要批准):

- [ ] 專案負責人審查本計劃
- [ ] 團隊會議討論並確認時間表
- [ ] 批准後創建 `refactor/architecture-restructuring` 分支
- [ ] 開始 Phase 0: 準備階段

**聯絡人**:

- 技術負責人: [指定負責人]
- 問題反饋: [Slack 頻道 / Email]

---

**文件維護**: 本文件將隨重構進度持續更新。  
**最後更新**: 2025-12-17  
**版本**: 1.0.0  
**狀態**: 📝 DRAFT - Awaiting Approval
