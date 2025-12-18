#!/usr/bin/env python3
"""
Enterprise SynergyMesh Orchestrator - 企業級統一協調系統

增強功能：
1. 多租戶支持 (Multi-Tenancy)
2. 高可用性部署 (HA Deployment)
3. 進階依賴管理 (Dependency Management)
4. 智能容錯機制 (Fault Tolerance)
5. 資源管理和配額 (Resource Management)
6. 審計和合規 (Audit & Compliance)
7. 性能優化 (Performance Optimization)

這是 Phase 5 企業級增強的核心組件。
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from functools import wraps
import json

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# 資料結構定義
# ============================================================================

class ExecutionStatus(Enum):
    """執行狀態"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class ComponentType(Enum):
    """組件類型"""
    AGENT = "agent"
    ISLAND = "island"
    BRIDGE = "bridge"
    SERVICE = "service"


class TenantTier(Enum):
    """租戶等級"""
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class RetryPolicy:
    """重試政策"""
    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0

    def get_delay(self, attempt: int) -> float:
        """計算重試延遲（指數退避）"""
        delay = min(
            self.initial_delay * (self.exponential_base ** attempt),
            self.max_delay
        )
        return delay


@dataclass
class ResourceQuota:
    """資源配額"""
    max_concurrent_tasks: int = 10
    max_memory_mb: int = 1024
    max_cpu_percent: float = 80.0
    max_tasks_per_hour: int = 1000
    rate_limit_per_second: float = 100.0


@dataclass
class TenantConfig:
    """租戶配置"""
    tenant_id: str
    tenant_name: str
    tier: TenantTier
    quota: ResourceQuota
    features_enabled: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.now)
    sla_uptime_percent: float = 99.9


@dataclass
class ComponentDependency:
    """組件依賴"""
    component_id: str
    depends_on: List[str] = field(default_factory=list)
    type: ComponentType = ComponentType.AGENT
    required: bool = True


@dataclass
class AuditLog:
    """審計日誌"""
    audit_id: str
    timestamp: datetime
    tenant_id: str
    action: str
    component_id: str
    user_id: Optional[str]
    status: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "timestamp": self.timestamp.isoformat(),
            "tenant_id": self.tenant_id,
            "action": self.action,
            "component_id": self.component_id,
            "user_id": self.user_id,
            "status": self.status,
            "metadata": self.metadata
        }


@dataclass
class ExecutionResult:
    """執行結果"""
    component_id: str
    component_type: ComponentType
    status: ExecutionStatus
    start_time: datetime
    tenant_id: Optional[str] = None
    end_time: Optional[datetime] = None
    output: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_id": self.component_id,
            "component_type": self.component_type.value,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "output": self.output,
            "error": self.error,
            "retry_count": self.retry_count,
            "tenant_id": self.tenant_id,
            "metadata": self.metadata
        }


# ============================================================================
# 裝飾器和輔助函數
# ============================================================================

def with_tenant_isolation(func):
    """租戶隔離裝飾器"""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        tenant_id = kwargs.get('tenant_id')
        if tenant_id and tenant_id not in self.tenants:
            raise ValueError(f"Tenant {tenant_id} not found")
        return await func(self, *args, **kwargs)
    return wrapper


def with_audit_log(func):
    """審計日誌裝飾器"""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        component_id = kwargs.get('component_id', 'unknown')
        tenant_id = kwargs.get('tenant_id', 'system')
        action = func.__name__

        try:
            result = await func(self, *args, **kwargs)
            self._log_audit(tenant_id, action, component_id, "success")
            return result
        except Exception as e:
            self._log_audit(tenant_id, action, component_id, "failure", str(e))
            raise
    return wrapper


def with_rate_limit(func):
    """速率限制裝飾器"""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        tenant_id = kwargs.get('tenant_id', 'system')

        # 檢查速率限制
        if not self._check_rate_limit(tenant_id):
            raise RuntimeError(f"Rate limit exceeded for tenant {tenant_id}")

        return await func(self, *args, **kwargs)
    return wrapper


# ============================================================================
# 核心企業級協調器
# ============================================================================

class EnterpriseSynergyMeshOrchestrator:
    """
    企業級 SynergyMesh 統一協調器

    核心功能：
    ✓ 多租戶隔離和管理
    ✓ 智能依賴解析和執行順序優化
    ✓ 自動重試和容錯
    ✓ 資源配額和限制
    ✓ 審計日誌和合規
    ✓ 性能監控和優化
    ✓ 高可用性部署支持
    """

    def __init__(self, project_root: Optional[Path] = None):
        """初始化企業級協調器"""
        self.project_root = project_root or Path.cwd()

        # 租戶管理
        self.tenants: Dict[str, TenantConfig] = {}
        self.tenant_agents: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.tenant_islands: Dict[str, Dict[str, Any]] = defaultdict(dict)

        # 依賴管理
        self.dependencies: Dict[str, ComponentDependency] = {}
        self.execution_order_cache: Dict[str, List[str]] = {}

        # 執行管理
        self.execution_results: List[ExecutionResult] = []
        self.active_tasks: Set[str] = set()
        self.retry_policies: Dict[str, RetryPolicy] = defaultdict(
            lambda: RetryPolicy()
        )

        # 資源管理
        self.tenant_resource_usage: Dict[str, Dict[str, float]] = defaultdict(
            lambda: defaultdict(float)
        )
        self.rate_limiters: Dict[str, Tuple[int, datetime]] = {}

        # 審計
        self.audit_logs: List[AuditLog] = []

        # 監控
        self.metrics = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_retry_attempts": 0,
            "average_execution_time_ms": 0.0
        }

        self.is_running = False
        self.start_time: Optional[datetime] = None

        logger.info("🏢 Enterprise SynergyMeshOrchestrator 初始化完成")

    # ========================================================================
    # 多租戶管理
    # ========================================================================

    def create_tenant(
        self,
        tenant_name: str,
        tier: TenantTier = TenantTier.BASIC,
        custom_quota: Optional[ResourceQuota] = None
    ) -> str:
        """創建租戶"""
        tenant_id = f"tenant-{uuid.uuid4().hex[:8]}"

        # 根據等級設置配額
        quota = custom_quota or self._get_default_quota(tier)

        config = TenantConfig(
            tenant_id=tenant_id,
            tenant_name=tenant_name,
            tier=tier,
            quota=quota,
            features_enabled=self._get_features_for_tier(tier)
        )

        self.tenants[tenant_id] = config
        logger.info(f"✅ 租戶已創建: {tenant_id} ({tenant_name}, {tier.value})")

        self._log_audit("system", "create_tenant", tenant_id, "success")

        return tenant_id

    def _get_default_quota(self, tier: TenantTier) -> ResourceQuota:
        """根據等級獲取默認配額"""
        quotas = {
            TenantTier.BASIC: ResourceQuota(
                max_concurrent_tasks=5,
                max_memory_mb=512,
                max_cpu_percent=50.0,
                max_tasks_per_hour=100,
                rate_limit_per_second=10.0
            ),
            TenantTier.PROFESSIONAL: ResourceQuota(
                max_concurrent_tasks=20,
                max_memory_mb=2048,
                max_cpu_percent=75.0,
                max_tasks_per_hour=5000,
                rate_limit_per_second=100.0
            ),
            TenantTier.ENTERPRISE: ResourceQuota(
                max_concurrent_tasks=100,
                max_memory_mb=8192,
                max_cpu_percent=95.0,
                max_tasks_per_hour=100000,
                rate_limit_per_second=1000.0
            )
        }
        return quotas.get(tier, ResourceQuota())

    def _get_features_for_tier(self, tier: TenantTier) -> Set[str]:
        """根據等級獲取啟用的功能"""
        features = {
            TenantTier.BASIC: {
                "basic_execution", "simple_monitoring"
            },
            TenantTier.PROFESSIONAL: {
                "basic_execution", "simple_monitoring",
                "advanced_retry", "resource_management",
                "audit_logs", "sla_monitoring"
            },
            TenantTier.ENTERPRISE: {
                "basic_execution", "simple_monitoring",
                "advanced_retry", "resource_management",
                "audit_logs", "sla_monitoring",
                "multi_tenancy", "high_availability",
                "custom_policies", "advanced_analytics"
            }
        }
        return features.get(tier, set())

    def get_tenant(self, tenant_id: str) -> Optional[TenantConfig]:
        """獲取租戶配置"""
        return self.tenants.get(tenant_id)

    # ========================================================================
    # 依賴管理
    # ========================================================================

    def add_dependency(
        self,
        component_id: str,
        depends_on: List[str],
        component_type: ComponentType = ComponentType.AGENT
    ) -> bool:
        """添加組件依賴"""
        try:
            # 檢測循環依賴
            if self._has_circular_dependency(component_id, depends_on):
                raise ValueError(f"循環依賴檢測: {component_id}")

            self.dependencies[component_id] = ComponentDependency(
                component_id=component_id,
                depends_on=depends_on,
                type=component_type
            )

            # 清除執行順序快取
            self.execution_order_cache.clear()

            logger.info(f"✅ 依賴已添加: {component_id} → {depends_on}")
            return True

        except ValueError as e:
            logger.error(f"❌ 依賴添加失敗: {e}")
            return False

    def _has_circular_dependency(
        self,
        component_id: str,
        new_dependencies: List[str],
        visited: Optional[Set[str]] = None
    ) -> bool:
        """檢測循環依賴"""
        if visited is None:
            visited = set()

        if component_id in visited:
            return True

        visited.add(component_id)

        for dep in new_dependencies:
            if dep in self.dependencies:
                dep_deps = self.dependencies[dep].depends_on
                if self._has_circular_dependency(dep, dep_deps, visited.copy()):
                    return True

        return False

    def resolve_execution_order(
        self,
        component_ids: List[str]
    ) -> List[str]:
        """解析執行順序（拓撲排序）"""
        cache_key = ",".join(sorted(component_ids))

        if cache_key in self.execution_order_cache:
            return self.execution_order_cache[cache_key]

        # 拓撲排序
        ordered = []
        processed = set()

        def process_component(comp_id: str):
            if comp_id in processed:
                return

            if comp_id in self.dependencies:
                for dep in self.dependencies[comp_id].depends_on:
                    if dep in component_ids:
                        process_component(dep)

            processed.add(comp_id)
            ordered.append(comp_id)

        for comp_id in component_ids:
            process_component(comp_id)

        self.execution_order_cache[cache_key] = ordered
        logger.info(f"✅ 執行順序已解析: {ordered}")

        return ordered

    # ========================================================================
    # 容錯和重試機制
    # ========================================================================

    async def execute_with_retry(
        self,
        func,
        component_id: str,
        tenant_id: str,
        max_retries: Optional[int] = None,
        **kwargs
    ) -> ExecutionResult:
        """帶重試的執行"""
        policy = self.retry_policies.get(
            component_id,
            RetryPolicy(max_retries=max_retries or 3)
        )

        start_time = datetime.now()
        last_error = None

        for attempt in range(policy.max_retries + 1):
            try:
                if attempt > 0:
                    delay = policy.get_delay(attempt - 1)
                    logger.info(f"⏳ 重試 {component_id} (第 {attempt} 次，延遲 {delay}s)")
                    await asyncio.sleep(delay)
                    self.metrics["total_retry_attempts"] += 1

                result = await func(**kwargs)

                return ExecutionResult(
                    component_id=component_id,
                    component_type=ComponentType.AGENT,
                    status=ExecutionStatus.SUCCESS,
                    start_time=start_time,
                    tenant_id=tenant_id,
                    end_time=datetime.now(),
                    output=result,
                    duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                    retry_count=attempt
                )

            except Exception as e:
                last_error = e
                logger.warning(f"⚠️  執行失敗 {component_id}: {e}")

                if attempt == policy.max_retries:
                    break

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() * 1000

        return ExecutionResult(
            component_id=component_id,
            component_type=ComponentType.AGENT,
            status=ExecutionStatus.FAILED,
            start_time=start_time,
            tenant_id=tenant_id,
            end_time=end_time,
            error=str(last_error),
            duration_ms=duration,
            retry_count=policy.max_retries
        )

    # ========================================================================
    # 資源管理
    # ========================================================================

    def _check_rate_limit(self, tenant_id: str) -> bool:
        """檢查速率限制"""
        if tenant_id not in self.tenants:
            return True

        tenant = self.tenants[tenant_id]
        rate_limit = tenant.quota.rate_limit_per_second

        now = datetime.now()
        if tenant_id in self.rate_limiters:
            count, last_reset = self.rate_limiters[tenant_id]

            if (now - last_reset).total_seconds() >= 1:
                # 重置計數器
                self.rate_limiters[tenant_id] = (1, now)
                return True
            else:
                if count < rate_limit:
                    self.rate_limiters[tenant_id] = (count + 1, last_reset)
                    return True
                return False
        else:
            self.rate_limiters[tenant_id] = (1, now)
            return True

    def check_resource_quota(
        self,
        tenant_id: str,
        resource_type: str = "tasks"
    ) -> bool:
        """檢查資源配額"""
        if tenant_id not in self.tenants:
            return True

        tenant = self.tenants[tenant_id]
        quota = tenant.quota

        if resource_type == "concurrent":
            active_count = len([
                t for t in self.active_tasks
                if t.startswith(tenant_id)
            ])
            return active_count < quota.max_concurrent_tasks

        return True

    # ========================================================================
    # 審計和合規
    # ========================================================================

    def _log_audit(
        self,
        tenant_id: str,
        action: str,
        component_id: str,
        status: str,
        error_msg: Optional[str] = None
    ):
        """記錄審計日誌"""
        audit_log = AuditLog(
            audit_id=f"audit-{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(),
            tenant_id=tenant_id,
            action=action,
            component_id=component_id,
            user_id=None,  # 可從上下文提取
            status=status,
            metadata={"error": error_msg} if error_msg else {}
        )

        self.audit_logs.append(audit_log)
        logger.debug(f"📋 審計: {action} on {component_id}")

    def get_audit_logs(
        self,
        tenant_id: str,
        hours: int = 24
    ) -> List[AuditLog]:
        """獲取審計日誌"""
        cutoff = datetime.now() - timedelta(hours=hours)

        return [
            log for log in self.audit_logs
            if log.tenant_id == tenant_id and log.timestamp >= cutoff
        ]

    # ========================================================================
    # 執行和監控
    # ========================================================================

    @with_audit_log
    async def execute_agent(
        self,
        agent_id: str,
        agent: Any,
        tenant_id: str,
        component_id: str = None
    ) -> ExecutionResult:
        """執行 Agent（含容錯）"""
        if not component_id:
            component_id = agent_id

        # 檢查資源配額
        if not self.check_resource_quota(tenant_id, "concurrent"):
            return ExecutionResult(
                component_id=component_id,
                component_type=ComponentType.AGENT,
                status=ExecutionStatus.FAILED,
                start_time=datetime.now(),
                tenant_id=tenant_id,
                error="Resource quota exceeded"
            )

        # 帶重試執行
        async def _execute():
            if hasattr(agent, 'start'):
                agent.start()
            return agent.execute() if hasattr(agent, 'execute') else None

        result = await self.execute_with_retry(
            _execute,
            component_id,
            tenant_id
        )

        # 更新指標
        self._update_metrics(result)

        return result

    def _update_metrics(self, result: ExecutionResult):
        """更新系統指標"""
        self.metrics["total_executions"] += 1

        if result.status == ExecutionStatus.SUCCESS:
            self.metrics["successful_executions"] += 1
        elif result.status == ExecutionStatus.FAILED:
            self.metrics["failed_executions"] += 1

        # 計算平均執行時間
        total_time = self.metrics["average_execution_time_ms"]
        avg_time = (
            (total_time * (self.metrics["total_executions"] - 1) + result.duration_ms) /
            self.metrics["total_executions"]
        )
        self.metrics["average_execution_time_ms"] = avg_time

    def get_metrics(self) -> Dict[str, Any]:
        """獲取系統指標"""
        return {
            **self.metrics,
            "success_rate": (
                self.metrics["successful_executions"] /
                max(self.metrics["total_executions"], 1) * 100
            ),
            "total_audit_logs": len(self.audit_logs),
            "active_tasks": len(self.active_tasks),
            "registered_tenants": len(self.tenants)
        }

    def get_tenant_health(self, tenant_id: str) -> Dict[str, Any]:
        """獲取租戶健康狀態"""
        tenant_logs = [
            log for log in self.execution_results
            if log.tenant_id == tenant_id
        ]

        if not tenant_logs:
            return {"status": "no_data"}

        successful = len([l for l in tenant_logs if l.status == ExecutionStatus.SUCCESS])
        total = len(tenant_logs)

        return {
            "tenant_id": tenant_id,
            "total_executions": total,
            "successful": successful,
            "uptime_percent": (successful / max(total, 1)) * 100,
            "last_execution": tenant_logs[-1].end_time.isoformat() if tenant_logs else None
        }


# 導出類
__all__ = [
    "EnterpriseSynergyMeshOrchestrator",
    "TenantConfig",
    "TenantTier",
    "ResourceQuota",
    "RetryPolicy",
    "ExecutionResult",
    "AuditLog",
    "ExecutionStatus",
    "ComponentType"
]
