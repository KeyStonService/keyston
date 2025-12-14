# SynergyMesh Directory Structure Guide

## Overview

This document describes the repository structure for the SynergyMesh project.

## Current Directory Structure

```
synergymesh/
├── .github/                    # GitHub configurations
│   └── workflows/             # CI/CD workflows
├── core/                       # Core platform services
│   ├── advisory-database/     # Advisory database service
│   └── contract_service/      # Contract management
│       └── contracts-L1/      # Layer 1 contracts
├── mcp-servers/               # MCP server implementations
├── frontend/                  # Frontend applications
│   └── ui/                    # Main UI application
├── automation/                # Automation tools
├── bridges/                   # Language and system bridges
├── config/                    # System configurations
├── docs/                      # Documentation
├── docker-templates/          # Docker template files
├── governance/                # Governance policies
├── infra/                     # Infrastructure configurations
├── infrastructure/            # Infrastructure as code
├── scripts/                   # Utility scripts
├── shared/                    # Shared utilities
├── tests/                     # Test suites
├── tools/                     # Development tools
├── v1-python-drones/          # v1 automation system (Python)
├── v2-multi-islands/          # v2 multi-language automation
├── docker-compose.yml         # Production Docker Compose
├── docker-compose.dev.yml     # Development Docker Compose
├── package.json               # Root package configuration
└── tsconfig.json              # TypeScript configuration
```

## Workspace Configuration

The npm workspaces are configured as:

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

## Key Directories

### Core Services (`core/`)

- **advisory-database/**: Security advisory database and management
- **contract_service/**: Contract management services
  - **contracts-L1/contracts/**: Layer 1 contract service (main TypeScript service)

### MCP Servers (`mcp-servers/`)

Model Context Protocol server implementations for:

- Code analysis
- Security scanning
- Test generation
- Documentation generation

### Frontend (`frontend/`)

- **ui/**: Main user interface application

### Automation Systems

- **v1-python-drones/**: Python-based automation (conceptual architecture)
- **v2-multi-islands/**: Multi-language automation system (conceptual architecture)

## Build Commands

```bash
# Install dependencies
npm install

# Build all workspaces
npm run build

# Run all tests
npm run test

# Lint all workspaces
npm run lint
```

## Docker Deployment

```bash
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d contracts-l1
docker-compose up -d mcp-servers
docker-compose up -d dashboard
```

## CI/CD Workflows

Key workflows in `.github/workflows/`:

- **core-services-ci.yml**: CI for core services
- **reusable-ci.yml**: Reusable CI pipeline
- **project-cd.yml**: Reusable CD pipeline
- **contracts-cd.yml**: Contracts service CD
- **mcp-servers-cd.yml**: MCP Servers CD
- **integration-deployment.yml**: Full integration & deployment

## Related Documentation

- [BUILD_COMPAT.md](./BUILD_COMPAT.md) - Build configuration guide
- [README.md](../README.md) - Project overview
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
