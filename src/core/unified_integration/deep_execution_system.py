"""
═══════════════════════════════════════════════════════════════════════════════
                    SynergyMesh Deep Execution System
                    深度執行系統 - 多層級系統操作引擎
═══════════════════════════════════════════════════════════════════════════════

This module provides deep execution capabilities for complex system operations,
enabling multi-level execution contexts, operation chaining, and comprehensive
auditing.

Core Capabilities:
- Multi-level execution contexts (多層級執行上下文)
- Operation dependency management (操作依賴管理)
- Deep validation and verification (深度驗證)
- Comprehensive operation auditing (全面操作審計)
- Automatic rollback support (自動回滾支援)

Design Principles:
- Hierarchical execution context management
- Dependency-aware operation scheduling
- Fail-safe execution with automatic recovery
- Complete audit trail for compliance
"""

import asyncio
import contextlib
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


class OperationStatus(Enum):
    """Operation execution status"""
    PENDING = 'pending'
    QUEUED = 'queued'
    VALIDATING = 'validating'
    EXECUTING = 'executing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    ROLLED_BACK = 'rolled_back'


class OperationPriority(Enum):
    """Operation priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class ValidationLevel(Enum):
    """Validation depth levels"""
    SHALLOW = 'shallow'    # Basic parameter validation
    STANDARD = 'standard'  # Standard validation with type checking
    DEEP = 'deep'          # Deep validation with dependency checks
    STRICT = 'strict'      # Full validation with external verification


class ExecutionDepth(Enum):
    """Execution depth levels"""
    SURFACE = 'surface'      # Surface-level execution
    INTERMEDIATE = 'intermediate'  # Intermediate depth
    DEEP = 'deep'            # Deep execution with full context
    RECURSIVE = 'recursive'  # Recursive execution through all layers


@dataclass
class OperationResult:
    """Result of an operation execution"""
    operation_id: str
    status: OperationStatus
    output: Any = None
    error: str | None = None
    duration_ms: float = 0.0
    validation_results: dict[str, Any] = field(default_factory=dict)
    audit_entry_id: str | None = None
    rollback_available: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            'operation_id': self.operation_id,
            'status': self.status.value,
            'output': self.output,
            'error': self.error,
            'duration_ms': self.duration_ms,
            'validation_results': self.validation_results,
            'audit_entry_id': self.audit_entry_id,
            'rollback_available': self.rollback_available,
            'metadata': self.metadata
        }


@dataclass
class Operation:
    """A system operation to execute"""
    operation_id: str
    name: str
    handler: Callable
    args: dict[str, Any] = field(default_factory=dict)
    priority: OperationPriority = OperationPriority.NORMAL
    validation_level: ValidationLevel = ValidationLevel.STANDARD
    execution_depth: ExecutionDepth = ExecutionDepth.DEEP
    dependencies: list[str] = field(default_factory=list)
    timeout_seconds: float = 60.0
    retry_count: int = 0
    max_retries: int = 3
    rollback_handler: Callable | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            'operation_id': self.operation_id,
            'name': self.name,
            'priority': self.priority.value,
            'validation_level': self.validation_level.value,
            'execution_depth': self.execution_depth.value,
            'dependencies': self.dependencies,
            'timeout_seconds': self.timeout_seconds,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class ExecutionContext:
    """Execution context for operations"""
    context_id: str
    name: str
    parent_context_id: str | None = None
    depth_level: int = 0
    state: dict[str, Any] = field(default_factory=dict)
    operations: list[str] = field(default_factory=list)
    results: dict[str, OperationResult] = field(default_factory=dict)
    child_contexts: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            'context_id': self.context_id,
            'name': self.name,
            'parent_context_id': self.parent_context_id,
            'depth_level': self.depth_level,
            'operations_count': len(self.operations),
            'child_contexts_count': len(self.child_contexts),
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'metadata': self.metadata
        }


@dataclass
class AuditEntry:
    """Audit entry for operation tracking"""
    entry_id: str
    operation_id: str
    context_id: str
    operation_name: str
    action: str
    status: OperationStatus
    user_id: str | None = None
    input_summary: dict[str, Any] = field(default_factory=dict)
    output_summary: dict[str, Any] = field(default_factory=dict)
    error_details: str | None = None
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            'entry_id': self.entry_id,
            'operation_id': self.operation_id,
            'context_id': self.context_id,
            'operation_name': self.operation_name,
            'action': self.action,
            'status': self.status.value,
            'user_id': self.user_id,
            'input_summary': self.input_summary,
            'output_summary': self.output_summary,
            'error_details': self.error_details,
            'duration_ms': self.duration_ms,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class DeepExecutionConfig:
    """Configuration for the deep execution system"""
    name: str = 'synergymesh-deep-execution'
    max_concurrent_operations: int = 20
    max_context_depth: int = 10
    default_timeout_seconds: float = 60.0
    enable_auto_rollback: bool = True
    enable_deep_validation: bool = True
    enable_audit_logging: bool = True
    audit_retention_count: int = 10000
    validation_timeout_seconds: float = 10.0


class OperationValidator:
    """
    操作驗證器 - Operation Validator
    
    Provides multi-level validation for operations before execution.
    """

    def __init__(self, config: DeepExecutionConfig):
        """Initialize the validator"""
        self.config = config
        self._validators: dict[ValidationLevel, list[Callable]] = {
            ValidationLevel.SHALLOW: [],
            ValidationLevel.STANDARD: [],
            ValidationLevel.DEEP: [],
            ValidationLevel.STRICT: []
        }
        self._stats = {
            'validations_performed': 0,
            'validations_passed': 0,
            'validations_failed': 0
        }

    async def validate(
        self,
        operation: Operation,
        context: ExecutionContext
    ) -> dict[str, Any]:
        """
        Validate an operation before execution
        
        Args:
            operation: Operation to validate
            context: Execution context
            
        Returns:
            Validation results
        """
        self._stats['validations_performed'] += 1
        results = {
            'valid': True,
            'level': operation.validation_level.value,
            'checks': [],
            'errors': [],
            'warnings': []
        }

        try:
            # Always run shallow validation
            await self._run_level_validation(
                ValidationLevel.SHALLOW, operation, context, results
            )

            # Run standard validation if level is standard or higher
            if operation.validation_level in [
                ValidationLevel.STANDARD,
                ValidationLevel.DEEP,
                ValidationLevel.STRICT
            ]:
                await self._run_level_validation(
                    ValidationLevel.STANDARD, operation, context, results
                )

            # Run deep validation if level is deep or strict
            if operation.validation_level in [
                ValidationLevel.DEEP,
                ValidationLevel.STRICT
            ]:
                await self._run_level_validation(
                    ValidationLevel.DEEP, operation, context, results
                )

            # Run strict validation if level is strict
            if operation.validation_level == ValidationLevel.STRICT:
                await self._run_level_validation(
                    ValidationLevel.STRICT, operation, context, results
                )

            # Built-in validations
            await self._run_builtin_validations(operation, context, results)

            if results['valid']:
                self._stats['validations_passed'] += 1
            else:
                self._stats['validations_failed'] += 1

        except Exception as e:
            results['valid'] = False
            results['errors'].append(f"Validation error: {str(e)}")
            self._stats['validations_failed'] += 1

        return results

    async def _run_level_validation(
        self,
        level: ValidationLevel,
        operation: Operation,
        context: ExecutionContext,
        results: dict[str, Any]
    ) -> None:
        """Run validators for a specific level"""
        for validator in self._validators[level]:
            try:
                if asyncio.iscoroutinefunction(validator):
                    result = await asyncio.wait_for(
                        validator(operation, context),
                        timeout=self.config.validation_timeout_seconds
                    )
                else:
                    result = validator(operation, context)

                if result:
                    if result.get('valid', True):
                        results['checks'].append({
                            'level': level.value,
                            'name': result.get('name', 'custom'),
                            'passed': True
                        })
                    else:
                        results['valid'] = False
                        results['errors'].append(result.get('error', 'Validation failed'))
                        results['checks'].append({
                            'level': level.value,
                            'name': result.get('name', 'custom'),
                            'passed': False,
                            'error': result.get('error')
                        })
            except TimeoutError:
                results['warnings'].append(f"Validator at {level.value} timed out")
            except Exception as e:
                results['warnings'].append(f"Validator error at {level.value}: {str(e)}")

    async def _run_builtin_validations(
        self,
        operation: Operation,
        context: ExecutionContext,
        results: dict[str, Any]
    ) -> None:
        """Run built-in validations"""
        # Check handler is callable
        if not callable(operation.handler):
            results['valid'] = False
            results['errors'].append("Operation handler is not callable")
            return

        results['checks'].append({
            'level': 'builtin',
            'name': 'handler_callable',
            'passed': True
        })

        # Check context depth
        if context.depth_level >= self.config.max_context_depth:
            results['valid'] = False
            results['errors'].append(
                f"Context depth {context.depth_level} exceeds max {self.config.max_context_depth}"
            )
            return

        results['checks'].append({
            'level': 'builtin',
            'name': 'context_depth',
            'passed': True
        })

        # Check timeout is reasonable
        if operation.timeout_seconds <= 0:
            results['warnings'].append("Operation timeout is not positive, using default")

        results['checks'].append({
            'level': 'builtin',
            'name': 'timeout_valid',
            'passed': operation.timeout_seconds > 0
        })

    def add_validator(self, level: ValidationLevel, validator: Callable) -> None:
        """Add a custom validator"""
        self._validators[level].append(validator)

    def get_stats(self) -> dict[str, Any]:
        """Get validator statistics"""
        return self._stats.copy()


class OperationScheduler:
    """
    操作調度器 - Operation Scheduler
    
    Schedules operations based on priority and dependencies.
    """

    def __init__(self, max_concurrent: int = 20):
        """Initialize the scheduler"""
        self.max_concurrent = max_concurrent
        self._queues: dict[OperationPriority, asyncio.Queue] = {
            priority: asyncio.Queue() for priority in OperationPriority
        }
        self._running: dict[str, asyncio.Task] = {}
        self._completed: dict[str, OperationResult] = {}
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._stats = {
            'operations_scheduled': 0,
            'operations_completed': 0,
            'operations_failed': 0
        }

    async def schedule(self, operation: Operation) -> None:
        """Schedule an operation for execution"""
        await self._queues[operation.priority].put(operation)
        self._stats['operations_scheduled'] += 1

    async def get_next(self) -> Operation | None:
        """Get the next operation to execute (highest priority first)"""
        for priority in OperationPriority:
            queue = self._queues[priority]
            if not queue.empty():
                return await queue.get()
        return None

    def can_execute(self, operation: Operation) -> bool:
        """Check if an operation can be executed (dependencies satisfied)"""
        for dep_id in operation.dependencies:
            if dep_id not in self._completed:
                return False
            if self._completed[dep_id].status != OperationStatus.COMPLETED:
                return False
        return True

    def mark_completed(self, operation_id: str, result: OperationResult) -> None:
        """Mark an operation as completed"""
        self._completed[operation_id] = result
        self._running.pop(operation_id, None)
        if result.status == OperationStatus.COMPLETED:
            self._stats['operations_completed'] += 1
        else:
            self._stats['operations_failed'] += 1

    def get_stats(self) -> dict[str, Any]:
        """Get scheduler statistics"""
        queue_sizes = {
            p.name: self._queues[p].qsize() for p in OperationPriority
        }
        return {
            **self._stats,
            'running_count': len(self._running),
            'queue_sizes': queue_sizes
        }


class AuditLogger:
    """
    審計記錄器 - Audit Logger
    
    Provides comprehensive audit logging for all operations.
    """

    def __init__(self, retention_count: int = 10000):
        """Initialize the audit logger"""
        self.retention_count = retention_count
        self._entries: list[AuditEntry] = []
        self._stats = {
            'entries_logged': 0,
            'entries_trimmed': 0
        }

    def log(
        self,
        operation: Operation,
        context: ExecutionContext,
        action: str,
        status: OperationStatus,
        result: OperationResult | None = None,
        user_id: str | None = None
    ) -> str:
        """
        Log an audit entry
        
        Args:
            operation: The operation being audited
            context: Execution context
            action: Action being performed (e.g., 'execute', 'rollback')
            status: Current operation status
            result: Optional operation result
            user_id: Optional user identifier
            
        Returns:
            Audit entry ID
        """
        entry = AuditEntry(
            entry_id=f"audit-{uuid4().hex[:12]}",
            operation_id=operation.operation_id,
            context_id=context.context_id,
            operation_name=operation.name,
            action=action,
            status=status,
            user_id=user_id,
            input_summary=self._summarize_input(operation.args),
            output_summary=self._summarize_output(result) if result else {},
            error_details=result.error if result else None,
            duration_ms=result.duration_ms if result else 0.0,
            metadata={
                'priority': operation.priority.value,
                'validation_level': operation.validation_level.value,
                'execution_depth': operation.execution_depth.value,
                'context_depth': context.depth_level
            }
        )

        self._entries.append(entry)
        self._stats['entries_logged'] += 1

        # Trim old entries if needed
        if len(self._entries) > self.retention_count:
            trim_count = len(self._entries) - self.retention_count
            self._entries = self._entries[trim_count:]
            self._stats['entries_trimmed'] += trim_count

        return entry.entry_id

    def _summarize_input(self, args: dict[str, Any]) -> dict[str, Any]:
        """Summarize input arguments for audit (redact sensitive data)"""
        # Specific sensitive field patterns using word boundaries
        sensitive_patterns = [
            'password', 'passwd', 'secret', 'api_token', 'access_token',
            'refresh_token', 'auth_token', 'api_key', 'private_key',
            'secret_key', 'encryption_key', 'credential', 'bearer'
        ]
        summary = {}
        for key, value in args.items():
            key_lower = key.lower()
            # Check if key matches or ends with sensitive patterns
            is_sensitive = any(
                key_lower == pattern or key_lower.endswith(f'_{pattern}') or key_lower.endswith(pattern)
                for pattern in sensitive_patterns
            )
            if is_sensitive:
                summary[key] = '[REDACTED]'
            elif isinstance(value, (str, int, float, bool)):
                summary[key] = value
            elif isinstance(value, (list, dict)):
                summary[key] = f'<{type(value).__name__} with {len(value)} items>'
            else:
                summary[key] = f'<{type(value).__name__}>'
        return summary

    def _summarize_output(self, result: OperationResult) -> dict[str, Any]:
        """Summarize output for audit"""
        return {
            'status': result.status.value,
            'has_output': result.output is not None,
            'has_error': result.error is not None,
            'duration_ms': result.duration_ms
        }

    def get_entries(
        self,
        operation_id: str | None = None,
        context_id: str | None = None,
        status: OperationStatus | None = None,
        limit: int = 100
    ) -> list[AuditEntry]:
        """Get audit entries with optional filters"""
        entries = self._entries

        if operation_id:
            entries = [e for e in entries if e.operation_id == operation_id]
        if context_id:
            entries = [e for e in entries if e.context_id == context_id]
        if status:
            entries = [e for e in entries if e.status == status]

        return entries[-limit:]

    def get_stats(self) -> dict[str, Any]:
        """Get audit logger statistics"""
        return {
            **self._stats,
            'current_entries': len(self._entries)
        }


class DeepExecutionSystem:
    """
    深度執行系統 - Deep Execution System
    
    Central system for managing deep execution of system operations.
    Provides multi-level execution contexts, operation scheduling,
    validation, and comprehensive auditing.
    
    Usage:
        system = DeepExecutionSystem()
        await system.start()
        
        # Create an execution context
        context = system.create_context('main-workflow')
        
        # Execute an operation
        result = await system.execute(
            name='process_data',
            handler=my_handler_function,
            args={'data': my_data},
            context_id=context.context_id
        )
        
        # Get audit trail
        audit = system.get_audit_entries(context_id=context.context_id)
    """

    def __init__(self, config: DeepExecutionConfig | None = None):
        """Initialize the deep execution system"""
        self.config = config or DeepExecutionConfig()

        # Core components
        self.validator = OperationValidator(self.config)
        self.scheduler = OperationScheduler(self.config.max_concurrent_operations)
        self.audit_logger = AuditLogger(self.config.audit_retention_count)

        # State management
        self._contexts: dict[str, ExecutionContext] = {}
        self._operations: dict[str, Operation] = {}
        self._rollback_stack: dict[str, list[Operation]] = {}
        self._operation_to_context: dict[str, str] = {}  # O(1) operation -> context lookup

        # Runtime state
        self._is_running = False
        self._processor_task: asyncio.Task | None = None

        # Statistics
        self._stats = {
            'operations_executed': 0,
            'operations_succeeded': 0,
            'operations_failed': 0,
            'rollbacks_executed': 0,
            'contexts_created': 0
        }

        logger.info("DeepExecutionSystem initialized - 深度執行系統已初始化")

    async def start(self) -> None:
        """Start the deep execution system"""
        if self._is_running:
            return

        self._is_running = True
        self._processor_task = asyncio.create_task(self._processing_loop())

        logger.info("DeepExecutionSystem started - 深度執行系統已啟動")

    async def stop(self) -> None:
        """Stop the deep execution system"""
        self._is_running = False

        if self._processor_task:
            self._processor_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._processor_task

        logger.info("DeepExecutionSystem stopped - 深度執行系統已停止")

    def create_context(
        self,
        name: str,
        parent_context_id: str | None = None,
        initial_state: dict[str, Any] | None = None
    ) -> ExecutionContext:
        """
        Create a new execution context
        
        創建新的執行上下文
        
        Args:
            name: Context name
            parent_context_id: Optional parent context ID for nested contexts
            initial_state: Optional initial state
            
        Returns:
            New execution context
        """
        # Determine depth level
        depth_level = 0
        if parent_context_id:
            parent = self._contexts.get(parent_context_id)
            if parent:
                depth_level = parent.depth_level + 1
                if depth_level > self.config.max_context_depth:
                    raise ValueError(
                        f"Max context depth {self.config.max_context_depth} exceeded"
                    )

        context = ExecutionContext(
            context_id=f"ctx-{uuid4().hex[:8]}",
            name=name,
            parent_context_id=parent_context_id,
            depth_level=depth_level,
            state=initial_state or {}
        )

        self._contexts[context.context_id] = context
        self._rollback_stack[context.context_id] = []
        self._stats['contexts_created'] += 1

        # Link to parent
        if parent_context_id and parent_context_id in self._contexts:
            self._contexts[parent_context_id].child_contexts.append(context.context_id)

        logger.debug(f"Context created: {context.context_id} (depth={depth_level})")
        return context

    def get_context(self, context_id: str) -> ExecutionContext | None:
        """Get an execution context by ID"""
        return self._contexts.get(context_id)

    async def execute(
        self,
        name: str,
        handler: Callable,
        args: dict[str, Any] | None = None,
        context_id: str | None = None,
        priority: OperationPriority = OperationPriority.NORMAL,
        validation_level: ValidationLevel = ValidationLevel.STANDARD,
        execution_depth: ExecutionDepth = ExecutionDepth.DEEP,
        dependencies: list[str] | None = None,
        timeout_seconds: float | None = None,
        rollback_handler: Callable | None = None,
        user_id: str | None = None
    ) -> OperationResult:
        """
        Execute an operation with deep execution capabilities
        
        執行具有深度執行能力的操作
        
        Args:
            name: Operation name
            handler: Operation handler function
            args: Operation arguments
            context_id: Optional context ID (creates new if not provided)
            priority: Operation priority
            validation_level: Validation depth level
            execution_depth: Execution depth level
            dependencies: List of operation IDs this depends on
            timeout_seconds: Operation timeout
            rollback_handler: Optional rollback handler
            user_id: Optional user identifier for audit
            
        Returns:
            Operation result
        """
        # Get or create context
        if context_id:
            context = self._contexts.get(context_id)
            if not context:
                raise ValueError(f"Context not found: {context_id}")
        else:
            context = self.create_context(f"auto-{name}")

        # Create operation
        operation = Operation(
            operation_id=f"op-{uuid4().hex[:8]}",
            name=name,
            handler=handler,
            args=args or {},
            priority=priority,
            validation_level=validation_level,
            execution_depth=execution_depth,
            dependencies=dependencies or [],
            timeout_seconds=timeout_seconds or self.config.default_timeout_seconds,
            rollback_handler=rollback_handler
        )

        self._operations[operation.operation_id] = operation
        self._operation_to_context[operation.operation_id] = context.context_id  # O(1) mapping
        context.operations.append(operation.operation_id)

        # Execute the operation
        result = await self._execute_operation(operation, context, user_id)

        # Store result in context
        context.results[operation.operation_id] = result

        return result

    async def _execute_operation(
        self,
        operation: Operation,
        context: ExecutionContext,
        user_id: str | None = None
    ) -> OperationResult:
        """Execute a single operation"""
        start_time = datetime.now(UTC)
        result = OperationResult(
            operation_id=operation.operation_id,
            status=OperationStatus.PENDING
        )

        try:
            # Check dependencies
            if not self.scheduler.can_execute(operation):
                result.status = OperationStatus.QUEUED
                await self.scheduler.schedule(operation)
                # Wait for dependencies with exponential backoff
                wait_time = 0.1  # Start with 100ms
                max_wait = 2.0  # Max wait between checks
                total_waited = 0.0
                while total_waited < operation.timeout_seconds:
                    if self.scheduler.can_execute(operation):
                        break
                    await asyncio.sleep(wait_time)
                    total_waited += wait_time
                    wait_time = min(wait_time * 1.5, max_wait)  # Exponential backoff
                else:
                    result.status = OperationStatus.FAILED
                    result.error = "Dependency timeout"
                    return result

            # Validate operation
            if self.config.enable_deep_validation:
                result.status = OperationStatus.VALIDATING
                validation_results = await self.validator.validate(operation, context)
                result.validation_results = validation_results

                if not validation_results.get('valid', False):
                    result.status = OperationStatus.FAILED
                    result.error = "; ".join(validation_results.get('errors', ['Validation failed']))

                    # Log audit entry
                    if self.config.enable_audit_logging:
                        result.audit_entry_id = self.audit_logger.log(
                            operation, context, 'validation_failed',
                            OperationStatus.FAILED, result, user_id
                        )

                    self._stats['operations_failed'] += 1
                    return result

            # Execute operation
            result.status = OperationStatus.EXECUTING
            self._stats['operations_executed'] += 1

            # Log audit entry for execution start
            if self.config.enable_audit_logging:
                self.audit_logger.log(
                    operation, context, 'execute_start',
                    OperationStatus.EXECUTING, None, user_id
                )

            # Add to rollback stack if rollback handler provided
            if operation.rollback_handler:
                self._rollback_stack[context.context_id].append(operation)
                result.rollback_available = True

            # Execute with timeout
            try:
                if asyncio.iscoroutinefunction(operation.handler):
                    output = await asyncio.wait_for(
                        operation.handler(**operation.args),
                        timeout=operation.timeout_seconds
                    )
                else:
                    output = operation.handler(**operation.args)

                result.output = output
                result.status = OperationStatus.COMPLETED
                self._stats['operations_succeeded'] += 1

            except TimeoutError:
                result.status = OperationStatus.FAILED
                result.error = f"Operation timed out after {operation.timeout_seconds}s"
                self._stats['operations_failed'] += 1

                # Attempt rollback if enabled
                if self.config.enable_auto_rollback and operation.rollback_handler:
                    await self._rollback_operation(operation, context)
                    result.status = OperationStatus.ROLLED_BACK

            except Exception as e:
                result.status = OperationStatus.FAILED
                result.error = str(e)
                operation.retry_count += 1

                # Retry logic
                if operation.retry_count < operation.max_retries:
                    logger.warning(
                        f"Operation {operation.name} failed, retrying "
                        f"({operation.retry_count}/{operation.max_retries})"
                    )
                    return await self._execute_operation(operation, context, user_id)

                self._stats['operations_failed'] += 1

                # Attempt rollback if enabled
                if self.config.enable_auto_rollback and operation.rollback_handler:
                    await self._rollback_operation(operation, context)
                    result.status = OperationStatus.ROLLED_BACK

        finally:
            end_time = datetime.now(UTC)
            result.duration_ms = (end_time - start_time).total_seconds() * 1000

            # Log final audit entry
            if self.config.enable_audit_logging:
                result.audit_entry_id = self.audit_logger.log(
                    operation, context, 'execute_complete',
                    result.status, result, user_id
                )

            # Update scheduler
            self.scheduler.mark_completed(operation.operation_id, result)

        return result

    async def _rollback_operation(
        self,
        operation: Operation,
        context: ExecutionContext
    ) -> bool:
        """Rollback an operation"""
        if not operation.rollback_handler:
            return False

        try:
            logger.info(f"Rolling back operation: {operation.name}")

            if asyncio.iscoroutinefunction(operation.rollback_handler):
                await operation.rollback_handler(**operation.args)
            else:
                operation.rollback_handler(**operation.args)

            self._stats['rollbacks_executed'] += 1

            # Log rollback audit entry
            if self.config.enable_audit_logging:
                self.audit_logger.log(
                    operation, context, 'rollback',
                    OperationStatus.ROLLED_BACK, None, None
                )

            return True

        except Exception as e:
            logger.error(f"Rollback failed for {operation.name}: {e}")
            return False

    async def rollback_context(self, context_id: str) -> list[str]:
        """
        Rollback all operations in a context (in reverse order)
        
        回滾上下文中的所有操作
        
        Args:
            context_id: Context ID to rollback
            
        Returns:
            List of rolled back operation IDs
        """
        context = self._contexts.get(context_id)
        if not context:
            return []

        rolled_back = []
        rollback_stack = self._rollback_stack.get(context_id, [])

        # Rollback in reverse order
        while rollback_stack:
            operation = rollback_stack.pop()
            if await self._rollback_operation(operation, context):
                rolled_back.append(operation.operation_id)

        return rolled_back

    def complete_context(self, context_id: str) -> bool:
        """
        Mark a context as completed
        
        Args:
            context_id: Context ID to complete
            
        Returns:
            True if successful
        """
        context = self._contexts.get(context_id)
        if not context:
            return False

        context.completed_at = datetime.now(UTC)
        return True

    async def _processing_loop(self) -> None:
        """Background processing loop for queued operations"""
        while self._is_running:
            try:
                operation = await self.scheduler.get_next()
                if operation and self.scheduler.can_execute(operation):
                    # Find context using O(1) lookup
                    context_id = self._operation_to_context.get(operation.operation_id)
                    context = self._contexts.get(context_id) if context_id else None

                    if context:
                        await self._execute_operation(operation, context)

                await asyncio.sleep(0.01)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Processing loop error: {e}")
                await asyncio.sleep(0.1)

    def get_audit_entries(
        self,
        operation_id: str | None = None,
        context_id: str | None = None,
        status: OperationStatus | None = None,
        limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get audit entries"""
        entries = self.audit_logger.get_entries(
            operation_id, context_id, status, limit
        )
        return [e.to_dict() for e in entries]

    def get_stats(self) -> dict[str, Any]:
        """Get system statistics"""
        return {
            'system': self._stats.copy(),
            'validator': self.validator.get_stats(),
            'scheduler': self.scheduler.get_stats(),
            'audit_logger': self.audit_logger.get_stats(),
            'is_running': self._is_running,
            'active_contexts': len(self._contexts),
            'total_operations': len(self._operations)
        }


# Factory function
def create_deep_execution_system(
    config: DeepExecutionConfig | None = None
) -> DeepExecutionSystem:
    """Create a new DeepExecutionSystem instance"""
    return DeepExecutionSystem(config)


# Export classes
__all__ = [
    'DeepExecutionSystem',
    'DeepExecutionConfig',
    'Operation',
    'OperationResult',
    'OperationStatus',
    'OperationPriority',
    'ExecutionContext',
    'ExecutionDepth',
    'ValidationLevel',
    'AuditEntry',
    'AuditLogger',
    'OperationValidator',
    'OperationScheduler',
    'create_deep_execution_system'
]
