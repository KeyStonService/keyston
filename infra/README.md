# Infrastructure Directory

This directory contains infrastructure configurations for SynergyMesh.

## Structure

```
infra/
├── infrastructure/   # Infrastructure configurations
├── config/          # System configurations
└── runtime-profiles/ # Runtime environment profiles
```

## Components

### Infrastructure (`infrastructure/`)
Infrastructure definitions including:
- Kubernetes configurations
- Monitoring setup
- Canary deployments
- Drift detection

### Config (`config/`)
System configurations:
- AI constitution
- Auto-fix bot settings
- Cloud agent delegation
- Monitoring configurations
- Security settings

### Runtime Profiles (`runtime-profiles/`)
Runtime environment profiles for:
- Development environments
- Staging environments
- Production environments

## See Also

- [Migration Guide](../docs/MIGRATION.md)
- [Deployment Infrastructure](../docs/architecture/DEPLOYMENT_INFRASTRUCTURE.md)
