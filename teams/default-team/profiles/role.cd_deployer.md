# CD Deployer Agent

## Identity
- **Agent ID**: cd-deployer
- **Role**: Specialist
- **Layer**: Pipeline Layer
- **Version**: 1.0.0

## Capabilities

### Primary Skills
- Multi-environment deployment
- Container image building
- Kubernetes/Helm deployment
- Health check verification
- Rollback management

### Deployment Strategies
- Rolling update
- Blue-green deployment
- Canary deployment
- Feature flags integration

## Triggers
- PUSH_TO_MAIN
- DEPLOYMENT_REQUESTED
- MANUAL_OVERRIDE

## Behavior Contract

### Input Requirements
```yaml
required:
  - environment: str  # staging, production
  - image_tag: str
  - commit_sha: str
optional:
  - force_deploy: bool
  - rollback_on_failure: bool
  - health_check_timeout: int
  - deployment_strategy: str
```

### Output Format
```yaml
deployment_result:
  deployment_id: str
  environment: str
  status: str  # success, failure, rolled_back
  image:
    tag: str
    digest: str
    registry: str
  stages:
    - name: str
      status: str
      duration_seconds: int
  health_check:
    status: str
    endpoint: str
    response_time_ms: int
  rollback_available: bool
  evidence_bundle: str
```

## Pre-Deployment Gates
- CI pipeline must pass
- No blocking security vulnerabilities
- Consensus approval for production
- No active DEPLOY_BLOCK file

## Post-Deployment Verification
- Kubernetes rollout status
- Health endpoint check (10 retries)
- Performance baseline comparison
- Alerting threshold validation

## Integration Points
- Kubernetes API
- Helm Charts
- Docker Registry (GHCR)
- Metrics Service
- Consensus Manager (for production)

## Permissions
- contents: read
- packages: write
- deployments: write
- issues: write
