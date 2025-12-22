"""
Resource Quota Manager

Manages resource quotas to prevent:
- CPU/Memory abuse by malicious repos
- Cost overruns from runaway analysis
- Platform instability from resource exhaustion

Per-org quotas ensure fair resource distribution.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Protocol
from uuid import UUID

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of resources that can be quotad"""
    CPU_SECONDS = "cpu_seconds"
    MEMORY_BYTES = "memory_bytes"
    ANALYSIS_COUNT = "analysis_count"
    CONCURRENT_RUNS = "concurrent_runs"
    STORAGE_BYTES = "storage_bytes"
    NETWORK_EGRESS_BYTES = "network_egress_bytes"
    API_CALLS = "api_calls"


class QuotaPeriod(Enum):
    """Quota period types"""
    HOURLY = "hourly"
    DAILY = "daily"
    MONTHLY = "monthly"
    UNLIMITED = "unlimited"


class QuotaExceededError(Exception):
    """Raised when a quota is exceeded"""
    def __init__(
        self,
        resource_type: ResourceType,
        current: int,
        limit: int,
        period: QuotaPeriod,
        resets_at: datetime | None = None,
    ):
        self.resource_type = resource_type
        self.current = current
        self.limit = limit
        self.period = period
        self.resets_at = resets_at

        super().__init__(
            f"Quota exceeded for {resource_type.value}: "
            f"{current}/{limit} ({period.value})"
            f"{f', resets at {resets_at}' if resets_at else ''}"
        )


@dataclass
class ResourceQuota:
    """
    Resource quota definition

    Defines limits for a specific resource type.
    """
    resource_type: ResourceType
    limit: int
    period: QuotaPeriod = QuotaPeriod.MONTHLY

    # Soft limit triggers warnings
    soft_limit: int | None = None

    # Burst allowance for temporary spikes
    burst_limit: int | None = None
    burst_window_seconds: int = 60


@dataclass
class QuotaUsage:
    """Current usage against a quota"""
    resource_type: ResourceType
    current: int
    limit: int
    period: QuotaPeriod
    period_start: datetime
    period_end: datetime | None = None

    @property
    def percentage_used(self) -> float:
        """Percentage of quota used"""
        if self.limit == 0:
            return 100.0
        return (self.current / self.limit) * 100

    @property
    def remaining(self) -> int:
        """Remaining quota"""
        return max(0, self.limit - self.current)

    @property
    def is_exceeded(self) -> bool:
        """Check if quota is exceeded"""
        return self.current >= self.limit


@dataclass
class OrgQuotaConfig:
    """
    Quota configuration for an organization

    Different plans have different quotas.
    """
    org_id: UUID
    plan: str = "free"

    # Analysis quotas
    max_analysis_per_month: int = 100
    max_concurrent_runs: int = 2

    # Resource quotas
    cpu_seconds_per_month: int = 36000  # 10 hours
    memory_limit_per_run: str = "512Mi"
    storage_bytes: int = 1073741824  # 1 GB

    # API quotas
    api_calls_per_hour: int = 1000
    api_calls_per_minute: int = 100

    # Network quotas
    network_egress_bytes_per_month: int = 10737418240  # 10 GB

    # Custom quotas
    custom_quotas: dict[str, int] = field(default_factory=dict)


class QuotaStorage(Protocol):
    """Storage interface for quota tracking"""

    async def get_usage(
        self,
        org_id: UUID,
        resource_type: ResourceType,
        period: QuotaPeriod,
        period_start: datetime,
    ) -> int:
        """Get current usage for a resource"""
        ...

    async def increment_usage(
        self,
        org_id: UUID,
        resource_type: ResourceType,
        period: QuotaPeriod,
        period_start: datetime,
        amount: int,
    ) -> int:
        """Increment usage, return new value"""
        ...

    async def get_concurrent_count(
        self,
        org_id: UUID,
    ) -> int:
        """Get count of concurrent runs"""
        ...

    async def set_concurrent_count(
        self,
        org_id: UUID,
        count: int,
    ) -> None:
        """Set concurrent run count"""
        ...


class QuotaConfigProvider(Protocol):
    """Provider for quota configurations"""

    async def get_config(self, org_id: UUID) -> OrgQuotaConfig:
        """Get quota config for an organization"""
        ...


@dataclass
class ResourceQuotaManager:
    """
    Resource Quota Manager

    Tracks and enforces resource quotas per organization.
    """

    storage: QuotaStorage
    config_provider: QuotaConfigProvider

    # Cache for quota configs
    _config_cache: dict[str, tuple[OrgQuotaConfig, datetime]] = field(default_factory=dict)
    _cache_ttl_seconds: int = 300

    # ------------------------------------------------------------------
    # Quota Checking
    # ------------------------------------------------------------------

    async def check_quota(
        self,
        org_id: UUID,
        resource_type: ResourceType,
        amount: int = 1,
    ) -> bool:
        """
        Check if an operation would exceed quota

        Args:
            org_id: Organization ID
            resource_type: Type of resource
            amount: Amount to check (e.g., 1 for one analysis)

        Returns:
            True if within quota, raises QuotaExceededError if not
        """
        config = await self._get_config(org_id)
        quota = self._get_quota_for_resource(config, resource_type)

        if quota.period == QuotaPeriod.UNLIMITED:
            return True

        period_start = self._get_period_start(quota.period)
        current_usage = await self.storage.get_usage(
            org_id, resource_type, quota.period, period_start
        )

        if current_usage + amount > quota.limit:
            raise QuotaExceededError(
                resource_type=resource_type,
                current=current_usage,
                limit=quota.limit,
                period=quota.period,
                resets_at=self._get_period_end(quota.period, period_start),
            )

        # Check soft limit (warning)
        if quota.soft_limit and current_usage + amount > quota.soft_limit:
            logger.warning(
                f"Quota soft limit exceeded: org={org_id} "
                f"resource={resource_type.value} "
                f"usage={current_usage + amount}/{quota.limit}"
            )

        return True

    async def check_concurrent_limit(
        self,
        org_id: UUID,
    ) -> bool:
        """
        Check if concurrent run limit is exceeded

        Returns:
            True if within limit
        """
        config = await self._get_config(org_id)
        current = await self.storage.get_concurrent_count(org_id)

        if current >= config.max_concurrent_runs:
            raise QuotaExceededError(
                resource_type=ResourceType.CONCURRENT_RUNS,
                current=current,
                limit=config.max_concurrent_runs,
                period=QuotaPeriod.UNLIMITED,
            )

        return True

    # ------------------------------------------------------------------
    # Quota Consumption
    # ------------------------------------------------------------------

    async def consume(
        self,
        org_id: UUID,
        resource_type: ResourceType,
        amount: int = 1,
    ) -> QuotaUsage:
        """
        Consume quota (increment usage)

        Should be called after check_quota succeeds.
        """
        config = await self._get_config(org_id)
        quota = self._get_quota_for_resource(config, resource_type)

        if quota.period == QuotaPeriod.UNLIMITED:
            return QuotaUsage(
                resource_type=resource_type,
                current=0,
                limit=0,
                period=quota.period,
                period_start=datetime.utcnow(),
            )

        period_start = self._get_period_start(quota.period)

        new_usage = await self.storage.increment_usage(
            org_id, resource_type, quota.period, period_start, amount
        )

        logger.debug(
            f"Quota consumed: org={org_id} resource={resource_type.value} "
            f"amount={amount} new_usage={new_usage}/{quota.limit}"
        )

        return QuotaUsage(
            resource_type=resource_type,
            current=new_usage,
            limit=quota.limit,
            period=quota.period,
            period_start=period_start,
            period_end=self._get_period_end(quota.period, period_start),
        )

    async def acquire_concurrent_slot(
        self,
        org_id: UUID,
    ) -> bool:
        """Acquire a concurrent run slot"""
        await self.check_concurrent_limit(org_id)

        current = await self.storage.get_concurrent_count(org_id)
        await self.storage.set_concurrent_count(org_id, current + 1)

        logger.debug(f"Concurrent slot acquired: org={org_id} count={current + 1}")

        return True

    async def release_concurrent_slot(
        self,
        org_id: UUID,
    ) -> None:
        """Release a concurrent run slot"""
        current = await self.storage.get_concurrent_count(org_id)
        new_count = max(0, current - 1)
        await self.storage.set_concurrent_count(org_id, new_count)

        logger.debug(f"Concurrent slot released: org={org_id} count={new_count}")

    # ------------------------------------------------------------------
    # Quota Queries
    # ------------------------------------------------------------------

    async def get_usage(
        self,
        org_id: UUID,
        resource_type: ResourceType,
    ) -> QuotaUsage:
        """Get current usage for a resource"""
        config = await self._get_config(org_id)
        quota = self._get_quota_for_resource(config, resource_type)

        if quota.period == QuotaPeriod.UNLIMITED:
            return QuotaUsage(
                resource_type=resource_type,
                current=0,
                limit=0,
                period=quota.period,
                period_start=datetime.utcnow(),
            )

        period_start = self._get_period_start(quota.period)
        current = await self.storage.get_usage(
            org_id, resource_type, quota.period, period_start
        )

        return QuotaUsage(
            resource_type=resource_type,
            current=current,
            limit=quota.limit,
            period=quota.period,
            period_start=period_start,
            period_end=self._get_period_end(quota.period, period_start),
        )

    async def get_all_usage(
        self,
        org_id: UUID,
    ) -> dict[str, QuotaUsage]:
        """Get usage for all resource types"""
        result = {}

        for resource_type in ResourceType:
            try:
                usage = await self.get_usage(org_id, resource_type)
                result[resource_type.value] = usage
            except Exception:
                pass  # Skip resources without quotas

        return result

    async def get_remaining(
        self,
        org_id: UUID,
        resource_type: ResourceType,
    ) -> int:
        """Get remaining quota"""
        usage = await self.get_usage(org_id, resource_type)
        return usage.remaining

    # ------------------------------------------------------------------
    # Private Methods
    # ------------------------------------------------------------------

    async def _get_config(self, org_id: UUID) -> OrgQuotaConfig:
        """Get quota config with caching"""
        cache_key = str(org_id)
        now = datetime.utcnow()

        if cache_key in self._config_cache:
            config, cached_at = self._config_cache[cache_key]
            if (now - cached_at).total_seconds() < self._cache_ttl_seconds:
                return config

        config = await self.config_provider.get_config(org_id)
        self._config_cache[cache_key] = (config, now)

        return config

    def _get_quota_for_resource(
        self,
        config: OrgQuotaConfig,
        resource_type: ResourceType,
    ) -> ResourceQuota:
        """Get quota definition for a resource type"""
        quotas = {
            ResourceType.ANALYSIS_COUNT: ResourceQuota(
                resource_type=ResourceType.ANALYSIS_COUNT,
                limit=config.max_analysis_per_month,
                period=QuotaPeriod.MONTHLY,
                soft_limit=int(config.max_analysis_per_month * 0.8),
            ),
            ResourceType.CONCURRENT_RUNS: ResourceQuota(
                resource_type=ResourceType.CONCURRENT_RUNS,
                limit=config.max_concurrent_runs,
                period=QuotaPeriod.UNLIMITED,
            ),
            ResourceType.CPU_SECONDS: ResourceQuota(
                resource_type=ResourceType.CPU_SECONDS,
                limit=config.cpu_seconds_per_month,
                period=QuotaPeriod.MONTHLY,
            ),
            ResourceType.STORAGE_BYTES: ResourceQuota(
                resource_type=ResourceType.STORAGE_BYTES,
                limit=config.storage_bytes,
                period=QuotaPeriod.UNLIMITED,
            ),
            ResourceType.API_CALLS: ResourceQuota(
                resource_type=ResourceType.API_CALLS,
                limit=config.api_calls_per_hour,
                period=QuotaPeriod.HOURLY,
            ),
            ResourceType.NETWORK_EGRESS_BYTES: ResourceQuota(
                resource_type=ResourceType.NETWORK_EGRESS_BYTES,
                limit=config.network_egress_bytes_per_month,
                period=QuotaPeriod.MONTHLY,
            ),
        }

        return quotas.get(
            resource_type,
            ResourceQuota(
                resource_type=resource_type,
                limit=0,
                period=QuotaPeriod.UNLIMITED,
            ),
        )

    def _get_period_start(self, period: QuotaPeriod) -> datetime:
        """Get start of current period"""
        now = datetime.utcnow()

        if period == QuotaPeriod.HOURLY:
            return now.replace(minute=0, second=0, microsecond=0)
        elif period == QuotaPeriod.DAILY:
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == QuotaPeriod.MONTHLY:
            return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        return now

    def _get_period_end(
        self,
        period: QuotaPeriod,
        period_start: datetime,
    ) -> datetime | None:
        """Get end of period"""
        if period == QuotaPeriod.HOURLY:
            return period_start + timedelta(hours=1)
        elif period == QuotaPeriod.DAILY:
            return period_start + timedelta(days=1)
        elif period == QuotaPeriod.MONTHLY:
            # Approximate - 30 days
            return period_start + timedelta(days=30)

        return None
