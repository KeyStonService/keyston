# SynergyMesh Documentation Portal

# 文檔入口

> 這是 SynergyMesh 所有文檔的統一入口。人類請從這裡開始，機器請讀
> [knowledge_index.yaml](./knowledge_index.yaml)。This is the unified entry
> point for all SynergyMesh documentation. Humans start here; machines read
> [knowledge_index.yaml](./knowledge_index.yaml).

## 🤖 For Agents & Automation 給智能體和自動化工具

**Machine-readable knowledge index / 機器可讀知識索引:**

- **[knowledge_index.yaml](./knowledge_index.yaml)** - Structured document
  catalog with metadata
- **[Living Knowledge Base](./LIVING_KNOWLEDGE_BASE.md)** - 活體知識庫設計：自動感知、建模、診斷、回饋
- Validate with: `python tools/docs/validate_index.py`

---

## 📚 Documentation Index 文檔索引

### 🏗️ Architecture 架構

核心架構設計和系統邊界定義。

| Document                                                                   | Description                                        |
| -------------------------------------------------------------------------- | -------------------------------------------------- |
| **[Architecture Layers](./architecture/layers.md)** ⭐                     | Five-layer architecture view with dependency rules |
| **[Repository Map](./architecture/repo-map.md)** ⭐                        | Semantic boundaries and decision guides            |
| [System Architecture](./architecture/SYSTEM_ARCHITECTURE.md)               | Four-layer microservices architecture              |
| [Deployment & Infrastructure](./architecture/DEPLOYMENT_INFRASTRUCTURE.md) | Docker, Kubernetes, CI/CD setup                    |
| [Code Quality Checks](./architecture/CODE_QUALITY_CHECKS.md)               | Quality tools configuration                        |
| [Security & Config Checks](./architecture/SECURITY_CONFIG_CHECKS.md)       | Security scanning and validation                   |

### 🤖 Automation & Agents 自動化與代理

AI 系統、自動化流程和智能代理。

| Document                                                          | Description                         |
| ----------------------------------------------------------------- | ----------------------------------- |
| **[Intelligent Automation](../automation/intelligent/README.md)** | Multi-agent AI code analysis system |
| **[Agent Services](../agent/README.md)**                          | Long-lifecycle business agents      |
| **[MCP Servers](../mcp-servers/README.md)**                       | LLM tool endpoints (MCP protocol)   |
| [Autonomous System](../automation/autonomous/README.md)           | Drone/self-driving framework        |
| [Auto-Assignment System](./AUTO_ASSIGNMENT_SYSTEM.md)             | Intelligent task assignment         |
| [Advanced Escalation](./ADVANCED_ESCALATION_SYSTEM.md)            | Multi-level escalation system       |

### 🏛️ Core Platform 核心平台

平台核心服務和執行環境。

| Document                                                           | Description                      |
| ------------------------------------------------------------------ | -------------------------------- |
| **[Core Services](../core/README.md)**                             | Platform core capabilities       |
| **[Runtime Environment](../runtime/README.md)**                    | Runtime hosting execution        |
| [Execution Engine](../core/execution_engine/README.md)             | Execution logic abstraction      |
| [Execution Architecture](../core/execution_architecture/README.md) | Execution topology design        |
| [Contract Service](../core/contract_service/README.md)             | Contract management microservice |
| [External Contracts](../contracts/README.md)                       | API specs and schemas            |

### ⚖️ Governance & Security 治理與安全

政策、規則、安全和合規。

| Document                                                  | Description                |
| --------------------------------------------------------- | -------------------------- |
| [Governance](../governance/README.md)                     | Policies, rules, SBOM      |
| [Vulnerability Management](./VULNERABILITY_MANAGEMENT.md) | CVE detection and response |
| [Secret Scanning](./SECRET_SCANNING.md)                   | Secret detection           |
| [Security Training](./SECURITY_TRAINING.md)               | Security best practices    |

### 🚀 Getting Started 快速入門

| Document                                    | Description                 |
| ------------------------------------------- | --------------------------- |
| [Quick Start Guide](./QUICK_START.md)       | Get up and running quickly  |
| [Island AI Setup](./ISLAND_AI_SETUP.md)     | Island AI integration       |
| [Integration Guide](./INTEGRATION_GUIDE.md) | External system integration |

### 🔄 CI/CD & Operations CI/CD 與運維

| Document                                          | Description                 |
| ------------------------------------------------- | --------------------------- |
| [Auto Review & Merge](./AUTO_REVIEW_MERGE.md)     | Automated PR workflow       |
| [Dynamic CI Assistant](./DYNAMIC_CI_ASSISTANT.md) | Interactive CI system       |
| [Cloud Delegation](./CLOUD_DELEGATION.md)         | Distributed task processing |

---

## 🎯 Quick Navigation 快速導航

### By Role 按角色

| Role                  | Start Here                                                  | Then Read                                                                                       |
| --------------------- | ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| **New Developer**     | [Quick Start](./QUICK_START.md)                             | [Examples](./EXAMPLES.md) → [Island AI Setup](./ISLAND_AI_SETUP.md)                             |
| **DevOps Engineer**   | [Deployment](./architecture/DEPLOYMENT_INFRASTRUCTURE.md)   | [CI/CD](./AUTO_REVIEW_MERGE.md) → [Monitoring](./architecture/CODE_QUALITY_CHECKS.md)           |
| **System Architect**  | [Architecture Layers](./architecture/layers.md)             | [Repo Map](./architecture/repo-map.md) → [System Design](./architecture/SYSTEM_ARCHITECTURE.md) |
| **Agent Developer**   | [Repo Map](./architecture/repo-map.md)                      | [Agent Services](../agent/README.md) → [MCP Servers](../mcp-servers/README.md)                  |
| **Security Engineer** | [Security Checks](./architecture/SECURITY_CONFIG_CHECKS.md) | [Vulnerability Mgmt](./VULNERABILITY_MANAGEMENT.md) → [Governance](../governance/README.md)     |

### By Domain 按領域

| Domain                 | Key Documents                                                                                                                     |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **Architecture**       | [layers.md](./architecture/layers.md), [repo-map.md](./architecture/repo-map.md)                                                  |
| **Autonomous Systems** | [autonomous/README.md](../automation/autonomous/README.md), [QUICKSTART.md](../automation/autonomous/docs-examples/QUICKSTART.md) |
| **AI/Agents**          | [intelligent/README.md](../automation/intelligent/README.md), [agent/README.md](../agent/README.md)                               |
| **Security**           | [SECURITY_CONFIG_CHECKS.md](./architecture/SECURITY_CONFIG_CHECKS.md), [governance/](../governance/)                              |
| **CI/CD**              | [AUTO_REVIEW_MERGE.md](./AUTO_REVIEW_MERGE.md), [DYNAMIC_CI_ASSISTANT.md](./DYNAMIC_CI_ASSISTANT.md)                              |

---

## 📋 Document Structure 文檔結構

```
docs/
├── README.md                  # 📍 You are here (Documentation Portal)
├── knowledge_index.yaml       # 🤖 Machine-readable index
├── architecture/              # 🏗️ Architecture documentation
│   ├── layers.md             # Architecture layers view
│   ├── repo-map.md           # Semantic boundaries
│   ├── SYSTEM_ARCHITECTURE.md
│   └── configuration/        # Config files & scripts
├── ci-cd/                    # CI/CD documentation
├── operations/               # Operations guides
├── security/                 # Security documentation
└── *.md                      # Feature-specific docs

tools/docs/
└── validate_index.py         # 🔍 Index validator
```

---

## 🆕 Recent Updates 最近更新

- **2025-11-30**: Phase 2 documentation system upgrade
  - Added `knowledge_index.yaml` for machine-readable document catalog
  - Added `validate_index.py` for index validation
  - Updated documentation portal structure

- **2025-11-30**: Phase 1 architecture documentation
  - Added architecture layers (`layers.md`) and repository map (`repo-map.md`)
  - Added boundary READMEs to key directories
  - Renamed `core/contracts/` to `core/contract_service/`

- **2025-11-21**: Initial comprehensive architecture documentation
  - System architecture design
  - Deployment and infrastructure guides
  - Code quality checks implementation

---

## 🤝 Contributing to Documentation 貢獻文檔

1. Check existing documentation for gaps
2. Follow the established format and style
3. **Update [knowledge_index.yaml](./knowledge_index.yaml)** when adding new
   docs
4. Run `python tools/docs/validate_index.py` before submitting
5. Submit a Pull Request

## 🔗 Related Resources 相關資源

- [Main README](../README.md) - Project overview
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute
- [Security Policy](../SECURITY.md) - Security practices

---

**Last Updated 最後更新**: 2025-11-30  
**Documentation Version 文檔版本**: 2.0.0  
**Maintained by 維護者**: SynergyMesh Development Team

---

## 🌟 系統概述

**Unmanned Island System**
是一個統一的企業級智能自動化平台，整合三大核心子系統：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        🏝️ Unmanned Island System                            │
│                              統一控制層                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐ │
│  │   🔷 SynergyMesh    │  │   ⚖️ Structural     │  │  🚁 Autonomous      │ │
│  │   Core Engine       │  │   Governance        │  │  Framework          │ │
│  │                     │  │                     │  │                     │ │
│  │  • AI 決策引擎      │  │  • Schema 命名空間  │  │  • 五骨架架構       │ │
│  │  • 認知處理器       │  │  • 十階段管道       │  │  • 無人機控制       │ │
│  │  • 服務註冊表       │  │  • SLSA 溯源        │  │  • 自駕車整合       │ │
│  │  • 安全機制         │  │  • 策略閘           │  │  • 安全監控         │ │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘ │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                           共用基礎設施層                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │ MCP 伺服器│ │ CI/CD    │ │ 監控告警 │ │ K8s 部署 │ │ 測試框架 │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 🎯 設計理念

| 原則           | 說明                                                 |
| -------------- | ---------------------------------------------------- |
| **統一入口**   | 單一配置檔 `synergymesh.yaml` 作為所有系統的真實來源 |
| **模組化設計** | 三大子系統獨立運作，透過統一接口協作                 |
| **零信任安全** | SLSA L3 溯源 + Sigstore 簽名 + 策略閘驗證            |
| **自主運維**   | AI 驅動的自動修復、智能派工、升級管理                |

---

## 🔷 核心子系統

### 1️⃣ SynergyMesh Core Engine（核心引擎）

雲原生智能業務自動化和數據編排平台。

```yaml
# 核心能力
capabilities:
  cognitive_processing: # 四層認知架構
    - perception # 感知層 - 遙測收集、異常偵測
    - reasoning # 推理層 - 因果圖構建、風險評分
    - execution # 執行層 - 多代理協作、同步屏障
    - proof # 證明層 - 審計鏈固化、SLSA 證據

  service_management: # 服務管理
    - discovery # 服務發現
    - health_monitoring # 健康監控
    - dependency_resolution # 依賴解析

  ai_engines: # AI 引擎
    - decision_engine # 決策引擎
    - hallucination_detector # 幻覺偵測
    - context_understanding # 上下文理解
```

**主要模組：**

- `core/unified_integration/` - 統一整合層（認知處理器、服務註冊表、配置優化器）
- `core/mind_matrix/` - 心智矩陣（執行長系統、多代理超圖）
- `core/safety_mechanisms/` - 安全機制（斷路器、緊急停止、回滾系統）
- `core/slsa_provenance/` - SLSA 溯源（證明管理、簽名驗證）

### 2️⃣ Structural Governance System（結構治理系統）

SuperRoot 風格的 Schema 命名空間與自主治理基礎設施。

```yaml
# Schema 命名空間
$schema: 'https://schema.synergymesh.io/docs-index/v1'

# 必要欄位
required_fields:
  - id, path, title, domain, layer, type
  - tags, owner, status, description

# 可選供應鏈欄位
optional_fields:
  - platforms, languages, provenance
  - sbom, signature, links, meta
```

**十階段治理管道：**

| 階段 | 名稱           | 說明                  |
| ---- | -------------- | --------------------- |
| 1    | Lint           | YAML/JSON 語法檢查    |
| 2    | Format         | 格式化規則驗證        |
| 3    | Schema         | JSON Schema 驗證      |
| 4    | Vector Test    | 測試向量驗證          |
| 5    | Policy Gate    | OPA/Conftest 策略檢查 |
| 6    | K8s Validation | Kubernetes 清單驗證   |
| 7    | SBOM           | 軟體物料清單生成      |
| 8    | Provenance     | SLSA 證據注入         |
| 9    | Cosign Sign    | Sigstore 無密鑰簽名   |
| 10   | Audit          | 審計事件記錄          |

### 🏗️ 治理工具

- `tools/docs/validate_index.py` - Schema 驗證器
- `tools/docs/scan_repo_generate_index.py` - 倉庫掃描生成索引
- `tools/docs/provenance_injector.py` - SLSA L3 證據注入、SBOM 生成

### 4️⃣ 活體知識庫（Living Knowledge Base）

> 讓系統自己感知變化、重建自身結構、自我檢查，並主動回報狀態。

本模組**不是**人工智慧助理、命令列工具、Copilot 或聊天機器人。  
它的唯一目的，是讓程式碼倉庫「知道自己現在長怎樣、哪裡有問題」，並用**機器可讀的方式**表達出來。

```yaml
# 知識循環四層次
knowledge_cycle:
  perception: # 感知層 - 偵測變化
    - Git 提交紀錄（檔案新增 / 修改 / 刪除）
    - GitHub Actions 工作流結果
    - 定期排程掃描

  modeling: # 建模層 - 重建結構
    outputs:
      - docs/generated-mndoc.yaml # 系統說明書
      - docs/knowledge-graph.yaml # 結構關係圖
      - docs/superroot-entities.yaml # SuperRoot ontology 編碼

  self_diagnosis: # 自我診斷層 - 找出問題
    checks:
      - 孤兒元件（無關聯的 Component）
      - 死設定（未使用的 Config）
      - 重疊工作流
      - 斷鏈文件
    output: docs/knowledge-health-report.yaml

  action: # 行動層 - 回報狀態
    - 更新 docs/KNOWLEDGE_HEALTH.md 儀表板
    - 必要時自動開 GitHub Issue
```

**目錄佈局：**

| 目錄         | 用途                                         |
| ------------ | -------------------------------------------- |
| `knowledge/` | 純知識資料層（YAML/JSON），不放程式碼        |
| `runtime/`   | 操作知識的程式碼：載入、建模、診斷、輸出報告 |
| `pipelines/` | 把 runtime 組合成完整活體流程                |
| `docs/`      | 給人類看的說明與健康報告                     |

📚 詳見 [活體知識庫設計說明](docs/LIVING_KNOWLEDGE_BASE.md)

### 3️⃣ Autonomous Framework（自主系統框架）

完整的五骨架無人機/自駕車自主系統框架。

```
五骨架架構 (Five-Skeleton Architecture)
├── 1. 架構穩定性骨架 (Architecture Stability) - C++ + ROS 2
│   └── 即時飛控 (100Hz)、IMU 融合、PID 控制器
├── 2. API 治理邊界骨架 (API Governance) - Python
│   └── 模組責任矩陣、API 合約驗證、依賴鏈檢查
├── 3. 測試與兼容性骨架 (Testing & Compatibility) - Python + YAML
│   └── 自動化測試套件、跨版本兼容測試
├── 4. 安全性與觀測骨架 (Security & Observability) - Go
│   └── 分散式事件日誌、安全監控、追蹤 ID
└── 5. 文件與範例骨架 (Documentation & Examples) - YAML + Markdown
    └── 治理矩陣定義、完整 API 文檔、快速入門指南
```

---

## 📁 統一目錄結構

```
unmanned-island/
│
├── 📄 synergymesh.yaml              # 🔑 統一主配置入口
│
├── 📁 core/                         # 🏛️ 核心平台服務
│   ├── unified_integration/         # 統一整合層
│   │   ├── cognitive_processor.py   # 認知處理器
│   │   ├── service_registry.py      # 服務註冊表
│   │   └── configuration_optimizer.py # 配置優化器
│   ├── mind_matrix/                 # 心智矩陣
│   ├── lifecycle_systems/           # 生命週期系統
│   ├── safety_mechanisms/           # 安全機制
│   ├── slsa_provenance/             # SLSA 溯源
│   ├── contract_service/            # 合約管理服務 (L1)
│   ├── ai_decision_engine.py        # AI 決策引擎
│   └── ...                          # 其他核心模組
│
├── 📁 automation/                   # 🤖 自動化模組
│   ├── intelligent/                 # 智能自動化
│   ├── autonomous/                  # 五骨架自主系統
│   ├── architect/                   # 架構分析修復
│   └── hyperautomation/             # 超自動化策略
│
├── 📁 config/                       # ⚙️ 配置中心
│   ├── system-manifest.yaml         # 系統宣告
│   ├── unified-config-index.yaml    # 統一配置索引 (v3.0.0)
│   ├── system-module-map.yaml       # 模組映射
│   ├── ai-constitution.yaml         # AI 憲法
│   ├── safety-mechanisms.yaml       # 安全機制
│   └── ...                          # 其他配置
│
├── 📁 governance/                   # ⚖️ 治理與策略
│   ├── schemas/                     # JSON Schema 定義
│   ├── policies/                    # OPA/Conftest 策略
│   ├── sbom/                        # 軟體物料清單
│   └── audit/                       # 審計配置
│
├── 📁 infrastructure/               # 🏗️ 基礎設施
│   ├── kubernetes/                  # K8s 部署清單
│   ├── monitoring/                  # 監控告警
│   ├── canary/                      # 金絲雀部署
│   └── drift/                       # 漂移檢測
│
├── 📁 mcp-servers/                  # 🔌 MCP 伺服器
│   ├── code-analyzer.js             # 程式碼分析
│   ├── security-scanner.js          # 安全掃描
│   └── slsa-validator.js            # SLSA 驗證
│
├── 📁 tools/                        # 🔧 工具腳本
│   └── cli/                         # Admin Copilot CLI
│       ├── bin/admin-copilot.js     # CLI 主程式
│       └── README.md                # CLI 文檔
│
├── 📁 apps/                         # 📱 應用程式
│   └── web/                         # 🌐 Web 前端與代碼分析 API
│       ├── src/                     # React 前端原始碼
│       ├── services/                # Python 後端服務
│       │   ├── api.py               # FastAPI 服務
│       │   ├── code_analyzer.py     # 代碼分析引擎
│       │   └── models.py            # 數據模型
│       ├── tests/                   # 測試套件
│       ├── k8s/                     # Kubernetes 部署配置
│       ├── deploy/                  # 部署配置
│       ├── Dockerfile               # 前端容器配置
│       └── Dockerfile.api           # API 容器配置
│
├── 📁 agent/                        # 🤖 代理服務
├── 📁 frontend/                     # 🎨 前端應用
├── 📁 tests/                        # 🧪 測試套件
├── 📁 ops/                          # 📋 運維資源
├── 📁 docs/                         # 📚 文檔
├── 📁 shared/                       # 📦 共用資源
├── 📁 legacy/                       # 📜 舊版存檔
│
└── 📁 .github/                      # 🔄 GitHub 配置
    └── workflows/                   # CI/CD 工作流
```

---

## 🚀 快速開始

### 環境需求

```bash
# 必要環境
Node.js >= 18.0.0
Python >= 3.10
npm >= 8.0.0

# 可選環境（自主系統）
ROS 2 Humble
Go >= 1.20
C++ 17 (GCC 11+)
```

### 安裝

```bash
# 克隆倉庫
git clone https://github.com/SynergyMesh-admin/Unmanned-Island.git
cd unmanned-island

# 安裝依賴
npm install

# 驗證安裝
npm run lint
npm run test
```

### 核心服務啟動

```bash
# 啟動合約管理服務 (L1)
cd core/contract_service/contracts-L1/contracts
npm install && npm run build
npm start

# 啟動 MCP 伺服器
cd mcp-servers
npm install && npm start

# 驗證配置
python tools/docs/validate_index.py --verbose
```

### 🖥️ Admin Copilot CLI (Public Preview)

<div align="center">

**The power of Admin Copilot, now in your terminal.**

</div>

Admin Copilot
CLI 將 AI 驅動的程式碼分析與操作能力帶入命令列，使系統可透過自然語言理解自身程式碼，並執行建置、偵錯與維護流程。

#### 核心特色

| 特色               | 說明                                   |
| ------------------ | -------------------------------------- |
| 🖥️ **終端機原生**  | 直接在命令列中與 AI 協作，無需切換工具 |
| 🔗 **GitHub 整合** | 使用自然語言存取倉庫、問題和拉取請求   |
| 🤖 **代理能力**    | AI 協作者可以計劃和執行複雜任務        |
| 🔌 **MCP 擴展**    | 支援自訂 MCP 伺服器擴展功能            |
| ✅ **完全控制**    | 每個操作在執行前都會預覽               |

#### 快速安裝

```bash
# 安裝 Admin Copilot CLI
cd tools/cli
npm install
npm link

# 啟動 CLI
admin-copilot
# 或使用簡短別名
smcli
```

#### 可用命令

| 命令              | 說明                 |
| ----------------- | -------------------- |
| `chat`            | 開始互動式 AI 對話   |
| `analyze [path]`  | 分析指定目錄的程式碼 |
| `fix`             | 修復程式碼問題       |
| `explain <query>` | 解釋程式碼或概念     |
| `generate <desc>` | 從自然語言生成程式碼 |
| `review [path]`   | 程式碼最佳實踐審查   |
| `test [path]`     | 為程式碼生成測試     |

#### 斜線命令（對話模式）

| 命令        | 說明                                       |
| ----------- | ------------------------------------------ |
| `/login`    | 使用 GitHub 認證                           |
| `/logout`   | 登出 GitHub                                |
| `/model`    | 選擇 AI 模型 (Claude Sonnet 4.5, GPT-5 等) |
| `/feedback` | 提交回饋                                   |
| `/help`     | 顯示幫助                                   |
| `/exit`     | 退出 CLI                                   |

#### 使用範例

```bash
# 開始 AI 對話
admin-copilot chat

# 分析程式碼
admin-copilot analyze ./src

# 自動修復問題
admin-copilot fix --auto

# 解釋概念
smcli explain "What is SLSA provenance?"

# 生成程式碼
admin-copilot generate "Create a REST API endpoint" --language typescript

# 審查程式碼
admin-copilot review ./src/controllers
```

#### 認證方式

1. **裝置流程（推薦）**：執行 `/login` 並按照指示操作
2. **個人存取令牌**：
   - 訪問 <https://github.com/settings/personal-access-tokens/new>
   - 新增「Copilot Requests」權限
   - 設定環境變數 `GH_TOKEN` 或 `GITHUB_TOKEN`

📚 詳見 [Admin Copilot CLI 完整文檔](docs/ADMIN_COPILOT_CLI.md)

### Docker 部署

```bash
# 開發環境
docker-compose -f docker-compose.dev.yml up -d

# 生產環境
docker-compose up -d
```

---

## 🌐 Web 前端與代碼分析 API (`apps/web`)

### 概述

`apps/web`
是 SynergyMesh 平台的企業級代碼分析服務，實現了多語言、多策略的智能代碼分析功能，包含：

- **React 前端 UI** - 架構視覺化與系統界面
- **FastAPI 後端** - 代碼分析 API 服務
- **完整測試套件** - 80%+ 覆蓋率

### 安裝與設定

#### 1. 前端安裝

```bash
cd apps/web

# 安裝 Node.js 依賴
npm install

# 開發模式（熱重載，使用 esbuild）
npm run dev
# 或直接執行
node scripts/build.mjs

# 生產構建
npm run build
# 或直接執行
node scripts/build.mjs --production
```

#### 2. 後端安裝

```bash
cd apps/web

# 創建虛擬環境（推薦）
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 安裝 Python 依賴
pip install -r requirements.txt

# 驗證安裝
python -c "import services.code_analyzer; print('OK')"
```

### 測試

```bash
cd apps/web

# 運行所有測試
pytest

# 單元測試
pytest -m unit

# 集成測試
pytest -m integration

# 性能測試
pytest -m performance

# 查看覆蓋率報告
pytest --cov=services --cov-report=html
```

### API 服務

#### 啟動服務

```bash
cd apps/web

# 使用 Docker Compose 啟動完整環境
docker-compose -f docker-compose.api.yml up -d

# 查看日誌
docker-compose -f docker-compose.api.yml logs -f code-analysis-api

# 訪問 API 文檔
open http://localhost:8000/api/docs
```

#### API 端點

| 端點                   | 方法   | 說明             |
| ---------------------- | ------ | ---------------- |
| `/api/v1/analyze`      | POST   | 提交代碼分析任務 |
| `/api/v1/analyze/{id}` | GET    | 獲取分析結果     |
| `/api/v1/analyze`      | GET    | 列出分析任務     |
| `/api/v1/analyze/{id}` | DELETE | 刪除分析記錄     |
| `/api/v1/metrics`      | GET    | 獲取系統指標     |
| `/healthz`             | GET    | 健康檢查         |

#### 使用範例

```bash
# 提交分析任務
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "repository": "https://github.com/example/repo",
    "commit_hash": "abc123",
    "strategy": "STANDARD"
  }'

# 獲取分析結果
curl http://localhost:8000/api/v1/analyze/{analysis_id}

# 查看系統指標
curl http://localhost:8000/api/v1/metrics
```

### 代碼分析引擎

#### 支援語言

| 語言                  | 狀態 | 說明     |
| --------------------- | ---- | -------- |
| Python                | ✅   | 完整支援 |
| JavaScript/TypeScript | ✅   | 完整支援 |
| Go                    | ✅   | 完整支援 |
| Rust                  | ✅   | 完整支援 |
| Java                  | ✅   | 完整支援 |
| C++                   | ✅   | 完整支援 |

#### 分析策略

| 策略            | 耗時      | 說明             |
| --------------- | --------- | ---------------- |
| `QUICK`         | < 1 分鐘  | 快速掃描常見問題 |
| `STANDARD`      | 1-5 分鐘  | 標準分析（推薦） |
| `DEEP`          | 5-30 分鐘 | 深度分析         |
| `COMPREHENSIVE` | 30+ 分鐘  | 全面分析所有面向 |

#### 檢測能力

**安全漏洞（6 類）**：

- 硬編碼密鑰
- SQL 注入
- XSS 漏洞
- CSRF 漏洞
- 不安全的反序列化
- 密碼學弱點

**代碼質量**：

- 圈複雜度
- 代碼重複率
- 類型註解缺失

**性能問題**：

- N+1 查詢
- 低效循環

### Docker 容器化

#### 前端容器

```bash
cd apps/web

# 構建前端鏡像
docker build -t synergymesh-web:latest .

# 運行容器
docker run -d -p 3002:3002 synergymesh-web:latest
```

#### API 容器

```bash
cd apps/web

# 構建 API 鏡像
docker build -f Dockerfile.api -t code-analysis-api:2.0.0 .

# 運行容器
docker run -d -p 8000:8000 code-analysis-api:2.0.0
```

#### Docker Compose 完整環境

```bash
cd apps/web

# 啟動所有服務（API + PostgreSQL + Redis + Prometheus + Grafana）
docker-compose -f docker-compose.api.yml up -d

# 停止服務
docker-compose -f docker-compose.api.yml down
```

### Kubernetes 部署

```bash
cd apps/web

# 應用 Kubernetes 配置
kubectl apply -f k8s/deployment-api.yaml
kubectl apply -f deploy/

# 查看部署狀態
kubectl get pods -n code-analysis
kubectl get svc -n code-analysis

# 查看日誌
kubectl logs -f deployment/code-analysis-api -n code-analysis

# 擴展副本
kubectl scale deployment code-analysis-api --replicas=5 -n code-analysis
```

### 性能指標

| 指標       | 目標值       | 實際值          |
| ---------- | ------------ | --------------- |
| 分析速度   | ≥ 1000 行/秒 | 1000-5000 行/秒 |
| 準確率     | ≥ 90%        | > 95%           |
| 測試覆蓋率 | ≥ 80%        | 80-85%          |
| 記憶體使用 | ≤ 512 MB     | < 512 MB        |

📚 詳見 [apps/web/README.md](apps/web/README.md) 與
[apps/web/PHASE2_IMPROVEMENTS.md](apps/web/PHASE2_IMPROVEMENTS.md)

---

## 🛠️ 核心功能

### 🤖 智能自動化

| 功能           | 說明                             | 入口                                 |
| -------------- | -------------------------------- | ------------------------------------ |
| 自動程式碼審查 | PR 自動審查與合併                | `.github/workflows/`                 |
| 智能派工系統   | 問題自動分配與負載均衡           | `core/contract_service/`             |
| 進階升級系統   | 五級升級階梯 (L1 Auto → L5 客服) | `docs/ADVANCED_ESCALATION_SYSTEM.md` |
| Auto-Fix Bot   | 自動修復 CI 失敗                 | `config/auto-fix-bot.yml`            |

### 🔒 安全與合規

| 功能         | 說明                  | 入口                    |
| ------------ | --------------------- | ----------------------- |
| SLSA L3 溯源 | 構建認證與簽名        | `core/slsa_provenance/` |
| Schema 驗證  | JSON Schema 合規檢查  | `governance/schemas/`   |
| 策略閘       | OPA/Conftest 策略執行 | `governance/policies/`  |
| SBOM 生成    | 軟體物料清單          | `governance/sbom/`      |

### 📊 監控與觀測

| 功能            | 說明                 | 入口                           |
| --------------- | -------------------- | ------------------------------ |
| 動態 CI 助手    | 每個 CI 都有獨立客服 | `docs/DYNAMIC_CI_ASSISTANT.md` |
| Prometheus 監控 | 指標收集與告警       | `infrastructure/monitoring/`   |
| 漂移檢測        | 基礎設施配置漂移     | `infrastructure/drift/`        |

---

## 🤝 互動命令

### CI 客服互動

```bash
# 特定 CI 分析
@copilot analyze Core Services CI     # 深度分析
@copilot fix Core Services CI         # 自動修復建議
@copilot help Integration CI          # 查看文檔

# 全局命令
@copilot 幫我分析                      # 分析所有 CI
@copilot 環境檢查                      # 環境診斷
```

### 治理工具

```bash
# 驗證文檔索引
python tools/docs/validate_index.py --verbose

# 掃描倉庫生成索引
python tools/docs/scan_repo_generate_index.py --dry-run

# 生成 SLSA 溯源
python tools/docs/provenance_injector.py --generate-provenance

# 生成 SBOM
python tools/docs/provenance_injector.py --generate-sbom
```

---

## 📚 文檔導航

### 核心文檔

| 文檔                                    | 說明               |
| --------------------------------------- | ------------------ |
| [系統架構](docs/architecture/)          | 架構設計與層級說明 |
| [快速入門](docs/QUICK_START.md)         | 快速開始指南       |
| [API 文檔](docs/AUTO_ASSIGNMENT_API.md) | REST API 參考      |
| [運維手冊](docs/operations/)            | 運維與部署指南     |

### 功能文檔

| 文檔                                               | 說明          |
| -------------------------------------------------- | ------------- |
| [自動審查與合併](docs/AUTO_REVIEW_MERGE.md)        | PR 自動化流程 |
| [智能派工系統](docs/AUTO_ASSIGNMENT_SYSTEM.md)     | 任務分配機制  |
| [進階升級系統](docs/ADVANCED_ESCALATION_SYSTEM.md) | 五級升級階梯  |
| [動態 CI 助手](docs/DYNAMIC_CI_ASSISTANT.md)       | CI 互動客服   |

### 治理文檔

| 文檔                                        | 說明              |
| ------------------------------------------- | ----------------- |
| [Schema 定義](governance/schemas/)          | JSON Schema 規範  |
| [策略配置](governance/policies/)            | OPA/Conftest 策略 |
| [審計格式](governance/audit/)               | 審計事件定義      |
| [知識索引](docs/knowledge_index.yaml)       | 機器可讀索引      |
| [活體知識庫](docs/LIVING_KNOWLEDGE_BASE.md) | 系統自我感知設計  |

### 應用程式文檔

| 文檔                                            | 說明               |
| ----------------------------------------------- | ------------------ |
| [Web 前端與 API](apps/web/README.md)            | 企業級代碼分析服務 |
| [Phase 2 改進](apps/web/PHASE2_IMPROVEMENTS.md) | API 與部署改進詳情 |

---

## 🔄 CI/CD

### 工作流程

| 工作流              | 觸發條件 | 說明           |
| ------------------- | -------- | -------------- |
| `core-services.yml` | PR/Push  | 核心服務測試   |
| `integration.yml`   | PR/Push  | 整合測試       |
| `apply.yaml`        | PR       | 十階段治理管道 |
| `auto-review.yml`   | PR       | 自動審查與合併 |

### 品質閘

```yaml
quality_gates:
  test_coverage: '>= 80%'
  lint_errors: 0
  security_vulnerabilities: 0
  schema_validation: pass
  policy_check: pass
```

---

## 🎛️ 全局配置總覽

本系統採用統一配置管理，以下是所有核心配置檔案的完整索引：

### 主配置入口

| 配置檔案                           | 說明                | 用途                       |
| ---------------------------------- | ------------------- | -------------------------- |
| `synergymesh.yaml`                 | 🔑 統一主配置入口   | 所有系統配置的唯一真實來源 |
| `config/system-manifest.yaml`      | 系統宣告清單        | 系統啟動與元件協調         |
| `config/unified-config-index.yaml` | 統一配置索引 v3.0.0 | 配置整合與目錄合併指南     |
| `config/system-module-map.yaml`    | 模組映射            | 目錄結構與元件映射         |

### AI 與治理配置

| 配置檔案                                  | 說明                            |
| ----------------------------------------- | ------------------------------- |
| `config/ai-constitution.yaml`             | AI 最高指導憲章（三層憲法體系） |
| `config/agents/team/virtual-experts.yaml` | 虛擬專家團隊配置                |
| `config/safety-mechanisms.yaml`           | 安全機制配置                    |
| `config/topology-mind-matrix.yaml`        | 心智矩陣拓撲配置                |

### 自動化與運維配置

| 配置檔案                            | 說明                       |
| ----------------------------------- | -------------------------- |
| `config/drone-config.yml`           | 無人機編隊與自動化系統配置 |
| `config/island-control.yml`         | 多語言無人之島系統配置     |
| `config/cloud-agent-delegation.yml` | 雲端代理程式委派配置       |
| `config/auto-fix-bot.yml`           | Auto-Fix Bot 自動修復配置  |
| `config/monitoring.yaml`            | 監控配置                   |
| `config/ci-error-handler.yaml`      | CI 錯誤處理配置            |

---

## 👨‍💼 虛擬專家團隊

系統內建六位高級虛擬專家，提供全方位技術諮詢：

| 專家              | 角色        | 專長領域                                 | 經驗  |
| ----------------- | ----------- | ---------------------------------------- | ----- |
| 🧠 Dr. Alex Chen  | AI 架構師   | 決策引擎、神經網路、ML 系統              | 15 年 |
| 💬 Sarah Wong     | NLP 專家    | 大語言模型、對話系統、Prompt Engineering | 12 年 |
| 🔐 Marcus Johnson | 安全架構師  | 零信任架構、滲透測試、合規框架           | 18 年 |
| 🗄️ Li Wei         | 數據庫專家  | PostgreSQL 優化、分佈式數據庫、數據倉庫  | 16 年 |
| 🚀 Emma Thompson  | DevOps 專家 | K8s 編排、GitOps、混沌工程               | 14 年 |
| 🏗️ James Miller   | 系統架構師  | 微服務、事件驅動、領域驅動設計           | 20 年 |

### 領域專家映射

```yaml
domain_mapping:
  DATABASE:     primary: Li Wei          secondary: [James Miller]
  SECURITY:     primary: Marcus Johnson  secondary: [Emma Thompson]
  ARCHITECTURE: primary: James Miller    secondary: [Alex Chen, Emma Thompson]
  AI_ML:        primary: Alex Chen       secondary: [Sarah Wong]
  NLP:          primary: Sarah Wong      secondary: [Alex Chen]
  DEVOPS:       primary: Emma Thompson   secondary: [James Miller]
```

---

## 🤖 智能代理服務

### 業務代理 (`services/agents/`)

長生命週期業務代理，負責自動化任務執行和系統協調：

| 代理                       | 職責       | 說明                                   |
| -------------------------- | ---------- | -------------------------------------- |
| **Auto-Repair Agent**      | 自動修復   | 自動檢測和修復程式碼問題，追蹤修復歷史 |
| **Code Analyzer Agent**    | 程式碼分析 | 深度品質分析、複雜度評估、安全路徑識別 |
| **Dependency Manager**     | 依賴管理   | 版本管理、漏洞檢測、升級建議           |
| **Orchestrator**           | 代理編排   | 多代理任務協調、工作流編排、通訊管理   |
| **Vulnerability Detector** | 漏洞檢測   | CVE 資料庫比對、安全報告生成           |

### 智能自動化代理 (`automation/intelligent/agents/`)

| 代理                     | 職責           |
| ------------------------ | -------------- |
| `recognition_server.py`  | 意圖識別伺服器 |
| `task_executor.py`       | 任務執行器     |
| `visualization_agent.py` | 視覺化代理     |

---

## 🚁 無人機系統配置

### 無人機編隊架構

系統支援多無人機編隊配置，整合自動駕駛與程式碼生成功能：

```yaml
drone_fleet:
  coordinator: # 🎯 主協調器 - 優先級 1
    name: '主協調器'
    auto_start: true

  autopilot: # 🛫 自動駕駛 - 優先級 2
    name: '自動駕駛'
    auto_start: true

  code_generator: # 💻 代碼生成器 - 優先級 3
    name: '代碼生成器'
    auto_start: false

  deployment_drone: # 🚀 部署無人機 - 優先級 4
    name: '部署無人機'
    auto_start: false
```

### 多語言島嶼系統

五大技術島嶼並行運作，各司其職：

| 島嶼                         | 技術棧       | 核心能力                                       |
| ---------------------------- | ------------ | ---------------------------------------------- |
| 🦀 **Rust 性能核心島**       | Rust 1.70+   | 性能監控、安全守護、數據管道、系統編排         |
| 🌊 **Go 雲原生服務島**       | Go 1.20+     | API 閘道、微服務網格、容器管理、分散式快取     |
| ⚡ **TypeScript 全棧開發島** | TS 5.0+      | Web 儀表板、API 客戶端生成、即時監控、開發工具 |
| 🐍 **Python AI 數據島**      | Python 3.10+ | AI 程式碼助手、數據分析、ML 管道、自動化腳本   |
| ☕ **Java 企業服務島**       | Java 17+     | 企業整合、消息佇列、批處理、遺留系統橋接       |

### 島嶼通信協議

```yaml
bridges:
  protocols: [grpc, rest, websocket, message_queue]
  timeout: 30s
  retry_policy:
    max_retries: 3
    backoff_multiplier: 2
```

---

## 🚗 自主系統框架（無人駕駛/無人機）

### 五骨架自治架構

完整的無人機/自駕車高自治系統框架，採用五骨架設計：

```
┌─────────────────────────────────────────────────────────────────┐
│                    無人機自治系統 - 五大骨架                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐    │
│  │  1️⃣ 架構穩定性骨架 (C++ + ROS 2)                       │    │
│  │  • Flight Controller • Sensor Fusion                  │    │
│  │  • Real-time Control Loop (100Hz)                     │    │
│  └───────────────────────────────────────────────────────┘    │
│  ┌───────────────────────────────────────────────────────┐    │
│  │  2️⃣ API 規格與治理邊界骨架 (Python)                     │    │
│  │  • Module Responsibility Matrix                       │    │
│  │  • API Contract Validation • Dependency Chain Check   │    │
│  └───────────────────────────────────────────────────────┘    │
│  ┌───────────────────────────────────────────────────────┐    │
│  │  3️⃣ 測試與兼容性骨架 (Python + YAML)                    │    │
│  │  • Automated Test Suites                              │    │
│  │  • Compatibility Matrix Validation                    │    │
│  └───────────────────────────────────────────────────────┘    │
│  ┌───────────────────────────────────────────────────────┐    │
│  │  4️⃣ 安全性與觀測骨架 (Go)                               │    │
│  │  • Distributed Event Logging • Safety Monitoring      │    │
│  │  • Trace ID & Distributed Tracing                     │    │
│  └───────────────────────────────────────────────────────┘    │
│  ┌───────────────────────────────────────────────────────┐    │
│  │  5️⃣ 文件與範例骨架 (YAML + Markdown)                    │    │
│  │  • Governance Matrix • API Documentation              │    │
│  │  • Quickstart Guides                                  │    │
│  └───────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 性能指標

| 指標         | 目標值  | 實際值 |
| ------------ | ------- | ------ |
| 控制迴圈延遲 | < 10ms  | ~5ms   |
| API 響應時間 | < 100ms | ~50ms  |
| 事件處理延遲 | < 1ms   | ~0.5ms |
| 系統可用性   | > 99.9% | 99.95% |

---

## ⚙️ 超自動化策略

### 自動化層級架構

```
automation/
├── intelligent/      # 智能自動化 - 任務編排、意圖理解
├── autonomous/       # 自主系統 - 五骨架框架
├── architect/        # 架構師 - 架構分析與修復
└── hyperautomation/  # 超自動化 - UAV 治理、高級策略
```

### 雲端代理委派

支援多雲端提供商的智能任務委派：

| 提供商    | 權重 | 主要任務             |
| --------- | ---- | -------------------- |
| **AWS**   | 40%  | 程式碼分析、安全掃描 |
| **GCP**   | 35%  | 自動修復、報告生成   |
| **Azure** | 25%  | 性能優化             |

### 任務路由策略

```yaml
task_routing:
  code-analysis:    provider: aws    priority: high
  auto-fix:         provider: gcp    priority: high
  optimization:     provider: azure  priority: medium
  security-scan:    provider: aws    priority: critical
  report-generation: provider: gcp   priority: low
```

---

## 🏛️ AI 治理憲章

系統採用三層憲法體系確保 AI 行為合規：

### 第一層：根本法則（不可違反）

| 法則          | 名稱         | 說明                             | 違規處理 |
| ------------- | ------------ | -------------------------------- | -------- |
| **Law Zero**  | 存在目的法則 | AI 存在目的是服務人類            | 系統停止 |
| **Law One**   | 不傷害法則   | 不得傷害人類或允許傷害發生       | 立即停止 |
| **Law Two**   | 服從法則     | 遵守有效指令（除非違反更高法則） | 升級處理 |
| **Law Three** | 自我保護法則 | 保護自身存在與完整性             | 記錄告警 |

### 護欄系統

```yaml
guardrails:
  safety: # 有害內容偵測、PII 偵測、危險操作偵測
  compliance: # GDPR、SOC2、HIPAA 合規
  ethics: # 偏見偵測、公平性檢查、透明度檢查
```

---

## 📊 能力矩陣總覽

| 能力分類       | 提供者                                                | 功能                         |
| -------------- | ----------------------------------------------------- | ---------------------------- |
| **認知處理**   | `core/unified_integration/cognitive_processor.py`     | 感知、推理、執行、證明       |
| **服務管理**   | `core/unified_integration/service_registry.py`        | 發現、健康監控、依賴解析     |
| **配置管理**   | `core/unified_integration/configuration_optimizer.py` | 驗證、漂移檢測、優化         |
| **安全合規**   | `core/slsa_provenance/`, `core/safety_mechanisms/`    | 認證、漏洞偵測、安全檢查     |
| **程式碼分析** | `mcp-servers/code-analyzer.js`                        | 靜態分析、架構分析、性能分析 |
| **代理服務**   | `services/agents/`                                    | 自動修復、漏洞偵測、編排     |

---

## 📄 授權

本專案採用 [MIT License](LICENSE) 授權。

---

## 🙏 致謝

- [SynergyMesh](https://github.com/SynergyMesh/SynergyMesh) - 核心引擎基礎
- [Sigstore](https://sigstore.dev/) - 無密鑰簽名
- [OPA](https://www.openpolicyagent.org/) - 策略引擎
- [SLSA](https://slsa.dev/) - 供應鏈安全框架

---

<div align="center">

**🏝️ Unmanned Island System**

_讓開發更高效，讓程式碼更完美！_

[GitHub](https://github.com/SynergyMesh-admin/Unmanned-Island) •
[Issues](https://github.com/SynergyMesh-admin/Unmanned-Island/issues) •
[Discussions](https://github.com/SynergyMesh-admin/Unmanned-Island/discussions)

</div>
