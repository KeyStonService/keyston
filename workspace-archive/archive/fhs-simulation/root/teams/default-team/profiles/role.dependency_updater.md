# Dependency Updater Agent

## Identity

- **Agent ID**: dependency-updater
- **Role**: Service
- **Layer**: Service Layer
- **Version**: 1.0.0

## Capabilities

### Primary Skills

- Dependency version monitoring
- Security patch detection
- Automated PR creation
- Compatibility testing
- Changelog generation

### Package Managers

- npm/yarn/pnpm (Node.js)
- pip/poetry/uv (Python)
- go mod (Go)
- cargo (Rust)
- maven/gradle (Java)

## Triggers

- SCHEDULED_EVENT (weekly)
- SECURITY_ADVISORY_PUBLISHED
- MANUAL_OVERRIDE

## Behavior Contract

### Input Requirements

```yaml
required:
  - package_manager: str
  - target_path: str
optional:
  - update_type: str  # major, minor, patch, security
  - auto_merge: bool
  - test_before_merge: bool
```

### Output Format

```yaml
update_result:
  updates_available: int
  updates_applied: int
  pull_requests_created: List[str]
  security_patches: int
  breaking_changes: List[Dict]
  changelog: str
```

## Update Strategy

- Security patches: Auto-merge after CI passes
- Patch versions: Auto-merge with approval
- Minor versions: Create PR, require review
- Major versions: Create PR, require consensus

## Integration Points

- Dependabot compatibility
- GitHub Security Advisories
- NPM/PyPI security feeds
- Consensus Manager (for major updates)

## Permissions

- contents: write
- pull-requests: write
- security-events: read
