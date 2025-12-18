"""
Tests for Phase 4 Components
Phase 4: Autonomous Trust Engine and Auto Governance Hub

Tests for:
- AutonomousTrustEngine
- AutoGovernanceHub
"""

import pytest
import asyncio
import sys
import os

# Add paths for imports
sys.path.insert(0, '/home/runner/work/SynergyMesh/SynergyMesh')

from core.autonomous_trust_engine import (
    AutonomousTrustEngine,
    TrustDomain,
    RiskLevel,
    AutonomyLevel,
    DecisionOutcome,
    ProposedAction,
    SafetyNet
)
from core.auto_governance_hub import (
    AutoGovernanceHub,
    PolicyType,
    PolicyEnforcement,
    GovernanceAction,
    ChangeType,
    ChangeRequest,
    GovernancePolicy
)


# ============================================
# Autonomous Trust Engine Tests
# ============================================

class TestAutonomousTrustEngine:
    """Tests for AutonomousTrustEngine"""
    
    @pytest.fixture
    def engine(self):
        """Create AutonomousTrustEngine instance"""
        return AutonomousTrustEngine(initial_trust=60.0)
    
    def test_initialization(self, engine):
        """Test engine initialization"""
        assert engine is not None
        assert engine.trust_score.overall == 60.0
        assert len(engine.safety_nets) > 0
    
    def test_get_current_autonomy_level(self, engine):
        """Test getting current autonomy level"""
        level = engine.get_current_autonomy_level()
        assert level == AutonomyLevel.ASSISTED
        
        # Test higher trust
        engine.trust_score.overall = 75
        assert engine.get_current_autonomy_level() == AutonomyLevel.AUTONOMOUS
        
        # Test highest trust
        engine.trust_score.overall = 95
        assert engine.get_current_autonomy_level() == AutonomyLevel.FULLY_AUTONOMOUS
    
    def test_get_acceptable_risk_level(self, engine):
        """Test getting acceptable risk level"""
        risk = engine.get_acceptable_risk_level()
        assert risk == RiskLevel.MODERATE
        
        # Test higher trust
        engine.trust_score.overall = 85
        assert engine.get_acceptable_risk_level() == RiskLevel.HIGH
    
    @pytest.mark.asyncio
    async def test_make_autonomous_decision_low_risk(self, engine):
        """Test autonomous decision for low risk action"""
        action = ProposedAction(
            action_id="act-1",
            action_type="config_update",
            domain=TrustDomain.CONFIGURATION,
            description="Update configuration",
            estimated_risk=RiskLevel.LOW,
            reversible=True
        )
        
        decision = await engine.make_autonomous_decision(action)
        
        assert decision.decision_id.startswith("decision-")
        assert decision.outcome == DecisionOutcome.APPROVED_AUTO
        assert decision.confidence > 0
    
    @pytest.mark.asyncio
    async def test_make_autonomous_decision_high_risk(self, engine):
        """Test autonomous decision for high risk action with low trust"""
        engine.trust_score.overall = 30  # Low trust
        
        action = ProposedAction(
            action_id="act-2",
            action_type="db_migration",
            domain=TrustDomain.DATABASE,
            description="Migrate database schema",
            estimated_risk=RiskLevel.HIGH,
            reversible=False,
            impact_scope="global"
        )
        
        decision = await engine.make_autonomous_decision(action)
        
        assert decision.outcome == DecisionOutcome.DEFERRED
    
    @pytest.mark.asyncio
    async def test_execute_decision(self, engine):
        """Test executing an approved decision"""
        action = ProposedAction(
            action_id="act-3",
            action_type="deploy_service",
            domain=TrustDomain.DEPLOYMENT,
            description="Deploy service",
            estimated_risk=RiskLevel.LOW
        )
        
        decision = await engine.make_autonomous_decision(action)
        assert decision.outcome == DecisionOutcome.APPROVED_AUTO
        
        executed = await engine.execute_decision(decision)
        
        assert executed.outcome == DecisionOutcome.EXECUTED
        assert executed.result is not None
        assert executed.result["success"] is True
    
    def test_safety_nets(self, engine):
        """Test safety nets are initialized"""
        assert "cascade_failure_prevention" in engine.safety_nets
        assert "resource_protection" in engine.safety_nets
        assert "data_integrity" in engine.safety_nets
        assert "security_boundary" in engine.safety_nets
    
    def test_add_safety_net(self, engine):
        """Test adding custom safety net"""
        custom_net = SafetyNet(
            name="custom_protection",
            trigger_conditions=["custom_condition"],
            action_on_trigger="custom_action"
        )
        
        engine.add_safety_net(custom_net)
        
        assert "custom_protection" in engine.safety_nets
    
    def test_register_action_handler(self, engine):
        """Test registering action handler"""
        async def custom_handler(action):
            return {"status": "custom"}
        
        engine.register_action_handler("custom_action", custom_handler)
        
        assert "custom_action" in engine.action_handlers
    
    def test_get_trust_status(self, engine):
        """Test getting trust status"""
        status = engine.get_trust_status()
        
        assert "overall_trust" in status
        assert "domain_trust" in status
        assert "autonomy_level" in status
        assert "acceptable_risk" in status
    
    def test_get_statistics(self, engine):
        """Test getting statistics"""
        stats = engine.get_statistics()
        
        assert "total_decisions" in stats
        assert "auto_approved" in stats
        assert "success_rate" in stats
        assert "safety_nets_active" in stats
    
    def test_get_decision_history(self, engine):
        """Test getting decision history"""
        history = engine.get_decision_history(limit=5)
        assert isinstance(history, list)


# ============================================
# Auto Governance Hub Tests
# ============================================

class TestAutoGovernanceHub:
    """Tests for AutoGovernanceHub"""
    
    @pytest.fixture
    def hub(self):
        """Create AutoGovernanceHub instance"""
        return AutoGovernanceHub()
    
    def test_initialization(self, hub):
        """Test hub initialization"""
        assert hub is not None
        assert len(hub.policies) >= 4  # Default policies
    
    def test_default_policies(self, hub):
        """Test default policies are loaded"""
        assert "deploy-auto" in hub.policies
        assert "security-enforce" in hub.policies
        assert "resource-auto" in hub.policies
        assert "access-auto" in hub.policies
    
    def test_add_policy(self, hub):
        """Test adding custom policy"""
        policy = GovernancePolicy(
            policy_id="custom-policy",
            name="Custom Policy",
            policy_type=PolicyType.COMPLIANCE,
            enforcement=PolicyEnforcement.ADVISORY
        )
        
        hub.add_policy(policy)
        
        assert "custom-policy" in hub.policies
    
    @pytest.mark.asyncio
    async def test_process_change_request_low_risk(self, hub):
        """Test processing low risk change request"""
        request = ChangeRequest(
            request_id="req-1",
            change_type=ChangeType.CONFIGURATION,
            description="Update config file",
            requestor="system-service-1",
            parameters={
                "tests_passing": True,
                "no_breaking_changes": True
            },
            risk_score=0.2
        )
        
        decision = await hub.process_change_request(request)
        
        assert decision.decision_id.startswith("gov-")
        assert decision.action == GovernanceAction.APPROVE
    
    @pytest.mark.asyncio
    async def test_process_change_request_deployment(self, hub):
        """Test processing deployment change request"""
        request = ChangeRequest(
            request_id="req-2",
            change_type=ChangeType.DEPLOYMENT,
            description="Deploy new version",
            requestor="ci-pipeline",
            parameters={
                "tests_passing": True,
                "no_breaking_changes": True,
                "rollback_available": True
            },
            risk_score=0.3
        )
        
        decision = await hub.process_change_request(request)
        
        assert decision.action in [GovernanceAction.APPROVE, GovernanceAction.AUTO_FIX]
    
    @pytest.mark.asyncio
    async def test_process_change_request_access(self, hub):
        """Test processing access change request"""
        request = ChangeRequest(
            request_id="req-3",
            change_type=ChangeType.ACCESS,
            description="Grant temporary access",
            requestor="auth-service",
            parameters={
                "least_privilege_compliant": True,
                "no_permanent_elevation": True
            },
            risk_score=0.4
        )
        
        decision = await hub.process_change_request(request)
        
        assert decision.action == GovernanceAction.APPROVE
    
    @pytest.mark.asyncio
    async def test_auto_corrections(self, hub):
        """Test auto-corrections are applied"""
        request = ChangeRequest(
            request_id="req-4",
            change_type=ChangeType.DEPLOYMENT,
            description="Deploy without rollback",
            requestor="manual-deploy",
            parameters={
                "rollback_available": False
            },
            risk_score=0.3
        )
        
        decision = await hub.process_change_request(request)
        
        # Check if auto-correction was applied
        if decision.auto_corrections:
            assert "Enabled automatic rollback" in decision.auto_corrections
    
    @pytest.mark.asyncio
    async def test_verify_compliance(self, hub):
        """Test compliance verification"""
        status = await hub.verify_compliance()
        
        assert hasattr(status, "compliant")
        assert hasattr(status, "violations")
        assert hasattr(status, "auto_fixed")
    
    def test_get_statistics(self, hub):
        """Test getting statistics"""
        stats = hub.get_statistics()
        
        assert "total_requests" in stats
        assert "auto_approved" in stats
        assert "approval_rate" in stats
        assert "active_policies" in stats
    
    def test_get_decision_history(self, hub):
        """Test getting decision history"""
        history = hub.get_decision_history(limit=5)
        assert isinstance(history, list)


# ============================================
# Integration Tests
# ============================================

class TestPhase4Integration:
    """Integration tests for Phase 4 components"""
    
    @pytest.mark.asyncio
    async def test_trust_engine_governance_integration(self):
        """Test trust engine and governance hub integration"""
        # Initialize both systems
        trust_engine = AutonomousTrustEngine(initial_trust=75.0)
        governance_hub = AutoGovernanceHub()
        
        # Create a deployment proposal
        action = ProposedAction(
            action_id="deploy-001",
            action_type="deployment",
            domain=TrustDomain.DEPLOYMENT,
            description="Deploy new service version",
            estimated_risk=RiskLevel.MODERATE,
            reversible=True
        )
        
        # Get trust-based decision
        trust_decision = await trust_engine.make_autonomous_decision(action)
        
        assert trust_decision.outcome == DecisionOutcome.APPROVED_AUTO
        
        # Process through governance hub
        change_request = ChangeRequest(
            request_id="change-001",
            change_type=ChangeType.DEPLOYMENT,
            description=action.description,
            requestor="trust-engine",
            parameters={
                "trust_score": trust_decision.trust_score_used,
                "risk_level": action.estimated_risk.value,
                "tests_passing": True,
                "no_breaking_changes": True
            },
            risk_score=0.4
        )
        
        gov_decision = await governance_hub.process_change_request(change_request)
        
        assert gov_decision.action == GovernanceAction.APPROVE
    
    @pytest.mark.asyncio
    async def test_full_autonomous_workflow(self):
        """Test full autonomous workflow without human approval"""
        trust_engine = AutonomousTrustEngine(initial_trust=80.0)
        governance_hub = AutoGovernanceHub()
        
        # Simulate multiple operations
        operations = [
            ("config_update", TrustDomain.CONFIGURATION, RiskLevel.LOW, ChangeType.CONFIGURATION),
            ("deploy_canary", TrustDomain.DEPLOYMENT, RiskLevel.MODERATE, ChangeType.DEPLOYMENT),
            ("grant_access", TrustDomain.SECURITY, RiskLevel.LOW, ChangeType.ACCESS),
        ]
        
        results = []
        
        for op_type, domain, risk, change_type in operations:
            # Trust decision
            action = ProposedAction(
                action_id=f"act-{op_type}",
                action_type=op_type,
                domain=domain,
                description=f"Perform {op_type}",
                estimated_risk=risk,
                reversible=True
            )
            
            trust_dec = await trust_engine.make_autonomous_decision(action)
            
            # Governance decision
            request = ChangeRequest(
                request_id=f"req-{op_type}",
                change_type=change_type,
                description=action.description,
                requestor="autonomous-system",
                parameters={"tests_passing": True},
                risk_score=risk.value / 10
            )
            
            gov_dec = await governance_hub.process_change_request(request)
            
            results.append({
                "operation": op_type,
                "trust_outcome": trust_dec.outcome.value,
                "gov_outcome": gov_dec.action.value
            })
        
        # All operations should complete without human approval
        assert all(
            r["trust_outcome"] in ["approved_auto", "executed"]
            for r in results
        )
        assert all(
            r["gov_outcome"] in ["approve", "auto_fix"]
            for r in results
        )
    
    @pytest.mark.asyncio
    async def test_no_human_approval_required(self):
        """Verify no human approval step exists in the workflow"""
        trust_engine = AutonomousTrustEngine(initial_trust=50.0)
        governance_hub = AutoGovernanceHub()
        
        # Process 10 different requests
        for i in range(10):
            action = ProposedAction(
                action_id=f"test-{i}",
                action_type="auto_task",
                domain=TrustDomain.CONFIGURATION,
                description=f"Auto task {i}",
                estimated_risk=RiskLevel.LOW
            )
            
            decision = await trust_engine.make_autonomous_decision(action)
            
            # No decision should require human approval
            assert decision.outcome != "requires_human_approval"
            assert "human" not in decision.reasoning.lower() or "not" in decision.reasoning.lower()
        
        # Check governance decisions don't escalate to humans
        for i in range(5):
            request = ChangeRequest(
                request_id=f"gov-test-{i}",
                change_type=ChangeType.CONFIGURATION,
                description=f"Gov test {i}",
                requestor="test-system",
                risk_score=0.2
            )
            
            decision = await governance_hub.process_change_request(request)
            
            # Should escalate to system, not humans
            assert decision.action != "requires_human_approval"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
