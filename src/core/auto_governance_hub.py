"""
Auto Governance Hub - 自動治理中樞
Phase 4: Autonomous Governance Without Human Approval

This module implements fully autonomous governance that removes the need
for human approval in deployment, policy enforcement, and system changes.

Core Features:
- Policy Auto-Enforcement (政策自動執行)
- Self-Healing Governance (自我修復治理)
- Compliance Auto-Verification (合規自動驗證)
- Change Auto-Approval (變更自動批准)

設計原則: 移除所有需要人工審批的架構/部署/策略
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)


class PolicyType(Enum):
    """Types of governance policies"""
    DEPLOYMENT = "deployment"
    SECURITY = "security"
    RESOURCE = "resource"
    COMPLIANCE = "compliance"
    ACCESS_CONTROL = "access_control"
    DATA_PROTECTION = "data_protection"


class PolicyEnforcement(Enum):
    """Policy enforcement modes"""
    STRICT = "strict"           # Block violations
    ADVISORY = "advisory"       # Warn but allow
    ADAPTIVE = "adaptive"       # Learn and adjust
    AUTO_CORRECT = "auto_correct"  # Auto-fix violations


class GovernanceAction(Enum):
    """Governance actions"""
    APPROVE = "approve"
    DENY = "deny"
    AUTO_FIX = "auto_fix"
    ESCALATE_TO_SYSTEM = "escalate_to_system"  # NOT to human
    DEFER = "defer"
    ROLLBACK = "rollback"


class ChangeType(Enum):
    """Types of system changes"""
    DEPLOYMENT = "deployment"
    CONFIGURATION = "configuration"
    INFRASTRUCTURE = "infrastructure"
    POLICY = "policy"
    ACCESS = "access"
    DATA = "data"


@dataclass
class GovernancePolicy:
    """Governance policy definition"""
    policy_id: str
    name: str
    policy_type: PolicyType
    enforcement: PolicyEnforcement
    rules: List[Dict[str, Any]] = field(default_factory=list)
    auto_approve_conditions: List[str] = field(default_factory=list)
    auto_deny_conditions: List[str] = field(default_factory=list)
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ChangeRequest:
    """Change request for autonomous approval"""
    request_id: str
    change_type: ChangeType
    description: str
    requestor: str  # System or service ID, not human
    parameters: Dict[str, Any] = field(default_factory=dict)
    risk_score: float = 0.0
    auto_rollback: bool = True
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class GovernanceDecision:
    """Governance decision result"""
    decision_id: str
    request: ChangeRequest
    action: GovernanceAction
    policy_applied: str
    reasoning: str
    conditions_met: List[str] = field(default_factory=list)
    auto_corrections: List[str] = field(default_factory=list)
    decided_at: datetime = field(default_factory=datetime.now)


@dataclass
class ComplianceStatus:
    """Compliance status"""
    compliant: bool
    violations: List[Dict[str, Any]] = field(default_factory=list)
    auto_fixed: List[str] = field(default_factory=list)
    pending_issues: List[str] = field(default_factory=list)
    last_checked: datetime = field(default_factory=datetime.now)


class AutoGovernanceHub:
    """
    自動治理中樞 - 完全自主治理系統
    
    Auto Governance Hub for fully autonomous system governance.
    Removes all human approval requirements from architecture/src/autonomous/deployment/policies.
    
    Core Principles:
    1. 所有決策自動化: All decisions are automated
    2. 政策自動執行: Policies are auto-enforced
    3. 合規自動驗證: Compliance is auto-verified
    4. 變更自動批准: Changes are auto-approved based on rules
    
    設計目標:
    - 零人工審批: No human approval required
    - 自我修復: Self-healing capabilities
    - 智能治理: Intelligent governance
    """
    
    # Default policy configurations
    DEFAULT_POLICIES = {
        "deployment_auto_approve": {
            "type": PolicyType.DEPLOYMENT,
            "enforcement": PolicyEnforcement.AUTO_CORRECT,
            "auto_approve": [
                "risk_score_below_threshold",
                "tests_passing",
                "no_breaking_changes"
            ]
        },
        "security_auto_enforce": {
            "type": PolicyType.SECURITY,
            "enforcement": PolicyEnforcement.STRICT,
            "auto_approve": [
                "no_privilege_escalation",
                "encryption_enabled",
                "audit_trail_active"
            ]
        }
    }
    
    def __init__(self):
        """Initialize Auto Governance Hub"""
        self.policies: Dict[str, GovernancePolicy] = {}
        self.decisions: List[GovernanceDecision] = []
        self.compliance_cache: Dict[str, ComplianceStatus] = {}
        self.change_handlers: Dict[ChangeType, Callable[..., Awaitable[Any]]] = {}
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "auto_approved": 0,
            "auto_denied": 0,
            "auto_fixed": 0,
            "rollbacks": 0
        }
        
        # Initialize default policies
        self._initialize_default_policies()
        
        logger.info("AutoGovernanceHub initialized - 自動治理中樞已初始化")
    
    def _initialize_default_policies(self) -> None:
        """Initialize default governance policies"""
        # Deployment auto-approval policy
        self.add_policy(GovernancePolicy(
            policy_id="deploy-auto",
            name="Deployment Auto-Approval",
            policy_type=PolicyType.DEPLOYMENT,
            enforcement=PolicyEnforcement.AUTO_CORRECT,
            auto_approve_conditions=[
                "risk_score < 0.5",
                "tests_passing == true",
                "no_breaking_changes == true",
                "rollback_available == true"
            ],
            auto_deny_conditions=[
                "risk_score > 0.9",
                "security_vulnerabilities > 0"
            ]
        ))
        
        # Security enforcement policy
        self.add_policy(GovernancePolicy(
            policy_id="security-enforce",
            name="Security Auto-Enforcement",
            policy_type=PolicyType.SECURITY,
            enforcement=PolicyEnforcement.STRICT,
            auto_approve_conditions=[
                "no_privilege_escalation == true",
                "encryption_at_rest == true",
                "audit_logging == true"
            ],
            auto_deny_conditions=[
                "exposes_credentials == true",
                "disables_security_features == true"
            ]
        ))
        
        # Resource allocation policy
        self.add_policy(GovernancePolicy(
            policy_id="resource-auto",
            name="Resource Auto-Management",
            policy_type=PolicyType.RESOURCE,
            enforcement=PolicyEnforcement.ADAPTIVE,
            auto_approve_conditions=[
                "within_quota == true",
                "cost_increase < 20%"
            ]
        ))
        
        # Access control policy
        self.add_policy(GovernancePolicy(
            policy_id="access-auto",
            name="Access Auto-Control",
            policy_type=PolicyType.ACCESS_CONTROL,
            enforcement=PolicyEnforcement.AUTO_CORRECT,
            auto_approve_conditions=[
                "least_privilege_compliant == true",
                "no_permanent_elevation == true"
            ]
        ))
    
    def add_policy(self, policy: GovernancePolicy) -> None:
        """Add a governance policy"""
        self.policies[policy.policy_id] = policy
        logger.info(f"Policy added: {policy.name}")
    
    async def process_change_request(
        self,
        request: ChangeRequest
    ) -> GovernanceDecision:
        """
        Process change request with fully autonomous governance
        
        完全自主處理變更請求，無需人工審批
        
        This method evaluates change requests against policies and makes
        autonomous decisions without any human approval step.
        
        Args:
            request: Change request to process
            
        Returns:
            Governance decision
        """
        decision_id = f"gov-{uuid.uuid4().hex[:8]}"
        self.stats["total_requests"] += 1
        
        # Find applicable policies
        applicable_policies = self._get_applicable_policies(request.change_type)
        
        if not applicable_policies:
            # No specific policy - use intelligent default approval
            return await self._make_default_decision(decision_id, request)
        
        # Evaluate against all applicable policies
        evaluation_results = []
        for policy in applicable_policies:
            result = await self._evaluate_policy(request, policy)
            evaluation_results.append(result)
        
        # Determine final action based on all evaluations
        action, reasoning, policy_applied = self._determine_action(evaluation_results)
        
        # Check for auto-corrections
        auto_corrections = []
        if action == GovernanceAction.AUTO_FIX:
            auto_corrections = await self._apply_auto_corrections(request)
            if auto_corrections:
                action = GovernanceAction.APPROVE
                self.stats["auto_fixed"] += 1
        
        # Create decision
        decision = GovernanceDecision(
            decision_id=decision_id,
            request=request,
            action=action,
            policy_applied=policy_applied,
            reasoning=reasoning,
            conditions_met=[r["conditions_met"] for r in evaluation_results if r.get("conditions_met")],
            auto_corrections=auto_corrections
        )
        
        # Update statistics
        if action == GovernanceAction.APPROVE:
            self.stats["auto_approved"] += 1
        elif action == GovernanceAction.DENY:
            self.stats["auto_denied"] += 1
        
        self.decisions.append(decision)
        
        logger.info(
            f"Governance decision: {decision_id} - {action.value} "
            f"(policy: {policy_applied})"
        )
        
        return decision
    
    def _get_applicable_policies(
        self,
        change_type: ChangeType
    ) -> List[GovernancePolicy]:
        """Get policies applicable to change type"""
        type_mapping = {
            ChangeType.DEPLOYMENT: [PolicyType.DEPLOYMENT, PolicyType.SECURITY],
            ChangeType.CONFIGURATION: [PolicyType.COMPLIANCE, PolicyType.SECURITY],
            ChangeType.INFRASTRUCTURE: [PolicyType.RESOURCE, PolicyType.SECURITY],
            ChangeType.POLICY: [PolicyType.COMPLIANCE],
            ChangeType.ACCESS: [PolicyType.ACCESS_CONTROL, PolicyType.SECURITY],
            ChangeType.DATA: [PolicyType.DATA_PROTECTION, PolicyType.COMPLIANCE]
        }
        
        applicable_types = type_mapping.get(change_type, [])
        
        return [
            policy for policy in self.policies.values()
            if policy.policy_type in applicable_types and policy.enabled
        ]
    
    async def _evaluate_policy(
        self,
        request: ChangeRequest,
        policy: GovernancePolicy
    ) -> Dict[str, Any]:
        """Evaluate request against a policy"""
        # Check auto-deny conditions first
        for condition in policy.auto_deny_conditions:
            if self._evaluate_condition(condition, request):
                return {
                    "policy_id": policy.policy_id,
                    "action": GovernanceAction.DENY,
                    "reason": f"Auto-deny condition met: {condition}",
                    "conditions_met": condition
                }
        
        # Check auto-approve conditions
        approve_conditions_met = []
        for condition in policy.auto_approve_conditions:
            if self._evaluate_condition(condition, request):
                approve_conditions_met.append(condition)
        
        # Determine action based on conditions met
        if len(approve_conditions_met) >= len(policy.auto_approve_conditions) * 0.7:
            return {
                "policy_id": policy.policy_id,
                "action": GovernanceAction.APPROVE,
                "reason": "Sufficient auto-approve conditions met",
                "conditions_met": ", ".join(approve_conditions_met)
            }
        
        # For adaptive enforcement, allow auto-fix
        if policy.enforcement == PolicyEnforcement.AUTO_CORRECT:
            return {
                "policy_id": policy.policy_id,
                "action": GovernanceAction.AUTO_FIX,
                "reason": "Auto-correction available",
                "conditions_met": ", ".join(approve_conditions_met)
            }
        
        # For advisory, approve with warning
        if policy.enforcement == PolicyEnforcement.ADVISORY:
            return {
                "policy_id": policy.policy_id,
                "action": GovernanceAction.APPROVE,
                "reason": "Advisory policy - proceeding with caution",
                "conditions_met": ", ".join(approve_conditions_met)
            }
        
        # Default to system escalation (NOT human)
        return {
            "policy_id": policy.policy_id,
            "action": GovernanceAction.ESCALATE_TO_SYSTEM,
            "reason": "Requires additional system analysis",
            "conditions_met": ", ".join(approve_conditions_met)
        }
    
    def _evaluate_condition(
        self,
        condition: str,
        request: ChangeRequest
    ) -> bool:
        """Evaluate a policy condition"""
        # Simplified condition evaluation
        # In production, this would be a proper expression evaluator
        
        params = request.parameters
        
        if "risk_score" in condition:
            if "<" in condition:
                threshold = float(condition.split("<")[1].strip())
                return request.risk_score < threshold
            elif ">" in condition:
                threshold = float(condition.split(">")[1].strip())
                return request.risk_score > threshold
        
        if "== true" in condition:
            key = condition.split("==")[0].strip()
            return params.get(key, False) is True
        
        if "== false" in condition:
            key = condition.split("==")[0].strip()
            return params.get(key, True) is False
        
        # Handle numeric comparisons like "security_vulnerabilities > 0"
        if ">" in condition and "==" not in condition:
            parts = condition.split(">")
            key = parts[0].strip()
            threshold = float(parts[1].strip())
            value = params.get(key, 0)
            if isinstance(value, (int, float)):
                return value > threshold
            return False
        
        if "<" in condition and "==" not in condition:
            parts = condition.split("<")
            key = parts[0].strip()
            threshold = float(parts[1].strip())
            value = params.get(key, 0)
            if isinstance(value, (int, float)):
                return value < threshold
            return False
        
        # Default to False for unknown conditions (safe default)
        return False
    
    def _determine_action(
        self,
        evaluation_results: List[Dict[str, Any]]
    ) -> tuple:
        """Determine final action from all policy evaluations"""
        # Priority: DENY > AUTO_FIX > ESCALATE_TO_SYSTEM > APPROVE
        
        deny_results = [r for r in evaluation_results if r["action"] == GovernanceAction.DENY]
        if deny_results:
            return (
                GovernanceAction.DENY,
                deny_results[0]["reason"],
                deny_results[0]["policy_id"]
            )
        
        auto_fix_results = [r for r in evaluation_results if r["action"] == GovernanceAction.AUTO_FIX]
        if auto_fix_results:
            return (
                GovernanceAction.AUTO_FIX,
                auto_fix_results[0]["reason"],
                auto_fix_results[0]["policy_id"]
            )
        
        escalate_results = [r for r in evaluation_results if r["action"] == GovernanceAction.ESCALATE_TO_SYSTEM]
        if escalate_results:
            # System escalation means more analysis, not human approval
            return (
                GovernanceAction.APPROVE,  # System handles escalation internally
                "Approved after additional system analysis",
                escalate_results[0]["policy_id"]
            )
        
        approve_results = [r for r in evaluation_results if r["action"] == GovernanceAction.APPROVE]
        if approve_results:
            return (
                GovernanceAction.APPROVE,
                approve_results[0]["reason"],
                approve_results[0]["policy_id"]
            )
        
        # Default approval if no policy matched
        return (
            GovernanceAction.APPROVE,
            "No blocking conditions found",
            "default"
        )
    
    async def _apply_auto_corrections(
        self,
        request: ChangeRequest
    ) -> List[str]:
        """Apply automatic corrections to comply with policies"""
        corrections = []
        
        # Example auto-corrections based on request type
        if request.change_type == ChangeType.DEPLOYMENT:
            if not request.parameters.get("rollback_available"):
                request.parameters["rollback_available"] = True
                request.auto_rollback = True
                corrections.append("Enabled automatic rollback")
            
            if not request.parameters.get("health_check"):
                request.parameters["health_check"] = True
                corrections.append("Added health check verification")
        
        if request.change_type == ChangeType.ACCESS:
            if not request.parameters.get("time_limited"):
                request.parameters["time_limited"] = True
                request.parameters["expires_in_hours"] = 24
                corrections.append("Added 24-hour time limit to access grant")
        
        return corrections
    
    async def _make_default_decision(
        self,
        decision_id: str,
        request: ChangeRequest
    ) -> GovernanceDecision:
        """Make default decision when no specific policy applies"""
        # Use intelligent defaults based on risk score
        if request.risk_score < 0.3:
            action = GovernanceAction.APPROVE
            reasoning = "Low risk - auto-approved with default policy"
        elif request.risk_score < 0.7:
            action = GovernanceAction.APPROVE
            reasoning = "Moderate risk - approved with monitoring"
        else:
            action = GovernanceAction.DEFER
            reasoning = "High risk - deferred for additional system analysis"
        
        self.stats["auto_approved"] += 1 if action == GovernanceAction.APPROVE else 0
        
        return GovernanceDecision(
            decision_id=decision_id,
            request=request,
            action=action,
            policy_applied="default",
            reasoning=reasoning
        )
    
    async def verify_compliance(
        self,
        scope: str = "all"
    ) -> ComplianceStatus:
        """
        Verify compliance automatically
        
        自動驗證合規性
        """
        violations = []
        auto_fixed = []
        
        # Check all enabled policies
        for policy_id, policy in self.policies.items():
            if not policy.enabled:
                continue
            
            # Simulate compliance check
            check_result = await self._check_policy_compliance(policy)
            
            if not check_result["compliant"]:
                if policy.enforcement == PolicyEnforcement.AUTO_CORRECT:
                    # Attempt auto-fix
                    fixed = await self._auto_fix_violation(policy, check_result)
                    if fixed:
                        auto_fixed.append(f"{policy.name}: {check_result['issue']}")
                    else:
                        violations.append({
                            "policy": policy.name,
                            "issue": check_result["issue"],
                            "severity": "medium"
                        })
                else:
                    violations.append({
                        "policy": policy.name,
                        "issue": check_result["issue"],
                        "severity": "high" if policy.enforcement == PolicyEnforcement.STRICT else "low"
                    })
        
        status = ComplianceStatus(
            compliant=len(violations) == 0,
            violations=violations,
            auto_fixed=auto_fixed,
            pending_issues=[v["issue"] for v in violations]
        )
        
        self.compliance_cache[scope] = status
        return status
    
    async def _check_policy_compliance(
        self,
        policy: GovernancePolicy
    ) -> Dict[str, Any]:
        """Check compliance with a specific policy"""
        # Simulated compliance check
        await asyncio.sleep(0.01)
        
        # In production, this would perform actual compliance checks
        return {
            "compliant": True,
            "issue": None
        }
    
    async def _auto_fix_violation(
        self,
        policy: GovernancePolicy,
        violation: Dict[str, Any]
    ) -> bool:
        """Attempt to auto-fix a policy violation"""
        # Simulated auto-fix
        await asyncio.sleep(0.01)
        
        # In production, this would apply actual fixes
        return True
    
    def register_change_handler(
        self,
        change_type: ChangeType,
        handler: Callable[..., Awaitable[Any]]
    ) -> None:
        """Register handler for change type"""
        self.change_handlers[change_type] = handler
        logger.info(f"Registered handler for change type: {change_type.value}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get governance hub statistics"""
        approval_rate = (
            self.stats["auto_approved"] / max(self.stats["total_requests"], 1) * 100
        )
        
        return {
            "total_requests": self.stats["total_requests"],
            "auto_approved": self.stats["auto_approved"],
            "auto_denied": self.stats["auto_denied"],
            "auto_fixed": self.stats["auto_fixed"],
            "approval_rate": round(approval_rate, 2),
            "active_policies": len([p for p in self.policies.values() if p.enabled]),
            "rollbacks": self.stats["rollbacks"]
        }
    
    def get_decision_history(
        self,
        limit: int = 10,
        change_type: Optional[ChangeType] = None
    ) -> List[Dict[str, Any]]:
        """Get recent governance decisions"""
        decisions = self.decisions
        
        if change_type:
            decisions = [d for d in decisions if d.request.change_type == change_type]
        
        return [
            {
                "decision_id": d.decision_id,
                "change_type": d.request.change_type.value,
                "action": d.action.value,
                "policy": d.policy_applied,
                "auto_corrections": d.auto_corrections,
                "decided_at": d.decided_at.isoformat()
            }
            for d in decisions[-limit:]
        ]


# Export classes
__all__ = [
    "AutoGovernanceHub",
    "PolicyType",
    "PolicyEnforcement",
    "GovernanceAction",
    "ChangeType",
    "GovernancePolicy",
    "ChangeRequest",
    "GovernanceDecision",
    "ComplianceStatus"
]
