"""
Tests for Phase 21: Cloud Agent Delegation System
"""

import asyncio
import pytest
import sys
import os

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))

from cloud_agent_delegation import (
    DelegationManager,
    DelegationConfig,
    DelegationResult,
    CloudProviderAdapter,
    ProviderType,
    ProviderConfig,
    TaskRouter,
    RoutingRule,
    RoutingStrategy,
    LoadBalancer,
    BalancingStrategy,
    ProviderHealth
)
from cloud_agent_delegation.delegation_manager import Task, TaskPriority, DelegationStatus


class TestDelegationManager:
    """Tests for DelegationManager"""
    
    @pytest.fixture
    def manager(self):
        config = DelegationConfig(
            name='test-delegation',
            max_concurrent_tasks=10
        )
        return DelegationManager(config)
        
    @pytest.mark.asyncio
    async def test_start_stop(self, manager):
        """Test manager start and stop"""
        await manager.start()
        assert manager._is_running is True
        
        await manager.stop()
        assert manager._is_running is False
        
    @pytest.mark.asyncio
    async def test_delegate_task(self, manager):
        """Test delegating a task"""
        await manager.start()
        
        result = await manager.delegate(
            task_name='test-task',
            task_type='analyze:code',
            payload={'code': 'test'}
        )
        
        assert isinstance(result, DelegationResult)
        assert result.task_id is not None
        
        await manager.stop()
        
    @pytest.mark.asyncio
    async def test_delegate_with_priority(self, manager):
        """Test delegating with priority"""
        await manager.start()
        
        result = await manager.delegate(
            task_name='critical-task',
            task_type='security:scan',
            payload={'target': 'test'},
            priority=TaskPriority.CRITICAL
        )
        
        assert result.task_id is not None
        
        task = manager.get_task(result.task_id)
        assert task.priority == TaskPriority.CRITICAL
        
        await manager.stop()
        
    @pytest.mark.asyncio
    async def test_get_stats(self, manager):
        """Test getting statistics"""
        await manager.start()
        
        await manager.delegate(
            task_name='task-1',
            task_type='test',
            payload={}
        )
        
        stats = manager.get_stats()
        
        assert 'total_tasks' in stats
        assert stats['total_tasks'] >= 1
        
        await manager.stop()


class TestCloudProviderAdapter:
    """Tests for CloudProviderAdapter"""
    
    @pytest.fixture
    def aws_adapter(self):
        config = ProviderConfig(
            name='aws-lambda',
            provider_type=ProviderType.AWS,
            region='us-east-1'
        )
        return CloudProviderAdapter(config)
        
    @pytest.fixture
    def gcp_adapter(self):
        config = ProviderConfig(
            name='gcp-functions',
            provider_type=ProviderType.GCP,
            region='us-central1'
        )
        return CloudProviderAdapter(config)
        
    @pytest.mark.asyncio
    async def test_execute_aws(self, aws_adapter):
        """Test AWS Lambda execution"""
        task = Task(
            id='test-123',
            name='test-task',
            type='analyze',
            payload={'code': 'test'}
        )
        
        result = await aws_adapter.execute(task)
        
        assert result.status == 'success'
        assert result.provider == 'aws-lambda'
        
    @pytest.mark.asyncio
    async def test_execute_gcp(self, gcp_adapter):
        """Test GCP Cloud Functions execution"""
        task = Task(
            id='test-456',
            name='test-task',
            type='analyze',
            payload={'code': 'test'}
        )
        
        result = await gcp_adapter.execute(task)
        
        assert result.status == 'success'
        assert result.provider == 'gcp-functions'
        
    @pytest.mark.asyncio
    async def test_health_check(self, aws_adapter):
        """Test provider health check"""
        result = await aws_adapter.health_check()
        
        assert 'healthy' in result
        assert 'status' in result


class TestTaskRouter:
    """Tests for TaskRouter"""
    
    @pytest.fixture
    def router(self):
        router = TaskRouter(default_provider='default')
        
        # Add default routing rules
        router.add_rule(RoutingRule(
            id='analyze-rule',
            name='analyze',
            pattern='analyze:*',
            preferred_provider='aws'
        ))
        router.add_rule(RoutingRule(
            id='fix-rule',
            name='fix',
            pattern='fix:*',
            preferred_provider='gcp'
        ))
        
        return router
        
    @pytest.mark.asyncio
    async def test_route_matching_rule(self, router):
        """Test routing with matching rule"""
        task = Task(
            id='test-123',
            name='analyze code',
            type='analyze:code',
            payload={}
        )
        
        result = await router.route(task)
        
        assert result.provider == 'aws'
        assert result.rule_name == 'analyze'
        
    @pytest.mark.asyncio
    async def test_route_default(self, router):
        """Test routing without matching rule"""
        task = Task(
            id='test-456',
            name='unknown task',
            type='unknown:type',
            payload={}
        )
        
        result = await router.route(task)
        
        assert result.provider == 'default'
        
    def test_add_remove_rule(self, router):
        """Test adding and removing rules"""
        new_rule = RoutingRule(
            id='new-rule',
            name='new',
            pattern='new:*',
            preferred_provider='azure'
        )
        
        router.add_rule(new_rule)
        assert router.get_rule('new-rule') is not None
        
        router.remove_rule('new-rule')
        assert router.get_rule('new-rule') is None


class TestLoadBalancer:
    """Tests for LoadBalancer"""
    
    @pytest.fixture
    def balancer(self):
        return LoadBalancer()
        
    @pytest.mark.asyncio
    async def test_start_stop(self, balancer):
        """Test balancer start and stop"""
        await balancer.start()
        assert balancer._is_running is True
        
        await balancer.stop()
        assert balancer._is_running is False
        
    def test_register_provider(self, balancer):
        """Test registering a provider"""
        balancer.register_provider('aws', object(), weight=40)
        
        assert 'aws' in balancer.list_providers()
        assert balancer.config.weights['aws'] == 40
        
    def test_unregister_provider(self, balancer):
        """Test unregistering a provider"""
        balancer.register_provider('test', object())
        
        result = balancer.unregister_provider('test')
        
        assert result is True
        assert 'test' not in balancer.list_providers()
        
    @pytest.mark.asyncio
    async def test_select_provider_round_robin(self, balancer):
        """Test round-robin selection"""
        balancer.config.strategy = BalancingStrategy.ROUND_ROBIN
        balancer.config.healthy_threshold = 1  # Lower threshold for testing
        
        balancer.register_provider('provider-1', object())
        balancer.register_provider('provider-2', object())
        
        # Mark both as healthy (need consecutive successes)
        balancer.update_health('provider-1', True)
        balancer.update_health('provider-2', True)
        
        selections = []
        for _ in range(4):
            selection = await balancer.select_provider()
            selections.append(selection)
            
        # Should alternate between providers
        assert 'provider-1' in selections
        assert 'provider-2' in selections
        
    @pytest.mark.asyncio
    async def test_select_provider_weighted(self, balancer):
        """Test weighted selection"""
        balancer.config.strategy = BalancingStrategy.WEIGHTED_ROUND_ROBIN
        balancer.config.healthy_threshold = 1  # Lower threshold for testing
        
        balancer.register_provider('aws', object(), weight=40)
        balancer.register_provider('gcp', object(), weight=35)
        balancer.register_provider('azure', object(), weight=25)
        
        # Mark all as healthy
        balancer.update_health('aws', True)
        balancer.update_health('gcp', True)
        balancer.update_health('azure', True)
        
        selections = []
        for _ in range(100):
            selection = await balancer.select_provider()
            selections.append(selection)
            
        # Count selections
        aws_count = selections.count('aws')
        gcp_count = selections.count('gcp')
        azure_count = selections.count('azure')
        
        # AWS should have more selections due to higher weight
        assert aws_count > azure_count
        
    def test_update_health(self, balancer):
        """Test updating provider health"""
        balancer.register_provider('test', object())
        
        # Initially unknown
        health = balancer.get_health('test')
        assert health.status.value == 'unknown'
        
        # Update to healthy
        balancer.update_health('test', True)
        balancer.update_health('test', True)  # Need consecutive successes
        
        health = balancer.get_health('test')
        assert health.is_healthy is True
        
    def test_get_stats(self, balancer):
        """Test getting statistics"""
        balancer.register_provider('aws', object(), weight=40)
        balancer.register_provider('gcp', object(), weight=35)
        
        stats = balancer.get_stats()
        
        assert stats['total_providers'] == 2
        assert 'providers' in stats


class TestIntegration:
    """Integration tests for the delegation system"""
    
    @pytest.mark.asyncio
    async def test_full_delegation_flow(self):
        """Test complete delegation flow"""
        # Create components
        router = TaskRouter(default_provider='aws')
        router.add_rule(RoutingRule(
            id='security-rule',
            name='security',
            pattern='security:*',
            preferred_provider='aws',
            priority='critical'
        ))
        
        balancer = LoadBalancer()
        balancer.register_provider('aws', object(), weight=40)
        balancer.register_provider('gcp', object(), weight=35)
        balancer.update_health('aws', True)
        balancer.update_health('gcp', True)
        
        config = DelegationConfig(name='integration-test')
        manager = DelegationManager(
            config=config,
            router=router,
            load_balancer=balancer
        )
        
        await manager.start()
        
        # Delegate a security task
        result = await manager.delegate(
            task_name='security-scan',
            task_type='security:vulnerability',
            payload={'target': 'app.py'},
            priority=TaskPriority.CRITICAL
        )
        
        assert result.task_id is not None
        assert result.status in [DelegationStatus.COMPLETED, DelegationStatus.FAILED]
        
        await manager.stop()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
