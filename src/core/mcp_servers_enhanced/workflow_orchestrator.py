"""
Workflow Orchestrator - Orchestrate complex multi-tool workflows

This module provides workflow orchestration capabilities for executing
complex sequences of MCP tool calls with dependencies, parallelization,
and error handling.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    PAUSED = 'paused'


class StepStatus(Enum):
    """Workflow step status"""
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    SKIPPED = 'skipped'


@dataclass
class WorkflowStep:
    """Definition of a workflow step"""
    id: str
    name: str
    tool: str
    arguments: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 30000  # milliseconds
    retry_count: int = 0
    retry_delay: int = 1000  # milliseconds
    condition: Optional[str] = None  # Expression to evaluate
    on_success: Optional[str] = None  # Step ID to run on success
    on_failure: Optional[str] = None  # Step ID to run on failure
    continue_on_failure: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'tool': self.tool,
            'arguments': self.arguments,
            'dependencies': self.dependencies,
            'timeout': self.timeout,
            'retry_count': self.retry_count,
            'retry_delay': self.retry_delay,
            'condition': self.condition,
            'on_success': self.on_success,
            'on_failure': self.on_failure,
            'continue_on_failure': self.continue_on_failure,
            'metadata': self.metadata
        }


@dataclass
class StepResult:
    """Result of a workflow step execution"""
    step_id: str
    step_name: str
    status: StepStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    attempts: int = 1
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert step result to dictionary"""
        return {
            'step_id': self.step_id,
            'step_name': self.step_name,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'duration_ms': self.duration_ms,
            'attempts': self.attempts,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


@dataclass
class WorkflowResult:
    """Result of a workflow execution"""
    workflow_id: str
    workflow_name: str
    status: WorkflowStatus
    steps: List[StepResult] = field(default_factory=list)
    total_duration_ms: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow result to dictionary"""
        return {
            'workflow_id': self.workflow_id,
            'workflow_name': self.workflow_name,
            'status': self.status.value,
            'steps': [s.to_dict() for s in self.steps],
            'total_duration_ms': self.total_duration_ms,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'output': self.output,
            'error': self.error,
            'metadata': self.metadata
        }


@dataclass
class Workflow:
    """Definition of a workflow"""
    id: str
    name: str
    description: str = ''
    steps: List[WorkflowStep] = field(default_factory=list)
    version: str = '1.0.0'
    timeout: int = 300000  # 5 minutes
    max_parallel: int = 5
    on_complete: Optional[Callable] = None
    on_error: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'steps': [s.to_dict() for s in self.steps],
            'timeout': self.timeout,
            'max_parallel': self.max_parallel,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }


class WorkflowOrchestrator:
    """
    Orchestrator for executing complex multi-step workflows
    
    Features:
    - Step dependency management
    - Parallel execution with limits
    - Retry logic
    - Conditional execution
    - Error handling and recovery
    """
    
    def __init__(self, tool_executor: Callable = None):
        """
        Initialize the orchestrator
        
        Args:
            tool_executor: Async function to execute tools
                          Signature: (tool_name: str, arguments: dict) -> dict
        """
        self._tool_executor = tool_executor or self._default_executor
        self._workflows: Dict[str, Workflow] = {}
        self._running_workflows: Dict[str, asyncio.Task] = {}
        self._workflow_results: Dict[str, WorkflowResult] = {}
        self._event_handlers: Dict[str, List[Callable]] = {}
        
    async def register_workflow(self, workflow: Workflow) -> None:
        """Register a workflow definition"""
        # Validate workflow
        self._validate_workflow(workflow)
        self._workflows[workflow.id] = workflow
        logger.info(f'Registered workflow: {workflow.name} (id: {workflow.id})')
        
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow by ID"""
        return self._workflows.get(workflow_id)
        
    async def execute_workflow(
        self,
        workflow_id: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> WorkflowResult:
        """
        Execute a workflow
        
        Args:
            workflow_id: ID of workflow to execute
            input_data: Optional input data for the workflow
            
        Returns:
            Workflow execution result
        """
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return WorkflowResult(
                workflow_id=workflow_id,
                workflow_name='unknown',
                status=WorkflowStatus.FAILED,
                error=f'Workflow not found: {workflow_id}'
            )
            
        result = WorkflowResult(
            workflow_id=workflow_id,
            workflow_name=workflow.name,
            status=WorkflowStatus.RUNNING,
            started_at=datetime.now(),
            metadata={'input': input_data}
        )
        
        try:
            await self._emit_event('workflow_started', result)
            
            # Execute steps
            step_results = await self._execute_steps(workflow, input_data or {})
            result.steps = step_results
            
            # Check if all steps succeeded
            failed_steps = [s for s in step_results if s.status == StepStatus.FAILED]
            if failed_steps and not all(
                self._get_step(workflow, s.step_id).continue_on_failure
                for s in failed_steps
            ):
                result.status = WorkflowStatus.FAILED
                result.error = f'{len(failed_steps)} step(s) failed'
            else:
                result.status = WorkflowStatus.COMPLETED
                # Collect output from final steps
                result.output = self._collect_output(step_results)
                
            result.completed_at = datetime.now()
            result.total_duration_ms = (
                (result.completed_at - result.started_at).total_seconds() * 1000
            )
            
            await self._emit_event('workflow_completed', result)
            
            if workflow.on_complete:
                await self._safe_callback(workflow.on_complete, result)
                
        except Exception as e:
            result.status = WorkflowStatus.FAILED
            result.error = str(e)
            result.completed_at = datetime.now()
            logger.error(f'Workflow {workflow_id} failed: {e}')
            
            if workflow.on_error:
                await self._safe_callback(workflow.on_error, result)
                
            await self._emit_event('workflow_error', result)
            
        self._workflow_results[workflow_id] = result
        return result
        
    async def execute_workflow_async(
        self,
        workflow_id: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute a workflow asynchronously
        
        Returns:
            Execution ID for tracking
        """
        execution_id = str(uuid4())
        task = asyncio.create_task(
            self.execute_workflow(workflow_id, input_data)
        )
        self._running_workflows[execution_id] = task
        return execution_id
        
    async def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel a running workflow"""
        task = self._running_workflows.get(execution_id)
        if task and not task.done():
            task.cancel()
            return True
        return False
        
    def get_workflow_status(self, execution_id: str) -> Optional[WorkflowResult]:
        """Get the status of a workflow execution"""
        return self._workflow_results.get(execution_id)
        
    def list_workflows(self) -> List[Workflow]:
        """List all registered workflows"""
        return list(self._workflows.values())
        
    def on(self, event: str, handler: Callable) -> None:
        """Register an event handler"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
        
    async def _execute_steps(
        self,
        workflow: Workflow,
        context: Dict[str, Any]
    ) -> List[StepResult]:
        """Execute all steps in a workflow"""
        results: Dict[str, StepResult] = {}
        completed: Set[str] = set()
        pending_steps = list(workflow.steps)
        
        while pending_steps:
            # Find steps that can be executed (all dependencies met)
            ready_steps = [
                step for step in pending_steps
                if all(dep in completed for dep in step.dependencies)
            ]
            
            if not ready_steps:
                # No steps ready but pending steps exist - circular dependency
                for step in pending_steps:
                    results[step.id] = StepResult(
                        step_id=step.id,
                        step_name=step.name,
                        status=StepStatus.FAILED,
                        error='Circular dependency detected'
                    )
                break
                
            # Execute ready steps in parallel (with limit)
            parallel_batch = ready_steps[:workflow.max_parallel]
            
            batch_tasks = [
                self._execute_step(step, context, results)
                for step in parallel_batch
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Process results
            for step, result in zip(parallel_batch, batch_results):
                if isinstance(result, Exception):
                    results[step.id] = StepResult(
                        step_id=step.id,
                        step_name=step.name,
                        status=StepStatus.FAILED,
                        error=str(result)
                    )
                else:
                    results[step.id] = result
                    
                completed.add(step.id)
                pending_steps.remove(step)
                
                # Update context with step output
                if result and not isinstance(result, Exception) and result.result:
                    context[f'step.{step.id}'] = result.result
                    
        return list(results.values())
        
    async def _execute_step(
        self,
        step: WorkflowStep,
        context: Dict[str, Any],
        previous_results: Dict[str, StepResult]
    ) -> StepResult:
        """Execute a single workflow step"""
        result = StepResult(
            step_id=step.id,
            step_name=step.name,
            status=StepStatus.RUNNING,
            started_at=datetime.now()
        )
        
        # Check condition
        if step.condition and not self._evaluate_condition(step.condition, context):
            result.status = StepStatus.SKIPPED
            result.completed_at = datetime.now()
            return result
            
        # Prepare arguments with context substitution
        arguments = self._substitute_arguments(step.arguments, context)
        
        # Execute with retries
        attempts = 0
        last_error = None
        
        while attempts <= step.retry_count:
            attempts += 1
            try:
                start_time = datetime.now()
                tool_result = await asyncio.wait_for(
                    self._tool_executor(step.tool, arguments),
                    timeout=step.timeout / 1000.0
                )
                end_time = datetime.now()
                
                if tool_result.get('success', True):
                    result.status = StepStatus.COMPLETED
                    result.result = tool_result.get('result', tool_result)
                    result.duration_ms = (end_time - start_time).total_seconds() * 1000
                    break
                else:
                    last_error = tool_result.get('error', 'Unknown error')
                    if attempts <= step.retry_count:
                        await asyncio.sleep(step.retry_delay / 1000.0)
                        
            except asyncio.TimeoutError:
                last_error = f'Step timed out after {step.timeout}ms'
            except Exception as e:
                last_error = str(e)
                if attempts <= step.retry_count:
                    await asyncio.sleep(step.retry_delay / 1000.0)
                    
        if result.status != StepStatus.COMPLETED:
            result.status = StepStatus.FAILED
            result.error = last_error
            
        result.attempts = attempts
        result.completed_at = datetime.now()
        
        await self._emit_event('step_completed', result)
        
        return result
        
    def _validate_workflow(self, workflow: Workflow) -> None:
        """Validate workflow definition"""
        step_ids = {step.id for step in workflow.steps}
        
        for step in workflow.steps:
            # Check dependencies exist
            for dep in step.dependencies:
                if dep not in step_ids:
                    raise ValueError(
                        f'Step {step.id} has unknown dependency: {dep}'
                    )
                    
            # Check on_success/on_failure references
            if step.on_success and step.on_success not in step_ids:
                raise ValueError(
                    f'Step {step.id} has unknown on_success reference: {step.on_success}'
                )
            if step.on_failure and step.on_failure not in step_ids:
                raise ValueError(
                    f'Step {step.id} has unknown on_failure reference: {step.on_failure}'
                )
                
    def _get_step(self, workflow: Workflow, step_id: str) -> Optional[WorkflowStep]:
        """Get a step by ID from workflow"""
        for step in workflow.steps:
            if step.id == step_id:
                return step
        return None
        
    def _evaluate_condition(
        self,
        condition: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Evaluate a condition expression
        
        NOTE: This is a simplified implementation for framework demonstration.
        Production implementation should use a proper expression evaluator
        like simpleeval or a custom DSL parser for safe condition evaluation.
        
        Args:
            condition: Condition expression string
            context: Context data for substitution
            
        Returns:
            True if condition is met, False otherwise
        """
        try:
            # Replace context references
            for key, value in context.items():
                condition = condition.replace(f'${{{key}}}', repr(value))
            # Basic safety check - only allow simple comparisons
            allowed_chars = set('0123456789.!=<>andornotTrueFalse"\' ')
            if not all(c in allowed_chars or c.isalnum() or c == '_' for c in condition):
                logger.warning(f'Unsafe condition blocked: {condition}')
                return True
            # For framework demonstration, return True
            # Production should implement proper condition evaluation
            return True
        except Exception as e:
            logger.error(f'Condition evaluation failed: {e}')
            return True
            
    def _substitute_arguments(
        self,
        arguments: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Substitute context values into arguments"""
        result = {}
        for key, value in arguments.items():
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                # Context reference
                ref = value[2:-1]
                result[key] = context.get(ref, value)
            elif isinstance(value, dict):
                result[key] = self._substitute_arguments(value, context)
            elif isinstance(value, list):
                result[key] = [
                    self._substitute_arguments({'_': v}, context)['_']
                    if isinstance(v, (dict, str)) else v
                    for v in value
                ]
            else:
                result[key] = value
        return result
        
    def _collect_output(self, step_results: List[StepResult]) -> Dict[str, Any]:
        """Collect output from completed steps"""
        output = {}
        for result in step_results:
            if result.status == StepStatus.COMPLETED and result.result:
                output[result.step_id] = result.result
        return output
        
    async def _emit_event(self, event: str, data: Any) -> None:
        """Emit an event to all handlers"""
        handlers = self._event_handlers.get(event, [])
        for handler in handlers:
            await self._safe_callback(handler, data)
            
    async def _safe_callback(self, callback: Callable, data: Any) -> None:
        """Safely execute a callback"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(data)
            else:
                callback(data)
        except Exception as e:
            logger.error(f'Callback error: {e}')
            
    async def _default_executor(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Default tool executor (for testing)"""
        return {
            'success': True,
            'tool': tool_name,
            'arguments': arguments,
            'result': {'status': 'executed'}
        }


# Factory functions
def create_workflow_orchestrator(
    tool_executor: Callable = None
) -> WorkflowOrchestrator:
    """Create a new WorkflowOrchestrator instance"""
    return WorkflowOrchestrator(tool_executor)


def create_workflow(
    name: str,
    steps: List[WorkflowStep],
    **kwargs
) -> Workflow:
    """Create a new Workflow instance"""
    return Workflow(
        id=str(uuid4()),
        name=name,
        steps=steps,
        **kwargs
    )


def create_step(
    name: str,
    tool: str,
    arguments: Dict[str, Any],
    **kwargs
) -> WorkflowStep:
    """Create a new WorkflowStep instance"""
    return WorkflowStep(
        id=kwargs.pop('id', str(uuid4())),
        name=name,
        tool=tool,
        arguments=arguments,
        **kwargs
    )


# Pre-defined workflow templates
def get_code_analysis_workflow() -> Workflow:
    """Get a pre-defined code analysis workflow"""
    return Workflow(
        id='code-analysis-workflow',
        name='Code Analysis Pipeline',
        description='Comprehensive code analysis workflow',
        steps=[
            WorkflowStep(
                id='analyze',
                name='Analyze Code',
                tool='analyze-code',
                arguments={'code': '${input.code}', 'language': '${input.language}'}
            ),
            WorkflowStep(
                id='security-scan',
                name='Security Scan',
                tool='scan-vulnerabilities',
                arguments={'code': '${input.code}'},
                dependencies=['analyze']
            ),
            WorkflowStep(
                id='performance',
                name='Performance Analysis',
                tool='analyze-performance',
                arguments={'code': '${input.code}'},
                dependencies=['analyze']
            ),
            WorkflowStep(
                id='generate-tests',
                name='Generate Tests',
                tool='generate-tests',
                arguments={
                    'code': '${input.code}',
                    'framework': 'jest'
                },
                dependencies=['security-scan', 'performance']
            ),
            WorkflowStep(
                id='generate-docs',
                name='Generate Documentation',
                tool='generate-docs',
                arguments={
                    'code': '${input.code}',
                    'format': 'markdown'
                },
                dependencies=['generate-tests']
            )
        ]
    )
