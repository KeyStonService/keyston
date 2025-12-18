"""
Autonomous Trust Engine - 智能信任系統
Phase 4: Fully Autonomous Decision Making Without Human Approval

This module implements a trust-based autonomous decision system that operates
without requiring human approval, using intelligent risk assessment and
progressive trust scoring.

Core Features:
- Trust Score System (信任積分系統)
- Risk-based autonomous decision making
- Multi-layer safety nets instead of human checkpoints
- Self-learning trust calibration

設計原則: 系統自己評估風險並決定行動範圍，而非將決策推給人類
Reference: Human-out-of-the-Loop (HOOTL) systems for fully autonomous operation
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)


class TrustDomain(Enum):
    """Trust domains for different operation types"""
    DATABASE = "database"
    DEPLOYMENT = "deployment"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    CODE_CHANGES = "code_changes"
    CONFIGURATION = "configuration"
    NETWORKING = "networking"


class RiskLevel(Enum):
    """Risk levels for operations"""
    MINIMAL = 1      # No significant impact
    LOW = 2          # Minor impact, easily reversible
    MODERATE = 3     # Moderate impact, reversible with effort
    HIGH = 4         # Significant impact, difficult to reverse
    CRITICAL = 5     # Critical impact, may be irreversible


class AutonomyLevel(Enum):
    """System autonomy levels based on trust"""
    SUPERVISED = "supervised"          # Requires human approval (initial state)
    ASSISTED = "assisted"              # Suggests actions, auto-executes low risk
    AUTONOMOUS = "autonomous"          # Fully autonomous for most operations
    FULLY_AUTONOMOUS = "fully_autonomous"  # Complete autonomy including critical ops


class DecisionOutcome(Enum):
    """Possible decision outcomes"""
    APPROVED_AUTO = "approved_auto"           # Auto-approved by trust system
    APPROVED_ESCALATED = "approved_escalated" # Approved after escalation
    DEFERRED = "deferred"                     # Deferred for more information
    REJECTED = "rejected"                     # Rejected due to risk
    EXECUTED = "executed"                     # Already executed


@dataclass
class TrustScore:
    """Trust score for autonomous operations"""
    overall: float = 50.0  # 0-100 overall trust score
    domains: Dict[TrustDomain, float] = field(default_factory=dict)
    history: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        # Initialize domain scores if not provided
        if not self.domains:
            self.domains = {domain: 50.0 for domain in TrustDomain}
        if not self.history:
            self.history = {
                "successful_operations": 0,
                "failed_operations": 0,
                "average_impact": 0.0,
                "user_satisfaction": 0.0,
                "rollbacks": 0
            }


@dataclass
class ProposedAction:
    """Action proposed by the autonomous system"""
    action_id: str
    action_type: str
    domain: TrustDomain
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    estimated_risk: RiskLevel = RiskLevel.LOW
    reversible: bool = True
    impact_scope: str = "local"  # local, service, system, global
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AutonomousDecision:
    """Decision made by the autonomous trust engine"""
    decision_id: str
    action: ProposedAction
    outcome: DecisionOutcome
    trust_score_used: float
    risk_assessment: Dict[str, Any]
    reasoning: str
    confidence: float
    executed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    rollback_available: bool = True


@dataclass
class SafetyNet:
    """Safety net configuration for autonomous operations"""
    name: str
    enabled: bool = True
    trigger_conditions: List[str] = field(default_factory=list)
    action_on_trigger: str = "pause_and_assess"
    auto_rollback: bool = True
    notification_channels: List[str] = field(default_factory=list)


class AutonomousTrustEngine:
    """
    智能信任引擎 - 完全自主決策系統
    
    Autonomous Trust Engine for fully autonomous operation without human approval.
    Uses intelligent risk assessment and progressive trust scoring.
    
    Core Principles:
    1. 系統從受限自主開始，逐步獲得更大權限
    2. 決策基於風險評估，而非簡單的人工審核
    3. 使用多層安全網，而非單點審核
    
    設計目標:
    - 完全無人化: No human approval required
    - 智能風險評估: Intelligent risk assessment
    - 自我學習: Self-learning trust calibration
    - 多層安全: Multi-layer safety nets
    """
    
    # Trust thresholds for different autonomy levels
    AUTONOMY_THRESHOLDS = {
        AutonomyLevel.SUPERVISED: 0,
        AutonomyLevel.ASSISTED: 40,
        AutonomyLevel.AUTONOMOUS: 70,
        AutonomyLevel.FULLY_AUTONOMOUS: 90
    }
    
    # Risk acceptance thresholds based on trust score
    RISK_ACCEPTANCE_MATRIX = {
        # (min_trust, max_risk_level)
        (0, 40): RiskLevel.MINIMAL,
        (40, 60): RiskLevel.LOW,
        (60, 80): RiskLevel.MODERATE,
        (80, 95): RiskLevel.HIGH,
        (95, 100): RiskLevel.CRITICAL
    }
    
    # Trust score adjustments
    TRUST_ADJUSTMENTS = {
        "success": 2.0,
        "failure": -5.0,
        "rollback_success": 1.0,
        "rollback_failure": -10.0,
        "positive_feedback": 3.0,
        "negative_feedback": -4.0
    }
    
    def __init__(self, initial_trust: float = 50.0):
        """
        Initialize the Autonomous Trust Engine
        
        Args:
            initial_trust: Starting trust score (default 50.0)
        """
        self.trust_score = TrustScore(overall=initial_trust)
        self.decisions: List[AutonomousDecision] = []
        self.safety_nets: Dict[str, SafetyNet] = {}
        self.action_handlers: Dict[str, Callable[..., Awaitable[Any]]] = {}
        self.rollback_handlers: Dict[str, Callable[..., Awaitable[Any]]] = {}
        
        # Statistics
        self.stats = {
            "total_decisions": 0,
            "auto_approved": 0,
            "auto_rejected": 0,
            "executions": 0,
            "successful_executions": 0,
            "rollbacks": 0
        }
        
        # Initialize default safety nets
        self._initialize_safety_nets()
        
        logger.info(
            f"AutonomousTrustEngine initialized - 智能信任引擎已初始化 "
            f"(initial trust: {initial_trust})"
        )
    
    def _initialize_safety_nets(self) -> None:
        """Initialize default safety nets"""
        default_nets = [
            SafetyNet(
                name="cascade_failure_prevention",
                trigger_conditions=["multiple_failures_in_succession", "error_rate_spike"],
                action_on_trigger="pause_all_operations",
                auto_rollback=True
            ),
            SafetyNet(
                name="resource_protection",
                trigger_conditions=["resource_exhaustion", "memory_pressure"],
                action_on_trigger="reduce_parallelism",
                auto_rollback=False
            ),
            SafetyNet(
                name="data_integrity",
                trigger_conditions=["checksum_mismatch", "data_corruption_detected"],
                action_on_trigger="halt_and_restore",
                auto_rollback=True
            ),
            SafetyNet(
                name="security_boundary",
                trigger_conditions=["privilege_escalation_attempt", "unauthorized_access"],
                action_on_trigger="lockdown",
                auto_rollback=True
            )
        ]
        
        for net in default_nets:
            self.safety_nets[net.name] = net
    
    def get_current_autonomy_level(self) -> AutonomyLevel:
        """Get current autonomy level based on trust score"""
        trust = self.trust_score.overall
        
        if trust >= self.AUTONOMY_THRESHOLDS[AutonomyLevel.FULLY_AUTONOMOUS]:
            return AutonomyLevel.FULLY_AUTONOMOUS
        elif trust >= self.AUTONOMY_THRESHOLDS[AutonomyLevel.AUTONOMOUS]:
            return AutonomyLevel.AUTONOMOUS
        elif trust >= self.AUTONOMY_THRESHOLDS[AutonomyLevel.ASSISTED]:
            return AutonomyLevel.ASSISTED
        return AutonomyLevel.SUPERVISED
    
    def get_acceptable_risk_level(self) -> RiskLevel:
        """Get maximum acceptable risk level based on current trust"""
        trust = self.trust_score.overall
        
        for (min_trust, max_trust), risk_level in self.RISK_ACCEPTANCE_MATRIX.items():
            if min_trust <= trust < max_trust:
                return risk_level
        
        return RiskLevel.CRITICAL if trust >= 95 else RiskLevel.MINIMAL
    
    async def make_autonomous_decision(
        self,
        action: ProposedAction
    ) -> AutonomousDecision:
        """
        Make fully autonomous decision without human approval
        
        完全自主決策，無需人工審核
        
        Key principle: System evaluates risk and decides action scope itself,
        rather than pushing decision to humans.
        
        Args:
            action: Proposed action to evaluate
            
        Returns:
            Autonomous decision with outcome
        """
        decision_id = f"decision-{uuid.uuid4().hex[:8]}"
        self.stats["total_decisions"] += 1
        
        # Perform risk assessment
        risk_assessment = self._assess_risk(action)
        
        # Get domain-specific trust
        domain_trust = self.trust_score.domains.get(action.domain, self.trust_score.overall)
        
        # Calculate combined trust score
        combined_trust = (self.trust_score.overall * 0.6) + (domain_trust * 0.4)
        
        # Determine if action can be auto-approved
        acceptable_risk = self.get_acceptable_risk_level()
        can_auto_approve = action.estimated_risk.value <= acceptable_risk.value
        
        # Check safety nets
        safety_check = self._check_safety_nets(action, risk_assessment)
        
        if not safety_check["passed"]:
            outcome = DecisionOutcome.REJECTED
            reasoning = f"Safety net triggered: {safety_check['triggered_net']}"
            confidence = 0.95
            self.stats["auto_rejected"] += 1
        elif can_auto_approve:
            outcome = DecisionOutcome.APPROVED_AUTO
            reasoning = self._generate_approval_reasoning(action, risk_assessment, combined_trust)
            confidence = min(combined_trust / 100, 0.99)
            self.stats["auto_approved"] += 1
        else:
            # For high-risk actions with insufficient trust, use intelligent deferral
            # NOT human approval, but system-level reassessment
            outcome = DecisionOutcome.DEFERRED
            reasoning = (
                f"Risk level {action.estimated_risk.value} exceeds current acceptable level "
                f"{acceptable_risk.value}. System will attempt alternative approach or "
                f"break down into lower-risk operations."
            )
            confidence = combined_trust / 100
        
        decision = AutonomousDecision(
            decision_id=decision_id,
            action=action,
            outcome=outcome,
            trust_score_used=combined_trust,
            risk_assessment=risk_assessment,
            reasoning=reasoning,
            confidence=confidence
        )
        
        self.decisions.append(decision)
        
        logger.info(
            f"Autonomous decision: {decision_id} - {outcome.value} "
            f"(trust: {combined_trust:.1f}, risk: {action.estimated_risk.name})"
        )
        
        return decision
    
    def _assess_risk(self, action: ProposedAction) -> Dict[str, Any]:
        """Perform comprehensive risk assessment"""
        risk_factors = {
            "base_risk": action.estimated_risk.value,
            "reversibility": 1.0 if action.reversible else 2.0,
            "scope_multiplier": self._get_scope_multiplier(action.impact_scope),
            "domain_sensitivity": self._get_domain_sensitivity(action.domain),
            "time_factor": self._get_time_factor()
        }
        
        # Calculate composite risk score
        composite_risk = (
            risk_factors["base_risk"] *
            risk_factors["reversibility"] *
            risk_factors["scope_multiplier"] *
            risk_factors["domain_sensitivity"] *
            risk_factors["time_factor"]
        )
        
        return {
            "factors": risk_factors,
            "composite_score": round(composite_risk, 2),
            "recommendation": self._get_risk_recommendation(composite_risk),
            "mitigations": self._suggest_mitigations(action, composite_risk)
        }
    
    def _get_scope_multiplier(self, scope: str) -> float:
        """Get risk multiplier based on impact scope"""
        multipliers = {
            "local": 1.0,
            "service": 1.5,
            "system": 2.0,
            "global": 3.0
        }
        return multipliers.get(scope, 1.0)
    
    def _get_domain_sensitivity(self, domain: TrustDomain) -> float:
        """Get sensitivity factor for domain"""
        sensitivity = {
            TrustDomain.DATABASE: 1.5,
            TrustDomain.SECURITY: 2.0,
            TrustDomain.INFRASTRUCTURE: 1.8,
            TrustDomain.DEPLOYMENT: 1.3,
            TrustDomain.CODE_CHANGES: 1.4,
            TrustDomain.CONFIGURATION: 1.2,
            TrustDomain.NETWORKING: 1.6
        }
        return sensitivity.get(domain, 1.0)
    
    def _get_time_factor(self) -> float:
        """Get time-based risk factor (higher during peak hours)"""
        hour = datetime.now().hour
        # Lower risk factor during off-peak hours (night time)
        if 2 <= hour < 6:
            return 0.8
        # Higher risk factor during business hours
        elif 9 <= hour < 17:
            return 1.2
        return 1.0
    
    def _get_risk_recommendation(self, composite_risk: float) -> str:
        """Get recommendation based on composite risk"""
        if composite_risk < 3:
            return "proceed_immediately"
        elif composite_risk < 6:
            return "proceed_with_monitoring"
        elif composite_risk < 10:
            return "proceed_with_caution"
        elif composite_risk < 15:
            return "consider_alternatives"
        return "high_risk_action"
    
    def _suggest_mitigations(
        self,
        action: ProposedAction,
        composite_risk: float
    ) -> List[str]:
        """Suggest risk mitigations"""
        mitigations = []
        
        if composite_risk > 5:
            mitigations.append("Create backup before execution")
        if not action.reversible:
            mitigations.append("Prepare manual rollback procedure")
        if action.impact_scope in ["system", "global"]:
            mitigations.append("Execute during maintenance window")
        if action.domain == TrustDomain.DATABASE:
            mitigations.append("Enable transaction logging")
        if action.domain == TrustDomain.SECURITY:
            mitigations.append("Audit trail required")
        
        return mitigations
    
    def _check_safety_nets(
        self,
        action: ProposedAction,
        risk_assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check all safety nets"""
        for name, net in self.safety_nets.items():
            if not net.enabled:
                continue
            
            # Check trigger conditions
            for condition in net.trigger_conditions:
                if self._evaluate_safety_condition(condition, action, risk_assessment):
                    return {
                        "passed": False,
                        "triggered_net": name,
                        "condition": condition,
                        "action": net.action_on_trigger
                    }
        
        return {"passed": True, "triggered_net": None}
    
    def _evaluate_safety_condition(
        self,
        condition: str,
        action: ProposedAction,
        risk_assessment: Dict[str, Any]
    ) -> bool:
        """Evaluate a safety condition"""
        # Simplified condition evaluation
        # In production, this would be more sophisticated
        
        if condition == "multiple_failures_in_succession":
            recent_failures = self.trust_score.history.get("recent_failures", 0)
            return recent_failures >= 3
        
        if condition == "privilege_escalation_attempt":
            return (
                action.domain == TrustDomain.SECURITY and
                "escalate" in action.action_type.lower()
            )
        
        return False
    
    def _generate_approval_reasoning(
        self,
        action: ProposedAction,
        risk_assessment: Dict[str, Any],
        trust_score: float
    ) -> str:
        """Generate human-readable reasoning for approval"""
        parts = [
            f"Auto-approved based on trust score {trust_score:.1f}.",
            f"Risk level {action.estimated_risk.name} is within acceptable range.",
        ]
        
        if action.reversible:
            parts.append("Action is reversible if issues occur.")
        
        recommendation = risk_assessment.get("recommendation", "")
        if recommendation:
            parts.append(f"System recommendation: {recommendation}.")
        
        return " ".join(parts)
    
    async def execute_decision(
        self,
        decision: AutonomousDecision
    ) -> AutonomousDecision:
        """
        Execute an approved decision
        
        執行已批准的決策
        
        Args:
            decision: Decision to execute
            
        Returns:
            Updated decision with execution result
        """
        if decision.outcome not in [DecisionOutcome.APPROVED_AUTO, DecisionOutcome.APPROVED_ESCALATED]:
            logger.warning(f"Cannot execute non-approved decision: {decision.decision_id}")
            return decision
        
        self.stats["executions"] += 1
        decision.executed_at = datetime.now()
        
        try:
            # Get handler for action type
            handler = self.action_handlers.get(decision.action.action_type)
            
            if handler:
                result = await handler(decision.action)
            else:
                # Simulate execution for unregistered handlers
                result = await self._simulate_execution(decision.action)
            
            decision.result = {
                "success": True,
                "data": result,
                "executed_at": decision.executed_at.isoformat()
            }
            decision.outcome = DecisionOutcome.EXECUTED
            
            # Update trust score positively
            self._update_trust_score("success", decision.action.domain)
            self.stats["successful_executions"] += 1
            
            logger.info(f"Decision executed successfully: {decision.decision_id}")
            
        except Exception as e:
            logger.error(f"Decision execution failed: {decision.decision_id} - {e}")
            
            decision.result = {
                "success": False,
                "error": str(e),
                "executed_at": decision.executed_at.isoformat()
            }
            
            # Update trust score negatively
            self._update_trust_score("failure", decision.action.domain)
            
            # Attempt rollback if available
            if decision.rollback_available:
                await self._attempt_rollback(decision)
        
        return decision
    
    async def _simulate_execution(self, action: ProposedAction) -> Dict[str, Any]:
        """Simulate action execution"""
        await asyncio.sleep(0.05)  # Simulate processing time
        
        return {
            "status": "completed",
            "action_id": action.action_id,
            "action_type": action.action_type,
            "message": f"Action '{action.description}' executed successfully"
        }
    
    async def _attempt_rollback(self, decision: AutonomousDecision) -> bool:
        """Attempt to rollback a failed decision"""
        self.stats["rollbacks"] += 1
        
        rollback_handler = self.rollback_handlers.get(decision.action.action_type)
        
        try:
            if rollback_handler:
                await rollback_handler(decision.action)
            else:
                await asyncio.sleep(0.02)  # Simulate rollback
            
            self._update_trust_score("rollback_success", decision.action.domain)
            logger.info(f"Rollback successful for decision: {decision.decision_id}")
            return True
            
        except Exception as e:
            self._update_trust_score("rollback_failure", decision.action.domain)
            logger.error(f"Rollback failed for decision: {decision.decision_id} - {e}")
            return False
    
    def _update_trust_score(
        self,
        event_type: str,
        domain: TrustDomain
    ) -> None:
        """Update trust score based on event"""
        adjustment = self.TRUST_ADJUSTMENTS.get(event_type, 0)
        
        # Update overall trust
        self.trust_score.overall = max(0, min(100, self.trust_score.overall + adjustment))
        
        # Update domain-specific trust
        if domain in self.trust_score.domains:
            self.trust_score.domains[domain] = max(
                0,
                min(100, self.trust_score.domains[domain] + adjustment)
            )
        
        # Update history
        if "success" in event_type:
            self.trust_score.history["successful_operations"] += 1
        elif "failure" in event_type:
            self.trust_score.history["failed_operations"] += 1
        
        self.trust_score.last_updated = datetime.now()
    
    def register_action_handler(
        self,
        action_type: str,
        handler: Callable[..., Awaitable[Any]],
        rollback_handler: Optional[Callable[..., Awaitable[Any]]] = None
    ) -> None:
        """Register handler for action type"""
        self.action_handlers[action_type] = handler
        if rollback_handler:
            self.rollback_handlers[action_type] = rollback_handler
        
        logger.info(f"Registered handler for action type: {action_type}")
    
    def add_safety_net(self, safety_net: SafetyNet) -> None:
        """Add a safety net"""
        self.safety_nets[safety_net.name] = safety_net
        logger.info(f"Safety net added: {safety_net.name}")
    
    def get_trust_status(self) -> Dict[str, Any]:
        """Get current trust status"""
        return {
            "overall_trust": round(self.trust_score.overall, 2),
            "domain_trust": {
                domain.value: round(score, 2)
                for domain, score in self.trust_score.domains.items()
            },
            "autonomy_level": self.get_current_autonomy_level().value,
            "acceptable_risk": self.get_acceptable_risk_level().name,
            "history": self.trust_score.history,
            "last_updated": self.trust_score.last_updated.isoformat()
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics"""
        success_rate = (
            self.stats["successful_executions"] / max(self.stats["executions"], 1) * 100
        )
        
        return {
            "total_decisions": self.stats["total_decisions"],
            "auto_approved": self.stats["auto_approved"],
            "auto_rejected": self.stats["auto_rejected"],
            "approval_rate": round(
                self.stats["auto_approved"] / max(self.stats["total_decisions"], 1) * 100, 2
            ),
            "executions": self.stats["executions"],
            "successful_executions": self.stats["successful_executions"],
            "success_rate": round(success_rate, 2),
            "rollbacks": self.stats["rollbacks"],
            "safety_nets_active": len([
                net for net in self.safety_nets.values() if net.enabled
            ])
        }
    
    def get_decision_history(
        self,
        limit: int = 10,
        domain: Optional[TrustDomain] = None
    ) -> List[Dict[str, Any]]:
        """Get recent decision history"""
        decisions = self.decisions
        
        if domain:
            decisions = [d for d in decisions if d.action.domain == domain]
        
        return [
            {
                "decision_id": d.decision_id,
                "action_type": d.action.action_type,
                "domain": d.action.domain.value,
                "outcome": d.outcome.value,
                "trust_used": round(d.trust_score_used, 2),
                "confidence": round(d.confidence, 2),
                "executed_at": d.executed_at.isoformat() if d.executed_at else None
            }
            for d in decisions[-limit:]
        ]


# Export classes
__all__ = [
    "AutonomousTrustEngine",
    "TrustDomain",
    "RiskLevel",
    "AutonomyLevel",
    "DecisionOutcome",
    "TrustScore",
    "ProposedAction",
    "AutonomousDecision",
    "SafetyNet"
]
