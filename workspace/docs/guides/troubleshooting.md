# 故障排除指南 - Troubleshooting Guide

## 目錄

1. [常見問題](#常見問題)
2. [診斷工具](#診斷工具)
3. [性能問題](#性能問題)
4. [資源問題](#資源問題)
5. [多租戶問題](#多租戶問題)
6. [依賴圖問題](#依賴圖問題)
7. [常見錯誤](#常見錯誤)

---

## 常見問題

### 問: 任務執行失敗，應該如何診斷？

**症狀：** `result.status.value == "failed"`

**診斷步驟：**

```python
# 1. 檢查錯誤信息
if result.status.value == "failed":
    print(f"錯誤: {result.error}")

# 2. 檢查重試情況
if result.retry_count > 0:
    print(f"執行失敗後重試了 {result.retry_count} 次")

# 3. 檢查執行時間
print(f"執行耗時: {result.duration_ms}ms")

# 4. 檢查審計日誌
logs = orch.get_audit_logs(tenant_id)
failure_logs = [log for log in logs if log.status == "failed"]
print(f"最近的失敗: {failure_logs[-1:]}")
```

**可能的原因和解決方案：**

| 錯誤 | 原因 | 解決方案 |
|------|------|--------|
| `RuntimeError: Task execution failed` | 任務邏輯錯誤 | 檢查任務函數實現 |
| `RuntimeError: Resource quota exceeded` | 超過配額 | 升級租戶層級或等待資源釋放 |
| `Timeout` | 執行超時 | 增加超時設置或優化任務 |

---

### 問: 重試機制似乎沒有工作？

**症狀：** 任務失敗但沒有重試

**診斷：**

```python
# 檢查重試策略是否設置
if "component_id" not in orch.retry_policies:
    print("❌ 未設置重試策略")

    # 設置默認重試策略
    orch.retry_policies["component_id"] = RetryPolicy(
        max_retries=3,
        initial_delay=1.0
    )

# 檢查重試政策配置
policy = orch.retry_policies.get("component_id")
if policy:
    print(f"✓ 重試策略: {policy.max_retries} 次重試")
    print(f"✓ 初始延遲: {policy.initial_delay}s")
```

**解決方案：**

1. 確保重試策略已配置
2. 檢查 `max_retries` 不為 0
3. 驗證任務函數是異步的（使用 `async def`）

---

### 問: 資源配額檢查總是失敗？

**症狀：** `check_resource_quota()` 總是返回 False

**診斷：**

```python
# 1. 驗證租戶存在
config = orch.get_tenant(tenant_id)
if not config:
    print("❌ 租戶不存在")
else:
    print(f"✓ 租戶: {config.tenant_name}")

# 2. 檢查配額
print(f"最大並發任務: {config.quota.max_concurrent_tasks}")
print(f"最大內存: {config.quota.max_memory_mb}MB")

# 3. 檢查當前使用情況
metrics = orch.get_metrics()
print(f"活躍任務: {metrics['active_tasks']}")

# 4. 檢查層級
print(f"租戶層級: {config.tier.value}")
```

**常見原因：**

- 租戶 ID 不存在或拼寫錯誤
- 租戶層級太低（Basic 層級有嚴格限制）
- 活躍任務已達上限
- 內存使用已達上限

**解決方案：**

```python
# 升級租戶層級
new_tenant = orch.create_tenant(
    config.tenant_name,
    TenantTier.PROFESSIONAL  # 更高的配額
)
```

---

## 診斷工具

### 系統健康檢查

```python
def system_health_check():
    """檢查整個系統的健康狀態"""
    print("=== 系統健康檢查 ===\n")

    # 檢查指標
    metrics = orch.get_metrics()
    print("📊 系統指標:")
    print(f"  • 總執行數: {metrics['total_executions']}")
    print(f"  • 成功率: {metrics['success_rate']:.1f}%")
    print(f"  • 平均執行時間: {metrics['average_execution_time_ms']:.0f}ms")
    print(f"  • 活躍任務: {metrics['active_tasks']}")
    print(f"  • 註冊租戶: {metrics['registered_tenants']}")

    # 檢查所有租戶
    print("\n👥 租戶狀態:")
    for tenant_id in orch.tenants:
        config = orch.get_tenant(tenant_id)
        health = orch.get_tenant_health(tenant_id)
        print(f"\n  {config.tenant_name} ({config.tier.value}):")
        print(f"    • 正常運行時間: {health.get('uptime_percent', 'N/A')}%")
        print(f"    • 總執行數: {health.get('total_executions', 0)}")

    # 檢查錯誤率高的租戶
    print("\n⚠️ 需要關注的租戶:")
    for tenant_id in orch.tenants:
        health = orch.get_tenant_health(tenant_id)
        if health.get('uptime_percent', 100) < 95:
            print(f"  • {orch.get_tenant(tenant_id).tenant_name}: "
                  f"{health['uptime_percent']:.1f}%")
```

### 依賴圖診斷

```python
def diagnose_dependency_graph():
    """診斷依賴圖的問題"""
    print("=== 依賴圖診斷 ===\n")

    # 統計信息
    stats = resolver.get_dependency_stats()
    print("📈 圖統計:")
    print(f"  • 總組件數: {stats['total_components']}")
    print(f"  • 總依賴數: {stats['total_dependencies']}")
    print(f"  • 平均依賴數: {stats['average_dependency_count']:.1f}")
    print(f"  • 最大深度: {stats['max_dependency_depth']}")
    print(f"  • 循環依賴: {stats['circular_dependencies']}")

    # 並行化分析
    analysis = resolver.get_parallelization_analysis()
    print("\n⚙️ 並行化分析:")
    print(f"  • 執行階段: {analysis['execution_phases']}")
    print(f"  • 順序執行時間: {analysis['sequential_time_ms']:.0f}ms")
    print(f"  • 並行執行時間: {analysis['parallel_time_ms']:.0f}ms")
    print(f"  • 加速倍數: {analysis['parallelization_factor']:.2f}x")

    # 優化建議
    recommendations = resolver.get_optimization_recommendations()
    if recommendations:
        print("\n💡 優化建議:")
        for rec in recommendations:
            print(f"  • {rec}")
```

### 審計日誌分析

```python
def analyze_audit_logs(tenant_id, hours=24):
    """分析租戶的審計日誌以發現問題"""
    logs = orch.get_audit_logs(tenant_id, hours=hours)

    print(f"=== {hours}小時內的審計分析 ===\n")

    # 統計操作
    from collections import Counter
    actions = Counter(log.action for log in logs)
    print("📊 操作統計:")
    for action, count in actions.most_common():
        print(f"  • {action}: {count} 次")

    # 統計狀態
    statuses = Counter(log.status for log in logs)
    print("\n✓ 狀態統計:")
    for status, count in statuses.items():
        percentage = count / len(logs) * 100
        print(f"  • {status}: {count} ({percentage:.1f}%)")

    # 找出失敗
    failures = [log for log in logs if log.status == "failed"]
    if failures:
        print(f"\n❌ 最近的 5 個失敗:")
        for log in failures[-5:]:
            print(f"  • {log.timestamp}: {log.action} on {log.component_id}")

    # 敏感操作
    sensitive = [log for log in logs
                 if log.action in ["create_tenant", "delete_tenant", "modify_quota"]]
    if sensitive:
        print(f"\n🔐 敏感操作:")
        for log in sensitive:
            print(f"  • {log.timestamp}: {log.action} (by {log.user_id})")
```

---

## 性能問題

### 問: 執行時間比預期長？

**診斷步驟：**

```python
# 1. 檢查執行時間
result = await orch.execute_with_retry(task, "comp", tenant_id)
print(f"執行耗時: {result.duration_ms}ms")

# 2. 與基準比較
baseline = 100  # 預期的毫秒數
if result.duration_ms > baseline * 1.5:
    print(f"⚠️ 執行時間異常長")

# 3. 檢查指標趨勢
metrics = orch.get_metrics()
avg_time = metrics['average_execution_time_ms']
print(f"平均執行時間: {avg_time:.0f}ms")

# 4. 檢查系統負載
print(f"活躍任務: {metrics['active_tasks']}")
```

**常見原因和解決方案：**

| 原因 | 表現 | 解決方案 |
|------|------|--------|
| 過度重試 | `retry_count > 2` | 檢查任務穩定性，優化重試策略 |
| 資源不足 | `average_execution_time` 持續增長 | 升級租戶層級或優化代碼 |
| 依賴鏈長 | 有很多執行階段 | 優化依賴圖，減少不必要的依賴 |
| 並發限制 | 許多任務排隊 | 檢查並發配額，優化任務 |

---

### 問: 並行化效果不好？

**診斷：**

```python
analysis = resolver.get_parallelization_analysis()
factor = analysis["parallelization_factor"]

if factor < 2.0:
    print(f"❌ 並行化因子低: {factor:.2f}x")

    # 分析原因
    critical = resolver.get_critical_path()
    print(f"關鍵路徑: {' → '.join(critical)}")
    print(f"路徑長度: {len(critical)}")

    # 獲取優化建議
    recommendations = resolver.get_optimization_recommendations()
    for rec in recommendations:
        print(f"💡 {rec}")
```

**常見原因：**

1. **依賴鏈長** - 組件呈線性排列

   ```
   解決: 重構為樹形或有向無環圖
   ```

2. **依賴複雜** - 過多的交叉依賴

   ```
   解決: 簡化依賴，引入中間層
   ```

3. **組件權重不均** - 某個組件耗時很長

   ```
   解決: 優化該組件的性能
   ```

---

## 資源問題

### 問: 內存使用持續增長？

**診斷：**

```python
import sys

# 1. 監控審計日誌大小
audit_log_size = len(orch.audit_logs)
print(f"審計日誌條目: {audit_log_size}")

# 2. 檢查租戶數量
tenant_count = len(orch.tenants)
print(f"租戶數量: {tenant_count}")

# 3. 檢查對象大小
orch_size = sys.getsizeof(orch)
print(f"協調器對象大小: {orch_size / 1024 / 1024:.2f} MB")
```

**解決方案：**

```python
# 1. 清理舊的審計日誌（在生產環境需要謹慎）
# orch.audit_logs = orch.audit_logs[-10000:]  # 只保留最後 10000 條

# 2. 定期導出和存檔日誌
logs = orch.get_audit_logs(tenant_id, hours=24)
# 存儲到數據庫或文件系統

# 3. 檢查租戶數量是否超出預期
if len(orch.tenants) > expected_count * 2:
    # 調查是否有泄漏的租戶
```

---

## 多租戶問題

### 問: 一個租戶的故障影響了其他租戶？

**症狀：** 一個租戶故障後，其他租戶也變慢或失敗

**診斷：**

```python
# 1. 檢查所有租戶的健康狀態
for tenant_id in orch.tenants:
    health = orch.get_tenant_health(tenant_id)
    config = orch.get_tenant(tenant_id)
    uptime = health.get('uptime_percent', 100)
    status = "✓" if uptime > 95 else "❌"
    print(f"{status} {config.tenant_name}: {uptime:.1f}%")

# 2. 檢查是否有共享資源問題
metrics = orch.get_metrics()
if metrics['active_tasks'] > threshold:
    print("⚠️ 系統任務超載")
```

**解決方案：**

- 增加系統容量
- 實施更嚴格的資源隔離
- 為高優先級租戶預留資源

---

## 依賴圖問題

### 問: 無法添加依賴？

**症狀：** `add_dependency()` 返回 False

**原因和解決方案：**

```python
# 可能原因 1: 循環依賴
if not resolver.add_dependency("comp1", "comp2"):
    print("❌ 無法添加依賴")

    # 檢查是否會形成循環
    # 使用拓撲排序來驗證當前圖的有效性
    try:
        order = resolver.topological_sort()
        print("✓ 當前圖有效")
    except:
        print("❌ 當前圖有循環")

# 可能原因 2: 組件不存在
try:
    resolver.add_dependency("comp1", "nonexistent")
except ValueError as e:
    print(f"❌ 組件不存在: {e}")
```

---

## 常見錯誤

### ModuleNotFoundError

**錯誤：** `ModuleNotFoundError: No module named 'core.orchestrators'`

**解決方案：**

```python
import sys
from pathlib import Path

# 添加 src 目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from core.orchestrators import EnterpriseSynergyMeshOrchestrator
```

---

### ValueError: Circular dependency

**錯誤：** `ValueError: Circular dependency detected`

**解決方案：**

```python
# 重新設計依賴關係，避免循環
# 良好的設計：A → B → C → D
# 不好的設計：A → B → C → A（循環）

# 使用依賴反轉原則
# 而不是: Service A 依賴 Service B
# 使用: 兩者都依賴一個抽象接口
```

---

### RuntimeError: Task execution failed

**錯誤：** `RuntimeError: Task execution failed`

**診斷：**

```python
result = await orch.execute_with_retry(task, "comp", tenant_id)

if result.status.value == "failed":
    print(f"錯誤信息: {result.error}")
    print(f"重試次數: {result.retry_count}")

    # 檢查是否是重試耗盡
    if result.retry_count >= 3:
        print("❌ 已達最大重試次數")
        # 進行回退或手動干預
```

---

## 獲取幫助

### 收集診斷信息

當報告問題時，請提供：

```python
def collect_diagnostics():
    """收集完整的診斷信息"""
    diagnostics = {
        "system_metrics": orch.get_metrics(),
        "dependency_stats": resolver.get_dependency_stats(),
        "tenant_count": len(orch.tenants),
        "audit_log_count": len(orch.audit_logs)
    }

    # 添加最近的錯誤日誌
    diagnostics["recent_failures"] = [
        log for log in orch.audit_logs
        if log.status == "failed"
    ][-10:]

    return diagnostics
```

---

**版本**: 1.0
**最後更新**: 2025-12-18
