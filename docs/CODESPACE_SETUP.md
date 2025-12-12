# GitHub Codespace Setup

## Overview

This document describes the default GitHub Codespace configuration for the
SynergyMesh project.

## Configuration Files

### `.devcontainer/devcontainer.json`

The development container configuration includes:

- **Base Image**:
  `mcr.microsoft.com/devcontainers/typescript-node:1-18-bullseye`
- **Node.js Version**: 18+ (matching project requirements)
- **Features**:
  - Node.js 18
  - Git (latest)
  - GitHub CLI (latest)

### `.vscode/settings.json`

VS Code workspace settings include:

- **Formatter**: Prettier (default formatter)
- **Format on Save**: Enabled
- **Indentation**: 2 spaces
- **ESLint**: Auto-fix on save
- **TypeScript**: Relative imports, auto-update imports on file move
- **File Exclusions**: node_modules, dist, .git (from search and explorer)

### `.vscode/extensions.json`

Recommended extensions for the project:

- **ESLint**: Code linting
- **Prettier**: Code formatting
- **TypeScript**: Language support
- **Island AI**: AI-powered code completion
- **Jest**: Testing framework support
- **JSON/YAML**: Configuration file support

## Features

### Port Forwarding

The following ports are automatically forwarded:

- `3000`: Main application server
- `3001`: Additional service port

### Post-Create Command

When the container is created, `npm install` is automatically run to install
dependencies.

### User

The container runs as the `node` user for security best practices.

## Usage

### Opening in Codespace

1. Navigate to the repository on GitHub
2. Click the "Code" button
3. Select "Codespaces" tab
4. Click "Create codespace on [branch]"

The container will automatically:

- Set up the Node.js 18 environment
- Install all recommended VS Code extensions
- Run `npm install` to install dependencies
- Configure TypeScript, ESLint, and Prettier

### Manual Setup (Local VS Code)

If using VS Code with the Dev Containers extension locally:

1. Install Docker Desktop
2. Install the "Dev Containers" extension in VS Code
3. Open the repository in VS Code
4. Press `F1` and select "Dev Containers: Reopen in Container"

## Customization

To customize the configuration:

1. Edit `.devcontainer/devcontainer.json` for container settings
2. Edit `.vscode/settings.json` for VS Code workspace settings
3. Edit `.vscode/extensions.json` to add/remove recommended extensions

## Troubleshooting

### Container Build Issues

If the container fails to build:

1. Check the Docker daemon is running
2. Verify network connectivity
3. Try rebuilding with `Dev Containers: Rebuild Container`

### Extension Issues

If recommended extensions don't install:

1. Check the VS Code marketplace is accessible
2. Manually install extensions from the Extensions panel
3. Verify extension IDs in `.vscode/extensions.json`

## References

- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [GitHub Codespaces](https://docs.github.com/en/codespaces)
- [Dev Container Specification](https://containers.dev/)
