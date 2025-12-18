"""
Tests for SynergyMesh Core Components
測試 SynergyMesh 核心組件

Tests for:
- NaturalLanguageProcessor
- AutonomousCoordinator
- SelfEvolutionEngine
- EcosystemOrchestrator
"""

import pytest
import asyncio
import os
import sys
from datetime import datetime

# Add the intelligent-automation directory to path for imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from machinenativeops_core.natural_language_processor import (
    NaturalLanguageProcessor,
    IntentType,
    ParsedIntent
)
from machinenativeops_core.autonomous_coordinator import (
    AutonomousCoordinator,
    TaskPriority,
    TaskStatus,
    SystemHealth
)
from machinenativeops_core.self_evolution_engine import (
    SelfEvolutionEngine,
    EvolutionPhase,
    LearningType,
    OptimizationType
)
from machinenativeops_core.ecosystem_orchestrator import (
    EcosystemOrchestrator,
    SubsystemType,
    SubsystemStatus,
    MessageType,
    MessagePriority
)


# ============================================
# NaturalLanguageProcessor Tests
# ============================================

class TestNaturalLanguageProcessor:
    """Tests for NaturalLanguageProcessor"""
    
    @pytest.fixture
    def processor(self):
        """Create NaturalLanguageProcessor instance"""
        return NaturalLanguageProcessor()
    
    def test_initialization(self, processor):
        """Test processor initialization"""
        assert processor is not None
        assert processor.session_count == 0
        assert len(processor.conversation_context) == 0
    
    def test_detect_language_chinese(self, processor):
        """Test Chinese language detection"""
        query = "我需要將用戶資料從舊系統同步到新系統"
        language = processor.detect_language(query)
        assert language == "zh"
    
    def test_detect_language_english(self, processor):
        """Test English language detection"""
        query = "I need to migrate user data from the old system"
        language = processor.detect_language(query)
        assert language == "en"
    
    def test_parse_intent_data_migration_chinese(self, processor):
        """Test parsing data migration intent in Chinese"""
        query = "我需要將用戶資料從舊系統同步到新系統"
        intent = processor.parse_intent(query)
        
        assert intent is not None
        assert intent.intent_type == IntentType.DATA_MIGRATION
        assert intent.confidence > 0.5
        assert intent.language == "zh"
    
    def test_parse_intent_system_integration_english(self, processor):
        """Test parsing system integration intent in English"""
        query = "I want to integrate the payment API with our backend"
        intent = processor.parse_intent(query)
        
        assert intent is not None
        assert intent.intent_type == IntentType.SYSTEM_INTEGRATION
        assert intent.confidence > 0.5
        assert intent.language == "en"
    
    def test_parse_intent_code_analysis(self, processor):
        """Test parsing code analysis intent"""
        query = "請分析這段代碼的性能問題"
        intent = processor.parse_intent(query)
        
        assert intent is not None
        assert intent.intent_type == IntentType.CODE_ANALYSIS
    
    def test_parse_intent_monitoring(self, processor):
        """Test parsing monitoring intent"""
        query = "Set up monitoring for the production servers"
        intent = processor.parse_intent(query)
        
        assert intent is not None
        assert intent.intent_type == IntentType.MONITORING_SETUP
    
    def test_session_context_management(self, processor):
        """Test session context management"""
        session_id = "test-session"
        
        processor.parse_intent("First query about migration", session_id)
        processor.parse_intent("Second query about integration", session_id)
        
        assert session_id in processor.conversation_context
        assert len(processor.conversation_context[session_id]) == 2
    
    def test_clear_session(self, processor):
        """Test clearing session context"""
        session_id = "test-session"
        processor.parse_intent("Test query", session_id)
        
        assert session_id in processor.conversation_context
        
        result = processor.clear_session(session_id)
        assert result is True
        assert session_id not in processor.conversation_context
    
    @pytest.mark.asyncio
    async def test_translate_to_technical_spec(self, processor):
        """Test translating intent to technical specification"""
        intent = ParsedIntent(
            intent_type=IntentType.DATA_MIGRATION,
            confidence=0.9,
            entities={"source_system": "old_db", "target_system": "new_db"},
            raw_query="Migrate data from old to new",
            language="en"
        )
        
        spec = await processor.translate_to_technical_spec(intent)
        
        assert spec is not None
        assert spec.spec_id.startswith("SPEC-")
        assert len(spec.tasks) > 0
        assert spec.automation_level in ["full", "partial", "manual"]
    
    @pytest.mark.asyncio
    async def test_process_natural_request(self, processor):
        """Test end-to-end natural request processing"""
        query = "I want to migrate data from MySQL to PostgreSQL"
        
        result = await processor.process_natural_request(query)
        
        assert result["status"] == "success"
        assert "intent" in result
        assert "specification" in result
        assert "message" in result
        assert result["specification"]["tasks"]
    
    def test_get_statistics(self, processor):
        """Test getting processor statistics"""
        processor.parse_intent("Test query 1")
        processor.parse_intent("Test query 2")
        
        stats = processor.get_statistics()
        
        assert "total_sessions" in stats
        assert "total_intents_processed" in stats


# ============================================
# AutonomousCoordinator Tests
# ============================================

class TestAutonomousCoordinator:
    """Tests for AutonomousCoordinator"""
    
    @pytest.fixture
    def coordinator(self):
        """Create AutonomousCoordinator instance"""
        return AutonomousCoordinator(worker_count=2)
    
    def test_initialization(self, coordinator):
        """Test coordinator initialization"""
        assert coordinator is not None
        assert coordinator.worker_count == 2
        assert coordinator.is_running is False
        assert len(coordinator.task_queue) == 0
    
    def test_schedule_task(self, coordinator):
        """Test scheduling a task"""
        task_id = coordinator.schedule_task(
            name="Test Task",
            description="A test task",
            task_type="test",
            params={"key": "value"},
            priority=TaskPriority.HIGH
        )
        
        assert task_id.startswith("task-")
        assert len(coordinator.task_queue) == 1
    
    def test_schedule_task_priority(self, coordinator):
        """Test task priority ordering"""
        coordinator.schedule_task(
            name="Low Priority",
            description="Low",
            task_type="test",
            params={},
            priority=TaskPriority.LOW
        )
        coordinator.schedule_task(
            name="High Priority",
            description="High",
            task_type="test",
            params={},
            priority=TaskPriority.HIGH
        )
        
        # High priority should be at top of heap
        assert coordinator.task_queue[0].priority == TaskPriority.HIGH
    
    def test_register_task_handler(self, coordinator):
        """Test registering task handler"""
        async def handler(**kwargs):
            return {"result": "success"}
        
        coordinator.register_task_handler("custom", handler)
        assert "custom" in coordinator._task_handlers
    
    @pytest.mark.asyncio
    async def test_start_stop(self, coordinator):
        """Test starting and stopping coordinator"""
        await coordinator.start()
        
        assert coordinator.is_running is True
        assert len(coordinator.workers) > 0
        
        await coordinator.stop()
        
        assert coordinator.is_running is False
    
    @pytest.mark.asyncio
    async def test_task_execution(self, coordinator):
        """Test task execution"""
        result_holder = {"executed": False}
        
        async def test_handler(**kwargs):
            result_holder["executed"] = True
            return {"status": "done"}
        
        coordinator.register_task_handler("execute_test", test_handler)
        
        await coordinator.start()
        
        task_id = coordinator.schedule_task(
            name="Execute Test",
            description="Test execution",
            task_type="execute_test",
            params={}
        )
        
        # Wait for task to complete
        await asyncio.sleep(0.5)
        
        assert result_holder["executed"] is True
        
        await coordinator.stop()
    
    def test_get_task_status(self, coordinator):
        """Test getting task status"""
        task_id = coordinator.schedule_task(
            name="Status Test",
            description="Test",
            task_type="test",
            params={}
        )
        
        status = coordinator.get_task_status(task_id)
        
        assert status is not None
        assert status["task_id"] == task_id
        assert status["status"] in ["pending", "scheduled"]
    
    def test_get_statistics(self, coordinator):
        """Test getting coordinator statistics"""
        stats = coordinator.get_statistics()
        
        assert "is_running" in stats
        assert "queue_size" in stats
        assert "tasks_processed" in stats
        assert "success_rate" in stats
    
    def test_get_health_report(self, coordinator):
        """Test getting health report"""
        health = coordinator.get_health_report()
        
        assert "overall_health" in health
        assert "checks" in health
        assert "recent_recoveries" in health


# ============================================
# SelfEvolutionEngine Tests
# ============================================

class TestSelfEvolutionEngine:
    """Tests for SelfEvolutionEngine"""
    
    @pytest.fixture
    def engine(self):
        """Create SelfEvolutionEngine instance"""
        return SelfEvolutionEngine()
    
    def test_initialization(self, engine):
        """Test engine initialization"""
        assert engine is not None
        assert engine.current_phase == EvolutionPhase.IDLE
        assert engine.is_evolving is False
    
    def test_record_learning(self, engine):
        """Test recording a learning event"""
        record_id = engine.record_learning(
            learning_type=LearningType.USER_INTERACTION,
            data={"action": "click", "target": "button"},
            confidence=0.8
        )
        
        assert record_id.startswith("learn-")
        assert len(engine.learning_records) == 1
        assert engine.stats["total_learnings"] == 1
    
    def test_record_learning_with_insights(self, engine):
        """Test recording learning with insights"""
        insights = ["Pattern detected", "Optimization possible"]
        record_id = engine.record_learning(
            learning_type=LearningType.ERROR_PATTERN,
            data={"error": "timeout"},
            insights=insights,
            confidence=0.9
        )
        
        record = engine.learning_records[0]
        assert record.insights == insights
    
    def test_pattern_memory_storage(self, engine):
        """Test pattern memory storage"""
        engine.record_learning(
            learning_type=LearningType.PERFORMANCE_METRIC,
            data={"metric": "response_time", "value": 100}
        )
        engine.record_learning(
            learning_type=LearningType.PERFORMANCE_METRIC,
            data={"metric": "response_time", "value": 150}
        )
        
        assert LearningType.PERFORMANCE_METRIC.value in engine.pattern_memory
        assert len(engine.pattern_memory[LearningType.PERFORMANCE_METRIC.value]) == 2
    
    def test_register_evolution_handler(self, engine):
        """Test registering evolution handler"""
        async def handler(action):
            return True
        
        engine.register_evolution_handler("performance", handler)
        assert "performance" in engine._evolution_handlers
    
    def test_register_validation_handler(self, engine):
        """Test registering validation handler"""
        async def handler():
            return {"passed": True}
        
        engine.register_validation_handler("system", handler)
        assert "system" in engine._validation_handlers
    
    @pytest.mark.asyncio
    async def test_evolution_cycle_basic(self, engine):
        """Test basic evolution cycle"""
        # Record enough learning events
        for i in range(15):
            engine.record_learning(
                learning_type=LearningType.USER_INTERACTION,
                data={"action": f"action_{i}"},
                confidence=0.7
            )
        
        cycle_id = await engine.start_evolution_cycle()
        
        assert cycle_id.startswith("cycle-")
        assert engine.stats["total_evolutions"] == 1
        assert engine.current_phase == EvolutionPhase.IDLE
    
    def test_get_evolution_status(self, engine):
        """Test getting evolution status"""
        status = engine.get_evolution_status()
        
        assert "is_evolving" in status
        assert "current_phase" in status
        assert "learning_records_count" in status
    
    def test_get_statistics(self, engine):
        """Test getting engine statistics"""
        stats = engine.get_statistics()
        
        assert "total_learnings" in stats
        assert "total_evolutions" in stats
        assert "success_rate" in stats
    
    def test_get_optimization_history(self, engine):
        """Test getting optimization history"""
        history = engine.get_optimization_history()
        
        assert isinstance(history, list)


# ============================================
# EcosystemOrchestrator Tests
# ============================================

class TestEcosystemOrchestrator:
    """Tests for EcosystemOrchestrator"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create EcosystemOrchestrator instance"""
        return EcosystemOrchestrator()
    
    def test_initialization(self, orchestrator):
        """Test orchestrator initialization"""
        assert orchestrator is not None
        assert orchestrator.is_running is False
        assert len(orchestrator.subsystems) == 0
    
    def test_register_subsystem(self, orchestrator):
        """Test registering a subsystem"""
        subsystem_id = orchestrator.register_subsystem(
            name="Test Subsystem",
            subsystem_type=SubsystemType.CUSTOM,
            capabilities=["test_capability"]
        )
        
        assert subsystem_id.startswith("sub-")
        assert subsystem_id in orchestrator.subsystems
        assert orchestrator.stats["subsystem_registrations"] == 1
    
    def test_register_subsystem_with_capabilities(self, orchestrator):
        """Test capability indexing during registration"""
        orchestrator.register_subsystem(
            name="Analysis Subsystem",
            subsystem_type=SubsystemType.CODE_ANALYZER,
            capabilities=["code_analysis", "security_scan"]
        )
        
        assert "code_analysis" in orchestrator._capability_index
        assert "security_scan" in orchestrator._capability_index
    
    def test_unregister_subsystem(self, orchestrator):
        """Test unregistering a subsystem"""
        subsystem_id = orchestrator.register_subsystem(
            name="Temp Subsystem",
            subsystem_type=SubsystemType.CUSTOM,
            capabilities=["temp_capability"]
        )
        
        result = orchestrator.unregister_subsystem(subsystem_id)
        
        assert result is True
        assert subsystem_id not in orchestrator.subsystems
        assert "temp_capability" not in orchestrator._capability_index or \
               subsystem_id not in orchestrator._capability_index.get("temp_capability", set())
    
    def test_find_subsystems_by_capability(self, orchestrator):
        """Test finding subsystems by capability"""
        sub1 = orchestrator.register_subsystem(
            name="Sub 1",
            subsystem_type=SubsystemType.CUSTOM,
            capabilities=["shared_capability", "unique_1"]
        )
        sub2 = orchestrator.register_subsystem(
            name="Sub 2",
            subsystem_type=SubsystemType.CUSTOM,
            capabilities=["shared_capability", "unique_2"]
        )
        
        found = orchestrator.find_subsystems_by_capability("shared_capability")
        
        assert len(found) == 2
        assert sub1 in found
        assert sub2 in found
    
    @pytest.mark.asyncio
    async def test_send_message(self, orchestrator):
        """Test sending messages between subsystems"""
        sub1 = orchestrator.register_subsystem(
            name="Sender",
            subsystem_type=SubsystemType.CUSTOM,
            capabilities=[]
        )
        sub2 = orchestrator.register_subsystem(
            name="Receiver",
            subsystem_type=SubsystemType.CUSTOM,
            capabilities=[]
        )
        
        message_id = await orchestrator.send_message(
            source_id=sub1,
            target_id=sub2,
            message_type=MessageType.REQUEST,
            payload={"data": "test"}
        )
        
        assert message_id.startswith("msg-")
        assert orchestrator.stats["messages_sent"] == 1
    
    def test_update_subsystem_status(self, orchestrator):
        """Test updating subsystem status"""
        subsystem_id = orchestrator.register_subsystem(
            name="Status Test",
            subsystem_type=SubsystemType.CUSTOM,
            capabilities=[]
        )
        
        result = orchestrator.update_subsystem_status(
            subsystem_id,
            SubsystemStatus.ACTIVE
        )
        
        assert result is True
        assert orchestrator.subsystems[subsystem_id].status == SubsystemStatus.ACTIVE
    
    def test_allocate_resource(self, orchestrator):
        """Test resource allocation"""
        subsystem_id = orchestrator.register_subsystem(
            name="Resource Test",
            subsystem_type=SubsystemType.CUSTOM,
            capabilities=[]
        )
        
        allocation_id = orchestrator.allocate_resource(
            subsystem_id=subsystem_id,
            resource_type="cpu",
            amount=0.5
        )
        
        assert allocation_id.startswith("alloc-")
        assert subsystem_id in orchestrator.resource_allocations
    
    @pytest.mark.asyncio
    async def test_start_stop(self, orchestrator):
        """Test starting and stopping orchestrator"""
        orchestrator.register_subsystem(
            name="Test",
            subsystem_type=SubsystemType.CUSTOM,
            capabilities=[]
        )
        
        await orchestrator.start()
        
        assert orchestrator.is_running is True
        
        await orchestrator.stop()
        
        assert orchestrator.is_running is False
    
    def test_get_ecosystem_status(self, orchestrator):
        """Test getting ecosystem status"""
        orchestrator.register_subsystem(
            name="Test",
            subsystem_type=SubsystemType.CUSTOM,
            capabilities=["test"]
        )
        
        status = orchestrator.get_ecosystem_status()
        
        assert "is_running" in status
        assert "total_subsystems" in status
        assert "capabilities_available" in status
        assert "test" in status["capabilities_available"]
    
    def test_get_subsystem_info(self, orchestrator):
        """Test getting subsystem info"""
        subsystem_id = orchestrator.register_subsystem(
            name="Info Test",
            subsystem_type=SubsystemType.CODE_ANALYZER,
            capabilities=["analysis"]
        )
        
        info = orchestrator.get_subsystem_info(subsystem_id)
        
        assert info is not None
        assert info["name"] == "Info Test"
        assert info["type"] == "code_analyzer"
        assert "analysis" in info["capabilities"]
    
    def test_list_subsystems(self, orchestrator):
        """Test listing all subsystems"""
        orchestrator.register_subsystem(
            name="Sub 1",
            subsystem_type=SubsystemType.CUSTOM,
            capabilities=[]
        )
        orchestrator.register_subsystem(
            name="Sub 2",
            subsystem_type=SubsystemType.CUSTOM,
            capabilities=[]
        )
        
        subsystems = orchestrator.list_subsystems()
        
        assert len(subsystems) == 2


# ============================================
# Integration Tests
# ============================================

class TestSynergyMeshIntegration:
    """Integration tests for SynergyMesh core components"""
    
    @pytest.mark.asyncio
    async def test_full_pipeline_integration(self):
        """Test integration of all core components"""
        # Initialize all components
        nlp = NaturalLanguageProcessor()
        coordinator = AutonomousCoordinator(worker_count=2)
        evolution = SelfEvolutionEngine()
        orchestrator = EcosystemOrchestrator()
        
        # Register subsystems in orchestrator
        nlp_id = orchestrator.register_subsystem(
            name="NLP Processor",
            subsystem_type=SubsystemType.LANGUAGE_PROCESSOR,
            capabilities=["natural_language", "intent_detection"]
        )
        
        coord_id = orchestrator.register_subsystem(
            name="Coordinator",
            subsystem_type=SubsystemType.AUTONOMOUS_COORDINATOR,
            capabilities=["task_scheduling", "monitoring"]
        )
        
        # Start components
        await coordinator.start()
        await orchestrator.start()
        
        # Process a natural language request
        result = await nlp.process_natural_request(
            "I need to analyze and optimize this code"
        )
        
        assert result["status"] == "success"
        
        # Record learning from interaction
        evolution.record_learning(
            learning_type=LearningType.USER_INTERACTION,
            data={
                "request": result["intent"]["type"],
                "success": True
            },
            confidence=0.9
        )
        
        # Send coordination message
        await orchestrator.send_message(
            source_id=nlp_id,
            target_id=coord_id,
            message_type=MessageType.REQUEST,
            payload={"spec": result["specification"]}
        )
        
        # Clean up
        await coordinator.stop()
        await orchestrator.stop()
        
        # Verify statistics
        assert evolution.stats["total_learnings"] > 0
        assert orchestrator.stats["messages_sent"] > 0


# ============================================
# Phase 2 Tests - NLI Layer
# ============================================

from machinenativeops_core.nli_layer import (
    NaturalLanguageInteractionLayer,
    InteractionMode,
    UserIntent
)
from machinenativeops_core.orchestration_layer import (
    IntentUnderstandingEngine,
    TaskOrchestrationEngine,
    TaskType,
    WorkflowStatus
)


class TestNaturalLanguageInteractionLayer:
    """Tests for NaturalLanguageInteractionLayer"""
    
    @pytest.fixture
    def nli(self):
        """Create NLI instance"""
        return NaturalLanguageInteractionLayer()
    
    def test_initialization(self, nli):
        """Test NLI initialization"""
        assert nli is not None
        assert len(nli.sessions) == 0
    
    def test_create_session(self, nli):
        """Test session creation"""
        session_id = nli.create_session(user_id="test-user")
        
        assert session_id.startswith("session-")
        assert session_id in nli.sessions
    
    def test_create_session_with_preferences(self, nli):
        """Test session creation with preferences"""
        session_id = nli.create_session(
            user_id="test-user",
            mode=InteractionMode.TEXT,
            language="zh",
            preferences={"theme": "dark"}
        )
        
        context = nli.get_session(session_id)
        assert context is not None
        assert context.language == "zh"
        assert context.preferences["theme"] == "dark"
    
    @pytest.mark.asyncio
    async def test_process_text_input_chinese(self, nli):
        """Test processing Chinese text input"""
        session_id = nli.create_session()
        
        result = await nli.process_text_input(
            session_id,
            "我需要遷移資料"
        )
        
        assert result.success is True
        assert result.intent == UserIntent.COMMAND
        assert result.confidence > 0
    
    @pytest.mark.asyncio
    async def test_process_text_input_english(self, nli):
        """Test processing English text input"""
        session_id = nli.create_session()
        
        result = await nli.process_text_input(
            session_id,
            "Help me with data migration"
        )
        
        assert result.success is True
    
    @pytest.mark.asyncio
    async def test_process_help_request(self, nli):
        """Test processing help request"""
        session_id = nli.create_session()
        
        result = await nli.process_text_input(session_id, "幫助")
        
        assert result.intent == UserIntent.HELP
        assert len(result.suggested_actions) > 0
    
    def test_register_visual_component(self, nli):
        """Test registering visual components"""
        comp_id = nli.register_visual_component(
            component_type="source",
            label="Data Source",
            description="Source connection"
        )
        
        assert comp_id.startswith("comp-")
        assert comp_id in nli.visual_components
    
    def test_get_available_components(self, nli):
        """Test getting available components"""
        nli.register_visual_component("source", "Source", "Data source")
        nli.register_visual_component("target", "Target", "Data target")
        
        components = nli.get_available_components()
        
        assert len(components) == 2
    
    def test_create_visual_workflow(self, nli):
        """Test creating visual workflow"""
        workflow = nli.create_visual_workflow(
            name="Test Workflow",
            components=[{"type": "source"}, {"type": "target"}]
        )
        
        assert workflow["workflow_id"].startswith("workflow-")
        assert workflow["name"] == "Test Workflow"
    
    def test_get_statistics(self, nli):
        """Test getting NLI statistics"""
        stats = nli.get_statistics()
        
        assert "total_interactions" in stats
        assert "mode_usage" in stats
        assert "active_sessions" in stats
    
    def test_close_session(self, nli):
        """Test closing session"""
        session_id = nli.create_session()
        
        result = nli.close_session(session_id)
        
        assert result is True
        assert session_id not in nli.sessions


# ============================================
# Phase 2 Tests - Orchestration Layer
# ============================================

class TestIntentUnderstandingEngine:
    """Tests for IntentUnderstandingEngine"""
    
    @pytest.fixture
    def intent_engine(self):
        """Create IntentUnderstandingEngine instance"""
        return IntentUnderstandingEngine()
    
    def test_initialization(self, intent_engine):
        """Test engine initialization"""
        assert intent_engine is not None
        assert intent_engine.stats["intents_parsed"] == 0
    
    def test_parse_intent_migration_chinese(self, intent_engine):
        """Test parsing migration intent in Chinese"""
        intent = intent_engine.parse_intent(
            "我需要將資料從舊系統遷移到新系統"
        )
        
        assert intent.task_type == TaskType.DATA_MIGRATION
        assert intent.confidence > 0.5
        assert intent.language == "zh"
    
    def test_parse_intent_sync_english(self, intent_engine):
        """Test parsing sync intent in English"""
        intent = intent_engine.parse_intent(
            "Synchronize data between databases"
        )
        
        assert intent.task_type == TaskType.DATA_SYNC
        assert intent.language == "en"
    
    def test_parse_intent_deployment(self, intent_engine):
        """Test parsing deployment intent"""
        intent = intent_engine.parse_intent("Deploy to production")
        
        assert intent.task_type == TaskType.DEPLOYMENT
    
    def test_entity_extraction(self, intent_engine):
        """Test entity extraction"""
        intent = intent_engine.parse_intent(
            "Migrate data from mysql to postgresql"
        )
        
        assert "source" in intent.entities or "target" in intent.entities
    
    def test_priority_detection(self, intent_engine):
        """Test priority detection"""
        intent = intent_engine.parse_intent(
            "Urgent: deploy the application immediately"
        )
        
        assert intent.priority == "high"
    
    def test_context_memory(self, intent_engine):
        """Test context memory management"""
        user_id = "test-user"
        
        intent_engine.parse_intent("Migrate data", user_id=user_id)
        intent_engine.parse_intent("Deploy app", user_id=user_id)
        
        memory = intent_engine.get_context_memory(user_id)
        
        assert memory is not None
        assert len(memory.last_intents) == 2
    
    def test_get_statistics(self, intent_engine):
        """Test getting statistics"""
        intent_engine.parse_intent("Test query")
        
        stats = intent_engine.get_statistics()
        
        assert stats["intents_parsed"] == 1
        assert "intent_distribution" in stats


class TestTaskOrchestrationEngine:
    """Tests for TaskOrchestrationEngine"""
    
    @pytest.fixture
    def orchestration_engine(self):
        """Create TaskOrchestrationEngine instance"""
        return TaskOrchestrationEngine()
    
    @pytest.fixture
    def intent_engine(self):
        """Create IntentUnderstandingEngine instance"""
        return IntentUnderstandingEngine()
    
    def test_initialization(self, orchestration_engine):
        """Test engine initialization"""
        assert orchestration_engine is not None
        assert orchestration_engine.stats["workflows_created"] == 0
    
    def test_generate_workflow_migration(self, orchestration_engine, intent_engine):
        """Test generating workflow for migration"""
        intent = intent_engine.parse_intent("Migrate data from old to new system")
        
        workflow = orchestration_engine.generate_workflow(intent)
        
        assert workflow.workflow_id.startswith("wf-")
        assert len(workflow.steps) > 0
        assert workflow.status == WorkflowStatus.DRAFT
    
    def test_generate_workflow_deployment(self, orchestration_engine, intent_engine):
        """Test generating workflow for deployment"""
        intent = intent_engine.parse_intent("Deploy application")
        
        workflow = orchestration_engine.generate_workflow(intent)
        
        assert len(workflow.steps) >= 3  # Build, test, deploy
    
    @pytest.mark.asyncio
    async def test_execute_workflow(self, orchestration_engine, intent_engine):
        """Test executing a workflow"""
        intent = intent_engine.parse_intent("Analyze code")
        workflow = orchestration_engine.generate_workflow(intent)
        
        result = await orchestration_engine.execute_workflow(workflow.workflow_id)
        
        assert result["status"] == "completed"
        assert orchestration_engine.stats["workflows_completed"] == 1
    
    def test_get_workflow_status(self, orchestration_engine, intent_engine):
        """Test getting workflow status"""
        intent = intent_engine.parse_intent("Deploy app")
        workflow = orchestration_engine.generate_workflow(intent)
        
        status = orchestration_engine.get_workflow_status(workflow.workflow_id)
        
        assert status is not None
        assert status["workflow_id"] == workflow.workflow_id
        assert "steps" in status
    
    def test_register_step_handler(self, orchestration_engine):
        """Test registering step handler"""
        async def custom_handler(step):
            return {"status": "custom"}
        
        orchestration_engine.register_step_handler("Custom Step", custom_handler)
        
        assert "Custom Step" in orchestration_engine.step_handlers
    
    def test_get_statistics(self, orchestration_engine):
        """Test getting statistics"""
        stats = orchestration_engine.get_statistics()
        
        assert "workflows_created" in stats
        assert "success_rate" in stats


# ============================================
# Phase 2 Integration Tests
# ============================================

class TestPhase2Integration:
    """Integration tests for Phase 2 components"""
    
    @pytest.mark.asyncio
    async def test_full_phase2_pipeline(self):
        """Test complete Phase 2 pipeline from NLI to workflow execution"""
        # Initialize components
        nli = NaturalLanguageInteractionLayer()
        intent_engine = IntentUnderstandingEngine()
        orchestration_engine = TaskOrchestrationEngine()
        
        # Create session
        session_id = nli.create_session(user_id="integration-test")
        
        # Process natural language input
        nli_result = await nli.process_text_input(
            session_id,
            "我需要將用戶資料從舊系統遷移到新系統"
        )
        
        assert nli_result.success is True
        
        # Parse intent
        intent = intent_engine.parse_intent(
            nli_result.response_data.get("action", "data migration")
        )
        
        # Generate and execute workflow
        workflow = orchestration_engine.generate_workflow(intent)
        result = await orchestration_engine.execute_workflow(workflow.workflow_id)
        
        assert result["status"] == "completed"
        
        # Clean up
        nli.close_session(session_id)
        
        # Verify statistics
        assert nli.stats["total_interactions"] > 0
        assert intent_engine.stats["intents_parsed"] > 0
        assert orchestration_engine.stats["workflows_completed"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
