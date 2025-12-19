# DependencyResolver API 文檔

## 目錄

1. [概述](#概述)
2. [核心方法](#核心方法)
3. [數據結構](#數據結構)
4. [使用示例](#使用示例)
5. [性能考量](#性能考量)

---

## 概述

`DependencyResolver` 是一個智能依賴解析引擎，能夠：

- **構建依賴圖**：管理組件之間的依賴關係
- **檢測循環依賴**：在運行前發現潛在問題
- **拓撲排序**：確定執行順序
- **並行化分析**：識別可並行執行的組件
- **性能優化**：提供優化建議

```python
from core.orchestrators import DependencyResolver

resolver = DependencyResolver()
```

---

## 核心方法

### `add_component(component_id, component_type, priority=0, weight=1.0) -> bool`

添加組件到依賴圖。

**參數：**
- `component_id` (str): 組件 ID（唯一標識符）
- `component_type` (str): 組件類型（如 "agent", "service", "task"）
- `priority` (int): 優先級（預設: 0，數字越大優先級越高）
- `weight` (float): 執行權重（用於性能估計，預設: 1.0）

**返回值：** bool（成功返回 True）

**示例：**
```python
# 添加數據庫組件
resolver.add_component("database", "service", priority=10, weight=0.5)

# 添加 API 服務
resolver.add_component("api_service", "service", priority=5, weight=1.0)

# 添加工作進程
resolver.add_component("worker", "task", priority=1, weight=2.0)
```

**最佳實踐：**
- 使用描述性的組件 ID（如 `user_service` 而非 `svc1`）
- 為關鍵服務設置更高的優先級
- 根據預期執行時間設置權重

---

### `add_dependency(from_component, to_component) -> bool`

添加依賴關係。

**參數：**
- `from_component` (str): 依賴者的組件 ID
- `to_component` (str): 被依賴的組件 ID

**語義：** `from_component` 依賴於 `to_component`（`from_component` 需要在 `to_component` 之後執行）

**返回值：** bool（成功返回 True，如果會創建循環則返回 False）

**示例：**
```python
# API 服務依賴於數據庫
resolver.add_dependency("api_service", "database")

# 工作進程依賴於 API 服務
resolver.add_dependency("worker", "api_service")

# 嘗試添加會創建循環的依賴（返回 False）
result = resolver.add_dependency("database", "api_service")
if not result:
    print("循環依賴被拒絕")
```

**循環依賴檢測：**
在添加依賴前，系統會自動檢測是否會創建循環：
```
依賴鏈: A → B → C → A
                   ^
                   |
              新的依賴，會形成循環
```

---

### `topological_sort(component_ids=None) -> List[str]`

執行拓撲排序。

**參數：**
- `component_ids` (List[str], optional): 要排序的組件列表。如果為 None，排序所有組件。

**返回值：** 排序後的組件 ID 列表

**示例：**
```python
# 排序所有組件
order = resolver.topological_sort()
print(f"執行順序: {' → '.join(order)}")

# 只排序特定組件
subset = resolver.topological_sort(["api_service", "worker", "database"])
```

**執行順序保證：**
- 依賴的組件在被依賴的組件之後
- 同級組件按優先級排序
- 算法複雜度: O(V + E)，其中 V 是組件數，E 是依賴數

---

### `get_execution_phases(component_ids=None) -> List[ExecutionPhase]`

獲取執行階段（識別可並行執行的組件）。

**參數：**
- `component_ids` (List[str], optional): 要分析的組件列表

**返回值：** `ExecutionPhase` 對象列表

**示例：**
```python
phases = resolver.get_execution_phases()

for phase in phases:
    print(f"\n階段 {phase.phase_number}:")
    print(f"  組件: {', '.join(phase.components)}")
    print(f"  可並行: {'是' if phase.can_parallel else '否'}")
    print(f"  估計時間: {phase.estimated_duration_ms:.0f}ms")
    print(f"  依賴數: {phase.dependency_count}")
```

**ExecutionPhase 屬性：**
- `phase_number`: 階段序號（從 1 開始）
- `components`: 該階段中的組件列表
- `can_parallel`: 該階段的組件是否可並行執行
- `estimated_duration_ms`: 估計執行時間（毫秒）
- `dependency_count`: 該階段的總依賴數

**並行化示例：**
```
階段 1: [database]              (1 個組件)
階段 2: [cache, auth]           (2 個並行)
階段 3: [api, user_service]     (2 個並行)
階段 4: [worker]                (1 個組件)

順序執行時間: 約 300ms
並行執行時間: 約 100ms
加速倍數: 3x
```

---

### `get_critical_path() -> List[str]`

獲取關鍵路徑（最長的執行路徑）。

**參數：** 無

**返回值：** 組件 ID 列表（按順序）

**示例：**
```python
critical = resolver.get_critical_path()
print(f"關鍵路徑: {' → '.join(critical)}")
print(f"路徑長度: {len(critical)} 個組件")
```

**用途：**
- 識別系統的瓶頸
- 優化重點（對關鍵路徑上的組件優化最有效）
- 性能預測

---

### `get_parallelization_analysis(component_ids=None) -> Dict`

獲取並行化分析結果。

**參數：**
- `component_ids` (List[str], optional): 要分析的組件列表

**返回值：** 包含以下鍵的字典：
- `total_components`: 總組件數
- `execution_phases`: 執行階段數
- `sequential_time_ms`: 順序執行的估計時間
- `parallel_time_ms`: 並行執行的估計時間
- `parallelization_factor`: 並行加速倍數
- `potential_speedup`: 格式化的加速倍數字符串

**示例：**
```python
analysis = resolver.get_parallelization_analysis()

print(f"組件總數: {analysis['total_components']}")
print(f"執行階段: {analysis['execution_phases']}")
print(f"順序執行: {analysis['sequential_time_ms']:.0f}ms")
print(f"並行執行: {analysis['parallel_time_ms']:.0f}ms")
print(f"加速倍數: {analysis['parallelization_factor']:.2f}x")
print(f"預期加速: {analysis['potential_speedup']}")
```

**輸出示例：**
```
組件總數: 20
執行階段: 5
順序執行: 2000ms
並行執行: 500ms
加速倍數: 4.00x
預期加速: 4.00x
```

---

### `get_optimization_recommendations() -> List[str]`

獲取優化建議。

**參數：** 無

**返回值：** 建議字符串列表

**示例：**
```python
recommendations = resolver.get_optimization_recommendations()

for rec in recommendations:
    print(f"💡 {rec}")
```

**可能的建議：**
- ⚠️ 依賴複雜性高，考慮重構以減少耦合
- 💡 低並行化機會，考慮優化依賴關係
- 🔗 依賴深度深，考慮引入中間層
- ✅ 依賴結構健康，無特別建議

---

### `get_dependency_stats() -> Dict`

獲取依賴圖統計信息。

**參數：** 無

**返回值：** 統計字典

**示例：**
```python
stats = resolver.get_dependency_stats()

print(f"總組件數: {stats['total_components']}")
print(f"總依賴數: {stats['total_dependencies']}")
print(f"平均依賴數: {stats['average_dependency_count']:.1f}")
print(f"最大深度: {stats['max_dependency_depth']}")
print(f"循環依賴: {stats['circular_dependencies']}")
```

---

### `export_graph() -> Dict`

導出依賴圖為 JSON 格式。

**參數：** 無

**返回值：** 包含節點、邊和統計的字典

**示例：**
```python
import json

graph_data = resolver.export_graph()

# 保存為 JSON
with open("dependency_graph.json", "w") as f:
    json.dump(graph_data, f, indent=2)

# 導出結構
print(f"節點數: {len(graph_data['nodes'])}")
print(f"邊數: {len(graph_data['edges'])}")
print(f"統計: {graph_data['statistics']}")
```

**導出格式：**
```json
{
  "nodes": [
    {"id": "database", "type": "service", "priority": 10, "weight": 0.5},
    {"id": "api", "type": "service", "priority": 5, "weight": 1.0}
  ],
  "edges": [
    {"from": "api", "to": "database"}
  ],
  "statistics": {...},
  "recommendations": [...]
}
```

---

## 數據結構

### DependencyNode

```python
@dataclass
class DependencyNode:
    component_id: str           # 組件 ID
    component_type: str         # 組件類型
    priority: int = 0           # 優先級
    weight: float = 1.0         # 執行權重
    dependencies: List[str]     # 依賴列表
    dependent_on: List[str]     # 被依賴列表
```

### ExecutionPhase

```python
@dataclass
class ExecutionPhase:
    phase_number: int           # 階段號
    components: List[str]       # 該階段的組件
    can_parallel: bool          # 是否可並行
    estimated_duration_ms: float # 估計耗時
    dependency_count: int       # 依賴計數
```

---

## 使用示例

### 微服務架構分析

```python
from core.orchestrators import DependencyResolver

resolver = DependencyResolver()

# 定義微服務
services = {
    "database": ("database", 1),
    "cache": ("cache", 2),
    "auth": ("auth", 3),
    "api_gateway": ("gateway", 4),
    "user_service": ("service", 2),
    "product_service": ("service", 2),
    "order_service": ("service", 2)
}

for service_id, (svc_type, priority) in services.items():
    resolver.add_component(service_id, svc_type, priority=priority)

# 定義依賴
dependencies = [
    ("cache", "database"),
    ("auth", "database"),
    ("user_service", "database"),
    ("user_service", "auth"),
    ("product_service", "database"),
    ("order_service", "user_service"),
    ("order_service", "product_service"),
    ("api_gateway", "auth"),
    ("api_gateway", "user_service"),
    ("api_gateway", "product_service"),
    ("api_gateway", "order_service")
]

for from_svc, to_svc in dependencies:
    resolver.add_dependency(from_svc, to_svc)

# 分析
print("=== 執行順序 ===")
order = resolver.topological_sort()
print(" → ".join(order))

print("\n=== 執行階段 ===")
phases = resolver.get_execution_phases()
for phase in phases:
    print(f"階段 {phase.phase_number}: {', '.join(phase.components)}")

print("\n=== 並行化分析 ===")
analysis = resolver.get_parallelization_analysis()
print(f"順序執行: {analysis['sequential_time_ms']:.0f}ms")
print(f"並行執行: {analysis['parallel_time_ms']:.0f}ms")
print(f"加速: {analysis['potential_speedup']}")

print("\n=== 優化建議 ===")
for rec in resolver.get_optimization_recommendations():
    print(f"  {rec}")
```

### 循環依賴檢測

```python
resolver = DependencyResolver()

# 添加組件
for i in range(3):
    resolver.add_component(f"comp{i}", "component")

# 創建鏈: comp1 → comp2 → comp0
resolver.add_dependency("comp1", "comp2")
resolver.add_dependency("comp2", "comp0")

# 嘗試添加循環依賴
if resolver.add_dependency("comp0", "comp1"):
    print("依賴已添加")
else:
    print("循環依賴被檢測並拒絕")
```

---

## 性能考量

### 複雜度分析

| 操作 | 複雜度 | 備註 |
|------|--------|------|
| `add_component` | O(1) | 常數時間 |
| `add_dependency` | O(V+E) | 循環檢測 |
| `topological_sort` | O(V+E) | Kahn 算法 |
| `get_execution_phases` | O(V+E) | 依賴關鍵路徑分析 |
| `get_critical_path` | O(V+E) | DFS 最長路徑 |

### 優化建議

**對於大型圖（>1000 個組件）：**
1. 預先驗證沒有循環依賴
2. 使用圖緩存避免重複計算
3. 批量操作而不是單個添加
4. 考慮分層管理

**記憶快取：**
- 拓撲排序結果被自動緩存
- 修改圖時快取被清除
- 手動調用 `memo_cache.clear()` 清除

---

## 版本信息

- **API 版本**: 1.0
- **文檔版本**: 1.0
- **最後更新**: 2025-12-18
