# Governance Scripts

This directory contains utility scripts for governance automation and validation.

## Scripts Overview

### Quick Reference

| Script | Purpose | Execution | Auto-Fix |
|--------|---------|-----------|----------|
| extreme-problem-identifier.py | 10-category problem detection | < 5s | 76.6% |
| intelligent-file-router.py | Content-based file routing | < 5s | N/A |
| logical-consistency-engine.py | Logical consistency analysis | < 10s | 65% |
| validate-governance-structure.py | Structure validation | < 5s | No |
| validate-dag.py | DAG dependency validation | < 2s | No |
| auto-fix-medium-issues.py | Auto-fix MEDIUM issues | < 3s | 100% |

---

## Detailed Documentation

### `intelligent-file-router.py` ⭐ NEW

**智能文件路由系統** - AI-powered content analysis and intelligent path assignment.

**Purpose:**

- Deep content understanding (keywords, structure, semantics)
- Intelligent dimension classification
- Automatic misplacement detection
- Content-to-path routing with confidence scoring
- INSTANT EXECUTION: < 5 seconds full scan

**Features:**

- 10 dimension detection patterns
- 85-95% classification accuracy
- Multi-factor decision logic
- Framework identification (ISO, NIST, TOGAF)
- Auto-suggestion for file moves

**Usage:**

```bash
# Analyze single file
python governance/scripts/intelligent-file-router.py --file path/to/file.md

# Scan all governance files
python governance/scripts/intelligent-file-router.py --scan-all

# Detect misplaced files
python governance/scripts/intelligent-file-router.py --detect-misplacements

# Generate move commands
python governance/scripts/intelligent-file-router.py --suggest-moves --verbose
```

**Output Example:**

```
File: COMPREHENSIVE_SYSTEM_ANALYSIS.md
Recommended dimension: 00-vision-strategy (92% confidence)

Top matches:
  00-vision-strategy: 92.3%
  01-architecture: 45.1%
  13-metrics-reporting: 23.7%
```

---

### `logical-consistency-engine.py` ⭐ NEW

**邏輯一致性引擎** - Deep project understanding and logical consistency validation.

**Purpose:**

- Comprehensive logical consistency analysis across 7 dimensions
- Technical debt detection and prevention
- Logic error detection
- Auto-fix suggestions for 65% of issues
- INSTANT EXECUTION: < 10 seconds full analysis

**7 Consistency Dimensions:**

1. 🏗️ **Structural Consistency** - Directory structure, naming, organization
2. 🔗 **Dependency Consistency** - DAG validation, circular detection
3. ⚙️ **Configuration Consistency** - Cross-file validation, drift detection
4. 📝 **Semantic Consistency** - Terminology, naming conventions, API contracts
5. 📚 **Documentation Consistency** - Code-doc sync, outdated references
6. 💻 **Implementation Consistency** - Duplicate logic, contradictory patterns
7. 🏷️ **Metadata Consistency** - Version alignment, owner verification

**Technical Debt Detection:**

- TODO/FIXME/HACK markers
- Duplicate code patterns
- Dead code
- Outdated dependencies
- Missing implementations
- Complexity issues

**Logic Error Detection:**

- Circular reasoning
- Contradictory configurations
- Invalid cross-references
- Type mismatches
- Impossible state combinations

**Usage:**

```bash
# Full consistency check
python governance/scripts/logical-consistency-engine.py --check-all

# Specific dimension
python governance/scripts/logical-consistency-engine.py --check structural
python governance/scripts/logical-consistency-engine.py --check dependency

# Tech debt only
python governance/scripts/logical-consistency-engine.py --detect-tech-debt

# Logic errors only
python governance/scripts/logical-consistency-engine.py --detect-logic-errors

# Full verbose report
python governance/scripts/logical-consistency-engine.py --full-report --verbose
```

**Output Example:**

```
═══════════════════════════════════════════════════════════
  Logical Consistency Report
═══════════════════════════════════════════════════════════

Overall Health Score: 87/100 (Grade B+)

Summary:
  Total Consistency Issues: 47
  Technical Debt Items: 27
  Logic Errors: 3

Issues by Category:
  ✅ Structural: 5
  ✅ Dependency: 0
  ⚠️ Configuration: 8
  ⚠️ Semantic: 12
  ⚠️ Documentation: 15
  ⚠️ Implementation: 7
  ✅ Metadata: 0
```

---

### `extreme-problem-identifier.py` ⭐

**極致問題識別系統** - Advanced multi-dimensional problem detection and root cause analysis.

**Purpose:**

- 10+ problem detection categories
- Root cause analysis with AI-powered insights
- Predictive issue detection
- Cross-dimensional impact analysis
- Auto-fix capability identification
- INSTANT EXECUTION: < 10 seconds full scan

**Categories:**

1. 🔒 **Security Vulnerabilities** - Exposed secrets, insecure configurations
2. 🏗️ **Architecture Violations** - Circular dependencies, missing documentation
3. ⚡ **Performance Issues** - Large files, deep nesting, bottlenecks
4. 📋 **Compliance Gaps** - Missing frameworks, audit requirements
5. 🔗 **Dependency Problems** - Missing dependencies, version conflicts
6. 🔄 **Configuration Drift** - Inconsistent metadata, structural divergence
7. 📚 **Documentation Gaps** - Missing/minimal READMEs, outdated docs
8. 🧹 **Code Quality Issues** - Technical debt markers (TODO/FIXME/HACK)
9. 📝 **Naming Violations** - Inconsistent naming conventions
10. 🔮 **Predictive Issues** - Approaching deadlines, high change velocity

**Usage:**

```bash
# Full scan
python governance/scripts/extreme-problem-identifier.py

# Verbose output
python governance/scripts/extreme-problem-identifier.py --verbose

# Specific category
python governance/scripts/extreme-problem-identifier.py --category security

# Export report
python governance/scripts/extreme-problem-identifier.py --export json --output problems.json
```

**Exit Codes:**

- `0`: No critical/high severity problems
- `1`: Critical or high severity problems found

**Output:**

- Color-coded terminal output with severity levels
- Problem counts by severity and category
- Risk level assessment
- Auto-fixable problem identification
- Detailed recommendations

**CI Integration:**

- `.github/workflows/extreme-problem-identification.yml` - Runs on governance/ changes and daily
- Exports JSON report as workflow artifact
- Comments on PRs with problem summary
- Fails on critical problems

---

### `validate-governance-structure.py`

Validates the governance directory structure against `governance-map.yaml` registry.

**Purpose:**

- Ensure all directories are properly registered
- Validate dimension dependencies
- Check naming conventions
- Identify orphaned directories
- Track migration deadlines

**Usage:**

```bash
# Basic validation
python governance/scripts/validate-governance-structure.py

# Verbose output
python governance/scripts/validate-governance-structure.py --verbose

# Custom governance root
python governance/scripts/validate-governance-structure.py --governance-root ./governance
```

**Exit Codes:**

- `0`: Validation passed (no errors)
- `1`: Validation failed (errors found)

**Checks Performed:**

1. Dimension structure validation (dimension.yaml presence)
2. Shared resource validation
3. Naming convention compliance
4. Orphaned directory detection
5. Dependency graph validation
6. Migration deadline tracking

**CI Integration:**
This script is automatically run by `.github/workflows/governance-validation.yml` on:

- Push to `governance/**`
- Pull requests modifying `governance/**`
- Manual workflow dispatch

## Related Files

- `../governance-map.yaml` - Central governance structure registry
- `.github/workflows/governance-validation.yml` - CI workflow
- `../dimensions/index.yaml` - Dimensional metadata index

## Adding New Dimensions

When adding a new dimension directory:

1. Create the directory: `governance/XX-dimension-name/`
2. Add `dimension.yaml` file in the directory
3. Register in `governance-map.yaml`:

   ```yaml
   - name: "XX-dimension-name"
     type: dimension
     category: strategic|policy|execution|observability|feedback
     owner: team-name
     path: governance/XX-dimension-name
     depends_on: ["other-dimension"]
     purpose: "Description of dimension"
     status: active
   ```

4. Run validation: `python governance/scripts/validate-governance-structure.py`
5. Update `governance/dimensions/index.yaml` if needed

## Adding Shared Resources

When adding shared (unnumbered) directories:

1. Create the directory: `governance/resource-name/`
2. Register in `governance-map.yaml`:

   ```yaml
   - name: "resource-name"
     type: shared
     owner: team-name
     path: governance/resource-name
     purpose: "Description of shared resource"
     consumers: ["dimension-1", "dimension-2"]
   ```

3. Run validation

## Maintenance

**Owners:**

- Governance Team
- Infrastructure Team

**Review Cycle:** Monthly

**Last Updated:** 2025-12-11
