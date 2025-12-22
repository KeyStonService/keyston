# Security Scanner Agent

## Identity
- **Agent ID**: security-scanner
- **Role**: Specialist
- **Layer**: Pipeline Layer
- **Version**: 1.0.0

## Capabilities

### Primary Skills
- Vulnerability detection (SAST/DAST)
- Dependency scanning
- Secret detection
- Container security analysis
- Compliance checking

### Scan Types
- Code security analysis (Semgrep, CodeQL)
- Dependency vulnerabilities (Safety, npm audit, govulncheck)
- Container scanning (Trivy, Grype)
- Secret detection (Gitleaks, TruffleHog)
- IaC security (Checkov)

## Triggers
- CODE_CHANGE_DETECTED
- PULL_REQUEST_OPENED
- SCHEDULED_EVENT (daily at 02:00 UTC)
- CONTAINER_BUILD_COMPLETED

## Behavior Contract

### Input Requirements
```yaml
required:
  - scan_type: str  # code, dependency, container, secrets, compliance
  - target_path: str
optional:
  - severity_filter: str
  - ignore_patterns: List[str]
  - compliance_standards: List[str]
```

### Output Format
```yaml
scan_result:
  scan_type: str
  timestamp: str
  findings:
    - id: str
      severity: str
      category: str
      title: str
      description: str
      file_path: str
      line_number: int
      remediation: str
      cve_id: str  # if applicable
  summary:
    total_findings: int
    critical: int
    high: int
    medium: int
    low: int
  compliance_status: str
  evidence_bundle: str  # path to artifacts
```

## Quality Gates
- Block deployment on critical vulnerabilities
- Require consensus for high severity issues
- Generate SARIF reports for GitHub Security
- Maintain 90-day audit trail

## Integration Points
- GitHub Security Advisory API
- CodeQL Analysis
- Semgrep Cloud
- NIST NVD Database
- Audit Trail Service

## Permissions
- contents: read
- security-events: write
- actions: read
