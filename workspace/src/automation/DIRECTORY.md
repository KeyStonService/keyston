# automation

## 目錄職責

此目錄為 MachineNativeOps 的**自動化層**，包含智能自動化、建築分析、超自動化策略和架構骨架框架索引。作為系統的自動化能力核心，它與 `src/core/`（決策引擎）和 `src/autonomous/`（自主執行）緊密協作。

## 子目錄說明

### 建築分析系統

| 子目錄 | 職責 |
|--------|------|
| `architect/` | 建築分析與修復主系統 |
| `architect/core/` | 核心分析引擎 |
| `architect/config/` | 分析器配置 |
| `architect/docs/` | 架構分析文檔 |
| `architect/examples/` | 使用範例 |
| `architect/frameworks/` | 架構框架支持 |
| `architect/frameworks-popular/` | 主流框架分析 |
| `architect/scenarios/` | 分析場景 |
| `architect/tests/` | 測試套件 |

### 超自動化系統

| 子目錄 | 職責 |
|--------|------|
| `hyperautomation/` | 超自動化策略主系統 |
| `hyperautomation/contracts/` | 自動化合約定義 |
| `hyperautomation/docs/` | 超自動化文檔 |
| `hyperautomation/policies/` | 自動化策略 |
| `hyperautomation/templates/` | 工作流模板 |

### 其他

| 子目錄 | 職責 |
|--------|------|
| `architecture-skeletons/` | 11 骨架架構模式定義與索引（對應 src/autonomous/infrastructure 的 8 個已實現骨架） |
| `_scratch/` | 實驗性代碼 |

## 核心 Python 檔案說明

### self_awareness_report.py

- **職責**：系統自我感知報告生成器
- **功能**：
  - 從 docs/project-manifest.md 生成倉庫狀態摘要
  - 輸出系統健康狀態、元件狀態
  - 問題診斷與修復建議
- **依賴**：docs/, config/

### zero_touch_deployment.py

- **職責**：零接觸部署引擎
- **功能**：
  - 全自動化部署流程
  - 環境配置自動檢測
  - 部署驗證與回滾
- **依賴**：deploy/, config/environments/

## 架構骨架框架 (Architecture Skeletons Framework)

本層提供 11 個架構骨架的統一索引（位於 `architecture-skeletons/`），這些骨架按功能可歸類為五大核心維度：

| 核心維度 | 對應骨架 | 技術棧 |
|---------|---------|--------|
| 架構穩定性 | architecture-stability | C++ + ROS 2 (100Hz) |
| API 與測試治理 | api-governance, testing-governance, testing-compatibility | Python + YAML |
| 安全與可觀測性 | security-observability | Go + Python |
| 身份與資料治理 | identity-tenancy, data-governance | - |
| 編排與知識管理 | nucleus-orchestrator, knowledge-base, performance-reliability, cost-management | - |

**註**：11 個骨架的完整索引與映射見 `architecture-skeletons/unified-index.yaml`；8 個已實現的骨架代碼位於 `src/autonomous/infrastructure/`。

## 核心能力

1. **智能自動化**
   - 自動缺陷檢測和修復
   - 自動治理與合規
   - 幻覺檢測

2. **建築分析**
   - 代碼模式檢測
   - 複雜度分析
   - 重構建議

3. **超自動化**
   - 工作流編排
   - RPA 協調
   - 流程挖掘

## 設計原則

1. **分層自動化**：從簡單腳本到智能決策，分層實現
2. **可組合性**：各自動化模組可獨立運行或組合使用
3. **安全優先**：所有自動化操作需通過安全檢查
4. **可審計性**：完整記錄自動化決策和執行過程

## 與其他目錄的關係

- **src/core/**：調用 AI 決策引擎進行智能決策
- **src/autonomous/**：提供自主執行能力
- **src/services/agents/**：與智能代理協作
- **config/**：讀取自動化配置
- **deploy/**：執行部署自動化
