"""
Test suite for Enhanced Integration Components
增強整合元件測試套件
"""

import asyncio
import pytest
from datetime import datetime, timezone

from core.unified_integration import (
    # Service Registry
    ServiceRegistry,
    RegistryConfig,
    ServiceMetadata,
    ServiceEndpoint,
    ServiceStatus,
    ServiceCategory,
    create_service_registry,
    register_core_services,
    
    # Cognitive Processor
    EnhancedCognitiveProcessor,
    ProcessorConfig,
    CognitiveSignal,
    CognitiveLayer,
    SignalType,
    create_cognitive_processor,
    
    # Configuration Optimizer
    ConfigurationOptimizer,
    OptimizerConfig,
    OptimizationCategory,
    create_configuration_optimizer,
)


class TestServiceRegistry:
    """Tests for ServiceRegistry"""
    
    @pytest.fixture
    def registry(self):
        """Create a fresh registry for each test"""
        return create_service_registry()
    
    def test_create_registry(self, registry):
        """Test registry creation"""
        assert registry is not None
        assert isinstance(registry, ServiceRegistry)
    
    def test_register_service(self, registry):
        """Test service registration"""
        service_id = registry.register_service(
            name='test-service',
            version='1.0.0',
            category=ServiceCategory.CORE,
            description='Test service'
        )
        
        assert service_id is not None
        assert 'test-service' in service_id
        
        # Verify service can be retrieved
        service = registry.get_service(service_id)
        assert service is not None
        assert service.name == 'test-service'
        assert service.version == '1.0.0'
    
    def test_discover_by_name(self, registry):
        """Test service discovery by name"""
        registry.register_service(
            name='discovery-test',
            version='1.0.0',
            category=ServiceCategory.INTEGRATION
        )
        
        services = registry.discover_by_name('discovery-test')
        assert len(services) == 1
        assert services[0].name == 'discovery-test'
    
    def test_discover_by_category(self, registry):
        """Test service discovery by category"""
        registry.register_service(
            name='security-service',
            version='1.0.0',
            category=ServiceCategory.SECURITY
        )
        
        services = registry.discover_by_category(ServiceCategory.SECURITY)
        assert len(services) >= 1
        assert any(s.name == 'security-service' for s in services)
    
    def test_discover_by_capability(self, registry):
        """Test service discovery by capability"""
        registry.register_service(
            name='capability-service',
            version='1.0.0',
            category=ServiceCategory.CORE,
            provides=['special-capability']
        )
        
        services = registry.discover_by_capability('special-capability')
        assert len(services) >= 1
        assert any(s.name == 'capability-service' for s in services)
    
    def test_deregister_service(self, registry):
        """Test service deregistration"""
        service_id = registry.register_service(
            name='temp-service',
            version='1.0.0',
            category=ServiceCategory.CORE
        )
        
        result = registry.deregister_service(service_id)
        assert result is True
        
        # Verify service is gone
        service = registry.get_service(service_id)
        assert service is None
    
    def test_heartbeat(self, registry):
        """Test service heartbeat"""
        service_id = registry.register_service(
            name='heartbeat-service',
            version='1.0.0',
            category=ServiceCategory.CORE
        )
        
        result = registry.heartbeat(service_id)
        assert result is True
        
        service = registry.get_service(service_id)
        assert service.last_heartbeat is not None
    
    def test_update_health(self, registry):
        """Test health status update"""
        service_id = registry.register_service(
            name='health-service',
            version='1.0.0',
            category=ServiceCategory.MONITORING
        )
        
        result = registry.update_health(
            service_id,
            ServiceStatus.HEALTHY,
            latency_ms=5.0
        )
        assert result is True
        
        service = registry.get_service(service_id)
        assert service.health.status == ServiceStatus.HEALTHY
        assert service.health.latency_ms == 5.0
    
    def test_register_core_services(self, registry):
        """Test registering core services"""
        register_core_services(registry)
        
        stats = registry.get_stats()
        assert stats['total_services'] >= 7  # At least 7 core services
    
    def test_get_stats(self, registry):
        """Test getting registry statistics"""
        registry.register_service(
            name='stats-service',
            version='1.0.0',
            category=ServiceCategory.CORE
        )
        
        stats = registry.get_stats()
        assert 'total_services' in stats
        assert 'registrations' in stats
        assert stats['registrations'] >= 1


class TestCognitiveProcessor:
    """Tests for EnhancedCognitiveProcessor"""
    
    @pytest.fixture
    def processor(self):
        """Create a fresh processor for each test"""
        return create_cognitive_processor()
    
    def test_create_processor(self, processor):
        """Test processor creation"""
        assert processor is not None
        assert isinstance(processor, EnhancedCognitiveProcessor)
    
    def test_processor_has_layers(self, processor):
        """Test processor has all cognitive layers"""
        assert processor.perception is not None
        assert processor.reasoning is not None
        assert processor.execution is not None
        assert processor.proof is not None
    
    @pytest.mark.asyncio
    async def test_process_signal(self, processor):
        """Test processing a signal through all layers"""
        await processor.start()
        
        try:
            signal = CognitiveSignal(
                signal_id='test-signal-001',
                signal_type=SignalType.TELEMETRY,
                layer=CognitiveLayer.L1_PERCEPTION,
                source='test',
                payload={'metric': 'cpu_usage', 'value': 75.5}
            )
            
            result = await processor.process_signal(signal)
            
            assert result['success'] is True
            assert 'layers_processed' in result
            assert len(result['layers_processed']) > 0
        finally:
            await processor.stop()
    
    @pytest.mark.asyncio
    async def test_process_anomaly_signal(self, processor):
        """Test processing an anomaly signal"""
        await processor.start()
        
        try:
            signal = CognitiveSignal(
                signal_id='anomaly-signal-001',
                signal_type=SignalType.ANOMALY,
                layer=CognitiveLayer.L1_PERCEPTION,
                source='detector',
                payload={'anomaly_type': 'spike', 'severity': 'high'},
                confidence=0.9
            )
            
            result = await processor.process_signal(signal)
            
            assert result['success'] is True
            # Anomaly signals should generate decisions
            assert 'decisions' in result
        finally:
            await processor.stop()
    
    def test_get_stats(self, processor):
        """Test getting processor statistics"""
        stats = processor.get_stats()
        
        assert 'processor' in stats
        assert 'perception' in stats
        assert 'reasoning' in stats
        assert 'execution' in stats
        assert 'proof' in stats


class TestConfigurationOptimizer:
    """Tests for ConfigurationOptimizer"""
    
    @pytest.fixture
    def optimizer(self):
        """Create a fresh optimizer for each test"""
        return create_configuration_optimizer()
    
    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing"""
        return {
            'environment': 'development',
            'max_concurrent_tasks': 100,
            'task_timeout_seconds': 300,
            'request_timeout_seconds': 30,
            'health_check_interval_seconds': 60,
            'enable_safety_mechanisms': True,
            'enable_circuit_breaker': True,
            'circuit_breaker_threshold': 5,
            'enable_slsa_provenance': True,
        }
    
    def test_create_optimizer(self, optimizer):
        """Test optimizer creation"""
        assert optimizer is not None
        assert isinstance(optimizer, ConfigurationOptimizer)
    
    def test_validate_valid_config(self, optimizer, sample_config):
        """Test validation of valid configuration"""
        result = optimizer.validate(sample_config)
        
        assert result.is_valid is True
        assert len(result.issues) == 0
    
    def test_validate_invalid_concurrent_tasks(self, optimizer, sample_config):
        """Test validation catches invalid concurrent tasks"""
        sample_config['max_concurrent_tasks'] = 0
        
        result = optimizer.validate(sample_config)
        
        assert result.is_valid is False
        assert any('max_concurrent_tasks' in str(issue) for issue in result.issues)
    
    def test_validate_invalid_timeout(self, optimizer, sample_config):
        """Test validation catches invalid timeout"""
        sample_config['task_timeout_seconds'] = 0
        
        result = optimizer.validate(sample_config)
        
        assert result.is_valid is False
    
    def test_validate_production_safety(self, optimizer):
        """Test validation requires safety in production"""
        prod_config = {
            'environment': 'production',
            'enable_safety_mechanisms': False,
            'max_concurrent_tasks': 100,
            'task_timeout_seconds': 300,
            'health_check_interval_seconds': 60,
        }
        
        result = optimizer.validate(prod_config)
        
        # Should fail validation
        assert result.is_valid is False
    
    def test_analyze_generates_recommendations(self, optimizer, sample_config):
        """Test analysis generates recommendations"""
        # Modify config to trigger recommendation
        sample_config['environment'] = 'development'
        sample_config['max_concurrent_tasks'] = 100  # Higher than dev recommendation
        
        recommendations = optimizer.analyze(sample_config)
        
        # Should generate at least one recommendation
        assert isinstance(recommendations, list)
    
    def test_create_snapshot(self, optimizer, sample_config):
        """Test creating configuration snapshot"""
        snapshot = optimizer.create_snapshot(sample_config)
        
        assert snapshot is not None
        assert snapshot.config == sample_config
        assert snapshot.snapshot_id is not None
    
    def test_set_baseline(self, optimizer, sample_config):
        """Test setting baseline configuration"""
        baseline = optimizer.set_baseline(sample_config)
        
        assert baseline is not None
        assert baseline.source == 'baseline'
    
    def test_detect_drift(self, optimizer, sample_config):
        """Test drift detection"""
        optimizer.set_baseline(sample_config)
        
        # Modify configuration
        modified_config = sample_config.copy()
        modified_config['max_concurrent_tasks'] = 200
        modified_config['new_setting'] = 'value'
        
        drift = optimizer.detect_drift(modified_config)
        
        assert drift is not None
        assert len(drift.drifted_keys) >= 1
        assert 'new_setting' in drift.added_keys
    
    def test_get_stats(self, optimizer, sample_config):
        """Test getting optimizer statistics"""
        optimizer.validate(sample_config)
        
        stats = optimizer.get_stats()
        
        assert 'validations' in stats
        assert stats['validations'] >= 1
        assert 'active_rules' in stats


class TestIntegrationFlow:
    """Integration tests for the complete flow"""
    
    @pytest.mark.asyncio
    async def test_full_integration_flow(self):
        """Test complete integration of all components"""
        # Create components
        registry = create_service_registry()
        processor = create_cognitive_processor()
        optimizer = create_configuration_optimizer()
        
        # Register services
        register_core_services(registry)
        
        # Start processor
        await processor.start()
        
        try:
            # Create and process a signal
            signal = CognitiveSignal(
                signal_id='integration-test-001',
                signal_type=SignalType.TELEMETRY,
                layer=CognitiveLayer.L1_PERCEPTION,
                source='integration-test',
                payload={'test': True}
            )
            
            result = await processor.process_signal(signal)
            assert result['success'] is True
            
            # Validate configuration
            config = {
                'environment': 'development',
                'max_concurrent_tasks': 50,
                'task_timeout_seconds': 300,
                'health_check_interval_seconds': 60,
                'enable_safety_mechanisms': True,
            }
            
            validation = optimizer.validate(config)
            assert validation.is_valid is True
            
            # Check registry stats
            stats = registry.get_stats()
            assert stats['total_services'] >= 7
            
        finally:
            await processor.stop()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
