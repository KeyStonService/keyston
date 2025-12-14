# Runtime Environment
# 運行時環境

> 實際運行時環境，承載 execution 的部署和啟動組件。
> Actual runtime environment, hosting execution deployment and startup components.

## 📋 Overview 概述

本目錄包含 SynergyMesh 平台的運行時組件，特別是 Mind Matrix runtime。這些組件負責實際的系統運行、部署啟動和運行時狀態管理。

This directory contains runtime components for the SynergyMesh platform, particularly the Mind Matrix runtime. These components handle actual system execution, deployment startup, and runtime state management.

## 📁 Directory Structure 目錄結構

```
runtime/
└── mind_matrix/
    ├── __init__.py
    ├── executive_auto.py    # 自動執行管理
    └── main.py              # 主入口點
```

## 🎯 What This Directory Does 本目錄負責什麼

### ✅ Responsibilities 職責

1. **Runtime Execution 運行時執行**
   - 實際部署時的啟動邏輯
   - 系統初始化和 bootstrap
   - 運行時狀態管理

2. **Mind Matrix Runtime**
   - 自動執行管理 (`executive_auto.py`)
   - 系統主入口點 (`main.py`)
   - 運行時協調

### ❌ What This Directory Does NOT Do 本目錄不負責什麼

- **不定義執行邏輯抽象** - 使用 `core/execution_engine/`
- **不定義執行架構** - 使用 `core/execution_architecture/`
- **不提供 AI 能力** - 使用 `core/` 中的 AI 引擎
- **不處理配置** - 配置在 `config/`

## 🔗 Relationship with core/execution_* 與 core/execution_* 的關係

```
┌─────────────────────────────────────────────────────────┐
│                   Architecture Level                     │
│                                                          │
│   core/execution_architecture/                           │
│   ├── 定義執行拓撲                                       │
│   ├── 定義 agent 編排設計                                │
│   └── 定義工具系統整合                                   │
│                                                          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Abstraction Level                      │
│                                                          │
│   core/execution_engine/                                 │
│   ├── 執行邏輯抽象                                       │
│   ├── Action executor                                    │
│   ├── Capability registry                                │
│   ├── Connector manager                                  │
│   └── Verification engine                                │
│                                                          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Runtime Level                          │
│                                                          │
│   runtime/                                               │
│   └── mind_matrix/                                       │
│       ├── 實際部署啟動                                   │
│       ├── 運行時狀態管理                                 │
│       └── System bootstrap                               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Summary 總結

| 組件 Component | 層級 Level | 職責 Responsibility |
|----------------|-----------|---------------------|
| `core/execution_architecture/` | 架構設計層 | 定義執行拓撲、agent 編排、工具系統 |
| `core/execution_engine/` | 抽象邏輯層 | 提供執行、驗證、回滾的抽象介面 |
| `runtime/` | 運行時環境層 | 實際部署、啟動、運行時狀態 |

## 🔗 Dependencies 依賴關係

### ✅ Allowed Dependencies 允許的依賴

| Dependency 依賴 | Purpose 用途 |
|----------------|--------------|
| `core/execution_engine/` | 使用執行邏輯抽象 |
| `core/execution_architecture/` | 讀取執行架構定義 |
| `shared/` | 共用工具和配置 |
| `config/` | 運行時配置 |

### ❌ Prohibited Dependencies 禁止的依賴

| Should NOT depend on 不應依賴 | Reason 原因 |
|------------------------------|-------------|
| `agent/` | 運行時不應直接依賴業務代理 |
| `automation/` | 運行時不應直接依賴自動化模組 |
| `frontend/` | 運行時不應依賴 UI |

## 🚀 Usage 使用方式

### Starting the Runtime 啟動運行時

```bash
cd runtime/mind_matrix
python main.py
```

### Integration Example 整合範例

```python
from runtime.mind_matrix import MindMatrix

# 初始化運行時
runtime = MindMatrix()
await runtime.initialize()

# 啟動系統
await runtime.start()

# 執行任務
result = await runtime.execute_task(task_definition)
```

## 📖 Related Documentation 相關文檔

- [Architecture Layers](../docs/architecture/layers.md) - 架構分層視圖
- [Repository Map](../docs/architecture/repo-map.md) - 倉庫語義邊界
- [Execution Engine](../core/execution_engine/) - 執行引擎
- [Execution Architecture](../core/execution_architecture/) - 執行架構

## 📝 Document History 文檔歷史

| Date 日期 | Version 版本 | Changes 變更 |
|-----------|-------------|--------------|
| 2025-11-30 | 1.0.0 | Initial README with boundary definitions |

---

**Owner 負責人**: Runtime Team  
**Last Updated 最後更新**: 2025-11-30
