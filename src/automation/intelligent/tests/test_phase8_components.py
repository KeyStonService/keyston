"""
═══════════════════════════════════════════════════════════
        Phase 8 Tests - Execution Engine Tests
        執行引擎測試
═══════════════════════════════════════════════════════════
"""

import pytest
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.execution_engine import (
    ExecutionEngine,
    ExecutionContext,
    ExecutionResult,
    ExecutionStatus,
    ActionType,
    CapabilityRegistry,
    Capability,
    CapabilityStatus,
    CapabilityRequirement,
    ConnectorManager,
    Connector,
    ConnectorType,
    ConnectionStatus,
    ActionExecutor,
    ActionPlan,
    ActionStep,
    StepResult,
    VerificationEngine,
    VerificationResult,
    VerificationStrategy,
    RollbackManager,
    RollbackPlan,
    RollbackStatus,
    Checkpoint,
)


# ============ ExecutionEngine Tests ============

class TestExecutionEngine:
    """執行引擎測試"""
    
    @pytest.fixture
    def engine(self):
        return ExecutionEngine()
    
    @pytest.mark.asyncio
    async def test_basic_execution(self, engine):
        """測試基本執行"""
        context = ExecutionContext(
            permissions=["database.read", "database.write"],
        )
        
        result = await engine.execute(
            ActionType.DATABASE,
            {"operation": "query", "sql": "SELECT * FROM users"},
            context,
        )
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output is not None
    
    @pytest.mark.asyncio
    async def test_dry_run_execution(self, engine):
        """測試模擬執行"""
        context = ExecutionContext(
            dry_run=True,
            permissions=["deployment.execute"],  # Add required permission
        )
        
        result = await engine.execute(
            ActionType.DEPLOYMENT,
            {"version": "1.0.0", "strategy": "rolling"},
            context,
        )
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output.get("simulated") is True
    
    @pytest.mark.asyncio
    async def test_execution_with_missing_permission(self, engine):
        """測試缺少權限的執行"""
        context = ExecutionContext(permissions=[])  # No permissions
        
        result = await engine.execute(
            ActionType.DATABASE,
            {"operation": "query"},
            context,
        )
        
        # Should fail due to missing permissions
        assert result.status == ExecutionStatus.FAILED
        assert "permission" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_deployment_execution(self, engine):
        """測試部署執行"""
        context = ExecutionContext(
            permissions=["deployment.execute"],
        )
        
        result = await engine.execute(
            ActionType.DEPLOYMENT,
            {
                "version": "2.0.0",
                "strategy": "blue_green",
                "replicas": 3,
            },
            context,
        )
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output.get("version") == "2.0.0"
    
    @pytest.mark.asyncio
    async def test_api_call_execution(self, engine):
        """測試 API 調用執行"""
        context = ExecutionContext(
            permissions=["api.call"],
        )
        
        result = await engine.execute(
            ActionType.API_CALL,
            {
                "url": "https://api.example.com/users",
                "method": "GET",
            },
            context,
        )
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output.get("status_code") == 200
    
    def test_register_custom_executor(self, engine):
        """測試註冊自定義執行器"""
        async def custom_executor(params, context, plan):
            return {"custom": True, "params": params}
        
        engine.register_executor(ActionType.MONITORING, custom_executor)
        
        # Verify registration (internal state)
        assert ActionType.MONITORING in engine._executors
    
    def test_get_stats(self, engine):
        """測試獲取統計"""
        stats = engine.get_stats()
        
        assert "total_executions" in stats
        assert "successful_executions" in stats
        assert "failed_executions" in stats


# ============ CapabilityRegistry Tests ============

class TestCapabilityRegistry:
    """能力註冊表測試"""
    
    @pytest.fixture
    def registry(self):
        return CapabilityRegistry()
    
    def test_register_capability(self, registry):
        """測試註冊能力"""
        capability = Capability(
            name="custom.capability",
            description="Custom capability",
            category="custom",
            status=CapabilityStatus.AVAILABLE,
        )
        
        cap_id = registry.register(capability)
        
        assert cap_id is not None
        assert registry.has("custom.capability")
    
    def test_get_capability(self, registry):
        """測試獲取能力"""
        cap = registry.get("database.query")
        
        assert cap is not None
        assert cap.name == "database.query"
        assert cap.status == CapabilityStatus.AVAILABLE
    
    def test_is_available(self, registry):
        """測試能力可用性檢查"""
        assert registry.is_available("database.query")
        assert registry.is_available("api.call")
    
    def test_get_by_category(self, registry):
        """測試按類別獲取"""
        db_caps = registry.get_by_category("database")
        
        assert len(db_caps) > 0
        assert all(c.category == "database" for c in db_caps)
    
    def test_update_status(self, registry):
        """測試更新狀態"""
        success = registry.update_status(
            "database.query",
            CapabilityStatus.DEGRADED,
        )
        
        assert success
        cap = registry.get("database.query")
        assert cap.status == CapabilityStatus.DEGRADED
    
    def test_record_invocation(self, registry):
        """測試記錄調用"""
        registry.record_invocation("database.query", True, 50.0)
        registry.record_invocation("database.query", True, 100.0)
        
        cap = registry.get("database.query")
        assert cap.invocation_count == 2
        assert cap.success_count == 2
    
    def test_get_stats(self, registry):
        """測試獲取統計"""
        stats = registry.get_stats()
        
        assert "total_capabilities" in stats
        assert "available_capabilities" in stats
        assert "categories" in stats


# ============ ConnectorManager Tests ============

class TestConnectorManager:
    """連接器管理器測試"""
    
    @pytest.fixture
    def manager(self):
        return ConnectorManager()
    
    @pytest.mark.asyncio
    async def test_create_connector(self, manager):
        """測試創建連接器"""
        connector = await manager.create(
            "test_db",
            ConnectorType.DATABASE,
        )
        
        assert connector is not None
        assert connector.name == "test_db"
        assert connector.connector_type == ConnectorType.DATABASE
    
    @pytest.mark.asyncio
    async def test_connect_disconnect(self, manager):
        """測試連接和斷開"""
        await manager.create("test_conn", ConnectorType.HTTP)
        
        # Connect
        success = await manager.connect("test_conn")
        assert success
        assert manager.is_connected("test_conn")
        
        # Disconnect
        success = await manager.disconnect("test_conn")
        assert success
        assert not manager.is_connected("test_conn")
    
    @pytest.mark.asyncio
    async def test_execute_operation(self, manager):
        """測試執行操作"""
        await manager.create("test_api", ConnectorType.HTTP)
        await manager.connect("test_api")
        
        result = await manager.execute(
            "test_api",
            "get_users",
            {"limit": 10},
        )
        
        assert result.get("success") is True
    
    @pytest.mark.asyncio
    async def test_health_check(self, manager):
        """測試健康檢查"""
        await manager.create("test_hc", ConnectorType.DATABASE)
        await manager.connect("test_hc")
        
        result = await manager.health_check("test_hc")
        
        assert "healthy" in result
        assert "checks" in result
    
    def test_get_by_type(self, manager):
        """測試按類型獲取"""
        asyncio.run(manager.create("db1", ConnectorType.DATABASE))
        asyncio.run(manager.create("db2", ConnectorType.DATABASE))
        
        db_connectors = manager.get_by_type(ConnectorType.DATABASE)
        assert len(db_connectors) == 2
    
    def test_get_stats(self, manager):
        """測試獲取統計"""
        stats = manager.get_stats()
        
        assert "total_connectors" in stats
        assert "connected_connectors" in stats


# ============ ActionExecutor Tests ============

class TestActionExecutor:
    """行動執行器測試"""
    
    @pytest.fixture
    def executor(self):
        return ActionExecutor()
    
    def test_create_plan(self, executor):
        """測試創建計劃"""
        plan = executor.create_plan(
            "Test Plan",
            [
                {"name": "step1", "params": {"key": "value1"}},
                {"name": "step2", "params": {"key": "value2"}},
            ],
        )
        
        assert plan.name == "Test Plan"
        assert len(plan.steps) == 2
    
    @pytest.mark.asyncio
    async def test_execute_plan(self, executor):
        """測試執行計劃"""
        plan = executor.create_plan(
            "Test Execution",
            [
                {"name": "prepare", "params": {"environment": "test"}},
                {"name": "verify", "params": {"expected": True}},
            ],
        )
        
        result = await executor.execute_plan(plan)
        
        assert result.status == "completed"
        assert len(result.results) == 2
    
    @pytest.mark.asyncio
    async def test_parallel_execution(self, executor):
        """測試並行執行"""
        plan = executor.create_plan(
            "Parallel Test",
            [
                {"name": "step1"},
                {"name": "step2"},
                {"name": "step3"},
            ],
            parallel=True,
        )
        
        result = await executor.execute_plan(plan)
        
        assert result.status == "completed"
    
    def test_register_handler(self, executor):
        """測試註冊處理器"""
        async def custom_handler(params, completed):
            return {"custom": True}
        
        executor.register_handler("custom_step", custom_handler)
        
        assert "custom_step" in executor._handlers
    
    def test_get_stats(self, executor):
        """測試獲取統計"""
        stats = executor.get_stats()
        
        assert "total_plans" in stats
        assert "successful_plans" in stats


# ============ VerificationEngine Tests ============

class TestVerificationEngine:
    """驗證引擎測試"""
    
    @pytest.fixture
    def engine(self):
        return VerificationEngine()
    
    def test_exact_match_verification(self, engine):
        """測試精確匹配驗證"""
        result = engine.verify(
            actual={"status": "success", "code": 200},
            expected={"status": "success", "code": 200},
            strategy=VerificationStrategy.EXACT_MATCH,
        )
        
        assert result.passed is True
    
    def test_partial_match_verification(self, engine):
        """測試部分匹配驗證"""
        result = engine.verify(
            actual={"status": "success", "code": 200, "data": []},
            expected={"status": "success"},
            strategy=VerificationStrategy.PARTIAL_MATCH,
        )
        
        assert result.passed is True
    
    def test_schema_validation(self, engine):
        """測試 Schema 驗證"""
        schema = {
            "type": "object",
            "required": ["id", "name"],
            "properties": {
                "id": {"type": "number"},
                "name": {"type": "string"},
            },
        }
        
        result = engine.verify(
            actual={"id": 1, "name": "Test"},
            expected=schema,
            strategy=VerificationStrategy.SCHEMA_VALIDATION,
        )
        
        assert result.passed is True
    
    def test_failed_verification(self, engine):
        """測試失敗的驗證"""
        result = engine.verify(
            actual={"status": "error"},
            expected={"status": "success"},
            strategy=VerificationStrategy.EXACT_MATCH,
        )
        
        assert result.passed is False
        assert len(result.errors) > 0
    
    def test_verify_output_with_rules(self, engine):
        """測試使用規則驗證輸出"""
        output = {"count": 50, "items": [1, 2, 3]}
        
        # Use partial match to verify output has expected properties
        result = engine.verify(
            output,
            {"count": 50},  # Expected to have count=50
            VerificationStrategy.PARTIAL_MATCH,
        )
        
        assert result.passed is True
    
    def test_register_validator(self, engine):
        """測試註冊驗證器"""
        def custom_validator(value, rule):
            return True, "Custom check passed"
        
        engine.register_validator("custom", custom_validator)
        
        assert "custom" in engine._validators


# ============ RollbackManager Tests ============

class TestRollbackManager:
    """回滾管理器測試"""
    
    @pytest.fixture
    def manager(self):
        return RollbackManager()
    
    def test_create_checkpoint(self, manager):
        """測試創建檢查點"""
        checkpoint = manager.create_checkpoint(
            name="test_checkpoint",
            state={"database_users": {"count": 100}},
            execution_id="exec_123",
        )
        
        assert checkpoint is not None
        assert checkpoint.name == "test_checkpoint"
        assert manager.get_checkpoint(checkpoint.id) is not None
    
    def test_get_checkpoints_for_execution(self, manager):
        """測試獲取執行的檢查點"""
        manager.create_checkpoint("cp1", {}, execution_id="exec_1")
        manager.create_checkpoint("cp2", {}, execution_id="exec_1")
        manager.create_checkpoint("cp3", {}, execution_id="exec_2")
        
        checkpoints = manager.get_checkpoints_for_execution("exec_1")
        
        assert len(checkpoints) == 2
    
    @pytest.mark.asyncio
    async def test_rollback_to_checkpoint(self, manager):
        """測試回滾到檢查點"""
        checkpoint = manager.create_checkpoint(
            name="rollback_target",
            state={"config_app": {"version": "1.0.0"}},
        )
        
        plan = await manager.rollback_to_checkpoint(checkpoint.id)
        
        assert plan.status in [RollbackStatus.COMPLETED, RollbackStatus.PARTIAL]
    
    @pytest.mark.asyncio
    async def test_rollback_execution(self, manager):
        """測試回滾執行"""
        manager.create_checkpoint(
            "step1", 
            {"database_table1": {}}, 
            execution_id="exec_rb"
        )
        manager.create_checkpoint(
            "step2", 
            {"file_config": {}}, 
            execution_id="exec_rb"
        )
        
        plan = await manager.rollback_execution("exec_rb")
        
        assert plan.status in [RollbackStatus.COMPLETED, RollbackStatus.PARTIAL]
    
    def test_delete_checkpoint(self, manager):
        """測試刪除檢查點"""
        checkpoint = manager.create_checkpoint("to_delete", {})
        
        success = manager.delete_checkpoint(checkpoint.id)
        
        assert success
        assert manager.get_checkpoint(checkpoint.id) is None
    
    def test_create_rollback_plan(self, manager):
        """測試創建回滾計劃"""
        plan = manager.create_rollback_plan(
            "Custom Rollback",
            [
                {"name": "step1", "handler": "database"},
                {"name": "step2", "handler": "config"},
            ],
        )
        
        assert plan.name == "Custom Rollback"
        assert len(plan.steps) == 2
    
    def test_get_stats(self, manager):
        """測試獲取統計"""
        stats = manager.get_stats()
        
        assert "total_checkpoints" in stats
        assert "total_rollbacks" in stats


# ============ Integration Tests ============

class TestPhase8Integration:
    """Phase 8 整合測試"""
    
    @pytest.mark.asyncio
    async def test_full_execution_pipeline(self):
        """測試完整執行管道"""
        # 創建組件
        engine = ExecutionEngine()
        registry = CapabilityRegistry()
        connector_manager = ConnectorManager()
        verification_engine = VerificationEngine()
        rollback_manager = RollbackManager()
        
        # 創建連接器
        await connector_manager.create("db", ConnectorType.DATABASE)
        await connector_manager.connect("db")
        
        # 創建檢查點
        checkpoint = rollback_manager.create_checkpoint(
            "before_execution",
            {"database_state": "initial"},
        )
        
        # 執行操作
        context = ExecutionContext(
            permissions=["database.read", "database.write"],
        )
        
        result = await engine.execute(
            ActionType.DATABASE,
            {"operation": "insert", "table": "users"},
            context,
        )
        
        # 驗證結果
        verification = verification_engine.verify(
            result.output,
            {"operation": "insert"},
            VerificationStrategy.PARTIAL_MATCH,
        )
        
        # 記錄能力調用
        registry.record_invocation(
            "database.write",
            result.status == ExecutionStatus.COMPLETED,
            result.duration_ms,
        )
        
        assert result.status == ExecutionStatus.COMPLETED
        assert verification.passed is True
    
    @pytest.mark.asyncio
    async def test_execution_with_rollback(self):
        """測試帶回滾的執行"""
        engine = ExecutionEngine()
        rollback_manager = RollbackManager()
        
        # 創建檢查點
        checkpoint = rollback_manager.create_checkpoint(
            "before_change",
            {"config_app": {"setting": "original"}},
            execution_id="exec_with_rb",
        )
        
        # 模擬執行（假設失敗需要回滾）
        context = ExecutionContext(
            permissions=["config.read", "config.write"],
            dry_run=True,  # 模擬執行
        )
        
        result = await engine.execute(
            ActionType.CONFIGURATION,
            {"config_path": "/app/config.yml", "changes": {"setting": "new"}},
            context,
        )
        
        # 如果需要回滾
        if not result.verification_passed and not context.dry_run:
            rollback_plan = await rollback_manager.rollback_to_checkpoint(
                checkpoint.id
            )
            assert rollback_plan.status in [
                RollbackStatus.COMPLETED, 
                RollbackStatus.PARTIAL
            ]
    
    def test_capability_requirement_check(self):
        """測試能力需求檢查"""
        registry = CapabilityRegistry()
        
        # 檢查數據庫寫入能力的需求
        result = registry.check_requirements("database.write")
        
        assert "capability" in result
        assert "requirements" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
