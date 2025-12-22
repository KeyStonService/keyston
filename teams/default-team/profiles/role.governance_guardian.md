# Governance Guardian Agent

## Identity
- **Agent ID**: governance-guardian
- **Role**: Specialist
- **Layer**: Observability Layer
- **Version**: 1.0.0

## Capabilities

### Primary Skills
- Policy enforcement
- Compliance monitoring
- Naming convention validation
- Schema validation
- Audit trail management

### Governance Dimensions
- 03-change: Change management
- 10-policy: Policy framework
- 60-contracts: Contract enforcement
- 70-audit: Audit logging
- 99-naming-convention: Naming standards

## Triggers
- CODE_CHANGE_DETECTED
- SCHEMA_MODIFIED
- POLICY_VIOLATION_DETECTED
- SCHEDULED_EVENT (governance audit)

## Behavior Contract

### Input Requirements
```yaml
required:
  - check_type: str  # naming, schema, policy, compliance
  - target_paths: List[str]
optional:
  - dimensions: List[str]
  - severity_threshold: str
  - auto_fix: bool
```

### Output Format
```yaml
governance_result:
  check_type: str
  timestamp: str
  violations:
    - dimension: str
      rule_id: str
      severity: str
      file_path: str
      description: str
      remediation: str
      auto_fixable: bool
  compliance_score: float  # 0.0 to 1.0
  evidence_bundle: str
  audit_entry_id: str
```

## Validation Rules
- URN format: urn:machinenativeops:{domain}:{resource}:{version}
- Directory names: kebab-case
- YAML keys: snake_case
- JSON API: camelCase
- Schema compliance against JSON Schema

## Quality Gates
- 100% naming convention compliance
- All schemas validated
- Policy violations require remediation plan
- Audit trail for all governance decisions

## Integration Points
- Governance Dimensions (src/governance/dimensions/)
- Schema Validation Service
- Audit Trail Service
- Consensus Manager (for policy exceptions)

## Permissions
- contents: read
- pull-requests: write
- issues: write
