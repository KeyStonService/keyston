# 🏝️ Unmanned Island System

<div align="center">

![Version](https://img.shields.io/badge/version-4.0.0-blue?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue?style=for-the-badge&logo=typescript)
![Python](https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge&logo=python)
![Node.js](https://img.shields.io/badge/Node.js-20+-green?style=for-the-badge&logo=node.js)

**🚀 次世代雲原生智能自動化平台**

_整合 SynergyMesh 核心引擎 + 結構治理系統 + 無人之島自主框架_

[快速開始](#-快速開始) • [系統架構](#-系統概述) • [核心功能](#-核心功能) •
[全局優化](#-全局優化推理系統global-optimization-reasoning) • [重構系統](#-refactor-playbook-system) • [活體知識庫](#4️⃣-活體知識庫living-knowledge-base) • [Admin Copilot CLI](#-admin-copilot-cli-public-preview) • [Web 應用](#-web-前端與代碼分析-api-appsweb) •
[配置總覽](#️-全局配置總覽) • [虛擬專家](#-虛擬專家團隊) • [智能代理](#-智能代理服務) •
[無人機系統](#-無人機系統配置) • [自主框架](#-自主系統框架無人駕駛無人機) •
[文檔](#-文檔導航) • [English](README.en.md)

</div>

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

## 🗺️ 技術路線規劃圖 | Technical Roadmap

### 📍 當前狀態 (v1.0.0)

```
✅ 已完成模組 (Production Ready)
├── 🔷 SynergyMesh Core Engine
│   ├── ✅ 統一整合層 (Unified Integration)
│   ├── ✅ 心智矩陣 (Mind Matrix)
│   ├── ✅ 安全機制 (Safety Mechanisms)
│   ├── ✅ SLSA L3 溯源 (Provenance)
│   └── ✅ 合約服務 L1 (Contract Service)
│
├── ⚖️ Structural Governance
│   ├── ✅ 23 維度治理矩陣
│   ├── ✅ Schema 命名空間
│   ├── ✅ 十階段治理管道
│   ├── ✅ 語言治理儀表板
│   └── ✅ 架構優化推理系統
│
├── 🚁 Autonomous Framework
│   ├── ✅ 11 個架構骨架
│   ├── ✅ 五骨架自主系統
│   └── ✅ 無人機配置系統
│
├── 📦 Build & Deployment System (NEW!)
│   ├── ✅ Windows 安裝程式 (EXE/MSI)
│   ├── ✅ macOS 安裝程式 (DMG/PKG/Homebrew)
│   ├── ✅ Linux 套件 (AppImage/DEB/RPM)
│   ├── ✅ Docker 容器化
│   ├── ✅ CI/CD 自動化 (GitHub Actions)
│   └── ✅ 完整文檔 (INSTALL/BUILD/RELEASE)
│
└── 🤖 Island AI Multi-Agent System
    ├── ✅ Stage 1: 6 個基礎 Agent
    └── 🔄 Stage 2-4: 進行中
```

### 🎯 發展階段

#### ✅ Phase 1: 核心基礎建設 (Completed)
- [x] SynergyMesh 核心引擎
- [x] 結構治理系統
- [x] 自主系統框架
- [x] 基礎文檔與測試

#### ✅ Phase 2: 智能化與自動化 (Completed)
- [x] Island AI Agent 系統 (Stage 1)
- [x] 語言治理自動化
- [x] 全局優化推理系統
- [x] Refactor Playbook 系統

#### ✅ Phase 3: 分發與部署系統 (Completed - v1.0.0)
- [x] 跨平台構建系統 (60 個檔案)
- [x] Windows/macOS/Linux 安裝程式
- [x] Docker 容器化完整堆疊
- [x] CI/CD 自動化管道
- [x] 代碼簽名與公證
- [x] 完整安裝/構建文檔

#### 🔄 Phase 4: 生產化與擴展 (In Progress)
- [ ] Island AI Stage 2-4 (協作、自學習、生產化)
- [ ] Architecture Reasoner Agent MVP
- [ ] Dashboard Frontend & Backend
- [ ] 性能優化與監控增強
- [ ] 多語言 SDK (Python/TypeScript/Go)

#### 📋 Phase 5: 企業級增強 (Planned - Q1 2025)
- [ ] 多租戶支持 (Multi-Tenancy)
- [ ] 高可用性部署 (HA Deployment)
- [ ] 進階身份認證 (Advanced IAM)
- [ ] 成本管理儀表板
- [ ] SLA 監控與自動報告

#### 🌟 Phase 6: 生態系統擴展 (Planned - Q2-Q3 2025)
- [ ] 插件市場 (Plugin Marketplace)
- [ ] 第三方整合 (GitHub/GitLab/Azure DevOps)
- [ ] 託管服務版本 (SaaS)
- [ ] 認證與培訓計劃
- [ ] 社區貢獻平台

### 📊 技術債務與優化計劃

| 領域 | 當前狀態 | 目標 | 優先級 |
|------|---------|------|--------|
| **語言收斂** | 8 種語言 | 5 種 (TypeScript, Python, Go, C++, Rust) | P0 |
| **架構合規** | 92% | 100% | P0 |
| **安全態勢** | 93.5/100 | 100 (零 HIGH+) | P0 |
| **測試覆蓋率** | 76% (+2%/週) | 85%+ | P1 |
| **重構進度** | 58% | 100% | P1 |
| **圈複雜度** | 15.7 (改善中) | ≤15 平均 | P2 |

### 🎓 學習路徑建議

**新用戶入門順序**:
1. 📖 閱讀 [README.md](./README.md) - 系統概覽
2. 📥 按照 [INSTALL.md](./INSTALL.md) 安裝
3. 🚀 跟隨 [快速開始](#-快速開始) 啟動服務
4. 📚 瀏覽 [文檔導航](#-文檔導航) 深入了解

**開發者進階路徑**:
1. 🔨 學習 [BUILD.md](./BUILD.md) - 構建系統
2. 🏗️ 理解 [架構治理矩陣](./governance/ARCHITECTURE_GOVERNANCE_MATRIX.md)
3. 🤖 探索 [Island AI 系統](./island-ai/README.md)
4. 🔄 掌握 [Refactor Playbook](./docs/refactor_playbooks/README.md)

**貢獻者完整路徑**:
1. 📋 閱讀 [CONTRIBUTING.md](./CONTRIBUTING.md) - 貢獻指南
2. 🔍 理解 [全局優化推理](#-全局優化推理系統global-optimization-reasoning)
3. ✅ 遵循 [AI Behavior Contract](./.github/AI-BEHAVIOR-CONTRACT.md)
4. 🚀 參與 [Issue 討論](https://github.com/SynergyMesh-admin/SynergyMesh/issues)

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

- core/unified_integration/ - 統一整合層（認知處理器、服務註冊表、配置優化器）
- core/mind_matrix/ - 心智矩陣（執行長系統、多代理超圖）
- core/safety_mechanisms/ - 安全機制（斷路器、緊急停止、回滾系統）
- core/slsa_provenance/ - SLSA 溯源（證明管理、簽名驗證）
- **island-ai/** ⭐ **NEW** - Island AI Multi-Agent System（智能代理系統，Stage 1 已上線）

#### 🤖 Island AI Multi-Agent System（智能代理系統）

**Stage 1 現已推出** - 六個基礎 AI Agent 提供智能診斷與系統洞察：

```typescript
// 快速使用 Island AI Agents
import { runStageOne } from 'island-ai';

const reports = await runStageOne({
  requestId: 'system-diagnostic',
  timestamp: new Date(),
  payload: { deploymentsPerWeek: 15 }
});

// 取得各 Agent 的診斷報告
reports.forEach(report => {
  console.log(`${report.agent}: ${report.insights.length} insights`);
});
```

**可用 Agents：**

| Agent              | 職責               | 關鍵功能                          |
| ------------------ | ------------------ | --------------------------------- |
| 🏗️ **Architect**     | 架構設計與優化     | 系統分析、設計模式建議、性能優化 |
| 🔒 **Security**      | 安全審計與修補     | 漏洞掃描、OWASP/CWE 規則檢查     |
| 🚀 **DevOps**        | 部署與監控         | CI/CD 管道、自動擴展、監控告警   |
| ✅ **QA**            | 測試與驗證         | 單元/整合/E2E 測試策略           |
| 📊 **Data Scientist** | 數據分析與預測    | 回歸/分類/聚類模型、趨勢分析     |
| 📋 **Product Manager** | 產品規劃與優先級 | KPI 追蹤、用戶反饋、功能排序     |

**整合狀態：**
- ✅ Stage 1 完成（6 個 Agents，TypeScript 實現）
- ✅ npm workspace 整合
- 🔄 與 SynergyMesh 核心引擎整合中
- 📋 Stage 2-4 規劃中（協作機制、自學習、生產化）

詳見：[island-ai/README.md](./island-ai/README.md) | [完整路線圖](./island-ai.md)

### 2️⃣ Structural Governance System（結構治理系統）

SuperRoot 風格的 Schema 命名空間與自主治理基礎設施。

#### 🎯 Language Governance Dashboard（語言治理儀表板）

**實時語言政策合規性監控與可視化系統**

```yaml
dashboard:
  route: "/#/language-governance"
  health_score: "85/100 (Grade B)"
  visualizations:
    - layer_model: 六層架構圖 (L0-L5)
    - sankey_flow: 違規流向圖 (來源→類型→修復)
    - hotspot_heatmap: 違規強度熱力圖 (0-100 分)
    - migration_flow: 叢集遷移流模型 (歷史+建議)
  
  api_endpoint: /api/v1/language-governance
  
  ci_automation:
    schedule: "每日 00:00 UTC"
    triggers: ["push", "pull_request"]
    generators:
      - tools/generate-sankey-data.py
      - tools/generate-hotspot-heatmap.py
      - tools/generate-migration-flow.py
```

**快速開始：**
```bash
# 存取儀表板
cd apps/web && npm run dev
# 瀏覽器開啟: http://localhost:8000/#/language-governance

# 手動產生治理資料
python3 tools/generate-sankey-data.py
python3 tools/generate-hotspot-heatmap.py
python3 tools/generate-migration-flow.py
```

**主要功能：**
- ✅ **健康分數監控**：85/100 (Grade B)，目標 90+ (Grade A)
- ✅ **違規追蹤**：2 個活躍違規，12% 減少趨勢
- ✅ **安全掃描**：Semgrep 整合，1 個警告
- ✅ **修復成功率**：87%，5% 改善
- ✅ **熱點識別**：4 個熱點，1 個嚴重 (≥70 分)
- ✅ **遷移建議**：9 個流程 (2 歷史 + 7 建議)

📚 完整文檔：
- [實作指南](docs/LANGUAGE_GOVERNANCE_IMPLEMENTATION.md)
- [Hotspot 演算法](docs/HOTSPOT_HEATMAP.md)
- [遷移流模型](docs/MIGRATION_FLOW.md)
- [PR 分析與行動計劃](docs/PR_ANALYSIS_AND_ACTION_PLAN.md)

---

## 🎯 全局優化推理系統（Global Optimization Reasoning）

> **讓 AI 與架構師用「全局視野」做決策，而不只是打補丁**

**Global Optimization Reasoning System** 是一套完整的架構治理與優化框架，確保所有重構、語言治理、模組調整都遵循「全局優化優先」原則。

### 核心原則：Global Optimization First

任何架構/重構/語言治理變更**必須**提供：

```yaml
three_layer_structure:
  layer_1_global_view:
    - 優化目標: "語言堆疊收斂至 5 種 (TypeScript, Python, Go, C++, Rust)"
    - 硬約束: ["core 不依賴 apps", "零 forbidden languages", "零 HIGH security findings"]
  
  layer_2_local_plan:
    - 範圍: "僅修改 core/contract_service/ 模組"
    - 影響分析:
        - 語言違規: "減少 3 → 0"
        - 架構合規: "維持 100%"
        - 測試覆蓋率: "76% → 82% (+6%)"
  
  layer_3_self_check:
    - 架構違規檢查: "✅ 無新增依賴反向"
    - 問題轉移檢查: "✅ 不將問題推給其他模組"
    - 骨架規則檢查: "✅ 符合 architecture-stability 骨架"
```

### 🏗️ Architecture Reasoner（架構推理代理）

**角色定義**：Global Layer agent，擁有 **VETO 權限**，負責全局架構決策。

```yaml
architecture_reasoner:
  role: "Global Reasoner"
  authority: "VETO (可否決違反約束的提案)"
  
  responsibilities:
    primary:
      - 評估所有重構提案的全局影響
      - 執行三層回應結構驗證
      - 判定是否違反架構骨架規則
    
    secondary:
      - 監控 6 個目標函數趨勢
      - 生成優化差距報告
      - 建議架構改進方案
  
  phase_integration:
    phase_0_1_2: "CRITICAL - 高階推理權重大"
    phase_3_4: "IMPORTANT - 執行期驗證"
    phase_5: "MONITORING - 持續監控優化指標"
  
  decision_flow:
    input: "Refactor Playbook (YAML) + 當前系統狀態"
    process:
      - 檢查 Global Optimization View 完整性
      - 驗證 Local Plan 對全局指標影響
      - 執行 Self-Check 三項檢查
    output:
      decision: "APPROVE | VETO | CONDITIONAL_APPROVE"
      reasoning: "詳細決策理由 (YAML 格式)"
      recommendations: "改進建議 (if VETO)"
```

📚 **完整文檔**：[services/agents/architecture-reasoner/README.md](services/agents/architecture-reasoner/README.md)

---

### 📊 六個核心目標函數（Objective Functions）

監控與優化系統健康的 6 個關鍵指標：

#### 1. Language Stack Convergence（語言堆疊收斂）
```yaml
formula: convergence = 1 - (current_count - ideal_count) / ideal_count
ideal_state: 5 種語言 (TypeScript, Python, Go, C++, Rust)
current_state: 8 種語言 (+ Java, Shell, PHP)
convergence_score: 0.40 (40% converged)
target: ≥ 0.90 (90%)
```

#### 2. Architecture Compliance（架構合規分數）
```yaml
formula: compliance = (valid_dependencies / total_dependencies) × 100%
checks:
  - 分層驗證: core → services → apps (單向)
  - 依賴反向檢查: 0 violations
  - Skeleton 規則: 5/5 骨架符合
current: 92%
target: 100%
```

#### 3. Security Posture Index（安全態勢指數）
```yaml
formula: security = 100 - (critical×10 + high×5 + medium×2 + low×0.5)
current_findings:
  critical: 0
  high: 1 (language violation)
  medium: 3
  low: 8
security_score: 93.5
target: 100 (zero HIGH+)
```

#### 4. Refactor Progress Index（重構進度指數）
```yaml
formula: progress = (completed_tasks / total_tasks) × 100%
tasks:
  p0_critical: 2/3 (67%)
  p1_important: 5/8 (63%)
  p2_nice_to_have: 1/12 (8%)
weighted_progress: 58%
target: 100%
```

#### 5. Test Coverage Momentum（測試覆蓋率動量）
```yaml
formula: momentum = (current_coverage - baseline_coverage) / weeks
baseline: 68% (4 weeks ago)
current: 76%
momentum: +2% per week
target: ≥ 75% coverage, ≥ 0% momentum
```

#### 6. Cyclomatic Complexity Trend（圈複雜度趨勢）
```yaml
formula: trend = (current_avg - baseline_avg) / baseline_avg
baseline: avg_complexity = 18.2
current: avg_complexity = 15.7
trend: -13.7% (improving ✅)
target: ≤ 15 avg, negative trend
```

📚 **完整規範**：[docs/ARCHITECTURE_OPTIMIZATION_DASHBOARD.md](docs/ARCHITECTURE_OPTIMIZATION_DASHBOARD.md)

---

### 🌐 Dashboard & API

**存取 Dashboard**：
```bash
# 啟動 Dashboard（Phase 5 實施後）
cd services/dashboard && npm run dev
# 瀏覽器開啟: http://localhost:3000/architecture/optimization
```

**API 端點**：

```yaml
api_endpoints:
  health:
    GET /api/architecture/health
    response:
      overall_score: 85
      language_convergence: 0.40
      architecture_compliance: 0.92
      security_posture: 93.5
      refactor_progress: 0.58
      coverage_momentum: 2.0
      complexity_trend: -0.137
  
  gap_report:
    GET /api/architecture/gap-report
    response:
      critical_gaps:
        - gap_id: "LANG-001"
          description: "3 個語言未收斂 (Java, Shell, PHP)"
          impact: "阻擋達成 90% 收斂目標"
          recommendation: "執行 P0 語言遷移計畫"
      
      projected_timeline: "18+ weeks to 100% health"
  
  metrics:
    GET /api/architecture/metrics/{metric-name}
    # metric-name: language-convergence | architecture-compliance | security | ...
  
  decision:
    POST /api/architecture/decision
    body:
      playbook_path: "docs/refactor_playbooks/03_refactor/core/..."
      dry_run: true
    response:
      decision: "VETO"
      reasoning: "Global View 缺少硬約束說明"
      recommendations: ["補充 architecture_constraints 區塊"]
```

---

### 🚀 快速開始

#### For AI Agents（立即可用）

```bash
# 1. 參考行為合約 Section 9
cat .github/AI-BEHAVIOR-CONTRACT.md  # 查看 Global Optimization First 原則

# 2. 使用 Playbook 模板
cp docs/refactor_playbooks/03_refactor/templates/REFRACTOR_PLAYBOOK_TEMPLATE.md \
   docs/refactor_playbooks/03_refactor/my-cluster/playbook.md

# 3. 填寫 Section 3: Language & Structure Refactoring Strategy
# 包含：Global View → Local Plan → Self-Check
```

#### For Developers（準備實施）

```bash
# 1. 查看 Architecture Reasoner 文檔
cat services/agents/architecture-reasoner/README.md

# 2. 理解 Dashboard 規範
cat docs/ARCHITECTURE_OPTIMIZATION_DASHBOARD.md

# 3. 查看驗證腳本規範（待實施）
cat tools/validation/README.md
```

#### For Reviewers（立即可用）

```bash
# 檢查提案是否符合 Global Optimization 結構
# ✅ 必須包含：Global View（優化目標 + 硬約束）
# ✅ 必須包含：Local Plan（範圍 + 影響分析）
# ✅ 必須包含：Self-Check（三項檢查）

# 參考當前系統狀態
cat config/system-module-map.example.yaml
```

---

### 📚 相關文檔

| 文檔 | 說明 |
|------|------|
| [AI-BEHAVIOR-CONTRACT.md](.github/AI-BEHAVIOR-CONTRACT.md) | Section 9: Global Optimization First 原則 |
| [AI_PROMPTS.md](docs/refactor_playbooks/03_refactor/meta/AI_PROMPTS.md) | Section 1.5: 高階最佳化推理提示詞 |
| [REFRACTOR_PLAYBOOK_TEMPLATE.md](docs/refactor_playbooks/03_refactor/templates/REFRACTOR_PLAYBOOK_TEMPLATE.md) | Sections 0 & 3: Playbook 模板與優化策略 |
| [architecture-reasoner/README.md](services/agents/architecture-reasoner/README.md) | Architecture Reasoner 完整規範 |
| [ARCHITECTURE_OPTIMIZATION_DASHBOARD.md](docs/ARCHITECTURE_OPTIMIZATION_DASHBOARD.md) | Dashboard 規範與 API 文檔 |
| [system-module-map.example.yaml](config/system-module-map.example.yaml) | 標準模組映射範本 |
| [validation/README.md](tools/validation/README.md) | 驗證腳本規範（待實施） |
| [global-optimization/README.md](tests/integration/global-optimization/README.md) | E2E 測試策略（待實施） |

---

### 🗺️ Implementation Roadmap

#### ✅ Phase 1-3: Core Documentation (已完成)
- AI Behavior Contract Section 9
- AI Prompts Section 1.5
- Playbook Template Section 3
- Architecture Reasoner Specification
- Dashboard Specification
- System Module Map Example

#### ✅ Phase 4: Integration & Validation (已完成基礎架構)
- 文檔交叉引用（本 README）
- 驗證腳本規範與骨架
- 測試結構與 fixtures

#### 📋 Phase 5: Implementation (預計 3-4 weeks)
**PR #1**: Dashboard Backend MVP
- 6 個目標函數計算引擎
- FastAPI 端點實現
- 可驗證成果：`curl localhost:8080/api/architecture/health`

**PR #2**: Architecture Reasoner Agent MVP
- 決策邏輯與 Veto 引擎
- CLI 介面
- 可驗證成果：`python agent.py --check playbook.yaml`

**PR #3**: Dashboard Frontend MVP
- React 可視化介面
- 指標卡片與 Gap Report UI
- 可驗證成果：瀏覽器訪問 Dashboard

#### 📋 Phase 6: Rollout & Training (預計 2-3 weeks)
- Quick Start Guide（30 分鐘上手）
- Training Workshops（理論 + 實作 + 分析）
- Gradual Enablement（Advisory → Soft Veto → Full Enforcement）

**總預估時程**：5-7 weeks 達成完整可操作系統

---

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

### 🏗️ 治理工具：

- tools/docs/validate_index.py - Schema 驗證器
- tools/docs/scan_repo_generate_index.py - 倉庫掃描生成索引
- tools/docs/provenance_injector.py - SLSA L3 證據注入、SBOM 生成
- **tools/generate-refactor-playbook.py** ⭐ **NEW** - AI 重構 Playbook 生成器
  - 自動分析語言治理數據、安全掃描、熱點分析
  - 為 8 個 clusters 生成結構化重構計畫（P0/P1/P2 優先級）
  - 包含檔案與目錄結構交付視圖
  - 整合 Auto-Fix Bot 與 Living Knowledge Base
  - 詳見：[docs/refactor_playbooks/README.md](./docs/refactor_playbooks/README.md)

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

## 4️⃣ 活體知識庫（Living Knowledge Base）

> 讓系統自己感知變化、重建自身結構、自我檢查，並主動回報狀態。

本模組**不是**人工智慧助理、命令列工具、Copilot 或聊天機器人。
它的唯一目的，是讓程式碼倉庫「知道自己現在長怎樣、哪裡有問題」，並用**機器可讀的方式**表達出來。

```yaml
# 知識循環四層次
knowledge_cycle:
  perception:      # 感知層 - 偵測變化
    - Git 提交紀錄（檔案新增 / 修改 / 刪除）
    - GitHub Actions 工作流結果
    - 定期排程掃描
  
  modeling:        # 建模層 - 重建結構
    outputs:
      - docs/generated-mndoc.yaml      # 系統說明書
      - docs/knowledge-graph.yaml      # 維度關係圖
      - docs/superroot-entities.yaml   # SuperRoot ontology 編碼
  
  self_diagnosis:  # 自我診斷層 - 找出問題
    checks:
      - 孤兒元件（無關聯的 Component）
      - 死設定（未使用的 Config）
      - 重疊工作流
      - 斷鏈文件
    output: docs/knowledge-health-report.yaml
  
  action:          # 行動層 - 回報狀態
    - 更新 docs/KNOWLEDGE_HEALTH.md 儀表板
    - 必要時自動開 GitHub Issue
```

**目錄佈局：**

| 目錄 | 用途 |
|------|------|
| knowledge/ | 純知識資料層（YAML/JSON），不放程式碼 |
| runtime/ | 操作知識的程式碼：載入、建模、診斷、輸出報告 |
| pipelines/ | 把 runtime 組合成完整活體流程 |
| docs/ | 給人類看的說明與健康報告 |

📚 詳見 docs/LIVING_KNOWLEDGE_BASE.md

---

## 📁 統一目錄結構

```
unmanned-island/
│
├── synergymesh.yaml              # 🔑 統一主配置入口
│
├── core/                         # 🏛️ 核心平台服務
│   ├── unified_integration/      # 統一整合層
│   ├── mind_matrix/              # 心智矩陣
│   ├── lifecycle_systems/        # 生命週期系統
│   ├── safety_mechanisms/        # 安全機制
│   ├── slsa_provenance/          # SLSA 溯源
│   ├── contract_service/         # 合約管理服務 (L1)
│   └── ...                       # 其他核心模組
│
├── automation/                   # 🤖 自動化模組
│   ├── intelligent/              # 智能自動化
│   ├── autonomous/               # 五骨架自主系統
│   ├── architect/                # 架構分析修復
│   └── hyperautomation/          # 超自動化策略
│
├── config/                       # ⚙️ 配置中心
│   ├── system-manifest.yaml      # 系統宣告
│   ├── unified-config-index.yaml # 統一配置索引 (v3.0.0)
│   ├── system-module-map.yaml    # 模組映射
│   ├── ai-constitution.yaml      # AI 憲法
│   ├── safety-mechanisms.yaml    # 安全機制
│   └── ...                       # 其他配置
│
├── governance/                   # ⚖️ 治理與策略
│   ├── schemas/                  # JSON Schema 定義
│   ├── policies/                 # OPA/Conftest 策略
│   ├── sbom/                     # 軟體物料清單
│   └── audit/                    # 審計配置
│
├── infrastructure/               # 🏗️ 基礎設施
│   ├── kubernetes/               # K8s 部署清單
│   ├── monitoring/               # 監控告警
│   ├── canary/                   # 金絲雀部署
│   └── drift/                    # 漂移檢測
│
├── mcp-servers/                  # 🔌 MCP 伺服器
├── tools/                        # 🔧 工具腳本
│   └── cli/                      # Admin Copilot CLI
├── apps/                         # 📱 應用程式
│   └── web/                      # 🌐 Web 前端與代碼分析 API
├── services/                     # 後端服務與代理
├── docs/                         # 📚 文檔
│   └── refactor_playbooks/       # 🔄 重構 Playbook 系統
│       ├── 01_deconstruction/    # 解構階段
│       ├── 02_integration/       # 集成階段
│       ├── 03_refactor/          # 重構階段
│       └── NEXT_STEPS_PLAN.md    # 下一步計劃
├── tests/                        # 🧪 測試套件
└── .github/                      # 🔄 GitHub 配置
```

---

## 🔄 Refactor Playbook System

**三階段重構系統** - 結構化的語言治理與架構重構控制平面

```
01_deconstruction → 02_integration → 03_refactor
                                         ↓
                            Proposer generates proposal
                                         ↓
                            Critic validates (architecture + quality)
                                         ↓
                            CI validates (gates) → Human review
```

### 主要功能

- **架構約束**: 依賴規則、骨架規則、語言策略（11 個架構骨架）
- **品質指標**: 可量化的前後對比（語言違規、Semgrep、複雜度、測試覆蓋率）
- **Proposer/Critic AI 工作流**: 雙層 AI 驗證（Proposer 生成 → Critic 審查 → 迭代修正）
- **配置整合**: 完全整合到 `system-module-map.yaml` 和 `unified-config-index.yaml`

### 快速入門

查看重構系統文檔：
```bash
# 查看重構系統總覽
cat docs/refactor_playbooks/README.md

# 查看下一步計劃
cat docs/refactor_playbooks/NEXT_STEPS_PLAN.md

# 運行驗證工具
python3 tools/validate-refactor-index.py
```

**詳細文檔**: [`docs/refactor_playbooks/`](docs/refactor_playbooks/)

---

## 🚀 快速開始

### 📥 安裝選擇

**我們提供多種安裝方式，請選擇最適合您的：**

| 用戶類型 | 推薦方式 | 文檔 |
|---------|---------|------|
| **一般用戶** | 下載對應平台的安裝程式 | [INSTALL.md](./INSTALL.md) |
| **開發者** | 從源碼安裝 | 見下方「從源碼安裝」 |
| **企業部署** | Docker Compose | 見下方「Docker 部署」 |
| **系統管理員** | 包管理器（apt/yum/brew） | [INSTALL.md](./INSTALL.md) |

💡 **完整跨平台安裝指南**: 請查看 [📦 跨平台安裝與構建系統](#-跨平台安裝與構建系統--cross-platform-build-system)

---

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

### 從源碼安裝（開發者）

```bash
# 1. Clone 倉庫
git clone https://github.com/SynergyMesh-admin/SynergyMesh.git
cd SynergyMesh

# 2. 安裝 Python 依賴
pip install -r requirements.txt
pip install -e .

# 3. 安裝 Node.js 依賴
npm install

# 4. 運行測試
npm run lint
npm run test
pytest
```

### 核心服務啟動

```bash
# 啟動合約服務
cd core/contract_service/contracts-L1/contracts
npm install && npm run build
npm start

# 啟動 MCP 伺服器
cd mcp-servers
npm install && npm start

# 驗證治理系統
python tools/docs/validate_index.py --verbose
```

### Docker 部署（推薦用於生產環境）

```bash
# 方式 1: 快速啟動
docker-compose -f docker-compose.dev.yml up -d

# 方式 2: 完整堆疊（包含監控）
wget https://raw.githubusercontent.com/SynergyMesh-admin/SynergyMesh/main/build/docker/docker-compose.yml
docker-compose up -d

# 查看服務狀態
docker-compose ps
docker-compose logs -f governance

# 訪問服務
# - Governance API: http://localhost:8000
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000
```

---

## 📦 跨平台安裝與構建系統 | Cross-Platform Build System

> **完整的跨平台分發解決方案，支援 Windows, macOS, Linux 和 Docker**

### 🎯 系統概覽

SynergyMesh 提供完整的自動化構建和分發系統，涵蓋所有主流平台：

```
構建系統架構
├── 🪟 Windows
│   ├── EXE 安裝程式（PyInstaller + NSIS）
│   ├── MSI 安裝程式（WiX Toolset）
│   └── 代碼簽名（EV Certificate 支持）
│
├── 🍎 macOS
│   ├── DMG 磁碟映像（create-dmg）
│   ├── PKG 安裝程式（pkgbuild）
│   ├── Homebrew Formula
│   └── 代碼簽名 + 公證（Apple Developer ID）
│
├── 🐧 Linux
│   ├── AppImage（通用二進制）
│   ├── DEB 包（Debian/Ubuntu）
│   ├── RPM 包（RHEL/CentOS/Fedora）
│   └── Systemd 服務整合
│
└── 🐳 Docker
    ├── Linux 容器（多階段構建）
    ├── Windows 容器
    └── Docker Compose 完整堆疊
```

### 📥 快速安裝

#### Windows 用戶

```batch
# 方式 1: 下載 EXE 安裝程式（推薦）
# 下載並雙擊: SynergyMesh-Governance-setup.exe

# 方式 2: 使用 MSI（企業部署）
msiexec /i SynergyMesh-Governance-1.0.0.msi /qn

# 驗證安裝
synergymesh --version
```

#### macOS 用戶

```bash
# 方式 1: 使用 Homebrew（推薦）
brew tap synergymesh/tap
brew install synergymesh-governance

# 方式 2: 下載 DMG
# 下載並安裝: SynergyMesh-Governance-1.0.0.dmg

# 方式 3: 使用 PKG
sudo installer -pkg SynergyMesh-Governance-1.0.0.pkg -target /

# 驗證安裝
synergymesh --version
```

#### Linux 用戶

```bash
# 方式 1: AppImage（通用，推薦）
wget https://github.com/SynergyMesh-admin/SynergyMesh/releases/download/v1.0.0/SynergyMesh-Governance-x86_64.AppImage
chmod +x SynergyMesh-Governance-x86_64.AppImage
./SynergyMesh-Governance-x86_64.AppImage

# 方式 2: Debian/Ubuntu (DEB)
wget https://github.com/SynergyMesh-admin/SynergyMesh/releases/download/v1.0.0/synergymesh-governance_1.0.0_amd64.deb
sudo apt install ./synergymesh-governance_1.0.0_amd64.deb

# 方式 3: RHEL/CentOS/Fedora (RPM)
wget https://github.com/SynergyMesh-admin/SynergyMesh/releases/download/v1.0.0/synergymesh-governance-1.0.0-1.x86_64.rpm
sudo rpm -i synergymesh-governance-1.0.0-1.x86_64.rpm

# 驗證安裝
synergymesh --version
```

#### Docker 用戶

```bash
# 方式 1: Docker Run（快速開始）
docker pull synergymesh/governance:latest
docker run -d \
  --name synergymesh-governance \
  -p 8000:8000 \
  -v synergymesh-data:/var/lib/synergymesh \
  synergymesh/governance:latest

# 方式 2: Docker Compose（完整堆疊，推薦）
wget https://raw.githubusercontent.com/SynergyMesh-admin/SynergyMesh/main/build/docker/docker-compose.yml
docker-compose up -d

# 查看狀態
docker ps
docker logs synergymesh-governance
```

### 🔨 從源碼構建

#### 統一構建腳本（推薦）

```bash
# 1. Clone 倉庫
git clone https://github.com/SynergyMesh-admin/SynergyMesh.git
cd SynergyMesh

# 2. 使用 Python 構建腳本
python3 build/build.py <platform>
# 平台選項: windows | macos | linux | docker | all

# 3. 或使用 Makefile
make build              # 當前平台
make build-windows      # Windows
make build-macos        # macOS
make build-linux        # Linux
make build-docker       # Docker
make build-all          # 所有平台
```

#### 平台特定構建

**Windows**:
```batch
cd build\windows
build-windows.bat
```

**macOS**:
```bash
cd build/macos
./build-macos.sh
```

**Linux**:
```bash
cd build/linux
./build-linux.sh
```

### 🤖 CI/CD 自動化

所有構建流程完全自動化，通過 GitHub Actions 實現：

```yaml
# 自動構建觸發條件
- Push to main/develop
- Pull Request
- Tag push (v*)
- Manual workflow dispatch

# 自動發布流程
1. 創建 Git tag: git tag -a v1.0.0 -m "Release v1.0.0"
2. 推送 tag: git push origin v1.0.0
3. GitHub Actions 自動執行：
   - 構建所有平台安裝包
   - 代碼簽名與公證
   - 創建 GitHub Release
   - 上傳所有產物
   - 推送 Docker 映像
```

### 📊 構建產物統計

```
總計: 60 個構建相關檔案

✅ Windows (11 個):
   • build-windows.bat
   • install.bat / uninstall.bat
   • windows-config.yaml
   • windows-requirements.txt
   • sign-windows.ps1
   • 其他配置檔案

✅ macOS (12 個):
   • build-macos.sh
   • install-macos.sh / uninstall-macos.sh
   • macos-config.yaml
   • Info.plist / entitlements.plist
   • sign-macos.sh
   • synergymesh-governance.rb (Homebrew)
   • 其他配置檔案

✅ Linux (15 個):
   • build-linux.sh
   • build-appimage.sh / build-deb.sh / build-rpm.sh
   • install-linux.sh / uninstall-linux.sh
   • linux-config.yaml
   • debian/* (DEB 配置)
   • redhat/*.spec (RPM 配置)
   • systemd/*.service

✅ Docker (4 個):
   • Dockerfile (Linux 多階段構建)
   • Dockerfile.windows
   • docker-compose.yml
   • .dockerignore

✅ 通用構建 (18 個):
   • build.py (統一構建腳本)
   • setup.py / pyproject.toml
   • MANIFEST.in / Makefile
   • INSTALL.md / BUILD.md / RELEASE.md
   • VERSION / CHANGELOG.md
   • 其他文檔
```

### 📚 詳細文檔

| 文檔 | 說明 |
|------|------|
| [INSTALL.md](./INSTALL.md) | 完整安裝指南（所有平台） |
| [BUILD.md](./BUILD.md) | 構建指南與故障排除 |
| [RELEASE.md](./RELEASE.md) | 發布流程與版本管理 |
| [build/windows/](./build/windows/) | Windows 構建檔案 |
| [build/macos/](./build/macos/) | macOS 構建檔案 |
| [build/linux/](./build/linux/) | Linux 構建檔案 |
| [build/docker/](./build/docker/) | Docker 配置 |

---

## 🖥️ Admin Copilot CLI (Public Preview)

Admin Copilot CLI 將 AI 驅動的程式碼分析與操作能力帶入命令列，使系統可透過自然語言理解自身程式碼，並執行建置、偵錯與維護流程。

詳見 docs/ADMIN_COPILOT_CLI.md 與 tools/cli/README.md。

---

## 🌐 Web 前端與代碼分析 API (apps/web)

apps/web 提供企業級代碼分析服務，包括 React 前端與 FastAPI 後端。

- 前端：npm install、npm run dev / build
- 後端：pip install -r requirements.txt、pytest

部署與 API 詳見 apps/web/README.md。

---

## 🛠️ 核心功能

### 🤖 智能自動化

| 功能           | 說明                             | 入口                                 |
| -------------- | -------------------------------- | ------------------------------------ |
| 自動程式碼審查 | PR 自動審查與合併                | .github/workflows/                   |
| 智能派工系統   | 問題自動分配與負載均衡           | core/contract_service/               |
| 進階升級系統   | 五級升級階梯 (L1 Auto → L5 客服) | docs/ADVANCED_ESCALATION_SYSTEM.md   |
| Auto-Fix Bot   | 自動修復 CI 失敗                 | config/auto-fix-bot.yml              |

### 🔒 安全與合規

| 功能         | 說明                  | 入口                    |
| ------------ | --------------------- | ----------------------- |
| SLSA L3 溯源 | 構建認證與簽名        | core/slsa_provenance/   |
| Schema 驗證  | JSON Schema 合規檢查  | governance/schemas/     |
| 策略閘       | OPA/Conftest 策略執行 | governance/policies/    |
| SBOM 生成    | 軟體物料清單          | governance/sbom/        |

### 📊 監控與觀測

| 功能            | 說明                 | 入口                         |
| --------------- | -------------------- | ---------------------------- |
| 動態 CI 助手    | 每個 CI 都有獨立客服 | docs/DYNAMIC_CI_ASSISTANT.md |
| Prometheus 監控 | 指標收集與告警       | infrastructure/monitoring/   |
| 漂移檢測        | 基礎設施配置漂移     | infrastructure/drift/        |

---

## 🎛️ 全局配置總覽

| 配置檔案                          | 說明                             |
|-----------------------------------|----------------------------------|
| synergymesh.yaml                  | 統一主配置入口                   |
| config/system-manifest.yaml       | 系統宣告清單                     |
| config/unified-config-index.yaml  | 統一配置索引 v3.0.0             |
| config/system-module-map.yaml     | 模組映射                         |
| config/ai-constitution.yaml       | AI 最高指導憲章（三層憲法體系） |
| config/agents/team/virtual-experts.yaml | 虛擬專家團隊配置                 |
| config/safety-mechanisms.yaml     | 安全機制配置                     |
| config/topology-mind-matrix.yaml  | 心智矩陣拓撲配置                 |
| config/drone-config.yml           | 無人機編隊與自動化系統配置       |
| config/cloud-agent-delegation.yml | 雲端代理程式委派配置             |

---

## 👨‍💼 虛擬專家團隊

內建多位虛擬專家，對應架構、安全、資料庫、DevOps 等領域，詳細映射參考 config/agents/team/virtual-experts.yaml。

---

## 🤖 智能代理服務

services/agents/ 提供長生命週期業務代理：

- Auto-Repair Agent：自動修復
- Code Analyzer Agent：程式碼分析
- Dependency Manager：依賴管理
- Orchestrator：代理編排
- Vulnerability Detector：漏洞檢測

更多細節見 services/agents/README.md。

---

## 🚁 無人機系統配置

drone-config.yml 定義無人機編隊與協調策略，並透過 automation/autonomous/ 五骨架框架實作。

---

## 🚗 自主系統框架（無人駕駛/無人機）

### 統一架構骨架系統 ⭐

**11 個完整架構骨架**，整合架構指南與實現代碼：

- **入口**: [`automation/architecture-skeletons/README.md`](./automation/architecture-skeletons/README.md)
- **索引**: [`automation/architecture-skeletons/unified-index.yaml`](./automation/architecture-skeletons/unified-index.yaml)
- **分析報告**: [`docs/ARCHITECTURE_SKELETON_ANALYSIS.md`](./docs/ARCHITECTURE_SKELETON_ANALYSIS.md)

#### 骨架清單 (11個)

| 骨架 | 狀態 | 用途 |
|------|------|------|
| architecture-stability | ✅ 生產 | 系統架構設計、服務邊界 |
| security-observability | ✅ 生產 | 安全機制、監控追蹤 |
| api-governance | ✅ 生產 | API 設計、版本管理 |
| testing-governance | ✅ 生產 | 測試策略、品質保證 |
| docs-governance | ✅ 生產 | 文檔標準、知識管理 |
| identity-tenancy | 🟡 設計 | 認證授權、多租戶 |
| data-governance | 🟡 設計 | 資料分類、隱私合規 |
| performance-reliability | 🟡 設計 | SLA、災難恢復 |
| cost-management | 🟡 設計 | 成本監控、預算規劃 |
| knowledge-base | 🟡 設計 | 知識組織、AI 上下文 |
| nucleus-orchestrator | 🟡 設計 | 工作流編排、代理協調 |

**詳細說明**: [`automation/autonomous/README.md`](./automation/autonomous/README.md)

---

## 📚 文檔導航

完整文檔入口：docs/README.md

- **架構**：docs/architecture/
- **快速入門**：docs/QUICK_START.md
- **API 文檔**：docs/AUTO_ASSIGNMENT_API.md
- **運維手冊**：docs/operations/
- **語言治理**：docs/LANGUAGE_GOVERNANCE_IMPLEMENTATION.md
- **重構劇本** ⭐：[docs/refactor_playbooks/](./docs/refactor_playbooks/)

### 📋 Refactor Playbooks（重構劇本系統）⭐

**三階段結構化重構流程**，從解構到執行的完整追溯性：

```
01_deconstruction → 02_integration → 03_refactor
   (解構)              (集成)           (重構)
```

**核心文檔**：
- [README](./docs/refactor_playbooks/README.md) - 系統總覽與使用指南
- [CONFIG_INTEGRATION_GUIDE](./docs/refactor_playbooks/CONFIG_INTEGRATION_GUIDE.md) - 配置整合指南
- [PROPOSER_CRITIC_WORKFLOW](./docs/refactor_playbooks/03_refactor/meta/PROPOSER_CRITIC_WORKFLOW.md) - 雙層 AI 重構工作流程 ⭐
- [LEGACY_ANALYSIS_REPORT](./docs/refactor_playbooks/LEGACY_ANALYSIS_REPORT.md) - 完整架構分析
- [INTEGRATION_REPORT](./docs/refactor_playbooks/INTEGRATION_REPORT.md) - 整合報告與使用方式

**快速開始**：
```bash
# 生成重構劇本
python3 tools/generate-refactor-playbook.py --cluster "core/"

# 驗證索引一致性
python3 tools/validate-refactor-index.py

# 查看當前狀態
cat docs/refactor_playbooks/03_refactor/INDEX.md
```

**關鍵特性**：
- ✅ 三階段重構流程（解構 → 集成 → 重構）
- ✅ 舊資產管理（實體隔離、知識保留）
- ✅ 架構約束強制（11 個骨架規則、依賴方向、語言策略）
- ✅ 品質指標量化（before/after 比對、零容忍閘門）
- ✅ Proposer/Critic 雙層 AI 工作流程
- ✅ CI/CD 整合（Auto-Fix Bot、違規映射）
- ✅ 機器可讀索引（index.yaml）供自動化使用

---

## 🔄 CI/CD

主要工作流位於 .github/workflows/，品質閘條件定義在各 CI 配置中（覆蓋率、Lint、Schema、Policy）。

---

## 📄 授權與致謝

本專案採用 MIT License 授權，詳見 LICENSE。

致謝 SynergyMesh、Sigstore、OPA、SLSA 等開源專案提供的基礎能力。

---

<div align="center">

**🏝️ Unmanned Island System**

_讓開發更高效，讓程式碼更完美！_

[GitHub](https://github.com/SynergyMesh-admin/Unmanned-Island) •
[Issues](https://github.com/SynergyMesh-admin/Unmanned-Island/issues) •
[Discussions](https://github.com/SynergyMesh-admin/Unmanned-Island/discussions)

</div>
