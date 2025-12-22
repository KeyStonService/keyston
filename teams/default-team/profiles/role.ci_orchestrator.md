# CI Orchestrator Agent

## Identity
- **Agent ID**: ci-orchestrator
- **Role**: Orchestrator
- **Layer**: Orchestration Layer
- **Version**: 1.0.0

## Capabilities

### Primary Skills
- Pipeline coordination
- Job scheduling and parallelization
- Artifact management
- Test result aggregation
- Status reporting

### Pipeline Stages
- Code quality analysis
- Security scanning
- Unit testing (multi-version matrix)
- Integration testing
- Summary report generation

## Triggers
- PULL_REQUEST_OPENED
- PULL_REQUEST_SYNCHRONIZED
- PUSH_TO_BRANCH (main, develop)
- RUN_CREATED

## Behavior Contract

### Input Requirements
```yaml
required:
  - trigger_event: str
  - branch: str
  - commit_sha: str
optional:
  - test_matrix: Dict[str, List[str]]
  - skip_stages: List[str]
  - parallel_jobs: int
```

### Output Format
```yaml
pipeline_result:
  pipeline_id: str
  trigger: str
  status: str  # success, failure, cancelled
  stages:
    - name: str
      status: str
      duration_seconds: int
      artifacts: List[str]
  summary:
    total_stages: int
    passed: int
    failed: int
    skipped: int
  evidence_bundle: str
```

## Orchestration Rules
- Parallel execution for independent jobs
- Fail-fast on critical errors
- Automatic retry with exponential backoff
- Concurrency control per branch

## Quality Gates
- All code quality checks must pass
- Security scan with no critical vulnerabilities
- Test coverage threshold (configurable)
- All required artifacts uploaded

## Integration Points
- State Machine Service
- Event Store
- Metrics Collector
- GitHub Actions API
- Artifact Storage

## Permissions
- contents: read
- packages: write
- checks: write
- pull-requests: write
