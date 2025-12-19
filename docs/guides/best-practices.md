# 最佳實踐指南 - Best Practices Guide

## 目錄

1. [多租戶管理](#多租戶管理)
2. [任務執行](#任務執行)
3. [依賴管理](#依賴管理)
4. [資源管理](#資源管理)
5. [監控和告警](#監控和告警)
6. [安全性](#安全性)
7. [性能優化](#性能優化)

---

## 多租戶管理

### ✅ 最佳實踐

#### 1. 為不同客戶使用不同層級

```python
# ❌ 不好 - 所有客戶都用同一層級
basic_tenant = orch.create_tenant("Company A", TenantTier.BASIC)
another_tenant = orch.create_tenant("Company B", TenantTier.BASIC)

# ✅ 好 - 根據需要選擇合適層級
starter_tenant = orch.create_tenant("Startup X", TenantTier.BASIC)
pro_tenant = orch.create_tenant("Company Y", TenantTier.PROFESSIONAL)
enterprise_tenant = orch.create_tenant("Big Corp", TenantTier.ENTERPRISE)
```

#### 2. 動態調整租戶配置

```python
# ✅ 在訂閱升級時更新配置
current_config = orch.get_tenant(tenant_id)
if needs_upgrade:
    # 創建新租戶或更新現有配置
    new_tenant = orch.create_tenant(
        current_config.tenant_name,
        TenantTier.PROFESSIONAL
    )
```

#### 3. 記錄租戶生命週期事件

```python
# ✅ 監控重要的租戶事件
for log in orch.get_audit_logs(tenant_id):
    if log.action == "create_tenant":
        print(f"租戶創建於: {log.timestamp}")
    elif log.action == "delete_tenant":
        print(f"租戶刪除於: {log.timestamp}")
```

---

## 任務執行

### ✅ 最佳實踐

#### 1. 檢查資源配額後才執行

```python
# ❌ 不好 - 直接執行，可能超配
result = await orch.execute_with_retry(task, "comp", tenant_id)

# ✅ 好 - 先檢查配額
if orch.check_resource_quota(tenant_id, "concurrent"):
    result = await orch.execute_with_retry(task, "comp", tenant_id)
else:
    return {"error": "Resource quota exceeded"}
```

#### 2. 自定義重試策略

```python
# ✅ 為不同的任務設置不同的重試策略
from core.orchestrators import RetryPolicy

# 快速、可靠的任務：保守重試
orch.retry_policies["fast_task"] = RetryPolicy(
    max_retries=2,
    initial_delay=0.5
)

# 慢速、不可靠的外部服務調用：激進重試
orch.retry_policies["external_api"] = RetryPolicy(
    max_retries=5,
    initial_delay=1.0,
    max_delay=30.0
)
```

#### 3. 處理執行結果

```python
# ✅ 完整的結果處理
result = await orch.execute_with_retry(task, "comp", tenant_id)

if result.status.value == "success":
    logger.info(f"Task succeeded in {result.duration_ms}ms")
    return result.output
elif result.status.value == "failed":
    logger.error(f"Task failed: {result.error}")
    if result.retry_count >= 3:
        # 重試耗盡，進行回退
        return fallback_handler()
else:
    logger.warning(f"Task timeout after {result.duration_ms}ms")
    return None
```

#### 4. 監控重試情況

```python
# ✅ 跟踪需要重試的任務
result = await orch.execute_with_retry(task, "comp", tenant_id)

if result.retry_count > 0:
    logger.warning(
        f"Task {result.component_id} needed "
        f"{result.retry_count} retries"
    )
    # 發送告警，查看為什麼需要重試
    alert_on_high_retry_count(tenant_id, result.component_id)
```

---

## 依賴管理

### ✅ 最佳實踐

#### 1. 盡量減少依賴

```python
# ❌ 過度耦合 - 每個組件都依賴所有其他組件
for i in range(10):
    for j in range(10):
        if i != j:
            resolver.add_dependency(f"comp{i}", f"comp{j}")

# ✅ 合理依賴 - 只添加必需的依賴
resolver.add_dependency("api_service", "database")
resolver.add_dependency("api_service", "cache")
resolver.add_dependency("worker", "database")
```

#### 2. 使用明確的依賴語義

```python
# ✅ 依賴關係清晰
# "api" 依賴於 "database" 意味著:
# - api 需要 database 在它之前啟動
# - api 獲取 database 的輸出
resolver.add_dependency("api", "database")
```

#### 3. 定期分析並行化機會

```python
# ✅ 找出可並行執行的組件
analysis = resolver.get_parallelization_analysis()
if analysis["parallelization_factor"] < 2.0:
    # 並行化機會不足
    recommendations = resolver.get_optimization_recommendations()
    for rec in recommendations:
        logger.info(f"優化建議: {rec}")
```

#### 4. 實現依賴圖可視化

```python
# ✅ 導出依賴圖用於分析
import json

graph = resolver.export_graph()
with open("dependency_graph.json", "w") as f:
    json.dump(graph, f, indent=2)

# 在可視化工具中查看
# - 識別瓶頸
# - 發現不必要的耦合
# - 規劃優化
```

---

## 資源管理

### ✅ 最佳實踐

#### 1. 理解層級配額

```python
# ✅ 根據客戶計劃選擇合適的配額
tiers = {
    TenantTier.BASIC: 100,        # 小型項目
    TenantTier.PROFESSIONAL: 5000, # 中型項目
    TenantTier.ENTERPRISE: 100000  # 大型企業
}

tenant_id = orch.create_tenant("Customer",
                              appropriate_tier)
```

#### 2. 實現優雅的配額超限處理

```python
# ✅ 檢查配額並提供有用的反饋
async def execute_task_safely(task, tenant_id):
    config = orch.get_tenant(tenant_id)

    if not orch.check_resource_quota(tenant_id):
        # 返回有用的錯誤信息
        return {
            "error": "Resource quota exceeded",
            "current_plan": config.tier.value,
            "upgrade_info": "Contact sales to upgrade"
        }

    return await orch.execute_with_retry(task, "comp", tenant_id)
```

#### 3. 監控資源使用趨勢

```python
# ✅ 追蹤資源使用以預測升級需求
metrics = orch.get_metrics()
if metrics["average_execution_time_ms"] > 500:
    # 響應時間變慢，可能需要升級計劃
    recommend_upgrade(tenant_id)

if metrics["active_tasks"] > threshold:
    # 並發任務接近上限
    send_capacity_warning(tenant_id)
```

---

## 監控和告警

### ✅ 最佳實踐

#### 1. 設置關鍵指標監控

```python
# ✅ 監控系統健康指標
def monitor_system_health():
    metrics = orch.get_metrics()

    # 監控成功率
    success_rate = metrics["success_rate"]
    if success_rate < 95:
        alert(f"Success rate low: {success_rate:.1f}%")

    # 監控響應時間
    avg_time = metrics["average_execution_time_ms"]
    if avg_time > 1000:
        alert(f"Average execution time high: {avg_time:.0f}ms")

    # 監控租戶數
    if metrics["registered_tenants"] > capacity_limit:
        alert("Approaching maximum tenant capacity")
```

#### 2. 實現審計日誌監控

```python
# ✅ 監控異常操作
def check_audit_logs():
    logs = orch.get_audit_logs(tenant_id, hours=1)

    # 統計失敗操作
    failures = [log for log in logs if log.status == "failed"]
    if len(failures) > threshold:
        alert(f"High failure rate for {tenant_id}")

    # 檢測敏感操作
    sensitive = [log for log in logs
                 if log.action in ["create_tenant", "delete_tenant"]]
    for log in sensitive:
        audit_log(f"Sensitive operation: {log.action}")
```

#### 3. 租戶健康檢查

```python
# ✅ 定期檢查租戶健康狀態
def health_check_all_tenants():
    for tenant_id in orch.tenants:
        health = orch.get_tenant_health(tenant_id)

        uptime = health.get("uptime_percent", 0)
        if uptime < 99:
            alert(f"Tenant {tenant_id} uptime: {uptime:.1f}%")

        config = orch.get_tenant(tenant_id)
        print(f"{config.tenant_name}: {health}")
```

---

## 安全性

### ✅ 最佳實踐

#### 1. 租戶隔離驗證

```python
# ✅ 始終驗證租戶 ID
@app.post("/execute")
async def execute_task(tenant_id: str, task_data: dict):
    # 驗證租戶存在
    try:
        config = orch.get_tenant(tenant_id)
    except ValueError:
        return {"error": "Invalid tenant"}

    # 驗證當前用戶是否屬於該租戶
    if not is_user_in_tenant(current_user, tenant_id):
        return {"error": "Unauthorized"}

    return await execute_task_for_tenant(tenant_id, task_data)
```

#### 2. 敏感操作日誌

```python
# ✅ 記錄所有敏感操作
def execute_sensitive_operation(operation, tenant_id):
    try:
        result = perform_operation(operation)
        audit_log(tenant_id, operation, "success")
    except Exception as e:
        audit_log(tenant_id, operation, "failed", error=str(e))
        # 發送安全告警
        security_alert(f"Failed operation: {operation}")
        raise
```

#### 3. 速率限制濫用檢測

```python
# ✅ 檢測可能的濫用行為
def detect_abuse(tenant_id):
    logs = orch.get_audit_logs(tenant_id, hours=1)

    # 計算請求率
    request_count = len(logs)
    config = orch.get_tenant(tenant_id)
    rate_limit = config.quota.rate_limit_per_second

    if request_count / 3600 > rate_limit * 1.5:
        # 明顯超過率限制
        investigate_tenant(tenant_id)
```

---

## 性能優化

### ✅ 最佳實踐

#### 1. 優化依賴圖

```python
# ✅ 識別並優化瓶頸
analysis = resolver.get_parallelization_analysis()

# 如果並行化因子低於 2.0，優化圖
if analysis["parallelization_factor"] < 2.0:
    # 分析關鍵路徑
    critical = resolver.get_critical_path()
    print(f"關鍵路徑: {' → '.join(critical)}")

    # 優化關鍵路徑上的組件
    for component in critical:
        optimize_component_performance(component)
```

#### 2. 批量操作優化

```python
# ❌ 不好 - 單個執行
for item in items:
    result = await orch.execute_with_retry(
        process_item,
        "processor",
        tenant_id
    )

# ✅ 好 - 批量執行
async def batch_process(items, tenant_id):
    tasks = [
        orch.execute_with_retry(
            process_item,
            f"processor_{i}",
            tenant_id
        )
        for i, item in enumerate(items)
    ]
    results = await asyncio.gather(*tasks)
    return results
```

#### 3. 執行時間預測

```python
# ✅ 使用執行階段估計預測時間
phases = resolver.get_execution_phases()

total_time = sum(p.estimated_duration_ms for p in phases)
parallel_time = max((p.estimated_duration_ms for p in phases), default=0)

print(f"預期順序執行時間: {total_time:.0f}ms")
print(f"預期並行執行時間: {parallel_time:.0f}ms")
```

#### 4. 緩存優化

```python
# ✅ 利用拓撲排序的緩存
# 第一次調用計算排序並緩存
order = resolver.topological_sort()

# 後續調用返回緩存的結果
order = resolver.topological_sort()  # 快速返回

# 在需要時清除緩存
resolver.memo_cache.clear()
```

---

## 常見模式

### 多步工作流

```python
# ✅ 協調多個帶依賴的步驟
async def orchestrate_workflow(tenant_id):
    steps = {
        "data_prep": prepare_data,
        "validation": validate_data,
        "processing": process_data,
        "storage": store_results
    }

    # 定義依賴
    resolver = DependencyResolver()
    for step_name in steps:
        resolver.add_component(step_name, "step")

    resolver.add_dependency("validation", "data_prep")
    resolver.add_dependency("processing", "validation")
    resolver.add_dependency("storage", "processing")

    # 執行
    order = resolver.topological_sort()
    for step_name in order:
        result = await orch.execute_with_retry(
            steps[step_name],
            step_name,
            tenant_id
        )
        if result.status.value != "success":
            return {"error": f"Step {step_name} failed"}

    return {"success": True}
```

### 降級和容錯

```python
# ✅ 實現降級策略
async def execute_with_fallback(task, tenant_id):
    result = await orch.execute_with_retry(
        task,
        "main_task",
        tenant_id,
        max_retries=3
    )

    if result.status.value == "success":
        return result.output

    # 嘗試降級版本
    logger.warning(f"Main task failed, using fallback")
    return await fallback_task(tenant_id)
```

---

## 檢查清單

在部署到生產前，確保：

- [ ] 所有租戶都有適當的層級分配
- [ ] 重試策略根據任務特性調整
- [ ] 資源配額適合預期工作負載
- [ ] 監控和告警已配置
- [ ] 審計日誌監控已實現
- [ ] 安全驗證已到位
- [ ] 依賴圖已優化
- [ ] 性能測試已完成
- [ ] 備份和恢復計劃已制定
- [ ] 文檔已更新

---

**版本**: 1.0
**最後更新**: 2025-12-18
