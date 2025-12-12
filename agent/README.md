# Agent Services

# 代理服務

> 長生命週期業務代理，負責自動化任務執行和系統協調。Long-lifecycle business
> agents for automated task execution and system orchestration.

## 📋 Overview 概述

本目錄包含 SynergyMesh 平台的智能業務代理。這些代理是獨立運行的服務，負責執行特定的自動化任務，如代碼修復、安全掃描和任務編排。

This directory contains intelligent business agents for the SynergyMesh
platform. These agents are independent services that handle specific automation
tasks such as code repair, security scanning, and task orchestration.

## 📁 Directory Structure 目錄結構

```
agent/
├── auto-repair/           # 自動修復代理 - Auto-repair agent
├── code-analyzer/         # 代碼分析代理 - Code analysis agent
├── dependency-manager/    # 依賴管理代理 - Dependency management agent
├── orchestrator/          # 代理編排器 - Agent orchestrator
├── vulnerability-detector/# 漏洞檢測代理 - Vulnerability detection agent
└── runbook-executor.sh    # 運維手冊執行腳本 - Runbook executor script
```

## 🎯 What This Directory Does 本目錄負責什麼

### ✅ Responsibilities 職責

1. **Auto-Repair Agent** (`auto-repair/`)
   - 自動檢測和修復代碼問題
   - 依據預定義規則執行修復
   - 追蹤修復歷史和結果

2. **Code Analyzer Agent** (`code-analyzer/`)
   - 深度代碼品質分析
   - 複雜度和可維護性評估
   - 安全關鍵路徑識別

3. **Dependency Manager** (`dependency-manager/`)
   - 依賴版本管理和更新
   - 漏洞依賴檢測
   - 依賴升級建議

4. **Orchestrator** (`orchestrator/`)
   - 多代理任務協調
   - 工作流編排和調度
   - 代理間通訊管理

5. **Vulnerability Detector** (`vulnerability-detector/`)
   - 安全漏洞主動檢測
   - CVE 資料庫比對
   - 安全報告生成

### ❌ What This Directory Does NOT Do 本目錄不負責什麼

- **不提供 LLM 工具端點** - 使用 `mcp-servers/` 中的 MCP 服務器
- **不實作平台級 AI 能力** - 使用 `core/` 中的 AI 引擎
- **不組合產品級 pipeline** - 使用 `automation/intelligent/` 中的 pipeline
- **不定義 API 合約** - 合約定義在 `contracts/`

## 🔗 Dependencies 依賴關係

### ✅ Allowed Dependencies 允許的依賴

| Dependency 依賴 | Purpose 用途                             |
| --------------- | ---------------------------------------- |
| `core/`         | 使用平台級 AI 決策引擎、上下文理解等能力 |
| `mcp-servers/`  | 調用 LLM 工具端點進行分析                |
| `shared/`       | 使用共用工具和配置                       |
| `config/`       | 讀取代理配置                             |

### ❌ Prohibited Dependencies 禁止的依賴

| Should NOT depend on 不應依賴 | Reason 原因                               |
| ----------------------------- | ----------------------------------------- |
| `automation/intelligent/`     | 避免循環依賴，pipeline 應調用代理而非相反 |
| `frontend/`                   | 代理不應直接依賴 UI                       |
| `infrastructure/`             | 代理邏輯不應依賴部署配置                  |

## 🚀 Usage 使用方式

### Running an Agent 執行代理

```bash
# 執行自動修復代理
cd agent/auto-repair
./run.sh

# 執行 runbook
cd agent
./runbook-executor.sh <runbook-name>
```

### Integration with Orchestrator 與編排器整合

```python
from agent.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()
orchestrator.register_agent('auto-repair')
orchestrator.register_agent('vulnerability-detector')

# 執行協調任務
result = await orchestrator.execute_workflow('security-scan-and-fix')
```

## 🔧 Development 開發

### Adding a New Agent 新增代理

1. 在 `agent/` 下創建新目錄
2. 實作標準代理介面
3. 在 `orchestrator/` 中註冊
4. 更新本 README

### Agent Interface 代理介面

所有代理應實作以下介面：

```python
class BaseAgent:
    async def initialize(self) -> None:
        """初始化代理"""
        pass

    async def execute(self, task: Task) -> Result:
        """執行任務"""
        pass

    async def health_check(self) -> HealthStatus:
        """健康檢查"""
        pass
```

## 📖 Related Documentation 相關文檔

- [Architecture Layers](../docs/architecture/layers.md) - 架構分層視圖
- [Repository Map](../docs/architecture/repo-map.md) - 倉庫語義邊界
- [MCP Servers](../mcp-servers/README.md) - LLM 工具端點
- [Core Services](../core/README.md) - 平台核心服務

## 📝 Document History 文檔歷史

| Date 日期  | Version 版本 | Changes 變更                             |
| ---------- | ------------ | ---------------------------------------- |
| 2025-11-30 | 1.0.0        | Initial README with boundary definitions |

---

**Owner 負責人**: Agent Team  
**Last Updated 最後更新**: 2025-11-30
