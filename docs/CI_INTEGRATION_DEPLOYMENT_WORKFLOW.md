# 🚀 Integration & Deployment Workflow Documentation

## Overview

The **Integration & Deployment** workflow (`integration-deployment.yml`) provides a comprehensive CI/CD pipeline for the MachineNativeOps platform, with a focus on the Tier 1 Contracts L1 Service and related npm workspace services.

## Purpose

This workflow was created to address CI failures in dependency installation and deployment processes, specifically for the Contracts L1 Service. It implements best practices for:

- **Reproducible Builds**: Using `npm ci` for consistent dependency installation
- **Multi-tier Service Management**: Separate stages for different service tiers
- **Integration Testing**: Comprehensive testing across workspaces
- **Deployment Readiness**: Automated preparation for production deployments

## Workflow Stages

### 1. Tier 1 - Contracts L1 Service 🏗️

**Purpose**: Build, test, and validate the core Contracts L1 Service

**Key Features**:
- Isolated working directory for the contract service
- Dependency installation with npm cache
- Code quality checks (format, lint, typecheck)
- Unit testing with coverage
- Build artifact generation
- SBOM (Software Bill of Materials) generation
- Security scanning

**Working Directory**: `src/core/contract_service/contracts-L1/contracts`

**Steps**:
1. Checkout code
2. Setup Node.js with caching
3. Install dependencies using `npm ci`
4. Verify installed packages
5. Format check
6. ESLint check
7. TypeScript type checking
8. Run unit tests
9. Build TypeScript to dist/
10. Generate SBOM
11. Security audit
12. Upload build artifacts
13. Generate service report

### 2. Tier 2 - Workspace Services 🔧

**Purpose**: Build and test other npm workspace services

**Strategy**: Matrix strategy for parallel processing

**Workspaces**:
- `src/mcp-servers`
- `src/core/advisory-database`

**Key Features**:
- Retry logic for `npm ci` (3 attempts)
- Fail-fast disabled for independent workspace testing
- Optional lint and test execution
- Conditional build steps

**Retry Mechanism**:
```yaml
for i in 1 2 3; do
  if npm ci --prefer-offline --no-audit; then
    break
  else
    echo "⚠️ npm ci failed (attempt $i/3)"
    if [ $i -eq 3 ]; then
      exit 1
    fi
    sleep 5
  fi
done
```

### 3. Integration Tests 🔗

**Purpose**: Validate integration between all services

**Dependencies**:
- Requires Tier 1 to succeed
- Runs after Tier 2 completes

**Steps**:
1. Install root dependencies
2. Install all workspace dependencies
3. Run integration test suite
4. Health checks across workspaces
5. Generate integration report

### 4. Deployment Preparation 🚀

**Purpose**: Prepare build artifacts for deployment

**Trigger Conditions**:
- Only on `push` events
- Only for `main` or `develop` branches

**Steps**:
1. Download build artifacts
2. Verify artifact completeness
3. Generate deployment report

### 5. Pipeline Summary 📋

**Purpose**: Aggregate results and provide visibility

**Features**:
- Runs with `if: always()` to execute even on failures
- Downloads all stage reports
- Generates comprehensive summary
- Posts PR comments on failures
- Uploads final summary report

**Failure Detection**:
```yaml
if: |
  github.event_name == 'pull_request' && 
  (contains(needs.*.result, 'failure') || contains(needs.*.result, 'cancelled'))
```

## Configuration

### Environment Variables

```yaml
env:
  NODE_VERSION: "20"
  PYTHON_VERSION: "3.11"
```

### Permissions

```yaml
permissions:
  contents: read
  packages: write
  checks: write
  pull-requests: write
```

### Concurrency Control

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
```

## Triggers

The workflow runs on:

1. **Push Events**:
   - `main` branch
   - `develop` branch

2. **Pull Request Events**:
   - `opened`
   - `synchronize`
   - `reopened`
   - Targeting `main` or `develop`

3. **Manual Dispatch**:
   - Via GitHub Actions UI

## Artifacts

### Generated Artifacts

| Artifact Name | Description | Retention |
|---------------|-------------|-----------|
| `contracts-l1-dist` | Build output from Contracts L1 Service | 7 days |
| `contracts-l1-report` | Service build and test report | 7 days |
| `integration-report` | Integration test results | 7 days |
| `deployment-preparation-report` | Deployment readiness report | 30 days |
| `pipeline-summary` | Overall pipeline summary | 30 days |

## Best Practices Implemented

### 1. Dependency Management

✅ **Use `npm ci` instead of `npm install`**
- Ensures reproducible builds
- Faster installation
- Validates package-lock.json

✅ **Implement retry logic**
- Handles transient network issues
- 3 attempts with 5-second delays
- Fails clearly after all attempts

✅ **Cache dependencies**
- Uses Node.js cache action
- Reduces installation time
- Cache key based on lock file

### 2. Error Handling

✅ **Non-blocking warnings**
- Optional steps don't fail the build
- Clear messaging for skipped steps

✅ **Detailed reporting**
- Stage-specific reports
- Aggregated summary
- PR comments on failures

✅ **Proper failure detection**
- Uses `contains(needs.*.result, 'failure')`
- Checks for cancelled jobs
- Accurate PR comment triggers

### 3. Security

✅ **Security scanning**
- npm audit at moderate level
- SBOM generation
- Audit reports in artifacts

✅ **CodeQL analysis**
- Automated on all commits
- No vulnerabilities detected

## Troubleshooting

### Common Issues

#### 1. Dependency Installation Failure

**Symptoms**: `npm ci` fails repeatedly

**Solution**:
- Check network connectivity
- Verify package-lock.json is committed
- Clear npm cache if needed
- Check for package version conflicts

#### 2. TypeScript Build Errors

**Symptoms**: `npm run build` fails

**Solution**:
- Run `npm run typecheck` locally
- Fix type errors in source files
- Ensure all dependencies are installed
- Check tsconfig.json configuration

#### 3. Test Failures

**Symptoms**: Tests fail in CI but pass locally

**Solution**:
- Check for environment-specific issues
- Verify test data and fixtures
- Review test timeouts
- Check for race conditions

#### 4. Artifact Upload Failures

**Symptoms**: Artifacts not uploaded or found

**Solution**:
- Verify dist/ directory exists
- Check file paths in upload action
- Ensure build step completed successfully
- Review artifact retention policies

## Monitoring

### Key Metrics

Track these metrics for workflow health:

1. **Success Rate**: % of successful workflow runs
2. **Build Time**: Total duration from start to finish
3. **Failure Points**: Which stages fail most often
4. **Artifact Size**: Size of generated artifacts

### Alerts

Configure alerts for:

- ❌ Repeated failures (>3 in a row)
- ⏱️ Excessive duration (>30 minutes)
- 🔒 Security vulnerabilities detected
- 📦 Artifact upload failures

## Maintenance

### Regular Tasks

**Weekly**:
- Review failed workflow runs
- Update dependencies if needed
- Check artifact storage usage

**Monthly**:
- Review and update Node.js version
- Update GitHub Actions versions
- Audit security scan results
- Optimize workflow performance

**Quarterly**:
- Review entire workflow structure
- Update documentation
- Benchmark against best practices
- Plan improvements

## Related Documentation

- [CI Pipeline Documentation](./ci.yml)
- [CD Pipeline Documentation](./cd.yml)
- [Contracts L1 Service Architecture](../src/core/contract_service/contracts-L1/contracts/ARCHITECTURE.md)
- [Workspace Configuration](../package.json)

## Support

For issues or questions:

1. Check this documentation
2. Review workflow run logs
3. Check CI Issues Fix Report
4. Create an issue with workflow run URL

---

**Last Updated**: 2025-12-21  
**Workflow Version**: 1.0.0  
**Maintainer**: MachineNativeOps Team
