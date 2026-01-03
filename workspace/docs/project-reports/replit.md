# Unmanned Island System (MachineNativeOps)

## Overview

Unmanned Island System is a next-generation cloud-native intelligent automation platform designed to achieve "zero-touch operations" for enterprise environments. The platform integrates three core subsystems:

1. **SynergyMesh Core Engine** - AI decision engine with cognitive processors and service registries
2. **Structural Governance** - Schema namespaces, 10-stage pipelines, and SLSA provenance
3. **Autonomous Framework** - Five-skeleton architecture for drone control and autonomous vehicle integration

The system targets 95%+ automation rate, 100% governance compliance, 99.9%+ availability, and 99.99%+ SLA for enterprise-grade reliability.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Multi-Language Stack

- **Primary Language**: TypeScript (strict mode) for core services and web applications
- **Secondary Languages**: Python 3.10+ for automation/AI tooling, Go for observability agents, C++/Rust for ROS/drone components
- **Package Manager**: npm with workspaces for the monorepo structure

### Workspace Organization

The repository uses npm workspaces defined in the root `package.json`:

- `src/mcp-servers` - MCP server implementations
- `src/core/contract_service/contracts-L1/contracts` - Express + Zod + Sigstore contract service
- `src/core/advisory-database` - Advisory database service
- `src/apps/web` - React frontend with Vite, Tailwind CSS, and shadcn/ui components
- `src/ai/src/ai` - AI-related modules

### Configuration Strategy

- **Primary Config**: `machinenativeops.yaml` (with `synergymesh.yaml` as compatibility symlink)
- **System Manifest**: `config/system-manifest.yaml` for module registry
- **Unified Index**: `config/unified-config-index.yaml` for configuration discovery
- All configurations should be treated as source of truth

### Backend Architecture

- **Framework**: Express.js with TypeScript
- **Validation**: Zod schemas for request/response validation
- **Security**: Sigstore for signing and verification, SLSA provenance
- **Pattern**: Controller + Service + Middleware layers

### Frontend Architecture

- **Build Tool**: Vite with React
- **Styling**: Tailwind CSS with shadcn/ui components
- **Path Aliases**: `@/` for client source, `@shared/` for shared modules

### Database

- **ORM**: Drizzle with PostgreSQL dialect
- **Config Location**: `config/drizzle.config.ts`
- **Schema Location**: `shared/schema.ts`
- **Migrations**: `./migrations` directory

### Key Development Commands

- `npm install` - Install all workspace dependencies
- `npm run lint` - Run ESLint across all workspaces
- `npm run test` - Run tests across all workspaces
- `npm run build` - Build all workspaces
- `npm run dev:stack` - Start development stack via shell script
- `npm run docs:lint` - Validate Markdown documentation

### AI Agent Behavior

The repository includes an AI Behavior Contract (`.github/AI-BEHAVIOR-CONTRACT.md`) that enforces:

- No vague excuses - use concrete, specific language
- Binary responses - CAN_COMPLETE or CANNOT_COMPLETE with specifics
- Proactive task decomposition for large tasks
- Draft mode by default for file modifications

## External Dependencies

### Third-Party Services

- **GitHub Actions** - CI/CD workflows with SLSA provenance
- **Sigstore** - Code signing and verification
- **Docker** - Container builds and deployments
- **Kubernetes** - Production orchestration

### Key NPM Dependencies

- **Express** - HTTP server framework
- **Zod** - Runtime type validation
- **Drizzle ORM** - Database operations
- **React 18** - Frontend UI library
- **Radix UI** - Accessible component primitives
- **Tailwind CSS** - Utility-first styling

### Python Dependencies

- **FastAPI/Uvicorn** - Python API services
- **Pydantic** - Data validation
- **PyYAML** - Configuration parsing
- **Pytest** - Testing framework

### Monitoring & Observability

- **Prometheus** - Metrics collection (config at `config/prometheus-config.yml`)
- **Grafana** - Dashboards (config at `config/grafana-dashboard.json`)
- **Elasticsearch** - Log aggregation

## Governance Framework

### Dimensions Structure (85 total: 00-99)

- **Location**: `src/governance/dimensions/`
- **Index**: `src/governance/dimensions/index.yaml`
- **Map**: `src/governance/governance-map.yaml`
- **Stack**: YAML + OPA/Rego + JSON Schema

### Dimension Layers

- **00-09**: Strategic Layer (vision, architecture, decision, risk)
- **10-29**: Operational Layer (policy, tools, metrics, quality)
- **30-49**: Execution Layer (schemas, templates, contracts, automation)
- **50-59**: Observability Layer (monitoring, alerting, insights)
- **60-80**: Advanced/Feedback Layer (AI, contracts, optimization)
- **81-83**: Extended Layer (auto-comment, stakeholder, integration)
- **90-99**: Meta-Specification Layer (naming conventions, meta-governance)

### 99-naming-convention (Meta-Specification Capstone)

Unified naming convention governance with nine sub-specifications:

- **URN Format**: `urn:machinenativeops:{domain}:{resource}:{version}`
- **Registered Domains**: governance, ai, core, autonomous, config, dimension
- **Naming Standards**: directories (kebab-case), YAML keys (snake_case), JSON API (camelCase)
- **Sub-specs**: directory, file, extension, key, value, mapping, reference, dependency, uri-urn

### Examples & Tutorials

- **Naming convention**: `src/governance/dimensions/99-naming-convention/examples/`
- **Change management examples**: `src/governance/dimensions/03-change/examples/`
- **Namespace tutorial**: `docs/tutorials/namespace/`

### Recent Changes (Dec 2025)

- Added 99-naming-convention as meta-specification layer capstone
- Established canonical URN format for all resources
- Resolved ID conflicts: 10-stakeholder→82, 30-integration→83
- Added 81-auto-comment dimension
- Total dimensions increased to 85 with meta-spec layer (90-99)
