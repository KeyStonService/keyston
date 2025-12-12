# Execution Engine

# 執行引擎

> 代碼執行邏輯抽象層，提供執行、驗證、回滾的統一介面。Code execution logic
> abstraction layer, providing unified interfaces for execution, verification,
> and rollback.

## 📋 Overview 概述

本目錄提供執行邏輯的抽象層，定義了 action 執行、capability 註冊、connector 管理和驗證引擎的標準介面。

This directory provides an abstraction layer for execution logic, defining
standard interfaces for action execution, capability registration, connector
management, and verification engine.

## 📁 Directory Structure 目錄結構

```
execution_engine/
├── __init__.py
├── action_executor.py      # Action 執行器
├── capability_registry.py  # 能力註冊表
├── connector_manager.py    # 連接器管理
├── execution_engine.py     # 主執行引擎
├── rollback_manager.py     # 回滾管理
└── verification_engine.py  # 驗證引擎
```

## 🎯 What This Directory Does 本目錄負責什麼

### ✅ Responsibilities 職責

1. **Action Execution 行動執行**
   - `action_executor.py` - 執行已驗證的 actions
   - 提供執行上下文管理
   - 處理執行結果

2. **Capability Registry 能力註冊**
   - `capability_registry.py` - 註冊和管理系統能力
   - 能力發現和查詢
   - 版本管理

3. **Connector Management 連接器管理**
   - `connector_manager.py` - 管理外部系統連接
   - 連接池管理
   - 連接健康檢查

4. **Verification 驗證**
   - `verification_engine.py` - 執行前驗證
   - 結果驗證
   - 安全性檢查

5. **Rollback 回滾**
   - `rollback_manager.py` - 執行失敗時的回滾邏輯
   - 狀態恢復
   - 補償操作

### ❌ What This Directory Does NOT Do 本目錄不負責什麼

- **不負責實際運行時啟動** - 使用 `runtime/`
- **不定義執行架構設計** - 使用 `core/execution_architecture/`
- **不實作具體業務邏輯** - 使用 `agent/` 或 `automation/`

## 🔗 Relationship with Related Components 與相關組件的關係

| 組件 Component                 | 關係 Relationship                                |
| ------------------------------ | ------------------------------------------------ |
| `core/execution_architecture/` | 架構設計層，定義 execution_engine 如何被編排     |
| `runtime/`                     | 運行時層，使用 execution_engine 的抽象來實際執行 |
| `agent/`                       | 業務代理，調用 execution_engine 來執行任務       |

## 📦 Key Interfaces 關鍵介面

### Execution Engine 執行引擎

```python
from core.execution_engine import ExecutionEngine

engine = ExecutionEngine()

# 執行 action
result = await engine.execute(
    action=validated_action,
    context=execution_context,
    sandbox=True
)
```

### Action Executor Action 執行器

```python
from core.execution_engine.action_executor import ActionExecutor

executor = ActionExecutor()
result = await executor.execute_action(
    action=action,
    params=params,
    timeout=30
)
```

### Verification Engine 驗證引擎

```python
from core.execution_engine.verification_engine import VerificationEngine

verifier = VerificationEngine()
is_valid = await verifier.verify(
    action=proposed_action,
    constraints=safety_constraints
)
```

## 🔗 Dependencies 依賴關係

### ✅ Allowed Dependencies 允許的依賴

| Dependency 依賴 | Purpose 用途   |
| --------------- | -------------- |
| `shared/`       | 共用工具和配置 |
| `config/`       | 執行配置       |

### ❌ Prohibited Dependencies 禁止的依賴

| Should NOT depend on 不應依賴 | Reason 原因              |
| ----------------------------- | ------------------------ |
| `runtime/`                    | 抽象層不應依賴具體運行時 |
| `agent/`                      | 抽象層不應依賴業務代理   |
| `automation/`                 | 抽象層不應依賴自動化模組 |

## 📖 Related Documentation 相關文檔

- [Architecture Layers](../../docs/architecture/layers.md) - 架構分層視圖
- [Repository Map](../../docs/architecture/repo-map.md) - 倉庫語義邊界
- [Runtime](../../runtime/README.md) - 運行時環境
- [Execution Architecture](../execution_architecture/README.md) - 執行架構

## 📝 Document History 文檔歷史

| Date 日期  | Version 版本 | Changes 變更                             |
| ---------- | ------------ | ---------------------------------------- |
| 2025-11-30 | 1.0.0        | Initial README with boundary definitions |

---

**Owner 負責人**: Core Platform Team  
**Last Updated 最後更新**: 2025-11-30
