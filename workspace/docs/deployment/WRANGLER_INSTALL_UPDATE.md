# Wrangler Installation & Update Guide

**Document Version**: 1.0.0  
**Last Updated**: 2026-01-03  
**Applicable System**: MachineNativeOps Platform - Cloudflare Workers

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Version Management](#version-management)
5. [Update Procedures](#update-procedures)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)
8. [Related Resources](#related-resources)

---

## 🎯 Overview

Wrangler is a command-line tool for building with Cloudflare developer products. This guide provides comprehensive instructions for installing and updating Wrangler within the MachineNativeOps platform.

### What is Wrangler?

Wrangler is the official CLI tool for:
- Building and deploying Cloudflare Workers
- Managing KV namespaces, D1 databases, and R2 buckets
- Local development and testing
- Secrets and environment variable management

### Why Local Installation?

The MachineNativeOps platform uses **local project installation** (rather than global) for Wrangler. This approach provides:

✅ **Version Control**: Team members use the same Wrangler version  
✅ **Project Isolation**: Different projects can use different Wrangler versions  
✅ **Rollback Capability**: Easy to revert to previous versions if needed  
✅ **CI/CD Consistency**: Same version in development and production  

---

## 🔧 System Requirements

### Operating System Support

Wrangler is supported on:
- **macOS**: 13.5 or later
- **Windows**: 11 or later
- **Linux**: Distributions that support glibc 2.35+

This follows [`workerd`'s OS support policy](https://github.com/cloudflare/workerd?tab=readme-ov-file#running-workerd).

### Node.js Requirements

Wrangler requires Node.js to be installed. We support running Wrangler with the [Current, Active, and Maintenance](https://nodejs.org/en/about/previous-releases) versions of Node.js.

**MachineNativeOps Requirements**:
- **Node.js**: >= 18.0.0 (as specified in `workspace/package.json`)
- **npm**: >= 8.0.0

### Recommended Setup

Use a Node version manager to avoid permission issues and easily switch between Node.js versions:

#### Option 1: Volta (Recommended)
```bash
# Install Volta
curl https://get.volta.sh | bash

# Install Node.js
volta install node@18
```

#### Option 2: nvm
```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Install Node.js
nvm install 18
nvm use 18
```

### Runtime Environment

**Important**: Your Worker will always be executed in `workerd`, the open source Cloudflare Workers runtime, regardless of your local Node.js version.

---

## 📦 Installation

### Installation Location

In the MachineNativeOps platform, Wrangler is installed at **two levels**:

1. **Root workspace** (`workspace/package.json`) - for global CLI commands
2. **Workers project** (`workspace/cloudflare/workers/package.json`) - for project-specific version

Both installations ensure consistency across the platform.

### Installation Methods

#### Method 1: npm (Default)

```bash
# Navigate to workspace root
cd /path/to/machine-native-ops/workspace

# Install Wrangler as dev dependency
npm install -D wrangler@latest

# Or install in workers project
cd cloudflare/workers
npm install -D wrangler@latest
```

#### Method 2: yarn

```bash
# In workspace root
yarn add -D wrangler@latest

# Or in workers project
cd cloudflare/workers
yarn add -D wrangler@latest
```

#### Method 3: pnpm

```bash
# In workspace root
pnpm add -D wrangler@latest

# Or in workers project
cd cloudflare/workers
pnpm add -D wrangler@latest
```

### Complete Installation Process

For a fresh installation in the MachineNativeOps platform:

```bash
# 1. Clone the repository
git clone https://github.com/MachineNativeOps/machine-native-ops.git
cd machine-native-ops

# 2. Install all workspace dependencies (includes Wrangler)
cd workspace
npm install

# 3. Verify Wrangler installation
npx wrangler --version
```

### Current Version in MachineNativeOps

The platform currently uses:
- **Root workspace**: `wrangler@^4.54.0`
- **Workers project**: `wrangler@^4.56.0`

Check `workspace/package.json` and `workspace/cloudflare/workers/package.json` for the exact versions.

---

## 🔍 Version Management

### Check Your Wrangler Version

```bash
# Method 1: Using npx
npx wrangler --version

# Method 2: Short form
npx wrangler -v

# Method 3: From workers directory
cd workspace/cloudflare/workers
npm run dev -- --version
```

Expected output:
```
⛅️ wrangler 4.56.0
```

### Check Installed Location

```bash
# Check which Wrangler is being used
which wrangler

# Or check the local installation
npm list wrangler
```

### Version Consistency Check

Ensure all team members use the same version:

```bash
# In workspace root
npm list wrangler --depth=0

# In workers project
cd cloudflare/workers
npm list wrangler --depth=0
```

---

## 🔄 Update Procedures

### Update to Latest Version

#### Method 1: npm

```bash
# Update in workspace root
npm install -D wrangler@latest

# Update in workers project
cd cloudflare/workers
npm install -D wrangler@latest
```

#### Method 2: yarn

```bash
# Update in workspace root
yarn add -D wrangler@latest

# Update in workers project
cd cloudflare/workers
yarn add -D wrangler@latest
```

#### Method 3: pnpm

```bash
# Update in workspace root
pnpm add -D wrangler@latest

# Update in workers project
cd cloudflare/workers
pnpm add -D wrangler@latest
```

### Update to Specific Version

```bash
# Install specific version
npm install -D wrangler@4.56.0

# Or use version range
npm install -D wrangler@^4.50.0
```

### Update All Workspace Dependencies

```bash
# From repository root
cd workspace
npm update

# Or update only Wrangler
npm update wrangler
```

### Update Verification

After updating, verify the new version:

```bash
# Check version
npx wrangler --version

# Test basic functionality
npx wrangler whoami

# Test local development
cd cloudflare/workers
npm run dev
```

### Update Best Practices

1. **Check Release Notes**: Review [Wrangler releases](https://github.com/cloudflare/workers-sdk/releases) for breaking changes
2. **Update Dev First**: Test in development environment before production
3. **Update package-lock.json**: Commit the updated lock file
4. **Test Deployments**: Run `npm run build` and test deployments after updating
5. **Team Communication**: Notify team members of version updates

---

## ✅ Verification

### Installation Verification

After installing or updating Wrangler, verify the installation:

```bash
# 1. Check version
npx wrangler --version

# 2. Check authentication status
npx wrangler whoami

# 3. Test local development
cd workspace/cloudflare/workers
npm run dev

# 4. Check available commands
npx wrangler --help
```

### Functionality Tests

Test core Wrangler functionality:

```bash
# List KV namespaces
npx wrangler kv:namespace list

# List D1 databases
npx wrangler d1 list

# List R2 buckets
npx wrangler r2 bucket list

# View deployment status
npx wrangler deployments list
```

### Integration Test

Run the complete integration test:

```bash
# From workspace root
npm run cf:dev

# Or use the convenience script
npm run dev:stack
```

Expected behavior:
- Wrangler dev server starts on `http://localhost:8787`
- No errors in console
- Health endpoint accessible: `curl http://localhost:8787/health`

---

## 🚨 Troubleshooting

### Common Issues

#### Issue 1: "wrangler: command not found"

**Cause**: Wrangler is not installed or not in PATH

**Solution**:
```bash
# Verify installation
npm list wrangler

# If not installed, install it
npm install -D wrangler@latest

# Use npx to run
npx wrangler --version
```

#### Issue 2: Permission Errors

**Cause**: Global npm installation without proper permissions

**Solution**:
```bash
# Use local installation (recommended)
npm install -D wrangler@latest

# Or fix npm permissions
# See: https://docs.npmjs.com/resolving-eacces-permissions-errors
```

#### Issue 3: Version Mismatch

**Cause**: Different versions in workspace vs workers project

**Solution**:
```bash
# Check both locations
npm list wrangler --depth=0
cd cloudflare/workers && npm list wrangler --depth=0

# Synchronize versions
npm install -D wrangler@4.56.0
cd cloudflare/workers && npm install -D wrangler@4.56.0
```

#### Issue 4: "npx wrangler" Uses Wrong Version

**Cause**: When Wrangler is not installed locally, `npx wrangler` will download and use the latest version

**Warning**: ⚠️ If Wrangler is not installed, running `npx wrangler` will use the latest version of Wrangler, which may differ from your project's specified version.

**Solution**:
```bash
# Always install Wrangler locally first
npm install -D wrangler@latest

# Then use npx
npx wrangler --version
```

#### Issue 5: Node.js Version Incompatibility

**Cause**: Using an unsupported Node.js version

**Solution**:
```bash
# Check Node.js version
node --version

# Should be >= 18.0.0
# If not, use nvm or volta to update
nvm install 18
nvm use 18

# Then reinstall Wrangler
npm install -D wrangler@latest
```

#### Issue 6: Build Errors After Update

**Cause**: Breaking changes in new Wrangler version

**Solution**:
```bash
# Check release notes
# https://github.com/cloudflare/workers-sdk/releases

# Rollback to previous version
npm install -D wrangler@4.54.0

# Or fix compatibility issues
# Review migration guide in release notes
```

### Getting Help

If you encounter issues not covered here:

1. **Check Documentation**:
   - [Wrangler Documentation](https://developers.cloudflare.com/workers/wrangler/)
   - [Cloudflare Workers Discord](https://discord.gg/cloudflaredev)

2. **Check MachineNativeOps Docs**:
   - [Cloudflare Deployment Guide](../CLOUDFLARE_DEPLOYMENT_FIX.md)
   - [Cloudflare GitHub Integration](./CLOUDFLARE_GITHUB_INTEGRATION.md)

3. **Report Issues**:
   - [MachineNativeOps Issues](https://github.com/MachineNativeOps/machine-native-ops/issues)
   - [Wrangler Issues](https://github.com/cloudflare/workers-sdk/issues)

---

## 🔗 Related Resources

### MachineNativeOps Documentation

- **[Cloudflare Deployment Guide](../CLOUDFLARE_DEPLOYMENT_FIX.md)** - Troubleshooting deployment issues
- **[Cloudflare GitHub Integration](./CLOUDFLARE_GITHUB_INTEGRATION.md)** - Complete integration guide
- **[Deployment Guide](./DEPLOYMENT_GUIDE.md)** - General deployment procedures
- **[Deployment Checklist](./DEPLOYMENT_CHECKLIST.md)** - Pre-deployment validation

### Official Cloudflare Resources

- **[Wrangler Commands](https://developers.cloudflare.com/workers/wrangler/commands/)** - Complete command reference
- **[Wrangler Configuration](https://developers.cloudflare.com/workers/wrangler/configuration/)** - Configuration file documentation
- **[Workers Documentation](https://developers.cloudflare.com/workers/)** - Cloudflare Workers guides
- **[Workers SDK Repository](https://github.com/cloudflare/workers-sdk)** - Source code and issues

### Package Manager Resources

- **[npm Documentation](https://docs.npmjs.com/)** - npm package manager
- **[yarn Documentation](https://yarnpkg.com/)** - Yarn package manager
- **[pnpm Documentation](https://pnpm.io/)** - pnpm package manager

### Node.js Version Managers

- **[Volta](https://volta.sh/)** - Fast, reliable Node.js version manager
- **[nvm](https://github.com/nvm-sh/nvm)** - Node Version Manager

---

## 📝 Quick Reference

### Essential Commands

```bash
# Install Wrangler
npm install -D wrangler@latest

# Check version
npx wrangler --version

# Update Wrangler
npm install -D wrangler@latest

# Start local dev server
npm run cf:dev

# Deploy to production
npm run cf:deploy:production

# View live logs
npm run cf:tail:production
```

### Package.json Scripts

The following scripts are available in `workspace/package.json`:

| Script | Command | Description |
|--------|---------|-------------|
| `cf:dev` | `cd cloudflare/workers && npm run dev` | Start local dev server |
| `cf:deploy` | `wrangler deploy` | Deploy to default environment |
| `cf:deploy:staging` | `wrangler deploy --env staging` | Deploy to staging |
| `cf:deploy:production` | `wrangler deploy --env production` | Deploy to production |
| `cf:tail` | `wrangler tail` | View live logs |
| `cf:tail:production` | `wrangler tail --env production` | View production logs |
| `cf:login` | `wrangler login` | Authenticate with Cloudflare |
| `cf:whoami` | `wrangler whoami` | Check authentication status |

### How to Run Wrangler Commands

Since Wrangler is installed locally (not globally), use one of these methods:

#### Method 1: npx (Recommended)
```bash
npx wrangler <command>
```

#### Method 2: npm scripts
```bash
npm run cf:<script>
```

#### Method 3: package.json scripts
```bash
# From workspace root
cd workspace/cloudflare/workers
npm run dev
```

#### Method 4: Direct path
```bash
./node_modules/.bin/wrangler <command>
```

---

## 🎯 Next Steps

After installing Wrangler:

1. **Authenticate**: Run `npx wrangler login` to authenticate with Cloudflare
2. **Configure**: Review and update `wrangler.toml` configuration
3. **Develop**: Start local development with `npm run cf:dev`
4. **Deploy**: Follow the [Cloudflare GitHub Integration Guide](./CLOUDFLARE_GITHUB_INTEGRATION.md)

---

**Document Status**: ✅ Complete  
**Maintained By**: MachineNativeOps Team  
**Last Review**: 2026-01-03
