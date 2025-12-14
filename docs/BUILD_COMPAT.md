# Build Compatibility Guide

## Overview

This document explains the build configuration for the SynergyMesh monorepo structure.

## Workspace Configuration

The `package.json` workspaces configuration:

```json
{
  "workspaces": [
    "mcp-servers",
    "core/contract_service/contracts-L1/contracts",
    "core/advisory-database",
    "frontend/ui"
  ]
}
```

## Directory Structure

The repository follows a clean, unified structure:

```
synergymesh/
├── core/                           # Core platform services
│   ├── advisory-database/         # Advisory database service
│   └── contract_service/          # Contract management services
│       └── contracts-L1/          # Layer 1 contracts
├── mcp-servers/                    # MCP server implementations
├── frontend/                       # Frontend applications
│   └── ui/                        # Main UI application
└── ...
```

## Path Aliases

The `tsconfig.json` includes path aliases for easier imports:

```json
{
  "compilerOptions": {
    "paths": {
      "@synergymesh/*": ["src/*"],
      "@core/*": ["core/*"],
      "@bridges/*": ["bridges/*"],
      "@automation/*": ["automation/*"],
      "@mcp/*": ["mcp-servers/*"],
      "@types/*": ["types/*"],
      "@utils/*": ["src/utils/*"]
    }
  }
}
```

## CI/CD Configuration

### GitHub Actions Workflow Paths

Workflow triggers use the core paths:

```yaml
on:
  push:
    paths:
      - 'core/**'
      - 'mcp-servers/**'
      - 'frontend/**'
```

## Testing

### Jest Configuration

The workspaces handle their own test configurations:

```bash
# Run all tests
npm run test

# Run tests for a specific workspace
npm run test --workspace=@synergymesh/contracts-l1
```

## Build Scripts

### NPM Scripts

Build scripts work across all workspaces:

```json
{
  "scripts": {
    "build": "npm run build --workspaces --if-present",
    "test": "npm run test --workspaces --if-present",
    "lint": "npm run lint --workspaces --if-present"
  }
}
```

## Docker Build

The `docker-compose.yml` configures services:

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d contracts-l1
docker-compose up -d mcp-servers
```

## Support

For build issues, refer to:

- [README.md](../README.md) - Project documentation
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
