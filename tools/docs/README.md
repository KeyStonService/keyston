# Documentation Tools

This directory contains automated tools for generating and analyzing
documentation in the SynergyMesh repository.

## Available Tools

### 📊 analyze_root_reports.py

Analyze root-level reports to generate consolidated analysis and health metrics.

**Purpose**: Scans all report files in `/reports/` and `/docs/reports/`,
extracts key metrics, findings, and recommendations, then generates consolidated
analysis in multiple formats.

**Usage**:

```bash
# Via Makefile (recommended)
make analyze-reports

# Direct invocation
python tools/docs/analyze_root_reports.py \
  --repo-root . \
  --output docs/reports-analysis.md \
  --json-output docs/reports-analysis.json \
  --verbose

# With YAML output
python tools/docs/analyze_root_reports.py \
  --repo-root . \
  --output docs/reports-analysis.md \
  --json-output docs/reports-analysis.json \
  --yaml-output docs/reports-analysis.yaml \
  --verbose
```

**Outputs**:

- **Markdown**: Human-readable analysis report with executive summary,
  inventory, findings, and action items
- **JSON**: Structured data for programmatic access and integration
- **YAML**: Alternative structured format (requires PyYAML)

**Features**:

- Automatic categorization of reports
- Status extraction (errors, warnings, successes)
- Key findings and recommendations extraction
- Metrics aggregation (success counts, warning counts, etc.)
- Date extraction from report content or file metadata
- Consolidated action items and health indicators

---

### 🕸️ generate_knowledge_graph.py

Generate a Knowledge Graph from the repository structure and MN-DOC entities.

**Usage**:

```bash
make kg
# or
python tools/docs/generate_knowledge_graph.py --repo-root . --output docs/knowledge-graph.yaml
```

---

### 📝 generate_mndoc_from_readme.py

Generate MN-DOC (Multi-Node Documentation) from README.md.

**Usage**:

```bash
make mndoc
# or
python tools/docs/generate_mndoc_from_readme.py --readme README.md --output docs/generated-mndoc.yaml
```

---

### 🔍 project_to_superroot.py

Project Knowledge Graph entities to SuperRoot format.

**Usage**:

```bash
make superroot
# or
python tools/docs/project_to_superroot.py --kg docs/knowledge-graph.yaml --output docs/superroot-entities.yaml
```

---

### 📋 scan_repo_generate_index.py

Scan repository and generate documentation index.

**Usage**:

```bash
python tools/docs/scan_repo_generate_index.py
```

---

### ✅ validate_index.py

Validate documentation index and structure.

**Usage**:

```bash
python tools/docs/validate_index.py --verbose
```

---

### 🔐 provenance_injector.py

Inject SLSA provenance metadata into build artifacts.

**Usage**:

```bash
python tools/docs/provenance_injector.py
```

---

### 💬 pr_comment_summary.py

Generate summary comments for pull requests.

**Usage**:

```bash
python tools/docs/pr_comment_summary.py
```

---

## Common Workflows

### Generate All Documentation Artifacts

```bash
make all-kg
```

This runs:

1. MN-DOC generation
2. Knowledge Graph generation
3. SuperRoot entity projection

### Analyze Reports After Updates

```bash
make analyze-reports
```

### Check for Documentation Drift

```bash
make check-drift
```

---

## Dependencies

Most tools require:

- Python 3.9+
- Standard library modules

Optional dependencies:

- **PyYAML**: For YAML output support (`pip install pyyaml`)

---

## Integration with CI/CD

These tools are integrated into GitHub Actions workflows:

- `.github/workflows/knowledge-graph-drift.yml`: Checks for drift in generated
  docs
- `.github/workflows/project-self-awareness.yml`: Runs self-awareness reports

---

## Tool Development Guidelines

When adding new tools to this directory:

1. **Follow existing patterns**: Use dataclasses, type hints, and docstrings
2. **Provide CLI interface**: Use argparse with help text
3. **Support verbose mode**: Use `--verbose` flag for detailed output
4. **Output to stdout by default**: Allow `-` or stdout for output
5. **Make executable**: Add shebang `#!/usr/bin/env python3` and `chmod +x`
6. **Update Makefile**: Add target if the tool is commonly used
7. **Document here**: Add entry to this README

---

## Questions or Issues?

For questions about these tools, see:

- Main documentation: `/docs/`
- Project manifest: `/docs/project-manifest.md`
- Governance index: `/governance/README.md`
