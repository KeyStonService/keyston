# FHS Directory Structure Implementation

**Date:** 2024-12-23  
**Status:** ✅ COMPLETED

---

## Overview

The root directory now implements the **Filesystem Hierarchy Standard (FHS)** with 11 standard directories, following Unix/Linux conventions while maintaining our minimal system skeleton principle.

---

## FHS Directories

### Symlinks to Workspace/Controlplane

Most FHS directories are **symbolic links** to appropriate locations in `workspace/` or `controlplane/`:

```
/bin -> workspace/src/bin
  Purpose: General user commands
  Writable: Yes (via workspace)
  
/sbin -> controlplane/baseline/validation
  Purpose: System administration commands (validators)
  Writable: No (immutable baseline)
  
/etc -> controlplane/baseline/config
  Purpose: Configuration pointers
  Writable: No (immutable baseline)
  
/lib -> workspace/shared
  Purpose: Shared libraries
  Writable: Yes (via workspace)
  
/usr -> workspace
  Purpose: Extended installation area
  Writable: Yes
  
/home -> workspace
  Purpose: User working area
  Writable: Yes
  
/srv -> workspace/services
  Purpose: Service data
  Writable: Yes (via workspace)
```

### Actual Directories

Some FHS directories are **real directories** for runtime data:

```
/var/
  Purpose: Variable runtime data
  Writable: Yes
  Subdirectories:
    - log/      (application logs)
    - run/      (runtime state)
    - state/    (persistent state)
    - cache/    (cache files)
    - evidence/ -> ../controlplane/overlay/evidence (symlink)
  
/tmp/
  Purpose: Temporary files
  Writable: Yes (with sticky bit 1777)
  
/opt/
  Purpose: Optional packages
  Writable: Yes
  
/init.d/
  Purpose: Initialization scripts
  Writable: Yes
```

---

## Complete Root Directory Structure

```
/workspace/
├── .env.example              # Environment variables template
├── .git/                     # Git repository
├── .github/                  # GitHub workflows
├── .gitignore                # Git ignore rules
├── .replit                   # Replit configuration
├── CNAME                     # Custom domain
├── README.md                 # Project documentation
│
├── root.bootstrap.yaml       # Boot pointer: System bootstrap
├── root.env.sh               # Boot pointer: Environment setup
├── root.fs.map               # Boot pointer: Filesystem mapping
│
├── bin -> workspace/src/bin              # FHS: User commands
├── sbin -> controlplane/baseline/validation  # FHS: Admin commands
├── etc -> controlplane/baseline/config   # FHS: Configuration
├── lib -> workspace/shared               # FHS: Shared libraries
├── var/                                  # FHS: Variable data
│   ├── log/
│   ├── run/
│   ├── state/
│   ├── cache/
│   └── evidence -> ../controlplane/overlay/evidence
├── usr -> workspace                      # FHS: Extended area
├── home -> workspace                     # FHS: User area
├── tmp/                                  # FHS: Temporary files
├── opt/                                  # FHS: Optional packages
├── srv -> workspace/services             # FHS: Service data
├── init.d/                               # FHS: Init scripts
│
├── controlplane/             # Governance layer (immutable)
│   ├── baseline/
│   │   ├── config/          (linked from /etc)
│   │   ├── specifications/
│   │   ├── registries/
│   │   ├── validation/      (linked from /sbin)
│   │   ├── integration/
│   │   └── documentation/
│   ├── overlay/
│   │   ├── state/
│   │   └── evidence/        (linked from /var/evidence)
│   └── governance/
│
├── workspace/                # Work layer (mutable)
│   ├── src/
│   │   ├── bin/             (linked from /bin)
│   │   ├── core/
│   │   ├── agents/
│   │   ├── tooling/
│   │   ├── adapters/
│   │   └── scripts/
│   ├── services/            (linked from /srv)
│   │   └── server/
│   ├── shared/              (linked from /lib)
│   ├── db/
│   ├── chatops/
│   ├── runtime/
│   ├── config/
│   ├── docs/
│   ├── tests/
│   ├── deploy/
│   ├── ops/
│   ├── archive/
│   └── private/
│
└── wrangler.toml -> workspace/config/wrangler.toml
```

---

## FHS Compliance

### ✅ Standard Directories (11/11)

All FHS standard directories are present:

1. ✅ `/bin` - Essential user command binaries
2. ✅ `/sbin` - System administration binaries
3. ✅ `/etc` - Host-specific system configuration
4. ✅ `/lib` - Essential shared libraries
5. ✅ `/var` - Variable data files
6. ✅ `/usr` - Secondary hierarchy
7. ✅ `/home` - User home directories
8. ✅ `/tmp` - Temporary files
9. ✅ `/opt` - Add-on application software packages
10. ✅ `/srv` - Data for services provided by system
11. ✅ `/init.d` - Service initialization scripts

---

## Design Principles

### 1. Symlinks for Logical Organization

Most FHS directories are symlinks to maintain:

- **Single Source of Truth**: Files exist in one location
- **Clear Ownership**: workspace (mutable) vs controlplane (immutable)
- **Easy Navigation**: Standard Unix paths work as expected

### 2. Real Directories for Runtime Data

Directories that need to be writable and independent:

- `/var` - Runtime state and logs
- `/tmp` - Temporary files (with sticky bit)
- `/opt` - Optional packages
- `/init.d` - Initialization scripts

### 3. Immutability Enforcement

Symlinks to `controlplane/baseline/` are read-only:

- `/etc` -> controlplane/baseline/config (immutable)
- `/sbin` -> controlplane/baseline/validation (immutable)

### 4. Workspace Integration

Symlinks to `workspace/` are writable:

- `/bin` -> workspace/src/bin
- `/lib` -> workspace/shared
- `/usr` -> workspace
- `/home` -> workspace
- `/srv` -> workspace/services

---

## Benefits

1. **FHS Compliance**: Standard Unix/Linux directory structure
2. **Minimal Root**: Only essential directories in root
3. **Clear Separation**: Governance (controlplane) vs Work (workspace)
4. **Familiar Paths**: Standard paths like /etc, /var, /tmp work as expected
5. **Immutability**: Critical paths are read-only via controlplane
6. **Flexibility**: Workspace paths are writable for development

---

## Usage Examples

### Access Configuration

```bash
# Standard FHS path
cat /etc/root.config.yaml

# Actual location
cat controlplane/baseline/config/root.config.yaml
```

### Run Validators

```bash
# Standard FHS path
/sbin/validate-root-specs.py

# Actual location
controlplane/baseline/validation/validate-root-specs.py
```

### Use Shared Libraries

```bash
# Standard FHS path
ls /lib

# Actual location
ls workspace/shared
```

### Write Logs

```bash
# Standard FHS path
echo "log entry" >> /var/log/app.log

# Actual location (real directory)
echo "log entry" >> var/log/app.log
```

---

## Verification

To verify FHS structure:

```bash
# Check all FHS directories exist
ls -la / | grep -E "bin|sbin|etc|lib|var|usr|home|tmp|opt|srv|init"

# Verify symlinks
ls -l /bin /sbin /etc /lib /usr /home /srv

# Check real directories
ls -la /var /tmp /opt /init.d
```

---

## Related Documents

- [Root Directory Structure](ROOT_DIRECTORY_STRUCTURE.md)
- [Root Cleanup Summary](ROOT_CLEANUP_SUMMARY.md)
- [Namespace Specification](NAMESPACE_SPECIFICATION_COMPLETE.md)
- [Path Specifications](../../controlplane/baseline/specifications/root.specs.paths.yaml)

---

**Status:** ✅ **FHS DIRECTORY STRUCTURE IMPLEMENTED**

The root directory now fully complies with both:

1. Minimal System Skeleton principle
2. Filesystem Hierarchy Standard (FHS)
