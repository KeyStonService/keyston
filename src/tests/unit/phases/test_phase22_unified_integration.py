"""
Tests for Phase 22: Unified System Integration

Comprehensive tests for the unified integration layer that connects
all SynergyMesh phases into a cohesive system.
"""

import asyncio
import pytest
from datetime import datetime, timezone

import sys
sys.path.insert(0, str(__file__).rsplit('/tests', 1)[0] + '/core')

from unified_integration import (
    UnifiedSystemController,
    IntegrationHub,
    IntegrationConfig,
    SystemOrchestrator,
    OrchestratorConfig,
    ConfigurationManager,
    SystemConfiguration,
)
from unified_integration.unified_controller import (
    SystemState,
    PhaseCategory,
    PhaseDefinition,
)
from unified_integration.integration_hub import (
    MessageType,
    MessagePriority,
)
from unified_integration.system_orchestrator import (
    WorkflowState,
    TaskType,
)
from unified_integration.configuration_manager import (
    Environment,
    PhaseConfig,
)


# ==================== UnifiedSystemController Tests ====================

class TestUnifiedSystemController:
    """Tests for UnifiedSystemController"""
    
    @pytest.fixture
    def controller(self):
        """Create a UnifiedSystemController instance"""
        return UnifiedSystemController()
        
    def test_initialization(self, controller):
        """Test controller initialization"""
        assert controller._state == SystemState.OFFLINE
        assert len(controller._phases) == 22
        assert not controller._is_running
        
    def test_phase_definitions(self, controller):
        """Test all 22 phases are defined"""
        assert len(controller.PHASE_DEFINITIONS) == 22
        
        # Check specific phases
        phase_1 = controller._get_phase_definition(1)
        assert phase_1 is not None
        assert phase_1.name == "Core Autonomous Coordination"
        assert phase_1.critical is True
        
        phase_22 = controller._get_phase_definition(22)
        assert phase_22 is not None
        assert phase_22.name == "Unified System Integration"
        assert phase_22.category == PhaseCategory.UNIFIED_INTEGRATION
        
    @pytest.mark.asyncio
    async def test_initialize(self, controller):
        """Test system initialization"""
        result = await controller.initialize()
        
        assert result is True
        assert controller._state == SystemState.READY
        
        # Check all phases initialized
        for phase_state in controller._phases.values():
            assert phase_state.status == 'initialized'
            
    @pytest.mark.asyncio
    async def test_start(self, controller):
        """Test system start"""
        await controller.initialize()
        result = await controller.start()
        
        assert result is True
        assert controller._state == SystemState.RUNNING
        assert controller._is_running is True
        
    @pytest.mark.asyncio
    async def test_stop(self, controller):
        """Test system stop"""
        await controller.initialize()
        await controller.start()
        result = await controller.stop()
        
        assert result is True
        assert controller._state == SystemState.OFFLINE
        assert controller._is_running is False
        
    @pytest.mark.asyncio
    async def test_process_request(self, controller):
        """Test request processing"""
        await controller.initialize()
        await controller.start()
        
        request = {
            'type': 'natural_language',
            'payload': {'text': 'Hello, SynergyMesh'}
        }
        
        result = await controller.process_request(request)
        
        assert result['success'] is True
        assert 'request_id' in result
        assert result['phases_invoked'] == [1, 2]
        
    @pytest.mark.asyncio
    async def test_request_routing(self, controller):
        """Test request routing to correct phases"""
        await controller.initialize()
        await controller.start()
        
        # Test different request types
        test_cases = [
            ('decision', [3, 4]),
            ('safety_check', [10]),
            ('monitoring', [11]),
            ('mcp_tool', [19]),
            ('provenance', [20]),
            ('cloud_delegation', [21]),
        ]
        
        for request_type, expected_phases in test_cases:
            request = {'type': request_type}
            result = await controller.process_request(request)
            assert result['phases_invoked'] == expected_phases
            
    def test_get_system_status(self, controller):
        """Test system status retrieval"""
        status = controller.get_system_status()
        
        assert 'state' in status
        assert 'phases' in status
        assert 'metrics' in status
        assert 'health' in status
        assert len(status['phases']) == 22
        
    def test_get_phase_status(self, controller):
        """Test individual phase status"""
        status = controller.get_phase_status(1)
        
        assert status is not None
        assert status['id'] == 1
        assert status['name'] == "Core Autonomous Coordination"
        assert status['critical'] is True
        
    def test_event_handling(self, controller):
        """Test event registration and handling"""
        events_received = []
        
        def handler(data):
            events_received.append(data)
            
        controller.on('test_event', handler)
        
        # Manually emit event
        asyncio.run(controller._emit_event('test_event', {'test': True}))
        
        assert len(events_received) == 1
        assert events_received[0]['test'] is True


# ==================== IntegrationHub Tests ====================

class TestIntegrationHub:
    """Tests for IntegrationHub"""
    
    @pytest.fixture
    def hub(self):
        """Create an IntegrationHub instance"""
        return IntegrationHub()
        
    @pytest.fixture
    def config(self):
        """Create an IntegrationConfig"""
        return IntegrationConfig(
            name='test-hub',
            max_queue_size=100,
            message_timeout_seconds=10
        )
        
    def test_initialization(self, hub):
        """Test hub initialization"""
        assert hub.config.name == 'synergymesh-hub'
        assert not hub._is_running
        
    @pytest.mark.asyncio
    async def test_start_stop(self, hub):
        """Test hub start and stop"""
        await hub.start()
        assert hub._is_running is True
        
        await hub.stop()
        assert hub._is_running is False
        
    def test_register_phase(self, hub):
        """Test phase registration"""
        hub.register_phase(1)
        hub.register_phase(2)
        
        assert 1 in hub._queues
        assert 2 in hub._queues
        
    def test_unregister_phase(self, hub):
        """Test phase unregistration"""
        hub.register_phase(1)
        hub.unregister_phase(1)
        
        assert 1 not in hub._queues
        
    @pytest.mark.asyncio
    async def test_send_message(self, hub):
        """Test message sending"""
        hub.register_phase(1)
        hub.register_phase(2)
        
        message_id = await hub.send_message(
            source_phase=1,
            target_phase=2,
            payload={'data': 'test'}
        )
        
        assert message_id is not None
        assert hub._messages_sent == 1
        assert hub._messages_delivered == 1
        
    @pytest.mark.asyncio
    async def test_broadcast(self, hub):
        """Test broadcast messaging"""
        events_received = []
        
        hub.register_phase(1)
        hub.register_phase(2)
        
        hub.subscribe(2, 'test.*', lambda data: events_received.append(data))
        
        count = await hub.broadcast(1, 'test.event', {'value': 42})
        
        assert count == 1
        assert len(events_received) == 1
        assert events_received[0]['data']['value'] == 42
        
    def test_subscribe_unsubscribe(self, hub):
        """Test subscription management"""
        hub.register_phase(1)
        
        sub_id = hub.subscribe(1, 'events.*', lambda x: None)
        assert sub_id in hub._subscriptions
        
        result = hub.unsubscribe(sub_id)
        assert result is True
        assert sub_id not in hub._subscriptions
        
    def test_get_stats(self, hub):
        """Test statistics retrieval"""
        hub.register_phase(1)
        hub.register_phase(2)
        
        stats = hub.get_stats()
        
        assert stats['registered_phases'] == 2
        assert stats['messages_sent'] == 0
        assert stats['is_running'] is False


# ==================== SystemOrchestrator Tests ====================

class TestSystemOrchestrator:
    """Tests for SystemOrchestrator"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create a SystemOrchestrator instance"""
        return SystemOrchestrator()
        
    @pytest.fixture
    def config(self):
        """Create an OrchestratorConfig"""
        return OrchestratorConfig(
            name='test-orchestrator',
            max_concurrent_workflows=5,
            max_concurrent_tasks=20
        )
        
    def test_initialization(self, orchestrator):
        """Test orchestrator initialization"""
        assert orchestrator.config.name == 'synergymesh-orchestrator'
        assert not orchestrator._is_running
        
    @pytest.mark.asyncio
    async def test_start_stop(self, orchestrator):
        """Test orchestrator start and stop"""
        await orchestrator.start()
        assert orchestrator._is_running is True
        
        await orchestrator.stop()
        assert orchestrator._is_running is False
        
    @pytest.mark.asyncio
    async def test_execute_workflow(self, orchestrator):
        """Test workflow execution"""
        await orchestrator.start()
        
        steps = [
            {'name': 'step1'},
            {'name': 'step2'},
            {'name': 'step3'}
        ]
        
        workflow = await orchestrator.execute_workflow(
            name='test-workflow',
            steps=steps
        )
        
        assert workflow.state == WorkflowState.COMPLETED
        assert 'step1' in workflow.results
        assert 'step2' in workflow.results
        assert 'step3' in workflow.results
        
        await orchestrator.stop()
        
    @pytest.mark.asyncio
    async def test_execute_workflow_async(self, orchestrator):
        """Test asynchronous workflow execution"""
        await orchestrator.start()
        
        steps = [{'name': 'async_step'}]
        
        workflow_id = await orchestrator.execute_workflow_async(
            name='async-workflow',
            steps=steps
        )
        
        assert workflow_id is not None
        
        # Wait for completion
        await asyncio.sleep(0.1)
        
        workflow = orchestrator.get_workflow(workflow_id)
        assert workflow is not None
        
        await orchestrator.stop()
        
    @pytest.mark.asyncio
    async def test_cancel_workflow(self, orchestrator):
        """Test workflow cancellation"""
        await orchestrator.start()
        
        # Create a long-running workflow
        async def long_task():
            await asyncio.sleep(10)
            
        steps = [{'name': 'long_step', 'handler': long_task}]
        
        workflow_id = await orchestrator.execute_workflow_async(
            name='cancellable-workflow',
            steps=steps
        )
        
        await asyncio.sleep(0.05)
        
        result = await orchestrator.cancel_workflow(workflow_id)
        assert result is True
        
        workflow = orchestrator.get_workflow(workflow_id)
        assert workflow.state == WorkflowState.CANCELLED
        
        await orchestrator.stop()
        
    def test_schedule_task(self, orchestrator):
        """Test task scheduling"""
        task_id = orchestrator.schedule_task(
            name='test-task',
            task_type=TaskType.HEALTH_CHECK,
            handler=lambda: None,
            interval_seconds=60
        )
        
        assert task_id is not None
        assert task_id in orchestrator._scheduled_tasks
        
    def test_unschedule_task(self, orchestrator):
        """Test task unscheduling"""
        task_id = orchestrator.schedule_task(
            name='test-task',
            task_type=TaskType.CLEANUP,
            handler=lambda: None,
            interval_seconds=60
        )
        
        result = orchestrator.unschedule_task(task_id)
        assert result is True
        assert task_id not in orchestrator._scheduled_tasks
        
    def test_enable_disable_task(self, orchestrator):
        """Test task enable/disable"""
        task_id = orchestrator.schedule_task(
            name='test-task',
            task_type=TaskType.MAINTENANCE,
            handler=lambda: None,
            interval_seconds=60
        )
        
        orchestrator.disable_task(task_id)
        assert orchestrator._scheduled_tasks[task_id].enabled is False
        
        orchestrator.enable_task(task_id)
        assert orchestrator._scheduled_tasks[task_id].enabled is True
        
    def test_get_stats(self, orchestrator):
        """Test statistics retrieval"""
        stats = orchestrator.get_stats()
        
        assert 'is_running' in stats
        assert 'total_workflows' in stats
        assert 'scheduled_tasks' in stats


# ==================== ConfigurationManager Tests ====================

class TestConfigurationManager:
    """Tests for ConfigurationManager"""
    
    @pytest.fixture
    def manager(self):
        """Create a ConfigurationManager instance"""
        return ConfigurationManager()
        
    @pytest.fixture
    def config(self):
        """Create a SystemConfiguration"""
        return SystemConfiguration(
            name='TestMesh',
            version='1.0.0',
            environment=Environment.DEVELOPMENT
        )
        
    def test_initialization(self, manager):
        """Test manager initialization"""
        assert manager._config.name == 'SynergyMesh'
        assert len(manager._config.phase_configs) == 22
        
    def test_get_set(self, manager):
        """Test get and set operations"""
        manager.set('log_level', 'DEBUG')
        assert manager.get('log_level') == 'DEBUG'
        
        manager.set('custom_key', 'custom_value')
        assert manager.get('custom_key') == 'custom_value'
        
    def test_phase_config(self, manager):
        """Test phase configuration"""
        phase_config = manager.get_phase_config(1)
        assert phase_config is not None
        assert phase_config.phase_id == 1
        
    def test_enable_disable_phase(self, manager):
        """Test phase enable/disable"""
        manager.disable_phase(5)
        assert manager.is_phase_enabled(5) is False
        
        manager.enable_phase(5)
        assert manager.is_phase_enabled(5) is True
        
    def test_validation(self, manager):
        """Test configuration validation"""
        # Valid configuration
        assert manager.validate() is True
        assert len(manager.get_validation_errors()) == 0
        
        # Invalid configuration
        manager._config.max_concurrent_tasks = 0
        assert manager.validate() is False
        assert len(manager.get_validation_errors()) > 0
        
    def test_environment(self, manager):
        """Test environment detection"""
        assert manager.is_development() is True
        assert manager.is_production() is False
        
        manager._config.environment = Environment.PRODUCTION
        assert manager.is_production() is True
        
    def test_export_config(self, manager):
        """Test configuration export"""
        exported = manager.export_config()
        
        assert 'name' in exported
        assert 'version' in exported
        assert 'environment' in exported
        assert 'phase_configs' in exported
        
    def test_watch_notification(self, manager):
        """Test configuration change notification"""
        changes = []
        
        def watcher(key, value):
            changes.append((key, value))
            
        manager.watch(watcher)
        manager.set('log_level', 'ERROR')
        
        assert len(changes) == 1
        assert changes[0] == ('log_level', 'ERROR')
        
        manager.unwatch(watcher)
        manager.set('log_level', 'INFO')
        
        assert len(changes) == 1  # No new notification


# ==================== Integration Tests ====================

class TestUnifiedIntegration:
    """Integration tests for the complete unified system"""
    
    @pytest.mark.asyncio
    async def test_full_system_lifecycle(self):
        """Test complete system lifecycle"""
        # Create components
        controller = UnifiedSystemController()
        hub = IntegrationHub()
        orchestrator = SystemOrchestrator()
        config_manager = ConfigurationManager()
        
        # Initialize
        await controller.initialize()
        await hub.start()
        await orchestrator.start()
        
        # Start controller
        await controller.start()
        
        # Verify system is operational
        assert controller._state == SystemState.RUNNING
        assert hub._is_running
        assert orchestrator._is_running
        
        # Process some requests
        for req_type in ['natural_language', 'decision', 'safety_check']:
            result = await controller.process_request({'type': req_type})
            assert result['success'] is True
            
        # Get system status
        status = controller.get_system_status()
        assert status['health']['status'] in ['healthy', 'degraded']
        
        # Shutdown
        await controller.stop()
        await orchestrator.stop()
        await hub.stop()
        
        assert controller._state == SystemState.OFFLINE
        
    @pytest.mark.asyncio
    async def test_cross_phase_communication(self):
        """Test cross-phase communication through hub"""
        hub = IntegrationHub()
        await hub.start()
        
        # Register phases
        for i in range(1, 23):
            hub.register_phase(i)
            
        # Test message routing
        messages_received = []
        
        def handler(msg):
            messages_received.append(msg)
            
        hub.register_phase(2, handler)
        
        await hub.send_message(
            source_phase=1,
            target_phase=2,
            payload={'action': 'coordinate'}
        )
        
        assert len(messages_received) == 1
        
        await hub.stop()
        
    @pytest.mark.asyncio
    async def test_workflow_orchestration(self):
        """Test workflow orchestration with multiple steps"""
        orchestrator = SystemOrchestrator()
        await orchestrator.start()
        
        execution_log = []
        
        async def step_handler(step_name: str):
            execution_log.append(step_name)
            return {'executed': step_name}
            
        steps = [
            {'name': 'init', 'handler': lambda: step_handler('init')},
            {'name': 'process', 'handler': lambda: step_handler('process')},
            {'name': 'finalize', 'handler': lambda: step_handler('finalize')}
        ]
        
        workflow = await orchestrator.execute_workflow(
            name='multi-step-workflow',
            steps=steps
        )
        
        assert workflow.state == WorkflowState.COMPLETED
        
        await orchestrator.stop()
        
    def test_configuration_propagation(self):
        """Test configuration propagation to phases"""
        config_manager = ConfigurationManager()
        
        # Update configuration
        config_manager.set('enable_safety_mechanisms', True)
        config_manager.set('max_concurrent_tasks', 50)
        
        # Verify propagation
        assert config_manager.get('enable_safety_mechanisms') is True
        assert config_manager.get('max_concurrent_tasks') == 50
        
        # Verify all phases have config
        for phase_id in range(1, 23):
            phase_config = config_manager.get_phase_config(phase_id)
            assert phase_config is not None
