"""
Test suite for Deep Execution System
深度執行系統測試套件
"""

import asyncio

import pytest

from core.unified_integration.deep_execution_system import (
    AuditLogger,
    DeepExecutionConfig,
    DeepExecutionSystem,
    ExecutionContext,
    Operation,
    OperationPriority,
    OperationResult,
    OperationScheduler,
    OperationStatus,
    OperationValidator,
    ValidationLevel,
    create_deep_execution_system,
)


class TestDeepExecutionSystem:
    """Tests for DeepExecutionSystem"""

    @pytest.fixture
    def system(self):
        """Create a fresh system for each test"""
        return create_deep_execution_system()

    @pytest.fixture
    def config(self):
        """Create a custom configuration"""
        return DeepExecutionConfig(
            max_concurrent_operations=10,
            max_context_depth=5,
            default_timeout_seconds=30.0,
            enable_auto_rollback=True,
            enable_deep_validation=True,
            enable_audit_logging=True
        )

    def test_create_system(self, system):
        """Test system creation"""
        assert system is not None
        assert isinstance(system, DeepExecutionSystem)

    def test_create_system_with_config(self, config):
        """Test system creation with custom config"""
        system = DeepExecutionSystem(config)
        assert system.config.max_concurrent_operations == 10
        assert system.config.max_context_depth == 5

    def test_create_context(self, system):
        """Test execution context creation"""
        context = system.create_context('test-context')

        assert context is not None
        assert isinstance(context, ExecutionContext)
        assert context.name == 'test-context'
        assert context.depth_level == 0

    def test_create_nested_context(self, system):
        """Test nested context creation"""
        parent = system.create_context('parent-context')
        child = system.create_context('child-context', parent_context_id=parent.context_id)

        assert child.parent_context_id == parent.context_id
        assert child.depth_level == 1
        assert child.context_id in parent.child_contexts

    def test_context_depth_limit(self, system):
        """Test context depth limit enforcement"""
        # Create a custom config with low max depth
        config = DeepExecutionConfig(max_context_depth=2)
        limited_system = DeepExecutionSystem(config)

        ctx1 = limited_system.create_context('level-0')
        ctx2 = limited_system.create_context('level-1', parent_context_id=ctx1.context_id)
        ctx3 = limited_system.create_context('level-2', parent_context_id=ctx2.context_id)

        # Should raise error when exceeding max depth
        with pytest.raises(ValueError, match="Max context depth"):
            limited_system.create_context('level-3', parent_context_id=ctx3.context_id)

    def test_get_context(self, system):
        """Test getting context by ID"""
        created = system.create_context('findable-context')
        found = system.get_context(created.context_id)

        assert found is not None
        assert found.context_id == created.context_id

    def test_get_nonexistent_context(self, system):
        """Test getting non-existent context returns None"""
        result = system.get_context('nonexistent-id')
        assert result is None

    @pytest.mark.asyncio
    async def test_start_and_stop(self, system):
        """Test system start and stop"""
        await system.start()
        assert system._is_running is True

        await system.stop()
        assert system._is_running is False

    @pytest.mark.asyncio
    async def test_execute_simple_operation(self, system):
        """Test executing a simple operation"""
        await system.start()

        try:
            def simple_handler(value):
                return value * 2

            result = await system.execute(
                name='double-value',
                handler=simple_handler,
                args={'value': 21}
            )

            assert result is not None
            assert isinstance(result, OperationResult)
            assert result.status == OperationStatus.COMPLETED
            assert result.output == 42
        finally:
            await system.stop()

    @pytest.mark.asyncio
    async def test_execute_async_operation(self, system):
        """Test executing an async operation"""
        await system.start()

        try:
            async def async_handler(value):
                await asyncio.sleep(0.01)
                return value + 100

            result = await system.execute(
                name='async-add',
                handler=async_handler,
                args={'value': 50}
            )

            assert result.status == OperationStatus.COMPLETED
            assert result.output == 150
        finally:
            await system.stop()

    @pytest.mark.asyncio
    async def test_execute_with_context(self, system):
        """Test executing operation in a specific context"""
        await system.start()

        try:
            context = system.create_context('my-workflow')

            def handler():
                return 'success'

            result = await system.execute(
                name='contextual-op',
                handler=handler,
                context_id=context.context_id
            )

            assert result.status == OperationStatus.COMPLETED
            assert result.operation_id in context.operations
        finally:
            await system.stop()

    @pytest.mark.asyncio
    async def test_execute_with_invalid_context(self, system):
        """Test executing with invalid context raises error"""
        await system.start()

        try:
            with pytest.raises(ValueError, match="Context not found"):
                await system.execute(
                    name='invalid-context-op',
                    handler=lambda: None,
                    context_id='nonexistent-context-id'
                )
        finally:
            await system.stop()

    @pytest.mark.asyncio
    async def test_execute_with_priority(self, system):
        """Test executing operation with priority"""
        await system.start()

        try:
            result = await system.execute(
                name='high-priority-op',
                handler=lambda: 'done',
                priority=OperationPriority.HIGH
            )

            assert result.status == OperationStatus.COMPLETED
        finally:
            await system.stop()

    @pytest.mark.asyncio
    async def test_execute_with_validation_levels(self, system):
        """Test executing with different validation levels"""
        await system.start()

        try:
            # Test with deep validation
            result = await system.execute(
                name='deep-validated-op',
                handler=lambda: 'validated',
                validation_level=ValidationLevel.DEEP
            )

            assert result.status == OperationStatus.COMPLETED
            assert 'valid' in result.validation_results
        finally:
            await system.stop()

    @pytest.mark.asyncio
    async def test_execute_failing_operation(self, system):
        """Test handling of failing operation"""
        await system.start()

        try:
            def failing_handler():
                raise ValueError("Intentional failure")

            # Configure with no retries for this test
            result = await system.execute(
                name='failing-op',
                handler=failing_handler,
                args={}
            )

            assert result.status in [OperationStatus.FAILED, OperationStatus.ROLLED_BACK]
            assert result.error is not None
        finally:
            await system.stop()

    @pytest.mark.asyncio
    async def test_execute_with_rollback(self, system):
        """Test operation rollback on failure"""
        await system.start()

        rollback_called = {'value': False}

        try:
            def failing_handler():
                raise RuntimeError("Planned failure")

            def rollback_handler():
                rollback_called['value'] = True

            result = await system.execute(
                name='rollbackable-op',
                handler=failing_handler,
                rollback_handler=rollback_handler
            )

            assert result.status == OperationStatus.ROLLED_BACK
            assert rollback_called['value'] is True
        finally:
            await system.stop()

    @pytest.mark.asyncio
    async def test_rollback_context(self, system):
        """Test rolling back all operations in a context"""
        await system.start()

        rollback_order = []

        try:
            context = system.create_context('rollback-test')

            def op1():
                return 'op1'

            def rollback_op1():
                rollback_order.append('op1')

            def op2():
                return 'op2'

            def rollback_op2():
                rollback_order.append('op2')

            await system.execute(
                name='op1',
                handler=op1,
                rollback_handler=rollback_op1,
                context_id=context.context_id
            )

            await system.execute(
                name='op2',
                handler=op2,
                rollback_handler=rollback_op2,
                context_id=context.context_id
            )

            rolled_back = await system.rollback_context(context.context_id)

            # Should rollback in reverse order (LIFO)
            assert len(rolled_back) == 2
            assert rollback_order == ['op2', 'op1']
        finally:
            await system.stop()

    @pytest.mark.asyncio
    async def test_complete_context(self, system):
        """Test completing a context"""
        await system.start()

        try:
            context = system.create_context('completable-context')

            result = system.complete_context(context.context_id)

            assert result is True
            assert context.completed_at is not None
        finally:
            await system.stop()

    def test_get_audit_entries(self, system):
        """Test getting audit entries"""
        entries = system.get_audit_entries()
        assert isinstance(entries, list)

    @pytest.mark.asyncio
    async def test_audit_logging(self, system):
        """Test audit logging during execution"""
        await system.start()

        try:
            context = system.create_context('audited-context')

            await system.execute(
                name='audited-op',
                handler=lambda: 'audited',
                context_id=context.context_id
            )

            entries = system.get_audit_entries(context_id=context.context_id)
            assert len(entries) >= 1

            # Check audit entry structure
            entry = entries[-1]
            assert 'operation_name' in entry
            assert 'status' in entry
            assert 'timestamp' in entry
        finally:
            await system.stop()

    def test_get_stats(self, system):
        """Test getting system statistics"""
        stats = system.get_stats()

        assert 'system' in stats
        assert 'validator' in stats
        assert 'scheduler' in stats
        assert 'audit_logger' in stats
        assert 'is_running' in stats


class TestOperationValidator:
    """Tests for OperationValidator"""

    @pytest.fixture
    def validator(self):
        """Create a fresh validator"""
        config = DeepExecutionConfig()
        return OperationValidator(config)

    @pytest.fixture
    def sample_operation(self):
        """Create a sample operation"""
        return Operation(
            operation_id='test-op-001',
            name='test-operation',
            handler=lambda: 'result',
            validation_level=ValidationLevel.STANDARD
        )

    @pytest.fixture
    def sample_context(self):
        """Create a sample context"""
        return ExecutionContext(
            context_id='test-ctx-001',
            name='test-context'
        )

    @pytest.mark.asyncio
    async def test_validate_valid_operation(self, validator, sample_operation, sample_context):
        """Test validation of valid operation"""
        result = await validator.validate(sample_operation, sample_context)

        assert result['valid'] is True
        assert len(result['errors']) == 0

    @pytest.mark.asyncio
    async def test_validate_non_callable_handler(self, validator, sample_context):
        """Test validation catches non-callable handler"""
        # Intentionally passing invalid handler type to test validation
        invalid_operation = Operation(
            operation_id='invalid-op',
            name='invalid',
            handler="not a callable"  # type: ignore[arg-type]  # Testing invalid input
        )

        result = await validator.validate(invalid_operation, sample_context)

        assert result['valid'] is False
        assert any('not callable' in err for err in result['errors'])

    @pytest.mark.asyncio
    async def test_validate_exceeds_context_depth(self, validator, sample_operation):
        """Test validation catches excessive context depth"""
        deep_context = ExecutionContext(
            context_id='deep-ctx',
            name='deep-context',
            depth_level=15  # Exceeds default max of 10
        )

        result = await validator.validate(sample_operation, deep_context)

        assert result['valid'] is False
        assert any('depth' in err.lower() for err in result['errors'])

    def test_add_custom_validator(self, validator):
        """Test adding custom validators"""
        def custom_validator(op, ctx):
            return {'valid': True, 'name': 'custom'}

        validator.add_validator(ValidationLevel.STANDARD, custom_validator)

        # Verify validator was added
        assert len(validator._validators[ValidationLevel.STANDARD]) == 1

    def test_get_stats(self, validator):
        """Test getting validator statistics"""
        stats = validator.get_stats()

        assert 'validations_performed' in stats
        assert 'validations_passed' in stats
        assert 'validations_failed' in stats


class TestOperationScheduler:
    """Tests for OperationScheduler"""

    @pytest.fixture
    def scheduler(self):
        """Create a fresh scheduler"""
        return OperationScheduler(max_concurrent=5)

    @pytest.fixture
    def sample_operation(self):
        """Create a sample operation"""
        return Operation(
            operation_id='sched-op-001',
            name='scheduled-operation',
            handler=lambda: 'result',
            priority=OperationPriority.NORMAL
        )

    @pytest.mark.asyncio
    async def test_schedule_operation(self, scheduler, sample_operation):
        """Test scheduling an operation"""
        await scheduler.schedule(sample_operation)

        stats = scheduler.get_stats()
        assert stats['operations_scheduled'] == 1

    @pytest.mark.asyncio
    async def test_get_next_by_priority(self, scheduler):
        """Test operations are retrieved by priority"""
        low_priority_op = Operation(
            operation_id='low-op',
            name='low-priority',
            handler=lambda: None,
            priority=OperationPriority.LOW
        )

        high_priority_op = Operation(
            operation_id='high-op',
            name='high-priority',
            handler=lambda: None,
            priority=OperationPriority.HIGH
        )

        # Schedule in reverse priority order
        await scheduler.schedule(low_priority_op)
        await scheduler.schedule(high_priority_op)

        # Should get high priority first
        next_op = await scheduler.get_next()
        assert next_op.operation_id == 'high-op'

    def test_can_execute_no_dependencies(self, scheduler, sample_operation):
        """Test can_execute with no dependencies"""
        assert scheduler.can_execute(sample_operation) is True

    def test_can_execute_with_unsatisfied_dependency(self, scheduler):
        """Test can_execute with unsatisfied dependency"""
        dependent_op = Operation(
            operation_id='dependent-op',
            name='dependent',
            handler=lambda: None,
            dependencies=['missing-dependency']
        )

        assert scheduler.can_execute(dependent_op) is False

    def test_can_execute_with_satisfied_dependency(self, scheduler):
        """Test can_execute with satisfied dependency"""
        # Mark a dependency as completed
        dep_result = OperationResult(
            operation_id='dep-op',
            status=OperationStatus.COMPLETED
        )
        scheduler.mark_completed('dep-op', dep_result)

        dependent_op = Operation(
            operation_id='dependent-op',
            name='dependent',
            handler=lambda: None,
            dependencies=['dep-op']
        )

        assert scheduler.can_execute(dependent_op) is True

    def test_mark_completed(self, scheduler):
        """Test marking operation as completed"""
        result = OperationResult(
            operation_id='completed-op',
            status=OperationStatus.COMPLETED
        )

        scheduler.mark_completed('completed-op', result)

        stats = scheduler.get_stats()
        assert stats['operations_completed'] == 1


class TestAuditLogger:
    """Tests for AuditLogger"""

    @pytest.fixture
    def logger(self):
        """Create a fresh audit logger"""
        return AuditLogger(retention_count=100)

    @pytest.fixture
    def sample_operation(self):
        """Create a sample operation"""
        return Operation(
            operation_id='audit-op-001',
            name='audited-operation',
            handler=lambda: 'result'
        )

    @pytest.fixture
    def sample_context(self):
        """Create a sample context"""
        return ExecutionContext(
            context_id='audit-ctx-001',
            name='audit-context'
        )

    def test_log_entry(self, logger, sample_operation, sample_context):
        """Test logging an audit entry"""
        entry_id = logger.log(
            sample_operation,
            sample_context,
            'execute',
            OperationStatus.COMPLETED
        )

        assert entry_id is not None
        assert entry_id.startswith('audit-')

    def test_log_entry_with_result(self, logger, sample_operation, sample_context):
        """Test logging with operation result"""
        result = OperationResult(
            operation_id=sample_operation.operation_id,
            status=OperationStatus.COMPLETED,
            output='success',
            duration_ms=50.5
        )

        entry_id = logger.log(
            sample_operation,
            sample_context,
            'execute',
            OperationStatus.COMPLETED,
            result=result
        )

        entries = logger.get_entries(operation_id=sample_operation.operation_id)
        assert len(entries) == 1
        assert entries[0].duration_ms == 50.5

    def test_sensitive_data_redaction(self, logger, sample_context):
        """Test sensitive data is redacted in audit"""
        sensitive_op = Operation(
            operation_id='sensitive-op',
            name='sensitive',
            handler=lambda: None,
            args={
                'username': 'user123',
                'password': 'secret123',
                'api_token': 'abc123'
            }
        )

        logger.log(
            sensitive_op,
            sample_context,
            'execute',
            OperationStatus.COMPLETED
        )

        entries = logger.get_entries(operation_id='sensitive-op')
        assert len(entries) == 1

        input_summary = entries[0].input_summary
        assert input_summary['username'] == 'user123'
        assert input_summary['password'] == '[REDACTED]'
        assert input_summary['api_token'] == '[REDACTED]'

    def test_get_entries_with_filters(self, logger, sample_operation, sample_context):
        """Test getting entries with filters"""
        # Log multiple entries
        logger.log(sample_operation, sample_context, 'start', OperationStatus.EXECUTING)
        logger.log(sample_operation, sample_context, 'complete', OperationStatus.COMPLETED)

        # Filter by operation
        op_entries = logger.get_entries(operation_id=sample_operation.operation_id)
        assert len(op_entries) == 2

        # Filter by context
        ctx_entries = logger.get_entries(context_id=sample_context.context_id)
        assert len(ctx_entries) == 2

        # Filter by status
        status_entries = logger.get_entries(status=OperationStatus.COMPLETED)
        assert len(status_entries) == 1

    def test_retention_trimming(self, sample_operation, sample_context):
        """Test old entries are trimmed based on retention"""
        small_logger = AuditLogger(retention_count=5)

        # Log more entries than retention allows
        for i in range(10):
            small_logger.log(
                sample_operation,
                sample_context,
                f'action-{i}',
                OperationStatus.COMPLETED
            )

        entries = small_logger.get_entries()
        assert len(entries) <= 5

        stats = small_logger.get_stats()
        assert stats['entries_trimmed'] == 5

    def test_get_stats(self, logger, sample_operation, sample_context):
        """Test getting logger statistics"""
        logger.log(sample_operation, sample_context, 'test', OperationStatus.COMPLETED)

        stats = logger.get_stats()

        assert 'entries_logged' in stats
        assert stats['entries_logged'] == 1
        assert 'current_entries' in stats


class TestIntegrationFlow:
    """Integration tests for the complete deep execution flow"""

    @pytest.mark.asyncio
    async def test_full_workflow_execution(self):
        """Test complete workflow with multiple operations"""
        system = create_deep_execution_system()
        await system.start()

        try:
            # Create a workflow context
            workflow = system.create_context('data-processing-workflow')

            # Step 1: Load data
            load_result = await system.execute(
                name='load-data',
                handler=lambda source: {'data': [1, 2, 3, 4, 5], 'source': source},
                args={'source': 'database'},
                context_id=workflow.context_id,
                priority=OperationPriority.HIGH
            )
            assert load_result.status == OperationStatus.COMPLETED

            # Step 2: Process data
            process_result = await system.execute(
                name='process-data',
                handler=lambda data: {'processed': [x * 2 for x in data]},
                args={'data': load_result.output['data']},
                context_id=workflow.context_id
            )
            assert process_result.status == OperationStatus.COMPLETED
            assert process_result.output['processed'] == [2, 4, 6, 8, 10]

            # Step 3: Save results
            save_result = await system.execute(
                name='save-results',
                handler=lambda results: {'saved': True, 'count': len(results)},
                args={'results': process_result.output['processed']},
                context_id=workflow.context_id
            )
            assert save_result.status == OperationStatus.COMPLETED

            # Complete the workflow
            system.complete_context(workflow.context_id)
            assert workflow.completed_at is not None

            # Verify audit trail
            audit_entries = system.get_audit_entries(context_id=workflow.context_id)
            assert len(audit_entries) >= 3

            # Verify statistics
            stats = system.get_stats()
            assert stats['system']['operations_succeeded'] >= 3

        finally:
            await system.stop()

    @pytest.mark.asyncio
    async def test_nested_context_execution(self):
        """Test execution across nested contexts"""
        system = create_deep_execution_system()
        await system.start()

        try:
            # Create parent context
            parent = system.create_context('parent-workflow')

            # Execute in parent
            parent_result = await system.execute(
                name='parent-op',
                handler=lambda: 'parent-done',
                context_id=parent.context_id
            )
            assert parent_result.status == OperationStatus.COMPLETED

            # Create child context
            child = system.create_context('child-workflow', parent_context_id=parent.context_id)
            assert child.depth_level == 1

            # Execute in child
            child_result = await system.execute(
                name='child-op',
                handler=lambda: 'child-done',
                context_id=child.context_id
            )
            assert child_result.status == OperationStatus.COMPLETED

            # Verify parent-child relationship
            assert child.context_id in parent.child_contexts

        finally:
            await system.stop()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
