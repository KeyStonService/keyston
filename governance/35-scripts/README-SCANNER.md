# Governance Directory Scanner

## Overview

The Governance Directory Scanner is a comprehensive tool for scanning, analyzing, and validating the SynergyMesh governance directory structure. It provides detailed reports on dimension completeness, file presence, naming conventions, and structural integrity.

## Features

- **Full Structure Scan**: Scans all 00-80 governance dimensions
- **File Completeness Verification**: Checks for required files (`dimension.yaml`, `README.md`, `framework.yaml`)
- **Naming Convention Validation**: Ensures directories follow the `XX-name` pattern
- **Dependency Analysis**: Validates dimension dependencies from `governance-map.yaml`
- **Orphaned Directory Detection**: Finds directories not registered in the governance map
- **Coverage Analysis**: Reports on dimension implementation coverage (0-80)
- **Statistics Generation**: Provides comprehensive metrics about governance health
- **Actionable Recommendations**: Generates specific recommendations for improvements
- **Multiple Report Formats**: Supports YAML, JSON, and text output formats

## Installation

No additional installation required. The scanner uses standard Python 3.10+ libraries:

- `pyyaml` - for YAML parsing
- Standard library modules: `pathlib`, `datetime`, `json`, `re`, `collections`

## Usage

### Basic Scan

Run a basic governance directory scan:

```bash
# From repository root
python governance/35-scripts/scan-governance-directory.py

# Or using Make
make scan-governance
```

### Verbose Mode

Enable detailed output for debugging:

```bash
python governance/35-scripts/scan-governance-directory.py --verbose

# Or using Make
make scan-governance
```

### Generate Reports

Generate a detailed report file:

```bash
# YAML format (default)
python governance/35-scripts/scan-governance-directory.py \
  --report-output governance/scan-report.yaml

# JSON format
python governance/35-scripts/scan-governance-directory.py \
  --report-format json \
  --report-output governance/scan-report.json

# Text format
python governance/35-scripts/scan-governance-directory.py \
  --report-format text \
  --report-output governance/scan-report.txt

# Or using Make
make scan-governance-report      # Generates YAML report
make scan-governance-json        # Generates JSON report
```

### Quiet Mode

Generate report without console output:

```bash
python governance/35-scripts/scan-governance-directory.py \
  --quiet \
  --report-output governance/scan-report.yaml
```

### Custom Governance Root

Scan a different governance directory:

```bash
python governance/35-scripts/scan-governance-directory.py \
  --governance-root /path/to/governance
```

## Makefile Targets

The scanner is integrated into the project Makefile with convenient targets:

### Available Targets

```bash
make scan-governance               # Run interactive scan with summary
make scan-governance-report        # Generate YAML report
make scan-governance-json          # Generate JSON report
make validate-governance-structure # Validate structure against governance-map.yaml
make validate-governance          # Validate architecture governance matrix
make governance-full-check        # Run all governance validations and scans
```

### Example Workflow

```bash
# 1. Run full governance check
make governance-full-check

# 2. Generate detailed report for review
make scan-governance-report

# 3. Review the report
cat governance/scan-report.yaml

# 4. Address issues and re-scan
make scan-governance
```

## Report Structure

### YAML Report Format

```yaml
metadata:
  scan_timestamp: '2025-12-12T23:00:00Z'
  governance_root: governance
  scanner_version: 1.0.0

statistics:
  total_directories: 87
  dimensions:
    total: 82
    with_dimension_yaml: 81
    with_readme: 72
    with_framework_yaml: 43
    missing_required_files: 1
  dimension_coverage:
    total_expected: 81
    total_present: 81
    coverage_percentage: 100.0
    missing_dimensions: []
  orphaned_directories:
    total: 1
    list: ['55-slo-sli']
  issues:
    total: 1
    by_severity:
      error: 1

dimensions:
  - path: governance/00-vision-strategy
    name: 00-vision-strategy
    type: dimension
    number: 0
    files:
      dimension.yaml: true
      README.md: true
      framework.yaml: false
    missing_required: []
    missing_recommended: ['framework.yaml']
    file_count: 22
    subdirs: ['gitops', 'crd', 'monitoring']

shared_resources:
  - path: governance/ci
    name: ci
    type: shared
    files: {...}

orphaned_directories:
  - '55-slo-sli'

issues:
  - type: missing_required_files
    severity: error
    directory: 55-slo-sli
    details: ['dimension.yaml']

recommendations:
  - "Create dimension.yaml files for 1 dimensions: 55-slo-sli"
  - "Add README.md documentation for 10 dimensions"
  - "Register 1 orphaned directories in governance-map.yaml"
```

## Validation Checks

The scanner performs the following validation checks:

### 1. Directory Classification

- **Numbered Dimensions** (00-80): Validates format `XX-name`
- **Shared Resources**: Identifies shared directories (ci, policies, schemas, etc.)
- **Deprecated Directories**: Detects `_*` prefixed directories
- **Unknown Directories**: Flags unrecognized directory patterns

### 2. File Completeness

**Required Files:**
- `dimension.yaml` - Dimension metadata and configuration

**Recommended Files:**
- `README.md` - Documentation for the dimension
- `framework.yaml` - Framework configuration (optional)

### 3. Naming Conventions

- Number range: 00-80
- Separator: hyphen (-)
- Character case: lowercase
- Pattern: `^[0-9]{2}-[a-z-]+$`

### 4. Dependency Validation

- Checks that dependencies declared in `governance-map.yaml` exist
- Validates cross-dimension references
- Detects circular dependencies (future)

### 5. Orphaned Detection

- Identifies directories not registered in `governance-map.yaml`
- Flags potential misplaced directories
- Suggests registration or migration to `_legacy`

### 6. Coverage Analysis

- Calculates dimension coverage (0-80)
- Identifies missing dimension numbers
- Reports coverage percentage

## Integration with Existing Tools

The scanner integrates with and complements existing governance tools:

### Related Tools

1. **validate-governance-structure.py** - Structure validation against governance-map.yaml
2. **intelligent-file-router.py** - Content-based path assignment
3. **logical-consistency-engine.py** - Logical consistency validation
4. **validate-governance-matrix.py** - Architecture governance matrix validation

### Integration Pattern

```bash
# Complete governance validation workflow
make validate-governance-structure  # Step 1: Structure validation
make scan-governance               # Step 2: Comprehensive scan
make validate-governance           # Step 3: Matrix validation
```

## Exit Codes

The scanner returns the following exit codes:

- `0` - Success, no errors found
- `1` - Errors detected (missing required files, invalid structure, etc.)

## Statistics Collected

### Directory Statistics
- Total directories
- Dimension count (00-80)
- Shared resources count
- Orphaned directories count

### File Statistics
- Total files across all dimensions
- Average files per dimension
- Dimensions with required files
- Dimensions with recommended files

### Coverage Statistics
- Expected dimensions (81 total)
- Present dimensions
- Missing dimensions
- Coverage percentage

### Issue Statistics
- Total issues
- Issues by severity (error, warning)
- Issues by type (missing files, naming, etc.)

## Troubleshooting

### Common Issues

**1. Scanner exits with error code 1**
- This is expected when issues are found
- Review the summary output to see what issues were detected
- Generate a report for detailed analysis

**2. governance-map.yaml not found**
- Ensure you're running from the repository root
- Check that `governance/governance-map.yaml` exists

**3. Orphaned directories detected**
- Add the directory to `governance-map.yaml` under `dimensions` or `shared_resources`
- Or move to `governance/_legacy/` if deprecated

**4. Missing dimension.yaml files**
- Create `dimension.yaml` files for flagged dimensions
- Use existing dimensions as templates

## Development

### Adding New Validation Checks

1. Add validation method to `GovernanceScanner` class
2. Call method in `scan()` method
3. Record issues in `self.issues` list
4. Update recommendations in `generate_recommendations()`

### Example: Adding Custom Check

```python
def check_custom_validation(self) -> bool:
    """Custom validation check."""
    for dim in self.dimensions:
        # Your validation logic
        if not some_condition:
            self.issues.append({
                'type': 'custom_check',
                'severity': 'warning',
                'directory': dim['name'],
                'details': ['Custom check failed']
            })
    return True

# Add to scan() method
self.check_custom_validation()
```

## Best Practices

1. **Run Before Commits**: Use `make governance-full-check` before committing governance changes
2. **Regular Scans**: Run weekly scans to catch drift and issues early
3. **Review Reports**: Generate and review detailed reports for comprehensive analysis
4. **Track Trends**: Compare scan reports over time to track improvements
5. **Address High-Priority Issues**: Fix `error` severity issues first

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Governance Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install pyyaml
      - name: Run governance scan
        run: make scan-governance-report
      - name: Upload scan report
        uses: actions/upload-artifact@v3
        with:
          name: governance-scan-report
          path: governance/scan-report.yaml
```

## Future Enhancements

- [ ] Circular dependency detection
- [ ] Historical trend analysis
- [ ] Automated issue fixing
- [ ] Integration with governance dashboard
- [ ] Performance optimization for large directories
- [ ] Parallel directory scanning
- [ ] Custom validation rule plugins
- [ ] HTML report generation

## References

- [Governance Map](../governance-map.yaml) - Central governance registry
- [Governance README](../README.md) - Governance framework overview
- [Validation Script](./validate-governance-structure.py) - Structure validator
- [Architecture Governance](../../docs/GOVERNANCE_INTEGRATION_ARCHITECTURE.md) - Integration architecture

## Support

For issues or questions:

1. Check this documentation
2. Review scan output and generated reports
3. Examine `governance/governance-map.yaml` structure
4. Consult governance team or create an issue

---

**Version**: 1.0.0  
**Last Updated**: 2025-12-12  
**Maintainer**: SynergyMesh Governance Team
