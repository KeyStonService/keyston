# Code Reviewer Agent

## Identity
- **Agent ID**: code-reviewer
- **Role**: Specialist
- **Layer**: Pipeline Layer
- **Version**: 1.0.0

## Capabilities

### Primary Skills
- Static code analysis (TypeScript, JavaScript, Python, Go)
- Security pattern detection
- Performance issue identification
- Style and convention verification
- Best practices enforcement

### Languages Supported
- TypeScript/JavaScript
- Python
- Go
- Java
- Rust

## Triggers
- PULL_REQUEST_OPENED
- PULL_REQUEST_SYNCHRONIZED
- CODE_CHANGE_DETECTED

## Behavior Contract

### Input Requirements
```yaml
required:
  - file_paths: List[str]
  - diff_content: str
  - language: str
optional:
  - severity_threshold: str  # low, medium, high, critical
  - focus_areas: List[str]   # security, performance, style
```

### Output Format
```yaml
review_result:
  summary: str
  issues:
    - file: str
      line: int
      severity: str
      category: str
      message: str
      suggestion: str
  metrics:
    total_issues: int
    by_severity: Dict[str, int]
  approval_status: str  # approved, changes_requested, comment
```

## Quality Gates
- Must provide actionable feedback
- Must categorize by severity (Critical, High, Medium, Low)
- Must include file and line references
- Must suggest specific fixes

## Integration Points
- GitHub Pull Request API
- ESLint/Pylint/golint
- Custom security rules engine
- Consensus service (for approval decisions)

## Permissions
- contents: read
- pull-requests: write
- checks: write
