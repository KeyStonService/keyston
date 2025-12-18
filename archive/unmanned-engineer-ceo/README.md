# 無人之島工程師 CEO / Unmanned Engineer CEO

## 願景 Vision

- 建立一套可複製的「虛擬工程師總執行長」能力模型，涵蓋技術、治理、智能與特質層。
- 讓 SynergyMesh + Structural Governance + Autonomous Framework 擁有統一的工程領導知識底座。
- 提供人/機皆可讀的資產，支援訓練、評估、派工與活體知識庫建模。

## 子系統分層 Layering
<<<<<<< HEAD
<<<<<<< HEAD

| 層級   | 目錄                          | 描述                                                                        |
| ------ | ----------------------------- | --------------------------------------------------------------------------- |
| 00     | 00-foundation                 | 核心計算機科學能力，對應 core/\* 核心模組設計規範。                         |
| 01     | 01-advanced-engineering       | 軟體工程深水區，映射 contract_service、automation/\*。                      |
| 02     | 02-enterprise-capabilities    | DevOps / 安全 / 觀測 / 效能，全程接軌 config/_與 infra/_。                  |
| 03     | 03-intelligence               | AI/ML/知識圖，支援 core/mind_matrix 與 docs/knowledge-\*。                  |
| 04     | 04-systems-thinking           | 系統思維與組織設計，連動 governance/ 與 services/agents。                   |
| 10     | 10-traits-matrix              | 認知與特質維度，使人才建模與行為觀測一致。                                  |
| 20     | 20-roadmap                    | 能力養成路線，供 HRD/主管在 org-playbook 中導入。                           |
| 30     | 30-assessment                 | 結構化評估矩陣，輸出 YAML 以供 pipelines/knowledge-base 使用。              |
| 40     | 40-simulations                | 模擬與演練腳本，對應 incident game day 與系統設計挑戰。                     |
| 50     | 50-org-implementation         | 組織導入指南，對齊 AI 憲法與治理策略。                                      |
| **60** | **60-machine-guides**         | **虛擬專家與機器導引**，支援 agents 的知識查詢與決策。                      |
| **70** | **70-architecture-skeletons** | **架構骨架原型**，展示系統各子系統的設計模式。                              |
| **80** | **80-skeleton-configs**       | **骨架配置完整實現** ✨ NEW，包含架構穩定性、安全可觀測性等實際配置和工具。 |
| 99     | 99-meta                       | 與活體知識庫/Schema Index 對接的映射層。                                    |
=======
=======

>>>>>>> origin/copilot/sub-pr-402
| 層級 | 目錄 | 描述 |
| ---- | ---- | ---- |
| 00 | 00-foundation | 核心計算機科學能力，對應 core/* 核心模組設計規範。 |
| 01 | 01-advanced-engineering | 軟體工程深水區，映射 contract_service、automation/*。 |
| 02 | 02-enterprise-capabilities | DevOps / 安全 / 觀測 / 效能，全程接軌 config/*與 infra/*。 |
| 03 | 03-intelligence | AI/ML/知識圖，支援 core/mind_matrix 與 docs/knowledge-*。 |
| 04 | 04-systems-thinking | 系統思維與組織設計，連動 governance/ 與 services/agents。 |
| 10 | 10-traits-matrix | 認知與特質維度，使人才建模與行為觀測一致。 |
| 20 | 20-roadmap | 能力養成路線，供 HRD/主管在 org-playbook 中導入。 |
| 30 | 30-assessment | 結構化評估矩陣，輸出 YAML 以供 pipelines/knowledge-base 使用。 |
| 40 | 40-simulations | 模擬與演練腳本，對應 incident game day 與系統設計挑戰。 |
| 50 | 50-org-implementation | 組織導入指南，對齊 AI 憲法與治理策略。 |
| **60** | **60-machine-guides** | **虛擬專家與機器導引**，支援 agents 的知識查詢與決策。 |
| **70** | **70-architecture-skeletons** | **架構骨架原型**，展示系統各子系統的設計模式。 |
| **80** | **80-skeleton-configs** | **骨架配置完整實現** ✨ NEW，包含架構穩定性、安全可觀測性等實際配置和工具。 |
| 99 | 99-meta | 與活體知識庫/Schema Index 對接的映射層。 |
<<<<<<< HEAD
>>>>>>> origin/alert-autofix-37
=======
>>>>>>> origin/copilot/sub-pr-402

## 使用方式 How To Use

1. **研發團隊**：依層級建立訓練計畫，透過 20-roadmap 與 30-assessment 評估成效。
2. **虛擬專家/代理**：Agents 可解析 manifest.yaml，自動定位對應知識模組與檔案。
3. **治理系統**：governance pipeline 可掃描 knowledge-index.yaml，將此資產併入 docs/knowledge-graph.yaml。
4. **自動化流程**：automation/self_awareness_report.py 可引用 skill/trait matrix 作為健康指標。
5. **骨架配置** (NEW)：
   - **架構驗證**：`80-skeleton-configs/01-architecture-stability/` 提供 Architecture Linter 驗證系統分層規則
   - **安全檢查**：`80-skeleton-configs/04-security-observability/` 包含 RBAC、日誌、追蹤配置與安全掃描工具
   - 詳見：[80-skeleton-configs README](./80-skeleton-configs/README.md)

## 維運原則 Operating Principles
<<<<<<< HEAD
<<<<<<< HEAD

- **Docs-first**：新增能力時先更新 manifest.yaml +
  README，並使用雙語（繁中+英文）標題以維持一致性。
- **Schema 對齊**：所有 YAML 項目應符合 governance/schemas 內既有結構（module,
  owner, lifecycle 等欄位）。
=======
- **Docs-first**：新增能力時先更新 manifest.yaml + README，並使用雙語（繁中+英文）標題以維持一致性。
- **Schema 對齊**：所有 YAML 項目應符合 governance/schemas 內既有結構（module, owner, lifecycle 等欄位）。
>>>>>>> origin/alert-autofix-37
=======

- **Docs-first**：新增能力時先更新 manifest.yaml + README，並使用雙語（繁中+英文）標題以維持一致性。
- **Schema 對齊**：所有 YAML 項目應符合 governance/schemas 內既有結構（module, owner, lifecycle 等欄位）。
>>>>>>> origin/copilot/sub-pr-402
- **可稽核**：重大改動需在 docs/KNOWLEDGE_HEALTH.md 加註版本，並於 manifest 中更新 revision 欄位。
- **活體循環**：每季透過 40-simulations 與 30-assessment 進行滾動式校準，輸出指標寫入 metrics-and-roi.md。

## Roadmap

- **Phase 1**：完成 00–02 層基礎檔案（本提交）。
- **Phase 2**：導入問卷/自評表單（30-assessment 子目錄）。
<<<<<<< HEAD
<<<<<<< HEAD
- **Phase 3**：結合 docs/generated-_與 agents/_ 執行自動指派。
=======
- **Phase 3**：結合 docs/generated-* 與 agents/* 執行自動指派。
>>>>>>> origin/alert-autofix-37
=======
- **Phase 3**：結合 docs/generated-*與 agents/* 執行自動指派。
>>>>>>> origin/copilot/sub-pr-402

## 維護 Maintainers

- Owner: SynergyMesh Architecture Guild
- Contact: <governance@unmanned.island>
- Alignment: config/system-manifest.yaml → module `engineer-ceo`
