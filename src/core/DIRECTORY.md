# core

## 目錄職責

此目錄為 MachineNativeOps 的**核心引擎**，包含 AI 決策、契約管理、編排器、Phase 4 智能自動化等關鍵系統。

## 子目錄分類

### 智能決策系統

| 子目錄 | 職責 |
|--------|------|
| `ai_constitution/` | AI 憲法與行為約束規則 |
| `virtual_experts/` | 虛擬專家系統 |
| `training_system/` | 訓練系統 |

### 編排與執行

| 子目錄 | 職責 |
|--------|------|
| `orchestrators/` | 編排器（SynergyMesh、語言島嶼、企業級） |
| `instant_generation/` | 即時代碼生成引擎 |
| `project_factory/` | 專案工廠（一鍵生成） |
| `engine/` | 核心執行引擎 |

### Phase 4 系統

| 子目錄 | 職責 |
|--------|------|
| `phase4/` | Phase 4 智能自動化（多語言、移動端、SaaS、計費） |

### 契約與治理

| 子目錄 | 職責 |
|--------|------|
| `contract_service/` | 契約服務 |
| `contracts/` | 契約定義 |
| `validators/` | 驗證器 |
| `slsa_provenance/` | SLSA 溯源與簽名 |

### 監控與安全

| 子目錄 | 職責 |
|--------|------|
| `monitoring/` | 監控系統 |
| `safety/` | 安全機制 |
| `ci_error_handler/` | CI 錯誤處理 |
| `advisory-database/` | 安全公告資料庫 |

### 其他

| 子目錄 | 職責 |
|--------|------|
| `new/` | 新核心模組（core, db, jobs 等） |
| `plugins/` | 插件系統 |
| `integrations/` | 整合模組 |
| `island_ai_runtime/` | Island AI 運行時 |
| `cloud_agent_delegation/` | 雲端代理委派 |
| `main_system/` | 主系統 |
| `tech_stack/` | 技術棧定義 |
| `yaml_module_system/` | YAML 模組系統 |
| `run-debug/` | 調試工具 |
| `_scratch/` | 臨時/實驗代碼 |

## 核心 Python 文件說明

### ai_decision_engine.py
- **職責**：AI 決策引擎（Phase 3）
- **功能**：智能決策、預測分析、多準則優化、自主策略選擇
- **決策類型**：Strategic, Tactical, Operational, Reactive, Predictive

### contract_engine.py
- **職責**：SynergyMesh 核心契約引擎
- **功能**：契約註冊、驗證、執行、生命週期管理、版本控制

### context_understanding_engine.py
- **職責**：上下文理解引擎（Phase 5）
- **功能**：深層上下文分析、業務邏輯推理、歷史記憶、多維度需求解析

### auto_bug_detector.py
- **職責**：自動錯誤檢測與修復器（Phase 5）
- **功能**：智能錯誤檢測、根因分析、自動修復、持續學習

### auto_governance_hub.py
- **職責**：自動治理中心
- **功能**：治理規則自動執行與監控

### plugin_system.py
- **職責**：SynergyMesh 插件系統
- **功能**：插件載入、註冊、生命週期管理

### config.py / exceptions.py / main.py
- **職責**：基礎設施文件
- **功能**：配置載入、異常定義、主入口（目前為空文件）

## 設計原則

1. **AI 驅動**：核心決策由 AI 引擎驅動，基於歷史數據進行預測
2. **契約優先**：所有操作通過契約定義和驗證
3. **可插拔架構**：功能通過插件系統擴展

## 與其他目錄的關係

- **src/autonomous/**：使用 core 的編排器和決策引擎
- **src/services/**：調用 core 的業務邏輯
- **config/**：提供配置參數
- **tests/**：對應的測試代碼
