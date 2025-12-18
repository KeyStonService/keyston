"""
Unit Tests for Partial Rollback Manager
部分回滾管理器單元測試

Tests for the PartialRollbackManager in core/safety_mechanisms/partial_rollback.py
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from core.safety_mechanisms.partial_rollback import (
    PartialRollbackManager,
    RollbackAction,
    RollbackScope,
)


@pytest.fixture
def rollback_manager() -> PartialRollbackManager:
    """Create a fresh PartialRollbackManager instance."""
    return PartialRollbackManager(checkpoint_retention=5)


@pytest.fixture
def sample_state() -> dict[str, Any]:
    """Create a sample state dictionary."""
    return {
        "phase_id": "test-phase",
        "status": "running",
        "data": {"key1": "value1", "key2": "value2"},
        "metadata": {"timestamp": datetime.utcnow().isoformat()}
    }


class TestRollbackTriggerEvaluation:
    """Tests for rollback trigger evaluation."""
    
    def test_evaluate_validation_failure_phase_scope(self, rollback_manager):
        """Test evaluation of validation failure at phase scope."""
        action = rollback_manager.evaluate_rollback_trigger(
            condition="validation-failure",
            scope="phase"
        )
        assert action == RollbackAction.ROLLBACK_CURRENT_PHASE
    
    def test_evaluate_validation_failure_artifact_scope(self, rollback_manager):
        """Test evaluation of validation failure at artifact scope."""
        action = rollback_manager.evaluate_rollback_trigger(
            condition="validation-failure",
            scope="artifact"
        )
        assert action == RollbackAction.SKIP_AND_CONTINUE
    
    def test_evaluate_resource_exhaustion(self, rollback_manager):
        """Test evaluation of resource exhaustion."""
        action = rollback_manager.evaluate_rollback_trigger(
            condition="resource-exhaustion",
            scope="plan-unit"
        )
        assert action == RollbackAction.RESCHEDULE_WITH_BACKOFF
    
    def test_evaluate_security_violation(self, rollback_manager):
        """Test evaluation of security violation."""
        action = rollback_manager.evaluate_rollback_trigger(
            condition="security-violation",
            scope="entire-execution"
        )
        assert action == RollbackAction.EMERGENCY_STOP_AND_ROLLBACK
    
    def test_evaluate_invalid_trigger(self, rollback_manager):
        """Test evaluation with invalid trigger returns emergency stop."""
        action = rollback_manager.evaluate_rollback_trigger(
            condition="invalid-trigger",
            scope="phase"
        )
        assert action == RollbackAction.EMERGENCY_STOP_AND_ROLLBACK
    
    def test_evaluate_invalid_scope(self, rollback_manager):
        """Test evaluation with invalid scope returns emergency stop."""
        action = rollback_manager.evaluate_rollback_trigger(
            condition="validation-failure",
            scope="invalid-scope"
        )
        assert action == RollbackAction.EMERGENCY_STOP_AND_ROLLBACK


class TestCheckpointManagement:
    """Tests for checkpoint management."""
    
    def test_create_checkpoint(self, rollback_manager, sample_state):
        """Test checkpoint creation."""
        execution_id = "exec-123"
        phase_id = "phase-1"
        
        checkpoint_id = rollback_manager.create_checkpoint(
            execution_id=execution_id,
            phase_id=phase_id,
            state=sample_state
        )
        
        assert checkpoint_id is not None
        assert checkpoint_id.startswith(f"cp_{execution_id}_{phase_id}_")
    
    def test_create_multiple_checkpoints(self, rollback_manager, sample_state):
        """Test creating multiple checkpoints."""
        execution_id = "exec-123"
        
        checkpoint_ids = []
        for i in range(3):
            checkpoint_id = rollback_manager.create_checkpoint(
                execution_id=execution_id,
                phase_id=f"phase-{i}",
                state=sample_state
            )
            checkpoint_ids.append(checkpoint_id)
        
        assert len(checkpoint_ids) == 3
        assert len(set(checkpoint_ids)) == 3  # All unique
    
    def test_list_checkpoints(self, rollback_manager, sample_state):
        """Test listing checkpoints."""
        execution_id = "exec-123"
        
        # Create checkpoints
        for i in range(3):
            rollback_manager.create_checkpoint(
                execution_id=execution_id,
                phase_id=f"phase-{i}",
                state=sample_state
            )
        
        checkpoints = rollback_manager.list_checkpoints(execution_id)
        assert len(checkpoints) == 3
    
    def test_checkpoint_retention(self, rollback_manager, sample_state):
        """Test checkpoint retention policy."""
        execution_id = "exec-123"
        retention = rollback_manager.checkpoint_retention
        
        # Create more checkpoints than retention limit
        for i in range(retention + 3):
            rollback_manager.create_checkpoint(
                execution_id=execution_id,
                phase_id=f"phase-{i}",
                state=sample_state
            )
        
        checkpoints = rollback_manager.list_checkpoints(execution_id)
        assert len(checkpoints) == retention
    
    def test_get_checkpoint_count(self, rollback_manager, sample_state):
        """Test getting checkpoint count."""
        execution_id = "exec-123"
        
        # Initially zero
        assert rollback_manager.get_checkpoint_count(execution_id) == 0
        
        # After creating checkpoints
        rollback_manager.create_checkpoint(
            execution_id=execution_id,
            phase_id="phase-1",
            state=sample_state
        )
        rollback_manager.create_checkpoint(
            execution_id=execution_id,
            phase_id="phase-2",
            state=sample_state
        )
        
        assert rollback_manager.get_checkpoint_count(execution_id) == 2


class TestRollbackExecution:
    """Tests for rollback execution."""
    
    def test_execute_phase_rollback(self, rollback_manager, sample_state):
        """Test executing phase-level rollback."""
        execution_id = "exec-123"
        phase_id = "phase-1"
        
        # Create checkpoint
        rollback_manager.create_checkpoint(
            execution_id=execution_id,
            phase_id=phase_id,
            state=sample_state
        )
        
        # Execute rollback
        result = rollback_manager.execute_rollback(
            scope="phase",
            target=phase_id,
            execution_id=execution_id
        )
        
        assert result.success is True
        assert result.scope == RollbackScope.PHASE
        assert result.target_id == phase_id
        assert phase_id in result.rolled_back_items
    
    def test_execute_rollback_without_checkpoint(self, rollback_manager):
        """Test rollback without checkpoint."""
        result = rollback_manager.execute_rollback(
            scope="phase",
            target="phase-1",
            execution_id="exec-nonexistent"
        )
        
        # Should succeed but without checkpoint restoration
        assert result.success is True
        assert result.checkpoint_id is None
    
    def test_execute_rollback_invalid_scope(self, rollback_manager):
        """Test rollback with invalid scope."""
        result = rollback_manager.execute_rollback(
            scope="invalid-scope",
            target="phase-1"
        )
        
        assert result.success is False
        assert "Invalid rollback scope" in result.message


class TestDependencyTracking:
    """Tests for dependency tracking."""
    
    def test_register_dependency(self, rollback_manager):
        """Test registering a dependency."""
        rollback_manager.register_dependency(
            source="task-b",
            target="task-a"  # task-b depends on task-a
        )
        
        # Should not raise any exceptions
        assert True
    
    def test_find_dependent_items(self, rollback_manager):
        """Test finding dependent items."""
        # Build dependency graph:
        # A → B → C
        # A → D
        rollback_manager.register_dependency("task-b", "task-a")
        rollback_manager.register_dependency("task-c", "task-b")
        rollback_manager.register_dependency("task-d", "task-a")
        
        # Rolling back A should affect B, C, D
        result = rollback_manager.execute_rollback(
            scope="phase",
            target="task-a"
        )
        
        rolled_back = set(result.rolled_back_items)
        assert "task-a" in rolled_back
        assert "task-b" in rolled_back
        assert "task-c" in rolled_back
        assert "task-d" in rolled_back
    
    def test_circular_dependency_handling(self, rollback_manager):
        """Test handling of circular dependencies."""
        # Create circular dependency: A → B → C → A
        rollback_manager.register_dependency("task-b", "task-a")
        rollback_manager.register_dependency("task-c", "task-b")
        rollback_manager.register_dependency("task-a", "task-c")
        
        # Should handle gracefully (visited tracking prevents infinite loop)
        result = rollback_manager.execute_rollback(
            scope="phase",
            target="task-a"
        )
        
        assert result.success is True
        # All tasks should be in rolled_back_items
        rolled_back = set(result.rolled_back_items)
        assert "task-a" in rolled_back
        assert "task-b" in rolled_back
        assert "task-c" in rolled_back


class TestCheckpointRestoration:
    """Tests for checkpoint restoration."""
    
    def test_restore_from_checkpoint(self, rollback_manager, sample_state):
        """Test restoring from a checkpoint."""
        execution_id = "exec-123"
        phase_id = "phase-1"
        
        # Create checkpoint
        checkpoint_id = rollback_manager.create_checkpoint(
            execution_id=execution_id,
            phase_id=phase_id,
            state=sample_state
        )
        
        # Restore from checkpoint
        result = rollback_manager.restore_from_checkpoint(checkpoint_id)
        
        assert result.success is True
        assert result.checkpoint_id == checkpoint_id
        assert result.target_id == phase_id
    
    def test_restore_nonexistent_checkpoint(self, rollback_manager):
        """Test restoring from nonexistent checkpoint."""
        result = rollback_manager.restore_from_checkpoint("nonexistent-checkpoint")
        
        assert result.success is False
        assert "not found" in result.message.lower()


class TestCheckpointCleanup:
    """Tests for checkpoint cleanup."""
    
    def test_cleanup_old_checkpoints(self, rollback_manager, sample_state):
        """Test cleaning up old checkpoints."""
        execution_id = "exec-123"
        
        # Create 10 checkpoints
        for i in range(10):
            rollback_manager.create_checkpoint(
                execution_id=execution_id,
                phase_id=f"phase-{i}",
                state=sample_state
            )
        
        # Cleanup, keeping only 3
        removed = rollback_manager.cleanup_old_checkpoints(
            execution_id=execution_id,
            keep_count=3
        )
        
        assert removed == 7  # 10 - 3 = 7
        assert rollback_manager.get_checkpoint_count(execution_id) == 3
    
    def test_cleanup_nonexistent_execution(self, rollback_manager):
        """Test cleanup for nonexistent execution."""
        removed = rollback_manager.cleanup_old_checkpoints(
            execution_id="nonexistent",
            keep_count=5
        )
        
        assert removed == 0


class TestEdgeCases:
    """Tests for edge cases and error conditions."""
    
    def test_empty_state(self, rollback_manager):
        """Test checkpoint with empty state."""
        checkpoint_id = rollback_manager.create_checkpoint(
            execution_id="exec-123",
            phase_id="phase-1",
            state={}
        )
        
        assert checkpoint_id is not None
    
    def test_large_state(self, rollback_manager):
        """Test checkpoint with large state."""
        large_state = {
            f"key_{i}": f"value_{i}" * 1000
            for i in range(100)
        }
        
        checkpoint_id = rollback_manager.create_checkpoint(
            execution_id="exec-123",
            phase_id="phase-1",
            state=large_state
        )
        
        assert checkpoint_id is not None
    
    def test_concurrent_rollbacks(self, rollback_manager, sample_state):
        """Test multiple concurrent rollbacks."""
        # Create checkpoints for different executions
        exec_ids = [f"exec-{i}" for i in range(5)]
        
        for exec_id in exec_ids:
            rollback_manager.create_checkpoint(
                execution_id=exec_id,
                phase_id="phase-1",
                state=sample_state
            )
        
        # Execute rollbacks for all
        results = []
        for exec_id in exec_ids:
            result = rollback_manager.execute_rollback(
                scope="phase",
                target="phase-1",
                execution_id=exec_id
            )
            results.append(result)
        
        # All should succeed
        assert all(r.success for r in results)
        assert len(results) == 5


class TestIntegration:
    """Integration tests combining multiple features."""
    
    def test_full_workflow(self, rollback_manager, sample_state):
        """Test complete workflow: checkpoint, dependencies, rollback, restore."""
        execution_id = "exec-integration"
        
        # 1. Register dependencies
        rollback_manager.register_dependency("task-2", "task-1")
        rollback_manager.register_dependency("task-3", "task-2")
        
        # 2. Create checkpoints at each step
        cp1 = rollback_manager.create_checkpoint(
            execution_id=execution_id,
            phase_id="task-1",
            state={**sample_state, "task": "task-1"}
        )
        
        cp2 = rollback_manager.create_checkpoint(
            execution_id=execution_id,
            phase_id="task-2",
            state={**sample_state, "task": "task-2"}
        )
        
        cp3 = rollback_manager.create_checkpoint(
            execution_id=execution_id,
            phase_id="task-3",
            state={**sample_state, "task": "task-3"}
        )
        
        # 3. Simulate failure in task-2
        rollback_result = rollback_manager.execute_rollback(
            scope="phase",
            target="task-2",
            execution_id=execution_id
        )
        
        assert rollback_result.success is True
        assert "task-2" in rollback_result.rolled_back_items
        assert "task-3" in rollback_result.rolled_back_items  # Dependent
        
        # 4. Restore from checkpoint
        restore_result = rollback_manager.restore_from_checkpoint(cp1)
        
        assert restore_result.success is True
        assert restore_result.checkpoint_id == cp1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
