# Core Platform Services

# 核心平台服務

> 平台核心能力層，提供 AI 引擎、決策系統、安全機制和整合服務。
> Platform core capabilities layer, providing AI engines, decision systems, safety mechanisms, and integration services.

## 📋 Overview 概述

本目錄包含 SynergyMesh 平台的核心服務和能力。這些是平台級的共用服務，被其他模組（如 `agent/`、`automation/`）調用。

This directory contains core services and capabilities for the SynergyMesh platform. These are platform-level shared services that are called by other modules such as `agent/` and `automation/`.

## 📁 Directory Structure 目錄結構

```
core/
├── ai_constitution/           # AI 憲法和倫理規則
├── ai_decision_engine.py      # AI 決策引擎
├── advisory-database/         # 安全諮詢數據庫
├── auto_bug_detector.py       # 自動錯誤檢測
├── auto_governance_hub.py     # 自動化治理中心
├── autonomous_trust_engine.py # 信任管理引擎
├── ci_error_handler/          # CI 錯誤處理
├── cloud_agent_delegation/    # 雲端代理任務委派
├── context_understanding_engine.py # 上下文理解引擎
├── contract_service/          # 合約管理服務（L1）
├── execution_architecture/    # 執行架構定義
├── execution_engine/          # 代碼執行引擎
├── hallucination_detector.py  # AI 幻覺檢測
├── main_system/               # 主系統核心
├── mcp_servers_enhanced/      # 增強型 MCP 服務器
├── monitoring_system/         # 系統監控
├── safety_mechanisms/         # 安全機制
├── slsa_provenance/           # SLSA 溯源支持
├── tech_stack/                # 技術棧定義
├── training_system/           # AI 訓練系統
├── unified_integration/       # 統一整合層
├── virtual_experts/           # 虛擬專家系統
└── yaml_module_system/        # 基於 YAML 的模組系統
```

## 🎯 What This Directory Does 本目錄負責什麼

### ✅ Responsibilities 職責

1. **AI Capabilities AI 能力**
   - `ai_decision_engine.py` - 平台級 AI 決策引擎
   - `context_understanding_engine.py` - 上下文理解和分析
   - `hallucination_detector.py` - AI 輸出幻覺檢測
   - `virtual_experts/` - 虛擬領域專家系統
   - `training_system/` - AI 模型訓練和優化

2. **Governance & Trust 治理與信任**
   - `ai_constitution/` - AI 行為憲法和倫理規則
   - `auto_governance_hub.py` - 自動化治理中心
   - `autonomous_trust_engine.py` - 信任評分和管理

3. **Execution 執行**
   - `execution_engine/` - 代碼執行邏輯抽象
   - `execution_architecture/` - 執行拓撲和設計定義

4. **Safety & Security 安全**
   - `safety_mechanisms/` - 安全機制實作
   - `slsa_provenance/` - SLSA 供應鏈安全
   - `advisory-database/` - 安全諮詢和漏洞資料庫

5. **Integration 整合**
   - `unified_integration/` - 統一系統整合層
   - `contract_service/` - 合約管理微服務（L1）
   - `cloud_agent_delegation/` - 雲端代理任務委派

### ❌ What This Directory Does NOT Do 本目錄不負責什麼

- **不提供 LLM 工具端點** - 使用 `mcp-servers/`
- **不實作業務代理** - 使用 `agent/`
- **不組合產品級 pipeline** - 使用 `automation/intelligent/`
- **不定義外部 API 合約** - 合約定義在根目錄 `contracts/`
- **不處理 CI/CD 工作流** - 使用 `.github/workflows/`

## 🔗 Dependencies 依賴關係

### ✅ Allowed Dependencies 允許的依賴

| Dependency 依賴 | Purpose 用途 |
|----------------|--------------|
| `shared/` | 共用工具和配置 |
| `runtime/` | 運行時環境 |
| `config/` | 配置文件 |
| `governance/` | 治理規則（僅讀取） |

### ❌ Prohibited Dependencies 禁止的依賴

| Should NOT depend on 不應依賴 | Reason 原因 |
|------------------------------|-------------|
| `automation/` | 避免循環依賴，automation 應調用 core |
| `agent/` | 避免循環依賴，agent 應調用 core |
| `mcp-servers/` | core 是被調用方，不應反向依賴 |
| `frontend/` | 核心服務不應依賴 UI |

## 📦 Key Modules 關鍵模組

### AI Decision Engine AI 決策引擎

```python
from core.ai_decision_engine import AIDecisionEngine

engine = AIDecisionEngine()
decision = await engine.make_decision(
    context=analysis_context,
    options=available_actions,
    constraints=safety_constraints
)
```

### Context Understanding 上下文理解

```python
from core.context_understanding_engine import ContextEngine

context_engine = ContextEngine()
understanding = await context_engine.analyze(
    input_text=user_query,
    domain='code_analysis',
    history=conversation_history
)
```

### Execution Engine 執行引擎

```python
from core.execution_engine import ExecutionEngine

executor = ExecutionEngine()
result = await executor.execute(
    action=validated_action,
    sandbox=True,
    timeout=30
)
```

## 🔧 contract_service/ vs contracts/

**重要區分 Important Distinction:**

| 目錄 Directory | 內容 Content | 說明 Description |
|----------------|--------------|------------------|
| `core/contract_service/` | 微服務程式碼 | 合約管理服務的實作代碼 |
| `contracts/` (根目錄) | 合約定義資料 | 外部 API 合約規格 (OpenAPI, JSON Schema) |

---

## 📖 Related Documentation 相關文檔

- [Architecture Layers](../docs/architecture/layers.md) - 架構分層視圖
- [Repository Map](../docs/architecture/repo-map.md) - 倉庫語義邊界
- [Execution Architecture](./execution_architecture/) - 執行架構詳細設計
- [Safety Mechanisms](./safety_mechanisms/) - 安全機制文檔

## 📝 Document History 文檔歷史

| Date 日期 | Version 版本 | Changes 變更 |
|-----------|-------------|--------------|
| 2025-11-30 | 1.0.0 | Initial README with boundary definitions |

---

**Owner 負責人**: Core Platform Team  
**Last Updated 最後更新**: 2025-11-30
