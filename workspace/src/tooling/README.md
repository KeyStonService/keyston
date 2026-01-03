# Workspace Tooling

Development tools and utilities for the workspace layer.

## Important Rules

### 1. Tools vs. Validators

**CRITICAL DISTINCTION:**

- **Authoritative Validators** (controlplane/baseline/validation/): Single source of truth for validation
- **Development Tools** (workspace/src/tooling/): Convenience wrappers that CALL validators

### 2. What Goes Here

**Allowed:**

- Development utilities that call controlplane validators
- Build tools and scripts
- Testing utilities
- Linting and formatting tools
- CI/CD helper scripts
- Development workflow automation

**NOT Allowed:**

- Governance validators (must be in controlplane/baseline/validation/)
- Specifications (must be in controlplane/baseline/specifications/)
- Registries (must be in controlplane/baseline/registries/)
- Any tool that replaces or duplicates controlplane validators

### 3. Tool Design Principles

All tools in this directory must follow these principles:

1. **Call, Don't Replace**: Tools must call controlplane validators, not implement their own validation logic
2. **Convenience Only**: Tools provide convenient interfaces but defer to authoritative sources
3. **No Truth**: Tools do not define governance truth; they only consume it
4. **Evidence in Overlay**: Tool outputs must go to workspace/runtime/ or controlplane/overlay/evidence/

## Available Tools

### validate.py

Development validation tool that wraps the authoritative controlplane validator.

**Usage:**

```bash
# Run full validation suite
python workspace/src/tooling/validate.py all

# Validate naming conventions
python workspace/src/tooling/validate.py naming root.config.yaml file
python workspace/src/tooling/validate.py naming controlplane directory
python workspace/src/tooling/validate.py naming v1.0.0 version

# Validate namespace
python workspace/src/tooling/validate.py namespace machinenativeops

# Validate URN
python workspace/src/tooling/validate.py urn urn:machinenativeops:module:core-validator:v1.0.0

# Validate path
python workspace/src/tooling/validate.py path controlplane/baseline/config/root.config.yaml
```

**What it does:**

- Calls `controlplane/baseline/validation/validate-root-specs.py` for full validation
- Calls individual validators in `controlplane/baseline/validation/validators/` for specific checks
- Provides convenient CLI interface for development workflow

**What it does NOT do:**

- Does NOT implement its own validation logic
- Does NOT replace controlplane validators
- Does NOT define governance rules

## Architecture

```
workspace/src/tooling/          # Development tools (this directory)
├── validate.py                 # Wrapper that calls controlplane validators
├── lint/                       # Code linting tools
├── format/                     # Code formatting tools
└── tests/                      # Testing utilities

controlplane/baseline/validation/  # Authoritative validators (SSOT)
├── validate-root-specs.py      # Main validator (authoritative)
├── validators/                 # Sub-validators (authoritative)
│   ├── validate_naming.py
│   ├── validate_namespace.py
│   ├── validate_urn.py
│   └── validate_paths.py
└── gate-root-specs.yml         # Gate rules (authoritative)
```

## Workflow

### Development Workflow

1. Developer makes changes in workspace
2. Developer runs `workspace/src/tooling/validate.py all`
3. Tool calls `controlplane/baseline/validation/validate-root-specs.py`
4. Validator runs all checks and generates evidence
5. Developer reviews results and fixes issues

### CI/CD Workflow

1. CI/CD pipeline runs authoritative validator directly
2. `controlplane/baseline/validation/validate-root-specs.py` is executed
3. Evidence is generated in `controlplane/overlay/evidence/`
4. Pipeline passes/fails based on validation results

## Adding New Tools

When adding new tools to this directory:

1. **Identify the authoritative source**: What controlplane validator/spec does this tool use?
2. **Design as wrapper**: Tool should call the authoritative source, not duplicate it
3. **Document dependencies**: Clearly state which controlplane components the tool depends on
4. **Handle errors gracefully**: If authoritative source is missing, fail with clear error message
5. **Output to correct location**: Logs go to workspace/runtime/logs/, evidence goes to controlplane/overlay/evidence/

## Examples

### Good Tool Design ✓

```python
# workspace/src/tooling/my-tool.py
from pathlib import Path

# Path to authoritative validator
VALIDATOR = Path(__file__).parent.parent.parent.parent / "controlplane" / "baseline" / "validation" / "validate-root-specs.py"

def run_validation():
    """Call the authoritative validator."""
    if not VALIDATOR.exists():
        raise FileNotFoundError(f"Authoritative validator not found: {VALIDATOR}")
    
    # Call the validator
    subprocess.run([sys.executable, str(VALIDATOR)])
```

### Bad Tool Design ✗

```python
# workspace/src/tooling/my-tool.py (WRONG!)

def validate_naming(name):
    """Implement our own validation logic."""  # ✗ WRONG!
    # This duplicates controlplane validator logic
    if not re.match(r'^[a-z][a-z0-9-]*$', name):
        return False
    return True
```

## Testing

Tools should be tested to ensure they correctly call authoritative validators:

```python
def test_validate_tool():
    """Test that validate.py calls controlplane validator."""
    result = subprocess.run(["python", "workspace/src/tooling/validate.py", "all"])
    
    # Check that it called the authoritative validator
    assert result.returncode in [0, 1]  # 0 = pass, 1 = fail
    
    # Check that evidence was generated by authoritative validator
    assert Path("controlplane/overlay/evidence/validation.report.json").exists()
```

## Maintenance

When controlplane validators are updated:

1. Tools automatically use the new validator logic (no changes needed)
2. Tools may need CLI updates if validator interface changes
3. Documentation should be updated to reflect new capabilities

## Support

For questions about:

- **Tool usage**: See this README
- **Validation rules**: See `controlplane/baseline/specifications/`
- **Validator implementation**: See `controlplane/baseline/validation/`
- **Governance policies**: See `controlplane/baseline/config/`
