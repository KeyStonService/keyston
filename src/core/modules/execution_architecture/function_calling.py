"""
Function Calling System (函數調用系統)
OpenAI-compatible function calling with tool routing

Reference: Function calling and tool execution in AI agents
"""

import asyncio
import json
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class FunctionCallStatus(Enum):
    """Status of a function call"""
    PENDING = "pending"
    VALIDATING = "validating"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"
    INVALID = "invalid"


@dataclass
class FunctionDefinition:
    """
    OpenAI-compatible function definition
    
    Reference: OpenAI function calling format
    """
    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=lambda: {
        "type": "object",
        "properties": {},
        "required": []
    })

    def to_openai_format(self) -> dict[str, Any]:
        """Convert to OpenAI function format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

    def validate_arguments(self, arguments: dict[str, Any]) -> list[str]:
        """Validate arguments against schema, return list of errors"""
        errors = []

        required = self.parameters.get("required", [])
        properties = self.parameters.get("properties", {})

        # Check required fields
        for field_name in required:
            if field_name not in arguments:
                errors.append(f"Missing required field: {field_name}")

        # Check types
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        for key, value in arguments.items():
            if key in properties:
                expected_type = properties[key].get("type")
                if expected_type and expected_type in type_map:
                    if not isinstance(value, type_map[expected_type]):
                        errors.append(f"Invalid type for {key}: expected {expected_type}")

        return errors


@dataclass
class FunctionCallResult:
    """Result of a function call"""
    function_name: str
    status: FunctionCallStatus
    arguments: dict[str, Any] = field(default_factory=dict)
    result: Any = None
    error: str | None = None
    validation_errors: list[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    call_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)

    def to_openai_response(self) -> dict[str, Any]:
        """Convert to OpenAI function call response format"""
        return {
            "tool_call_id": self.call_id,
            "role": "tool",
            "name": self.function_name,
            "content": json.dumps(self.result) if self.result else str(self.error)
        }


class FunctionCallHandler:
    """
    函數調用處理器
    Handles function call validation and execution
    """

    def __init__(self):
        self._functions: dict[str, FunctionDefinition] = {}
        self._handlers: dict[str, Callable] = {}
        self._call_history: list[FunctionCallResult] = []

    def register(
        self,
        function_def: FunctionDefinition,
        handler: Callable
    ) -> None:
        """Register a function with its handler"""
        self._functions[function_def.name] = function_def
        self._handlers[function_def.name] = handler

    def unregister(self, function_name: str) -> None:
        """Unregister a function"""
        if function_name in self._functions:
            del self._functions[function_name]
        if function_name in self._handlers:
            del self._handlers[function_name]

    def get_function(self, name: str) -> FunctionDefinition | None:
        """Get a function definition"""
        return self._functions.get(name)

    def list_functions(self) -> list[FunctionDefinition]:
        """List all registered functions"""
        return list(self._functions.values())

    def get_openai_tools(self) -> list[dict[str, Any]]:
        """Get all functions in OpenAI tools format"""
        return [f.to_openai_format() for f in self._functions.values()]

    async def handle_call(
        self,
        function_name: str,
        arguments: dict[str, Any]
    ) -> FunctionCallResult:
        """Handle a function call"""
        start_time = datetime.now()

        # Check if function exists
        if function_name not in self._functions:
            result = FunctionCallResult(
                function_name=function_name,
                status=FunctionCallStatus.INVALID,
                arguments=arguments,
                error=f"Function not found: {function_name}"
            )
            self._call_history.append(result)
            return result

        function_def = self._functions[function_name]

        # Validate arguments
        validation_errors = function_def.validate_arguments(arguments)
        if validation_errors:
            result = FunctionCallResult(
                function_name=function_name,
                status=FunctionCallStatus.INVALID,
                arguments=arguments,
                validation_errors=validation_errors,
                error=f"Validation failed: {'; '.join(validation_errors)}"
            )
            self._call_history.append(result)
            return result

        # Execute handler
        handler = self._handlers.get(function_name)
        if not handler:
            result = FunctionCallResult(
                function_name=function_name,
                status=FunctionCallStatus.FAILED,
                arguments=arguments,
                error=f"No handler for function: {function_name}"
            )
            self._call_history.append(result)
            return result

        try:
            if asyncio.iscoroutinefunction(handler):
                output = await handler(**arguments)
            else:
                output = handler(**arguments)

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            result = FunctionCallResult(
                function_name=function_name,
                status=FunctionCallStatus.SUCCESS,
                arguments=arguments,
                result=output,
                execution_time_ms=execution_time
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            result = FunctionCallResult(
                function_name=function_name,
                status=FunctionCallStatus.FAILED,
                arguments=arguments,
                error=str(e),
                execution_time_ms=execution_time
            )

        self._call_history.append(result)
        return result

    def parse_openai_tool_call(
        self,
        tool_call: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        """Parse an OpenAI tool call response"""
        function_name = tool_call.get("function", {}).get("name", "")
        arguments_str = tool_call.get("function", {}).get("arguments", "{}")

        try:
            arguments = json.loads(arguments_str)
        except json.JSONDecodeError:
            arguments = {}

        return function_name, arguments

    def get_history(self) -> list[FunctionCallResult]:
        """Get call history"""
        return self._call_history.copy()

    def clear_history(self) -> None:
        """Clear call history"""
        self._call_history.clear()


@dataclass
class RoutingRule:
    """A rule for routing tool calls"""
    name: str
    condition: Callable[[str, dict[str, Any]], bool]
    executor_id: str
    priority: int = 0


class ToolCallRouter:
    """
    工具調用路由器
    Routes tool calls to appropriate executors
    """

    def __init__(self):
        self._executors: dict[str, Any] = {}
        self._rules: list[RoutingRule] = []
        self._default_executor: str | None = None

    def register_executor(
        self,
        executor_id: str,
        executor: Any
    ) -> None:
        """Register an executor"""
        self._executors[executor_id] = executor

    def unregister_executor(self, executor_id: str) -> None:
        """Unregister an executor"""
        if executor_id in self._executors:
            del self._executors[executor_id]

    def add_rule(self, rule: RoutingRule) -> None:
        """Add a routing rule"""
        self._rules.append(rule)
        # Sort by priority (higher first)
        self._rules.sort(key=lambda r: r.priority, reverse=True)

    def remove_rule(self, rule_name: str) -> None:
        """Remove a routing rule"""
        self._rules = [r for r in self._rules if r.name != rule_name]

    def set_default_executor(self, executor_id: str) -> None:
        """Set the default executor"""
        self._default_executor = executor_id

    def route(
        self,
        tool_name: str,
        params: dict[str, Any]
    ) -> Any | None:
        """Route a tool call to the appropriate executor"""
        # Check rules in priority order
        for rule in self._rules:
            if rule.condition(tool_name, params):
                if rule.executor_id in self._executors:
                    return self._executors[rule.executor_id]

        # Use default executor
        if self._default_executor and self._default_executor in self._executors:
            return self._executors[self._default_executor]

        return None

    async def execute(
        self,
        tool_name: str,
        params: dict[str, Any]
    ) -> Any:
        """Route and execute a tool call"""
        executor = self.route(tool_name, params)

        if executor is None:
            raise ValueError(f"No executor found for tool: {tool_name}")

        # Execute based on executor type
        if hasattr(executor, 'execute'):
            if asyncio.iscoroutinefunction(executor.execute):
                return await executor.execute(tool_name, params)
            else:
                return executor.execute(tool_name, params)
        elif callable(executor):
            if asyncio.iscoroutinefunction(executor):
                return await executor(tool_name, params)
            else:
                return executor(tool_name, params)
        else:
            raise ValueError(f"Executor is not callable: {type(executor)}")

    def list_executors(self) -> list[str]:
        """List all executor IDs"""
        return list(self._executors.keys())

    def list_rules(self) -> list[RoutingRule]:
        """List all routing rules"""
        return self._rules.copy()


# Helper functions for creating common function definitions
def create_query_function(
    name: str = "query_database",
    description: str = "Execute a database query"
) -> FunctionDefinition:
    """Create a database query function definition"""
    return FunctionDefinition(
        name=name,
        description=description,
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The SQL query to execute"
                },
                "database": {
                    "type": "string",
                    "description": "The database to query"
                }
            },
            "required": ["query"]
        }
    )


def create_api_function(
    name: str = "call_api",
    description: str = "Make an HTTP API call"
) -> FunctionDefinition:
    """Create an API call function definition"""
    return FunctionDefinition(
        name=name,
        description=description,
        parameters={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to call"
                },
                "method": {
                    "type": "string",
                    "description": "HTTP method (GET, POST, etc.)"
                },
                "body": {
                    "type": "object",
                    "description": "Request body"
                }
            },
            "required": ["url", "method"]
        }
    )


def create_code_function(
    name: str = "execute_code",
    description: str = "Execute code in a sandbox"
) -> FunctionDefinition:
    """Create a code execution function definition"""
    return FunctionDefinition(
        name=name,
        description=description,
        parameters={
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The code to execute"
                },
                "language": {
                    "type": "string",
                    "description": "Programming language"
                }
            },
            "required": ["code", "language"]
        }
    )
