"""
═══════════════════════════════════════════════════════════
    Function Calling System (函數調用系統)
    OpenAI-compatible function calling with tool routing
═══════════════════════════════════════════════════════════

This module provides a comprehensive function calling infrastructure for AI agents,
enabling structured tool execution with validation, routing, and history tracking.
It follows the OpenAI function calling specification while providing additional
enterprise-grade features like routing rules and execution tracking.

本模組提供 AI 代理的完整函數調用基礎設施，支援結構化工具執行、驗證、路由和歷史追蹤。
遵循 OpenAI 函數調用規範，同時提供路由規則和執行追蹤等企業級功能。

Core Capabilities (核心功能):
---------------------------------
1. **Function Definition & Validation** - Define functions with JSON Schema validation
2. **OpenAI Compatibility** - Full support for OpenAI function calling format
3. **Async/Sync Execution** - Handle both synchronous and asynchronous handlers
4. **Tool Call Routing** - Route calls to different executors based on rules
5. **Execution History** - Track all function calls with status and timing
6. **Error Handling** - Comprehensive validation and execution error handling

Architecture Overview (架構概覽):
---------------------------------
The system consists of four main components:

1. **FunctionDefinition**: Defines available functions with JSON Schema parameters
   - Validates input arguments against schema
   - Converts to OpenAI-compatible format

2. **FunctionCallResult**: Tracks execution results and metadata
   - Captures success/failure status
   - Records execution time and errors
   - Stores call history for auditing

3. **FunctionCallHandler**: Manages function registration and execution
   - Registers functions with their handlers
   - Validates arguments before execution
   - Executes handlers (sync or async)
   - Maintains execution history

4. **ToolCallRouter**: Routes tool calls to appropriate executors
   - Defines routing rules with conditions
   - Supports multiple executors
   - Priority-based rule matching

Design Principles (設計原則):
------------------------------
- **Type Safety**: Full type hints and runtime validation
- **OpenAI Compatibility**: Adheres to OpenAI function calling specification
- **Flexibility**: Support for sync/async, multiple executors, custom routing
- **Observability**: Complete execution history and detailed error messages
- **Extensibility**: Easy to add new functions, executors, and routing rules

Usage Example (使用範例):
--------------------------

Basic Function Registration and Execution:
```python
from core.execution_architecture.function_calling import (
    FunctionDefinition, FunctionCallHandler
)

# Initialize handler
handler = FunctionCallHandler()

# Define a function
def calculate_sum(a: int, b: int) -> int:
    return a + b

function_def = FunctionDefinition(
    name="calculate_sum",
    description="Add two numbers together",
    parameters={
        "type": "object",
        "properties": {
            "a": {"type": "integer", "description": "First number"},
            "b": {"type": "integer", "description": "Second number"}
        },
        "required": ["a", "b"]
    }
)

# Register function
handler.register(function_def, calculate_sum)

# Execute function call
result = await handler.handle_call("calculate_sum", {"a": 5, "b": 3})
print(f"Result: {result.result}")  # Output: Result: 8
print(f"Status: {result.status}")  # Output: Status: FunctionCallStatus.SUCCESS
```

Tool Call Routing:
```python
from core.execution_architecture.function_calling import (
    ToolCallRouter, RoutingRule
)

# Initialize router
router = ToolCallRouter()

# Register executors
router.register_executor("database", database_executor)
router.register_executor("api", api_executor)

# Add routing rules
router.add_rule(RoutingRule(
    name="route_db_calls",
    condition=lambda name, params: name.startswith("query_"),
    executor_id="database",
    priority=10
))

router.add_rule(RoutingRule(
    name="route_api_calls",
    condition=lambda name, params: "url" in params,
    executor_id="api",
    priority=5
))

# Route and execute
result = await router.execute("query_users", {"table": "users"})
```

OpenAI Integration:
```python
# Get all functions in OpenAI format
tools = handler.get_openai_tools()

# Use with OpenAI API
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Calculate 5 + 3"}],
    tools=tools,
    tool_choice="auto"
)

# Parse and execute tool call
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    func_name, args = handler.parse_openai_tool_call(tool_call)
    result = await handler.handle_call(func_name, args)
```

Integration Points (整合點):
----------------------------
- **Execution Engine** (core/execution_engine/execution_engine.py): Uses this for action execution
- **MCP Integration** (core/execution_architecture/mcp/): Model Context Protocol tool calls
- **LangChain Integration**: Compatible with LangChain tool calling
- **Island AI Runtime**: Provides tool execution for AI agents

Error Handling (錯誤處理):
--------------------------
The system provides detailed error information through FunctionCallResult:

1. **INVALID**: Function not found or validation failed
   - Check validation_errors for specific issues

2. **FAILED**: Execution raised an exception
   - Check error field for exception message

3. **SUCCESS**: Execution completed successfully
   - Result available in result field

References (參考文獻):
-----------------------
- OpenAI Function Calling: https://platform.openai.com/docs/guides/function-calling
- JSON Schema: https://json-schema.org/
- Python Type Hints: https://docs.python.org/3/library/typing.html

Author: SynergyMesh Platform Team
Version: 1.0.0
Last Updated: 2025-12-12
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime
import uuid
import json
import asyncio


class FunctionCallStatus(Enum):
    """
    Status tracking for function call execution lifecycle.

    This enum represents all possible states a function call can be in,
    from initial submission through validation to final execution.

    States (狀態):
    -------------
    - PENDING: Call received but not yet processed
    - VALIDATING: Arguments are being validated against schema
    - EXECUTING: Handler is currently executing the function
    - SUCCESS: Execution completed successfully with a result
    - FAILED: Execution raised an exception or error
    - INVALID: Call validation failed (missing required params, wrong types, etc.)

    State Transitions (狀態轉換):
    ---------------------------
    PENDING → VALIDATING → EXECUTING → SUCCESS
                         ↘ INVALID
                                     ↘ FAILED

    Example:
        >>> result = await handler.handle_call("my_function", {"arg": "value"})
        >>> if result.status == FunctionCallStatus.SUCCESS:
        ...     print(f"Result: {result.result}")
        >>> elif result.status == FunctionCallStatus.INVALID:
        ...     print(f"Validation errors: {result.validation_errors}")
        >>> elif result.status == FunctionCallStatus.FAILED:
        ...     print(f"Execution error: {result.error}")
    """
    PENDING = "pending"
    VALIDATING = "validating"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"
    INVALID = "invalid"


@dataclass
class FunctionDefinition:
    """
    OpenAI-compatible function definition with JSON Schema validation.

    Defines a callable function with its name, description, and parameter schema.
    Parameters follow JSON Schema specification for validation. This class provides
    conversion to OpenAI format and runtime argument validation.

    符合 OpenAI 格式的函數定義，使用 JSON Schema 進行參數驗證。

    Attributes:
        name (str): Unique function identifier. Must be valid Python identifier.
                    函數的唯一標識符
        description (str): Human-readable function description. Used by AI to understand
                          when to call this function.
                          函數的可讀描述，供 AI 理解何時調用
        parameters (Dict[str, Any]): JSON Schema object defining function parameters.
                                     Follows JSON Schema Draft 7 specification.
                                     JSON Schema 參數定義

    Parameter Schema Format:
        The parameters dictionary should follow this structure:
        ```python
        {
            "type": "object",
            "properties": {
                "param_name": {
                    "type": "string|number|integer|boolean|array|object",
                    "description": "Parameter description",
                    # Optional constraints:
                    "enum": ["option1", "option2"],  # For enums
                    "minimum": 0,  # For numbers
                    "maxLength": 100,  # For strings
                    # etc.
                }
            },
            "required": ["param1", "param2"]  # List of required parameters
        }
        ```

    Example:
        >>> # Define a simple calculation function
        >>> calc_func = FunctionDefinition(
        ...     name="calculate_area",
        ...     description="Calculate area of a rectangle",
        ...     parameters={
        ...         "type": "object",
        ...         "properties": {
        ...             "width": {
        ...                 "type": "number",
        ...                 "description": "Width in meters",
        ...                 "minimum": 0
        ...             },
        ...             "height": {
        ...                 "type": "number",
        ...                 "description": "Height in meters",
        ...                 "minimum": 0
        ...             }
        ...         },
        ...         "required": ["width", "height"]
        ...     }
        ... )
        >>>
        >>> # Convert to OpenAI format
        >>> openai_tool = calc_func.to_openai_format()
        >>>
        >>> # Validate arguments
        >>> errors = calc_func.validate_arguments({"width": 10, "height": 5})
        >>> print(f"Validation errors: {errors}")  # Output: []

    See Also:
        - FunctionCallHandler: For registering and executing functions
        - FunctionCallResult: For execution results
        - JSON Schema: https://json-schema.org/

    Reference:
        OpenAI Function Calling: https://platform.openai.com/docs/guides/function-calling
    """
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=lambda: {
        "type": "object",
        "properties": {},
        "required": []
    })
    
    def to_openai_format(self) -> Dict[str, Any]:
        """
        Convert function definition to OpenAI tools format.

        Transforms the function definition into the format expected by OpenAI's
        function calling API. This format is used when passing tools to the
        ChatCompletion API.

        將函數定義轉換為 OpenAI 工具格式。

        Returns:
            Dict[str, Any]: OpenAI-compatible tool definition with structure:
                {
                    "type": "function",
                    "function": {
                        "name": str,
                        "description": str,
                        "parameters": Dict[str, Any]
                    }
                }

        Example:
            >>> func_def = FunctionDefinition(
            ...     name="get_weather",
            ...     description="Get current weather",
            ...     parameters={"type": "object", "properties": {
            ...         "location": {"type": "string"}
            ...     }}
            ... )
            >>> openai_format = func_def.to_openai_format()
            >>> print(openai_format)
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get current weather",
                    "parameters": {...}
                }
            }

        See Also:
            - FunctionCallHandler.get_openai_tools(): Get all registered functions
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
    
    def validate_arguments(self, arguments: Dict[str, Any]) -> List[str]:
        """
        Validate function call arguments against the JSON Schema.

        Performs runtime validation of arguments to ensure they match the
        parameter schema. Checks for required fields and type correctness.
        Returns a list of validation error messages (empty if valid).

        根據 JSON Schema 驗證函數調用參數。

        Args:
            arguments (Dict[str, Any]): The arguments to validate. Keys should
                                       match parameter names defined in schema.

        Returns:
            List[str]: List of validation error messages. Empty list means
                      all validations passed. Each error describes what
                      validation failed.

        Validation Checks:
            1. Required Fields: All fields in "required" array must be present
            2. Type Checking: Values must match their declared JSON Schema type
            3. Future: Additional constraints (min/max, enum, patterns, etc.)

        Type Mapping:
            - "string" → str
            - "number" → int or float
            - "integer" → int
            - "boolean" → bool
            - "array" → list
            - "object" → dict

        Example:
            >>> func_def = FunctionDefinition(
            ...     name="create_user",
            ...     description="Create a new user",
            ...     parameters={
            ...         "type": "object",
            ...         "properties": {
            ...             "name": {"type": "string"},
            ...             "age": {"type": "integer"}
            ...         },
            ...         "required": ["name"]
            ...     }
            ... )
            >>>
            >>> # Valid arguments
            >>> errors = func_def.validate_arguments({"name": "Alice", "age": 30})
            >>> print(errors)  # Output: []
            >>>
            >>> # Missing required field
            >>> errors = func_def.validate_arguments({"age": 30})
            >>> print(errors)  # Output: ['Missing required field: name']
            >>>
            >>> # Wrong type
            >>> errors = func_def.validate_arguments({"name": "Alice", "age": "30"})
            >>> print(errors)  # Output: ['Invalid type for age: expected integer']

        Note:
            This is a basic validation implementation. For comprehensive JSON Schema
            validation, consider using libraries like jsonschema or pydantic.

        See Also:
            - FunctionCallHandler.handle_call(): Uses this for validation
            - FunctionCallResult.validation_errors: Stores validation errors
        """
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
    """
    Complete execution result for a function call with metadata and telemetry.

    Captures all information about a function call execution including status,
    arguments, results, errors, timing, and unique identifier. Used for
    execution tracking, auditing, and debugging.

    函數調用的完整執行結果，包含元數據和遙測數據。

    Attributes:
        function_name (str): Name of the function that was called.
                            被調用的函數名稱
        status (FunctionCallStatus): Current execution status (SUCCESS, FAILED, INVALID, etc.)
                                    執行狀態
        arguments (Dict[str, Any]): Arguments passed to the function.
                                   傳遞給函數的參數
        result (Any): Function return value. Only populated if status is SUCCESS.
                     函數返回值（僅在成功時有效）
        error (Optional[str]): Error message if execution or validation failed.
                              錯誤訊息（如果執行或驗證失敗）
        validation_errors (List[str]): List of validation error messages.
                                      Empty if validation passed.
                                      驗證錯誤列表
        execution_time_ms (float): Execution duration in milliseconds.
                                  執行時間（毫秒）
        call_id (str): Unique identifier for this function call (UUID).
                      函數調用的唯一標識符
        timestamp (datetime): When the function call was made.
                             函數調用的時間戳

    Status-Result Matrix:
        - SUCCESS: result is populated, error is None
        - FAILED: error is populated with exception message, result is None
        - INVALID: validation_errors is populated, both result and error may be set
        - PENDING/VALIDATING/EXECUTING: Intermediate states (rarely seen in results)

    Example:
        >>> handler = FunctionCallHandler()
        >>> # ... register functions ...
        >>>
        >>> # Successful execution
        >>> result = await handler.handle_call("add", {"a": 5, "b": 3})
        >>> print(f"Status: {result.status}")  # SUCCESS
        >>> print(f"Result: {result.result}")  # 8
        >>> print(f"Time: {result.execution_time_ms}ms")  # e.g., 0.5ms
        >>>
        >>> # Failed execution
        >>> result = await handler.handle_call("divide", {"a": 5, "b": 0})
        >>> print(f"Status: {result.status}")  # FAILED
        >>> print(f"Error: {result.error}")  # "division by zero"
        >>>
        >>> # Invalid arguments
        >>> result = await handler.handle_call("add", {"a": 5})  # missing 'b'
        >>> print(f"Status: {result.status}")  # INVALID
        >>> print(f"Errors: {result.validation_errors}")  # ['Missing required field: b']

    See Also:
        - FunctionCallStatus: Status enum values
        - FunctionCallHandler: Creates FunctionCallResult instances
        - FunctionCallHandler.get_history(): Retrieve all call results
    """
    function_name: str
    status: FunctionCallStatus
    arguments: Dict[str, Any] = field(default_factory=dict)
    result: Any = None
    error: Optional[str] = None
    validation_errors: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    call_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_openai_response(self) -> Dict[str, Any]:
        """
        Convert execution result to OpenAI function call response format.

        Transforms the result into the message format expected by OpenAI's
        ChatCompletion API when returning function call results to the model.

        將執行結果轉換為 OpenAI 函數調用響應格式。

        Returns:
            Dict[str, Any]: OpenAI-compatible message with structure:
                {
                    "tool_call_id": str,  # Unique call identifier
                    "role": "tool",       # Message role
                    "name": str,          # Function name
                    "content": str        # JSON-encoded result or error
                }

        Response Content:
            - If result exists: JSON-encoded result object
            - If error exists: String error message
            - Content is always a string for OpenAI compatibility

        Example:
            >>> result = FunctionCallResult(
            ...     function_name="get_weather",
            ...     status=FunctionCallStatus.SUCCESS,
            ...     result={"temperature": 72, "condition": "sunny"},
            ...     call_id="abc-123"
            ... )
            >>> response = result.to_openai_response()
            >>> print(response)
            {
                "tool_call_id": "abc-123",
                "role": "tool",
                "name": "get_weather",
                "content": '{"temperature": 72, "condition": "sunny"}'
            }

        Usage Pattern:
            ```python
            # Execute function call
            result = await handler.handle_call("my_func", args)

            # Convert to OpenAI response
            response_message = result.to_openai_response()

            # Add to conversation
            messages.append(response_message)

            # Continue chat completion
            next_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages
            )
            ```

        See Also:
            - FunctionCallHandler.parse_openai_tool_call(): Parse OpenAI tool calls
            - OpenAI Function Calling Docs: Response format specification
        """
        return {
            "tool_call_id": self.call_id,
            "role": "tool",
            "name": self.function_name,
            "content": json.dumps(self.result) if self.result else str(self.error)
        }


class FunctionCallHandler:
    """
    Central registry and executor for AI function calls.

    Manages the complete lifecycle of function calls including registration,
    validation, execution, and history tracking. Supports both synchronous
    and asynchronous handlers with automatic detection.

    函數調用處理器 - 管理 AI 函數調用的完整生命週期。

    This handler provides:
    - **Function Registry**: Register/unregister functions with handlers
    - **Validation**: Automatic argument validation against JSON Schema
    - **Execution**: Safe execution of sync/async handlers
    - **History**: Complete audit trail of all function calls
    - **OpenAI Integration**: Convert to/from OpenAI format

    Responsibilities (職責):
        1. Maintain registry of available functions
        2. Map function names to executable handlers
        3. Validate arguments before execution
        4. Execute handlers safely with error handling
        5. Track execution history for auditing
        6. Provide OpenAI-compatible interfaces

    Attributes:
        _functions (Dict[str, FunctionDefinition]): Registry of function definitions
        _handlers (Dict[str, Callable]): Registry of function handlers (sync or async)
        _call_history (List[FunctionCallResult]): Complete execution history

    Thread Safety:
        This class is NOT thread-safe. Use separate instances per thread or
        add external synchronization for concurrent access.

    Example - Basic Usage:
        >>> handler = FunctionCallHandler()
        >>>
        >>> # Define and register a function
        >>> def greet(name: str, formal: bool = False) -> str:
        ...     prefix = "Good day" if formal else "Hello"
        ...     return f"{prefix}, {name}!"
        >>>
        >>> func_def = FunctionDefinition(
        ...     name="greet",
        ...     description="Greet a person by name",
        ...     parameters={
        ...         "type": "object",
        ...         "properties": {
        ...             "name": {"type": "string", "description": "Person's name"},
        ...             "formal": {"type": "boolean", "description": "Use formal greeting"}
        ...         },
        ...         "required": ["name"]
        ...     }
        ... )
        >>>
        >>> handler.register(func_def, greet)
        >>>
        >>> # Execute function call
        >>> result = await handler.handle_call("greet", {"name": "Alice", "formal": True})
        >>> print(result.result)  # "Good day, Alice!"

    Example - Async Handler:
        >>> async def fetch_data(url: str) -> dict:
        ...     async with httpx.AsyncClient() as client:
        ...         response = await client.get(url)
        ...         return response.json()
        >>>
        >>> func_def = FunctionDefinition(
        ...     name="fetch_data",
        ...     description="Fetch data from URL",
        ...     parameters={
        ...         "type": "object",
        ...         "properties": {
        ...             "url": {"type": "string"}
        ...         },
        ...         "required": ["url"]
        ...     }
        ... )
        >>>
        >>> handler.register(func_def, fetch_data)
        >>> result = await handler.handle_call("fetch_data", {"url": "https://api.example.com"})

    Example - OpenAI Integration:
        >>> # Get all functions in OpenAI format
        >>> tools = handler.get_openai_tools()
        >>>
        >>> # Use with OpenAI API
        >>> response = openai.ChatCompletion.create(
        ...     model="gpt-4",
        ...     messages=[{"role": "user", "content": "Greet Alice formally"}],
        ...     tools=tools,
        ...     tool_choice="auto"
        ... )
        >>>
        >>> # Parse and execute tool call from OpenAI response
        >>> if response.choices[0].message.tool_calls:
        ...     for tool_call in response.choices[0].message.tool_calls:
        ...         func_name, args = handler.parse_openai_tool_call(tool_call)
        ...         result = await handler.handle_call(func_name, args)
        ...         # Add result back to conversation
        ...         messages.append(result.to_openai_response())

    See Also:
        - FunctionDefinition: Define functions with schemas
        - FunctionCallResult: Execution results
        - ToolCallRouter: Route calls to different handlers
    """

    def __init__(self):
        """
        Initialize an empty function call handler.

        Creates empty registries for functions and handlers, and initializes
        an empty call history list.

        初始化函數調用處理器。
        """
        self._functions: Dict[str, FunctionDefinition] = {}
        self._handlers: Dict[str, Callable] = {}
        self._call_history: List[FunctionCallResult] = []
    
    def register(
        self,
        function_def: FunctionDefinition,
        handler: Callable
    ) -> None:
        """
        Register a function with its executable handler.

        Adds a function to the registry, making it available for execution.
        The handler can be either synchronous or asynchronous - the system
        automatically detects and handles both.

        註冊函數及其處理器。

        Args:
            function_def (FunctionDefinition): The function definition with
                                              name, description, and parameters
            handler (Callable): The executable function (sync or async).
                               Must accept **kwargs matching the parameter schema.

        Raises:
            None: Silently overwrites if function name already registered

        Handler Requirements:
            - Function signature must accept parameters defined in schema
            - Can be sync (def) or async (async def)
            - Should return a value (returned in FunctionCallResult.result)
            - Should raise exceptions for errors (captured in FunctionCallResult.error)

        Example:
            >>> handler = FunctionCallHandler()
            >>>
            >>> # Register synchronous function
            >>> def add(a: int, b: int) -> int:
            ...     return a + b
            >>>
            >>> add_def = FunctionDefinition(
            ...     name="add",
            ...     description="Add two numbers",
            ...     parameters={
            ...         "type": "object",
            ...         "properties": {
            ...             "a": {"type": "integer"},
            ...             "b": {"type": "integer"}
            ...         },
            ...         "required": ["a", "b"]
            ...     }
            ... )
            >>> handler.register(add_def, add)
            >>>
            >>> # Register async function
            >>> async def fetch_url(url: str) -> str:
            ...     # ... async implementation ...
            ...     return content
            >>>
            >>> fetch_def = FunctionDefinition(name="fetch_url", ...)
            >>> handler.register(fetch_def, fetch_url)

        Note:
            If a function with the same name exists, it will be replaced.
            No warning is issued for overwrites.

        See Also:
            - unregister(): Remove a registered function
            - list_functions(): View all registered functions
        """
        self._functions[function_def.name] = function_def
        self._handlers[function_def.name] = handler
    
    def unregister(self, function_name: str) -> None:
        """Unregister a function"""
        if function_name in self._functions:
            del self._functions[function_name]
        if function_name in self._handlers:
            del self._handlers[function_name]
    
    def get_function(self, name: str) -> Optional[FunctionDefinition]:
        """Get a function definition"""
        return self._functions.get(name)
    
    def list_functions(self) -> List[FunctionDefinition]:
        """List all registered functions"""
        return list(self._functions.values())
    
    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """Get all functions in OpenAI tools format"""
        return [f.to_openai_format() for f in self._functions.values()]
    
    async def handle_call(
        self,
        function_name: str,
        arguments: Dict[str, Any]
    ) -> FunctionCallResult:
        """
        Execute a function call with validation and error handling.

        This is the main entry point for function execution. It performs
        validation, executes the handler, and returns a complete result
        with status, timing, and any errors.

        處理函數調用 - 驗證、執行並返回結果。

        Args:
            function_name (str): Name of the function to call.
                                Must be registered via register().
            arguments (Dict[str, Any]): Arguments to pass to the function.
                                       Keys must match parameter schema.

        Returns:
            FunctionCallResult: Complete execution result with:
                - status: SUCCESS, FAILED, or INVALID
                - result: Function return value (if successful)
                - error: Error message (if failed)
                - validation_errors: List of validation errors (if invalid)
                - execution_time_ms: Time taken to execute
                - call_id: Unique identifier for this call
                - timestamp: When the call was made

        Execution Flow:
            1. Check if function exists → INVALID if not found
            2. Validate arguments against schema → INVALID if validation fails
            3. Check if handler exists → FAILED if missing
            4. Execute handler (sync or async) → SUCCESS or FAILED
            5. Capture timing and result/error
            6. Add to call history
            7. Return result

        Error Handling:
            - Function not found → status=INVALID, error="Function not found: {name}"
            - Validation failed → status=INVALID, validation_errors=[...]
            - Handler missing → status=FAILED, error="No handler for function: {name}"
            - Execution exception → status=FAILED, error=exception message

        Example - Successful Call:
            >>> handler = FunctionCallHandler()
            >>> # ... register functions ...
            >>>
            >>> result = await handler.handle_call("add", {"a": 5, "b": 3})
            >>> if result.status == FunctionCallStatus.SUCCESS:
            ...     print(f"Result: {result.result}")  # 8
            ...     print(f"Time: {result.execution_time_ms}ms")

        Example - Validation Error:
            >>> result = await handler.handle_call("add", {"a": 5})  # missing 'b'
            >>> if result.status == FunctionCallStatus.INVALID:
            ...     print(f"Errors: {result.validation_errors}")
            ...     # ['Missing required field: b']

        Example - Execution Error:
            >>> result = await handler.handle_call("divide", {"a": 5, "b": 0})
            >>> if result.status == FunctionCallStatus.FAILED:
            ...     print(f"Error: {result.error}")
            ...     # "division by zero"

        Performance:
            - Validation: O(n) where n = number of parameters
            - Execution: Depends on handler implementation
            - History storage: O(1) append

        Thread Safety:
            Not thread-safe. Use separate instances for concurrent calls.

        See Also:
            - register(): Add functions to registry
            - get_history(): View all past calls
            - parse_openai_tool_call(): Parse OpenAI format before calling
        """
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
        tool_call: Dict[str, Any]
    ) -> tuple[str, Dict[str, Any]]:
        """Parse an OpenAI tool call response"""
        function_name = tool_call.get("function", {}).get("name", "")
        arguments_str = tool_call.get("function", {}).get("arguments", "{}")
        
        try:
            arguments = json.loads(arguments_str)
        except json.JSONDecodeError:
            arguments = {}
        
        return function_name, arguments
    
    def get_history(self) -> List[FunctionCallResult]:
        """Get call history"""
        return self._call_history.copy()
    
    def clear_history(self) -> None:
        """Clear call history"""
        self._call_history.clear()


@dataclass
class RoutingRule:
    """
    A routing rule for directing tool calls to specific executors.

    Defines a condition-based routing rule with priority. The condition function
    evaluates the tool name and parameters to determine if this rule applies.
    Rules are evaluated in priority order (highest first).

    路由規則 - 定義將工具調用導向特定執行器的條件。

    Attributes:
        name (str): Unique identifier for this rule. Used for debugging and removal.
                    規則名稱
        condition (Callable[[str, Dict[str, Any]], bool]): Function that evaluates
                   if this rule matches. Receives (tool_name, params) and returns
                   True if this rule applies, False otherwise.
                   條件函數
        executor_id (str): ID of the executor to use if condition matches.
                          Must be registered in the router.
                          執行器 ID
        priority (int): Rule priority. Higher numbers evaluated first.
                       Default: 0. Use higher priorities for more specific rules.
                       優先級（數字越大越優先）

    Priority Guidelines:
        - Critical/security rules: 100+
        - Specific business rules: 50-99
        - General routing: 10-49
        - Fallback rules: 0-9

    Example - Simple Condition:
        >>> rule = RoutingRule(
        ...     name="database_rule",
        ...     condition=lambda name, params: name.startswith("db_"),
        ...     executor_id="database_executor",
        ...     priority=10
        ... )

    Example - Complex Condition:
        >>> def is_admin_operation(name: str, params: Dict[str, Any]) -> bool:
        ...     return (
        ...         params.get("user_role") == "admin" and
        ...         name in ["delete_user", "modify_permissions"]
        ...     )
        >>>
        >>> rule = RoutingRule(
        ...     name="admin_ops_rule",
        ...     condition=is_admin_operation,
        ...     executor_id="admin_executor",
        ...     priority=100  # High priority for security
        ... )

    Example - Tenant-Based Routing:
        >>> rule = RoutingRule(
        ...     name="tenant_a_rule",
        ...     condition=lambda name, params: params.get("tenant") == "tenant_a",
        ...     executor_id="tenant_a_executor",
        ...     priority=50
        ... )

    Condition Best Practices:
        - Keep conditions fast (evaluated on every call)
        - Avoid side effects in conditions
        - Make conditions deterministic
        - Use specific conditions for high-priority rules
        - Use general conditions for low-priority rules

    See Also:
        - ToolCallRouter.add_rule(): Add rule to router
        - ToolCallRouter.route(): Evaluate rules to find executor
    """
    name: str
    condition: Callable[[str, Dict[str, Any]], bool]
    executor_id: str
    priority: int = 0


class ToolCallRouter:
    """
    Intelligent routing system for distributing tool calls to specialized executors.

    Routes function calls to different executors based on configurable rules.
    Supports priority-based rule matching, default executors, and both sync/async
    execution patterns. Useful for distributed systems, multi-tenant applications,
    or workload partitioning.

    工具調用路由器 - 將工具調用路由到合適的執行器。

    Use Cases:
        - Route database calls to database executor
        - Route API calls to HTTP executor
        - Route compute-intensive calls to background workers
        - Multi-tenant routing based on tenant ID
        - A/B testing with traffic splitting
        - Load balancing across multiple executors

    Architecture:
        1. Register multiple executors (handlers, services, workers)
        2. Define routing rules with conditions and priorities
        3. Set optional default executor for unmatched calls
        4. Route calls through rule evaluation
        5. Execute on matched executor

    Attributes:
        _executors (Dict[str, Any]): Registry of executor instances by ID
        _rules (List[RoutingRule]): Ordered list of routing rules (by priority)
        _default_executor (Optional[str]): Fallback executor ID if no rules match

    Rule Matching:
        Rules are evaluated in priority order (highest first).
        First matching rule determines the executor.
        If no rules match, use default executor.
        If no default, raise ValueError.

    Example - Database vs API Routing:
        >>> router = ToolCallRouter()
        >>>
        >>> # Register executors
        >>> router.register_executor("database", DatabaseExecutor())
        >>> router.register_executor("api", APIExecutor())
        >>> router.register_executor("default", GeneralExecutor())
        >>>
        >>> # Add routing rules
        >>> router.add_rule(RoutingRule(
        ...     name="route_db",
        ...     condition=lambda name, params: name.startswith("query_"),
        ...     executor_id="database",
        ...     priority=10
        ... ))
        >>>
        >>> router.add_rule(RoutingRule(
        ...     name="route_api",
        ...     condition=lambda name, params: "url" in params,
        ...     executor_id="api",
        ...     priority=5
        ... ))
        >>>
        >>> router.set_default_executor("default")
        >>>
        >>> # Route calls
        >>> result = await router.execute("query_users", {"table": "users"})
        >>> # → Routed to database executor
        >>>
        >>> result = await router.execute("fetch", {"url": "https://..."})
        >>> # → Routed to api executor
        >>>
        >>> result = await router.execute("other", {"data": "..."})
        >>> # → Routed to default executor

    Example - Multi-Tenant Routing:
        >>> router = ToolCallRouter()
        >>>
        >>> router.register_executor("tenant_a", TenantAExecutor())
        >>> router.register_executor("tenant_b", TenantBExecutor())
        >>>
        >>> router.add_rule(RoutingRule(
        ...     name="tenant_a_route",
        ...     condition=lambda name, params: params.get("tenant_id") == "tenant_a",
        ...     executor_id="tenant_a",
        ...     priority=10
        ... ))
        >>>
        >>> router.add_rule(RoutingRule(
        ...     name="tenant_b_route",
        ...     condition=lambda name, params: params.get("tenant_id") == "tenant_b",
        ...     executor_id="tenant_b",
        ...     priority=10
        ... ))

    Thread Safety:
        Not thread-safe. Use separate instances or add synchronization.

    Performance:
        - Rule evaluation: O(n) where n = number of rules
        - Rules sorted by priority once on add/remove
        - Executor lookup: O(1) hash table lookup

    See Also:
        - RoutingRule: Define routing conditions
        - FunctionCallHandler: Basic executor without routing
    """

    def __init__(self):
        """
        Initialize an empty tool call router.

        Creates empty registries for executors and rules, with no default executor.

        初始化工具調用路由器。
        """
        self._executors: Dict[str, Any] = {}
        self._rules: List[RoutingRule] = []
        self._default_executor: Optional[str] = None
    
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
        params: Dict[str, Any]
    ) -> Optional[Any]:
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
        params: Dict[str, Any]
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
    
    def list_executors(self) -> List[str]:
        """List all executor IDs"""
        return list(self._executors.keys())
    
    def list_rules(self) -> List[RoutingRule]:
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
