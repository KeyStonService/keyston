# Agent Examples

# 代理使用範例

> 提供清晰的使用範例，降低新開發者的學習障礙。
> Provides clear usage examples to reduce the learning barrier for new developers.

## 📋 Overview 概述

本目錄包含代理系統的使用範例，展示如何使用和整合各個代理組件。這些範例作為即時文件，幫助新成員快速上手並理解系統功能。

This directory contains usage examples for the agent system, demonstrating how to use and integrate various agent components. These examples serve as living documentation to help new members quickly get started and understand system capabilities.

## 📁 Directory Structure 目錄結構

```
examples/
├── basic/                     # 基礎範例 - Basic examples
│   ├── basic_usage.py        # 基礎使用方式 - Basic usage
│   └── hello_agent.py        # 最簡範例 - Minimal example
├── integration/               # 整合範例 - Integration examples
│   ├── multi_agent_workflow.py# 多代理工作流 - Multi-agent workflow
│   └── orchestrator_demo.py  # 編排器演示 - Orchestrator demo
├── advanced/                  # 進階範例 - Advanced examples
│   ├── custom_agent.py       # 自定義代理 - Custom agent implementation
│   └── streaming_analysis.py # 串流分析 - Streaming analysis
└── notebooks/                 # Jupyter 筆記本 - Jupyter notebooks
    └── agent_tutorial.ipynb  # 代理教程 - Agent tutorial
```

## 🚀 Quick Start 快速開始

### Basic Usage 基礎使用

```python
"""
basic_usage.py - 展示代理基本使用方式
Demonstrates basic agent usage patterns.

Note: Import paths assume the agent package is installed.
See Prerequisites section for installation instructions.
"""

from agent.orchestrator import AgentOrchestrator
from agent.code_analyzer import CodeAnalyzer

# 初始化編排器
orchestrator = AgentOrchestrator()

# 註冊代理 (提供代理名稱和實例)
orchestrator.register_agent('code-analyzer', CodeAnalyzer())

# 執行簡單任務
result = await orchestrator.execute_task(
    agent='code-analyzer',
    task='analyze',
    params={'file_path': 'src/main.py'}
)

print(f"Analysis complete: {result.summary}")
```

### Multi-Agent Workflow 多代理工作流

```python
"""
multi_agent_workflow.py - 展示多代理協作
Demonstrates multi-agent collaboration patterns.
"""

from agent.orchestrator import AgentOrchestrator

# 初始化編排器
orchestrator = AgentOrchestrator()

# 註冊多個代理 (使用代理名稱，編排器會自動創建實例)
# 也可以傳入實例: orchestrator.register_agent('code-analyzer', CodeAnalyzer())
orchestrator.register_agent('code-analyzer')
orchestrator.register_agent('vulnerability-detector')
orchestrator.register_agent('auto-repair')

# 定義工作流
workflow = {
    'name': 'security-scan-and-fix',
    'steps': [
        {'agent': 'code-analyzer', 'action': 'analyze'},
        {'agent': 'vulnerability-detector', 'action': 'scan'},
        {'agent': 'auto-repair', 'action': 'fix', 'condition': 'issues_found'}
    ]
}

# 執行工作流
result = await orchestrator.execute_workflow(workflow)
print(f"Workflow complete: {result.status}")
```

## 📂 Example Categories 範例分類

### 1. Basic Examples 基礎範例

入門級範例，適合剛接觸代理系統的開發者。

| File | Description |
|------|-------------|
| `basic/hello_agent.py` | 最簡單的代理調用範例 |
| `basic/basic_usage.py` | 基礎使用模式 |
| `basic/configuration.py` | 配置代理參數 |

### 2. Integration Examples 整合範例

展示如何將多個代理組合使用。

| File | Description |
|------|-------------|
| `integration/multi_agent_workflow.py` | 多代理工作流協作 |
| `integration/orchestrator_demo.py` | 編排器完整演示 |
| `integration/event_driven.py` | 事件驅動的代理協作 |

### 3. Advanced Examples 進階範例

複雜場景和自定義實現範例。

| File | Description |
|------|-------------|
| `advanced/custom_agent.py` | 實現自定義代理 |
| `advanced/streaming_analysis.py` | 串流式代碼分析 |
| `advanced/ml_integration.py` | 機器學習整合 |

## 🔧 Running Examples 執行範例

### Prerequisites 前置條件

```bash
# 確保已安裝依賴
pip install -r requirements.txt

# 或使用專案根目錄的安裝方式
cd /path/to/project
pip install -e .
```

### Run a Single Example 執行單個範例

```bash
# 執行基礎範例
python examples/basic/basic_usage.py

# 執行整合範例
python examples/integration/multi_agent_workflow.py
```

### Run All Examples 執行所有範例

```bash
# 執行所有範例（用於驗證）
python -m pytest examples/ --doctest-modules
```

## 📝 Contributing Examples 貢獻範例

### Guidelines 準則

1. **Self-contained**: 範例應該是獨立的，不依賴外部狀態
2. **Well-documented**: 每個範例必須包含詳細的註釋和文檔字串
3. **Runnable**: 範例必須可以直接執行
4. **Error-handled**: 包含適當的錯誤處理

### Example Template 範例模板

```python
#!/usr/bin/env python3
"""
Example: <example_name>
Description: <brief description>

This example demonstrates:
- Point 1
- Point 2

Usage:
    python examples/<category>/<example_name>.py

Requirements:
    - Python 3.10+
    - agent package installed
"""

import asyncio
from agent import AgentOrchestrator

async def main():
    """Main entry point for the example."""
    # Your example code here
    pass

if __name__ == "__main__":
    asyncio.run(main())
```

## 📖 Related Documentation 相關文檔

- [Agent README](../README.md) - 代理服務總覽
- [Code Analyzer](../code-analyzer/README.md) - 代碼分析代理
- [Orchestrator](../orchestrator/README.md) - 編排器代理
- [API Reference](../../docs/API.md) - API 參考

---

**Owner 負責人**: Agent Team  
**Last Updated 最後更新**: 2025-12-15
