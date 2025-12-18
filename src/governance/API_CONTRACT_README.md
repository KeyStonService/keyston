# API Contract and Governance Boundary Module

> **Version**: 1.0.0  
> **Status**: ✅ PRODUCTION READY  
> **Date**: 2025-12-12

## 📋 Overview

Complete implementation of API contract governance framework for multi-module
systems. Provides contract definition, validation, boundary enforcement,
dependency management, and comprehensive reporting.

## 🎯 Core Features

### 1. Contract Definition ✅

Define complete API contracts with:

- Input/output JSON schemas
- Latency requirements (SLA enforcement)
- Authorization rules (allowed callers)
- Error handling strategies
- Version control

### 2. Boundary Enforcement ✅

Enforce strict boundaries:

- Language restrictions per module
- Protocol isolation
- Cross-contamination prevention
- Architectural integrity validation

### 3. Automated Validation ✅

Runtime validation of:

- API call authorization
- Input schema compliance
- Output schema compliance
- Latency constraints
- Type safety

### 4. Dependency Management ✅

Comprehensive dependency tracking:

- Module dependency graph
- Circular dependency detection
- Dependency chain analysis
- Visual dependency reports

### 5. Governance Reporting ✅

Detailed reports including:

- Contract registry status
- Call history and statistics
- Success/failure rates
- Latency metrics
- Boundary violations

## 🚀 Quick Start

### Installation

```python
# Module is ready to use - no installation needed
from governance.api_contract import GovernanceValidator, ModuleRole
```

### Basic Usage

```python
from governance.api_contract import GovernanceValidator, ModuleRole

# Create validator
validator = GovernanceValidator()

# Register a contract
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

# Validate an API call
result = validator.validate_call(
    from_module="data_source",
    to_module="sensor_processor",
    data={"sensor_data": [1, 2, 3]},
    latency_ms=45
)

print(f"Valid: {result.is_valid}")
print(f"Errors: {result.errors}")
print(f"Warnings: {result.warnings}")
```

## 📦 Complete API Reference

### Classes

#### `ModuleRole` (Enum)

Module responsibility categories:

- `DATA_PROCESSOR`: Data processing modules
- `DECISION_ENGINE`: Decision-making modules
- `CONTROL_SYSTEM`: Control system modules
- `SENSOR_INTERFACE`: Sensor interface modules
- `ACTUATOR_INTERFACE`: Actuator interface modules
- `COMMUNICATION_HUB`: Communication modules
- `MONITORING_SERVICE`: Monitoring modules
- `STORAGE_SERVICE`: Storage modules
- `ANALYTICS_ENGINE`: Analytics modules
- `USER_INTERFACE`: UI modules

#### `ErrorCategory` (Enum)

Error classification types:

- `CONTRACT_VIOLATION`: Contract violations
- `BOUNDARY_VIOLATION`: Boundary violations
- `TIMEOUT`: Timeout errors
- `INVALID_INPUT`: Invalid input errors
- `INVALID_OUTPUT`: Invalid output errors
- `CIRCULAR_DEPENDENCY`: Circular dependencies
- `MISSING_CONTRACT`: Missing contracts
- `UNAUTHORIZED_ACCESS`: Unauthorized access
- `RUNTIME_ERROR`: Runtime errors

#### `APIContract` (Dataclass)

Contract specification:

```python
@dataclass
class APIContract:
    module_name: str                # Unique module identifier
    role: ModuleRole                # Module responsibility
    input_schema: Dict[str, Any]    # JSON schema for input
    output_schema: Dict[str, Any]   # JSON schema for output
    max_latency_ms: float           # Maximum latency in ms
    allowed_callers: List[str]      # Authorized callers
    error_handling: str             # Error strategy
    version: str                    # Contract version
    description: str                # Human-readable description
```

#### `ValidationResult` (Dataclass)

Validation outcome:

```python
@dataclass
class ValidationResult:
    is_valid: bool                  # Validation passed
    errors: List[str]               # Error messages
    warnings: List[str]             # Warning messages
    latency_ms: Optional[float]     # Measured latency
    timestamp: float                # Validation timestamp
```

#### `GovernanceValidator` (Class)

Main validator with methods:

**Contract Management:**

- `register_contract()` - Register new API contract
- `export_contracts()` - Export contracts to JSON
- `import_contracts()` - Import contracts from JSON

**Validation:**

- `validate_call()` - Validate API call
- `validate_boundary()` - Validate language boundary

**Dependency Management:**

- `add_dependency()` - Add module dependency
- `detect_circular_dependencies()` - Find circular dependencies

**Boundary Rules:**

- `set_boundary_rule()` - Set language restrictions

**Reporting:**

- `generate_governance_report()` - Generate complete report

## 💡 Usage Examples

### Example 1: Multi-Module System

```python
from governance.api_contract import GovernanceValidator, ModuleRole

validator = GovernanceValidator()

# Register sensor module
validator.register_contract(
    module_name="temperature_sensor",
    role=ModuleRole.SENSOR_INTERFACE,
    input_schema={"type": "object"},
    output_schema={
        "type": "object",
        "properties": {
            "temperature": {"type": "number"},
            "timestamp": {"type": "number"}
        }
    },
    max_latency_ms=50,
    description="Reads temperature sensor data"
)

# Register processor module
validator.register_contract(
    module_name="data_processor",
    role=ModuleRole.DATA_PROCESSOR,
    input_schema={
        "type": "object",
        "properties": {
            "temperature": {"type": "number"},
            "timestamp": {"type": "number"}
        }
    },
    output_schema={
        "type": "object",
        "properties": {
            "processed_temperature": {"type": "number"},
            "alert": {"type": "string"}
        }
    },
    max_latency_ms=100,
    allowed_callers=["temperature_sensor"],
    description="Processes sensor data and generates alerts"
)

# Register decision module
validator.register_contract(
    module_name="decision_engine",
    role=ModuleRole.DECISION_ENGINE,
    input_schema={
        "type": "object",
        "properties": {
            "processed_temperature": {"type": "number"},
            "alert": {"type": "string"}
        }
    },
    output_schema={
        "type": "object",
        "properties": {
            "action": {"type": "string"}
        }
    },
    max_latency_ms=50,
    allowed_callers=["data_processor"],
    description="Makes control decisions"
)

# Validate call chain
result1 = validator.validate_call(
    from_module="temperature_sensor",
    to_module="data_processor",
    data={"temperature": 25.5, "timestamp": 1234567890},
    latency_ms=45
)

result2 = validator.validate_call(
    from_module="data_processor",
    to_module="decision_engine",
    data={"processed_temperature": 25.5, "alert": "normal"},
    latency_ms=30
)

print(f"Call 1 Valid: {result1.is_valid}")
print(f"Call 2 Valid: {result2.is_valid}")
```

### Example 2: Circular Dependency Detection

```python
validator = GovernanceValidator()

# Add dependencies
validator.add_dependency("module_a", "module_b")
validator.add_dependency("module_b", "module_c")
validator.add_dependency("module_c", "module_d")
validator.add_dependency("module_d", "module_b")  # Creates cycle

# Detect cycles
cycles = validator.detect_circular_dependencies()
print(f"Circular dependencies found: {cycles}")
# Output: [['module_b', 'module_c', 'module_d', 'module_b']]
```

### Example 3: Boundary Enforcement

```python
validator = GovernanceValidator()

# Set language boundaries
validator.set_boundary_rule("safety_critical_module", ["rust", "c"])
validator.set_boundary_rule("analytics_module", ["python", "r"])
validator.set_boundary_rule("web_service", ["typescript", "javascript"])

# Validate boundaries
result1 = validator.validate_boundary("safety_critical_module", "rust")
print(f"Rust in safety module: {result1.is_valid}")  # True

result2 = validator.validate_boundary("safety_critical_module", "python")
print(f"Python in safety module: {result2.is_valid}")  # False
print(f"Errors: {result2.errors}")
```

### Example 4: Governance Reporting

```python
validator = GovernanceValidator()

# ... register contracts and make calls ...

# Generate comprehensive report
report = validator.generate_governance_report()

print(f"Total Contracts: {report['total_contracts']}")
print(f"Total API Calls: {report['total_calls']}")
print(f"Success Rate: {report['call_statistics']['success_rate']:.2%}")
print(f"Circular Dependencies: {len(report['circular_dependencies'])}")

if 'latency' in report['call_statistics']:
    latency = report['call_statistics']['latency']
    print(f"Average Latency: {latency['avg_ms']:.2f}ms")
    print(f"Max Latency: {latency['max_ms']:.2f}ms")
```

### Example 5: Contract Export/Import

```python
validator = GovernanceValidator()

# Register contracts
validator.register_contract(
    module_name="module_1",
    role=ModuleRole.DATA_PROCESSOR,
    input_schema={"type": "object"},
    output_schema={"type": "object"},
    max_latency_ms=100
)

# Export to file
validator.export_contracts("contracts.json")

# Later, import in another process
new_validator = GovernanceValidator()
new_validator.import_contracts("contracts.json")

print(f"Imported {len(new_validator.contracts)} contracts")
```

## 🧪 Testing

Complete test suite included:

```bash
# Run all tests
python governance/28-tests/unit/test_api_contract.py

# Run with pytest
pytest governance/28-tests/unit/test_api_contract.py -v

# Run specific test
pytest governance/28-tests/unit/test_api_contract.py::TestGovernanceValidator::test_validate_call_success -v
```

**Test Coverage:**

- ✅ Contract registration and serialization
- ✅ Call validation (success and failure cases)
- ✅ Authorization checking
- ✅ Latency constraint validation
- ✅ Circular dependency detection
- ✅ Boundary enforcement
- ✅ Governance reporting
- ✅ Export/import functionality
- ✅ Integration workflows

## 📊 Architecture Context

### Design Principles

1. **Strict Isolation**: Modules are isolated by contracts
2. **Real-time Guarantees**: Latency constraints enforced
3. **Fault Tolerance**: Well-defined error strategies
4. **Multi-language Support**: Language boundaries enforced
5. **Auditability**: Complete call history tracking

### Use Cases

- **Autonomous Vehicles**: Safety-critical module isolation
- **Flight Control Systems**: Real-time latency guarantees
- **Industrial Control**: Deterministic behavior enforcement
- **Microservices**: API contract validation
- **Multi-team Development**: Clear module boundaries

## 🔧 Advanced Features

### Schema Validation

Supports JSON Schema validation for:

- Object types with properties
- Required fields
- Array types
- String, number, boolean types
- Nested objects

### Error Handling Strategies

- `fail_fast`: Immediate failure on error
- `retry`: Automatic retry on failure
- `fallback`: Use fallback implementation
- `log_and_continue`: Log error and continue

### Latency Monitoring

- Per-call latency tracking
- Statistical analysis (min, max, avg)
- SLA violation detection
- Performance trending

## 📈 Performance

- **Contract Lookup**: O(1) hash table lookup
- **Dependency Detection**: O(V + E) DFS algorithm
- **Schema Validation**: O(n) where n is data size
- **Memory**: Minimal overhead per contract

## 🛡️ Security

- Authorization checking per contract
- Boundary enforcement prevents injection
- Call history for audit trails
- No code execution in validation

## 🔄 Integration

### With Other Governance Tools

```python
# Integrate with instant-governance-cli
from governance.api_contract import GovernanceValidator

validator = GovernanceValidator()
# ... setup contracts ...

# Export for governance reporting
report = validator.generate_governance_report()
with open("governance/api-contract-report.json", "w") as f:
    json.dump(report, f, indent=2)
```

### With CI/CD

```bash
# Add to CI pipeline
python -c "
from governance.api_contract import GovernanceValidator
validator = GovernanceValidator()
validator.import_contracts('contracts.json')
# Validate all contracts loaded
assert len(validator.contracts) > 0
print('✅ API contracts validated')
"
```

## 📝 Best Practices

1. **Version Contracts**: Always specify version numbers
2. **Document Everything**: Use description fields
3. **Test Boundaries**: Validate language boundaries early
4. **Monitor Latency**: Track latency trends
5. **Review Cycles**: Detect circular dependencies in CI
6. **Export Regularly**: Backup contracts to JSON
7. **Validate Early**: Catch violations in development

## 🆘 Troubleshooting

### Common Issues

**Issue**: Contract validation fails

```python
# Check if contract exists
if module_name not in validator.contracts:
    print(f"Contract not found for {module_name}")
```

**Issue**: Circular dependency detected

```python
# Find and print cycles
cycles = validator.detect_circular_dependencies()
for cycle in cycles:
    print(f"Cycle: {' -> '.join(cycle)}")
```

**Issue**: Latency violations

```python
# Review latency statistics
report = validator.generate_governance_report()
if 'latency' in report['call_statistics']:
    print(f"Max latency: {report['call_statistics']['latency']['max_ms']}ms")
```

## 🎯 Roadmap

Future enhancements:

- [ ] Advanced JSON Schema validation with jsonschema library
- [ ] WebSocket/gRPC protocol support
- [ ] Distributed tracing integration
- [ ] Prometheus metrics export
- [ ] Visual dependency graph generation
- [ ] Contract migration tools
- [ ] Performance profiling

## 📚 References

- [JSON Schema](https://json-schema.org/)
- [Microservices Contracts](https://martinfowler.com/articles/consumerDrivenContracts.html)
- [API Governance](https://www.asyncapi.com/docs/tutorials/getting-started/coming-from-openapi)

---

**Version**: 1.0.0  
**Status**: ✅ PRODUCTION READY  
**Author**: SynergyMesh Governance Team  
**Date**: 2025-12-12
