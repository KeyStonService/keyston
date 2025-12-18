#!/usr/bin/env python3
"""
Enterprise SynergyMesh Orchestrator 使用示例

演示：
1. 多租戶設置和管理
2. 依賴解析和優化
3. 容錯和重試機制
4. 資源配額管理
5. 審計日誌
6. 監控和指標
"""

import asyncio
import sys
from pathlib import Path

# 添加 src 到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from core.orchestrators import (
    EnterpriseSynergyMeshOrchestrator,
    DependencyResolver,
    TenantTier,
    ResourceQuota,
    RetryPolicy
)


# ============================================================================
# 示例 1: 多租戶設置
# ============================================================================

async def demo_multi_tenancy():
    """演示多租戶支持"""
    print("\n" + "=" * 70)
    print("示例 1: 多租戶支持")
    print("=" * 70)

    orchestrator = EnterpriseSynergyMeshOrchestrator()

    # 創建不同等級的租戶
    tenant1 = orchestrator.create_tenant(
        "小企業客戶",
        TenantTier.BASIC
    )

    tenant2 = orchestrator.create_tenant(
        "中型企業客戶",
        TenantTier.PROFESSIONAL
    )

    tenant3 = orchestrator.create_tenant(
        "大型企業客戶",
        TenantTier.ENTERPRISE
    )

    # 顯示租戶信息
    for tenant_id in [tenant1, tenant2, tenant3]:
        config = orchestrator.get_tenant(tenant_id)
        print(f"\n📋 租戶: {config.tenant_name}")
        print(f"   ID: {tenant_id}")
        print(f"   等級: {config.tier.value}")
        print(f"   最大並發任務: {config.quota.max_concurrent_tasks}")
        print(f"   最大內存: {config.quota.max_memory_mb} MB")
        print(f"   啟用功能: {len(config.features_enabled)} 項")


# ============================================================================
# 示例 2: 依賴解析和優化
# ============================================================================

async def demo_dependency_resolution():
    """演示智能依賴解析"""
    print("\n" + "=" * 70)
    print("示例 2: 依賴解析和優化")
    print("=" * 70)

    resolver = DependencyResolver()

    # 添加組件
    components = {
        "base_agent": ("agent", 1),
        "coordinator": ("agent", 2),
        "autopilot": ("agent", 2),
        "deployment": ("agent", 3),
        "python_island": ("island", 1),
        "rust_island": ("island", 1),
        "orchestrator": ("orchestrator", 4)
    }

    for comp_id, (comp_type, priority) in components.items():
        resolver.add_component(comp_id, comp_type, priority)

    # 添加依賴
    dependencies = [
        ("coordinator", "base_agent"),
        ("autopilot", "base_agent"),
        ("deployment", "base_agent"),
        ("orchestrator", "coordinator"),
        ("orchestrator", "autopilot"),
        ("orchestrator", "deployment"),
        ("orchestrator", "python_island"),
        ("orchestrator", "rust_island")
    ]

    for from_comp, to_comp in dependencies:
        resolver.add_dependency(from_comp, to_comp)

    # 執行拓撲排序
    print("\n🔄 拓撲排序結果:")
    sorted_comps = resolver.topological_sort()
    for i, comp in enumerate(sorted_comps, 1):
        print(f"  {i}. {comp}")

    # 獲取執行階段
    print("\n⚙️  執行階段分析:")
    phases = resolver.get_execution_phases()
    for phase in phases:
        print(f"\n  階段 {phase.phase_number}:")
        print(f"    組件: {', '.join(phase.components)}")
        print(f"    可並行: {'✓' if phase.can_parallel else '✗'}")
        print(f"    估計時間: {phase.estimated_duration_ms:.0f} ms")

    # 並行化分析
    print("\n📊 並行化分析:")
    analysis = resolver.get_parallelization_analysis()
    for key, value in analysis.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    # 優化建議
    print("\n💡 優化建議:")
    recommendations = resolver.get_optimization_recommendations()
    for rec in recommendations:
        print(f"  {rec}")

    # 關鍵路徑
    print("\n🔗 關鍵路徑:")
    critical = resolver.get_critical_path()
    print(f"  {' → '.join(critical)}")


# ============================================================================
# 示例 3: 容錯和重試機制
# ============================================================================

async def demo_fault_tolerance():
    """演示容錯和重試"""
    print("\n" + "=" * 70)
    print("示例 3: 容錯和重試機制")
    print("=" * 70)

    orchestrator = EnterpriseSynergyMeshOrchestrator()
    tenant_id = orchestrator.create_tenant("測試租戶", TenantTier.BASIC)

    # 模擬組件執行（會失敗的函數）
    async def failing_task(**kwargs):
        """會失敗的任務"""
        raise RuntimeError("模擬失敗")

    async def success_task(**kwargs):
        """成功的任務"""
        await asyncio.sleep(0.1)
        return {"status": "success", "data": "執行結果"}

    # 設置重試政策
    orchestrator.retry_policies["test_component"] = RetryPolicy(
        max_retries=3,
        initial_delay=0.1,
        max_delay=1.0
    )

    # 執行會失敗的任務
    print("\n❌ 執行會失敗的任務:")
    result = await orchestrator.execute_with_retry(
        failing_task,
        "test_component",
        tenant_id
    )
    print(f"  狀態: {result.status.value}")
    print(f"  重試次數: {result.retry_count}")
    print(f"  執行時間: {result.duration_ms:.0f} ms")

    # 執行成功的任務
    print("\n✅ 執行成功的任務:")
    result = await orchestrator.execute_with_retry(
        success_task,
        "success_component",
        tenant_id
    )
    print(f"  狀態: {result.status.value}")
    print(f"  重試次數: {result.retry_count}")
    print(f"  輸出: {result.output}")


# ============================================================================
# 示例 4: 資源管理和監控
# ============================================================================

async def demo_resource_management():
    """演示資源管理"""
    print("\n" + "=" * 70)
    print("示例 4: 資源管理和監控")
    print("=" * 70)

    orchestrator = EnterpriseSynergyMeshOrchestrator()

    # 創建不同配額的租戶
    basic_tenant = orchestrator.create_tenant(
        "基礎計劃客戶",
        TenantTier.BASIC
    )

    enterprise_tenant = orchestrator.create_tenant(
        "企業計劃客戶",
        TenantTier.ENTERPRISE
    )

    # 檢查配額
    print("\n📊 基礎計劃配額:")
    basic_config = orchestrator.get_tenant(basic_tenant)
    print(f"  最大並發: {basic_config.quota.max_concurrent_tasks}")
    print(f"  最大內存: {basic_config.quota.max_memory_mb} MB")
    print(f"  速率限制: {basic_config.quota.rate_limit_per_second} req/s")
    print(f"  小時配額: {basic_config.quota.max_tasks_per_hour} tasks")

    print("\n📊 企業計劃配額:")
    enterprise_config = orchestrator.get_tenant(enterprise_tenant)
    print(f"  最大並發: {enterprise_config.quota.max_concurrent_tasks}")
    print(f"  最大內存: {enterprise_config.quota.max_memory_mb} MB")
    print(f"  速率限制: {enterprise_config.quota.rate_limit_per_second} req/s")
    print(f"  小時配額: {enterprise_config.quota.max_tasks_per_hour} tasks")

    # 檢查資源配額
    print(f"\n✅ 基礎租戶可並發執行: {orchestrator.check_resource_quota(basic_tenant, 'concurrent')}")
    print(f"✅ 企業租戶可並發執行: {orchestrator.check_resource_quota(enterprise_tenant, 'concurrent')}")


# ============================================================================
# 示例 5: 審計和監控
# ============================================================================

async def demo_audit_and_monitoring():
    """演示審計和監控"""
    print("\n" + "=" * 70)
    print("示例 5: 審計和監控")
    print("=" * 70)

    orchestrator = EnterpriseSynergyMeshOrchestrator()
    tenant_id = orchestrator.create_tenant("測試租戶", TenantTier.PROFESSIONAL)

    # 執行一些操作
    await demo_resource_management()

    # 獲取審計日誌
    audit_logs = orchestrator.get_audit_logs(tenant_id, hours=24)
    print(f"\n📋 審計日誌 ({len(audit_logs)} 條記錄):")
    for log in audit_logs[-5:]:  # 顯示最後 5 條
        print(f"  - {log.action} on {log.component_id} ({log.status})")

    # 獲取系統指標
    metrics = orchestrator.get_metrics()
    print(f"\n📊 系統指標:")
    print(f"  總執行數: {metrics['total_executions']}")
    print(f"  成功執行: {metrics['successful_executions']}")
    print(f"  失敗執行: {metrics['failed_executions']}")
    print(f"  成功率: {metrics['success_rate']:.1f}%")
    print(f"  平均執行時間: {metrics['average_execution_time_ms']:.1f} ms")
    print(f"  活躍任務: {metrics['active_tasks']}")
    print(f"  已註冊租戶: {metrics['registered_tenants']}")

    # 租戶健康狀態
    print(f"\n❤️  租戶健康狀態:")
    health = orchestrator.get_tenant_health(tenant_id)
    if health.get("uptime_percent"):
        print(f"  正常運行時間: {health['uptime_percent']:.1f}%")
        print(f"  總執行次數: {health['total_executions']}")
        print(f"  成功執行: {health['successful']}")
    else:
        print(f"  狀態: {health.get('status', '無數據')}")


# ============================================================================
# 主函數
# ============================================================================

async def main():
    """運行所有示例"""
    print("\n" + "=" * 70)
    print("Enterprise SynergyMesh Orchestrator - 功能演示")
    print("=" * 70)

    try:
        # 運行所有示例
        await demo_multi_tenancy()
        await demo_dependency_resolution()
        await demo_fault_tolerance()
        await demo_resource_management()
        await demo_audit_and_monitoring()

        print("\n" + "=" * 70)
        print("✅ 所有示例執行完成！")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
