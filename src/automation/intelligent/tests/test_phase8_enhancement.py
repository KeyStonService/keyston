"""
Tests for Phase 8 Enhancement - Technology Stack Architecture

Tests for:
- Architecture Configuration
- Framework Integrations (LangChain, CrewAI, AutoGen, LangGraph)
- Multi-Agent Coordinator
- Python Bridge
"""

import pytest
import asyncio
import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.tech_stack.architecture_config import (
    TechStackConfig,
    LanguageConfig,
    FrameworkConfig,
    ArchitectureLayer,
    LanguageType,
    FrameworkCategory,
    get_recommended_stack,
    get_stack_summary,
)

from core.tech_stack.framework_integrations import (
    FrameworkIntegration,
    LangChainIntegration,
    CrewAIIntegration,
    AutoGenIntegration,
    LangGraphIntegration,
    FrameworkOrchestrator,
    FrameworkCredentials,
    AgentConfig,
    AgentType,
    FrameworkStatus,
)

from core.tech_stack.multi_agent_coordinator import (
    AgentRole,
    AgentCapability,
    AgentDefinition,
    TeamTask,
    AgentTeam,
    TaskRouter,
    AgentCommunicationBus,
    MultiAgentCoordinator,
    TaskPriority,
    create_code_review_agent,
    create_architect_agent,
    create_security_agent,
    create_devops_agent,
)

from core.tech_stack.python_bridge import (
    PythonBridge,
    PythonEnvironment,
    PythonEnvironmentConfig,
    PackageManager,
    PythonExecutor,
    PythonPackage,
    PythonVersion,
    EnvironmentType,
    ExecutionMode,
)


# ============ Architecture Configuration Tests ============

class TestArchitectureConfig:
    """Tests for architecture configuration"""
    
    def test_get_recommended_stack(self):
        """Test getting recommended tech stack"""
        stack = get_recommended_stack()
        
        assert stack is not None
        assert stack.name == "SynergyMesh Tech Stack"
        assert stack.architecture_type == "hybrid"
        assert "python" in stack.languages
        assert "typescript" in stack.languages
    
    def test_stack_has_required_frameworks(self):
        """Test that stack includes required AI frameworks"""
        stack = get_recommended_stack()
        
        # Check AI agent frameworks
        assert "langchain" in stack.frameworks
        assert "crewai" in stack.frameworks
        assert "autogen" in stack.frameworks
        assert "langgraph" in stack.frameworks
        
        # Check ML libraries
        assert "pytorch" in stack.frameworks
        assert "transformers" in stack.frameworks
    
    def test_stack_has_required_layers(self):
        """Test that stack has required architecture layers"""
        stack = get_recommended_stack()
        
        assert ArchitectureLayer.AI_CORE.value in stack.layers
        assert ArchitectureLayer.ORCHESTRATION.value in stack.layers
        assert ArchitectureLayer.DATA.value in stack.layers
    
    def test_ai_core_uses_python(self):
        """Test that AI core layer uses Python"""
        stack = get_recommended_stack()
        
        ai_layer = stack.layers[ArchitectureLayer.AI_CORE.value]
        assert ai_layer.primary_language == LanguageType.PYTHON
    
    def test_stack_validation(self):
        """Test stack validation"""
        stack = get_recommended_stack()
        validation = stack.validate()
        
        assert validation["valid"] is True
        assert len(validation["issues"]) == 0
    
    def test_get_frameworks_by_category(self):
        """Test getting frameworks by category"""
        stack = get_recommended_stack()
        
        ai_frameworks = stack.get_frameworks_by_category(FrameworkCategory.AI_AGENT)
        assert len(ai_frameworks) >= 4  # langchain, crewai, autogen, langgraph
    
    def test_get_stack_summary(self):
        """Test getting stack summary"""
        summary = get_stack_summary()
        
        assert "name" in summary
        assert "key_frameworks" in summary
        assert "ai_agents" in summary["key_frameworks"]
    
    def test_language_config(self):
        """Test language configuration"""
        stack = get_recommended_stack()
        python_config = stack.languages["python"]
        
        assert python_config.name == "Python"
        assert python_config.adoption_rate > 50.0
        assert python_config.is_suitable_for("AI/ML development")
    
    def test_framework_install_command(self):
        """Test framework install command generation"""
        stack = get_recommended_stack()
        langchain = stack.frameworks["langchain"]
        
        install_cmd = langchain.get_install_command()
        assert "pip install" in install_cmd


# ============ Framework Integration Tests ============

class TestFrameworkIntegrations:
    """Tests for AI framework integrations"""
    
    @pytest.mark.asyncio
    async def test_langchain_initialization(self):
        """Test LangChain initialization"""
        integration = LangChainIntegration()
        
        credentials = FrameworkCredentials(api_key="test-key")
        result = await integration.initialize(credentials)
        
        assert result is True
        assert integration.status == FrameworkStatus.CONNECTED
    
    @pytest.mark.asyncio
    async def test_langchain_create_agent(self):
        """Test LangChain agent creation"""
        integration = LangChainIntegration()
        await integration.initialize(FrameworkCredentials(api_key="test"))
        
        config = AgentConfig(
            name="TestAgent",
            agent_type=AgentType.TASK_ORIENTED
        )
        agent_id = await integration.create_agent(config)
        
        assert agent_id is not None
        assert agent_id in integration.agents
    
    @pytest.mark.asyncio
    async def test_langchain_execute_task(self):
        """Test LangChain task execution"""
        integration = LangChainIntegration()
        await integration.initialize(FrameworkCredentials(api_key="test"))
        
        config = AgentConfig(name="TestAgent")
        agent_id = await integration.create_agent(config)
        
        result = await integration.execute_task(agent_id, "Test task")
        
        assert result.success is True
        assert "LangChain" in result.result
    
    @pytest.mark.asyncio
    async def test_langchain_create_chain(self):
        """Test LangChain chain creation"""
        integration = LangChainIntegration()
        await integration.initialize(FrameworkCredentials(api_key="test"))
        
        chain_id = await integration.create_chain(
            "test_chain",
            "sequential",
            [{"name": "step1"}, {"name": "step2"}]
        )
        
        assert chain_id == "test_chain"
        assert chain_id in integration.chains
    
    @pytest.mark.asyncio
    async def test_crewai_initialization(self):
        """Test CrewAI initialization"""
        integration = CrewAIIntegration()
        
        result = await integration.initialize(FrameworkCredentials(api_key="test"))
        
        assert result is True
        assert integration.status == FrameworkStatus.CONNECTED
    
    @pytest.mark.asyncio
    async def test_crewai_create_crew(self):
        """Test CrewAI crew creation"""
        integration = CrewAIIntegration()
        await integration.initialize(FrameworkCredentials(api_key="test"))
        
        # Create agents
        agent1 = AgentConfig(name="Researcher")
        agent2 = AgentConfig(name="Writer")
        id1 = await integration.create_agent(agent1)
        id2 = await integration.create_agent(agent2)
        
        # Create crew
        crew_id = await integration.create_crew(
            "test_crew",
            "Research Team",
            [id1, id2]
        )
        
        assert crew_id == "test_crew"
        assert crew_id in integration.crews
    
    @pytest.mark.asyncio
    async def test_crewai_execute_crew(self):
        """Test CrewAI crew execution"""
        integration = CrewAIIntegration()
        await integration.initialize(FrameworkCredentials(api_key="test"))
        
        agent = AgentConfig(name="Worker")
        agent_id = await integration.create_agent(agent)
        
        crew_id = await integration.create_crew("crew1", "Test", [agent_id])
        task_id = await integration.create_task("task1", "Do something", agent_id, "Result")
        
        result = await integration.execute_crew(crew_id, [task_id])
        
        assert result.success is True
    
    @pytest.mark.asyncio
    async def test_autogen_initialization(self):
        """Test AutoGen initialization"""
        integration = AutoGenIntegration()
        
        result = await integration.initialize(FrameworkCredentials(api_key="test"))
        
        assert result is True
        assert integration.status == FrameworkStatus.CONNECTED
    
    @pytest.mark.asyncio
    async def test_autogen_group_chat(self):
        """Test AutoGen group chat creation"""
        integration = AutoGenIntegration()
        await integration.initialize(FrameworkCredentials(api_key="test"))
        
        agent1 = AgentConfig(name="Agent1")
        agent2 = AgentConfig(name="Agent2")
        id1 = await integration.create_agent(agent1)
        id2 = await integration.create_agent(agent2)
        
        chat_id = await integration.create_group_chat("chat1", [id1, id2])
        
        assert chat_id == "chat1"
        assert chat_id in integration.group_chats
    
    @pytest.mark.asyncio
    async def test_autogen_initiate_chat(self):
        """Test AutoGen chat initiation"""
        integration = AutoGenIntegration()
        await integration.initialize(FrameworkCredentials(api_key="test"))
        
        agent1 = AgentConfig(name="User")
        agent2 = AgentConfig(name="Assistant")
        id1 = await integration.create_agent(agent1)
        id2 = await integration.create_agent(agent2)
        
        result = await integration.initiate_chat(id1, id2, "Hello!")
        
        assert result.success is True
        assert len(result.result) >= 2  # At least request and response
    
    @pytest.mark.asyncio
    async def test_langgraph_initialization(self):
        """Test LangGraph initialization"""
        integration = LangGraphIntegration()
        
        result = await integration.initialize(FrameworkCredentials(api_key="test"))
        
        assert result is True
        assert integration.status == FrameworkStatus.CONNECTED
    
    @pytest.mark.asyncio
    async def test_langgraph_create_graph(self):
        """Test LangGraph graph creation"""
        integration = LangGraphIntegration()
        await integration.initialize(FrameworkCredentials(api_key="test"))
        
        graph_id = await integration.create_graph(
            "workflow",
            nodes=[{"id": "start"}, {"id": "process"}, {"id": "end"}],
            edges=[
                {"source": "start", "target": "process"},
                {"source": "process", "target": "end"}
            ],
            entry_point="start"
        )
        
        assert graph_id == "workflow"
        assert graph_id in integration.graphs
    
    @pytest.mark.asyncio
    async def test_langgraph_execute_graph(self):
        """Test LangGraph graph execution"""
        integration = LangGraphIntegration()
        await integration.initialize(FrameworkCredentials(api_key="test"))
        
        await integration.create_graph(
            "test_graph",
            nodes=[{"id": "node1"}],
            edges=[],
            entry_point="node1"
        )
        
        result = await integration.execute_graph("test_graph", {"input": "test"})
        
        assert result.success is True
        assert result.result["completed"] is True
    
    @pytest.mark.asyncio
    async def test_framework_orchestrator(self):
        """Test framework orchestrator"""
        orchestrator = FrameworkOrchestrator()
        
        # Register frameworks
        langchain = LangChainIntegration()
        crewai = CrewAIIntegration()
        
        orchestrator.register_framework(langchain, set_as_default=True)
        orchestrator.register_framework(crewai)
        
        # Initialize all
        results = await orchestrator.initialize_all({
            "langchain": FrameworkCredentials(api_key="test"),
            "crewai": FrameworkCredentials(api_key="test")
        })
        
        assert results["langchain"] is True
        assert results["crewai"] is True
    
    @pytest.mark.asyncio
    async def test_framework_orchestrator_execute(self):
        """Test framework orchestrator task execution"""
        orchestrator = FrameworkOrchestrator()
        
        langchain = LangChainIntegration()
        orchestrator.register_framework(langchain, set_as_default=True)
        await orchestrator.initialize_all({
            "langchain": FrameworkCredentials(api_key="test")
        })
        
        # Create agent
        config = AgentConfig(name="TestAgent")
        await langchain.create_agent(config)
        
        result = await orchestrator.execute_task("Test task")
        
        assert result.success is True


# ============ Multi-Agent Coordinator Tests ============

class TestMultiAgentCoordinator:
    """Tests for multi-agent coordination"""
    
    def test_agent_definition(self):
        """Test agent definition"""
        agent = AgentDefinition(
            name="TestAgent",
            role=AgentRole.CODER,
            capabilities=[AgentCapability.CODE_GENERATION, AgentCapability.CODE_REVIEW]
        )
        
        assert agent.name == "TestAgent"
        assert agent.role == AgentRole.CODER
        assert agent.has_capability(AgentCapability.CODE_GENERATION)
        assert not agent.has_capability(AgentCapability.DEPLOYMENT)
    
    def test_agent_can_handle_task(self):
        """Test agent task capability check"""
        agent = AgentDefinition(
            name="Coder",
            capabilities=[AgentCapability.CODE_GENERATION, AgentCapability.CODE_DEBUGGING]
        )
        
        assert agent.can_handle_task([AgentCapability.CODE_GENERATION])
        assert not agent.can_handle_task([AgentCapability.DEPLOYMENT])
    
    def test_task_router(self):
        """Test task router"""
        router = TaskRouter()
        
        # Register agents
        coder = AgentDefinition(
            name="Coder",
            role=AgentRole.CODER,
            capabilities=[AgentCapability.CODE_GENERATION]
        )
        reviewer = AgentDefinition(
            name="Reviewer",
            role=AgentRole.REVIEWER,
            capabilities=[AgentCapability.CODE_REVIEW]
        )
        
        router.register_agent(coder)
        router.register_agent(reviewer)
        
        # Create task
        task = TeamTask(
            title="Write Code",
            required_capabilities=[AgentCapability.CODE_GENERATION]
        )
        
        # Route task
        assigned = router.route_task(task)
        
        assert assigned is not None
        assert assigned.name == "Coder"
    
    def test_task_router_load_balancing(self):
        """Test task router load balancing"""
        router = TaskRouter()
        
        agent1 = AgentDefinition(name="Agent1", max_concurrent_tasks=2)
        agent2 = AgentDefinition(name="Agent2", max_concurrent_tasks=2)
        
        router.register_agent(agent1)
        router.register_agent(agent2)
        
        # Route multiple tasks
        task1 = TeamTask(title="Task1")
        task2 = TeamTask(title="Task2")
        task3 = TeamTask(title="Task3")
        
        router.route_task(task1)
        router.route_task(task2)
        router.route_task(task3)
        
        # Check load distribution
        status = router.get_load_status()
        total_load = sum(s["current_load"] for s in status.values())
        assert total_load == 3
    
    def test_agent_team(self):
        """Test agent team creation"""
        team = AgentTeam(name="Development Team")
        
        coder = AgentDefinition(name="Coder", role=AgentRole.CODER)
        reviewer = AgentDefinition(name="Reviewer", role=AgentRole.REVIEWER)
        
        team.add_agent(coder)
        team.add_agent(reviewer)
        team.set_leader(coder.id)
        
        assert len(team.agents) == 2
        assert team.leader_id == coder.id
    
    def test_team_get_agents_by_role(self):
        """Test getting team agents by role"""
        team = AgentTeam(name="Test Team")
        
        team.add_agent(AgentDefinition(name="Coder1", role=AgentRole.CODER))
        team.add_agent(AgentDefinition(name="Coder2", role=AgentRole.CODER))
        team.add_agent(AgentDefinition(name="Reviewer", role=AgentRole.REVIEWER))
        
        coders = team.get_agents_by_role(AgentRole.CODER)
        assert len(coders) == 2
    
    @pytest.mark.asyncio
    async def test_coordinator_start_stop(self):
        """Test coordinator start and stop"""
        coordinator = MultiAgentCoordinator()
        
        await coordinator.start()
        assert coordinator._started is True
        
        await coordinator.stop()
        assert coordinator._started is False
    
    @pytest.mark.asyncio
    async def test_coordinator_register_agent(self):
        """Test coordinator agent registration"""
        coordinator = MultiAgentCoordinator()
        await coordinator.start()
        
        agent = AgentDefinition(name="TestAgent")
        agent_id = coordinator.register_agent(agent)
        
        assert agent_id in coordinator.agents
        
        await coordinator.stop()
    
    @pytest.mark.asyncio
    async def test_coordinator_create_team(self):
        """Test coordinator team creation"""
        coordinator = MultiAgentCoordinator()
        await coordinator.start()
        
        agent1 = AgentDefinition(name="Agent1")
        agent2 = AgentDefinition(name="Agent2")
        
        id1 = coordinator.register_agent(agent1)
        id2 = coordinator.register_agent(agent2)
        
        team = coordinator.create_team("Test Team", [id1, id2], leader_id=id1)
        
        assert team.id in coordinator.teams
        assert len(team.agents) == 2
        
        await coordinator.stop()
    
    @pytest.mark.asyncio
    async def test_coordinator_submit_task(self):
        """Test coordinator task submission"""
        coordinator = MultiAgentCoordinator()
        await coordinator.start()
        
        agent = AgentDefinition(
            name="Worker",
            capabilities=[AgentCapability.TASK_EXECUTION]
        )
        coordinator.register_agent(agent)
        
        task = TeamTask(
            title="Test Task",
            required_capabilities=[AgentCapability.TASK_EXECUTION]
        )
        task_id = await coordinator.submit_task(task)
        
        assert task_id in coordinator.tasks
        assert coordinator.tasks[task_id].status == "assigned"
        
        await coordinator.stop()
    
    @pytest.mark.asyncio
    async def test_coordinator_execute_task(self):
        """Test coordinator task execution"""
        coordinator = MultiAgentCoordinator()
        await coordinator.start()
        
        agent = AgentDefinition(name="Worker")
        coordinator.register_agent(agent)
        
        task = TeamTask(title="Execute Me")
        await coordinator.submit_task(task)
        
        result = await coordinator.execute_task(task.id)
        
        assert result is not None
        assert result.status == "completed"
        
        await coordinator.stop()
    
    @pytest.mark.asyncio
    async def test_coordinator_execute_workflow(self):
        """Test coordinator workflow execution"""
        coordinator = MultiAgentCoordinator()
        await coordinator.start()
        
        agent = AgentDefinition(name="Worker", max_concurrent_tasks=5)
        coordinator.register_agent(agent)
        
        tasks = [
            TeamTask(title="Task1"),
            TeamTask(title="Task2"),
            TeamTask(title="Task3")
        ]
        
        results = await coordinator.execute_workflow(tasks, parallel=True)
        
        assert len(results) == 3
        assert all(r.status == "completed" for r in results)
        
        await coordinator.stop()
    
    def test_factory_functions(self):
        """Test agent factory functions"""
        reviewer = create_code_review_agent()
        assert reviewer.role == AgentRole.REVIEWER
        assert AgentCapability.CODE_REVIEW in reviewer.capabilities
        
        architect = create_architect_agent()
        assert architect.role == AgentRole.ARCHITECT
        
        security = create_security_agent()
        assert security.role == AgentRole.SECURITY_EXPERT
        
        devops = create_devops_agent()
        assert devops.role == AgentRole.DEVOPS


# ============ Python Bridge Tests ============

class TestPythonBridge:
    """Tests for Python bridge"""
    
    def test_python_package(self):
        """Test Python package definition"""
        package = PythonPackage(
            name="langchain",
            version="0.1.0",
            extras=["openai"]
        )
        
        install_str = package.get_install_string()
        assert "langchain" in install_str
        assert "openai" in install_str
        assert "0.1.0" in install_str
    
    def test_package_manager_recommended_packages(self):
        """Test package manager recommended packages"""
        manager = PackageManager()
        
        ai_packages = manager.get_recommended_packages("ai_agents")
        assert len(ai_packages) > 0
        assert any(p.name == "langchain" for p in ai_packages)
        
        ml_packages = manager.get_recommended_packages("ml_libraries")
        assert len(ml_packages) > 0
        assert any(p.name == "torch" for p in ml_packages)
    
    def test_python_environment_config(self):
        """Test Python environment configuration"""
        config = PythonEnvironmentConfig(
            name="test_env",
            python_version=PythonVersion.PYTHON_311,
            environment_type=EnvironmentType.VIRTUALENV
        )
        
        assert config.name == "test_env"
        assert config.python_version == PythonVersion.PYTHON_311
    
    @pytest.mark.asyncio
    async def test_python_environment_create(self):
        """Test Python environment creation"""
        config = PythonEnvironmentConfig(
            name="test_env",
            environment_type=EnvironmentType.SYSTEM
        )
        
        env = PythonEnvironment(config)
        result = await env.create()
        
        assert result is True
        assert env.is_active is True
    
    @pytest.mark.asyncio
    async def test_python_environment_install_package(self):
        """Test package installation in environment"""
        config = PythonEnvironmentConfig(
            name="test_env",
            environment_type=EnvironmentType.SYSTEM
        )
        
        env = PythonEnvironment(config)
        await env.create()
        
        package = PythonPackage(name="requests")
        result = await env.install_package(package)
        
        assert result is True
        assert "requests" in env.installed_packages
    
    @pytest.mark.asyncio
    async def test_python_executor(self):
        """Test Python executor"""
        config = PythonEnvironmentConfig(
            name="test_env",
            environment_type=EnvironmentType.SYSTEM
        )
        env = PythonEnvironment(config)
        await env.create()
        
        executor = PythonExecutor(env)
        result = await executor.execute_code("print('Hello')", ExecutionMode.INLINE)
        
        assert result.success is True
    
    @pytest.mark.asyncio
    async def test_python_executor_stats(self):
        """Test Python executor statistics"""
        config = PythonEnvironmentConfig(environment_type=EnvironmentType.SYSTEM)
        env = PythonEnvironment(config)
        await env.create()
        
        executor = PythonExecutor(env)
        
        # Execute multiple times
        for i in range(3):
            await executor.execute_code(f"x = {i}")
        
        stats = executor.get_execution_stats()
        
        assert stats["total"] == 3
        assert stats["success"] == 3
    
    @pytest.mark.asyncio
    async def test_python_bridge_initialize(self):
        """Test Python bridge initialization"""
        bridge = PythonBridge()
        result = await bridge.initialize(setup_ai_env=True, include_ml=False)
        
        assert result is True
        assert bridge._initialized is True
        assert bridge.default_environment is not None
    
    @pytest.mark.asyncio
    async def test_python_bridge_execute_code(self):
        """Test Python bridge code execution"""
        bridge = PythonBridge()
        await bridge.initialize(setup_ai_env=True, include_ml=False)
        
        result = await bridge.execute_ai_code("result = 1 + 1")
        
        assert result.success is True
    
    @pytest.mark.asyncio
    async def test_python_bridge_status(self):
        """Test Python bridge status"""
        bridge = PythonBridge()
        await bridge.initialize(setup_ai_env=True, include_ml=False)
        
        status = bridge.get_status()
        
        assert status["initialized"] is True
        assert status["default_environment"] is not None
        assert "recommended_packages" in status
    
    @pytest.mark.asyncio
    async def test_package_manager_setup_ai_environment(self):
        """Test AI environment setup"""
        manager = PackageManager()
        env = await manager.setup_ai_environment(include_ml=False)
        
        assert env is not None
        assert env.is_active is True
        assert "synergymesh_ai" in manager.environments


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
