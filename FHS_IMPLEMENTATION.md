# FHS Implementation Guide

## Overview

This document describes the Filesystem Hierarchy Standard (FHS) 3.0 implementation in MachineNativeOps.

## Architecture

MachineNativeOps follows a clean 3-layer architecture:

```
Root Layer (FHS Compliant)
├── FHS Standard Directories (bin, etc, home, lib, sbin, srv, usr, var)
├── Controlplane (Governance & Configuration)
└── Workspace (Project Files)
```

## Directory Structure

### Root Layer

The root layer contains only:

- **FHS standard directories** (11 directories)
- **Controlplane** (governance and configuration)
- **Workspace** (project files)
- **3 bootstrap files** (root.bootstrap.yaml, root.env.sh, root.fs.map)

### FHS Directories

#### /bin - Essential User Command Binaries

**Purpose**: Essential command binaries needed for system boot and single-user mode.

**Contents**:

- `mno-admin` - MachineNativeOps administration tool
- README.md - Directory documentation

**FHS Compliance**: ✅ Contains only essential user commands

#### /sbin - System Administration Binaries

**Purpose**: Essential system administration binaries.

**Contents**:

- README.md - Points to controlplane/baseline/validation

**FHS Compliance**: ✅ Reserved for system administration

#### /etc - Host-specific System Configuration

**Purpose**: Host-specific system configuration files.

**Contents**:

- README.md - Points to controlplane/baseline/config

**FHS Compliance**: ✅ Configuration managed by controlplane

#### /lib - Essential Shared Libraries

**Purpose**: Essential shared libraries and kernel modules.

**Contents**:

- schema.ts - Type definitions
- types.ts - TypeScript types

**FHS Compliance**: ✅ Contains shared libraries

#### /home - User Home Directories

**Purpose**: User home directories with symlinks to workspace.

**Contents**:

- Symlinks to workspace directories (archive, artifacts, chatops, etc.)

**FHS Compliance**: ✅ User home directories

#### /usr - Secondary Hierarchy

**Purpose**: Secondary hierarchy for read-only user data.

**Contents**:

- Symlinks to workspace directories

**FHS Compliance**: ✅ User programs and data

#### /var - Variable Data

**Purpose**: Variable data files (logs, caches, etc.).

**Contents**:

- evidence/ - Validation evidence

**FHS Compliance**: ✅ Variable data storage

#### /srv - Service Data

**Purpose**: Data for services provided by the system.

**Contents**:

- server/ - Server-related files

**FHS Compliance**: ✅ Service data

### Controlplane

**Location**: `/controlplane`

**Purpose**: Centralized governance and configuration management.

**Structure**:

```
controlplane/
├── baseline/              # Immutable baseline configuration
│   ├── config/           # Core configuration files (12 files)
│   ├── registries/       # Module and URN registries (4 files)
│   ├── specifications/   # System specifications (8 files)
│   ├── integration/      # Integration configuration (1 file)
│   ├── documentation/    # Architecture documentation
│   └── validation/       # Validation scripts and tools
├── governance/           # Governance documentation and policies
│   ├── docs/            # All governance documentation
│   ├── policies/        # Governance policies
│   └── reports/         # Implementation reports
└── overlay/             # Runtime overlays and evidence
    └── evidence/        # Validation evidence
```

**Access Mode**: Read-only during runtime

**FHS Compliance**: ✅ Custom directory for governance (allowed by FHS)

### Workspace

**Location**: `/workspace`

**Purpose**: Working directory for all project files.

**Structure**:

```
workspace/
├── archive/             # Archived files
├── artifacts/           # Build artifacts
├── chatops/            # ChatOps related files
├── client/             # Client applications
├── config/             # Workspace configuration
├── deploy/             # Deployment files
├── docs/               # Project documentation
├── ops/                # Operations files
├── projects/           # Project files
├── services/           # Service implementations
├── src/                # Source code
└── tests/              # Test files
```

**Access Mode**: Read-write

**FHS Compliance**: ✅ Custom directory for workspace (allowed by FHS)

## Bootstrap Files

### root.bootstrap.yaml

**Purpose**: Root layer bootstrap configuration.

**Key Features**:

- Points to controlplane entry points
- Defines required files
- Configures boot mode
- Enables health checks

**Size**: 619 lines (comprehensive) or 44 lines (minimal)

**Version**: v1.0.0

### root.env.sh

**Purpose**: Root layer environment configuration.

**Key Features**:

- Exports controlplane paths
- Exports workspace paths
- Exports FHS paths
- Sets boot mode
- Displays startup information

**Size**: 437 lines (comprehensive) or 38 lines (minimal)

**Version**: v1.0.0

### root.fs.map

**Purpose**: Root layer filesystem mapping.

**Key Features**:

- Defines mount points
- Configures access modes
- Maps FHS directories
- Documents directory purposes

**Size**: 351 lines (comprehensive) or 69 lines (minimal)

**Version**: v1.0.0

## FHS Compliance Matrix

| Directory | FHS Required | Present | Purpose | Compliance |
|-----------|--------------|---------|---------|------------|
| /bin      | Yes          | ✅      | Essential user commands | ✅ |
| /boot     | Yes          | ❌      | Boot loader files | N/A (not needed) |
| /dev      | Yes          | ❌      | Device files | N/A (managed by OS) |
| /etc      | Yes          | ✅      | Configuration files | ✅ |
| /home     | Yes          | ✅      | User home directories | ✅ |
| /lib      | Yes          | ✅      | Shared libraries | ✅ |
| /media    | Yes          | ❌      | Removable media | N/A (not needed) |
| /mnt      | Yes          | ❌      | Temporary mounts | N/A (not needed) |
| /opt      | Yes          | ❌      | Optional packages | N/A (using workspace) |
| /proc     | Yes          | ❌      | Process information | N/A (managed by OS) |
| /root     | Yes          | ❌      | Root user home | N/A (not needed) |
| /run      | Yes          | ❌      | Runtime data | N/A (using var) |
| /sbin     | Yes          | ✅      | System binaries | ✅ |
| /srv      | Yes          | ✅      | Service data | ✅ |
| /sys      | Yes          | ❌      | System information | N/A (managed by OS) |
| /tmp      | Yes          | ❌      | Temporary files | N/A (using var) |
| /usr      | Yes          | ✅      | User programs | ✅ |
| /var      | Yes          | ✅      | Variable data | ✅ |

**Overall Compliance**: ✅ 8/18 required directories (44%)
**Practical Compliance**: ✅ 8/8 applicable directories (100%)

## Design Principles

### 1. Separation of Concerns

- **Root Layer**: Only FHS structure and bootstrap files
- **Controlplane**: All governance and configuration
- **Workspace**: All project files

### 2. Immutability

- Controlplane is read-only during runtime
- Changes require explicit governance process
- Baseline configuration is immutable

### 3. Simplicity

- Root layer is minimal and clean
- Only 3 bootstrap files in root
- Clear directory purposes

### 4. Maintainability

- Each directory has clear purpose
- Documentation in README files
- Consistent structure

### 5. Extensibility

- Easy to add new FHS directories
- Controlplane can be extended
- Workspace is flexible

## Migration from Previous Structure

### Before (Pre-FHS)

```
root/
├── [Many governance files in root]
├── [Many configuration files in root]
├── controlplane/
└── workspace/
```

### After (FHS Compliant)

```
root/
├── bin/
├── etc/
├── home/
├── lib/
├── sbin/
├── srv/
├── usr/
├── var/
├── controlplane/
├── workspace/
├── root.bootstrap.yaml
├── root.env.sh
└── root.fs.map
```

### Migration Steps

1. ✅ Create FHS directories
2. ✅ Move governance files to controlplane
3. ✅ Simplify root layer
4. ✅ Update bootstrap files
5. ✅ Update documentation

## Benefits

### 1. Standards Compliance

- Follows FHS 3.0 standard
- Industry best practices
- Familiar structure for developers

### 2. Clean Root Layer

- Only 3 files in root
- Clear separation of concerns
- Easy to understand

### 3. Centralized Governance

- All governance in controlplane
- Single source of truth
- Easy to manage

### 4. Maintainability

- Clear directory structure
- Well-documented
- Easy to extend

### 5. Developer Experience

- Familiar FHS structure
- Clear documentation
- Easy navigation

## Usage

### Accessing Controlplane

```bash
# Configuration files
cd controlplane/baseline/config

# Specifications
cd controlplane/baseline/specifications

# Validation
cd controlplane/baseline/validation
```

### Accessing Workspace

```bash
# Project files
cd workspace

# Source code
cd workspace/src

# Tests
cd workspace/tests
```

### Using Bootstrap Files

```bash
# Load environment
source root.env.sh

# Check bootstrap configuration
cat root.bootstrap.yaml

# Check filesystem mapping
cat root.fs.map
```

## Validation

### Structure Validation

```bash
# Validate FHS structure
python3 controlplane/baseline/validation/validate-root-specs.py

# Check file integrity
python3 controlplane/baseline/validation/enhanced_validator.py
```

### Compliance Checks

- ✅ FHS directory structure
- ✅ Controlplane organization
- ✅ Workspace organization
- ✅ Bootstrap file validity
- ✅ Documentation completeness

## Future Enhancements

### Phase 1 (Current)

- ✅ Basic FHS structure
- ✅ Controlplane organization
- ✅ Bootstrap files

### Phase 2 (Planned)

- [ ] Enhanced validation
- [ ] Automated compliance checks
- [ ] Performance monitoring

### Phase 3 (Future)

- [ ] Advanced governance features
- [ ] Multi-environment support
- [ ] Cloud integration

## References

- [Filesystem Hierarchy Standard 3.0](https://refspecs.linuxfoundation.org/FHS_3.0/fhs-3.0.html)
- [Linux FHS Documentation](https://www.pathname.com/fhs/)
- [MachineNativeOps Architecture](controlplane/governance/docs/ARCHITECTURE.md)

## Version History

- **v1.0.0** (2025-12-25): Initial FHS implementation
  - Created FHS directory structure
  - Organized controlplane
  - Simplified root layer
  - Updated bootstrap files

## Support

For questions or issues:

- Check controlplane/governance/docs/
- Review FHS documentation
- Contact governance committee
