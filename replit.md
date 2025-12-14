# SynergyMesh

Next-generation cloud-native platform for intelligent business automation and seamless data orchestration.

## Project Overview

SynergyMesh is an autonomous coordination grid system (無人化自主協同網格系統) that combines AI agents, multi-agent orchestration, and enterprise automation capabilities.

## Project Architecture

This is a polyglot monorepo containing:

### Languages & Frameworks
- **TypeScript/JavaScript**: Frontend (React) and tooling
- **Python**: Core AI/ML modules, automation, and backend services
- **Rust**: High-performance runtime components (planned)
- **Go**: Microservices (planned)

### Directory Structure
```
apps/
  web/           # React frontend application (esbuild + Tailwind) - STATIC ONLY
  web-backend/   # Python backend services (moved from web/ for deployment compatibility)

core/
  modules/       # Python AI/automation modules
  safety_mechanisms/
  slsa_provenance/
  unified_integration/

mcp-servers/     # MCP server implementations
island-ai/       # Island AI components
tools/           # Development utilities
docs/            # Documentation
tests/           # Test suites
```

### Package Managers
- **npm**: Primary JavaScript package manager (workspaces in package.json)
- **pnpm**: Alternative JS package manager (pnpm-workspace.yaml)
- **pip/uv**: Python dependencies (pyproject.toml)

## Development

### Frontend
```bash
cd apps/web && npm run dev
```
- Runs on port 5000
- Uses esbuild for bundling
- Tailwind CSS for styling

### Python
```bash
pip install -e ".[dev]"
```

## Workflows

- **Frontend**: `cd apps/web && npm run dev` - React development server on port 5000

## Deployment

The frontend is configured for static deployment:
- Build: `npm run build --workspace apps/web`
- Output: `apps/web/dist/`

## Configuration Files

| File | Purpose |
|------|---------|
| `package.json` | npm workspaces configuration |
| `pnpm-workspace.yaml` | pnpm workspaces (synced with npm) |
| `pyproject.toml` | Python project configuration |
| `Cargo.toml` | Rust workspace (members pending) |
| `go.work` | Go workspace (modules pending) |
| `tsconfig.json` | TypeScript configuration |

## Notes

- Rust crates in Cargo.toml are commented out (pending implementation)
- Go services in go.work are commented out (pending implementation)
- Frontend binds to 0.0.0.0:5000 for Replit compatibility
