"""
Tests for Phase 3 Components
Phase 3: Core AI, Bridges, and Automation

Tests for:
- AIDecisionEngine
- LanguageBridgeManager
- ZeroTouchDeploymentEngine
"""

import pytest
import asyncio
import sys
import os

# Add paths for imports
sys.path.insert(0, '/home/runner/work/SynergyMesh/SynergyMesh')

from core.ai_decision_engine import (
    AIDecisionEngine,
    DecisionType,
    DecisionPriority,
    ConfidenceLevel,
    DecisionContext,
    DecisionOption
)
from bridges.language_bridges import (
    LanguageBridgeManager,
    Language,
    BridgeType,
    BridgeStatus,
    CodeFragment
)
from automation.zero_touch_deployment import (
    ZeroTouchDeploymentEngine,
    DeploymentEnvironment,
    DeploymentStatus,
    DeploymentStrategy
)


# ============================================
# AI Decision Engine Tests
# ============================================

class TestAIDecisionEngine:
    """Tests for AIDecisionEngine"""
    
    @pytest.fixture
    def engine(self):
        """Create AIDecisionEngine instance"""
        return AIDecisionEngine()
    
    def test_initialization(self, engine):
        """Test engine initialization"""
        assert engine is not None
        assert engine.stats["decisions_made"] == 0
    
    @pytest.mark.asyncio
    async def test_make_decision_basic(self, engine):
        """Test basic decision making"""
        context = DecisionContext(
            context_id="ctx-1",
            domain="deployment",
            current_state={"status": "ready"}
        )
        
        options = [
            DecisionOption(
                option_id="opt-1",
                name="Deploy Now",
                description="Deploy immediately",
                benefit_score=0.8,
                risk_score=0.2,
                confidence=0.7
            ),
            DecisionOption(
                option_id="opt-2",
                name="Wait",
                description="Wait for better conditions",
                benefit_score=0.5,
                risk_score=0.1,
                confidence=0.6
            )
        ]
        
        decision = await engine.make_decision(context, options)
        
        assert decision.decision_id.startswith("dec-")
        assert decision.selected_option is not None
        assert decision.confidence_level in ConfidenceLevel
    
    @pytest.mark.asyncio
    async def test_make_decision_with_priority(self, engine):
        """Test decision making with priority"""
        context = DecisionContext(
            context_id="ctx-2",
            domain="security",
            objectives=["minimize_risk"]
        )
        
        options = [
            DecisionOption(
                option_id="opt-1",
                name="Patch Now",
                description="Apply security patch",
                benefit_score=0.9,
                risk_score=0.1
            )
        ]
        
        decision = await engine.make_decision(
            context, options,
            decision_type=DecisionType.STRATEGIC,
            priority=DecisionPriority.CRITICAL
        )
        
        assert decision.decision_type == DecisionType.STRATEGIC
        assert decision.priority == DecisionPriority.CRITICAL
    
    @pytest.mark.asyncio
    async def test_predict_outcome(self, engine):
        """Test outcome prediction"""
        current_state = {
            "success_rate": 0.95,
            "error_rate": 0.02,
            "performance": 0.8
        }
        
        prediction = await engine.predict_outcome(
            current_state,
            prediction_type="system_health"
        )
        
        assert prediction.prediction_id.startswith("pred-")
        assert 0 <= prediction.probability <= 1
        assert len(prediction.recommendations) > 0
    
    def test_record_outcome(self, engine):
        """Test recording decision outcomes"""
        # Make a decision first
        async def make_and_record():
            context = DecisionContext(context_id="ctx-3", domain="test")
            options = [DecisionOption(option_id="opt-1", name="Test", description="Test option")]
            decision = await engine.make_decision(context, options)
            
            engine.record_outcome(decision.decision_id, success=True)
            return decision
        
        decision = asyncio.get_event_loop().run_until_complete(make_and_record())
        
        assert engine.stats["successful_decisions"] >= 1
    
    def test_get_statistics(self, engine):
        """Test getting statistics"""
        stats = engine.get_statistics()
        
        assert "decisions_made" in stats
        assert "predictions_made" in stats
        assert "success_rate" in stats
    
    def test_get_decision_history(self, engine):
        """Test getting decision history"""
        history = engine.get_decision_history(limit=5)
        
        assert isinstance(history, list)


# ============================================
# Language Bridge Manager Tests
# ============================================

class TestLanguageBridgeManager:
    """Tests for LanguageBridgeManager"""
    
    @pytest.fixture
    def manager(self):
        """Create LanguageBridgeManager instance"""
        return LanguageBridgeManager()
    
    def test_initialization(self, manager):
        """Test manager initialization"""
        assert manager is not None
        assert len(manager.endpoints) == 0
    
    def test_register_endpoint(self, manager):
        """Test endpoint registration"""
        endpoint_id = manager.register_endpoint(
            language=Language.PYTHON,
            host="localhost",
            port=5000
        )
        
        assert endpoint_id.startswith("ep-python-")
        assert endpoint_id in manager.endpoints
    
    def test_register_multiple_endpoints(self, manager):
        """Test registering multiple endpoints"""
        py_id = manager.register_endpoint(language=Language.PYTHON)
        js_id = manager.register_endpoint(language=Language.JAVASCRIPT)
        go_id = manager.register_endpoint(language=Language.GO)
        
        assert len(manager.endpoints) == 3
    
    def test_create_bridge(self, manager):
        """Test bridge creation"""
        py_id = manager.register_endpoint(language=Language.PYTHON)
        js_id = manager.register_endpoint(language=Language.JAVASCRIPT)
        
        bridge_id = manager.create_bridge(py_id, js_id)
        
        assert bridge_id.startswith("bridge-")
        assert bridge_id in manager.connections
        assert manager.connections[bridge_id].status == BridgeStatus.CONNECTED
    
    @pytest.mark.asyncio
    async def test_execute_cross_language(self, manager):
        """Test cross-language execution"""
        py_id = manager.register_endpoint(language=Language.PYTHON)
        go_id = manager.register_endpoint(language=Language.GO)
        bridge_id = manager.create_bridge(py_id, go_id)
        
        code = CodeFragment(
            fragment_id="code-1",
            language=Language.PYTHON,
            code="def main(): return 42",
            entry_point="main"
        )
        
        result = await manager.execute_cross_language(bridge_id, code)
        
        assert result.success is True
        assert result.source_language == Language.PYTHON
        assert result.target_language == Language.GO
    
    def test_get_bridge_status(self, manager):
        """Test getting bridge status"""
        py_id = manager.register_endpoint(language=Language.PYTHON)
        js_id = manager.register_endpoint(language=Language.JAVASCRIPT)
        bridge_id = manager.create_bridge(py_id, js_id)
        
        status = manager.get_bridge_status(bridge_id)
        
        assert status is not None
        assert status["status"] == "connected"
    
    def test_list_bridges(self, manager):
        """Test listing bridges"""
        py_id = manager.register_endpoint(language=Language.PYTHON)
        js_id = manager.register_endpoint(language=Language.JAVASCRIPT)
        manager.create_bridge(py_id, js_id)
        
        bridges = manager.list_bridges()
        
        assert len(bridges) == 1
    
    def test_disconnect_bridge(self, manager):
        """Test disconnecting bridge"""
        py_id = manager.register_endpoint(language=Language.PYTHON)
        js_id = manager.register_endpoint(language=Language.JAVASCRIPT)
        bridge_id = manager.create_bridge(py_id, js_id)
        
        result = manager.disconnect_bridge(bridge_id)
        
        assert result is True
        assert manager.connections[bridge_id].status == BridgeStatus.DISCONNECTED
    
    def test_get_statistics(self, manager):
        """Test getting statistics"""
        stats = manager.get_statistics()
        
        assert "endpoints_registered" in stats
        assert "active_bridges" in stats
        assert "supported_languages" in stats


# ============================================
# Zero-Touch Deployment Tests
# ============================================

class TestZeroTouchDeploymentEngine:
    """Tests for ZeroTouchDeploymentEngine"""
    
    @pytest.fixture
    def engine(self):
        """Create ZeroTouchDeploymentEngine instance"""
        return ZeroTouchDeploymentEngine()
    
    def test_initialization(self, engine):
        """Test engine initialization"""
        assert engine is not None
        assert engine.stats["total_deployments"] == 0
    
    def test_create_deployment_config(self, engine):
        """Test creating deployment configuration"""
        config_id = engine.create_deployment_config(
            target_name="my-service",
            environment=DeploymentEnvironment.STAGING,
            artifact_name="my-app",
            artifact_version="1.0.0",
            strategy=DeploymentStrategy.ROLLING
        )
        
        assert config_id.startswith("config-")
        assert config_id in engine.deployment_configs
    
    @pytest.mark.asyncio
    async def test_deploy_rolling(self, engine):
        """Test rolling deployment"""
        config_id = engine.create_deployment_config(
            target_name="test-service",
            environment=DeploymentEnvironment.STAGING,
            artifact_name="test-app",
            artifact_version="1.0.0",
            strategy=DeploymentStrategy.ROLLING,
            replicas=3
        )
        
        result = await engine.deploy(config_id)
        
        assert result.deployment_id.startswith("deploy-")
        assert result.status == DeploymentStatus.COMPLETED
        assert len(result.logs) > 0
    
    @pytest.mark.asyncio
    async def test_deploy_blue_green(self, engine):
        """Test blue-green deployment"""
        config_id = engine.create_deployment_config(
            target_name="test-service",
            environment=DeploymentEnvironment.PRODUCTION,
            artifact_name="test-app",
            artifact_version="2.0.0",
            strategy=DeploymentStrategy.BLUE_GREEN
        )
        
        result = await engine.deploy(config_id)
        
        assert result.status == DeploymentStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_deploy_canary(self, engine):
        """Test canary deployment"""
        config_id = engine.create_deployment_config(
            target_name="test-service",
            environment=DeploymentEnvironment.PRODUCTION,
            artifact_name="test-app",
            artifact_version="3.0.0",
            strategy=DeploymentStrategy.CANARY
        )
        
        result = await engine.deploy(config_id)
        
        assert result.status == DeploymentStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_get_deployment_status(self, engine):
        """Test getting deployment status"""
        config_id = engine.create_deployment_config(
            target_name="status-test",
            environment=DeploymentEnvironment.STAGING,
            artifact_name="test-app",
            artifact_version="1.0.0"
        )
        
        result = await engine.deploy(config_id)
        status = engine.get_deployment_status(result.deployment_id)
        
        assert status is not None
        assert status["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_get_deployment_logs(self, engine):
        """Test getting deployment logs"""
        config_id = engine.create_deployment_config(
            target_name="logs-test",
            environment=DeploymentEnvironment.STAGING,
            artifact_name="test-app",
            artifact_version="1.0.0"
        )
        
        result = await engine.deploy(config_id)
        logs = engine.get_deployment_logs(result.deployment_id)
        
        assert logs is not None
        assert len(logs) > 0
    
    def test_get_statistics(self, engine):
        """Test getting statistics"""
        stats = engine.get_statistics()
        
        assert "total_deployments" in stats
        assert "success_rate" in stats
        assert "supported_strategies" in stats


# ============================================
# Integration Tests
# ============================================

class TestPhase3Integration:
    """Integration tests for Phase 3 components"""
    
    @pytest.mark.asyncio
    async def test_decision_to_deployment_pipeline(self):
        """Test decision → deployment pipeline"""
        # Initialize components
        decision_engine = AIDecisionEngine()
        deployment_engine = ZeroTouchDeploymentEngine()
        
        # Create decision context for deployment
        context = DecisionContext(
            context_id="pipeline-ctx",
            domain="deployment",
            current_state={"environment": "staging", "health": "good"},
            objectives=["deploy_new_version"]
        )
        
        # Define deployment options
        options = [
            DecisionOption(
                option_id="opt-rolling",
                name="Rolling Deployment",
                description="Deploy using rolling strategy",
                benefit_score=0.8,
                risk_score=0.2,
                confidence=0.7
            ),
            DecisionOption(
                option_id="opt-canary",
                name="Canary Deployment",
                description="Deploy using canary strategy",
                benefit_score=0.7,
                risk_score=0.3,
                confidence=0.6
            )
        ]
        
        # Make deployment decision
        decision = await decision_engine.make_decision(context, options)
        
        assert decision.selected_option is not None
        
        # Execute deployment based on decision
        strategy = (
            DeploymentStrategy.ROLLING if "Rolling" in decision.selected_option.name
            else DeploymentStrategy.CANARY
        )
        
        config_id = deployment_engine.create_deployment_config(
            target_name="pipeline-service",
            environment=DeploymentEnvironment.STAGING,
            artifact_name="pipeline-app",
            artifact_version="1.0.0",
            strategy=strategy
        )
        
        result = await deployment_engine.deploy(config_id)
        
        # Record outcome
        decision_engine.record_outcome(
            decision.decision_id,
            success=(result.status == DeploymentStatus.COMPLETED)
        )
        
        assert result.status == DeploymentStatus.COMPLETED
        assert decision_engine.stats["decisions_made"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
