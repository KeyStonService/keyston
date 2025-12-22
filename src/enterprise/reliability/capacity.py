"""
Capacity Management

Manages capacity and cost control:
- Per-org analysis quotas
- Concurrency limits
- Storage quotas
- Cost estimation and tracking

Prevents cost overruns and ensures fair resource usage.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of resources for capacity planning"""
    ANALYSIS_RUNS = "analysis_runs"
    CONCURRENT_RUNS = "concurrent_runs"
    STORAGE_GB = "storage_gb"
    API_CALLS = "api_calls"
    COMPUTE_HOURS = "compute_hours"
    EGRESS_GB = "egress_gb"


class PlanTier(Enum):
    """Subscription plan tiers"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class CapacityPlan:
    """
    Capacity plan for an organization

    Defines resource limits based on subscription tier.
    """
    tier: PlanTier = PlanTier.FREE

    # Analysis limits
    monthly_analysis_limit: int = 100
    concurrent_runs_limit: int = 2

    # Storage limits
    storage_gb_limit: int = 1
    artifact_retention_days: int = 30

    # API limits
    api_calls_per_minute: int = 60
    api_calls_per_hour: int = 1000

    # Compute limits
    compute_hours_per_month: float = 10.0
    max_run_duration_minutes: int = 30

    # Network limits
    egress_gb_per_month: float = 10.0

    # Features
    advanced_analytics: bool = False
    custom_policies: bool = False
    sso_enabled: bool = False
    priority_support: bool = False


# Predefined plans
CAPACITY_PLANS: dict[PlanTier, CapacityPlan] = {
    PlanTier.FREE: CapacityPlan(
        tier=PlanTier.FREE,
        monthly_analysis_limit=100,
        concurrent_runs_limit=2,
        storage_gb_limit=1,
        artifact_retention_days=7,
        api_calls_per_minute=30,
        api_calls_per_hour=500,
        compute_hours_per_month=5.0,
        max_run_duration_minutes=10,
        egress_gb_per_month=5.0,
    ),
    PlanTier.STARTER: CapacityPlan(
        tier=PlanTier.STARTER,
        monthly_analysis_limit=1000,
        concurrent_runs_limit=5,
        storage_gb_limit=10,
        artifact_retention_days=30,
        api_calls_per_minute=60,
        api_calls_per_hour=2000,
        compute_hours_per_month=50.0,
        max_run_duration_minutes=30,
        egress_gb_per_month=50.0,
        custom_policies=True,
    ),
    PlanTier.PROFESSIONAL: CapacityPlan(
        tier=PlanTier.PROFESSIONAL,
        monthly_analysis_limit=10000,
        concurrent_runs_limit=20,
        storage_gb_limit=100,
        artifact_retention_days=90,
        api_calls_per_minute=120,
        api_calls_per_hour=5000,
        compute_hours_per_month=500.0,
        max_run_duration_minutes=60,
        egress_gb_per_month=200.0,
        advanced_analytics=True,
        custom_policies=True,
    ),
    PlanTier.ENTERPRISE: CapacityPlan(
        tier=PlanTier.ENTERPRISE,
        monthly_analysis_limit=100000,
        concurrent_runs_limit=100,
        storage_gb_limit=1000,
        artifact_retention_days=365,
        api_calls_per_minute=1000,
        api_calls_per_hour=50000,
        compute_hours_per_month=5000.0,
        max_run_duration_minutes=120,
        egress_gb_per_month=1000.0,
        advanced_analytics=True,
        custom_policies=True,
        sso_enabled=True,
        priority_support=True,
    ),
}


@dataclass
class UsageForecast:
    """
    Usage forecast for capacity planning
    """
    resource_type: ResourceType
    current_usage: float
    forecasted_usage: float
    forecast_period_days: int = 30

    # Trend
    trend: str = "stable"  # increasing, stable, decreasing
    growth_rate_percent: float = 0.0

    # Capacity
    limit: float = 0.0
    usage_percent: float = 0.0
    forecasted_percent: float = 0.0

    # Alerts
    will_exceed: bool = False
    days_until_exceeded: int | None = None

    @property
    def is_at_risk(self) -> bool:
        """Check if approaching limit"""
        return self.usage_percent > 80.0 or self.will_exceed


@dataclass
class CostEstimate:
    """
    Cost estimate for an organization
    """
    org_id: UUID = field(default_factory=uuid4)
    period_start: datetime = field(default_factory=datetime.utcnow)
    period_end: datetime = field(default_factory=datetime.utcnow)

    # Base cost
    base_cost: float = 0.0
    plan_tier: PlanTier = PlanTier.FREE

    # Usage-based costs
    overage_analysis_cost: float = 0.0
    overage_storage_cost: float = 0.0
    overage_compute_cost: float = 0.0
    overage_egress_cost: float = 0.0

    # Total
    total_cost: float = 0.0

    # Usage details
    usage_breakdown: dict[str, float] = field(default_factory=dict)


@dataclass
class UsageRecord:
    """Record of resource usage"""
    org_id: UUID
    resource_type: ResourceType
    amount: float
    recorded_at: datetime = field(default_factory=datetime.utcnow)
    period: str = "monthly"  # hourly, daily, monthly


class UsageStorage(Protocol):
    """Interface for usage data storage"""

    async def record_usage(self, record: UsageRecord) -> None:
        ...

    async def get_usage(
        self,
        org_id: UUID,
        resource_type: ResourceType,
        start_time: datetime,
        end_time: datetime,
    ) -> float:
        ...

    async def get_usage_history(
        self,
        org_id: UUID,
        resource_type: ResourceType,
        days: int = 30,
    ) -> list[UsageRecord]:
        ...


class PlanProvider(Protocol):
    """Interface for getting org's capacity plan"""

    async def get_plan(self, org_id: UUID) -> CapacityPlan:
        ...


@dataclass
class CapacityManager:
    """
    Capacity Manager

    Manages capacity planning and cost control:
    - Usage tracking
    - Quota enforcement
    - Cost estimation
    - Capacity forecasting
    """

    usage_storage: UsageStorage | None = None
    plan_provider: PlanProvider | None = None

    # Cost rates ($ per unit)
    rates: dict[str, float] = field(default_factory=lambda: {
        "analysis_overage": 0.01,     # $0.01 per analysis over limit
        "storage_gb": 0.10,           # $0.10 per GB per month
        "compute_hour": 0.50,         # $0.50 per compute hour
        "egress_gb": 0.05,            # $0.05 per GB egress
    })

    # Plan base costs
    plan_costs: dict[PlanTier, float] = field(default_factory=lambda: {
        PlanTier.FREE: 0.0,
        PlanTier.STARTER: 49.0,
        PlanTier.PROFESSIONAL: 199.0,
        PlanTier.ENTERPRISE: 999.0,
    })

    # ------------------------------------------------------------------
    # Usage Tracking
    # ------------------------------------------------------------------

    async def record_usage(
        self,
        org_id: UUID,
        resource_type: ResourceType,
        amount: float,
    ) -> None:
        """Record resource usage"""
        if self.usage_storage:
            record = UsageRecord(
                org_id=org_id,
                resource_type=resource_type,
                amount=amount,
            )
            await self.usage_storage.record_usage(record)

    async def get_current_usage(
        self,
        org_id: UUID,
        resource_type: ResourceType,
    ) -> float:
        """Get current month's usage"""
        if not self.usage_storage:
            return 0.0

        now = datetime.utcnow()
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        return await self.usage_storage.get_usage(
            org_id,
            resource_type,
            start,
            now,
        )

    async def get_usage_summary(
        self,
        org_id: UUID,
    ) -> dict[str, Any]:
        """Get usage summary for all resource types"""
        plan = await self._get_plan(org_id)

        summary = {
            "plan_tier": plan.tier.value,
            "resources": {},
        }

        resource_limits = {
            ResourceType.ANALYSIS_RUNS: plan.monthly_analysis_limit,
            ResourceType.STORAGE_GB: plan.storage_gb_limit,
            ResourceType.COMPUTE_HOURS: plan.compute_hours_per_month,
            ResourceType.EGRESS_GB: plan.egress_gb_per_month,
        }

        for resource_type, limit in resource_limits.items():
            usage = await self.get_current_usage(org_id, resource_type)
            summary["resources"][resource_type.value] = {
                "usage": usage,
                "limit": limit,
                "percentage": (usage / limit * 100) if limit > 0 else 0,
                "remaining": max(0, limit - usage),
            }

        return summary

    # ------------------------------------------------------------------
    # Quota Checking
    # ------------------------------------------------------------------

    async def check_quota(
        self,
        org_id: UUID,
        resource_type: ResourceType,
        amount: float = 1.0,
    ) -> tuple[bool, str]:
        """
        Check if usage would exceed quota

        Returns (allowed, message)
        """
        plan = await self._get_plan(org_id)
        current_usage = await self.get_current_usage(org_id, resource_type)

        limits = {
            ResourceType.ANALYSIS_RUNS: plan.monthly_analysis_limit,
            ResourceType.STORAGE_GB: plan.storage_gb_limit,
            ResourceType.COMPUTE_HOURS: plan.compute_hours_per_month,
            ResourceType.EGRESS_GB: plan.egress_gb_per_month,
        }

        limit = limits.get(resource_type, float("inf"))

        if current_usage + amount > limit:
            return False, (
                f"Quota exceeded for {resource_type.value}: "
                f"{current_usage + amount:.1f}/{limit:.1f}"
            )

        # Warn if approaching limit
        if current_usage + amount > limit * 0.8:
            logger.warning(
                f"Approaching quota limit: org={org_id} "
                f"resource={resource_type.value} "
                f"usage={current_usage + amount:.1f}/{limit:.1f}"
            )

        return True, ""

    # ------------------------------------------------------------------
    # Capacity Forecasting
    # ------------------------------------------------------------------

    async def forecast_usage(
        self,
        org_id: UUID,
        resource_type: ResourceType,
        forecast_days: int = 30,
    ) -> UsageForecast:
        """
        Forecast future usage based on historical trends
        """
        plan = await self._get_plan(org_id)

        # Get historical usage
        history = []
        if self.usage_storage:
            history = await self.usage_storage.get_usage_history(
                org_id,
                resource_type,
                days=30,
            )

        current_usage = await self.get_current_usage(org_id, resource_type)

        # Calculate trend
        if len(history) >= 7:
            # Simple linear trend calculation
            recent_avg = sum(r.amount for r in history[-7:]) / 7
            older_avg = sum(r.amount for r in history[:-7]) / max(1, len(history) - 7)

            if older_avg > 0:
                growth_rate = (recent_avg - older_avg) / older_avg * 100
            else:
                growth_rate = 0.0

            if growth_rate > 5:
                trend = "increasing"
            elif growth_rate < -5:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
            growth_rate = 0.0

        # Forecast
        daily_rate = current_usage / max(1, datetime.utcnow().day)
        forecasted = daily_rate * 30 * (1 + growth_rate / 100)

        # Get limit
        limits = {
            ResourceType.ANALYSIS_RUNS: plan.monthly_analysis_limit,
            ResourceType.STORAGE_GB: plan.storage_gb_limit,
            ResourceType.COMPUTE_HOURS: plan.compute_hours_per_month,
            ResourceType.EGRESS_GB: plan.egress_gb_per_month,
        }
        limit = limits.get(resource_type, 0)

        # Calculate days until exceeded
        will_exceed = forecasted > limit
        days_until_exceeded = None
        if will_exceed and daily_rate > 0:
            remaining = limit - current_usage
            days_until_exceeded = int(remaining / daily_rate) if remaining > 0 else 0

        return UsageForecast(
            resource_type=resource_type,
            current_usage=current_usage,
            forecasted_usage=forecasted,
            forecast_period_days=forecast_days,
            trend=trend,
            growth_rate_percent=growth_rate,
            limit=float(limit),
            usage_percent=(current_usage / limit * 100) if limit > 0 else 0,
            forecasted_percent=(forecasted / limit * 100) if limit > 0 else 0,
            will_exceed=will_exceed,
            days_until_exceeded=days_until_exceeded,
        )

    async def get_capacity_report(
        self,
        org_id: UUID,
    ) -> dict[str, Any]:
        """Get comprehensive capacity report"""
        forecasts = {}

        for resource_type in [
            ResourceType.ANALYSIS_RUNS,
            ResourceType.STORAGE_GB,
            ResourceType.COMPUTE_HOURS,
        ]:
            forecast = await self.forecast_usage(org_id, resource_type)
            forecasts[resource_type.value] = {
                "current": forecast.current_usage,
                "forecasted": forecast.forecasted_usage,
                "limit": forecast.limit,
                "trend": forecast.trend,
                "at_risk": forecast.is_at_risk,
                "will_exceed": forecast.will_exceed,
                "days_until_exceeded": forecast.days_until_exceeded,
            }

        return {
            "org_id": str(org_id),
            "generated_at": datetime.utcnow().isoformat(),
            "forecasts": forecasts,
            "recommendations": self._generate_recommendations(forecasts),
        }

    def _generate_recommendations(
        self,
        forecasts: dict[str, dict[str, Any]],
    ) -> list[str]:
        """Generate capacity recommendations"""
        recommendations = []

        for resource, data in forecasts.items():
            if data.get("will_exceed"):
                recommendations.append(
                    f"Consider upgrading plan: {resource} is projected to exceed limit "
                    f"in {data.get('days_until_exceeded', 'N/A')} days"
                )
            elif data.get("at_risk"):
                recommendations.append(
                    f"Monitor {resource}: usage at {data.get('forecasted', 0):.0f}% of limit"
                )

        return recommendations

    # ------------------------------------------------------------------
    # Cost Estimation
    # ------------------------------------------------------------------

    async def estimate_cost(
        self,
        org_id: UUID,
        period_start: datetime | None = None,
        period_end: datetime | None = None,
    ) -> CostEstimate:
        """
        Estimate cost for an organization

        Includes base plan cost and any overage charges.
        """
        plan = await self._get_plan(org_id)

        if period_start is None:
            period_start = datetime.utcnow().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
        if period_end is None:
            period_end = datetime.utcnow()

        estimate = CostEstimate(
            org_id=org_id,
            period_start=period_start,
            period_end=period_end,
            plan_tier=plan.tier,
            base_cost=self.plan_costs.get(plan.tier, 0.0),
        )

        # Calculate overages
        analysis_usage = await self.get_current_usage(org_id, ResourceType.ANALYSIS_RUNS)
        if analysis_usage > plan.monthly_analysis_limit:
            overage = analysis_usage - plan.monthly_analysis_limit
            estimate.overage_analysis_cost = overage * self.rates["analysis_overage"]
            estimate.usage_breakdown["analysis_overage"] = overage

        storage_usage = await self.get_current_usage(org_id, ResourceType.STORAGE_GB)
        if storage_usage > plan.storage_gb_limit:
            overage = storage_usage - plan.storage_gb_limit
            estimate.overage_storage_cost = overage * self.rates["storage_gb"]
            estimate.usage_breakdown["storage_overage_gb"] = overage

        compute_usage = await self.get_current_usage(org_id, ResourceType.COMPUTE_HOURS)
        if compute_usage > plan.compute_hours_per_month:
            overage = compute_usage - plan.compute_hours_per_month
            estimate.overage_compute_cost = overage * self.rates["compute_hour"]
            estimate.usage_breakdown["compute_overage_hours"] = overage

        egress_usage = await self.get_current_usage(org_id, ResourceType.EGRESS_GB)
        if egress_usage > plan.egress_gb_per_month:
            overage = egress_usage - plan.egress_gb_per_month
            estimate.overage_egress_cost = overage * self.rates["egress_gb"]
            estimate.usage_breakdown["egress_overage_gb"] = overage

        # Total
        estimate.total_cost = (
            estimate.base_cost
            + estimate.overage_analysis_cost
            + estimate.overage_storage_cost
            + estimate.overage_compute_cost
            + estimate.overage_egress_cost
        )

        return estimate

    # ------------------------------------------------------------------
    # Private Methods
    # ------------------------------------------------------------------

    async def _get_plan(self, org_id: UUID) -> CapacityPlan:
        """Get capacity plan for an organization"""
        if self.plan_provider:
            return await self.plan_provider.get_plan(org_id)

        # Default to free plan
        return CAPACITY_PLANS[PlanTier.FREE]
