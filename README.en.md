# 🏝️ Unmanned Island System

<div align="center">

![Version](https://img.shields.io/badge/version-4.0.0-blue?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue?style=for-the-badge&logo=typescript)
![Python](https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge&logo=python)
![Node.js](https://img.shields.io/badge/Node.js-20+-green?style=for-the-badge&logo=node.js)

**🚀 Next-Generation Cloud-Native Intelligent Automation Platform**

_SynergyMesh Core Engine + Structural Governance System + Autonomous Framework_

[Quick Start](#-quick-start) • [System Overview](#-system-overview) •
[Core Features](#-core-features) •
[Living Knowledge Base](#4️⃣-living-knowledge-base) •
[Admin Copilot CLI](#-admin-copilot-cli-public-preview) •
[Web Apps](#-web-ui--code-analysis-api-appsweb) •
[Config Overview](#️-global-configuration-overview) •
[Virtual Experts](#-virtual-expert-team) • [Agent Services](#-agent-services) •
[Drone System](#-drone-system-configuration) •
[Autonomous Framework](#-autonomous-framework-drone--av) •
[Documentation](#-documentation) • [中文](README.md)

</div>

---

## 🌟 System Overview

**Unmanned Island System** is a unified enterprise-grade intelligent automation
platform that integrates three core subsystems:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        🏝️ Unmanned Island System                            │
│                           Unified Control Layer                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐ │
│  │   🔷 SynergyMesh    │  │   ⚖️ Structural     │  │  🚁 Autonomous      │ │
│  │   Core Engine       │  │   Governance        │  │  Framework          │ │
│  │                     │  │                     │  │                     │ │
│  │  • AI Decision      │  │  • Schema Namespace │  │  • Five-Skeleton    │ │
│  │  • Cognitive Proc.  │  │  • 10-Stage Pipe    │  │  • Drone Control    │ │
│  │  • Service Registry │  │  • SLSA Provenance  │  │  • AV Integration   │ │
│  │  • Safety Mechanisms│  │  • Policy Gates     │  │  • Safety Monitor   │ │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘ │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                         Shared Infrastructure Layer                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │MCP Servers│ │  CI/CD   │ │Monitoring│ │ K8s Deploy│ │  Testing │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 🎯 Design Principles

| Principle                 | Description                                                                |
| ------------------------- | -------------------------------------------------------------------------- |
| **Single Entry Point**    | synergymesh.yaml as the single source of truth for all configurations      |
| **Modular Design**        | Three subsystems operate independently, collaborate via unified interfaces |
| **Zero-Trust Security**   | SLSA L3 provenance + Sigstore signing + policy gate validation             |
| **Autonomous Operations** | AI-driven auto-repair, intelligent assignment, escalation management       |

---

## 🔷 Core Subsystems

### 1️⃣ SynergyMesh Core Engine

Cloud-native intelligent business automation and data orchestration platform.

````yaml
# Core Capabilities
capabilities:
Node.js >= 18.0.0


  ### 3️⃣ Autonomous Framework

  Complete five-skeleton drone/self-driving autonomous system framework:

  - Architecture Stability (C++ + ROS 2)
  - API Governance (Python)
  - Testing & Compatibility (Python + YAML)
  - Security & Observability (Go)
  - Documentation & Examples (YAML + Markdown)

  Details: automation/autonomous/README.md.

  ---

  ## 📁 Unified Directory Structure

  High-level layout (see README.md for Chinese version):

  - synergymesh.yaml – unified configuration entry
  - core/ – core platform services
  - automation/ – intelligent, autonomous, architect, hyperautomation modules
  - config/ – system manifests, AI constitution, safety mechanisms
  - governance/ – schemas, policies, SBOM, audit
  - infrastructure/ – Kubernetes, monitoring, drift
  - mcp-servers/ – MCP servers for LLM tools
  - tools/cli/ – Admin Copilot CLI
  - apps/web/ – web UI + code analysis API
  - services/agents/ – long-lived business agents
  - docs/ – documentation portal

  ---

  ## 🚀 Quick Start

  ### Prerequisites

  ```bash
  Node.js >= 18.0.0
  Python >= 3.10
  npm >= 8.0.0

  # Optional (autonomous systems)
  ROS 2 Humble
  Go >= 1.20
  C++ 17 (GCC 11+)
````

### Installation

```bash
git clone https://github.com/SynergyMesh-admin/Unmanned-Island.git
cd unmanned-island

npm install

npm run lint
npm run test
```

### Start Core Services

```bash
cd core/contract_service/contracts-L1/contracts
npm install && npm run build
npm start

cd mcp-servers
npm install && npm start

python tools/docs/validate_index.py --verbose
```

### Docker Deployment

```bash
| Document                                                  | Description               |
docker-compose up -d
```

---

## 🛠️ Core Features

### 🤖 Intelligent Automation

| Feature             | Description                                 | Entry Point                        |
| ------------------- | ------------------------------------------- | ---------------------------------- |
| Auto Code Review    | Automated PR review & merge                 | .github/workflows/                 |
| Smart Assignment    | Auto-assignment with load balancing         | core/contract_service/             |
| Advanced Escalation | 5-level escalation ladder (L1 Auto → L5 CS) | docs/ADVANCED_ESCALATION_SYSTEM.md |
| Auto-Fix Bot        | Automatic CI failure repair                 | config/auto-fix-bot.yml            |

### 🔒 Security & Compliance

| Feature            | Description                  | Entry Point           |
| ------------------ | ---------------------------- | --------------------- |
| SLSA L3 Provenance | Build attestation & signing  | core/slsa_provenance/ |
| Schema Validation  | JSON Schema compliance check | governance/schemas/   |
| Policy Gates       | OPA/Conftest policy checks   | governance/policies/  |
| SBOM Generation    | Software Bill of Materials   | governance/sbom/      |

### 📊 Monitoring & Observability

| Feature               | Description                   | Entry Point                  |
| --------------------- | ----------------------------- | ---------------------------- |
| Dynamic CI Assistant  | Per-CI intelligent assistant  | docs/DYNAMIC_CI_ASSISTANT.md |
| Prometheus Monitoring | Metrics collection & alerting | infrastructure/monitoring/   |
| Drift Detection       | Infra configuration drift     | infrastructure/drift/        |

---

## 4️⃣ Living Knowledge Base

Self-aware documentation and structure model of the repository.

- Detects changes (git history, CI results, scheduled scans)
- Rebuilds structure (generated-mndoc.yaml, knowledge-graph.yaml)
- Runs self-diagnostics (orphan components, dead configs, broken links)
- Emits health reports and can open GitHub issues automatically

  Design details: docs/LIVING_KNOWLEDGE_BASE.md.

  ***

## 🖥️ Admin Copilot CLI (Public Preview)

Admin Copilot CLI brings AI-powered analysis and operations into the terminal:

- Chat, analyze, fix, explain, generate, review, test
- GitHub integration and MCP extension support
- Safe-by-default: previews every action before execution

  See docs/ADMIN_COPILOT_CLI.md and tools/cli/README.md.

  ***

## 🌐 Web UI & Code Analysis API (apps/web)

apps/web contains:

- React front-end UI (npm install, npm run dev/build)
- FastAPI backend for multi-language code analysis (pytest, coverage)
- Docker, docker-compose and Kubernetes manifests

  Details: apps/web/README.md.

  ***

## ️ Global Configuration Overview

Key configuration files:

- synergymesh.yaml – global entry
- config/system-manifest.yaml – system manifest
- config/unified-config-index.yaml – unified config index
- config/system-module-map.yaml – module mapping
- config/ai-constitution.yaml – AI constitution
- config/agents/team/virtual-experts.yaml – virtual expert team
- config/safety-mechanisms.yaml – safety mechanisms
- config/topology-mind-matrix.yaml – mind matrix topology
- config/drone-config.yml – drone fleet configuration

  ***

## 👨‍💼 Virtual Expert Team

Virtual experts model domain knowledge across architecture, security, DB, AI,
DevOps, etc. Mappings and domains: config/agents/team/virtual-experts.yaml.

---

## 🤖 Agent Services

services/agents/ exposes long-lived business agents:

- Auto-Repair Agent – automatic code repair
- Code Analyzer Agent – deep code analysis
- Dependency Manager – dependency updates and security
- Orchestrator – multi-agent workflows
- Vulnerability Detector – CVE detection and reports

  See services/agents/README.md.

  ***

## 🚁 Drone System Configuration

Drone fleet and automation configuration is defined in config/drone-config.yml
and implemented by automation/autonomous/.

---

## 🚗 Autonomous Framework (Drone / AV)

Five-skeleton autonomous framework for drones and autonomous vehicles.

Full architecture and testing flows: automation/autonomous/README.md.

---

## 📚 Documentation

Main documentation portal: docs/README.md.

- Architecture: docs/architecture/
- Quick Start: docs/QUICK_START.md
- API Docs: docs/AUTO_ASSIGNMENT_API.md
- Operations: docs/operations/

  ***

## 🔄 CI/CD

Workflows under .github/workflows/ enforce quality gates:

- core-services.yml – core services tests
- integration.yml – integration tests
- apply.yaml – 10-stage governance pipeline
- auto-review.yml – auto review & merge

  Quality gates: coverage, lint, security, schema, policy.

  ***

## 📄 License & Acknowledgments

Licensed under the MIT License (see LICENSE).

Thanks to SynergyMesh, Sigstore, OPA and SLSA for foundational components.

---

  <div align="center">

**🏝️ Unmanned Island System**

_Making development more efficient, making code more perfect!_

[GitHub](https://github.com/SynergyMesh-admin/Unmanned-Island) •
[Issues](https://github.com/SynergyMesh-admin/Unmanned-Island/issues) •
[Discussions](https://github.com/SynergyMesh-admin/Unmanned-Island/discussions)

  </div>
| --------------------------------------------------------- | ------------------------- |
| [Auto Review & Merge](docs/AUTO_REVIEW_MERGE.md)          | PR automation workflow    |
| [Smart Assignment](docs/AUTO_ASSIGNMENT_SYSTEM.md)        | Task assignment mechanism |
| [Advanced Escalation](docs/ADVANCED_ESCALATION_SYSTEM.md) | 5-level escalation ladder |
| [Dynamic CI Assistant](docs/DYNAMIC_CI_ASSISTANT.md)      | CI interactive service    |

### Governance Documentation

| Document                                     | Description                |
| -------------------------------------------- | -------------------------- |
| [Schema Definitions](governance/schemas/)    | JSON Schema specifications |
| [Policy Configuration](governance/policies/) | OPA/Conftest policies      |
| [Audit Format](governance/audit/)            | Audit event definitions    |
| [Knowledge Index](docs/knowledge_index.yaml) | Machine-readable index     |

---

## 🔄 CI/CD

### Workflows

| Workflow            | Trigger | Description                  |
| ------------------- | ------- | ---------------------------- |
| `core-services.yml` | PR/Push | Core service tests           |
| `integration.yml`   | PR/Push | Integration tests            |
| `apply.yaml`        | PR      | 10-stage governance pipeline |
| `auto-review.yml`   | PR      | Auto review & merge          |

### Quality Gates

```yaml
quality_gates:
  test_coverage: '>= 80%'
  lint_errors: 0
  security_vulnerabilities: 0
  schema_validation: pass
  policy_check: pass
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- [SynergyMesh](https://github.com/SynergyMesh/SynergyMesh) - Core engine
  foundation
- [Sigstore](https://sigstore.dev/) - Keyless signing
- [OPA](https://www.openpolicyagent.org/) - Policy engine
- [SLSA](https://slsa.dev/) - Supply chain security framework

---

<div align="center">

**🏝️ Unmanned Island System**

_Making development more efficient, making code more perfect!_

[GitHub](https://github.com/SynergyMesh-admin/Unmanned-Island) •
[Issues](https://github.com/SynergyMesh-admin/Unmanned-Island/issues) •
[Discussions](https://github.com/SynergyMesh-admin/Unmanned-Island/discussions)

</div>
