"""
Tests for Phase 19: MCP Servers Enhanced Integration
"""

import asyncio
import pytest
import sys
import os

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))

from mcp_servers_enhanced import (
    MCPServerManager,
    MCPServerConfig,
    ToolRegistry,
    ToolDefinition,
    ToolCategory,
    WorkflowOrchestrator,
    WorkflowStep,
    Workflow,
    RealTimeConnector,
    ConnectionConfig,
    TransportType
)


class TestMCPServerManager:
    """Tests for MCPServerManager"""
    
    @pytest.fixture
    def manager(self):
        return MCPServerManager()
        
    @pytest.mark.asyncio
    async def test_register_server(self, manager):
        """Test server registration"""
        config = MCPServerConfig(
            name='test-server',
            version='1.0.0'
        )
        
        server = await manager.register_server(config)
        
        assert server is not None
        assert server.config.name == 'test-server'
        assert server.id is not None
        
    @pytest.mark.asyncio
    async def test_list_servers(self, manager):
        """Test listing servers"""
        config1 = MCPServerConfig(name='server-1')
        config2 = MCPServerConfig(name='server-2')
        
        await manager.register_server(config1)
        await manager.register_server(config2)
        
        servers = manager.list_servers()
        assert len(servers) == 2
        
    @pytest.mark.asyncio
    async def test_unregister_server(self, manager):
        """Test server unregistration"""
        config = MCPServerConfig(name='test-server')
        server = await manager.register_server(config)
        
        result = await manager.unregister_server(server.id)
        
        assert result is True
        assert manager.get_server(server.id) is None


class TestToolRegistry:
    """Tests for ToolRegistry"""
    
    @pytest.fixture
    def registry(self):
        return ToolRegistry()
        
    def test_register_tool(self, registry):
        """Test tool registration"""
        tool = ToolDefinition(
            name='test-tool',
            description='A test tool',
            input_schema={'type': 'object', 'properties': {}},
            category=ToolCategory.CODE_ANALYSIS
        )
        
        registry.register(tool)
        
        assert registry.exists('test-tool')
        assert registry.get('test-tool').name == 'test-tool'
        
    def test_list_by_category(self, registry):
        """Test listing tools by category"""
        tool1 = ToolDefinition(
            name='tool-1',
            description='Tool 1',
            input_schema={},
            category=ToolCategory.SECURITY
        )
        tool2 = ToolDefinition(
            name='tool-2',
            description='Tool 2',
            input_schema={},
            category=ToolCategory.SECURITY
        )
        
        registry.register(tool1)
        registry.register(tool2)
        
        security_tools = registry.list_by_category(ToolCategory.SECURITY)
        assert len(security_tools) == 2
        
    def test_validate_arguments(self, registry):
        """Test argument validation"""
        tool = ToolDefinition(
            name='test-tool',
            description='Test',
            input_schema={
                'type': 'object',
                'properties': {
                    'code': {'type': 'string'}
                },
                'required': ['code']
            }
        )
        
        registry.register(tool)
        
        # Valid arguments
        result = registry.validate_arguments('test-tool', {'code': 'test'})
        assert result['valid'] is True
        
        # Missing required field
        result = registry.validate_arguments('test-tool', {})
        assert result['valid'] is False


class TestWorkflowOrchestrator:
    """Tests for WorkflowOrchestrator"""
    
    @pytest.fixture
    def orchestrator(self):
        return WorkflowOrchestrator()
        
    @pytest.mark.asyncio
    async def test_register_workflow(self, orchestrator):
        """Test workflow registration"""
        workflow = Workflow(
            id='test-workflow',
            name='Test Workflow',
            steps=[
                WorkflowStep(
                    id='step-1',
                    name='Step 1',
                    tool='test-tool',
                    arguments={'key': 'value'}
                )
            ]
        )
        
        await orchestrator.register_workflow(workflow)
        
        result = orchestrator.get_workflow('test-workflow')
        assert result is not None
        assert result.name == 'Test Workflow'
        
    @pytest.mark.asyncio
    async def test_execute_workflow(self, orchestrator):
        """Test workflow execution"""
        workflow = Workflow(
            id='test-workflow',
            name='Test Workflow',
            steps=[
                WorkflowStep(
                    id='step-1',
                    name='Step 1',
                    tool='test-tool',
                    arguments={'key': 'value'}
                )
            ]
        )
        
        await orchestrator.register_workflow(workflow)
        result = await orchestrator.execute_workflow('test-workflow')
        
        assert result is not None
        assert result.workflow_id == 'test-workflow'


class TestRealTimeConnector:
    """Tests for RealTimeConnector"""
    
    @pytest.fixture
    def connector(self):
        return RealTimeConnector()
        
    @pytest.mark.asyncio
    async def test_start_stop(self, connector):
        """Test connector start and stop"""
        await connector.start()
        assert connector._is_running is True
        
        await connector.stop()
        assert connector._is_running is False
        
    @pytest.mark.asyncio
    async def test_connect(self, connector):
        """Test establishing connection"""
        await connector.start()
        
        config = ConnectionConfig(
            server_name='test-server',
            transport=TransportType.STDIO
        )
        
        connection = await connector.connect(config)
        
        assert connection is not None
        assert connection.config.server_name == 'test-server'
        
        await connector.stop()
        
    @pytest.mark.asyncio
    async def test_list_connections(self, connector):
        """Test listing connections"""
        await connector.start()
        
        config1 = ConnectionConfig(server_name='server-1')
        config2 = ConnectionConfig(server_name='server-2')
        
        await connector.connect(config1)
        await connector.connect(config2)
        
        connections = connector.list_connections()
        assert len(connections) == 2
        
        await connector.stop()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
