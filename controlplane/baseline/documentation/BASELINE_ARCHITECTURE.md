# Baseline Architecture Documentation

## Overview

The **baseline** directory contains the immutable governance truth for the root namespace. This architecture implements a strict separation between governance (baseline) and runtime state (overlay), enabling self-healing without polluting the source of truth.

## Architecture Principles

### 1. Immutability

- **Baseline files are read-only at runtime**
- Changes require explicit governance process
- Filesystem permissions enforce immutability
- No runtime modification allowed

### 2. Separation of Concerns

```
baseline/     → Governance truth (immutable)
overlay/      → Runtime state (writable)
active/       → Synthesized view (read-only)
```

### 3. Evidence-Based Validation

- All operations produce evidence
- Evidence stored in overlay/evidence/
- Validation reports track compliance
- Audit trail maintained

## Directory Structure

```
controlplane/baseline/
├── config/                    # Core configuration files (10 files)
│   ├── root.config.yaml       # Main system configuration
│   ├── root.devices.map       # Device mapping rules
│   ├── root.governance.yaml   # Governance policies
│   ├── root.integrity.yaml    # Integrity checking rules
│   ├── root.kernel.map        # Kernel module mappings
│   ├── root.modules.yaml      # Module configuration
│   ├── root.naming-policy.yaml # Naming conventions
│   ├── root.provenance.yaml   # Provenance tracking
│   ├── root.super-execution.yaml # Privileged execution rules
│   └── root.trust.yaml        # Trust model definitions
│
├── specifications/            # Formal specifications (5 files)
│   ├── root.specs.context.yaml    # Context specifications
│   ├── root.specs.logic.yaml      # Logic specifications
│   ├── root.specs.mapping.yaml    # Mapping specifications
│   ├── root.specs.naming.yaml     # Naming specifications
│   └── root.specs.references.yaml # Reference specifications
│
├── registries/                # Component registries (2 files)
│   ├── root.registry.modules.yaml  # Module registry
│   └── root.registry.devices.yaml  # Device registry
│
├── integration/               # Integration rules (1 file)
│   └── root.integration.yaml  # Cross-component integration
│
├── validation/                # Validation system (3 files)
│   ├── gate-root-specs.yml    # Validation gate configuration
│   ├── validate-root-specs.py # Core validation engine
│   └── vectors/
│       └── root.validation.vectors.yaml # Test vectors
│
└── documentation/             # Architecture docs (1 file)
    └── BASELINE_ARCHITECTURE.md # This file
```

## Component Descriptions

### Configuration Files (config/)

#### root.config.yaml

Main system configuration defining core parameters, paths, and system-wide settings.

#### root.devices.map

Device mapping rules that define how devices are accessed and managed within the root namespace.

#### root.governance.yaml

Governance policies including approval workflows, change management, and compliance requirements.

#### root.integrity.yaml

Integrity checking rules for verifying system component authenticity and detecting tampering.

#### root.kernel.map

Kernel module mappings defining which kernel modules are allowed and how they're loaded.

#### root.modules.yaml

Module configuration specifying module parameters, dependencies, and loading order.

#### root.naming-policy.yaml

Naming conventions and policies for all system components, ensuring consistency.

#### root.provenance.yaml

Provenance tracking configuration for maintaining audit trails and change history.

#### root.super-execution.yaml

Privileged execution rules defining when and how elevated privileges are granted.

#### root.trust.yaml

Trust model definitions including trust levels, verification methods, and trust boundaries.

### Specifications (specifications/)

#### root.specs.context.yaml

Context specifications defining the operational environment and constraints.

#### root.specs.logic.yaml

Logic specifications defining behavioral rules and decision-making processes.

#### root.specs.mapping.yaml

Mapping specifications defining relationships between components.

#### root.specs.naming.yaml

Naming specifications providing formal naming rules and patterns.

#### root.specs.references.yaml

Reference specifications defining how components reference each other.

### Registries (registries/)

#### root.registry.modules.yaml

Canonical registry of all modules with metadata, dependencies, and trust levels.

#### root.registry.devices.yaml

Canonical registry of all devices with types, permissions, and access rules.

### Integration (integration/)

#### root.integration.yaml

Cross-component integration rules ensuring components work together correctly.

### Validation (validation/)

#### gate-root-specs.yml

Validation gate configuration defining validation checkpoints and requirements.

#### validate-root-specs.py

Core validation engine that executes validation rules and produces evidence.

#### root.validation.vectors.yaml

Test vectors for validating the validation system itself.

## Data Flow

### Bootstrap Sequence

1. Load root.config.yaml (system configuration)
2. Load specifications (formal rules)
3. Load registries (component catalogs)
4. Apply governance policies
5. Enable integrity checking
6. Validate complete system

### Runtime Operation

1. Check naming policy
2. Verify trust level
3. Validate against specifications
4. Check registry
5. Apply governance
6. Record provenance
7. Generate evidence

### Validation Flow

1. Load validation vectors
2. Execute validation rules
3. Check cross-component consistency
4. Verify integration constraints
5. Generate validation report
6. Store evidence in overlay/

## Integration Points

### Config ↔ Specifications

- Configurations must align with specifications
- Naming policies must match naming specs
- Trust policies must align with governance specs

### Modules ↔ Devices

- Modules can only access registered devices
- Device permissions align with module trust levels
- Module dependencies satisfied before device access

### Governance ↔ Trust

- Trust levels match governance classifications
- Provenance tracking for all governed components
- Integrity checks align with trust requirements

### Naming ↔ Registry

- All registered items follow naming policies
- Module names match naming policy patterns
- Registry entries use canonical names

## Validation System

### Validation Gates

- **Pre-bootstrap**: Verify baseline integrity
- **Post-bootstrap**: Verify system initialization
- **Runtime**: Continuous validation
- **Pre-shutdown**: Verify clean state

### Validation Rules

- **Structural**: File existence, format, syntax
- **Semantic**: Logical consistency, completeness
- **Integration**: Cross-component alignment
- **Security**: Trust, integrity, provenance

### Evidence Generation

All validation produces evidence stored in `overlay/evidence/`:

- Validation reports (JSON)
- Test results
- Integrity checksums
- Audit logs

## Self-Healing Model

### Scope

- **Allowed**: Write to overlay/
- **Allowed**: Extend registries via overlay
- **Allowed**: Add runtime configurations
- **Forbidden**: Modify baseline/
- **Forbidden**: Modify active/

### Process

1. Detect issue via validation
2. Determine if self-healable
3. Generate overlay correction
4. Validate correction
5. Apply to overlay/
6. Re-synthesize active/
7. Generate evidence

### Constraints

- Must maintain integration constraints
- Must pass all validation gates
- Must preserve baseline immutability
- Must generate complete evidence

## Usage Guidelines

### For System Administrators

1. Never modify baseline/ directly
2. Use overlay/ for runtime changes
3. Review validation reports regularly
4. Maintain evidence archives
5. Follow governance processes for baseline updates

### For Developers

1. Reference baseline/ for canonical definitions
2. Extend via overlay/ for customizations
3. Use active/ for runtime queries
4. Write validation tests for new components
5. Document integration points

### For Auditors

1. Baseline/ is the governance truth
2. Evidence/ contains validation proof
3. Validation reports show compliance
4. Provenance tracks all changes
5. Integrity checks detect tampering

## Maintenance

### Baseline Updates

1. Propose change via governance process
2. Create change request with justification
3. Review and approve via governance.yaml rules
4. Update baseline/ files
5. Run full validation suite
6. Generate update evidence
7. Commit to version control

### Validation Updates

1. Add new validation rules to validate-root-specs.py
2. Add test vectors to root.validation.vectors.yaml
3. Update gate-root-specs.yml if needed
4. Test validation changes
5. Document new validation requirements

## Security Considerations

### Immutability Enforcement

- Filesystem permissions (read-only)
- Version control (audit trail)
- Integrity checking (tamper detection)
- Validation gates (compliance verification)

### Trust Boundaries

- Baseline → Overlay (one-way reference)
- Overlay → Active (synthesis only)
- Active → Runtime (read-only view)

### Audit Trail

- All changes tracked in provenance
- Evidence generated for all operations
- Validation reports archived
- Governance approvals recorded

## Troubleshooting

### Validation Failures

1. Check validation report in overlay/evidence/
2. Review specific failed rules
3. Verify baseline file integrity
4. Check cross-component consistency
5. Review recent overlay changes

### Integration Issues

1. Check root.integration.yaml rules
2. Verify component references
3. Check registry completeness
4. Validate naming consistency
5. Review trust level alignment

### Self-Healing Failures

1. Verify overlay/ is writable
2. Check validation constraints
3. Review self-heal logs
4. Verify integration rules
5. Check evidence generation

## References

- **Root Bootstrap**: `/workspace/root.bootstrap.yaml`
- **Root Environment**: `/workspace/root.env.sh`
- **Root Filesystem Map**: `/workspace/root.fs.map`
- **Overlay Directory**: `/workspace/controlplane/overlay/`
- **Active View**: `/workspace/controlplane/active/`

## Version History

- **v1.0.0**: Initial baseline architecture
  - 10 configuration files
  - 5 specification files
  - 2 registry files
  - 1 integration file
  - Complete validation system
  - Self-healing support

---

**Document Status**: Immutable Baseline Documentation  
**Last Updated**: 2024  
**Maintained By**: Root Namespace Governance  
**Review Cycle**: Per governance policy
