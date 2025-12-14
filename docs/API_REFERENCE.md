# API Reference | API 參考

## Contract Engine API

### ContractRegistry

#### register(contract: ContractDefinition) -> str
Register a new contract.

**Parameters:**
- `contract`: Contract definition to register

**Returns:** Contract ID

**Example:**
```python
from core.contract_engine import ContractRegistry, ContractDefinition, ContractMetadata, ContractType

registry = ContractRegistry()
contract = ContractDefinition(
    metadata=ContractMetadata(
        name="my_contract",
        version="1.0.0",
        contract_type=ContractType.SERVICE,
        description="My service contract",
        author="developer"
    ),
    schema={},
    validation_rules=[],
    execution_config={},
    lifecycle_config={}
)
contract_id = registry.register(contract)
```

### ContractValidator

#### validate_definition(contract: ContractDefinition) -> ValidationResult
Validate contract definition.

### ContractExecutor

#### execute(contract_id: str, input_data: Dict, context: Dict) -> ExecutionResult
Execute a contract.

## Validation System API

### MultiLayerValidator

#### validate(data: Dict) -> List[ValidationResult]
Run all validation layers.

### SyntaxValidator

#### validate(data: Dict) -> ValidationResult
Validate syntax.

### SecurityValidator

#### validate(data: Dict) -> ValidationResult
Validate security.

For complete API documentation, see source code docstrings.
