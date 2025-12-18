"""
Phase 14 Component Tests - Main System Integration
測試主系統整合組件
"""

import pytest
from datetime import datetime
from typing import Any, Dict

# Import Phase 14 components
from core.main_system.synergymesh_core import (
    SynergyMeshCore,
    SystemConfig,
    PhaseStatus,
    SystemHealth,
    PhaseInfo,
)
from core.main_system.system_bootstrap import (
    SystemBootstrap,
    BootstrapConfig,
    ServiceRegistry,
    DependencyInjector,
    ServiceDefinition,
    ServiceLifecycle,
)
from core.main_system.phase_orchestrator import (
    PhaseOrchestrator,
    PhaseDefinition,
    PhaseTransition,
    ExecutionMode,
    PhaseState,
)
from core.main_system.automation_pipeline import (
    AutomationPipeline,
    PipelineTask,
    TaskResult,
    PipelineConfig,
    TaskPriority,
    TaskStatus,
)


class TestSynergyMeshCore:
    """Test SynergyMeshCore"""
    
    def test_core_initialization(self):
        """Test core initialization"""
        core = SynergyMeshCore()
        assert core is not None
        assert not core.is_initialized
        assert not core.is_running
    
    def test_core_with_config(self):
        """Test core with custom config"""
        config = SystemConfig(
            name="TestSystem",
            version="2.0.0",
            environment="test"
        )
        core = SynergyMeshCore(config=config)
        assert core.config.name == "TestSystem"
        assert core.config.version == "2.0.0"
    
    def test_core_initialize(self):
        """Test core initialize"""
        core = SynergyMeshCore()
        result = core.initialize()
        assert result is True
        assert core.is_initialized
    
    def test_core_start_stop(self):
        """Test core start and stop"""
        core = SynergyMeshCore()
        core.initialize()
        
        result = core.start()
        assert result is True
        assert core.is_running
        
        result = core.stop()
        assert result is True
        assert not core.is_running
    
    def test_core_phases(self):
        """Test core phases"""
        core = SynergyMeshCore()
        phases = core.get_all_phases()
        
        assert len(phases) == 13
        assert "phase_1" in phases
        assert "phase_13" in phases
    
    def test_core_health(self):
        """Test core health check"""
        core = SynergyMeshCore()
        core.initialize()
        core.start()
        
        health = core.get_health()
        assert health.overall_status in ["healthy", "degraded", "unhealthy"]
    
    def test_core_process_task_natural_language(self):
        """Test process natural language task"""
        core = SynergyMeshCore()
        core.initialize()
        core.start()
        
        result = core.process_task({"type": "natural_language", "id": "test1"})
        assert result["success"] is True
        assert "phase_1" in result["processed_by"]
        assert "phase_2" in result["processed_by"]
    
    def test_core_process_task_training(self):
        """Test process training task (Phase 7)"""
        core = SynergyMeshCore()
        core.initialize()
        core.start()
        
        result = core.process_task({"type": "training", "id": "test2"})
        assert result["success"] is True
        assert "phase_7" in result["processed_by"]
    
    def test_core_process_task_expert_consultation(self):
        """Test process expert consultation task (Phase 7)"""
        core = SynergyMeshCore()
        core.initialize()
        core.start()
        
        result = core.process_task({"type": "expert_consultation", "id": "test3"})
        assert result["success"] is True
        assert "phase_7" in result["processed_by"]
    
    def test_core_process_task_safety(self):
        """Test process safety task (Phase 10)"""
        core = SynergyMeshCore()
        core.initialize()
        core.start()
        
        result = core.process_task({"type": "safety_check", "id": "test4"})
        assert result["success"] is True
        assert "phase_10" in result["processed_by"]
    
    def test_core_service_registration(self):
        """Test service registration"""
        core = SynergyMeshCore()
        core.register_service("test_service", {"name": "test"})
        
        service = core.get_service("test_service")
        assert service is not None
        assert service["name"] == "test"


class TestSystemBootstrap:
    """Test SystemBootstrap"""
    
    def test_bootstrap_initialization(self):
        """Test bootstrap initialization"""
        bootstrap = SystemBootstrap()
        assert bootstrap is not None
        assert not bootstrap.is_initialized
    
    def test_bootstrap_with_config(self):
        """Test bootstrap with config"""
        config = BootstrapConfig(
            parallel_init=True,
            fail_fast=True
        )
        bootstrap = SystemBootstrap(config=config)
        assert bootstrap.config.parallel_init is True
        assert bootstrap.config.fail_fast is True
    
    def test_service_registry(self):
        """Test service registry"""
        registry = ServiceRegistry()
        
        # Create a simple service class
        class TestService:
            pass
        
        definition = ServiceDefinition(
            name="test_service",
            service_class=TestService
        )
        
        registry.register(definition)
        assert registry.get_definition("test_service") is not None
    
    def test_dependency_injector(self):
        """Test dependency injector"""
        injector = DependencyInjector()
        
        class TestClass:
            pass
        
        injector.bind("test", TestClass)
        assert injector.has_binding("test")
        
        instance = injector.resolve("test")
        assert instance is not None
    
    def test_bootstrap_initialize(self):
        """Test bootstrap initialize"""
        bootstrap = SystemBootstrap()
        
        class SimpleService:
            pass
        
        bootstrap.register_service(ServiceDefinition(
            name="simple",
            service_class=SimpleService
        ))
        
        result = bootstrap.initialize()
        assert result is True
        assert bootstrap.is_initialized
    
    def test_bootstrap_health_check(self):
        """Test bootstrap health check"""
        bootstrap = SystemBootstrap()
        bootstrap.initialize()
        
        health = bootstrap.health_check()
        assert "healthy" in health
        assert "services" in health


class TestPhaseOrchestrator:
    """Test PhaseOrchestrator"""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initialization"""
        orchestrator = PhaseOrchestrator()
        assert orchestrator is not None
        
        phases = orchestrator.get_all_phases()
        assert len(phases) == 13
    
    def test_orchestrator_execution_order(self):
        """Test execution order"""
        orchestrator = PhaseOrchestrator()
        order = orchestrator.get_execution_order()
        
        assert len(order) == 13
        # Phase 1 should be first (no dependencies)
        assert order[0] == "phase_1"
    
    def test_orchestrator_can_execute(self):
        """Test can execute check"""
        orchestrator = PhaseOrchestrator()
        
        # Phase 1 can execute (no dependencies)
        assert orchestrator.can_execute("phase_1") is True
        
        # Phase 2 cannot execute (depends on phase_1)
        assert orchestrator.can_execute("phase_2") is False
    
    def test_orchestrator_execute_phase(self):
        """Test execute phase"""
        orchestrator = PhaseOrchestrator()
        
        result = orchestrator.execute_phase("phase_1")
        assert result.state == PhaseState.COMPLETED
        assert result.phase_id == "phase_1"
    
    def test_orchestrator_transitions(self):
        """Test phase transitions"""
        orchestrator = PhaseOrchestrator()
        
        transition = orchestrator.transition("phase_1", "phase_2", "auto")
        assert transition.from_phase == "phase_1"
        assert transition.to_phase == "phase_2"
    
    def test_orchestrator_reset(self):
        """Test phase reset"""
        orchestrator = PhaseOrchestrator()
        orchestrator.execute_phase("phase_1")
        
        result = orchestrator.reset_phase("phase_1")
        assert result is True
        assert orchestrator.get_state("phase_1") == PhaseState.PENDING
    
    def test_orchestrator_summary(self):
        """Test execution summary"""
        orchestrator = PhaseOrchestrator()
        summary = orchestrator.get_summary()
        
        assert "total_phases" in summary
        assert summary["total_phases"] == 13


class TestAutomationPipeline:
    """Test AutomationPipeline"""
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization"""
        pipeline = AutomationPipeline()
        assert pipeline is not None
    
    def test_pipeline_with_config(self):
        """Test pipeline with config"""
        config = PipelineConfig(
            max_concurrent_tasks=10,
            dry_run=True
        )
        pipeline = AutomationPipeline(config=config)
        assert pipeline.config.max_concurrent_tasks == 10
        assert pipeline.config.dry_run is True
    
    def test_pipeline_submit_task(self):
        """Test task submission"""
        pipeline = AutomationPipeline()
        
        task = PipelineTask(
            name="test_task",
            task_type="natural_language"
        )
        
        task_id = pipeline.submit_task(task)
        assert task_id is not None
    
    def test_pipeline_route_task(self):
        """Test task routing"""
        pipeline = AutomationPipeline()
        
        # Test natural language routing
        task1 = PipelineTask(task_type="natural_language")
        phases1 = pipeline.route_task(task1)
        assert "phase_1" in phases1
        assert "phase_2" in phases1
        
        # Test training routing (Phase 7)
        task2 = PipelineTask(task_type="training")
        phases2 = pipeline.route_task(task2)
        assert "phase_7" in phases2
        
        # Test expert consultation routing (Phase 7)
        task3 = PipelineTask(task_type="expert_consultation")
        phases3 = pipeline.route_task(task3)
        assert "phase_7" in phases3
    
    def test_pipeline_execute_task(self):
        """Test task execution"""
        config = PipelineConfig(dry_run=True)
        pipeline = AutomationPipeline(config=config)
        
        task = PipelineTask(
            name="test_task",
            task_type="monitoring"
        )
        
        result = pipeline.execute_task(task)
        assert result.status == TaskStatus.COMPLETED
    
    def test_pipeline_metrics(self):
        """Test pipeline metrics"""
        pipeline = AutomationPipeline()
        metrics = pipeline.get_metrics()
        
        assert "tasks_submitted" in metrics
        assert "tasks_completed" in metrics
    
    def test_pipeline_queue_status(self):
        """Test queue status"""
        pipeline = AutomationPipeline()
        status = pipeline.get_queue_status()
        
        assert "queued" in status
        assert "running" in status
        assert "completed" in status


class TestPhaseIntegration:
    """Test phase integration"""
    
    def test_all_phases_defined(self):
        """Test all 13 phases are defined"""
        core = SynergyMeshCore()
        phases = core.get_all_phases()
        
        for i in range(1, 14):
            phase_id = f"phase_{i}"
            assert phase_id in phases, f"Missing {phase_id}"
    
    def test_all_task_types_routed(self):
        """Test all task types are routed correctly"""
        core = SynergyMeshCore()
        core.initialize()
        core.start()
        
        task_types = [
            ("natural_language", ["phase_1", "phase_2"]),
            ("decision", ["phase_3", "phase_4"]),
            ("quality_check", ["phase_5", "phase_6"]),
            ("training", ["phase_7"]),
            ("expert_consultation", ["phase_7"]),
            ("knowledge_query", ["phase_7"]),
            ("execution", ["phase_8", "phase_9"]),
            ("safety_check", ["phase_10"]),
            ("circuit_breaker", ["phase_10"]),
            ("emergency_stop", ["phase_10"]),
            ("monitoring", ["phase_11"]),
            ("remediation", ["phase_11"]),
            ("ci_error", ["phase_12"]),
            ("auto_fix", ["phase_12"]),
            ("yaml_validation", ["phase_13"]),
            ("policy_check", ["phase_13"]),
            ("slsa_compliance", ["phase_13"]),
        ]
        
        for task_type, expected_phases in task_types:
            result = core.process_task({"type": task_type, "id": f"test_{task_type}"})
            for phase in expected_phases:
                assert phase in result["processed_by"], f"Task {task_type} missing {phase}"
