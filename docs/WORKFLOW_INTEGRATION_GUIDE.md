# Workflow System Integration Guide

## Overview

This guide explains how the workflow system has been integrated into the SynergyMesh project structure, following the three-systems architecture (SynergyMesh Core, Structural Governance, Autonomous/Drone Stack).

## Quick Start

### Using Docker (Recommended)

Start the complete workflow system with all dependencies:

```bash
# Start workflow system with monitoring
docker-compose --profile workflow up -d

# View logs
docker-compose --profile workflow logs -f workflow-system

# Stop workflow system
docker-compose --profile workflow down
```

Services started:
- **workflow-system** (port 8081) - Main workflow engine
- **workflow-postgres** - PostgreSQL database
- **workflow-redis** - Redis cache
- **workflow-prometheus** (port 9090) - Metrics collection
- **workflow-grafana** (port 3010) - Metrics visualization

### Using Python Directly

```bash
# Install dependencies
pip install -r requirements-workflow.txt

# Run contract engine
python -m core.contract_engine --config config/system-manifest.yaml --stats

# Generate a contract
python tools/generators/contract_generator.py \
  --type workflow \
  --name my_workflow \
  --output /tmp/my_contract.yaml
```

## Architecture

### Three-Systems Integration

#### 1. SynergyMesh Core
Core engine components for workflow execution:

- **Contract Engine** (`core/contract_engine.py`)
  - Contract registry and versioning
  - Contract validation
  - Contract execution with timeout
  - Lifecycle management (deprecation, retirement)
  
- **Plugin System** (`core/plugin_system.py`)
  - Plugin discovery and loading
  - Plugin registry
  - Sandboxed execution
  
- **Multi-Layer Validator** (`core/validators/multi_layer_validator.py`)
  - Syntax validation
  - Semantic validation
  - Security validation
  - Performance validation
  - Compliance validation

#### 2. Structural Governance
Policy and contract definitions:

- **Behavior Contracts** (`governance/policies/workflow/behavior-contracts.yaml`)
  - AI governance contracts
  - Validation phase contracts
  - Deployment phase contracts
  - Plugin contracts
  - Self-improvement contracts
  
- **Validation Rules** (`governance/policies/workflow/validation-rules.yaml`)
  - Syntax rules
  - Semantic rules
  - Security rules

#### 3. Autonomous/Drone Stack
Automation tools and generators:

- **Contract Generator** (`tools/generators/contract_generator.py`)
  - Template-based contract generation
  - Service and workflow contracts

## Configuration

The workflow system is configured through `config/system-manifest.yaml` under the `workflow_system` section.

### Key Configuration Sections

#### Core Engine
```yaml
workflow_system:
  core_engine:
    contract_engine:
      enabled: true
      execution_mode: "strict"  # strict | permissive | audit
      registry:
        type: "distributed"
        storage_backend: "postgresql"
    plugin_system:
      enabled: true
      auto_discovery: true
```

#### AI Governance
```yaml
workflow_system:
  ai_governance:
    analysis_engine:
      enabled: true
      pattern_recognition:
        confidence_threshold: 0.85
      conflict_detection:
        enabled: true
      risk_assessment:
        enabled: true
```

#### Validation System
```yaml
workflow_system:
  validation_system:
    multi_layer:
      enabled: true
      fail_fast: false
      parallel_execution: true
      layers:
        - name: "syntax"
          severity: "critical"
        - name: "semantic"
          severity: "high"
        - name: "security"
          severity: "critical"
```

#### Pipeline Configuration
```yaml
workflow_system:
  pipeline:
    execution:
      mode: "orchestrated"
      concurrency: 10
      timeout_seconds: 3600
    quality_gates:
      - name: "code_quality"
        blocking: true
      - name: "security"
        blocking: true
```

## Usage Examples

### Python API

#### Initialize Contract Engine

```python
from core.contract_engine import (
    ContractEngine,
    ContractDefinition,
    ContractMetadata,
    ContractType
)

# Initialize engine
engine = ContractEngine({
    "execution_mode": "strict",
    "storage_backend": "memory",
    "cache_enabled": True,
    "timeout_seconds": 30
})

# Get statistics
stats = engine.get_statistics()
print(f"Total contracts: {stats['total_contracts']}")
```

#### Create and Register a Contract

```python
from datetime import datetime

# Create contract metadata
metadata = ContractMetadata(
    name="my_service_contract",
    version="1.0.0",
    contract_type=ContractType.SERVICE,
    description="My service contract",
    author="team@example.com"
)

# Create contract definition
contract = ContractDefinition(
    metadata=metadata,
    schema={
        "type": "object",
        "properties": {
            "input": {"type": "string"},
            "output": {"type": "string"}
        },
        "required": ["input"]
    },
    validation_rules=[
        {
            "type": "syntax",
            "condition": "input is not null"
        }
    ],
    execution_config={
        "timeout_seconds": 30,
        "retry_enabled": True
    },
    lifecycle_config={
        "deprecation_period_days": 90
    }
)

# Register contract
contract_id = engine.registry.register(contract)
print(f"Contract registered: {contract_id}")
```

#### Execute a Contract

```python
import asyncio

async def main():
    # Define execution handler
    async def service_handler(contract, input_data, context):
        # Process input
        result = input_data["input"].upper()
        return {"output": result}
    
    # Register handler
    engine.executor.register_handler(
        ContractType.SERVICE,
        service_handler
    )
    
    # Execute contract
    result = await engine.executor.execute(
        contract_id=contract_id,
        input_data={"input": "hello world"},
        context={"user": "test"}
    )
    
    print(f"Execution successful: {result.success}")
    print(f"Output: {result.output}")
    print(f"Duration: {result.duration_ms}ms")

# Run
asyncio.run(main())
```

#### Use Plugin System

```python
from core.plugin_system import PluginSystem

# Initialize plugin system
plugin_system = PluginSystem({
    "plugin_directories": [
        "/app/plugins",
        "./custom_plugins"
    ]
})

# Discover and load plugins
plugin_system.initialize()

# Get plugin registry
registry = plugin_system.loader.registry
plugins = registry.list_all()

for plugin in plugins:
    print(f"Plugin: {plugin.name} v{plugin.version}")
```

#### Use Multi-Layer Validator

```python
from core.validators.multi_layer_validator import MultiLayerValidator

# Initialize validator
validator = MultiLayerValidator({
    "fail_fast": False,
    "parallel_execution": True
})

# Add validation layers (custom validators)
class SyntaxValidator:
    def validate(self, data):
        from core.validators.multi_layer_validator import ValidationResult
        # Perform syntax validation
        return ValidationResult(
            layer="syntax",
            is_valid=True,
            errors=[],
            warnings=[]
        )

validator.add_validator(SyntaxValidator())

# Run validation
results = validator.validate({"code": "print('hello')"})

for result in results:
    print(f"Layer: {result.layer}, Valid: {result.is_valid}")
    if result.errors:
        print(f"  Errors: {result.errors}")
```

#### Generate Contracts

```python
from tools.generators.contract_generator import ContractGenerator

# Initialize generator
generator = ContractGenerator()

# Generate a workflow contract
contract = generator.generate(
    contract_type="workflow",
    name="data_processing_workflow",
    version="1.0.0",
    description="Process data through multiple stages",
    author="data-team@example.com"
)

# Save to file
generator.save(contract, "/tmp/workflow_contract.yaml")
print("Contract generated and saved")
```

### CLI Usage

#### Contract Engine

```bash
# Display engine statistics
python -m core.contract_engine --stats

# Load configuration
python -m core.contract_engine --config config/system-manifest.yaml --stats
```

#### Contract Generator

```bash
# Generate a service contract
python tools/generators/contract_generator.py \
  --type service \
  --name user_authentication \
  --output contracts/user_auth.yaml

# Generate a workflow contract
python tools/generators/contract_generator.py \
  --type workflow \
  --name data_pipeline \
  --output contracts/data_pipeline.yaml
```

## Testing

### Unit Tests

```bash
# Run contract engine tests
pytest tests/unit/test_contract_engine.py -v

# Run integration tests
pytest tests/integration/test_workflow_system.py -v
```

### Docker Integration Tests

```bash
# Build workflow image
docker-compose --profile workflow build workflow-system

# Start workflow system
docker-compose --profile workflow up -d

# Check service health
docker-compose --profile workflow ps

# View logs
docker-compose --profile workflow logs workflow-system

# Stop services
docker-compose --profile workflow down
```

## Monitoring and Observability

### Prometheus Metrics

Access Prometheus at `http://localhost:9090` when running with Docker.

Key metrics:
- `contract_executions_total` - Total contract executions
- `contract_execution_duration_seconds` - Execution duration histogram
- `contract_validation_errors_total` - Validation errors
- `plugin_loads_total` - Plugin loads
- `validation_layer_duration_seconds` - Validation layer duration

### Grafana Dashboards

Access Grafana at `http://localhost:3010` (username: admin, password: admin).

Pre-configured dashboard: Workflow System Overview

### Logs

Structured JSON logging is enabled by default:

```json
{
  "timestamp": "2025-12-09T01:00:00.000Z",
  "level": "info",
  "message": "Contract registered",
  "service": "contract_engine",
  "contract_id": "abc-123",
  "trace_id": "xyz-789"
}
```

## Security

### Authentication & Authorization

The workflow system supports OAuth2 authentication and RBAC authorization:

```yaml
workflow_system:
  security:
    authentication:
      enabled: true
      provider: "oauth2"
      token_expiry_seconds: 3600
    authorization:
      enabled: true
      model: "rbac"
      rbac:
        roles:
          - name: "admin"
            permissions: ["*"]
          - name: "developer"
            permissions: ["deploy:dev", "deploy:staging", "view:*"]
```

### Encryption

- **At Rest:** AES-256-GCM
- **In Transit:** TLS 1.3 with mTLS
- **Secrets:** Vault-based secret management

### Vulnerability Scanning

Integrated security validation includes:
- OWASP Top 10 checks
- Dependency vulnerability scanning (NVD database)
- Code analysis with CodeQL
- Container scanning with Trivy

## Troubleshooting

### Common Issues

#### Contract Engine Won't Start

```bash
# Check configuration
python -m core.contract_engine --config config/system-manifest.yaml

# Verify Python dependencies
pip install -r requirements-workflow.txt

# Check logs
docker-compose --profile workflow logs workflow-system
```

#### Database Connection Issues

```bash
# Verify PostgreSQL is running
docker-compose --profile workflow ps workflow-postgres

# Check PostgreSQL logs
docker-compose --profile workflow logs workflow-postgres

# Test connection
docker-compose --profile workflow exec workflow-postgres \
  psql -U workflow -d workflow -c "SELECT 1"
```

#### Plugin Loading Failures

```bash
# Check plugin directories exist
ls -la /app/plugins /app/core/plugins

# Verify plugin signatures (if enabled)
# Check plugin manifest files
```

### Debug Mode

Enable debug logging:

```bash
# Docker
docker-compose --profile workflow up -d
docker-compose --profile workflow exec workflow-system \
  sh -c "export LOG_LEVEL=debug && python -m core.contract_engine"

# Python
LOG_LEVEL=debug python -m core.contract_engine --config config/system-manifest.yaml
```

## Development

### Contributing

When adding new workflow components:

1. **Follow naming conventions:** `snake_case` for Python, `camelCase` for TypeScript
2. **Add type hints:** All Python functions should have type annotations
3. **Write tests:** Minimum 80% code coverage
4. **Update documentation:** Include docstrings and update relevant guides
5. **Run linters:** `pylint`, `mypy`, `flake8`

### Project Structure

```
SynergyMesh/
├── core/
│   ├── contract_engine.py          # Contract engine (883 lines)
│   ├── plugin_system.py            # Plugin system (77 lines)
│   └── validators/
│       └── multi_layer_validator.py # Multi-layer validator (47 lines)
├── governance/
│   └── policies/
│       └── workflow/
│           ├── behavior-contracts.yaml    # Behavior contracts
│           └── validation-rules.yaml      # Validation rules
├── tools/
│   └── generators/
│       └── contract_generator.py   # Contract generator (69 lines)
├── deployment/
│   └── docker/
│       └── Dockerfile.workflow     # Workflow Docker image
├── config/
│   ├── system-manifest.yaml        # Main configuration (with workflow_system section)
│   └── unified-config-index.yaml   # Configuration index
└── docs/
    └── WORKFLOW_INTEGRATION_GUIDE.md  # This file
```

### Adding New Validators

```python
from core.validators.multi_layer_validator import ValidationResult

class CustomValidator:
    def validate(self, data):
        errors = []
        warnings = []
        
        # Your validation logic here
        if some_condition:
            errors.append("Validation error message")
        
        return ValidationResult(
            layer="custom",
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

# Register validator
from core.validators.multi_layer_validator import MultiLayerValidator
validator = MultiLayerValidator(config)
validator.add_validator(CustomValidator())
```

### Creating Custom Plugins

```python
from core.plugin_system import Plugin

class MyCustomPlugin(Plugin):
    def __init__(self):
        super().__init__("my_plugin", "1.0.0")
    
    def initialize(self) -> bool:
        # Plugin initialization logic
        return True
    
    def execute(self, context):
        # Plugin execution logic
        return {"result": "success"}
    
    def cleanup(self):
        # Plugin cleanup logic
        pass
```

## References

- **Main Documentation:** [README.md](../README.md)
- **Integration Summary:** [WORKFLOW_INTEGRATION_SUMMARY.md](../WORKFLOW_INTEGRATION_SUMMARY.md)
- **API Reference:** [docs/API_REFERENCE.md](API_REFERENCE.md)
- **Deployment Guide:** [docs/DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Workflow System Details:** [docs/WORKFLOW_SYSTEM.md](WORKFLOW_SYSTEM.md)

## Support

For issues, questions, or contributions:

- **GitHub Issues:** https://github.com/SynergyMesh/SynergyMesh/issues
- **Documentation:** https://docs.synergymesh.io
- **Community:** https://community.synergymesh.io

---

**Last Updated:** 2025-12-09
**Version:** 2.0.0
