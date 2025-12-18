# API 規格與治理邊界骨架 (API Specification & Governance Boundary Skeleton)

## 概述

Python 模組治理層，定義模組責任矩陣、API 邊界、錯誤分類，提供自動化驗證。

## 功能特性

- ✅ **模組責任矩陣**：清晰定義每個模組的責任範圍
- ✅ **API 契約驗證**：強制輸入/輸出 schema 驗證
- ✅ **依賴鏈檢測**：自動檢測循環依賴
- ✅ **治理報告生成**：生成自動化治理報告
- ✅ **錯誤分類**：系統化的錯誤處理策略

## 系統需求

- Python >= 3.8

## 安裝

```bash
pip install -r requirements.txt
```

## 使用範例

### 基本使用

```python
from api_contract import GovernanceValidator

# 創建驗證器
validator = GovernanceValidator()

# 驗證 API 調用
validator.validate_api_call("flight_controller", {
    "target_altitude": 10.0,
    "target_velocity": [1.0, 2.0, 3.0]
})

# 驗證依賴鏈
validator.validate_dependency_chain("flight_controller")

# 生成治理報告
report = validator.generate_governance_report()
print(report)
```

### 運行示例

```bash
python api_contract.py
```

### 預期輸出

```
✓ API call validated successfully
✓ Dependency chain validated

治理報告：
{
  "total_modules": 2,
  "modules": {
    "flight_controller": {
      "role": "flight_control",
      "max_latency_ms": 10.0,
      "dependencies": ["sensor_fusion", "safety_monitor"],
      "error_categories": ["sensor_error", "control_error"]
    },
    "safety_monitor": {
      "role": "safety_monitor",
      "max_latency_ms": 5.0,
      "dependencies": [],
      "error_categories": ["safety_violation"]
    }
  }
}
```

## 模組責任分類

| 模組角色 | 描述 | 最大延遲 |
|---------|------|---------|
| SENSOR_FUSION | 感測器資料融合 | 50ms |
| FLIGHT_CONTROL | 飛行控制 | 10ms |
| NAVIGATION | 導航規劃 | 100ms |
| SAFETY_MONITOR | 安全監控 | 5ms |
| OBSERVABILITY | 可觀測性 | 100ms |

## 錯誤分類

| 錯誤類型 | 處理策略 |
|---------|---------|
| SENSOR_ERROR | fallback_to_last_known_state |
| CONTROL_ERROR | emergency_landing |
| NAVIGATION_ERROR | replan_route |
| SAFETY_VIOLATION | trigger_emergency_protocol |
| SYSTEM_ERROR | graceful_shutdown |

## 整合至 SynergyMesh

此模組與 SynergyMesh 契約服務整合：

1. **API 治理**：提供 API 契約驗證能力
2. **依賴管理**：檢測模組間的依賴關係
3. **錯誤處理**：統一的錯誤分類和處理策略

## 參考資料

- [API Contract Design](https://martinfowler.com/articles/consumerDrivenContracts.html)
- [Dependency Management Best Practices](https://12factor.net/dependencies)
