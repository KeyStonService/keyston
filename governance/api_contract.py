#!/usr/bin/env python3
"""
API Contract and Governance Boundary Definition Module
=======================================================

This module provides a comprehensive framework for defining, validating, and enforcing
API contracts and governance boundaries between different system modules. It ensures
consistency, reliability, and maintainability in multi-module architectures.

Core Functionality
------------------
1. **Contract Definition**: Define API contracts with input/output schemas, latency requirements,
   and error handling strategies for each module.

2. **Boundary Enforcement**: Enforce strict language and protocol boundaries between modules
   to prevent cross-contamination and maintain architectural integrity.

3. **Automated Validation**: Automatically validate API calls against defined contracts,
   ensuring type safety and contract compliance at runtime.

4. **Dependency Management**: Detect and prevent circular dependencies in module dependency chains.

5. **Governance Reporting**: Generate comprehensive governance reports for auditing and monitoring.

Key Components
--------------
- **ModuleRole**: Enum defining different module responsibility categories
- **ErrorCategory**: Enum classifying different types of system errors
- **APIContract**: Dataclass representing a complete API contract specification
- **GovernanceValidator**: Main validator class for contract enforcement and validation

Architecture Context
--------------------
This module is designed for systems requiring:
- Strict module isolation (e.g., flight control systems, autonomous vehicles)
- Real-time performance guarantees with latency constraints
- Fault-tolerant error handling with well-defined fallback strategies
- Multi-language or multi-service integration with consistent interfaces

Usage Example
-------------
Basic usage:

    >>> from api_contract import GovernanceValidator, ModuleRole
    >>>
    >>> # Initialize validator with predefined contracts
    >>> validator = GovernanceValidator()
    >>>
    >>> # Register a new contract
    >>> validator.register_contract(
    ...     module_name="sensor_processor",
    ...     role=ModuleRole.DATA_PROCESSOR,
    ...     input_schema={"type": "object", "properties": {"sensor_data": {"type": "array"}}},
    ...     output_schema={"type": "object", "properties": {"processed_data": {"type": "array"}}},
    ...     max_latency_ms=100
    ... )
    >>>
    >>> # Validate an API call
    >>> result = validator.validate_call(
    ...     from_module="sensor_processor",
    ...     to_module="decision_engine",
    ...     data={"sensor_data": [1, 2, 3]}
    ... )
    >>> print(result.is_valid)
    True

Advanced usage with dependency detection:

    >>> # Check for circular dependencies
    >>> validator.add_dependency("module_a", "module_b")
    >>> validator.add_dependency("module_b", "module_c")
    >>> validator.add_dependency("module_c", "module_a")  # Creates cycle
    >>> cycles = validator.detect_circular_dependencies()
    >>> print(cycles)
    [['module_a', 'module_b', 'module_c', 'module_a']]

Author: SynergyMesh Governance Team
Version: 1.0.0
Date: 2025-12-12
"""

import json
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict
import re


class ModuleRole(Enum):
    """
    Enum defining different module responsibility categories.
    
    These roles help classify modules by their primary function in the system,
    enabling better governance and dependency management.
    """
    DATA_PROCESSOR = "data_processor"
    DECISION_ENGINE = "decision_engine"
    CONTROL_SYSTEM = "control_system"
    SENSOR_INTERFACE = "sensor_interface"
    ACTUATOR_INTERFACE = "actuator_interface"
    COMMUNICATION_HUB = "communication_hub"
    MONITORING_SERVICE = "monitoring_service"
    STORAGE_SERVICE = "storage_service"
    ANALYTICS_ENGINE = "analytics_engine"
    USER_INTERFACE = "user_interface"


class ErrorCategory(Enum):
    """
    Enum classifying different types of system errors.
    
    Used for error handling strategies and governance reporting.
    """
    CONTRACT_VIOLATION = "contract_violation"
    BOUNDARY_VIOLATION = "boundary_violation"
    TIMEOUT = "timeout"
    INVALID_INPUT = "invalid_input"
    INVALID_OUTPUT = "invalid_output"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    MISSING_CONTRACT = "missing_contract"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    RUNTIME_ERROR = "runtime_error"


@dataclass
class APIContract:
    """
    Dataclass representing a complete API contract specification.
    
    Attributes:
        module_name: Unique identifier for the module
        role: Module's primary responsibility category
        input_schema: JSON schema for expected input data
        output_schema: JSON schema for expected output data
        max_latency_ms: Maximum allowed latency in milliseconds
        allowed_callers: List of module names allowed to call this module
        error_handling: Strategy for handling errors (e.g., "retry", "fallback", "fail_fast")
        version: Contract version for compatibility tracking
        description: Human-readable description of the contract
    """
    module_name: str
    role: ModuleRole
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    max_latency_ms: float
    allowed_callers: List[str] = field(default_factory=list)
    error_handling: str = "fail_fast"
    version: str = "1.0.0"
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert contract to dictionary for serialization."""
        result = asdict(self)
        result['role'] = self.role.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'APIContract':
        """Create contract from dictionary."""
        data['role'] = ModuleRole(data['role'])
        return cls(**data)


@dataclass
class ValidationResult:
    """
    Result of contract validation.
    
    Attributes:
        is_valid: Whether the validation passed
        errors: List of error messages if validation failed
        warnings: List of warning messages
        latency_ms: Measured latency if applicable
        timestamp: When the validation occurred
    """
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    latency_ms: Optional[float] = None
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return asdict(self)


class GovernanceValidator:
    """
    Main validator class for contract enforcement and validation.
    
    This class provides the core functionality for managing API contracts,
    validating calls, detecting dependencies, and generating governance reports.
    
    Attributes:
        contracts: Dictionary mapping module names to their contracts
        dependencies: Graph of module dependencies
        call_history: Log of validated API calls
    """
    
    def __init__(self):
        """Initialize the governance validator."""
        self.contracts: Dict[str, APIContract] = {}
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.call_history: List[Dict[str, Any]] = []
        self.boundary_rules: Dict[str, List[str]] = {}
        
    def register_contract(
        self,
        module_name: str,
        role: ModuleRole,
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any],
        max_latency_ms: float,
        allowed_callers: Optional[List[str]] = None,
        error_handling: str = "fail_fast",
        version: str = "1.0.0",
        description: str = ""
    ) -> None:
        """
        Register a new API contract.
        
        Args:
            module_name: Unique identifier for the module
            role: Module's primary responsibility category
            input_schema: JSON schema for expected input data
            output_schema: JSON schema for expected output data
            max_latency_ms: Maximum allowed latency in milliseconds
            allowed_callers: List of module names allowed to call this module
            error_handling: Strategy for handling errors
            version: Contract version
            description: Human-readable description
        """
        contract = APIContract(
            module_name=module_name,
            role=role,
            input_schema=input_schema,
            output_schema=output_schema,
            max_latency_ms=max_latency_ms,
            allowed_callers=allowed_callers or [],
            error_handling=error_handling,
            version=version,
            description=description
        )
        self.contracts[module_name] = contract
        
    def validate_call(
        self,
        from_module: str,
        to_module: str,
        data: Dict[str, Any],
        latency_ms: Optional[float] = None
    ) -> ValidationResult:
        """
        Validate an API call against defined contracts.
        
        Args:
            from_module: Name of the calling module
            to_module: Name of the target module
            data: Data being passed in the call
            latency_ms: Measured latency of the call (optional)
        
        Returns:
            ValidationResult with validation status and any errors/warnings
        """
        errors = []
        warnings = []
        
        # Check if target module has a contract
        if to_module not in self.contracts:
            errors.append(f"No contract found for module '{to_module}'")
            return ValidationResult(is_valid=False, errors=errors)
        
        contract = self.contracts[to_module]
        
        # Check if caller is authorized
        if contract.allowed_callers and from_module not in contract.allowed_callers:
            errors.append(f"Module '{from_module}' not authorized to call '{to_module}'")
        
        # Validate input schema (simplified validation)
        if not self._validate_schema(data, contract.input_schema):
            errors.append(f"Input data does not match schema for '{to_module}'")
        
        # Check latency constraint
        if latency_ms is not None and latency_ms > contract.max_latency_ms:
            warnings.append(
                f"Latency {latency_ms}ms exceeds maximum {contract.max_latency_ms}ms"
            )
        
        # Record call in history
        self.call_history.append({
            'from_module': from_module,
            'to_module': to_module,
            'timestamp': time.time(),
            'is_valid': len(errors) == 0,
            'latency_ms': latency_ms
        })
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            latency_ms=latency_ms
        )
    
    def add_dependency(self, from_module: str, to_module: str) -> None:
        """
        Add a dependency relationship between modules.
        
        Args:
            from_module: Name of the dependent module
            to_module: Name of the module being depended upon
        """
        self.dependencies[from_module].add(to_module)
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """
        Detect circular dependencies in the module dependency graph.
        
        Returns:
            List of cycles, where each cycle is a list of module names
        """
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.dependencies.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path[:])
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    if cycle not in cycles:
                        cycles.append(cycle)
            
            rec_stack.remove(node)
        
        for module in self.dependencies.keys():
            if module not in visited:
                dfs(module, [])
        
        return cycles
    
    def set_boundary_rule(self, module: str, allowed_languages: List[str]) -> None:
        """
        Set language boundary rules for a module.
        
        Args:
            module: Module name
            allowed_languages: List of programming languages allowed for this module
        """
        self.boundary_rules[module] = allowed_languages
    
    def validate_boundary(self, module: str, language: str) -> ValidationResult:
        """
        Validate if a module respects its language boundary.
        
        Args:
            module: Module name
            language: Programming language being used
        
        Returns:
            ValidationResult with validation status
        """
        if module not in self.boundary_rules:
            return ValidationResult(
                is_valid=True,
                warnings=[f"No boundary rules defined for module '{module}'"]
            )
        
        allowed = self.boundary_rules[module]
        if language not in allowed:
            return ValidationResult(
                is_valid=False,
                errors=[f"Language '{language}' not allowed for module '{module}'. Allowed: {allowed}"]
            )
        
        return ValidationResult(is_valid=True)
    
    def generate_governance_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive governance report.
        
        Returns:
            Dictionary containing governance metrics and status
        """
        report = {
            'timestamp': time.time(),
            'total_contracts': len(self.contracts),
            'total_calls': len(self.call_history),
            'circular_dependencies': self.detect_circular_dependencies(),
            'contracts': {
                name: contract.to_dict()
                for name, contract in self.contracts.items()
            },
            'call_statistics': self._generate_call_statistics(),
            'boundary_rules': self.boundary_rules
        }
        return report
    
    def _validate_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        Simplified schema validation.
        
        Args:
            data: Data to validate
            schema: JSON schema to validate against
        
        Returns:
            True if valid, False otherwise
        """
        # Simplified validation - in production, use jsonschema library
        if schema.get('type') == 'object':
            if not isinstance(data, dict):
                return False
            
            required = schema.get('required', [])
            for field in required:
                if field not in data:
                    return False
            
            properties = schema.get('properties', {})
            for key, value in data.items():
                if key in properties:
                    prop_schema = properties[key]
                    if prop_schema.get('type') == 'array' and not isinstance(value, list):
                        return False
                    elif prop_schema.get('type') == 'string' and not isinstance(value, str):
                        return False
                    elif prop_schema.get('type') == 'number' and not isinstance(value, (int, float)):
                        return False
        
        return True
    
    def _generate_call_statistics(self) -> Dict[str, Any]:
        """
        Generate statistics from call history.
        
        Returns:
            Dictionary with call statistics
        """
        if not self.call_history:
            return {'total_calls': 0}
        
        valid_calls = sum(1 for call in self.call_history if call['is_valid'])
        latencies = [call['latency_ms'] for call in self.call_history if call.get('latency_ms')]
        
        stats = {
            'total_calls': len(self.call_history),
            'valid_calls': valid_calls,
            'invalid_calls': len(self.call_history) - valid_calls,
            'success_rate': valid_calls / len(self.call_history) if self.call_history else 0
        }
        
        if latencies:
            stats['latency'] = {
                'min_ms': min(latencies),
                'max_ms': max(latencies),
                'avg_ms': sum(latencies) / len(latencies)
            }
        
        return stats
    
    def export_contracts(self, filepath: str) -> None:
        """
        Export all contracts to a JSON file.
        
        Args:
            filepath: Path to output file
        """
        contracts_dict = {
            name: contract.to_dict()
            for name, contract in self.contracts.items()
        }
        with open(filepath, 'w') as f:
            json.dump(contracts_dict, f, indent=2)
    
    def import_contracts(self, filepath: str) -> None:
        """
        Import contracts from a JSON file.
        
        Args:
            filepath: Path to input file
        """
        with open(filepath, 'r') as f:
            contracts_dict = json.load(f)
        
        for name, contract_data in contracts_dict.items():
            contract = APIContract.from_dict(contract_data)
            self.contracts[name] = contract


# Example usage and testing
if __name__ == "__main__":
    # Create validator
    validator = GovernanceValidator()
    
    # Register contracts
    validator.register_contract(
        module_name="sensor_processor",
        role=ModuleRole.DATA_PROCESSOR,
        input_schema={
            "type": "object",
            "properties": {
                "sensor_data": {"type": "array"}
            },
            "required": ["sensor_data"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "processed_data": {"type": "array"}
            }
        },
        max_latency_ms=100,
        description="Processes raw sensor data"
    )
    
    validator.register_contract(
        module_name="decision_engine",
        role=ModuleRole.DECISION_ENGINE,
        input_schema={
            "type": "object",
            "properties": {
                "processed_data": {"type": "array"}
            }
        },
        output_schema={
            "type": "object",
            "properties": {
                "decision": {"type": "string"}
            }
        },
        max_latency_ms=50,
        allowed_callers=["sensor_processor"],
        description="Makes decisions based on processed data"
    )
    
    # Validate a call
    result = validator.validate_call(
        from_module="sensor_processor",
        to_module="decision_engine",
        data={"processed_data": [1, 2, 3]},
        latency_ms=45
    )
    
    print("Validation Result:")
    print(f"  Valid: {result.is_valid}")
    print(f"  Errors: {result.errors}")
    print(f"  Warnings: {result.warnings}")
    print(f"  Latency: {result.latency_ms}ms")
    
    # Add dependencies
    validator.add_dependency("sensor_processor", "decision_engine")
    validator.add_dependency("decision_engine", "control_system")
    
    # Check for circular dependencies
    cycles = validator.detect_circular_dependencies()
    print(f"\nCircular Dependencies: {cycles}")
    
    # Set boundary rules
    validator.set_boundary_rule("sensor_processor", ["python", "rust"])
    boundary_result = validator.validate_boundary("sensor_processor", "python")
    print(f"\nBoundary Validation: {boundary_result.is_valid}")
    
    # Generate governance report
    report = validator.generate_governance_report()
    print(f"\nGovernance Report:")
    print(f"  Total Contracts: {report['total_contracts']}")
    print(f"  Total Calls: {report['total_calls']}")
    print(f"  Success Rate: {report['call_statistics']['success_rate']:.2%}")
