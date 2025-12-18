"""
Tool Definition System (工具定義系統)
Defines the core tool interface and execution framework

Reference: LangChain tool calling and function execution standards
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime
import uuid
import json
import asyncio


class ToolCategory(Enum):
    """Tool categories for organization and routing"""
    DATABASE = "database"
    FILESYSTEM = "filesystem"
    API = "api"
    DEPLOYMENT = "deployment"
    SECURITY = "security"
    MONITORING = "monitoring"
    CODE = "code"
    COMMUNICATION = "communication"


class ToolStatus(Enum):
    """Status of tool execution"""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    RETRY = "retry"
    PENDING = "pending"


@dataclass
class ToolResult:
    """Result of tool execution"""
    tool_name: str
    status: ToolStatus
    output: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Tool:
    """
    工具接口定義
    Core tool interface for the SynergyMesh execution system
    
    Reference: Function calling and tool execution standards
    """
    # Tool metadata
    name: str
    description: str
    category: ToolCategory
    version: str = "1.0.0"
    
    # Input/output schemas (JSON Schema format)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    
    # Execution configuration
    timeout_seconds: float = 30.0
    max_retries: int = 3
    requires_confirmation: bool = False
    
    # Execution function
    execute_fn: Optional[Callable] = None
    
    # Metadata
    tool_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Execute the tool with given parameters"""
        start_time = datetime.now()
        
        try:
            # Validate input
            self._validate_input(params)
            
            # Execute the function
            if self.execute_fn is None:
                raise ValueError(f"Tool {self.name} has no execution function")
            
            if asyncio.iscoroutinefunction(self.execute_fn):
                result = await asyncio.wait_for(
                    self.execute_fn(params),
                    timeout=self.timeout_seconds
                )
            else:
                result = self.execute_fn(params)
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.SUCCESS,
                output=result,
                execution_time_ms=execution_time
            )
            
        except asyncio.TimeoutError:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.TIMEOUT,
                error=f"Tool execution timed out after {self.timeout_seconds}s",
                execution_time_ms=execution_time
            )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILURE,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    def _validate_input(self, params: Dict[str, Any]) -> None:
        """Validate input parameters against schema"""
        if not self.input_schema:
            return
        
        required = self.input_schema.get('required', [])
        properties = self.input_schema.get('properties', {})
        
        for req_field in required:
            if req_field not in params:
                raise ValueError(f"Missing required field: {req_field}")
        
        for key, value in params.items():
            if key in properties:
                expected_type = properties[key].get('type')
                if expected_type and not self._check_type(value, expected_type):
                    raise ValueError(f"Invalid type for {key}: expected {expected_type}")
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected JSON Schema type"""
        type_map = {
            'string': str,
            'number': (int, float),
            'integer': int,
            'boolean': bool,
            'array': list,
            'object': dict,
        }
        return isinstance(value, type_map.get(expected_type, object))
    
    def to_openai_function(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.input_schema or {"type": "object", "properties": {}}
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary representation"""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "version": self.version,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "tags": self.tags,
        }


class ToolRegistry:
    """
    工具註冊表
    Central registry for all available tools
    """
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._categories: Dict[ToolCategory, List[str]] = {cat: [] for cat in ToolCategory}
        self._tags: Dict[str, List[str]] = {}
    
    def register(self, tool: Tool) -> None:
        """Register a tool"""
        if tool.name in self._tools:
            raise ValueError(f"Tool {tool.name} already registered")
        
        self._tools[tool.name] = tool
        self._categories[tool.category].append(tool.name)
        
        for tag in tool.tags:
            if tag not in self._tags:
                self._tags[tag] = []
            self._tags[tag].append(tool.name)
    
    def unregister(self, tool_name: str) -> None:
        """Unregister a tool"""
        if tool_name not in self._tools:
            return
        
        tool = self._tools[tool_name]
        self._categories[tool.category].remove(tool_name)
        
        for tag in tool.tags:
            if tag in self._tags and tool_name in self._tags[tag]:
                self._tags[tag].remove(tool_name)
        
        del self._tools[tool_name]
    
    def get(self, tool_name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self._tools.get(tool_name)
    
    def get_by_category(self, category: ToolCategory) -> List[Tool]:
        """Get all tools in a category"""
        return [self._tools[name] for name in self._categories.get(category, [])]
    
    def get_by_tag(self, tag: str) -> List[Tool]:
        """Get all tools with a specific tag"""
        return [self._tools[name] for name in self._tags.get(tag, [])]
    
    def list_all(self) -> List[Tool]:
        """List all registered tools"""
        return list(self._tools.values())
    
    def search(self, query: str) -> List[Tool]:
        """Search tools by name or description"""
        query_lower = query.lower()
        results = []
        for tool in self._tools.values():
            if query_lower in tool.name.lower() or query_lower in tool.description.lower():
                results.append(tool)
        return results
    
    def to_openai_functions(self) -> List[Dict[str, Any]]:
        """Convert all tools to OpenAI function format"""
        return [tool.to_openai_function() for tool in self._tools.values()]


class ToolExecutor:
    """
    工具執行器
    Executes tools with retry logic, timeout handling, and error recovery
    """
    
    def __init__(self, registry: Optional[ToolRegistry] = None):
        self.registry = registry or ToolRegistry()
        self._execution_history: List[ToolResult] = []
    
    async def execute(
        self,
        tool_name: str,
        params: Dict[str, Any],
        retry_on_failure: bool = True
    ) -> ToolResult:
        """Execute a tool by name"""
        tool = self.registry.get(tool_name)
        if not tool:
            return ToolResult(
                tool_name=tool_name,
                status=ToolStatus.FAILURE,
                error=f"Tool not found: {tool_name}"
            )
        
        attempts = tool.max_retries if retry_on_failure else 1
        last_result = None
        
        for attempt in range(attempts):
            result = await tool.execute(params)
            last_result = result
            
            if result.status == ToolStatus.SUCCESS:
                break
            
            if attempt < attempts - 1:
                result.status = ToolStatus.RETRY
                await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
        
        self._execution_history.append(last_result)
        return last_result
    
    async def execute_many(
        self,
        tool_calls: List[Dict[str, Any]],
        parallel: bool = False
    ) -> List[ToolResult]:
        """Execute multiple tools"""
        if parallel:
            tasks = [
                self.execute(call['tool_name'], call.get('params', {}))
                for call in tool_calls
            ]
            return await asyncio.gather(*tasks)
        else:
            results = []
            for call in tool_calls:
                result = await self.execute(call['tool_name'], call.get('params', {}))
                results.append(result)
            return results
    
    def get_history(self) -> List[ToolResult]:
        """Get execution history"""
        return self._execution_history.copy()
    
    def clear_history(self) -> None:
        """Clear execution history"""
        self._execution_history.clear()


# Pre-built tool factories for common operations
def create_database_tool(
    name: str,
    description: str,
    execute_fn: Callable,
    input_schema: Optional[Dict] = None
) -> Tool:
    """Factory for creating database tools"""
    return Tool(
        name=name,
        description=description,
        category=ToolCategory.DATABASE,
        execute_fn=execute_fn,
        input_schema=input_schema or {"type": "object", "properties": {}},
        tags=["database", "sql"]
    )


def create_api_tool(
    name: str,
    description: str,
    execute_fn: Callable,
    input_schema: Optional[Dict] = None
) -> Tool:
    """Factory for creating API tools"""
    return Tool(
        name=name,
        description=description,
        category=ToolCategory.API,
        execute_fn=execute_fn,
        input_schema=input_schema or {"type": "object", "properties": {}},
        tags=["api", "http"]
    )


def create_code_tool(
    name: str,
    description: str,
    execute_fn: Callable,
    input_schema: Optional[Dict] = None
) -> Tool:
    """Factory for creating code execution tools"""
    return Tool(
        name=name,
        description=description,
        category=ToolCategory.CODE,
        execute_fn=execute_fn,
        input_schema=input_schema or {"type": "object", "properties": {}},
        tags=["code", "execution"]
    )
