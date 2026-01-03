# Enterprise SynergyMesh Orchestrator API 文檔

## 目錄

1. [概述](#概述)
2. [核心類](#核心類)
3. [多租戶管理](#多租戶管理)
4. [任務執行](#任務執行)
5. [資源管理](#資源管理)
6. [審計和監控](#審計和監控)
7. [錯誤處理](#錯誤處理)
8. [使用示例](#使用示例)

---

## 概述

`EnterpriseSynergyMeshOrchestrator` 是一個企業級的分佈式協調器，提供以下核心功能：

- **多租戶隔離**：為不同客戶提供獨立的資源和功能
- **智能依賴管理**：自動解析組件依賴並優化執行順序
- **容錯重試**：內置指數退避重試機制
- **資源配額管理**：按租戶和層級限制資源使用
- **審計日誌**：完整記錄所有操作以用於合規性
- **性能監控**：實時指標收集和健康狀態監測

---

## 核心類

### EnterpriseSynergyMeshOrchestrator

主要協調器類，負責管理租戶、執行任務和監控系統。

```python
from core.orchestrators import EnterpriseSynergyMeshOrchestrator

orch = EnterpriseSynergyMeshOrchestrator()
```

#### 主要方法

##### `create_tenant(tenant_name: str, tier: TenantTier) -> str`

創建新租戶。

**參數：**

- `tenant_name` (str): 租戶名稱
- `tier` (TenantTier): 租戶等級 (BASIC, PROFESSIONAL, ENTERPRISE)

**返回值：** 租戶 ID (str)

**示例：**

```python
tenant_id = orch.create_tenant("Company A", TenantTier.PROFESSIONAL)
# 返回: "tenant-abc123def456"
```

**功能：**

- 創建新租戶記錄
- 分配租戶 ID
- 初始化資源配額
- 記錄審計日誌

---

##### `get_tenant(tenant_id: str) -> TenantConfig`

獲取租戶配置。

**參數：**

- `tenant_id` (str): 租戶 ID

**返回值：** `TenantConfig` 對象

**示例：**

```python
config = orch.get_tenant(tenant_id)
print(f"等級: {config.tier.value}")
print(f"最大並發: {config.quota.max_concurrent_tasks}")
print(f"啟用功能: {config.features_enabled}")
```

**返回的 TenantConfig 屬性：**

- `tenant_id`: 租戶 ID
- `tenant_name`: 租戶名稱
- `tier`: 租戶等級 (TenantTier)
- `quota`: 資源配額 (ResourceQuota)
- `features_enabled`: 啟用的功能列表
- `created_at`: 創建時間

---

##### `execute_with_retry(task_func, component_id, tenant_id, max_retries=3) -> ExecutionResult`

使用重試機制執行任務（異步）。

**參數：**

- `task_func` (async callable): 異步任務函數
- `component_id` (str): 組件 ID
- `tenant_id` (str): 租戶 ID
- `max_retries` (int): 最大重試次數 (預設: 3)

**返回值：** `ExecutionResult` 對象

**示例：**

```python
async def my_task(**kwargs):
    # 任務邏輯
    return {"result": "success"}

result = await orch.execute_with_retry(
    my_task,
    "my_component",
    tenant_id,
    max_retries=3
)

if result.status.value == "success":
    print(f"成功！耗時: {result.duration_ms}ms")
    print(f"重試次數: {result.retry_count}")
else:
    print(f"失敗: {result.error}")
```

**ExecutionResult 屬性：**

- `component_id`: 組件 ID
- `status`: 執行狀態 (SUCCESS, FAILED, TIMEOUT)
- `output`: 任務輸出
- `error`: 錯誤信息（如果失敗）
- `duration_ms`: 執行耗時
- `retry_count`: 實際重試次數

---

##### `check_resource_quota(tenant_id: str, quota_type: str = "concurrent") -> bool`

檢查租戶是否有足夠的資源配額。

**參數：**

- `tenant_id` (str): 租戶 ID
- `quota_type` (str): 配額類型 (concurrent, memory, rate_limit)

**返回值：** bool

**示例：**

```python
can_run = orch.check_resource_quota(tenant_id, "concurrent")
if can_run:
    # 執行任務
    pass
else:
    # 等待資源釋放或返回 429 Too Many Requests
    pass
```

---

##### `get_metrics() -> dict`

獲取系統指標。

**返回值：** 指標字典

**示例：**

```python
metrics = orch.get_metrics()
print(f"總執行數: {metrics['total_executions']}")
print(f"成功率: {metrics['success_rate']:.1f}%")
print(f"平均執行時間: {metrics['average_execution_time_ms']:.1f}ms")
print(f"活躍任務: {metrics['active_tasks']}")
print(f"已註冊租戶: {metrics['registered_tenants']}")
```

**返回的指標：**

- `total_executions`: 總執行數
- `successful_executions`: 成功執行數
- `failed_executions`: 失敗執行數
- `success_rate`: 成功率 (%)
- `average_execution_time_ms`: 平均執行時間 (ms)
- `total_retry_attempts`: 總重試次數
- `active_tasks`: 當前活躍任務數
- `registered_tenants`: 已註冊租戶數

---

##### `get_tenant_health(tenant_id: str) -> dict`

獲取租戶健康狀態。

**參數：**

- `tenant_id` (str): 租戶 ID

**返回值：** 健康狀態字典

**示例：**

```python
health = orch.get_tenant_health(tenant_id)
print(f"正常運行時間: {health['uptime_percent']:.1f}%")
print(f"總執行數: {health['total_executions']}")
print(f"成功執行: {health['successful']}")
```

---

##### `get_audit_logs(tenant_id: str, hours: int = 24, action: str = None) -> List[AuditLog]`

獲取租戶的審計日誌。

**參數：**

- `tenant_id` (str): 租戶 ID
- `hours` (int): 回查時間範圍（小時）
- `action` (str): 可選，篩選特定操作類型

**返回值：** `AuditLog` 對象列表

**示例：**

```python
# 獲取過去 24 小時的所有日誌
logs = orch.get_audit_logs(tenant_id)

# 獲取過去 7 天的 create_tenant 操作
logs = orch.get_audit_logs(tenant_id, hours=168, action="create_tenant")

for log in logs:
    print(f"{log.timestamp}: {log.action} ({log.status})")
    print(f"  操作者: {log.user_id}")
    print(f"  組件: {log.component_id}")
```

**AuditLog 屬性：**

- `audit_id`: 審計記錄 ID
- `timestamp`: 時間戳
- `tenant_id`: 租戶 ID
- `action`: 操作類型
- `component_id`: 組件 ID
- `user_id`: 用戶 ID
- `status`: 操作狀態
- `metadata`: 額外元數據

---

## 多租戶管理

### TenantTier 枚舉

定義租戶的三個層級。

```python
from core.orchestrators import TenantTier

# 基礎層
TenantTier.BASIC
# 專業層
TenantTier.PROFESSIONAL
# 企業層
TenantTier.ENTERPRISE
```

### 層級配額對比

| 功能 | Basic | Professional | Enterprise |
|------|-------|-------------|-----------|
| 最大並發任務 | 5 | 20 | 100 |
| 最大內存 (MB) | 512 | 2048 | 8192 |
| 最大 CPU 使用率 (%) | 50 | 75 | 95 |
| 小時任務限制 | 100 | 5000 | 100000 |
| 速率限制 (req/s) | 10 | 100 | 1000 |

### 租戶隔離保證

每個租戶：

- 擁有獨立的資源配額
- 不能訪問其他租戶的數據
- 有獨立的審計日誌
- 的故障不影響其他租戶

---

## 任務執行

### 重試策略

```python
from core.orchestrators import RetryPolicy

policy = RetryPolicy(
    max_retries=3,
    initial_delay=1.0,  # 初始延遲 (秒)
    max_delay=60.0,     # 最大延遲 (秒)
    exponential_base=2  # 指數退避基數
)

orch.retry_policies["component_id"] = policy
```

**指數退避公式：**

```
delay = min(
    initial_delay * (exponential_base ^ attempt),
    max_delay
)
```

**示例延遲序列（1s 初始延遲）：**

- 第 1 次重試: 1s
- 第 2 次重試: 2s
- 第 3 次重試: 4s
- 第 4 次重試: 8s
- 第 5 次重試: 16s
- ...
- 上限: 60s

### 執行狀態

```python
from core.orchestrators import ExecutionStatus

ExecutionStatus.SUCCESS    # 成功
ExecutionStatus.FAILED     # 失敗
ExecutionStatus.TIMEOUT    # 超時
ExecutionStatus.RETRYING   # 重試中
```

---

## 資源管理

### ResourceQuota 配置

```python
from core.orchestrators import ResourceQuota

quota = ResourceQuota(
    max_concurrent_tasks=20,      # 最大並發任務
    max_memory_mb=2048,           # 最大內存 (MB)
    max_cpu_percent=75,           # 最大 CPU 使用率 (%)
    max_tasks_per_hour=5000,      # 小時任務限制
    rate_limit_per_second=100     # 速率限制 (req/s)
)
```

### 配額檢查流程

1. 獲取租戶配置
2. 檢查當前使用情況
3. 比較配額限制
4. 返回是否允許執行
5. 記錄審計日誌

### 速率限制

- 使用 1 秒滑動窗口
- 按租戶層級限制請求
- 超限請求被拒絕（返回 429）
- 自動重置過期的窗口

---

## 審計和監控

### 審計日誌記錄

所有敏感操作都會被記錄：

- `create_tenant` - 創建租戶
- `delete_tenant` - 刪除租戶
- `modify_quota` - 修改配額
- `execute_task` - 執行任務
- `execute_with_retry` - 帶重試的執行

### 日誌保留期

- 基本日誌: 90 天
- 敏感操作日誌: 1 年
- 審計日誌導出: 支持 CSV、JSON 格式

### 監控指標

**實時指標：**

- 活躍任務數
- 每秒請求數 (RPS)
- 平均響應時間
- 錯誤率

**累計指標：**

- 總執行數
- 成功率
- 總重試次數
- 平均執行時間

---

## 錯誤處理

### 常見異常

```python
from core.orchestrators import ...

try:
    result = await orch.execute_with_retry(task, "comp", tenant_id)
except ValueError as e:
    # 無效的租戶 ID 或組件 ID
    print(f"驗證錯誤: {e}")
except RuntimeError as e:
    # 任務執行失敗
    print(f"執行錯誤: {e}")
except Exception as e:
    # 其他系統錯誤
    print(f"系統錯誤: {e}")
```

### 最佳實踐

1. **總是檢查資源配額**

   ```python
   if orch.check_resource_quota(tenant_id):
       # 執行任務
   ```

2. **實現優雅降級**

   ```python
   if result.status.value != "success":
       # 降級到備用方案
   ```

3. **監控重試次數**

   ```python
   if result.retry_count > 0:
       logging.warning(f"Task required {result.retry_count} retries")
   ```

4. **定期檢查審計日誌**

   ```python
   suspicious = orch.get_audit_logs(tenant_id, action="failed")
   if len(suspicious) > threshold:
       # 告警
   ```

---

## 使用示例

### 完整工作流示例

```python
import asyncio
from core.orchestrators import (
    EnterpriseSynergyMeshOrchestrator,
    TenantTier,
    RetryPolicy
)

async def main():
    # 初始化協調器
    orch = EnterpriseSynergyMeshOrchestrator()

    # 創建租戶
    tenant_id = orch.create_tenant("MyCompany", TenantTier.PROFESSIONAL)

    # 設置重試策略
    orch.retry_policies["my_component"] = RetryPolicy(
        max_retries=3,
        initial_delay=0.5
    )

    # 定義任務
    async def process_order(**kwargs):
        # 業務邏輯
        return {"order_id": "12345", "status": "processed"}

    # 檢查資源配額
    if orch.check_resource_quota(tenant_id):
        # 執行任務
        result = await orch.execute_with_retry(
            process_order,
            "order_processor",
            tenant_id
        )

        if result.status.value == "success":
            print(f"訂單已處理: {result.output}")
        else:
            print(f"處理失敗: {result.error}")
            print(f"重試次數: {result.retry_count}")
    else:
        print("資源配額已達上限")

    # 獲取指標
    metrics = orch.get_metrics()
    print(f"系統健康: 成功率 {metrics['success_rate']:.1f}%")

    # 檢查租戶健康
    health = orch.get_tenant_health(tenant_id)
    print(f"租戶狀態: {health}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 版本信息

- **API 版本**: 1.0
- **文檔版本**: 1.0
- **最後更新**: 2025-12-18

---

## 獲取幫助

- 查看 [最佳實踐指南](best-practices.md)
- 查看 [故障排除指南](troubleshooting.md)
- 查看 [配置指南](configuration.md)
