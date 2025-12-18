"""
Tool Registry - Central registry for all MCP tools

This module provides a centralized registry for managing tool definitions,
validation, and execution across multiple MCP servers.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from uuid import uuid4

logger = logging.getLogger(__name__)


class ToolCategory(Enum):
    """Tool category enumeration"""
    CODE_ANALYSIS = 'code_analysis'
    SECURITY = 'security'
    TESTING = 'testing'
    DOCUMENTATION = 'documentation'
    PERFORMANCE = 'performance'
    DEPLOYMENT = 'deployment'
    MONITORING = 'monitoring'
    VALIDATION = 'validation'
    AUTOMATION = 'automation'
    OTHER = 'other'


class ToolStatus(Enum):
    """Tool availability status"""
    AVAILABLE = 'available'
    DEPRECATED = 'deprecated'
    DISABLED = 'disabled'
    EXPERIMENTAL = 'experimental'


@dataclass
class ToolDefinition:
    """Definition of an MCP tool"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    category: ToolCategory = ToolCategory.OTHER
    status: ToolStatus = ToolStatus.AVAILABLE
    version: str = '1.0.0'
    server_name: Optional[str] = None
    server_id: Optional[str] = None
    output_schema: Optional[Dict[str, Any]] = None
    examples: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool definition to dictionary"""
        return {
            'name': self.name,
            'description': self.description,
            'inputSchema': self.input_schema,
            'outputSchema': self.output_schema,
            'category': self.category.value,
            'status': self.status.value,
            'version': self.version,
            'server_name': self.server_name,
            'server_id': self.server_id,
            'examples': self.examples,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }
        
    def validate_input(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input arguments against schema
        
        Returns:
            Validation result with 'valid' boolean and optional 'errors' list
        """
        errors = []
        schema = self.input_schema
        
        # Check required fields
        required = schema.get('required', [])
        for field_name in required:
            if field_name not in arguments:
                errors.append(f"Missing required field: {field_name}")
                
        # Validate property types
        properties = schema.get('properties', {})
        for key, value in arguments.items():
            if key in properties:
                prop_schema = properties[key]
                type_error = self._validate_type(key, value, prop_schema)
                if type_error:
                    errors.append(type_error)
                    
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
        
    def _validate_type(
        self,
        field_name: str,
        value: Any,
        schema: Dict[str, Any]
    ) -> Optional[str]:
        """Validate a single field type"""
        expected_type = schema.get('type')
        
        type_map = {
            'string': str,
            'number': (int, float),
            'integer': int,
            'boolean': bool,
            'array': list,
            'object': dict
        }
        
        if expected_type and expected_type in type_map:
            expected = type_map[expected_type]
            if not isinstance(value, expected):
                return f"Field '{field_name}' expected type {expected_type}, got {type(value).__name__}"
                
        # Check enum values
        if 'enum' in schema and value not in schema['enum']:
            return f"Field '{field_name}' must be one of {schema['enum']}"
            
        return None


@dataclass
class ToolExecutionResult:
    """Result of a tool execution"""
    tool_name: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    duration_ms: float = 0.0
    server_name: Optional[str] = None
    execution_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'execution_id': self.execution_id,
            'tool_name': self.tool_name,
            'success': self.success,
            'result': self.result,
            'error': self.error,
            'error_code': self.error_code,
            'duration_ms': self.duration_ms,
            'server_name': self.server_name,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


class ToolRegistry:
    """
    Central registry for MCP tools
    
    Manages tool registration, lookup, validation, and provides
    search and filtering capabilities.
    """
    
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._category_index: Dict[ToolCategory, List[str]] = {}
        self._server_index: Dict[str, List[str]] = {}
        self._aliases: Dict[str, str] = {}  # alias -> tool_name
        
    def register(self, tool: ToolDefinition) -> None:
        """
        Register a tool in the registry
        
        Args:
            tool: Tool definition to register
        """
        self._tools[tool.name] = tool
        
        # Update category index
        if tool.category not in self._category_index:
            self._category_index[tool.category] = []
        if tool.name not in self._category_index[tool.category]:
            self._category_index[tool.category].append(tool.name)
            
        # Update server index
        if tool.server_name:
            if tool.server_name not in self._server_index:
                self._server_index[tool.server_name] = []
            if tool.name not in self._server_index[tool.server_name]:
                self._server_index[tool.server_name].append(tool.name)
                
        logger.debug(f'Registered tool: {tool.name}')
        
    def unregister(self, tool_name: str) -> bool:
        """
        Unregister a tool from the registry
        
        Returns:
            True if tool was removed, False if not found
        """
        tool = self._tools.pop(tool_name, None)
        if not tool:
            return False
            
        # Update category index
        if tool.category in self._category_index:
            if tool_name in self._category_index[tool.category]:
                self._category_index[tool.category].remove(tool_name)
                
        # Update server index
        if tool.server_name and tool.server_name in self._server_index:
            if tool_name in self._server_index[tool.server_name]:
                self._server_index[tool.server_name].remove(tool_name)
                
        # Remove aliases
        aliases_to_remove = [
            alias for alias, name in self._aliases.items()
            if name == tool_name
        ]
        for alias in aliases_to_remove:
            del self._aliases[alias]
            
        logger.debug(f'Unregistered tool: {tool_name}')
        return True
        
    def get(self, tool_name: str) -> Optional[ToolDefinition]:
        """
        Get a tool by name
        
        Args:
            tool_name: Tool name or alias
            
        Returns:
            Tool definition or None if not found
        """
        # Check if it's an alias
        resolved_name = self._aliases.get(tool_name, tool_name)
        return self._tools.get(resolved_name)
        
    def exists(self, tool_name: str) -> bool:
        """Check if a tool exists"""
        resolved_name = self._aliases.get(tool_name, tool_name)
        return resolved_name in self._tools
        
    def add_alias(self, alias: str, tool_name: str) -> bool:
        """
        Add an alias for a tool
        
        Returns:
            True if alias was added, False if tool doesn't exist
        """
        if tool_name not in self._tools:
            return False
        self._aliases[alias] = tool_name
        return True
        
    def list_all(
        self,
        status: Optional[ToolStatus] = None
    ) -> List[ToolDefinition]:
        """
        List all registered tools
        
        Args:
            status: Optional filter by status
            
        Returns:
            List of tool definitions
        """
        tools = list(self._tools.values())
        if status:
            tools = [t for t in tools if t.status == status]
        return tools
        
    def list_by_category(self, category: ToolCategory) -> List[ToolDefinition]:
        """Get all tools in a category"""
        tool_names = self._category_index.get(category, [])
        return [self._tools[name] for name in tool_names if name in self._tools]
        
    def list_by_server(self, server_name: str) -> List[ToolDefinition]:
        """Get all tools from a server"""
        tool_names = self._server_index.get(server_name, [])
        return [self._tools[name] for name in tool_names if name in self._tools]
        
    def search(
        self,
        query: str,
        categories: Optional[List[ToolCategory]] = None,
        status: Optional[ToolStatus] = None
    ) -> List[ToolDefinition]:
        """
        Search for tools by name or description
        
        Args:
            query: Search query string
            categories: Optional list of categories to filter
            status: Optional status filter
            
        Returns:
            List of matching tools
        """
        query_lower = query.lower()
        results = []
        
        for tool in self._tools.values():
            # Apply filters
            if status and tool.status != status:
                continue
            if categories and tool.category not in categories:
                continue
                
            # Search in name and description
            if (query_lower in tool.name.lower() or
                query_lower in tool.description.lower()):
                results.append(tool)
                
        return results
        
    def validate_arguments(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate arguments for a tool
        
        Args:
            tool_name: Tool name
            arguments: Arguments to validate
            
        Returns:
            Validation result
        """
        tool = self.get(tool_name)
        if not tool:
            return {
                'valid': False,
                'errors': [f'Tool not found: {tool_name}']
            }
            
        return tool.validate_input(arguments)
        
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        status_counts = {}
        for tool in self._tools.values():
            status = tool.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
        category_counts = {}
        for category, tools in self._category_index.items():
            category_counts[category.value] = len(tools)
            
        return {
            'total_tools': len(self._tools),
            'total_servers': len(self._server_index),
            'total_aliases': len(self._aliases),
            'status_distribution': status_counts,
            'category_distribution': category_counts
        }
        
    def export_schema(self) -> Dict[str, Any]:
        """Export all tool schemas for documentation"""
        return {
            'version': '1.0.0',
            'tools': [tool.to_dict() for tool in self._tools.values()],
            'categories': [c.value for c in ToolCategory],
            'statistics': self.get_stats()
        }


# Factory function
def create_tool_registry() -> ToolRegistry:
    """Create a new ToolRegistry instance"""
    return ToolRegistry()


# Pre-defined tool definitions for common operations
def get_default_tool_definitions() -> List[ToolDefinition]:
    """Get default tool definitions for SynergyMesh"""
    return [
        ToolDefinition(
            name='analyze-code',
            description='Analyze code for patterns, complexity, and quality metrics',
            input_schema={
                'type': 'object',
                'properties': {
                    'code': {'type': 'string', 'description': 'Source code to analyze'},
                    'language': {'type': 'string', 'description': 'Programming language'},
                    'metrics': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'description': 'Metrics to analyze'
                    }
                },
                'required': ['code']
            },
            category=ToolCategory.CODE_ANALYSIS,
            server_name='code-analyzer'
        ),
        ToolDefinition(
            name='scan-vulnerabilities',
            description='Scan code for security vulnerabilities',
            input_schema={
                'type': 'object',
                'properties': {
                    'code': {'type': 'string'},
                    'severity_threshold': {
                        'type': 'string',
                        'enum': ['low', 'medium', 'high', 'critical']
                    }
                },
                'required': ['code']
            },
            category=ToolCategory.SECURITY,
            server_name='security-scanner'
        ),
        ToolDefinition(
            name='validate-provenance',
            description='Validate SLSA provenance data for supply chain security',
            input_schema={
                'type': 'object',
                'properties': {
                    'provenance': {'type': 'object'},
                    'level': {'type': 'string', 'enum': ['1', '2', '3', '4']}
                },
                'required': ['provenance']
            },
            category=ToolCategory.VALIDATION,
            server_name='slsa-validator'
        ),
        ToolDefinition(
            name='generate-tests',
            description='Generate unit tests for code',
            input_schema={
                'type': 'object',
                'properties': {
                    'code': {'type': 'string'},
                    'framework': {
                        'type': 'string',
                        'enum': ['jest', 'pytest', 'mocha', 'junit']
                    },
                    'coverage_target': {
                        'type': 'number',
                        'minimum': 0,
                        'maximum': 100
                    }
                },
                'required': ['code']
            },
            category=ToolCategory.TESTING,
            server_name='test-generator'
        ),
        ToolDefinition(
            name='generate-docs',
            description='Generate documentation for code',
            input_schema={
                'type': 'object',
                'properties': {
                    'code': {'type': 'string'},
                    'format': {
                        'type': 'string',
                        'enum': ['markdown', 'jsdoc', 'sphinx', 'openapi']
                    }
                },
                'required': ['code']
            },
            category=ToolCategory.DOCUMENTATION,
            server_name='doc-generator'
        ),
        ToolDefinition(
            name='analyze-performance',
            description='Analyze code performance characteristics',
            input_schema={
                'type': 'object',
                'properties': {
                    'code': {'type': 'string'},
                    'analysis_type': {
                        'type': 'string',
                        'enum': ['complexity', 'memory', 'runtime']
                    }
                },
                'required': ['code']
            },
            category=ToolCategory.PERFORMANCE,
            server_name='performance-analyzer'
        )
    ]
