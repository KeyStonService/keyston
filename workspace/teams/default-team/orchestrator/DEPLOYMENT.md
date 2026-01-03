# SuperAgent Deployment Guide

This guide explains how to deploy the SuperAgent using Kustomize-based deployment strategy with environment-specific configurations.

## Overview

SuperAgent uses **Kustomize** to manage Kubernetes deployments across multiple environments (dev, staging, prod). This approach provides:

- ✅ **Easy version management** - Update image tags in one place per environment
- ✅ **Environment-specific configuration** - Different replicas, resources, and settings per environment
- ✅ **DRY principle** - Base configuration shared across all environments
- ✅ **GitOps friendly** - All configuration is declarative and version-controlled

## Directory Structure

```
k8s/
├── base/                       # Base Kubernetes manifests
│   ├── deployment.yaml        # Base deployment with all resources
│   └── kustomization.yaml     # Base Kustomize config
└── overlays/                  # Environment-specific overlays
    ├── dev/
    │   └── kustomization.yaml # Dev-specific overrides
    ├── staging/
    │   └── kustomization.yaml # Staging-specific overrides
    └── prod/
        └── kustomization.yaml # Prod-specific overrides
```

## Environment Configuration

### Development (dev)

- **Namespace**: `machinenativeops-dev`
- **Image Tag**: `dev-latest`
- **Replicas**: 1
- **Log Level**: DEBUG
- **Resources**: Standard (128Mi/100m CPU)

**Use case**: Local development and testing

### Staging (staging)

- **Namespace**: `machinenativeops-staging`
- **Image Tag**: `v1.0.0-rc` (release candidate)
- **Replicas**: 2
- **Log Level**: INFO
- **Resources**: Standard (128Mi/100m CPU)

**Use case**: Pre-production testing and validation

### Production (prod)

- **Namespace**: `machinenativeops`
- **Image Tag**: `v1.0.0` (stable release)
- **Replicas**: 3
- **Log Level**: WARN
- **Resources**: Enhanced (256Mi/200m CPU requests, 1Gi/1000m limits)

**Use case**: Production workloads

## Quick Start

### Using the Deployment Script (Recommended)

The easiest way to deploy is using the provided `deploy.sh` script:

```bash
# Deploy to development
./deploy.sh dev

# Deploy to staging
./deploy.sh staging

# Deploy to production
./deploy.sh prod
```

The script will:

1. ✅ Build the Docker image
2. ✅ Test the image locally
3. ✅ Deploy to Kubernetes using Kustomize
4. ✅ Wait for deployment to be ready
5. ✅ Run integration tests

### Manual Deployment with kubectl

You can also deploy manually using kubectl's built-in Kustomize support:

```bash
# Deploy to dev
kubectl apply -k k8s/overlays/dev

# Deploy to staging
kubectl apply -k k8s/overlays/staging

# Deploy to prod
kubectl apply -k k8s/overlays/prod
```

### Manual Deployment with Kustomize CLI

If you have the standalone `kustomize` CLI installed:

```bash
# Build and apply dev configuration
kustomize build k8s/overlays/dev | kubectl apply -f -

# Build and apply staging configuration
kustomize build k8s/overlays/staging | kubectl apply -f -

# Build and apply prod configuration
kustomize build k8s/overlays/prod | kubectl apply -f -
```

## Updating Image Versions

### Quick Version Update

To update the image version for a specific environment, edit the corresponding overlay's `kustomization.yaml`:

**For production:**

```yaml
# k8s/overlays/prod/kustomization.yaml
images:
- name: machinenativeops/super-agent
  newTag: v1.1.0  # Change this to the new version
```

Then redeploy:

```bash
./deploy.sh prod
```

**For staging:**

```yaml
# k8s/overlays/staging/kustomization.yaml
images:
- name: machinenativeops/super-agent
  newTag: v1.1.0-rc  # Update to new release candidate
```

**For dev:**

```yaml
# k8s/overlays/dev/kustomization.yaml
images:
- name: machinenativeops/super-agent
  newTag: dev-latest  # Usually kept as latest or specific dev build
```

### Version Management Best Practices

1. **Development**: Use `dev-latest` or date-based tags (`dev-20251221`)
2. **Staging**: Use release candidates (`v1.0.0-rc`, `v1.1.0-rc1`)
3. **Production**: Use stable semver tags (`v1.0.0`, `v1.1.0`)

## Verification

### Check Deployment Status

```bash
# For dev
kubectl get pods -n machinenativeops-dev -l app.kubernetes.io/name=super-agent
kubectl get deploy -n machinenativeops-dev dev-super-agent

# For staging
kubectl get pods -n machinenativeops-staging -l app.kubernetes.io/name=super-agent
kubectl get deploy -n machinenativeops-staging staging-super-agent

# For prod
kubectl get pods -n machinenativeops -l app.kubernetes.io/name=super-agent
kubectl get deploy -n machinenativeops super-agent
```

### View Logs

```bash
# Dev
kubectl logs -n machinenativeops-dev -l app.kubernetes.io/name=super-agent -f

# Staging
kubectl logs -n machinenativeops-staging -l app.kubernetes.io/name=super-agent -f

# Prod
kubectl logs -n machinenativeops -l app.kubernetes.io/name=super-agent -f
```

### Port Forward and Test

```bash
# Dev
kubectl port-forward -n machinenativeops-dev svc/dev-super-agent 8080:8080

# Staging
kubectl port-forward -n machinenativeops-staging svc/staging-super-agent 8080:8080

# Prod
kubectl port-forward -n machinenativeops svc/super-agent 8080:8080

# Then test
python3 test_super_agent.py http://localhost:8080
```

## Preview Changes

Before applying changes, you can preview the generated manifests:

```bash
# Preview dev configuration
kubectl kustomize k8s/overlays/dev

# Preview staging configuration
kubectl kustomize k8s/overlays/staging

# Preview prod configuration
kubectl kustomize k8s/overlays/prod
```

Or with standalone kustomize:

```bash
kustomize build k8s/overlays/dev
kustomize build k8s/overlays/staging
kustomize build k8s/overlays/prod
```

## Rollback

### Using kubectl

```bash
# Rollback to previous version in prod
kubectl rollout undo deployment/super-agent -n machinenativeops

# Rollback to specific revision
kubectl rollout history deployment/super-agent -n machinenativeops
kubectl rollout undo deployment/super-agent -n machinenativeops --to-revision=2
```

### Using Git

Since all configuration is in Git, you can also:

1. Revert the `kustomization.yaml` change in Git
2. Redeploy using `./deploy.sh <env>`

## Advanced Configuration

### Adding New Environment Variables

Edit the overlay's `kustomization.yaml` and add to the patches section:

```yaml
patches:
- patch: |-
    - op: add
      path: /spec/template/spec/containers/0/env/-
      value:
        name: MY_NEW_VAR
        value: my-value
  target:
    kind: Deployment
    name: super-agent
```

### Adjusting Resources

For production, resources are already enhanced in the overlay. To adjust:

```yaml
patches:
- patch: |-
    - op: replace
      path: /spec/template/spec/containers/0/resources/limits/memory
      value: 2Gi
    - op: replace
      path: /spec/template/spec/containers/0/resources/limits/cpu
      value: "2000m"
  target:
    kind: Deployment
    name: super-agent
```

### Changing Replica Count

Edit the overlay's `kustomization.yaml`:

```yaml
replicas:
- name: super-agent
  count: 5  # Increase to 5 replicas
```

## Troubleshooting

### Kustomize Build Fails

Check the YAML syntax in your kustomization files:

```bash
# Validate syntax
kubectl kustomize k8s/overlays/dev --enable-alpha-plugins
```

### Image Not Found

Ensure the image exists in your registry:

```bash
docker images | grep super-agent
```

Build if needed:

```bash
docker build -t machinenativeops/super-agent:v1.0.0 .
```

### Deployment Not Starting

Check pod events:

```bash
kubectl describe pod -n machinenativeops -l app.kubernetes.io/name=super-agent
```

Check logs:

```bash
kubectl logs -n machinenativeops -l app.kubernetes.io/name=super-agent --tail=50
```

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Deploy to staging
  run: |
    ./deploy.sh staging
  if: github.ref == 'refs/heads/develop'

- name: Deploy to production
  run: |
    ./deploy.sh prod
  if: github.ref == 'refs/heads/main'
```

### ArgoCD

Create an ArgoCD Application for each environment:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: super-agent-prod
spec:
  source:
    repoURL: https://github.com/your-org/your-repo
    targetRevision: main
    path: agents/super-agent/k8s/overlays/prod
  destination:
    server: https://kubernetes.default.svc
    namespace: machinenativeops
```

## Additional Resources

- [Kustomize Documentation](https://kustomize.io/)
- [kubectl Kustomize Integration](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/)
- [SuperAgent README](./README.md)
- [MachineNativeOps Architecture](../../docs/architecture.md)
