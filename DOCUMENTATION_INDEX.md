# 📚 Unmanned Island System - 專案文檔總覽

> **文件版本**: 1.0.0  
> **維護者**: SynergyMesh Development Team  
> **備註**: 此文件為手動維護，最新的機器可讀索引請參考 [docs/knowledge_index.yaml](./docs/knowledge_index.yaml)

本文件整合專案中所有 `.md` 文件，提供統一的文檔導航與詳細操作流程說明。

---

## 目錄

1. [快速導覽](#-快速導覽)
2. [專案根目錄文檔](#-專案根目錄文檔)
3. [架構設計文檔](#-架構設計文檔-docsarchitecture)
4. [自動化系統文檔](#-自動化系統文檔-automation)
5. [核心平台文檔](#-核心平台文檔-core)
6. [CI/CD 與運維文檔](#-cicd-與運維文檔)
7. [安全與治理文檔](#-安全與治理文檔)
8. [服務與代理文檔](#-服務與代理文檔-services)
9. [應用程式文檔](#-應用程式文檔-apps)
10. [開發環境文檔](#-開發環境文檔-devcontainer)
11. [基礎設施文檔](#-基礎設施文檔-infrastructure)
12. [工具與腳本文檔](#-工具與腳本文檔-tools)
13. [其他文檔](#-其他文檔)
14. [詳細操作流程](#-詳細操作流程)

---

## 🚀 快速導覽

### 按角色推薦閱讀順序

| 角色              | 第一步                                                                                             | 第二步                                                                 | 第三步                                                                                 |
| ----------------- | -------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **新手開發者**    | [README.md](./README.md)                                                                           | [docs/QUICK_START.md](./docs/QUICK_START.md)                           | [docs/EXAMPLES.md](./docs/EXAMPLES.md)                                                 |
| **專案經理** ⭐   | [docs/INCOMPLETE_TASKS_SCAN_REPORT.md](./docs/INCOMPLETE_TASKS_SCAN_REPORT.md)                    | [PROJECT_DELIVERY_CHECKLIST.md](./PROJECT_DELIVERY_CHECKLIST.md)       | [docs/PR_ANALYSIS_AND_ACTION_PLAN.md](./docs/PR_ANALYSIS_AND_ACTION_PLAN.md)          |
| **DevOps 工程師** | [docs/architecture/DEPLOYMENT_INFRASTRUCTURE.md](./docs/architecture/DEPLOYMENT_INFRASTRUCTURE.md) | [docs/AUTO_REVIEW_MERGE.md](./docs/AUTO_REVIEW_MERGE.md)               | [docs/operations/](./docs/operations/)                                                 |
| **系統架構師**    | [docs/architecture/layers.md](./docs/architecture/layers.md)                                       | [docs/architecture/repo-map.md](./docs/architecture/repo-map.md)       | [docs/architecture/SYSTEM_ARCHITECTURE.md](./docs/architecture/SYSTEM_ARCHITECTURE.md) |
| **安全工程師**    | [SECURITY.md](./SECURITY.md)                                                                       | [docs/VULNERABILITY_MANAGEMENT.md](./docs/VULNERABILITY_MANAGEMENT.md) | [docs/security/](./docs/security/)                                                     |

---

## 📄 專案根目錄文檔

專案根目錄的核心文檔，提供專案概覽與基本指引。

| 文件路徑                                   | 說明                     | 操作指引                             |
| ------------------------------------------ | ------------------------ | ------------------------------------ |
| [README.md](./README.md)                   | 專案主要說明文件（中文） | 閱讀瞭解系統概述、快速開始、核心功能 |
| [README.en.md](./README.en.md)             | 專案主要說明文件（英文） | English version of main README       |
| [CHANGELOG.md](./CHANGELOG.md)             | 版本更新日誌             | 追蹤版本變更歷史                     |
| [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) | 社區行為準則             | 參與專案前必讀                       |
| [CONTRIBUTING.md](./CONTRIBUTING.md)       | 貢獻指南                 | 提交 PR 前必讀，了解代碼風格與流程   |
| [SECURITY.md](./SECURITY.md)               | 安全政策                 | 報告安全漏洞的流程                   |

### AI 協作規範 ⭐ **NEW**

| 文件路徑                                                                                          | 說明             | 操作指引                         |
| ------------------------------------------------------------------------------------------------- | ---------------- | -------------------------------- |
| [.github/AI-BEHAVIOR-CONTRACT.md](./.github/AI-BEHAVIOR-CONTRACT.md) ⭐                          | AI 行為合約      | AI 代理必讀，定義協作規範與責任  |
| [.github/AI-BEHAVIOR-CONTRACT-QUICK-REFERENCE.md](./.github/AI-BEHAVIOR-CONTRACT-QUICK-REFERENCE.md) | 快速參考卡       | 4 核心規則速查表，模板與範例     |
| [.github/copilot-instructions.md](./.github/copilot-instructions.md)                             | Copilot 技術指南 | 技術實現指引，參考三系統視圖     |
| [.github/island-ai-instructions.md](./.github/island-ai-instructions.md)                         | Island AI 規範   | 代碼風格、測試、文檔語言標準     |
| [.github/agents/my-agent.agent.md](./.github/agents/my-agent.agent.md)                           | 自定義代理配置   | 無人島智能代理行為定義           |

**AI 行為合約關鍵原則：**

- ✅ 使用具體語言（禁止模糊理由如「好像」「可能」）
- ✅ 二元回應：CAN_COMPLETE 或 CANNOT_COMPLETE + 缺少資源清單
- ✅ 主動拆解大任務（2-3 個子任務 + 執行順序）
- ✅ 預設草稿模式（檔案修改需明確授權）

**驗證工具：**

```bash
# 驗證 AI 回應合規性
.github/scripts/validate-ai-response.sh --commit HEAD
```

---

## 🏗️ 架構設計文檔 (`docs/architecture/`)

系統架構、設計原則與技術決策文檔。

| 文件路徑                                                                                                           | 說明             | 關鍵內容                |
| ------------------------------------------------------------------------------------------------------------------ | ---------------- | ----------------------- |
| [docs/architecture/README.md](./docs/architecture/README.md)                                                       | 架構文檔入口     | 架構文檔總覽            |
| [docs/architecture/layers.md](./docs/architecture/layers.md) ⭐                                                    | 五層架構視圖     | 依賴規則、層級職責      |
| [docs/architecture/repo-map.md](./docs/architecture/repo-map.md) ⭐                                                | 倉庫語義邊界     | 目錄結構、決策指南      |
| [docs/architecture/SYSTEM_ARCHITECTURE.md](./docs/architecture/SYSTEM_ARCHITECTURE.md)                             | 系統架構設計     | 四層微服務架構          |
| [docs/architecture/DEPLOYMENT_INFRASTRUCTURE.md](./docs/architecture/DEPLOYMENT_INFRASTRUCTURE.md)                 | 部署基礎設施     | Docker、K8s、CI/CD 設置 |
| [docs/architecture/CODE_QUALITY_CHECKS.md](./docs/architecture/CODE_QUALITY_CHECKS.md)                             | 代碼質量檢查     | 質量工具配置            |
| [docs/architecture/SECURITY_CONFIG_CHECKS.md](./docs/architecture/SECURITY_CONFIG_CHECKS.md)                       | 安全配置檢查     | 安全掃描與驗證          |
| [docs/architecture/DIRECTORY_STRUCTURE.md](./docs/architecture/DIRECTORY_STRUCTURE.md)                             | 目錄結構說明     | 專案目錄佈局            |
| [docs/DIRECTORY_TREE.md](./docs/DIRECTORY_TREE.md) ⭐                                                              | 完整目錄樹狀結構 | 全部子目錄展開          |
| [docs/architecture/DELEGATION_WORKFLOW.md](./docs/architecture/DELEGATION_WORKFLOW.md)                             | 委派工作流       | 任務委派流程            |
| [docs/architecture/FileDescription.md](./docs/architecture/FileDescription.md)                                     | 文件描述         | 重要文件說明            |
| [docs/architecture/ADVANCED_SYSTEM_INTEGRATION.md](./docs/architecture/ADVANCED_SYSTEM_INTEGRATION.md)             | 進階系統整合     | 高級整合方案            |
| [docs/architecture/REPOSITORY_INTEGRATION_ASSESSMENT.md](./docs/architecture/REPOSITORY_INTEGRATION_ASSESSMENT.md) | 倉庫整合評估     | 整合評估報告            |
| [docs/architecture/matechat-integration.md](./docs/architecture/matechat-integration.md)                           | MateChat 整合    | 聊天系統整合            |
| [docs/architecture.zh.md](./docs/architecture.zh.md)                                                               | 架構說明（中文） | 中文架構文檔            |

---

## 🎯 語言治理文檔 (`docs/`) ⭐ **NEW**

實時語言政策合規性監控與可視化系統文檔。

| 文件路徑                                                                                         | 說明                     | 關鍵內容                           |
| ------------------------------------------------------------------------------------------------ | ------------------------ | ---------------------------------- |
| [docs/LANGUAGE_GOVERNANCE_IMPLEMENTATION.md](./docs/LANGUAGE_GOVERNANCE_IMPLEMENTATION.md) ⭐   | 完整實作指南             | 架構、API、前端組件、CI/CD         |
| [docs/HOTSPOT_HEATMAP.md](./docs/HOTSPOT_HEATMAP.md)                                            | 違規熱點地圖             | 演算法、色碼、Top 熱點             |
| [docs/MIGRATION_FLOW.md](./docs/MIGRATION_FLOW.md)                                              | 叢集遷移流模型           | 歷史/建議流程、遷移路徑            |
| [docs/KNOWLEDGE_HEALTH.md](./docs/KNOWLEDGE_HEALTH.md)                                          | 知識庫健康度量           | 85/100 分數、趨勢、A-F 等級        |
| [docs/PR_ANALYSIS_AND_ACTION_PLAN.md](./docs/PR_ANALYSIS_AND_ACTION_PLAN.md) ⭐                 | PR #2 深度分析與行動計劃 | 差距分析、下一步、資源需求         |
| [docs/INCOMPLETE_TASKS_SCAN_REPORT.md](./docs/INCOMPLETE_TASKS_SCAN_REPORT.md) ⭐ **NEW**      | 未完成任務掃描報告       | 1,952 項待辦、優先級、行動計劃     |
| [governance/language-governance-report.md](./governance/language-governance-report.md)          | 治理報告                 | 違規清單、合規狀態                 |
| [governance/sankey-data.json](./governance/sankey-data.json)                                    | Sankey 圖資料            | 違規流向                           |
| [governance/hotspot-data.json](./governance/hotspot-data.json)                                  | 熱點資料                 | 檔案強度分數                       |
| [governance/migration-flow.json](./governance/migration-flow.json)                              | 遷移流資料               | 叢集遷移邊                         |
| [governance/semgrep-report.json](./governance/semgrep-report.json)                              | 安全掃描結果             | Semgrep 發現                       |
| [knowledge/language-history.yaml](./knowledge/language-history.yaml)                            | 語言歷史事件             | 修復/掃描/違規時間軸               |

**使用指引：**
```bash
# 存取儀表板
cd apps/web && npm run dev
# 瀏覽器: http://localhost:8000/#/language-governance

# 手動產生資料
python3 tools/generate-sankey-data.py
python3 tools/generate-hotspot-heatmap.py
python3 tools/generate-migration-flow.py

# 查看 API
curl http://localhost:8000/api/v1/language-governance
```

---

## 📋 Refactor Playbooks（重構劇本系統）⭐ **NEW**

三階段結構化重構系統，從解構到執行的完整追溯性。

| 文件路徑                                                                                         | 說明                     | 關鍵內容                           |
| ------------------------------------------------------------------------------------------------ | ------------------------ | ---------------------------------- |
| [docs/refactor_playbooks/README.md](./docs/refactor_playbooks/README.md) ⭐                      | 重構系統總覽             | 三階段流程、使用指南、LLM 整合     |
| [docs/refactor_playbooks/LEGACY_ANALYSIS_REPORT.md](./docs/refactor_playbooks/LEGACY_ANALYSIS_REPORT.md) ⭐ | 舊資產系統完整分析報告   | 架構、索引系統、CI/CD 整合、最佳實務 |
| [docs/refactor_playbooks/ARCHITECTURE.md](./docs/refactor_playbooks/ARCHITECTURE.md)            | 系統架構設計             | 資料流程、生成器設計               |
| [docs/refactor_playbooks/IMPLEMENTATION_SUMMARY.md](./docs/refactor_playbooks/IMPLEMENTATION_SUMMARY.md) | 實作摘要                 | 完成功能、統計數據、使用方式       |

### 三階段文檔

| 階段 | 文件路徑 | 說明 | 關鍵內容 |
|------|----------|------|----------|
| **Phase 1: Deconstruction** | [01_deconstruction/README.md](./docs/refactor_playbooks/01_deconstruction/README.md) | 解構層說明 | 考古挖掘、模式識別、依賴分析 |
|  | [01_deconstruction/legacy_assets_index.yaml](./docs/refactor_playbooks/01_deconstruction/legacy_assets_index.yaml) | 舊資產索引 | ID → 來源/描述/原因 |
| **Phase 2: Integration** | [02_integration/README.md](./docs/refactor_playbooks/02_integration/README.md) | 集成層說明 | 語言策略、模組邊界、架構藍圖 |
| **Phase 3: Refactor** | [03_refactor/README.md](./docs/refactor_playbooks/03_refactor/README.md) | 重構層說明 | 可執行計畫、Auto-Fix 整合 |
|  | [03_refactor/INDEX.md](./docs/refactor_playbooks/03_refactor/INDEX.md) | 人類可讀索引 | 劇本清單、狀態總覽 |
|  | [03_refactor/index.yaml](./docs/refactor_playbooks/03_refactor/index.yaml) | 機器可讀索引 | CI/工具使用、cluster 映射 |

### 模板與規範

| 文件路徑 | 說明 | 用途 |
|----------|------|------|
| [03_refactor/templates/REFRACTOR_PLAYBOOK_TEMPLATE.md](./docs/refactor_playbooks/03_refactor/templates/REFRACTOR_PLAYBOOK_TEMPLATE.md) | 劇本標準模板 | 建立新重構劇本 |
| [03_refactor/templates/SECTION_SNIPPETS.md](./docs/refactor_playbooks/03_refactor/templates/SECTION_SNIPPETS.md) | 常用章節片段 | P0/P1/P2 範例、驗收條件 |
| [03_refactor/templates/META_CONVENTIONS.md](./docs/refactor_playbooks/03_refactor/templates/META_CONVENTIONS.md) | 命名與格式規範 | 檔名規則、Cluster ID 格式 |

**使用指引：**
```bash
# 生成所有 clusters 的 playbooks
python3 tools/generate-refactor-playbook.py --repo-root .

# 生成特定 cluster
python3 tools/generate-refactor-playbook.py --cluster "core/"

# 生成 LLM prompts
python3 tools/generate-refactor-playbook.py --use-llm

# 查看人類可讀索引
cat docs/refactor_playbooks/03_refactor/INDEX.md

# 查看機器可讀索引（CI/工具使用）
cat docs/refactor_playbooks/03_refactor/index.yaml
```

**核心概念：**
- **三階段流程**：解構 → 集成 → 重構
- **舊資產管理**：實體隔離、知識保留、引用透明
- **CI/CD 整合**：Auto-Fix Bot、違規映射、狀態追蹤
- **可執行計畫**：P0/P1/P2 優先級、具體到檔案層級

---

## 🤖 自動化系統文檔 (`automation/`)

自動化模組、智能代理與超自動化策略文檔。

### 智能自動化 (`automation/intelligent/`)

| 文件路徑                                                                           | 說明           | 操作指引               |
| ---------------------------------------------------------------------------------- | -------------- | ---------------------- |
| [automation/intelligent/README.md](./automation/intelligent/README.md)             | 智能自動化系統 | 多代理 AI 代碼分析系統 |
| [automation/intelligent/AUTO_UPGRADE.md](./automation/intelligent/AUTO_UPGRADE.md) | 自動升級指南   | 系統升級流程           |

### Island AI Multi-Agent System (`island-ai/`) ⭐ **NEW**

**Island AI Stage 1** - 六個基礎 Agent 的 TypeScript 實現，提供智能診斷與系統洞察。

| 文件路徑                                   | 說明                 | 狀態     | 操作指引                       |
| ------------------------------------------ | -------------------- | -------- | ------------------------------ |
| [island-ai/README.md](./island-ai/README.md) ⭐ | Island AI 總覽 | ✅ Stage 1 | 多 Agent 系統架構與使用指南     |
| [island-ai.md](./island-ai.md)              | 四階段實施路線圖     | 📋 規劃  | 完整發展計畫（54,000 行代碼）  |
| [island-ai-readme.md](./island-ai-readme.md) | Stage 1 詳細說明   | ✅ 完成  | 基礎運行時與 6 個 Agent 實現   |

**Stage 1 Agents（已實現）：**

| Agent 名稱          | 模組路徑                              | 職責               | 關鍵功能                      |
| ------------------- | ------------------------------------- | ------------------ | ----------------------------- |
| **Architect**       | `island-ai/src/agents/architect/`     | 架構設計與優化     | 系統分析、設計模式建議、性能優化 |
| **Security**        | `island-ai/src/agents/security/`      | 安全審計與修補     | 漏洞掃描、OWASP/CWE 規則檢查 |
| **DevOps**          | `island-ai/src/agents/devops/`        | 部署與監控         | CI/CD 管道、自動擴展、告警管理 |
| **QA**              | `island-ai/src/agents/qa/`            | 測試與驗證         | 單元/整合/E2E 測試策略執行   |
| **Data Scientist**  | `island-ai/src/agents/data-scientist/` | 數據分析與預測   | 回歸/分類/聚類模型、趨勢預測 |
| **Product Manager** | `island-ai/src/agents/product-manager/` | 產品優先級與路線圖 | KPI 追蹤、用戶反饋分析、功能排序 |

**快速開始：**
```bash
# 建置 Island AI
npm run build -w island-ai

# 執行單元測試（需先實現）
npm run test -w island-ai

# 使用範例
import { runStageOne } from 'island-ai';

const reports = await runStageOne({
  requestId: 'diagnostic-001',
  timestamp: new Date(),
  payload: { deploymentsPerWeek: 15 }
});
```

**整合狀態：**
- ✅ npm workspace 整合完成
- ✅ TypeScript 建置配置完成
- ✅ CI/CD 自動包含（透過 `--workspaces` 參數）
- 🔄 SynergyMesh 核心引擎整合（進行中）
- 🔄 Agent 協作機制（Stage 2 規劃）

**下一階段（Stage 2）：**
- 7 種 Agent 協作機制
- 觸發器系統與決策引擎
- 多 Agent 協調與同步屏障
- 詳見 [island-ai.md](./island-ai.md) 四階段路線圖

### 統一架構骨架系統 (`automation/architecture-skeletons/`) ⭐ **NEW**

完整的 11 個架構骨架系統，整合 unmanned-engineer-ceo 指南與 automation/autonomous 實現。

| 文件路徑                                                                                                                    | 說明                       | 操作指引             |
| --------------------------------------------------------------------------------------------------------------------------- | -------------------------- | -------------------- |
| [automation/architecture-skeletons/README.md](./automation/architecture-skeletons/README.md) ⭐                             | 統一骨架系統入口           | AI 和工程師使用指南  |
| [automation/architecture-skeletons/unified-index.yaml](./automation/architecture-skeletons/unified-index.yaml)             | 完整骨架索引和映射         | AI 查詢主要文件      |
| [automation/architecture-skeletons/mapping.yaml](./automation/architecture-skeletons/mapping.yaml)                         | 指南與實現雙向映射         | 路徑映射參考         |
| [docs/ARCHITECTURE_SKELETON_ANALYSIS.md](./docs/ARCHITECTURE_SKELETON_ANALYSIS.md)                                         | 架構骨架整合分析報告       | 整合策略和實施計劃   |
| [unmanned-engineer-ceo/60-machine-guides/70-architecture-skeletons/](./unmanned-engineer-ceo/60-machine-guides/70-architecture-skeletons/) | 11 個完整架構指南（源文件） | AI 架構決策參考      |

### 自主系統框架 (`automation/autonomous/`)

11 個架構骨架的實現代碼（與 unmanned-engineer-ceo 指南對應）。

| 文件路徑                                                                                                                          | 說明                     | 狀態     | 操作指引                 |
| --------------------------------------------------------------------------------------------------------------------------------- | ------------------------ | -------- | ------------------------ |
| [automation/autonomous/README.md](./automation/autonomous/README.md)                                                              | 自主系統框架             | ✅       | 11 骨架架構說明          |
| [automation/autonomous/INTEGRATION_SUMMARY.md](./automation/autonomous/INTEGRATION_SUMMARY.md)                                    | 整合摘要                 | ✅       | 整合實施結果             |
| [automation/autonomous/architecture-stability/README.md](./automation/autonomous/architecture-stability/README.md)                | 架構穩定性骨架           | ✅ 生產  | 即時飛控系統（C++ ROS2） |
| [automation/autonomous/api-governance/README.md](./automation/autonomous/api-governance/README.md)                                | API 治理骨架             | ✅ 生產  | API 規範與驗證（Python） |
| [automation/autonomous/security-observability/README.md](./automation/autonomous/security-observability/README.md)                | 安全與可觀測性骨架       | ✅ 生產  | 分散式事件日誌（Go）     |
| [automation/autonomous/testing-compatibility/README.md](./automation/autonomous/testing-compatibility/README.md)                  | 測試治理骨架             | ✅ 生產  | 自動化測試套件（Python） |
| [automation/autonomous/docs-examples/README.md](./automation/autonomous/docs-examples/README.md)                                  | 文檔治理骨架             | ✅ 生產  | 治理矩陣和範例           |
| [automation/autonomous/identity-tenancy/README.md](./automation/autonomous/identity-tenancy/README.md)                            | 身份與多租戶骨架         | 🟡 設計  | 認證授權、RBAC/ABAC      |
| [automation/autonomous/data-governance/README.md](./automation/autonomous/data-governance/README.md)                              | 資料治理骨架             | 🟡 設計  | 資料分類、隱私合規       |
| [automation/autonomous/performance-reliability/README.md](./automation/autonomous/performance-reliability/README.md)              | 性能與可靠性骨架         | 🟡 設計  | SLA、容量規劃、災難恢復  |
| [automation/autonomous/cost-management/README.md](./automation/autonomous/cost-management/README.md)                              | 成本管理骨架             | 🟡 設計  | 成本監控、預算規劃       |
| [automation/autonomous/knowledge-base/README.md](./automation/autonomous/knowledge-base/README.md)                                | 知識庫骨架               | 🟡 設計  | 知識組織、AI 上下文管理  |
| [automation/autonomous/nucleus-orchestrator/README.md](./automation/autonomous/nucleus-orchestrator/README.md)                    | 核心編排骨架             | 🟡 設計  | 工作流編排、代理協調     |
| [automation/autonomous/docs-examples/API_DOCUMENTATION.md](./automation/autonomous/docs-examples/API_DOCUMENTATION.md)            | API 文檔                 | ✅       | API 參考                 |
| [automation/autonomous/docs-examples/QUICKSTART.md](./automation/autonomous/docs-examples/QUICKSTART.md)                          | 快速入門                 | ✅       | 自主系統快速開始         |

### 架構師工具 (`automation/architect/`)

| 文件路徑                                                                                                               | 說明       | 操作指引       |
| ---------------------------------------------------------------------------------------------------------------------- | ---------- | -------------- |
| [automation/architect/README.md](./automation/architect/README.md)                                                     | 架構師工具 | 架構分析與修復 |
| [automation/architect/docs/API.md](./automation/architect/docs/API.md)                                                 | API 文檔   | 架構師 API     |
| [automation/architect/docs/DEPLOYMENT.md](./automation/architect/docs/DEPLOYMENT.md)                                   | 部署指南   | 部署說明       |
| [automation/architect/docs/INTEGRATION_GUIDE.md](./automation/architect/docs/INTEGRATION_GUIDE.md)                     | 整合指南   | 整合說明       |
| [automation/architect/docs/automation-iteration/README.md](./automation/architect/docs/automation-iteration/README.md) | 自動化迭代 | 迭代說明       |
| [automation/architect/docs/autonomous-driving/README.md](./automation/architect/docs/autonomous-driving/README.md)     | 自駕車系統 | 自駕車整合     |
| [automation/architect/docs/drone-systems/README.md](./automation/architect/docs/drone-systems/README.md)               | 無人機系統 | 無人機控制     |
| [automation/architect/frameworks-popular/README.md](./automation/architect/frameworks-popular/README.md)               | 熱門框架   | 框架說明       |

### 超自動化策略 (`automation/hyperautomation/`)

| 文件路徑                                                                                                                                       | 說明         | 操作指引       |
| ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | -------------- |
| [automation/hyperautomation/README.md](./automation/hyperautomation/README.md)                                                                 | 超自動化系統 | UAV 治理策略   |
| [automation/hyperautomation/CHANGELOG.md](./automation/hyperautomation/CHANGELOG.md)                                                           | 更新日誌     | 版本變更       |
| [automation/hyperautomation/QUICK_REFERENCE.md](./automation/hyperautomation/QUICK_REFERENCE.md)                                               | 快速參考     | 常用命令       |
| [automation/hyperautomation/docs/ci-cd-strategy.md](./automation/hyperautomation/docs/ci-cd-strategy.md)                                       | CI/CD 策略   | 持續整合策略   |
| [automation/hyperautomation/docs/core-principles.md](./automation/hyperautomation/docs/core-principles.md)                                     | 核心原則     | 設計原則       |
| [automation/hyperautomation/docs/uav-autonomous-driving-governance.md](./automation/hyperautomation/docs/uav-autonomous-driving-governance.md) | UAV 自駕治理 | 無人機自駕治理 |
| [automation/hyperautomation/docs/usage-notes.md](./automation/hyperautomation/docs/usage-notes.md)                                             | 使用說明     | 使用注意事項   |
| [automation/hyperautomation/templates/impl/examples/README.md](./automation/hyperautomation/templates/impl/examples/README.md)                 | 範例模板     | 實作範例       |

### 自我覺察報告 (`automation/`)

| 文件路徑                                                                      | 說明                 | 操作指引                                    |
| ----------------------------------------------------------------------------- | -------------------- | ------------------------------------------- |
| [automation/self-awareness-dashboard.md](./automation/self-awareness-dashboard.md) | 自我覺察儀表板指南 | CLI、PR、Nightly 報告與 JSON 輸出的整合流程 |

---

## 🏛️ 核心平台文檔 (`core/`)

平台核心服務、執行引擎與合約管理文檔。

| 文件路徑                                                                                         | 說明           | 操作指引       |
| ------------------------------------------------------------------------------------------------ | -------------- | -------------- |
| [core/README.md](./core/README.md)                                                               | 核心平台概覽   | 核心能力說明   |
| [core/advisory-database/README.md](./core/advisory-database/README.md)                           | 漏洞數據庫     | 安全諮詢數據   |
| [core/contract_service/README.md](./core/contract_service/README.md)                             | 合約服務       | 合約管理微服務 |
| [core/contract_service/external/README.md](./core/contract_service/external/README.md)           | 外部合約       | 外部 API 規範  |
| [core/modules/execution_architecture/README.md](./core/modules/execution_architecture/README.md) | 執行架構       | 執行拓撲設計   |
| [core/modules/execution_engine/README.md](./core/modules/execution_engine/README.md)             | 執行引擎       | 執行邏輯抽象   |
| [core/modules/mind_matrix/RUNTIME_README.md](./core/modules/mind_matrix/RUNTIME_README.md)       | 心智矩陣運行時 | 多代理協作     |

### 合約服務 L1 層 (`core/contract_service/contracts-L1/`)

| 文件路徑                                                                                                                                             | 說明             | 操作指引      |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ------------- |
| [core/contract_service/contracts-L1/ai-chat-service/README.md](./core/contract_service/contracts-L1/ai-chat-service/README.md)                       | AI 聊天服務      | 聊天服務說明  |
| [core/contract_service/contracts-L1/contracts/BUILD_PROVENANCE.md](./core/contract_service/contracts-L1/contracts/BUILD_PROVENANCE.md)               | 構建溯源         | SLSA 溯源說明 |
| [core/contract_service/contracts-L1/contracts/SLSA_INTEGRATION_REPORT.md](./core/contract_service/contracts-L1/contracts/SLSA_INTEGRATION_REPORT.md) | SLSA 整合報告    | SLSA 實施報告 |
| [core/contract_service/contracts-L1/contracts/deploy/README.md](./core/contract_service/contracts-L1/contracts/deploy/README.md)                     | 部署說明         | 部署指南      |
| [core/contract_service/contracts-L1/contracts/docs/architecture.zh.md](./core/contract_service/contracts-L1/contracts/docs/architecture.zh.md)       | 架構說明（中文） | 合約架構      |
| [core/contract_service/contracts-L1/contracts/docs/runbook.zh.md](./core/contract_service/contracts-L1/contracts/docs/runbook.zh.md)                 | 運維手冊（中文） | 運維指南      |
| [core/contract_service/contracts-L1/contracts/sbom/README.md](./core/contract_service/contracts-L1/contracts/sbom/README.md)                         | SBOM 說明        | 軟體物料清單  |
| [core/contract_service/contracts-L1/contracts/web/README.md](./core/contract_service/contracts-L1/contracts/web/README.md)                           | Web 服務         | Web 服務說明  |

---

## 🔄 CI/CD 與運維文檔

持續整合、部署與運維相關文檔。

### CI/CD 文檔 (`docs/ci-cd/`)

| 文件路徑                                                                       | 說明         | 操作指引    |
| ------------------------------------------------------------------------------ | ------------ | ----------- |
| [docs/ci-cd/README.md](./docs/ci-cd/README.md)                                 | CI/CD 入口   | CI/CD 總覽  |
| [docs/ci-cd/workflow-coordination.md](./docs/ci-cd/workflow-coordination.md) ⭐ | 工作流程協調策略 | 三層工作流程架構、成本優化、最佳實踐 |
| [docs/ci-cd/IMPLEMENTATION_SUMMARY.md](./docs/ci-cd/IMPLEMENTATION_SUMMARY.md) | 實施摘要     | 實施結果    |
| [docs/ci-cd/stage-1-basic-ci.md](./docs/ci-cd/stage-1-basic-ci.md)             | 基礎 CI 階段 | 第一階段 CI |

### 自動化流程文檔

| 文件路徑                                                                       | 說明               | 操作指引      |
| ------------------------------------------------------------------------------ | ------------------ | ------------- |
| [docs/AUTO_REVIEW_MERGE.md](./docs/AUTO_REVIEW_MERGE.md)                       | 自動審查合併       | PR 自動化流程 |
| [docs/AUTO_MERGE.md](./docs/AUTO_MERGE.md)                                     | 自動合併           | 自動合併設置  |
| [docs/AUTO_ASSIGNMENT_SYSTEM.md](./docs/AUTO_ASSIGNMENT_SYSTEM.md)             | 自動派工系統       | 任務分配機制  |
| [docs/AUTO_ASSIGNMENT_API.md](./docs/AUTO_ASSIGNMENT_API.md)                   | 自動派工 API       | API 參考      |
| [docs/AUTO_ASSIGNMENT_SUMMARY.md](./docs/AUTO_ASSIGNMENT_SUMMARY.md)           | 自動派工摘要       | 系統摘要      |
| [docs/AUTO_ASSIGNMENT_DEMO.md](./docs/AUTO_ASSIGNMENT_DEMO.md)                 | 自動派工演示       | 演示說明      |
| [docs/DYNAMIC_CI_ASSISTANT.md](./docs/DYNAMIC_CI_ASSISTANT.md)                 | 動態 CI 助手       | CI 互動客服   |
| [docs/CI_AUTO_COMMENT_SYSTEM.md](./docs/CI_AUTO_COMMENT_SYSTEM.md)             | CI 自動評論系統    | 自動評論      |
| [docs/CI_BATCH_UPGRADE_SUMMARY.md](./docs/CI_BATCH_UPGRADE_SUMMARY.md)         | CI 批量升級摘要    | 批量升級      |
| [docs/CI_DEPLOYMENT_UPGRADE_PLAN.md](./docs/CI_DEPLOYMENT_UPGRADE_PLAN.md)     | CI 部署升級計劃    | 升級計劃      |
| [docs/CI_GLOBAL_STATUS_FIX.md](./docs/CI_GLOBAL_STATUS_FIX.md)                 | CI 全局狀態修復    | 狀態修復      |
| [docs/INTERACTIVE_CI_UPGRADE_GUIDE.md](./docs/INTERACTIVE_CI_UPGRADE_GUIDE.md) | 互動式 CI 升級指南 | 升級指南      |
| [docs/ci-troubleshooting.md](./docs/ci-troubleshooting.md)                     | CI 故障排除        | 問題排查      |
| [docs/autonomous-ci-compliance.md](./docs/autonomous-ci-compliance.md)         | 自主 CI 合規       | 合規檢查      |

### 運維文檔 (`docs/operations/`)

| 文件路徑                                                                             | 說明     | 操作指引     |
| ------------------------------------------------------------------------------------ | -------- | ------------ |
| [docs/operations/DeploymentGuide.md](./docs/operations/DeploymentGuide.md)           | 部署指南 | 完整部署流程 |
| [docs/operations/MONITORING_GUIDE.md](./docs/operations/MONITORING_GUIDE.md)         | 監控指南 | 監控設置     |
| [docs/operations/PRODUCTION_READINESS.md](./docs/operations/PRODUCTION_READINESS.md) | 生產就緒 | 上線檢查清單 |

### CI 治理框架 (`config/`, `scripts/hooks/`)

> **新增於 PR #73** - 完整的 CI 治理框架，包含智能代理配置、錯誤處理映射、和 Stage 0 自動化檢查。

| 文件路徑 | 說明 | 操作指引 |
| --- | --- | --- |
| [config/ci-agent-config.yaml](./config/ci-agent-config.yaml) | CI Copilot 智能代理配置 | 定義代理角色、分析流程、骨架整合 |
| [config/ci-error-handler.yaml](./config/ci-error-handler.yaml) | 錯誤分類與行動映射 | 錯誤類型 → 優先級 → 修復步驟 |
| [.github/workflows/reusable-ci.yml](./.github/workflows/reusable-ci.yml) ⭐ | 可重用 CI 管道 | 統一的 lint、test、build 流程 |
| [.github/workflows/reusable-docker-build.yml](./.github/workflows/reusable-docker-build.yml) ⭐ | 可重用 Docker 建置 | 統一的容器建置、測試、掃描流程 |
| [.github/workflows/monorepo-dispatch.yml](./.github/workflows/monorepo-dispatch.yml) | Monorepo CI 調度器 | 基礎 CI，路徑偵測、快速反饋 |
| [.github/workflows/core-services-ci.yml](./.github/workflows/core-services-ci.yml) | 核心服務 CI | 包含 Docker 建置的完整 CI |
| [.github/workflows/integration-deployment.yml](./.github/workflows/integration-deployment.yml) | 整合與部署 | 全面系統整合測試、四層驗證 |
| [.github/workflows/arch-governance-validation.yml](./.github/workflows/arch-governance-validation.yml) | 架構與治理驗證工作流程 | 自動驗證架構、安全、資料治理 |
| [scripts/hooks/pre-commit](./scripts/hooks/pre-commit) | Stage 0 提交前檢查 | YAML 驗證、Workflow 檢查、敏感資料掃描 |
| [scripts/hooks/pre-push](./scripts/hooks/pre-push) | Stage 0 推送前驗證 | 必要檔案、目錄結構、骨架索引檢查 |
| [scripts/hooks/install-hooks.sh](./scripts/hooks/install-hooks.sh) | Git Hooks 安裝腳本 | 一鍵安裝本地 hooks |
| [docs/reports/PR73_CI_GOVERNANCE_ANALYSIS.md](./docs/reports/PR73_CI_GOVERNANCE_ANALYSIS.md) | CI 治理框架分析報告 | 完整架構分析與整合說明 |

### 自動修復文檔 (`docs/automation/`)

| 文件路徑                                                                         | 說明              | 操作指引       |
| -------------------------------------------------------------------------------- | ----------------- | -------------- |
| [docs/automation/AUTO_FIX_BOT.md](./docs/automation/AUTO_FIX_BOT.md)             | Auto-Fix Bot      | 自動修復機器人 |
| [docs/automation/AUTO_FIX_BOT_GUIDE.md](./docs/automation/AUTO_FIX_BOT_GUIDE.md) | Auto-Fix Bot 指南 | 使用指南       |
| [docs/AUTO_FIX_BOT_V2_GUIDE.md](./docs/AUTO_FIX_BOT_V2_GUIDE.md)                 | Auto-Fix Bot V2   | V2 版本指南    |

---

## 🔒 安全與治理文檔

安全政策、漏洞管理與治理配置文檔。

### 安全文檔 (`docs/security/`)

| 文件路徑                                                                                       | 說明          | 操作指引                 |
| ---------------------------------------------------------------------------------------------- | ------------- | ------------------------ |
| [docs/security/SECURITY_SUMMARY.md](./docs/security/SECURITY_SUMMARY.md)                       | 安全摘要      | 安全總覽                 |
| [docs/security/GHAS_IMPLEMENTATION_SUMMARY.md](./docs/security/GHAS_IMPLEMENTATION_SUMMARY.md) | GHAS 實施摘要 | GitHub Advanced Security |
| [docs/VULNERABILITY_MANAGEMENT.md](./docs/VULNERABILITY_MANAGEMENT.md)                         | 漏洞管理      | CVE 偵測與回應           |
| [docs/SECRET_SCANNING.md](./docs/SECRET_SCANNING.md)                                           | 密鑰掃描      | 密鑰偵測                 |
| [docs/SECURITY_TRAINING.md](./docs/SECURITY_TRAINING.md)                                       | 安全培訓      | 安全最佳實踐             |
| [docs/GHAS_DEPLOYMENT.md](./docs/GHAS_DEPLOYMENT.md)                                           | GHAS 部署     | GHAS 設置                |
| [docs/GHAS_COMPLETE_GUIDE.md](./docs/GHAS_COMPLETE_GUIDE.md)                                   | GHAS 完整指南 | 完整 GHAS 指南           |
| [docs/CODEQL_SETUP.md](./docs/CODEQL_SETUP.md)                                                 | CodeQL 設置   | CodeQL 配置              |

### 治理文檔 (`governance/`)

| 文件路徑                                                                                                                     | 說明              | 操作指引      |
| ---------------------------------------------------------------------------------------------------------------------------- | ----------------- | ------------- |
| [governance/README.md](./governance/README.md)                                                                               | 治理入口          | 政策與規則    |
| [governance/ARCHITECTURE_GOVERNANCE_MATRIX.md](./governance/ARCHITECTURE_GOVERNANCE_MATRIX.md) ⭐                            | 架構治理矩陣      | 九大治理維度完整框架 |
| [governance/architecture/layers-domains.yaml](./governance/architecture/layers-domains.yaml)                                 | 層級與領域定義    | 架構層級與功能領域語義 |
| [governance/ownership-map.yaml](./governance/ownership-map.yaml)                                                             | 所有權與生命週期  | 模組責任人與狀態追蹤 |
| [governance/architecture-health.yaml](./governance/architecture-health.yaml)                                                 | 架構健康度指標    | 可量測的架構品質閘門 |
| [governance/behavior-contracts/](./governance/behavior-contracts/)                                                          | 行為契約目錄      | 模組 API、事件與不變條件 |
| [governance/modules/](./governance/modules/)                                                                                 | 模組角色與能力    | 模組責任與功能定義 |
| [governance/policies/architecture-rules.yaml](./governance/policies/architecture-rules.yaml)                                 | 架構策略規則      | 可執行的治理策略 |
| [governance/23-policies/python-code-standards.md](./governance/23-policies/python-code-standards.md) ⭐ **NEW**              | Python 代碼標準   | Python 語法與質量規範 |
| [governance/35-scripts/validate-python-syntax.py](./governance/35-scripts/validate-python-syntax.py) ⭐ **NEW**              | Python 語法驗證器 | 自動化語法檢查工具 |
| [governance/environment-matrix/LANGUAGE_DIMENSION_MAPPING.md](./governance/environment-matrix/LANGUAGE_DIMENSION_MAPPING.md) | 語言維度映射      | 多語言配置    |
| [governance/policies/conftest/matechat-integration/README.md](./governance/policies/conftest/matechat-integration/README.md) | MateChat 整合策略 | Conftest 策略 |

### 重構 Playbooks (`docs/refactor_playbooks/`) ⭐ **NEW**

AI 驅動的重構計畫生成系統，為每個目錄群集提供可執行的重構指南。

| 文件路徑                                                                     | 說明                   | 操作指引                         |
| ---------------------------------------------------------------------------- | ---------------------- | -------------------------------- |
| [docs/refactor_playbooks/README.md](./docs/refactor_playbooks/README.md) ⭐ | 重構 Playbooks 入口    | 了解如何使用和生成重構計畫       |
| [tools/generate-refactor-playbook.py](./tools/generate-refactor-playbook.py) | Playbook 生成器        | 自動生成 cluster 重構計畫        |
| [governance/language-governance-report.md](./governance/language-governance-report.md) | 語言治理報告           | 語言違規與統計資料               |
| [governance/ai-refactor-suggestions.md](./governance/ai-refactor-suggestions.md) | AI 重構建議            | 全局重構策略與最佳實踐           |
| [apps/web/public/data/hotspot.json](./apps/web/public/data/hotspot.json)     | Hotspot 熱點分析       | 高風險檔案列表                   |
| [apps/web/public/data/cluster-heatmap.json](./apps/web/public/data/cluster-heatmap.json) | Cluster 熱力圖         | 目錄群集健康分數                 |
| [apps/web/public/data/migration-flow.json](./apps/web/public/data/migration-flow.json) | 語言遷移流向           | 語言遷移建議與歷史               |

**關鍵功能：**
- 🤖 LLM 驅動的重構計畫生成（包含 System/User Prompt 模板）
- 📊 整合語言治理、安全掃描、熱點分析數據
- 🎯 分級重構計畫（P0/P1/P2）與明確的行動項目
- 🔄 自動化與人工審查範圍區分
- ✅ 驗收條件與成功指標定義

**使用方式：**
```bash
# 生成所有 clusters 的 playbooks
python3 tools/generate-refactor-playbook.py

# 生成特定 cluster 的 playbook
python3 tools/generate-refactor-playbook.py --cluster "core/"

# 生成 LLM prompts（供 ChatGPT/Claude 使用）
python3 tools/generate-refactor-playbook.py --use-llm
```

---

## 🔌 服務與代理文檔 (`services/`)

業務代理服務與 MCP 伺服器文檔。

### 代理服務 (`services/agents/`)

| 文件路徑                                                                                               | 說明         | 操作指引       |
| ------------------------------------------------------------------------------------------------------ | ------------ | -------------- |
| [services/agents/README.md](./services/agents/README.md)                                               | 代理服務入口 | 代理服務總覽   |
| [services/agents/auto-repair/README.md](./services/agents/auto-repair/README.md)                       | 自動修復代理 | 自動偵測修復   |
| [services/agents/code-analyzer/README.md](./services/agents/code-analyzer/README.md)                   | 代碼分析代理 | 深度代碼分析   |
| [services/agents/dependency-manager/README.md](./services/agents/dependency-manager/README.md)         | 依賴管理代理 | 版本與漏洞管理 |
| [services/agents/orchestrator/README.md](./services/agents/orchestrator/README.md)                     | 編排代理     | 多代理協調     |
| [services/agents/vulnerability-detector/README.md](./services/agents/vulnerability-detector/README.md) | 漏洞偵測代理 | CVE 資料庫比對 |

### MCP 伺服器 (`mcp-servers/`)

| 文件路徑                                                   | 說明           | 操作指引     |
| ---------------------------------------------------------- | -------------- | ------------ |
| [mcp-servers/README.md](./mcp-servers/README.md)           | MCP 伺服器入口 | LLM 工具端點 |
| [mcp-servers/VALIDATION.md](./mcp-servers/VALIDATION.md)   | 驗證說明       | 驗證配置     |

> **注意**: 歷史路徑 `services/mcp/` 仍然存在以保持向後相容，但 CI/CD 和 npm workspaces 使用 `mcp-servers/`。

---

## 📱 應用程式文檔 (`apps/`)

Web 前端與 API 服務文檔。

| 文件路徑                                                             | 說明         | 操作指引           |
| -------------------------------------------------------------------- | ------------ | ------------------ |
| [apps/web/README.md](./apps/web/README.md)                           | Web 應用入口 | 企業級代碼分析服務 |
| [apps/web/PHASE2_IMPROVEMENTS.md](./apps/web/PHASE2_IMPROVEMENTS.md) | Phase 2 改進 | API 與部署改進     |

---

## 🛠️ 開發環境文檔 (`.devcontainer/`)

開發容器、模板與環境設置文檔。

| 文件路徑                                                                     | 說明         | 操作指引     |
| ---------------------------------------------------------------------------- | ------------ | ------------ |
| [.devcontainer/README.md](./.devcontainer/README.md)                         | 開發容器入口 | 開發環境設置 |
| [.devcontainer/QUICK_START.md](./.devcontainer/QUICK_START.md)               | 快速開始     | 環境快速設置 |
| [.devcontainer/CHANGELOG.md](./.devcontainer/CHANGELOG.md)                   | 更新日誌     | 環境變更     |
| [.devcontainer/KB.md](./.devcontainer/KB.md)                                 | 知識庫       | 常見問題     |
| [.devcontainer/SOLUTION_SUMMARY.md](./.devcontainer/SOLUTION_SUMMARY.md)     | 解決方案摘要 | 方案說明     |
| [.devcontainer/TEST-GUIDE.md](./.devcontainer/TEST-GUIDE.md)                 | 測試指南     | 測試說明     |
| [.devcontainer/life-system-README.md](./.devcontainer/life-system-README.md) | 生命系統說明 | 生命週期     |

### 模板 (`.devcontainer/templates/`)

| 文件路徑                                                                                                           | 說明             | 操作指引     |
| ------------------------------------------------------------------------------------------------------------------ | ---------------- | ------------ |
| [.devcontainer/templates/connector-template/README.md](./.devcontainer/templates/connector-template/README.md)     | 連接器模板       | 連接器開發   |
| [.devcontainer/templates/docker/README.md](./.devcontainer/templates/docker/README.md)                             | Docker 模板      | 容器配置     |
| [.devcontainer/templates/docker/NODEJS_USER_SETUP.md](./.devcontainer/templates/docker/NODEJS_USER_SETUP.md)       | Node.js 用戶設置 | Node.js 環境 |
| [.devcontainer/templates/integration-template/README.md](./.devcontainer/templates/integration-template/README.md) | 整合模板         | 整合開發     |
| [.devcontainer/templates/service-template/README.md](./.devcontainer/templates/service-template/README.md)         | 服務模板         | 服務開發     |

---

## 🏗️ 基礎設施文檔 (`infrastructure/`)

Kubernetes 部署與基礎設施配置文檔。

| 文件路徑                                                                                                                         | 說明            | 操作指引 |
| -------------------------------------------------------------------------------------------------------------------------------- | --------------- | -------- |
| [infrastructure/kubernetes/README.md](./infrastructure/kubernetes/README.md)                                                     | Kubernetes 入口 | K8s 總覽 |
| [infrastructure/kubernetes/manifests/README.md](./infrastructure/kubernetes/manifests/README.md)                                 | K8s 清單        | 部署清單 |
| [infrastructure/kubernetes/manifests/IMPLEMENTATION_SUMMARY.md](./infrastructure/kubernetes/manifests/IMPLEMENTATION_SUMMARY.md) | 實施摘要        | 實施結果 |

---

## 🔧 工具與腳本文檔 (`tools/`)

CLI 工具與腳本文檔。

| 文件路徑                                             | 說明              | 操作指引     |
| ---------------------------------------------------- | ----------------- | ------------ |
| [tools/cli/README.md](./tools/cli/README.md)         | Admin Copilot CLI | CLI 工具說明 |
| [tools/scripts/README.md](./tools/scripts/README.md) | 腳本說明          | 工具腳本     |

### 治理與重構工具 (`tools/`)

| 文件路徑                                                                                                 | 說明                     | 操作指引                   |
| -------------------------------------------------------------------------------------------------------- | ------------------------ | -------------------------- |
| [tools/generate-refactor-playbook.py](./tools/generate-refactor-playbook.py) ⭐                          | AI 重構 Playbook 生成器  | 為每個 cluster 生成重構計畫 |
| [tools/governance/language-governance-analyzer.py](./tools/governance/language-governance-analyzer.py)   | 語言治理分析器           | 掃描語言違規               |
| [tools/governance/check-language-policy.py](./tools/governance/check-language-policy.py)                 | 語言政策檢查             | CI 語言政策驗證            |
| [tools/language-health-score.py](./tools/language-health-score.py)                                       | 語言健康分數計算         | 計算語言治理健康分數       |
| [tools/generate-language-dashboard.py](./tools/generate-language-dashboard.py)                           | 語言儀表板生成器         | 生成治理儀表板數據         |

---

## 📋 其他文檔

### 主要功能文檔 (`docs/`)

| 文件路徑                                                         | 說明              | 操作指引              |
| ---------------------------------------------------------------- | ----------------- | --------------------- |
| [docs/README.md](./docs/README.md)                               | 文檔入口          | 文檔總覽              |
| [docs/index.md](./docs/index.md)                                 | 文檔索引          | 索引頁面              |
| [docs/QUICK_START.md](./docs/QUICK_START.md)                     | 快速開始          | Auto-Fix Bot 快速上手 |
| [docs/EXAMPLES.md](./docs/EXAMPLES.md)                           | 範例              | 使用範例              |
| [docs/INTEGRATION_GUIDE.md](./docs/INTEGRATION_GUIDE.md)         | 整合指南          | 外部系統整合          |
| [docs/COPILOT_SETUP.md](./docs/COPILOT_SETUP.md)                 | Copilot 設置      | GitHub Copilot 整合   |
| [docs/ADMIN_COPILOT_CLI.md](./docs/ADMIN_COPILOT_CLI.md)         | Admin Copilot CLI | CLI 完整文檔          |
| [docs/CLOUD_DELEGATION.md](./docs/CLOUD_DELEGATION.md)           | 雲端委派          | 分散式任務處理        |
| [docs/LIVING_KNOWLEDGE_BASE.md](./docs/LIVING_KNOWLEDGE_BASE.md) | 活體知識庫        | 系統自我感知設計      |
| [docs/PROJECT_STRUCTURE.md](./docs/PROJECT_STRUCTURE.md)         | 專案結構          | 目錄說明              |
| [docs/project-manifest.md](./docs/project-manifest.md)           | 自述守則          | 變更範圍、禁行清單    |
| [docs/issues/known-failures.md](./docs/issues/known-failures.md) | 已知問題索引      | 常見失敗範例與修復    |
| [docs/ROOT_README.md](./docs/ROOT_README.md)                     | 根 README         | 根目錄說明            |
| [docs/VISUAL_ELEMENTS.md](./docs/VISUAL_ELEMENTS.md)             | 視覺元素          | UI 元素指南           |
| [docs/BUILD_COMPAT.md](./docs/BUILD_COMPAT.md)                   | 構建兼容性        | 兼容性說明            |
| [docs/MIGRATION.md](./docs/MIGRATION.md)                         | 遷移指南          | 版本遷移              |
| [docs/MERGE_BLOCKED_FIX.md](./docs/MERGE_BLOCKED_FIX.md)         | 合併阻塞修復      | 修復合併問題          |
| [docs/DISASTER_RECOVERY.md](./docs/DISASTER_RECOVERY.md)         | 災難恢復          | 恢復流程              |
| [docs/EFFICIENCY_METRICS.md](./docs/EFFICIENCY_METRICS.md)       | 效率指標          | 性能指標              |

### 進階功能文檔

| 文件路徑                                                                                   | 說明              | 操作指引         |
| ------------------------------------------------------------------------------------------ | ----------------- | ---------------- |
| [docs/ADVANCED_ESCALATION_SYSTEM.md](./docs/ADVANCED_ESCALATION_SYSTEM.md)                 | 進階升級系統      | 五級升級階梯     |
| [docs/ADVANCED_FEATURES_SUMMARY.md](./docs/ADVANCED_FEATURES_SUMMARY.md)                   | 進階功能摘要      | 功能總覽         |
| [docs/INTELLIGENT_AUTOMATION_INTEGRATION.md](./docs/INTELLIGENT_AUTOMATION_INTEGRATION.md) | 智能自動化整合    | 整合說明         |
| [docs/MATECHAT_INTEGRATION_SUMMARY.md](./docs/MATECHAT_INTEGRATION_SUMMARY.md)             | MateChat 整合摘要 | 整合結果         |
| [docs/SYSTEM_BRIDGING_ASSESSMENT.md](./docs/SYSTEM_BRIDGING_ASSESSMENT.md)                 | 系統橋接評估      | 評估報告         |
| [docs/DEPLOYMENT_ASSESSMENT.md](./docs/DEPLOYMENT_ASSESSMENT.md)                           | 部署評估          | 部署評估         |
| [docs/TIER1_CONTRACTS_L1_DEPLOYMENT_PLAN.md](./docs/TIER1_CONTRACTS_L1_DEPLOYMENT_PLAN.md) | L1 部署計劃       | 部署計劃         |
| [docs/CODESPACE_SETUP.md](./docs/CODESPACE_SETUP.md)                                       | Codespace 設置    | GitHub Codespace |

### 中文文檔

| 文件路徑                                                                           | 說明                 | 操作指引 |
| ---------------------------------------------------------------------------------- | -------------------- | -------- |
| [docs/production-deployment-guide.zh.md](./docs/production-deployment-guide.zh.md) | 生產部署指南（中文） | 生產部署 |
| [docs/deep-integration-guide.zh.md](./docs/deep-integration-guide.zh.md)           | 深度整合指南（中文） | 深度整合 |
| [docs/runbook.zh.md](./docs/runbook.zh.md)                                         | 運維手冊（中文）     | 運維指南 |

### 報告文檔 (`docs/reports/`)

| 文件路徑                                                                                                     | 說明             | 操作指引 |
| ------------------------------------------------------------------------------------------------------------ | ---------------- | -------- |
| [docs/reports/COMPREHENSIVE_IMPLEMENTATION_REPORT.md](./docs/reports/COMPREHENSIVE_IMPLEMENTATION_REPORT.md) | 綜合實施報告     | 完整報告 |
| [docs/reports/PHASE1_IMPLEMENTATION_SUMMARY.md](./docs/reports/PHASE1_IMPLEMENTATION_SUMMARY.md)             | Phase 1 實施摘要 | 第一階段 |
| [docs/reports/PHASE1_VALIDATION_REPORT.md](./docs/reports/PHASE1_VALIDATION_REPORT.md)                       | Phase 1 驗證報告 | 驗證結果 |

### 範例文檔 (`docs/examples/`)

| 文件路徑                                                                         | 說明     | 操作指引 |
| -------------------------------------------------------------------------------- | -------- | -------- |
| [docs/examples/README.md](./docs/examples/README.md)                             | 範例入口 | 範例總覽 |
| [docs/examples/configuration/README.md](./docs/examples/configuration/README.md) | 配置範例 | 配置說明 |

### 故障排除文檔 (`docs/troubleshooting/`)

| 文件路徑                                                                                               | 說明               | 操作指引         |
| ------------------------------------------------------------------------------------------------------ | ------------------ | ---------------- |
| [docs/troubleshooting/github-copilot-agent-fix.md](./docs/troubleshooting/github-copilot-agent-fix.md) | Copilot Agent 修復 | 問題修復         |
| [docs/troubleshooting/INDEX.md](./docs/troubleshooting/INDEX.md)                                       | 故障排除索引       | 對應信號→Runbook |

### 代理角色文檔 (`docs/agents/`)

| 文件路徑                                                             | 說明             | 操作指引       |
| -------------------------------------------------------------------- | ---------------- | -------------- |
| [docs/agents/CLOUD_AGENT_ROLE.md](./docs/agents/CLOUD_AGENT_ROLE.md) | 雲端代理角色指南 | 委派範圍與守則 |

### 配置文檔 (`config/`)

| 文件路徑                                                         | 說明          | 操作指引 |
| ---------------------------------------------------------------- | ------------- | -------- |
| [config/conftest/README.md](./config/conftest/README.md)         | Conftest 配置 | 策略配置 |
| [config/integrations/README.md](./config/integrations/README.md) | 整合配置      | 整合設置 |

### 運維工具文檔 (`ops/`)

| 文件路徑                                                                                     | 說明         | 操作指引          |
| -------------------------------------------------------------------------------------------- | ------------ | ----------------- |
| [ops/migration/README.md](./ops/migration/README.md)                                         | 遷移工具     | 遷移說明          |
| [ops/migration/templates/migration_report.md](./ops/migration/templates/migration_report.md) | 遷移報告模板 | 報告模板          |
| [ops/onboarding/pr-template.md](./ops/onboarding/pr-template.md)                             | PR 模板      | Pull Request 模板 |

### 舊版文檔 (`legacy/`)

| 文件路徑                                                                 | 說明             | 操作指引 |
| ------------------------------------------------------------------------ | ---------------- | -------- |
| [legacy/v1-python-drones/README.md](./legacy/v1-python-drones/README.md) | V1 Python 無人機 | 舊版說明 |
| [legacy/v2-multi-islands/README.md](./legacy/v2-multi-islands/README.md) | V2 多島嶼系統    | 舊版說明 |

### 其他

| 文件路徑                                                               | 說明           | 操作指引          |
| ---------------------------------------------------------------------- | -------------- | ----------------- |
| [shared/README.md](./shared/README.md)                                 | 共用資源       | 共用模組          |
| [tests/README.md](./tests/README.md)                                   | 測試說明       | 測試指南          |
| [.github/copilot-instructions.md](./.github/copilot-instructions.md)   | Copilot 指令   | AI 指令配置       |
| [.github/profile/README.md](./.github/profile/README.md)               | GitHub Profile | 組織說明          |
| [.github/PULL_REQUEST_TEMPLATE.md](./.github/PULL_REQUEST_TEMPLATE.md) | PR 模板        | Pull Request 模板 |

---

## 📖 詳細操作流程

以下提供常見操作的詳細步驟說明。

### 1. 專案環境設置

#### 1.1 基本環境需求

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

#### 1.2 完整安裝流程

```bash
# 步驟 1: 克隆倉庫
git clone https://github.com/SynergyMesh-admin/Unmanned-Island.git
cd unmanned-island

# 步驟 2: 安裝 Node.js 依賴
npm install

# 步驟 3: 驗證安裝
npm run lint
npm run test

# 步驟 4: 構建專案
npm run build
```

#### 1.3 使用 Dev Container

```bash
# 在 VS Code 中
1. 安裝 "Remote - Containers" 擴展
2. 按 F1 -> "Remote-Containers: Reopen in Container"
3. 等待容器構建完成
4. 開始開發
```

### 2. 核心服務啟動

#### 2.1 啟動合約管理服務 (L1)

```bash
# 步驟 1: 進入合約服務目錄
cd core/contract_service/contracts-L1/contracts

# 步驟 2: 安裝依賴
npm install

# 步驟 3: 構建服務
npm run build

# 步驟 4: 啟動服務
npm start

# 服務將在 http://localhost:3000 運行
```

#### 2.2 啟動 MCP 伺服器

```bash
# 步驟 1: 進入 MCP 服務目錄
cd services/mcp

# 步驟 2: 安裝依賴
npm install

# 步驟 3: 啟動服務
npm start
```

### 3. Admin Copilot CLI 使用

#### 3.1 安裝 CLI

```bash
# 步驟 1: 進入 CLI 目錄
cd tools/cli

# 步驟 2: 安裝依賴
npm install

# 步驟 3: 全局連結
npm link

# 步驟 4: 驗證安裝
admin-copilot --version
# 或使用簡短別名
smcli --version
```

#### 3.2 CLI 常用命令

```bash
# 開始互動式 AI 對話
admin-copilot chat

# 分析指定目錄的程式碼
admin-copilot analyze ./src

# 自動修復程式碼問題
admin-copilot fix --auto

# 解釋程式碼或概念
smcli explain "What is SLSA provenance?"

# 生成程式碼
admin-copilot generate "Create a REST API endpoint" --language typescript

# 程式碼最佳實踐審查
admin-copilot review ./src/controllers
```

#### 3.3 認證設置

```bash
# 方法 1: 裝置流程（推薦）
admin-copilot chat
/login
# 按照終端指示完成認證

# 方法 2: 個人存取令牌
export GITHUB_TOKEN=your_personal_access_token
```

### 4. Web 應用與 API 服務

#### 4.1 前端開發

```bash
# 步驟 1: 進入 Web 應用目錄
cd apps/web

# 步驟 2: 安裝依賴
npm install

# 步驟 3: 開發模式（熱重載）
npm run dev

# 步驟 4: 生產構建
npm run build
```

#### 4.2 後端 API 服務

```bash
# 步驟 1: 創建虛擬環境
cd apps/web
python3 -m venv venv

# 步驟 2: 啟用虛擬環境
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 步驟 3: 安裝 Python 依賴
pip install -r requirements.txt

# 步驟 4: 驗證安裝
python -c "import services.code_analyzer; print('OK')"
```

#### 4.3 運行測試

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

### 5. Docker 部署

#### 5.1 開發環境部署

```bash
# 啟動開發環境
docker-compose -f docker-compose.dev.yml up -d

# 查看日誌
docker-compose -f docker-compose.dev.yml logs -f

# 停止服務
docker-compose -f docker-compose.dev.yml down
```

#### 5.2 生產環境部署

```bash
# 啟動生產環境
docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f

# 停止服務
docker-compose down
```

#### 5.3 API 服務完整環境

```bash
cd apps/web

# 啟動完整環境（API + PostgreSQL + Redis + Prometheus + Grafana）
docker-compose -f docker-compose.api.yml up -d

# 訪問 API 文檔
open http://localhost:8000/api/docs

# 查看服務日誌
docker-compose -f docker-compose.api.yml logs -f code-analysis-api
```

### 6. Kubernetes 部署

#### 6.1 基本部署

```bash
# 應用 Kubernetes 配置
kubectl apply -f infrastructure/kubernetes/manifests/

# 查看部署狀態
kubectl get pods -n unmanned-island
kubectl get svc -n unmanned-island

# 查看日誌
kubectl logs -f deployment/contract-service -n unmanned-island
```

#### 6.2 Web 應用 K8s 部署

```bash
cd apps/web

# 應用部署配置
kubectl apply -f k8s/deployment-api.yaml
kubectl apply -f deploy/

# 查看部署狀態
kubectl get pods -n code-analysis
kubectl get svc -n code-analysis

# 擴展副本
kubectl scale deployment code-analysis-api --replicas=5 -n code-analysis
```

### 7. 治理工具使用

#### 7.1 驗證文檔索引

```bash
# 驗證 knowledge_index.yaml
python tools/docs/validate_index.py --verbose
```

#### 7.2 掃描倉庫生成索引

```bash
# 乾運行模式
python tools/docs/scan_repo_generate_index.py --dry-run

# 實際執行
python tools/docs/scan_repo_generate_index.py
```

#### 7.3 生成 SLSA 溯源

```bash
# 生成溯源證明
python tools/docs/provenance_injector.py --generate-provenance

# 生成軟體物料清單
python tools/docs/provenance_injector.py --generate-sbom
```

### 8. Auto-Fix Bot 使用

#### 8.1 初始化

```bash
# 進入專案目錄
cd your-project

# 初始化 Auto-Fix Bot
autofix init

# 這會創建 config/autofixrc.json 配置文件
```

#### 8.2 分析與修復

```bash
# 分析整個項目
autofix analyze

# 自動修復所有可修復的問題
autofix fix --auto

# 逐個確認修復
autofix fix --interactive

# 監控模式
autofix watch --auto-fix
```

#### 8.3 雲端委派

```bash
# 登錄雲端服務
autofix login

# 啟用雲端委派
autofix config set cloudDelegation.enabled true

# 使用雲端資源分析
autofix analyze --cloud
```

### 9. CI/CD 互動命令

#### 9.1 CI 客服互動

```bash
# 特定 CI 分析
@copilot analyze Core Services CI     # 深度分析
@copilot fix Core Services CI         # 自動修復建議
@copilot help Integration CI          # 查看文檔

# 全局命令
@copilot 幫我分析                      # 分析所有 CI
@copilot 環境檢查                      # 環境診斷
```

### 10. 故障排除

#### 10.1 常見問題

| 問題             | 解決方案                                                         |
| ---------------- | ---------------------------------------------------------------- |
| npm install 失敗 | 清除 node_modules 並重試: `rm -rf node_modules && npm install`   |
| Python 依賴衝突  | 使用虛擬環境: `python3 -m venv venv && source venv/bin/activate` |
| Docker 構建失敗  | 清除 Docker 緩存: `docker system prune -a`                       |
| K8s Pod 無法啟動 | 檢查日誌: `kubectl logs <pod-name> -n <namespace>`               |

#### 10.2 日誌查看

```bash
# 查看 Docker Compose 日誌
docker-compose logs -f [service-name]

# 查看 K8s Pod 日誌
kubectl logs -f deployment/<deployment-name> -n <namespace>

# 查看系統日誌
journalctl -u <service-name> -f
```

---

## 📊 文檔統計

> **備註**: 以下統計表為本索引**手動維護**的主要文檔數量快照（已分類整理）。  
> 完整的機器掃描發現倉庫中共有 **426 個 `.md` 文件**（包含子模組、模板、範例等）。  
> 執行 `find . -name "*.md" -type f | wc -l` 可取得最新完整數量。  
> **最新掃描**: 2025-12-06

| 類別             | 數量（手動索引） |
| ---------------- | ---------------- |
| 專案根目錄文檔   | 6                |
| 架構設計文檔     | 14               |
| 自動化系統文檔   | 28               |
| 核心平台文檔     | 15               |
| CI/CD 與運維文檔 | 23               |
| 安全與治理文檔   | 11               |
| 服務與代理文檔   | 8                |
| 應用程式文檔     | 2                |
| 開發環境文檔     | 12               |
| 基礎設施文檔     | 3                |
| 工具與腳本文檔   | 2                |
| 其他文檔         | 52               |
| **手動索引小計** | **約 176**       |
| **完整掃描總計** | **426**          |

> **自動生成索引**: 完整的機器可讀索引請參考 [docs/generated-index.yaml](./docs/generated-index.yaml)（426 個文件）

---

## 🔗 相關資源

- [主要 README](./README.md) - 專案概覽
- [貢獻指南](./CONTRIBUTING.md) - 如何貢獻
- [安全政策](./SECURITY.md) - 安全實踐
- [知識索引](./docs/knowledge_index.yaml) - 機器可讀索引（手動維護）
- [生成索引](./docs/generated-index.yaml) - 自動掃描生成的完整索引
- [知識圖譜](./docs/knowledge-graph.yaml) - 倉庫結構知識圖譜
- [SuperRoot 實體](./docs/superroot-entities.yaml) - SuperRoot 格式實體投射

---

**文件版本**: 1.1.0  
**最後更新**: 2025-12-06  
**維護者**: SynergyMesh Development Team  
**自動化索引**: 請參考 [docs/knowledge_index.yaml](./docs/knowledge_index.yaml) 或 [docs/generated-index.yaml](./docs/generated-index.yaml)
獲取機器可讀的最新索引
