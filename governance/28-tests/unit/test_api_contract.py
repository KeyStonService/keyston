#!/usr/bin/env python3
"""
Unit tests for API Contract and Governance Boundary Module
===========================================================

Tests all functionality of the api_contract module including:
- Contract registration and validation
- Boundary enforcement
- Circular dependency detection
- Governance reporting

Author: SynergyMesh Governance Team
Version: 1.0.0
Date: 2025-12-12
"""

import pytest
import json
import tempfile
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api_contract import (
    GovernanceValidator,
    ModuleRole,
    ErrorCategory,
    APIContract,
    ValidationResult
)


class TestAPIContract:
    """Tests for APIContract dataclass"""
    
    def test_contract_creation(self):
        """Test creating a basic contract"""
        contract = APIContract(
            module_name="test_module",
            role=ModuleRole.DATA_PROCESSOR,
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            max_latency_ms=100
        )
        assert contract.module_name == "test_module"
        assert contract.role == ModuleRole.DATA_PROCESSOR
        assert contract.max_latency_ms == 100
    
    def test_contract_to_dict(self):
        """Test contract serialization to dictionary"""
        contract = APIContract(
            module_name="test_module",
            role=ModuleRole.DECISION_ENGINE,
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            max_latency_ms=50
        )
        contract_dict = contract.to_dict()
        
        assert contract_dict['module_name'] == "test_module"
        assert contract_dict['role'] == "decision_engine"
        assert contract_dict['max_latency_ms'] == 50
    
    def test_contract_from_dict(self):
        """Test contract deserialization from dictionary"""
        data = {
            'module_name': 'test_module',
            'role': 'data_processor',
            'input_schema': {'type': 'object'},
            'output_schema': {'type': 'object'},
            'max_latency_ms': 75,
            'allowed_callers': [],
            'error_handling': 'fail_fast',
            'version': '1.0.0',
            'description': 'Test contract'
        }
        contract = APIContract.from_dict(data)
        
        assert contract.module_name == 'test_module'
        assert contract.role == ModuleRole.DATA_PROCESSOR
        assert contract.max_latency_ms == 75


class TestGovernanceValidator:
    """Tests for GovernanceValidator class"""
    
    @pytest.fixture
    def validator(self):
        """Create a fresh validator for each test"""
        return GovernanceValidator()
    
    def test_register_contract(self, validator):
        """Test registering a new contract"""
        validator.register_contract(
            module_name="sensor_module",
            role=ModuleRole.SENSOR_INTERFACE,
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            max_latency_ms=100
        )
        
        assert "sensor_module" in validator.contracts
        assert validator.contracts["sensor_module"].role == ModuleRole.SENSOR_INTERFACE
    
    def test_validate_call_success(self, validator):
        """Test successful call validation"""
        # Register contracts
        validator.register_contract(
            module_name="module_a",
            role=ModuleRole.DATA_PROCESSOR,
            input_schema={
                "type": "object",
                "properties": {"data": {"type": "array"}},
                "required": ["data"]
            },
            output_schema={"type": "object"},
            max_latency_ms=100
        )
        
        validator.register_contract(
            module_name="module_b",
            role=ModuleRole.DECISION_ENGINE,
            input_schema={
                "type": "object",
                "properties": {"input": {"type": "array"}}
            },
            output_schema={"type": "object"},
            max_latency_ms=50,
            allowed_callers=["module_a"]
        )
        
        # Validate call
        result = validator.validate_call(
            from_module="module_a",
            to_module="module_b",
            data={"input": [1, 2, 3]},
            latency_ms=30
        )
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert result.latency_ms == 30
    
    def test_validate_call_no_contract(self, validator):
        """Test validation with missing contract"""
        result = validator.validate_call(
            from_module="module_a",
            to_module="nonexistent_module",
            data={"test": "data"}
        )
        
        assert not result.is_valid
        assert "No contract found" in result.errors[0]
    
    def test_validate_call_unauthorized(self, validator):
        """Test validation with unauthorized caller"""
        validator.register_contract(
            module_name="protected_module",
            role=ModuleRole.CONTROL_SYSTEM,
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            max_latency_ms=100,
            allowed_callers=["authorized_module"]
        )
        
        result = validator.validate_call(
            from_module="unauthorized_module",
            to_module="protected_module",
            data={}
        )
        
        assert not result.is_valid
        assert "not authorized" in result.errors[0].lower()
    
    def test_validate_call_latency_warning(self, validator):
        """Test latency warning generation"""
        validator.register_contract(
            module_name="fast_module",
            role=ModuleRole.DATA_PROCESSOR,
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            max_latency_ms=50
        )
        
        result = validator.validate_call(
            from_module="caller",
            to_module="fast_module",
            data={},
            latency_ms=100  # Exceeds max_latency_ms
        )
        
        assert result.is_valid  # Still valid, just warning
        assert len(result.warnings) > 0
        assert "exceeds maximum" in result.warnings[0].lower()
    
    def test_add_dependency(self, validator):
        """Test adding module dependencies"""
        validator.add_dependency("module_a", "module_b")
        validator.add_dependency("module_a", "module_c")
        
        assert "module_b" in validator.dependencies["module_a"]
        assert "module_c" in validator.dependencies["module_a"]
    
    def test_detect_circular_dependencies_no_cycle(self, validator):
        """Test circular dependency detection with no cycles"""
        validator.add_dependency("module_a", "module_b")
        validator.add_dependency("module_b", "module_c")
        validator.add_dependency("module_c", "module_d")
        
        cycles = validator.detect_circular_dependencies()
        assert len(cycles) == 0
    
    def test_detect_circular_dependencies_with_cycle(self, validator):
        """Test circular dependency detection with a cycle"""
        validator.add_dependency("module_a", "module_b")
        validator.add_dependency("module_b", "module_c")
        validator.add_dependency("module_c", "module_a")
        
        cycles = validator.detect_circular_dependencies()
        assert len(cycles) > 0
        # Check that cycle contains all three modules
        cycle = cycles[0]
        assert "module_a" in cycle
        assert "module_b" in cycle
        assert "module_c" in cycle
    
    def test_set_boundary_rule(self, validator):
        """Test setting language boundary rules"""
        validator.set_boundary_rule("python_module", ["python", "cython"])
        
        assert "python_module" in validator.boundary_rules
        assert "python" in validator.boundary_rules["python_module"]
        assert "cython" in validator.boundary_rules["python_module"]
    
    def test_validate_boundary_success(self, validator):
        """Test successful boundary validation"""
        validator.set_boundary_rule("rust_module", ["rust", "c"])
        
        result = validator.validate_boundary("rust_module", "rust")
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_boundary_failure(self, validator):
        """Test failed boundary validation"""
        validator.set_boundary_rule("rust_module", ["rust", "c"])
        
        result = validator.validate_boundary("rust_module", "python")
        assert not result.is_valid
        assert "not allowed" in result.errors[0].lower()
    
    def test_validate_boundary_no_rules(self, validator):
        """Test boundary validation with no rules defined"""
        result = validator.validate_boundary("undefined_module", "python")
        
        assert result.is_valid  # Should pass with warning
        assert len(result.warnings) > 0
    
    def test_generate_governance_report(self, validator):
        """Test governance report generation"""
        # Setup some contracts and calls
        validator.register_contract(
            module_name="test_module",
            role=ModuleRole.DATA_PROCESSOR,
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            max_latency_ms=100
        )
        
        validator.validate_call(
            from_module="caller",
            to_module="test_module",
            data={},
            latency_ms=50
        )
        
        # Generate report
        report = validator.generate_governance_report()
        
        assert 'timestamp' in report
        assert report['total_contracts'] == 1
        assert report['total_calls'] == 1
        assert 'call_statistics' in report
        assert report['call_statistics']['total_calls'] == 1
    
    def test_export_import_contracts(self, validator):
        """Test exporting and importing contracts"""
        # Register contracts
        validator.register_contract(
            module_name="module_1",
            role=ModuleRole.DATA_PROCESSOR,
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            max_latency_ms=100
        )
        
        validator.register_contract(
            module_name="module_2",
            role=ModuleRole.DECISION_ENGINE,
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            max_latency_ms=50
        )
        
        # Export to temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            validator.export_contracts(filepath)
            
            # Create new validator and import
            new_validator = GovernanceValidator()
            new_validator.import_contracts(filepath)
            
            # Verify imported contracts
            assert len(new_validator.contracts) == 2
            assert "module_1" in new_validator.contracts
            assert "module_2" in new_validator.contracts
            assert new_validator.contracts["module_1"].role == ModuleRole.DATA_PROCESSOR
        finally:
            Path(filepath).unlink(missing_ok=True)
    
    def test_call_history_tracking(self, validator):
        """Test that call history is properly tracked"""
        validator.register_contract(
            module_name="target",
            role=ModuleRole.DATA_PROCESSOR,
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            max_latency_ms=100
        )
        
        # Make multiple calls
        validator.validate_call("caller1", "target", {})
        validator.validate_call("caller2", "target", {})
        validator.validate_call("caller3", "target", {})
        
        assert len(validator.call_history) == 3
        assert validator.call_history[0]['from_module'] == "caller1"
        assert validator.call_history[1]['from_module'] == "caller2"
        assert validator.call_history[2]['from_module'] == "caller3"


class TestValidationResult:
    """Tests for ValidationResult dataclass"""
    
    def test_validation_result_creation(self):
        """Test creating a validation result"""
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=["Warning message"],
            latency_ms=45.5
        )
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.warnings) == 1
        assert result.latency_ms == 45.5
    
    def test_validation_result_to_dict(self):
        """Test validation result serialization"""
        result = ValidationResult(
            is_valid=False,
            errors=["Error 1", "Error 2"],
            warnings=[],
            latency_ms=100
        )
        
        result_dict = result.to_dict()
        assert result_dict['is_valid'] == False
        assert len(result_dict['errors']) == 2
        assert result_dict['latency_ms'] == 100


class TestModuleRole:
    """Tests for ModuleRole enum"""
    
    def test_module_role_values(self):
        """Test that all module roles have correct values"""
        assert ModuleRole.DATA_PROCESSOR.value == "data_processor"
        assert ModuleRole.DECISION_ENGINE.value == "decision_engine"
        assert ModuleRole.CONTROL_SYSTEM.value == "control_system"
        assert ModuleRole.SENSOR_INTERFACE.value == "sensor_interface"


class TestErrorCategory:
    """Tests for ErrorCategory enum"""
    
    def test_error_category_values(self):
        """Test that all error categories have correct values"""
        assert ErrorCategory.CONTRACT_VIOLATION.value == "contract_violation"
        assert ErrorCategory.BOUNDARY_VIOLATION.value == "boundary_violation"
        assert ErrorCategory.TIMEOUT.value == "timeout"
        assert ErrorCategory.CIRCULAR_DEPENDENCY.value == "circular_dependency"


# Integration tests
class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_complete_workflow(self):
        """Test a complete workflow from registration to reporting"""
        validator = GovernanceValidator()
        
        # Step 1: Register contracts
        validator.register_contract(
            module_name="sensor",
            role=ModuleRole.SENSOR_INTERFACE,
            input_schema={"type": "object"},
            output_schema={
                "type": "object",
                "properties": {"sensor_data": {"type": "array"}}
            },
            max_latency_ms=100
        )
        
        validator.register_contract(
            module_name="processor",
            role=ModuleRole.DATA_PROCESSOR,
            input_schema={
                "type": "object",
                "properties": {"sensor_data": {"type": "array"}}
            },
            output_schema={
                "type": "object",
                "properties": {"processed_data": {"type": "array"}}
            },
            max_latency_ms=50,
            allowed_callers=["sensor"]
        )
        
        validator.register_contract(
            module_name="decision",
            role=ModuleRole.DECISION_ENGINE,
            input_schema={
                "type": "object",
                "properties": {"processed_data": {"type": "array"}}
            },
            output_schema={
                "type": "object",
                "properties": {"decision": {"type": "string"}}
            },
            max_latency_ms=25,
            allowed_callers=["processor"]
        )
        
        # Step 2: Add dependencies
        validator.add_dependency("sensor", "processor")
        validator.add_dependency("processor", "decision")
        
        # Step 3: Validate calls
        result1 = validator.validate_call(
            "sensor", "processor",
            {"sensor_data": [1, 2, 3]},
            latency_ms=40
        )
        assert result1.is_valid
        
        result2 = validator.validate_call(
            "processor", "decision",
            {"processed_data": [4, 5, 6]},
            latency_ms=20
        )
        assert result2.is_valid
        
        # Step 4: Check no circular dependencies
        cycles = validator.detect_circular_dependencies()
        assert len(cycles) == 0
        
        # Step 5: Set boundary rules
        validator.set_boundary_rule("sensor", ["python", "c"])
        validator.set_boundary_rule("processor", ["rust"])
        validator.set_boundary_rule("decision", ["python"])
        
        # Step 6: Generate report
        report = validator.generate_governance_report()
        assert report['total_contracts'] == 3
        assert report['total_calls'] == 2
        assert report['call_statistics']['success_rate'] == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
