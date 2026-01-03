# Controlplane Usage Guide

## Overview

The Controlplane architecture implements a **Baseline + Overlay + Active** design pattern that separates immutable governance truth from runtime state, enabling self-healing without polluting the source of truth.

## Architecture Components

### 1. Baseline (Immutable Governance Truth)

**Location**: `controlplane/baseline/`  
**Access**: Read-only  
**Purpose**: Contains the canonical, immutable governance configuration

**Structure**:

```
baseline/
├── config/              # Core configuration files (10 files)
├── specifications/      # Formal specifications (5 files)
├── registries/          # Component registries (2 files)
├── integration/         # Integration rules (1 file)
├── validation/          # Validation system (3 files)
└── documentation/       # Architecture documentation
```

**Key Principle**: Baseline files are **never modified at runtime**. All changes require explicit governance approval and version control.

### 2. Overlay (Writable Runtime State)

**Location**: `controlplane/overlay/`  
**Access**: Read-write  
**Purpose**: Stores runtime state, self-healing corrections, and operational evidence

**Structure**:

```
overlay/
├── config/              # Runtime configuration extensions
├── evidence/            # Validation evidence and reports
├── runtime/             # Runtime state data
└── logs/                # Operational logs
```

**Key Principle**: Self-healing operations **only write to overlay**. This preserves baseline integrity while allowing system adaptation.

### 3. Active (Synthesized View)

**Location**: `controlplane/active/`  
**Access**: Read-only  
**Purpose**: Provides a unified, read-only view of baseline + overlay

**Key Principle**: Active view is **synthesized on-demand** and never directly modified.

## Quick Start

### Running Validation

Execute the validation system to verify baseline integrity:

```bash
# Run validation
python3 controlplane/baseline/validation/validate-root-specs.py

# Check validation results
cat controlplane/overlay/evidence/validation/validation.report.json

# View human-readable report
cat controlplane/overlay/evidence/validation/validation.report.md
```

### Accessing Configuration

```bash
# Source environment variables
source root.env.sh

# Access baseline configuration
cat $MACHINENATIVEOPS_BASELINE_CONFIG/root.config.yaml

# Access overlay evidence
ls -la $MACHINENATIVEOPS_OVERLAY_EVIDENCE/

# View validation manifest
cat $MACHINENATIVEOPS_OVERLAY_EVIDENCE/validation/controlplane.manifest.json
```

### Environment Variables

The following environment variables are available after sourcing `root.env.sh`:

**Controlplane Paths**:

- `MACHINENATIVEOPS_CONTROLPLANE`: Root controlplane directory
- `MACHINENATIVEOPS_BASELINE`: Baseline directory
- `MACHINENATIVEOPS_OVERLAY`: Overlay directory
- `MACHINENATIVEOPS_ACTIVE`: Active view directory

**Baseline Subdirectories**:

- `MACHINENATIVEOPS_BASELINE_CONFIG`: Baseline configuration
- `MACHINENATIVEOPS_BASELINE_SPECS`: Baseline specifications
- `MACHINENATIVEOPS_BASELINE_REGISTRIES`: Baseline registries
- `MACHINENATIVEOPS_BASELINE_INTEGRATION`: Integration rules
- `MACHINENATIVEOPS_BASELINE_VALIDATION`: Validation system
- `MACHINENATIVEOPS_BASELINE_DOCS`: Documentation

**Overlay Subdirectories**:

- `MACHINENATIVEOPS_OVERLAY_CONFIG`: Runtime configuration
- `MACHINENATIVEOPS_OVERLAY_EVIDENCE`: Validation evidence
- `MACHINENATIVEOPS_OVERLAY_RUNTIME`: Runtime state
- `MACHINENATIVEOPS_OVERLAY_LOGS`: Operational logs

**Validation Tools**:

- `MACHINENATIVEOPS_VALIDATOR`: Validation script path
- `MACHINENATIVEOPS_VALIDATION_GATE`: Validation gate config
- `MACHINENATIVEOPS_VALIDATION_VECTORS`: Test vectors

## Common Operations

### 1. Viewing Baseline Configuration

```bash
# List all baseline config files
ls -la controlplane/baseline/config/

# View specific configuration
cat controlplane/baseline/config/root.config.yaml
cat controlplane/baseline/config/root.governance.yaml
cat controlplane/baseline/config/root.trust.yaml
```

### 2. Checking Validation Status

```bash
# View latest validation report
cat controlplane/overlay/evidence/validation/validation.report.json | jq '.pass'

# View validation summary
cat controlplane/overlay/evidence/validation/validation.report.json | jq '.summary'

# Check specific stage results
cat controlplane/overlay/evidence/validation/validation.report.json | jq '.stages.structural'
```

### 3. Reviewing Evidence

```bash
# List all evidence
find controlplane/overlay/evidence -type f

# View validation manifest
cat controlplane/overlay/evidence/validation/controlplane.manifest.json

# Read markdown report
less controlplane/overlay/evidence/validation/validation.report.md
```

### 4. Extending Configuration (Self-Healing)

When the system needs to adapt, it writes to overlay:

```bash
# Create overlay configuration extension
cat > controlplane/overlay/config/custom-extension.yaml << EOF
metadata:
  name: custom-extension
  type: overlay
  extends: baseline/config/root.config.yaml

configuration:
  custom_setting: value
EOF

# Validate the extension
python3 controlplane/baseline/validation/validate-root-specs.py
```

## Validation System

### Validation Stages

The validation system executes five stages:

1. **Structural Validation**: Verifies directory structure and file existence
2. **Syntax Validation**: Checks YAML syntax and structure
3. **Semantic Validation**: Validates logical consistency
4. **Integration Validation**: Verifies cross-component integration
5. **Security Validation**: Checks security properties

### Validation Reports

After validation, three artifacts are generated:

1. **validation.report.json**: Machine-readable validation results
2. **validation.report.md**: Human-readable markdown report
3. **controlplane.manifest.json**: Validation manifest with metadata

### Success Criteria

Validation passes when:

- All 50 checks pass across all stages
- No critical failures detected
- Evidence successfully generated
- Report shows `"pass": true`

## Integration with Bootstrap

The controlplane is integrated with the root bootstrap process:

### root.bootstrap.yaml

```yaml
spec:
  controlplane:
    enabled: true
    baseline_path: controlplane/baseline
    overlay_path: controlplane/overlay
    active_path: controlplane/active
    validation:
      enabled: true
      validator: controlplane/baseline/validation/validate-root-specs.py
      on_failure: halt_system
```

### root.fs.map

Filesystem mappings include:

- `controlplane_baseline`: Read-only baseline directory
- `controlplane_overlay`: Read-write overlay directory
- `controlplane_active`: Read-only active view

### root.env.sh

Environment variables provide easy access to all controlplane paths and tools.

## Best Practices

### DO ✅

1. **Always validate after changes**: Run validation after any configuration changes
2. **Use overlay for runtime state**: Write all runtime data to overlay
3. **Review evidence regularly**: Check validation reports and evidence
4. **Follow naming conventions**: Use consistent naming from baseline policies
5. **Document extensions**: Document any overlay extensions clearly
6. **Version control baseline**: Keep baseline under strict version control
7. **Archive evidence**: Maintain evidence archives for audit trails

### DON'T ❌

1. **Never modify baseline at runtime**: Baseline is immutable
2. **Don't write to active**: Active view is read-only
3. **Don't bypass validation**: Always run validation gates
4. **Don't ignore validation failures**: Address failures immediately
5. **Don't pollute baseline**: Keep runtime state in overlay
6. **Don't skip evidence generation**: Always generate evidence
7. **Don't modify validation system**: Validation is part of baseline

## Troubleshooting

### Validation Failures

If validation fails:

1. Check the validation report:

   ```bash
   cat controlplane/overlay/evidence/validation/validation.report.json | jq '.stages[] | select(.passed == false)'
   ```

2. Review specific failed checks:

   ```bash
   cat controlplane/overlay/evidence/validation/validation.report.md
   ```

3. Fix the issues and re-run validation:

   ```bash
   python3 controlplane/baseline/validation/validate-root-specs.py
   ```

### Missing Files

If files are missing:

1. Check the structural validation stage
2. Verify all 19 baseline files exist:
   - 10 config files
   - 5 specification files
   - 2 registry files
   - 1 integration file
   - 1 documentation file

3. Recreate missing files from templates

### Permission Issues

If permission errors occur:

1. Verify baseline is read-only (in production)
2. Verify overlay is writable
3. Check filesystem permissions in root.fs.map

## Advanced Topics

### Custom Validation Rules

To add custom validation rules:

1. Edit `controlplane/baseline/validation/validate-root-specs.py`
2. Add new validation methods
3. Update validation stages
4. Add test vectors to `root.validation.vectors.yaml`
5. Test thoroughly before deployment

### Overlay Extensions

To create overlay extensions:

1. Create extension file in `controlplane/overlay/config/`
2. Reference baseline configuration
3. Add only delta/extension data
4. Run validation to verify
5. Document the extension purpose

### Evidence Management

Evidence is automatically generated and stored in:

- `controlplane/overlay/evidence/validation/`

Manage evidence:

```bash
# Archive old evidence
tar -czf evidence-$(date +%Y%m%d).tar.gz controlplane/overlay/evidence/

# Clean old evidence (keep last 90 days)
find controlplane/overlay/evidence -type f -mtime +90 -delete
```

## Security Considerations

### Immutability Enforcement

In production:

- Baseline directory should be mounted read-only
- Filesystem permissions enforce immutability
- Version control tracks all baseline changes

### Trust Boundaries

- **Baseline → Overlay**: One-way reference only
- **Overlay → Active**: Synthesis only, no direct modification
- **Active → Runtime**: Read-only view

### Audit Trail

All operations generate evidence:

- Validation reports
- Integrity checksums
- Provenance tracking
- Change logs

## Support and Resources

### Documentation

- **Architecture**: `controlplane/baseline/documentation/BASELINE_ARCHITECTURE.md`
- **Usage Guide**: This file
- **Validation Gate**: `controlplane/baseline/validation/gate-root-specs.yml`

### Tools

- **Validator**: `controlplane/baseline/validation/validate-root-specs.py`
- **Bootstrap**: `root.bootstrap.yaml`
- **Environment**: `root.env.sh`
- **Filesystem Map**: `root.fs.map`

### Getting Help

For issues or questions:

1. Review validation reports
2. Check documentation
3. Examine evidence logs
4. Consult architecture documentation

---

**Version**: 1.0.0  
**Last Updated**: 2025-12-23  
**Maintained By**: MachineNativeOps Root Namespace Governance
