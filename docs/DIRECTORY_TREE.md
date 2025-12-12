# 🏝️ Unmanned Island System - 完整目錄樹狀結構

<div align="center">

![Version](https://img.shields.io/badge/version-3.0.0-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/status-開發中-yellow?style=for-the-badge)
![Last Updated](https://img.shields.io/badge/最後更新-2024.12-green?style=for-the-badge)

**完整展開所有子目錄 • 無限遞歸 • 自動生成**

</div>

---

## 📋 目錄

- [📖 專案概述](#-專案概述)
- [📊 統計資訊](#-統計資訊)
- [🗂️ 完整目錄樹狀結構](#️-完整目錄樹狀結構)

---

## 📖 專案概述

此文件包含 **unmanned-island**
專案的完整目錄樹狀結構，展開所有子目錄、子子目錄至無限延伸。

### 技術棧

| 層級     | 技術                        | 用途           |
| -------- | --------------------------- | -------------- |
| 後端     | TypeScript, Python, Node.js | 核心服務與 API |
| 前端     | React, TypeScript           | Web 應用介面   |
| 基礎設施 | Kubernetes, Docker          | 容器化部署     |
| CI/CD    | GitHub Actions              | 自動化流程     |
| 安全     | Sigstore, SLSA              | 供應鏈安全     |
| 監控     | Prometheus, Grafana         | 系統觀測       |

---

## 📊 統計資訊

| 統計項目    | 數量  |
| ----------- | ----- |
| 📁 目錄數量 | 306   |
| 📄 檔案數量 | 1,186 |
| 🏛️ 主要模組 | 15+   |
| 🔧 工具腳本 | 30+   |
| 📚 文件檔案 | 100+  |

---

## 🗂️ 完整目錄樹狀結構

以下是專案的完整目錄樹狀結構，包含所有子目錄及檔案：

```
.
├── .devcontainer
│   ├── automation
│   │   ├── auto-pilot.js
│   │   ├── code-generator.ts
│   │   ├── deployment-drone.sh
│   │   └── drone-coordinator.py
│   ├── environments
│   │   ├── development.env
│   │   ├── production.env
│   │   └── staging.env
│   ├── grafana
│   │   └── provisioning
│   │       ├── dashboards
│   │       │   └── life-system.yml
│   │       └── datasources
│   │           └── prometheus.yml
│   ├── init-db
│   │   └── 01-init-life-system.sql
│   ├── scripts
│   │   ├── health-check.sh
│   │   └── start-life-system.sh
│   ├── templates
│   │   ├── connector-template
│   │   │   └── README.md
│   │   ├── docker
│   │   │   ├── NODEJS_USER_SETUP.md
│   │   │   ├── README.md
│   │   │   └── validate-dockerfiles.sh
│   │   ├── integration-template
│   │   │   └── README.md
│   │   └── service-template
│   │       └── README.md
│   ├── CHANGELOG.md
│   ├── Dockerfile
│   ├── KB.md
│   ├── QUICK_START.md
│   ├── README.md
│   ├── SOLUTION_SUMMARY.md
│   ├── TEST-GUIDE.md
│   ├── devcontainer-v2.json
│   ├── devcontainer.json
│   ├── docker-compose.dev.yml
│   ├── docker-compose.yml
│   ├── install-optional-tools.sh
│   ├── life-system-README.md
│   ├── post-create.sh
│   ├── post-start-v2.sh
│   ├── post-start.sh
│   ├── prometheus.yml
│   ├── requirements.txt
│   ├── setup.sh
│   └── start-dev-server.sh
├── .github
│   ├── ISSUE_TEMPLATE
│   │   ├── bug_report.yml
│   │   ├── config.yml
│   │   ├── documentation.yml
│   │   └── feature_request.yml
│   ├── agents
│   │   └── my-agent.agent.md
│   ├── codeql
│   │   ├── custom-queries
│   │   │   ├── enterprise-security.ql
│   │   │   └── qlpack.yml
│   │   └── codeql-config.yml
│   ├── private
│   │   ├── agents
│   │   │   ├── code-review.agent.md
│   │   │   ├── dependency-updater.agent.md
│   │   │   ├── security-scanner.agent.md
│   │   │   └── workflow-optimizer.agent.md
│   │   ├── config
│   │   │   └── agent-settings.yml
│   │   ├── templates
│   │   │   └── agent-template.md
│   │   └── README.md
│   ├── profile
│   │   └── README.md
│   ├── scripts
│   │   ├── auto-fix-imports.sh
│   │   ├── risk_assessment.py
│   │   └── solution_generator.py
│   ├── secret-scanning
│   │   └── custom-patterns.yml
│   ├── workflows
│   │   ├── auto-review-merge.yml
│   │   ├── auto-update-knowledge-graph.yml
│   │   ├── auto-vulnerability-fix.yml
│   │   ├── autofix-bot.yml
│   │   ├── autonomous-ci-guardian.yml
│   │   ├── ci-auto-comment.yml
│   │   ├── ci-failure-auto-solution.yml
│   │   ├── codeql.yml
│   │   ├── compliance-report.yml
│   │   ├── conftest-validation.yml
│   │   ├── contracts-cd.yml
│   │   ├── copilot-setup-steps.yml
│   │   ├── core-services-ci.yml
│   │   ├── create-staging-branch.yml
│   │   ├── delete-staging-branches.yml
│   │   ├── dependency-manager-ci.yml
│   │   ├── dynamic-ci-assistant.yml
│   │   ├── integration-deployment.yml
│   │   ├── interactive-ci-service.yml
│   │   ├── label.yml
│   │   ├── language-check.yml
│   │   ├── mcp-servers-cd.yml
│   │   ├── mndoc-knowledge-graph.yml
│   │   ├── monorepo-dispatch.yml
│   │   ├── osv-scanner.yml
│   │   ├── phase1-integration.yml
│   │   ├── policy-simulate.yml
│   │   ├── pr-security-gate.yml
│   │   ├── project-cd.yml
│   │   ├── reusable-ci.yml
│   │   ├── secret-bypass-request.yml
│   │   ├── secret-protection.yml
│   │   ├── setup-runner.yml
│   │   ├── snyk-security.yml
│   │   ├── stale.yml
│   │   ├── validate-copilot-instructions.yml
│   │   └── validate-yaml.yml
│   ├── CODEOWNERS
│   ├── FUNDING.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── actionlint.yaml
│   ├── auto-review-config.yml
│   ├── copilot-instructions.md
│   ├── dependabot.yml
│   ├── labeler.yml
│   └── security-policy.yml
├── .vscode
│   ├── extensions.json
│   ├── mcp.json
│   ├── settings.json
│   └── tasks.json
├── apps
│   └── web
│       ├── core
│       │   └── analyzers
│       │       └── analyzer.py
│       ├── deploy
│       │   ├── deployment.yaml
│       │   ├── hpa.yaml
│       │   ├── rbac.yaml
│       │   └── service.yaml
│       ├── k8s
│       │   └── deployment-api.yaml
│       ├── scripts
│       │   └── build.mjs
│       ├── services
│       │   ├── api.py
│       │   ├── code_analyzer.py
│       │   └── models.py
│       ├── src
│       │   ├── components
│       │   │   ├── layout
│       │   │   │   ├── Footer.tsx
│       │   │   │   └── Navbar.tsx
│       │   │   └── ui
│       │   │       ├── accordion.tsx
│       │   │       ├── alert-dialog.tsx
│       │   │       ├── alert.tsx
│       │   │       ├── aspect-ratio.tsx
│       │   │       ├── avatar.tsx
│       │   │       ├── badge.tsx
│       │   │       ├── breadcrumb.tsx
│       │   │       ├── button.tsx
│       │   │       ├── calendar.tsx
│       │   │       ├── card.tsx
│       │   │       ├── carousel.tsx
│       │   │       ├── chart.tsx
│       │   │       ├── checkbox.tsx
│       │   │       ├── collapsible.tsx
│       │   │       ├── command.tsx
│       │   │       ├── context-menu.tsx
│       │   │       ├── dialog.tsx
│       │   │       ├── drawer.tsx
│       │   │       ├── dropdown-menu.tsx
│       │   │       ├── form.tsx
│       │   │       ├── hover-card.tsx
│       │   │       ├── input-otp.tsx
│       │   │       ├── input.tsx
│       │   │       ├── label.tsx
│       │   │       ├── menubar.tsx
│       │   │       ├── navigation-menu.tsx
│       │   │       ├── pagination.tsx
│       │   │       ├── popover.tsx
│       │   │       ├── progress.tsx
│       │   │       ├── radio-group.tsx
│       │   │       ├── resizable.tsx
│       │   │       ├── scroll-area.tsx
│       │   │       ├── select.tsx
│       │   │       ├── separator.tsx
│       │   │       ├── sheet.tsx
│       │   │       ├── sidebar.tsx
│       │   │       ├── skeleton.tsx
│       │   │       ├── slider.tsx
│       │   │       ├── sonner.tsx
│       │   │       ├── switch.tsx
│       │   │       ├── table.tsx
│       │   │       ├── tabs.tsx
│       │   │       ├── textarea.tsx
│       │   │       ├── toast.tsx
│       │   │       ├── toaster.tsx
│       │   │       ├── toggle-group.tsx
│       │   │       ├── toggle.tsx
│       │   │       └── tooltip.tsx
│       │   ├── hooks
│       │   │   ├── use-mobile.tsx
│       │   │   └── use-toast.ts
│       │   ├── lib
│       │   │   └── utils.ts
│       │   ├── pages
│       │   │   ├── Architecture.tsx
│       │   │   ├── Backend.tsx
│       │   │   ├── Contact.tsx
│       │   │   ├── Frontend.tsx
│       │   │   └── Home.tsx
│       │   ├── App.tsx
│       │   ├── main.tsx
│       │   └── shadcn.css
│       ├── tests
│       │   ├── __init__.py
│       │   └── test_code_analyzer.py
│       ├── Dockerfile
│       ├── Dockerfile.api
│       ├── PHASE2_IMPROVEMENTS.md
│       ├── README.md
│       ├── docker-compose.api.yml
│       ├── index.html
│       ├── package.json
│       ├── pytest.ini
│       ├── requirements.txt
│       ├── tailwind.config.js
│       └── tsconfig.json
├── automation
│   ├── architect
│   │   ├── config
│   │   │   └── automation-architect.yml
│   │   ├── core
│   │   │   ├── analysis
│   │   │   │   ├── __init__.py
│   │   │   │   ├── architecture_analyzer.py
│   │   │   │   ├── performance_analyzer.py
│   │   │   │   ├── security_scanner.py
│   │   │   │   └── static_analyzer.py
│   │   │   ├── orchestration
│   │   │   │   ├── __init__.py
│   │   │   │   ├── event_bus.py
│   │   │   │   └── pipeline.py
│   │   │   ├── repair
│   │   │   │   ├── __init__.py
│   │   │   │   ├── ast_transformer.py
│   │   │   │   ├── repair_verifier.py
│   │   │   │   └── rule_engine.py
│   │   │   └── __init__.py
│   │   ├── docs
│   │   │   ├── automation-iteration
│   │   │   │   └── README.md
│   │   │   ├── autonomous-driving
│   │   │   │   └── README.md
│   │   │   ├── drone-systems
│   │   │   │   └── README.md
│   │   │   ├── API.md
│   │   │   ├── DEPLOYMENT.md
│   │   │   └── INTEGRATION_GUIDE.md
│   │   ├── examples
│   │   │   └── basic_usage.py
│   │   ├── frameworks-popular
│   │   │   └── README.md
│   │   ├── tests
│   │   │   ├── unit
│   │   │   │   ├── test_security_scanner.py
│   │   │   │   └── test_static_analyzer.py
│   │   │   └── __init__.py
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── docker-compose.yml
│   │   └── requirements.txt
│   ├── autonomous
│   │   ├── api-governance
│   │   │   ├── README.md
│   │   │   ├── api_contract.py
│   │   │   └── requirements.txt
│   │   ├── architecture-stability
│   │   │   ├── CMakeLists.txt
│   │   │   ├── README.md
│   │   │   ├── flight_controller.cpp
│   │   │   └── package.xml
│   │   ├── docs-examples
│   │   │   ├── API_DOCUMENTATION.md
│   │   │   ├── QUICKSTART.md
│   │   │   ├── README.md
│   │   │   └── governance_matrix.yaml
│   │   ├── security-observability
│   │   │   ├── observability
│   │   │   │   └── event_logger.go
│   │   │   ├── README.md
│   │   │   ├── go.mod
│   │   │   └── main.go
│   │   ├── testing-compatibility
│   │   │   ├── README.md
│   │   │   ├── requirements.txt
│   │   │   ├── test_compatibility.py
│   │   │   └── test_config.yaml
│   │   ├── INTEGRATION_SUMMARY.md
│   │   └── README.md
│   ├── hyperautomation
│   │   ├── contracts
│   │   │   └── file-contract.json
│   │   ├── docs
│   │   │   ├── ci-cd-strategy.md
│   │   │   ├── core-principles.md
│   │   │   ├── sbom-placeholder.json
│   │   │   ├── uav-autonomous-driving-governance.md
│   │   │   └── usage-notes.md
│   │   ├── policies
│   │   │   ├── gatekeeper
│   │   │   │   ├── geo-fencing.yaml
│   │   │   │   └── uav-ad-labels.yaml
│   │   │   └── rego
│   │   │       └── uav_ad.rego
│   │   ├── templates
│   │   │   └── impl
│   │   │       └── examples
│   │   │           ├── README.md
│   │   │           ├── ad-deployment.yaml
│   │   │           ├── namespace.yaml
│   │   │           ├── uav-configmap.yaml
│   │   │           └── uav-deployment.yaml
│   │   ├── CHANGELOG.md
│   │   ├── QUICK_REFERENCE.md
│   │   └── README.md
│   ├── intelligent
│   │   ├── agents
│   │   │   ├── __init__.py
│   │   │   ├── py.typed
│   │   │   ├── recognition_server.py
│   │   │   ├── task_executor.py
│   │   │   └── visualization_agent.py
│   │   ├── examples
│   │   │   └── demo.py
│   │   ├── synergymesh_core
│   │   │   ├── __init__.py
│   │   │   ├── autonomous_coordinator.py
│   │   │   ├── ecosystem_orchestrator.py
│   │   │   ├── natural_language_processor.py
│   │   │   ├── nli_layer.py
│   │   │   ├── orchestration_layer.py
│   │   │   └── self_evolution_engine.py
│   │   ├── test-vectors
│   │   │   ├── generator.py
│   │   │   ├── py.typed
│   │   │   └── security-samples.json
│   │   ├── tests
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py
│   │   │   ├── test_phase10_components.py
│   │   │   ├── test_phase11_components.py
│   │   │   ├── test_phase12_components.py
│   │   │   ├── test_phase13_components.py
│   │   │   ├── test_phase14_components.py
│   │   │   ├── test_phase3_components.py
│   │   │   ├── test_phase4_components.py
│   │   │   ├── test_phase5_components.py
│   │   │   ├── test_phase6_components.py
│   │   │   ├── test_phase7_components.py
│   │   │   ├── test_phase8_components.py
│   │   │   ├── test_phase8_enhancement.py
│   │   │   ├── test_phase9_components.py
│   │   │   ├── test_synergymesh_core.py
│   │   │   └── test_task_executor.py
│   │   ├── AUTO_UPGRADE.md
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── auto_upgrade_env.py
│   │   ├── pipeline_service.py
│   │   ├── py.typed
│   │   ├── pyrightconfig.json
│   │   ├── pytest.ini
│   │   └── requirements.txt
│   └── zero_touch_deployment.py
├── config
│   ├── autofix
│   │   ├── rules
│   │   │   ├── performance-rules.yaml
│   │   │   └── security-rules.yaml
│   │   └── config.json
│   ├── conftest
│   │   └── README.md
│   ├── docker
│   │   ├── compose.architect.yaml
│   │   ├── compose.base.yaml
│   │   ├── compose.dev.yaml
│   │   ├── compose.devcontainer.yaml
│   │   ├── compose.example.yaml
│   │   └── index.yaml
│   ├── integrations
│   │   ├── matechat
│   │   │   └── config.yaml
│   │   ├── README.md
│   │   ├── jira-integration.py
│   │   └── slack-webhook.sh
│   ├── ai-constitution.yaml
│   ├── auto-fix-bot.prompt.yml
│   ├── auto-fix-bot.yml
│   ├── auto-scaffold.json
│   ├── ci-comprehensive-solution.yaml
│   ├── ci-error-handler.yaml
│   ├── cloud-agent-delegation.yml
│   ├── dependencies.yaml
│   ├── drone-config.yml
│   ├── elasticsearch-config.sh
│   ├── environment.yaml
│   ├── grafana-dashboard.json
│   ├── island-control.yml
│   ├── monitoring.yaml
│   ├── peachy-build.toml
│   ├── prometheus-config.yml
│   ├── prometheus-rules.yml
│   ├── safety-mechanisms.yaml
│   ├── security-network-config.yml
│   ├── synergymesh.config.yaml
│   ├── system-manifest.yaml
│   ├── system-module-map.yaml
│   ├── topology-mind-matrix.yaml
│   ├── unified-config-index.yaml
│   ├── virtual-experts.yaml
│   └── yaml-module-system.yaml
├── core
│   ├── advisory-database
│   │   ├── src
│   │   │   ├── __tests__
│   │   │   │   └── advisory.test.ts
│   │   │   ├── services
│   │   │   │   ├── advisory-bot.ts
│   │   │   │   └── advisory-service.ts
│   │   │   ├── types
│   │   │   │   ├── advisory.ts
│   │   │   │   └── index.ts
│   │   │   ├── utils
│   │   │   │   └── ghsa.ts
│   │   │   ├── validators
│   │   │   │   └── advisory-validator.ts
│   │   │   └── index.ts
│   │   ├── .eslintrc.json
│   │   ├── README.md
│   │   ├── jest.config.js
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── contract_service
│   │   ├── contracts-L1
│   │   │   ├── ai-chat-service
│   │   │   │   ├── src
│   │   │   │   │   ├── controllers
│   │   │   │   │   │   └── chat-controller.ts
│   │   │   │   │   ├── models
│   │   │   │   │   │   └── openai-service.ts
│   │   │   │   │   ├── server.ts
│   │   │   │   │   └── types.ts
│   │   │   │   ├── .env.example
│   │   │   │   ├── README.md
│   │   │   │   ├── package-lock.json
│   │   │   │   ├── package.json
│   │   │   │   └── tsconfig.json
│   │   │   └── contracts
│   │   │       ├── ci
│   │   │       │   └── contract-checker.js
│   │   │       ├── contracts
│   │   │       │   └── external-api.json
│   │   │       ├── deploy
│   │   │       │   ├── k8s
│   │   │       │   │   ├── configmap.yaml
│   │   │       │   │   ├── deployment-production.yaml
│   │   │       │   │   ├── ingress.yaml
│   │   │       │   │   ├── kustomization.yaml
│   │   │       │   │   ├── namespace.yaml
│   │   │       │   │   ├── prometheusrule.yaml
│   │   │       │   │   ├── secret.yaml
│   │   │       │   │   ├── service-production.yaml
│   │   │       │   │   └── servicemonitor.yaml
│   │   │       │   ├── README.md
│   │   │       │   ├── alerts.yaml
│   │   │       │   ├── deployment.yaml
│   │   │       │   ├── docker-compose.production.yml
│   │   │       │   ├── grafana-dashboard.json
│   │   │       │   ├── hpa.yaml
│   │   │       │   ├── monitoring.yaml
│   │   │       │   ├── networkpolicy.yaml
│   │   │       │   ├── nginx.conf
│   │   │       │   ├── pdb.yaml
│   │   │       │   ├── rbac.yaml
│   │   │       │   └── service.yaml
│   │   │       ├── docs
│   │   │       │   ├── architecture.zh.md
│   │   │       │   └── runbook.zh.md
│   │   │       ├── policy
│   │   │       │   ├── manifest-policies.rego
│   │   │       │   └── report-schema.json
│   │   │       ├── public
│   │   │       │   └── index.html
│   │   │       ├── sbom
│   │   │       │   ├── README.md
│   │   │       │   └── signing-policy.yml
│   │   │       ├── scripts
│   │   │       │   └── build.mjs
│   │   │       ├── src
│   │   │       │   ├── __tests__
│   │   │       │   │   ├── api.test.ts
│   │   │       │   │   ├── assignment.test.ts
│   │   │       │   │   ├── env.test.ts
│   │   │       │   │   ├── escalation.test.ts
│   │   │       │   │   ├── provenance.test.ts
│   │   │       │   │   ├── response.test.ts
│   │   │       │   │   └── slsa.test.ts
│   │   │       │   ├── config
│   │   │       │   │   └── env.ts
│   │   │       │   ├── controllers
│   │   │       │   │   ├── assignment.ts
│   │   │       │   │   ├── escalation.ts
│   │   │       │   │   ├── provenance.ts
│   │   │       │   │   └── slsa.ts
│   │   │       │   ├── middleware
│   │   │       │   │   ├── audit-log.ts
│   │   │       │   │   ├── error.ts
│   │   │       │   │   ├── logging.ts
│   │   │       │   │   ├── rate-limit.ts
│   │   │       │   │   └── response.ts
│   │   │       │   ├── services
│   │   │       │   │   ├── assignment
│   │   │       │   │   │   ├── auto-assignment-engine.ts
│   │   │       │   │   │   ├── responsibility-governance.ts
│   │   │       │   │   │   ├── responsibility-matrix.ts
│   │   │       │   │   │   └── workload-balancer.ts
│   │   │       │   │   ├── escalation
│   │   │       │   │   │   └── escalation-engine.ts
│   │   │       │   │   ├── attestation.ts
│   │   │       │   │   └── provenance.ts
│   │   │       │   ├── types
│   │   │       │   │   ├── assignment.ts
│   │   │       │   │   ├── escalation.ts
│   │   │       │   │   └── express.d.ts
│   │   │       │   ├── config.ts
│   │   │       │   ├── routes.ts
│   │   │       │   └── server.ts
│   │   │       ├── web
│   │   │       │   ├── components
│   │   │       │   │   ├── layout
│   │   │       │   │   │   ├── Footer.tsx
│   │   │       │   │   │   └── Navbar.tsx
│   │   │       │   │   └── ui
│   │   │       │   │       ├── accordion.tsx
│   │   │       │   │       ├── alert-dialog.tsx
│   │   │       │   │       ├── alert.tsx
│   │   │       │   │       ├── aspect-ratio.tsx
│   │   │       │   │       ├── avatar.tsx
│   │   │       │   │       ├── badge.tsx
│   │   │       │   │       ├── breadcrumb.tsx
│   │   │       │   │       ├── button.tsx
│   │   │       │   │       ├── calendar.tsx
│   │   │       │   │       ├── card.tsx
│   │   │       │   │       ├── carousel.tsx
│   │   │       │   │       ├── chart.tsx
│   │   │       │   │       ├── checkbox.tsx
│   │   │       │   │       ├── collapsible.tsx
│   │   │       │   │       ├── command.tsx
│   │   │       │   │       ├── context-menu.tsx
│   │   │       │   │       ├── dialog.tsx
│   │   │       │   │       ├── drawer.tsx
│   │   │       │   │       ├── dropdown-menu.tsx
│   │   │       │   │       ├── form.tsx
│   │   │       │   │       ├── hover-card.tsx
│   │   │       │   │       ├── input-otp.tsx
│   │   │       │   │       ├── input.tsx
│   │   │       │   │       ├── label.tsx
│   │   │       │   │       ├── menubar.tsx
│   │   │       │   │       ├── navigation-menu.tsx
│   │   │       │   │       ├── pagination.tsx
│   │   │       │   │       ├── popover.tsx
│   │   │       │   │       ├── progress.tsx
│   │   │       │   │       ├── radio-group.tsx
│   │   │       │   │       ├── resizable.tsx
│   │   │       │   │       ├── scroll-area.tsx
│   │   │       │   │       ├── select.tsx
│   │   │       │   │       ├── separator.tsx
│   │   │       │   │       ├── sheet.tsx
│   │   │       │   │       ├── sidebar.tsx
│   │   │       │   │       ├── skeleton.tsx
│   │   │       │   │       ├── slider.tsx
│   │   │       │   │       ├── sonner.tsx
│   │   │       │   │       ├── switch.tsx
│   │   │       │   │       ├── table.tsx
│   │   │       │   │       ├── tabs.tsx
│   │   │       │   │       ├── textarea.tsx
│   │   │       │   │       ├── toast.tsx
│   │   │       │   │       ├── toaster.tsx
│   │   │       │   │       ├── toggle-group.tsx
│   │   │       │   │       ├── toggle.tsx
│   │   │       │   │       └── tooltip.tsx
│   │   │       │   ├── hooks
│   │   │       │   │   ├── use-mobile.tsx
│   │   │       │   │   └── use-toast.ts
│   │   │       │   ├── lib
│   │   │       │   │   └── utils.ts
│   │   │       │   ├── pages
│   │   │       │   │   ├── Architecture.tsx
│   │   │       │   │   ├── Backend.tsx
│   │   │       │   │   ├── Contact.tsx
│   │   │       │   │   ├── Frontend.tsx
│   │   │       │   │   ├── Home.tsx
│   │   │       │   │   └── SLSAAttestation.tsx
│   │   │       │   ├── src
│   │   │       │   │   ├── components
│   │   │       │   │   │   ├── layout
│   │   │       │   │   │   │   ├── Footer.tsx
│   │   │       │   │   │   │   └── Navbar.tsx
│   │   │       │   │   │   └── ui
│   │   │       │   │   │       ├── accordion.tsx
│   │   │       │   │   │       ├── alert-dialog.tsx
│   │   │       │   │   │       ├── alert.tsx
│   │   │       │   │   │       ├── aspect-ratio.tsx
│   │   │       │   │   │       ├── avatar.tsx
│   │   │       │   │   │       ├── badge.tsx
│   │   │       │   │   │       ├── breadcrumb.tsx
│   │   │       │   │   │       ├── button.tsx
│   │   │       │   │   │       ├── calendar.tsx
│   │   │       │   │   │       ├── card.tsx
│   │   │       │   │   │       ├── carousel.tsx
│   │   │       │   │   │       ├── chart.tsx
│   │   │       │   │   │       ├── checkbox.tsx
│   │   │       │   │   │       ├── collapsible.tsx
│   │   │       │   │   │       ├── command.tsx
│   │   │       │   │   │       ├── context-menu.tsx
│   │   │       │   │   │       ├── dialog.tsx
│   │   │       │   │   │       ├── drawer.tsx
│   │   │       │   │   │       ├── dropdown-menu.tsx
│   │   │       │   │   │       ├── form.tsx
│   │   │       │   │   │       ├── hover-card.tsx
│   │   │       │   │   │       ├── input-otp.tsx
│   │   │       │   │   │       ├── input.tsx
│   │   │       │   │   │       ├── label.tsx
│   │   │       │   │   │       ├── menubar.tsx
│   │   │       │   │   │       ├── navigation-menu.tsx
│   │   │       │   │   │       ├── pagination.tsx
│   │   │       │   │   │       ├── popover.tsx
│   │   │       │   │   │       ├── progress.tsx
│   │   │       │   │   │       ├── radio-group.tsx
│   │   │       │   │   │       ├── resizable.tsx
│   │   │       │   │   │       ├── scroll-area.tsx
│   │   │       │   │   │       ├── select.tsx
│   │   │       │   │   │       ├── separator.tsx
│   │   │       │   │   │       ├── sheet.tsx
│   │   │       │   │   │       ├── sidebar.tsx
│   │   │       │   │   │       ├── skeleton.tsx
│   │   │       │   │   │       ├── slider.tsx
│   │   │       │   │   │       ├── sonner.tsx
│   │   │       │   │   │       ├── switch.tsx
│   │   │       │   │   │       ├── table.tsx
│   │   │       │   │   │       ├── tabs.tsx
│   │   │       │   │   │       ├── textarea.tsx
│   │   │       │   │   │       ├── toast.tsx
│   │   │       │   │   │       ├── toaster.tsx
│   │   │       │   │   │       ├── toggle-group.tsx
│   │   │       │   │   │       ├── toggle.tsx
│   │   │       │   │   │       └── tooltip.tsx
│   │   │       │   │   ├── lib
│   │   │       │   │   │   └── utils.ts
│   │   │       │   │   ├── App.tsx
│   │   │       │   │   ├── main.tsx
│   │   │       │   │   └── styles.css
│   │   │       │   ├── App.tsx
│   │   │       │   ├── README.md
│   │   │       │   ├── build.mjs
│   │   │       │   ├── main.tsx
│   │   │       │   ├── package.json
│   │   │       │   ├── shadcn.css
│   │   │       │   └── tailwind.config.js
│   │   │       ├── .dockerignore
│   │   │       ├── .env.example
│   │   │       ├── .eslintrc.json
│   │   │       ├── .gitignore
│   │   │       ├── BUILD_PROVENANCE.md
│   │   │       ├── Dockerfile
│   │   │       ├── SLSA_INTEGRATION_REPORT.md
│   │   │       ├── jest.config.js
│   │   │       ├── package-lock.json
│   │   │       ├── package.json
│   │   │       ├── tailwind.config.js
│   │   │       ├── tsconfig.json
│   │   │       └── web-package.json
│   │   ├── external
│   │   │   ├── README.md
│   │   │   └── external-api.json
│   │   └── README.md
│   ├── modules
│   │   ├── ai_constitution
│   │   │   ├── __init__.py
│   │   │   ├── adaptive_guidelines.py
│   │   │   ├── constitution_engine.py
│   │   │   ├── fundamental_laws.py
│   │   │   ├── guardrails.py
│   │   │   ├── operational_rules.py
│   │   │   └── policy_as_prompt.py
│   │   ├── ci_error_handler
│   │   │   ├── __init__.py
│   │   │   ├── auto_fix_engine.py
│   │   │   ├── ci_error_analyzer.py
│   │   │   ├── fix_status_tracker.py
│   │   │   └── issue_manager.py
│   │   ├── cloud_agent_delegation
│   │   │   ├── __init__.py
│   │   │   ├── cloud_provider_adapter.py
│   │   │   ├── delegation_manager.py
│   │   │   ├── load_balancer.py
│   │   │   └── task_router.py
│   │   ├── drone_system
│   │   │   ├── __init__.py
│   │   │   ├── autopilot.py
│   │   │   ├── base.py
│   │   │   ├── config.py
│   │   │   ├── coordinator.py
│   │   │   ├── deployment.py
│   │   │   ├── py.typed
│   │   │   └── utils.py
│   │   ├── execution_architecture
│   │   │   ├── README.md
│   │   │   ├── __init__.py
│   │   │   ├── agent_orchestration.py
│   │   │   ├── function_calling.py
│   │   │   ├── langchain_integration.py
│   │   │   ├── mcp_integration.py
│   │   │   └── tool_system.py
│   │   ├── execution_engine
│   │   │   ├── README.md
│   │   │   ├── __init__.py
│   │   │   ├── action_executor.py
│   │   │   ├── capability_registry.py
│   │   │   ├── connector_manager.py
│   │   │   ├── execution_engine.py
│   │   │   ├── rollback_manager.py
│   │   │   └── verification_engine.py
│   │   ├── main_system
│   │   │   ├── __init__.py
│   │   │   ├── automation_pipeline.py
│   │   │   ├── phase_orchestrator.py
│   │   │   ├── synergymesh_core.py
│   │   │   └── system_bootstrap.py
│   │   ├── mcp_servers_enhanced
│   │   │   ├── __init__.py
│   │   │   ├── mcp_server_manager.py
│   │   │   ├── realtime_connector.py
│   │   │   ├── tool_registry.py
│   │   │   └── workflow_orchestrator.py
│   │   ├── mind_matrix
│   │   │   ├── RUNTIME_README.md
│   │   │   ├── __init__.py
│   │   │   ├── executive_auto.py
│   │   │   └── main.py
│   │   ├── monitoring_system
│   │   │   ├── __init__.py
│   │   │   ├── auto_diagnosis.py
│   │   │   ├── auto_remediation.py
│   │   │   ├── intelligent_monitoring.py
│   │   │   ├── observability_platform.py
│   │   │   ├── self_learning.py
│   │   │   └── smart_anomaly_detector.py
│   │   ├── tech_stack
│   │   │   ├── __init__.py
│   │   │   ├── architecture_config.py
│   │   │   ├── framework_integrations.py
│   │   │   ├── multi_agent_coordinator.py
│   │   │   └── python_bridge.py
│   │   ├── training_system
│   │   │   ├── __init__.py
│   │   │   ├── example_library.py
│   │   │   ├── knowledge_base.py
│   │   │   └── skills_training.py
│   │   ├── virtual_experts
│   │   │   ├── __init__.py
│   │   │   ├── domain_experts.py
│   │   │   ├── expert_base.py
│   │   │   └── expert_team.py
│   │   ├── yaml_module_system
│   │   │   ├── __init__.py
│   │   │   ├── audit_trail.py
│   │   │   ├── ci_verification_pipeline.py
│   │   │   ├── policy_gate.py
│   │   │   ├── slsa_compliance.py
│   │   │   ├── yaml_module_definition.py
│   │   │   └── yaml_schema_validator.py
│   │   └── __init__.py
│   ├── safety_mechanisms
│   │   ├── __init__.py
│   │   ├── anomaly_detector.py
│   │   ├── circuit_breaker.py
│   │   ├── emergency_stop.py
│   │   ├── escalation_ladder.py
│   │   ├── rollback_system.py
│   │   └── safety_net.py
│   ├── slsa_provenance
│   │   ├── __init__.py
│   │   ├── artifact_verifier.py
│   │   ├── attestation_manager.py
│   │   ├── provenance_generator.py
│   │   └── signature_verifier.py
│   ├── unified_integration
│   │   ├── __init__.py
│   │   ├── cli_bridge.py
│   │   ├── cognitive_processor.py
│   │   ├── configuration_manager.py
│   │   ├── configuration_optimizer.py
│   │   ├── deep_execution_system.py
│   │   ├── integration_hub.py
│   │   ├── service_registry.py
│   │   ├── system_orchestrator.py
│   │   ├── unified_controller.py
│   │   └── work_configuration_manager.py
│   ├── README.md
│   ├── ai_decision_engine.py
│   ├── auto_bug_detector.py
│   ├── auto_governance_hub.py
│   ├── autonomous_trust_engine.py
│   ├── context_understanding_engine.py
│   └── hallucination_detector.py
├── docs
│   ├── architecture
│   │   ├── ADVANCED_SYSTEM_INTEGRATION.md
│   │   ├── CODE_QUALITY_CHECKS.md
│   │   ├── DELEGATION_WORKFLOW.md
│   │   ├── DEPLOYMENT_INFRASTRUCTURE.md
│   │   ├── DIRECTORY_STRUCTURE.md
│   │   ├── FILE_MANIFEST.txt
│   │   ├── FileDescription.md
│   │   ├── README.md
│   │   ├── REPOSITORY_INTEGRATION_ASSESSMENT.md
│   │   ├── SECURITY_CONFIG_CHECKS.md
│   │   ├── SYSTEM_ARCHITECTURE.md
│   │   ├── layers.md
│   │   ├── matechat-integration.md
│   │   └── repo-map.md
│   ├── automation
│   │   ├── AUTO_FIX_BOT.md
│   │   └── AUTO_FIX_BOT_GUIDE.md
│   ├── ci-cd
│   │   ├── IMPLEMENTATION_SUMMARY.md
│   │   ├── README.md
│   │   └── stage-1-basic-ci.md
│   ├── examples
│   │   ├── configuration
│   │   │   ├── docker
│   │   │   │   ├── Dockerfile.code-checker
│   │   │   │   └── docker-compose.yml
│   │   │   ├── jenkins
│   │   │   │   └── Jenkinsfile.code-quality
│   │   │   ├── kubernetes
│   │   │   │   └── k8s-sonarqube.yaml
│   │   │   ├── monitoring
│   │   │   │   └── prometheus-config.yaml
│   │   │   ├── python
│   │   │   │   ├── config_validator.py
│   │   │   │   └── security_scanner.py
│   │   │   ├── scripts
│   │   │   │   ├── config-check.sh
│   │   │   │   ├── format-check.sh
│   │   │   │   ├── phase2-security-check.sh
│   │   │   │   └── security-scan.sh
│   │   │   ├── .eslintrc.example.js
│   │   │   ├── .prettierrc.example.json
│   │   │   ├── README.md
│   │   │   └── sonar-project.properties.example
│   │   └── README.md
│   ├── mndoc
│   │   ├── components
│   │   │   └── core-components.yaml
│   │   ├── subsystems
│   │   │   ├── autonomous-framework.yaml
│   │   │   ├── structural-governance.yaml
│   │   │   └── synergymesh-core.yaml
│   │   ├── governance-pipeline.yaml
│   │   ├── index.yaml
│   │   └── system.yaml
│   ├── operations
│   │   ├── DeploymentGuide.md
│   │   ├── MONITORING_GUIDE.md
│   │   └── PRODUCTION_READINESS.md
│   ├── reports
│   │   ├── COMPREHENSIVE_IMPLEMENTATION_REPORT.md
│   │   ├── PHASE1_IMPLEMENTATION_SUMMARY.md
│   │   └── PHASE1_VALIDATION_REPORT.md
│   ├── security
│   │   ├── GHAS_IMPLEMENTATION_SUMMARY.md
│   │   └── SECURITY_SUMMARY.md
│   ├── troubleshooting
│   │   └── github-copilot-agent-fix.md
│   ├── ADMIN_COPILOT_CLI.md
│   ├── ADVANCED_ESCALATION_SYSTEM.md
│   ├── ADVANCED_FEATURES_SUMMARY.md
│   ├── AUTO_ASSIGNMENT_API.md
│   ├── AUTO_ASSIGNMENT_DEMO.md
│   ├── AUTO_ASSIGNMENT_SUMMARY.md
│   ├── AUTO_ASSIGNMENT_SYSTEM.md
│   ├── AUTO_FIX_BOT_V2_GUIDE.md
│   ├── AUTO_MERGE.md
│   ├── AUTO_REVIEW_MERGE.md
│   ├── BUILD_COMPAT.md
│   ├── CI_AUTO_COMMENT_SYSTEM.md
│   ├── CI_BATCH_UPGRADE_SUMMARY.md
│   ├── CI_DEPLOYMENT_UPGRADE_PLAN.md
│   ├── CI_GLOBAL_STATUS_FIX.md
│   ├── CLOUD_DELEGATION.md
│   ├── CODEQL_SETUP.md
│   ├── CODESPACE_SETUP.md
│   ├── COPILOT_SETUP.md
│   ├── DEPLOYMENT_ASSESSMENT.md
│   ├── DISASTER_RECOVERY.md
│   ├── DYNAMIC_CI_ASSISTANT.md
│   ├── EFFICIENCY_METRICS.md
│   ├── EXAMPLES.md
│   ├── GHAS_COMPLETE_GUIDE.md
│   ├── GHAS_DEPLOYMENT.md
│   ├── INTEGRATION_GUIDE.md
│   ├── INTELLIGENT_AUTOMATION_INTEGRATION.md
│   ├── INTERACTIVE_CI_UPGRADE_GUIDE.md
│   ├── LIVING_KNOWLEDGE_BASE.md
│   ├── MATECHAT_INTEGRATION_SUMMARY.md
│   ├── MERGE_BLOCKED_FIX.md
│   ├── MIGRATION.md
│   ├── PROJECT_STRUCTURE.md
│   ├── QUICK_START.md
│   ├── README.md
│   ├── ROOT_README.md
│   ├── SECRET_SCANNING.md
│   ├── SECURITY_TRAINING.md
│   ├── SYSTEM_BRIDGING_ASSESSMENT.md
│   ├── TIER1_CONTRACTS_L1_DEPLOYMENT_PLAN.md
│   ├── VISUAL_ELEMENTS.md
│   ├── VULNERABILITY_MANAGEMENT.md
│   ├── _config.yml
│   ├── architecture.zh.md
│   ├── autonomous-ci-compliance.md
│   ├── ci-troubleshooting.md
│   ├── deep-integration-guide.zh.md
│   ├── docs-index.json
│   ├── generated-mndoc.yaml
│   ├── index.md
│   ├── knowledge-graph.yaml
│   ├── knowledge_index.yaml
│   ├── production-deployment-guide.zh.md
│   ├── runbook.zh.md
│   ├── superroot-entities.yaml
│   └── unmanned-island.mndoc.yaml
├── governance
│   ├── audit
│   │   ├── append-only-log-client.js
│   │   └── format.yaml
│   ├── deployment
│   │   └── matechat-services.yml
│   ├── environment-matrix
│   │   ├── LANGUAGE_DIMENSION_MAPPING.md
│   │   └── module-environment-matrix.yml
│   ├── policies
│   │   ├── conftest
│   │   │   ├── matechat-integration
│   │   │   │   ├── README.md
│   │   │   │   └── integration-policy.rego
│   │   │   └── naming_policy.rego
│   │   ├── base-policies.yaml
│   │   ├── base-policy.yaml
│   │   ├── ci-policy-gate.yaml
│   │   ├── cli-safe-mode.rego
│   │   └── manifest-policies.rego
│   ├── registry
│   │   ├── module-A.yaml
│   │   ├── module-contracts-l1.yaml
│   │   ├── schema.json
│   │   └── services.yaml
│   ├── rules
│   │   └── language-policy.yml
│   ├── sbom
│   │   ├── docs-provenance.json
│   │   ├── provenance.json
│   │   ├── signing-policy.yml
│   │   └── synergymesh.spdx.json
│   ├── schemas
│   │   ├── mndoc
│   │   │   ├── entity-component-collection.schema.json
│   │   │   ├── entity-component.schema.json
│   │   │   ├── entity-configuration.schema.json
│   │   │   ├── entity-governance.schema.json
│   │   │   ├── entity-subsystem.schema.json
│   │   │   ├── entity-system.schema.json
│   │   │   ├── knowledge-graph.schema.json
│   │   │   ├── mapping-rules.schema.json
│   │   │   ├── mndoc-index.schema.json
│   │   │   └── mndoc.schema.json
│   │   ├── ai-constitution.schema.json
│   │   ├── auto-fix-bot-v2.schema.json
│   │   ├── cloud-agent-delegation.schema.json
│   │   ├── code-analysis.schema.json
│   │   ├── dependencies.schema.json
│   │   ├── docs-index.schema.json
│   │   ├── environment.schema.json
│   │   ├── osv-advisory.schema.json
│   │   ├── repair.schema.json
│   │   ├── safety-mechanisms.schema.json
│   │   ├── virtual-experts.schema.json
│   │   └── vulnerability.schema.json
│   ├── README.md
│   └── mapping-rules.yaml
├── infrastructure
│   ├── canary
│   │   └── policy-sim-plan.yaml
│   ├── drift
│   │   ├── rules.yaml
│   │   └── scan-cronjob.yaml
│   ├── kubernetes
│   │   ├── cache
│   │   │   ├── redis-service.yaml
│   │   │   └── redis-statefulset.yaml
│   │   ├── database
│   │   │   ├── postgres-service.yaml
│   │   │   └── postgres-statefulset.yaml
│   │   ├── hpa
│   │   │   ├── hpa.yaml
│   │   │   └── vpa.yaml
│   │   ├── ingress
│   │   │   ├── cert-manager.yaml
│   │   │   └── ingress.yaml
│   │   ├── manifests
│   │   │   ├── 01-namespace-rbac
│   │   │   │   ├── namespace.yaml
│   │   │   │   ├── network-policies.yaml
│   │   │   │   ├── pod-security-policies.yaml
│   │   │   │   └── rbac.yaml
│   │   │   ├── 02-storage
│   │   │   │   ├── persistent-volume-claims.yaml
│   │   │   │   └── storage-classes.yaml
│   │   │   ├── 03-secrets-config
│   │   │   │   ├── configmaps.yaml
│   │   │   │   └── secrets.yaml
│   │   │   ├── 04-databases
│   │   │   │   ├── postgres
│   │   │   │   │   ├── backup-cronjob.yaml
│   │   │   │   │   ├── monitoring.yaml
│   │   │   │   │   ├── service.yaml
│   │   │   │   │   └── statefulset.yaml
│   │   │   │   └── redis
│   │   │   │       ├── monitoring.yaml
│   │   │   │       ├── service.yaml
│   │   │   │       └── statefulset.yaml
│   │   │   ├── 05-core-services
│   │   │   │   ├── auto-repair
│   │   │   │   │   ├── deployment.yaml
│   │   │   │   │   ├── hpa.yaml
│   │   │   │   │   ├── network-policy.yaml
│   │   │   │   │   └── service.yaml
│   │   │   │   ├── code-analyzer
│   │   │   │   │   ├── deployment.yaml
│   │   │   │   │   ├── hpa.yaml
│   │   │   │   │   ├── network-policy.yaml
│   │   │   │   │   ├── pdb.yaml
│   │   │   │   │   └── service.yaml
│   │   │   │   ├── contracts-l1
│   │   │   │   │   ├── deployment.yaml
│   │   │   │   │   ├── hpa.yaml
│   │   │   │   │   ├── network-policy.yaml
│   │   │   │   │   ├── pdb.yaml
│   │   │   │   │   └── service.yaml
│   │   │   │   ├── orchestrator
│   │   │   │   │   ├── deployment.yaml
│   │   │   │   │   ├── network-policy.yaml
│   │   │   │   │   └── service.yaml
│   │   │   │   ├── result-aggregator
│   │   │   │   │   ├── deployment.yaml
│   │   │   │   │   ├── network-policy.yaml
│   │   │   │   │   └── service.yaml
│   │   │   │   └── vulnerability-detector
│   │   │   │       ├── deployment.yaml
│   │   │   │       ├── hpa.yaml
│   │   │   │       ├── network-policy.yaml
│   │   │   │       └── service.yaml
│   │   │   ├── 06-monitoring
│   │   │   │   ├── alertmanager
│   │   │   │   │   ├── configmap.yaml
│   │   │   │   │   ├── deployment.yaml
│   │   │   │   │   └── service.yaml
│   │   │   │   ├── grafana
│   │   │   │   │   ├── configmap.yaml
│   │   │   │   │   ├── deployment.yaml
│   │   │   │   │   └── service.yaml
│   │   │   │   ├── jaeger
│   │   │   │   │   ├── deployment.yaml
│   │   │   │   │   └── service.yaml
│   │   │   │   ├── loki
│   │   │   │   │   ├── configmap.yaml
│   │   │   │   │   ├── deployment.yaml
│   │   │   │   │   └── service.yaml
│   │   │   │   ├── node-exporter
│   │   │   │   │   ├── daemonset.yaml
│   │   │   │   │   └── service.yaml
│   │   │   │   └── prometheus
│   │   │   │       ├── configmap.yaml
│   │   │   │       ├── deployment.yaml
│   │   │   │       └── service.yaml
│   │   │   ├── 07-logging
│   │   │   │   └── fluent-bit
│   │   │   │       ├── configmap.yaml
│   │   │   │       ├── daemonset.yaml
│   │   │   │       └── rbac.yaml
│   │   │   ├── 08-ingress-gateway
│   │   │   │   ├── ingress-controller.yaml
│   │   │   │   └── ingress-rules.yaml
│   │   │   ├── 09-backup-recovery
│   │   │   │   └── velero-backup.yaml
│   │   │   ├── 10-testing
│   │   │   │   └── performance-tests.yaml
│   │   │   ├── 11-ci-cd
│   │   │   │   └── argocd-deployment.yaml
│   │   │   ├── 12-security
│   │   │   │   ├── falco-deployment.yaml
│   │   │   │   └── trivy-scanner.yaml
│   │   │   ├── overlays
│   │   │   │   ├── dev
│   │   │   │   │   └── kustomization.yaml
│   │   │   │   ├── prod
│   │   │   │   │   └── kustomization.yaml
│   │   │   │   └── staging
│   │   │   │       └── kustomization.yaml
│   │   │   ├── IMPLEMENTATION_SUMMARY.md
│   │   │   ├── README.md
│   │   │   └── kustomization.yaml
│   │   ├── monitoring
│   │   │   ├── grafana-deployment.yaml
│   │   │   ├── jaeger-deployment.yaml
│   │   │   ├── loki-deployment.yaml
│   │   │   ├── monitoring-services.yaml
│   │   │   └── prometheus-deployment.yaml
│   │   ├── network-policies
│   │   │   └── network-policy.yaml
│   │   ├── overlays
│   │   │   ├── dev
│   │   │   │   └── kustomization.yaml
│   │   │   ├── prod
│   │   │   │   └── kustomization.yaml
│   │   │   └── staging
│   │   │       └── kustomization.yaml
│   │   ├── rbac
│   │   │   ├── role.yaml
│   │   │   ├── rolebinding.yaml
│   │   │   └── serviceaccount.yaml
│   │   ├── services
│   │   │   ├── auto-repair-deployment.yaml
│   │   │   ├── code-analyzer-deployment.yaml
│   │   │   ├── orchestrator-deployment.yaml
│   │   │   ├── services.yaml
│   │   │   └── vulnerability-detector-deployment.yaml
│   │   ├── storage
│   │   │   ├── pvc.yaml
│   │   │   └── storageclass.yaml
│   │   ├── README.md
│   │   ├── configmap.yaml
│   │   ├── hpa.yaml
│   │   ├── kustomization.yaml
│   │   ├── namespace.yaml
│   │   └── secrets.yaml
│   └── monitoring
│       ├── alerts
│       │   └── service-alerts.yml
│       ├── grafana-dashboard.json
│       └── prometheus.yml
├── legacy
│   ├── v1-python-drones
│   │   ├── config
│   │   │   ├── __init__.py
│   │   │   └── drone_config.py
│   │   ├── drones
│   │   │   ├── __init__.py
│   │   │   ├── autopilot_drone.py
│   │   │   ├── base_drone.py
│   │   │   ├── coordinator_drone.py
│   │   │   └── deployment_drone.py
│   │   ├── utils
│   │   │   ├── __init__.py
│   │   │   └── helpers.py
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── main.py
│   └── v2-multi-islands
│       ├── bridges
│       │   ├── __init__.py
│       │   └── language_bridge.py
│       ├── config
│       │   ├── __init__.py
│       │   └── island_config.py
│       ├── islands
│       │   ├── __init__.py
│       │   ├── base_island.py
│       │   ├── go_island.py
│       │   ├── java_island.py
│       │   ├── python_island.py
│       │   ├── rust_island.py
│       │   └── typescript_island.py
│       ├── orchestrator
│       │   ├── __init__.py
│       │   └── island_orchestrator.py
│       ├── utils
│       │   ├── __init__.py
│       │   └── helpers.py
│       ├── README.md
│       ├── __init__.py
│       └── main.py
├── mcp-servers -> services/mcp
├── ops
│   ├── migration
│   │   ├── scripts
│   │   │   ├── v1_to_v2.py
│   │   │   └── v2_to_v1.py
│   │   ├── templates
│   │   │   └── migration_report.md
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── migrator.py
│   ├── onboarding
│   │   └── pr-template.md
│   ├── reports
│   │   ├── schema
│   │   │   ├── compliance.schema.json
│   │   │   └── sla.schema.json
│   │   └── language-compliance.json
│   └── runbooks
│       └── ng-degrade.json
├── scripts
│   ├── naming
│   │   └── language-checker.mjs
│   └── fix-copilot.sh
├── services
│   ├── agents
│   │   ├── auto-repair
│   │   │   └── README.md
│   │   ├── code-analyzer
│   │   │   └── README.md
│   │   ├── dependency-manager
│   │   │   ├── config
│   │   │   │   └── manager.yaml
│   │   │   ├── src
│   │   │   │   ├── analyzers
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── base_analyzer.py
│   │   │   │   │   ├── go_analyzer.py
│   │   │   │   │   ├── npm_analyzer.py
│   │   │   │   │   └── pip_analyzer.py
│   │   │   │   ├── combination
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── combination_templates.py
│   │   │   │   │   ├── core_satellite.py
│   │   │   │   │   ├── dynamic_adjuster.py
│   │   │   │   │   └── quarterly_review.py
│   │   │   │   ├── crossplatform
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── arvr_integration.py
│   │   │   │   │   ├── emergency_response.py
│   │   │   │   │   ├── iot_integration.py
│   │   │   │   │   ├── risk_assessment.py
│   │   │   │   │   ├── tech_stack_matrix.py
│   │   │   │   │   └── web3_integration.py
│   │   │   │   ├── enterprise
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── analytics.py
│   │   │   │   │   ├── integration.py
│   │   │   │   │   ├── recommendation.py
│   │   │   │   │   └── security.py
│   │   │   │   ├── evaluation
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── evaluation_report.py
│   │   │   │   │   ├── smartv_framework.py
│   │   │   │   │   └── weight_config.py
│   │   │   │   ├── future
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── development_tracker.py
│   │   │   │   │   ├── lowcode_integration.py
│   │   │   │   │   ├── privacy_framework.py
│   │   │   │   │   └── sustainable_analyzer.py
│   │   │   │   ├── implementation
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── action_guide.py
│   │   │   │   │   ├── implementation_plan.py
│   │   │   │   │   └── success_metrics.py
│   │   │   │   ├── models
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── dependency.py
│   │   │   │   │   ├── update.py
│   │   │   │   │   └── vulnerability.py
│   │   │   │   ├── scanners
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── license_scanner.py
│   │   │   │   │   └── vulnerability_scanner.py
│   │   │   │   ├── strategy
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── case_study_engine.py
│   │   │   │   │   ├── evolution_tracker.py
│   │   │   │   │   ├── resource_optimizer.py
│   │   │   │   │   └── strategy_advisor.py
│   │   │   │   ├── updaters
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── auto_updater.py
│   │   │   │   ├── utils
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── audit_logger.py
│   │   │   │   │   ├── dependency_tree.py
│   │   │   │   │   ├── language_boundary.py
│   │   │   │   │   └── policy_simulator.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── engine.py
│   │   │   ├── tests
│   │   │   │   ├── __init__.py
│   │   │   │   ├── test_models.py
│   │   │   │   ├── test_phase10.py
│   │   │   │   ├── test_phase2.py
│   │   │   │   ├── test_phase3.py
│   │   │   │   ├── test_phase4.py
│   │   │   │   ├── test_phase5.py
│   │   │   │   ├── test_phase6.py
│   │   │   │   ├── test_phase7.py
│   │   │   │   ├── test_phase8.py
│   │   │   │   └── test_phase9.py
│   │   │   └── README.md
│   │   ├── orchestrator
│   │   │   └── README.md
│   │   ├── vulnerability-detector
│   │   │   └── README.md
│   │   ├── README.md
│   │   └── runbook-executor.sh
│   ├── mcp
│   │   ├── deploy
│   │   │   ├── deployment.yaml
│   │   │   ├── hpa.yaml
│   │   │   ├── pdb.yaml
│   │   │   ├── rbac.yaml
│   │   │   └── service.yaml
│   │   ├── .eslintrc.json
│   │   ├── .gitignore
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── VALIDATION.md
│   │   ├── code-analyzer.js
│   │   ├── comprehensive-validator.js
│   │   ├── deployment-validator.js
│   │   ├── doc-generator.js
│   │   ├── index.js
│   │   ├── logic-validator.js
│   │   ├── package-lock.json
│   │   ├── package.json
│   │   ├── performance-analyzer.js
│   │   ├── security-scanner.js
│   │   ├── slsa-validator.js
│   │   └── test-generator.js
│   └── __init__.py
├── shared
│   ├── config
│   │   ├── __init__.py
│   │   └── base_config.py
│   ├── constants
│   │   ├── __init__.py
│   │   └── system_constants.py
│   ├── utils
│   │   ├── __init__.py
│   │   └── common_helpers.py
│   ├── README.md
│   ├── __init__.py
│   └── language_bridges.py
├── tests
│   ├── performance
│   │   ├── benchmark.js
│   │   └── load-test.js
│   ├── unit
│   │   ├── auto-fix-bot
│   │   │   ├── invalid_bad_threshold.json
│   │   │   └── valid_minimal.json
│   │   ├── cloud-agent-delegation
│   │   │   ├── invalid_bad_weights.json
│   │   │   ├── invalid_missing_provider.json
│   │   │   ├── valid_full.json
│   │   │   └── valid_minimal.json
│   │   ├── osv-advisory
│   │   │   ├── invalid-schema.json
│   │   │   ├── valid-full.json
│   │   │   └── valid-minimal.json
│   │   ├── phases
│   │   │   ├── test_phase19_mcp_servers.py
│   │   │   ├── test_phase20_slsa_provenance.py
│   │   │   ├── test_phase21_cloud_delegation.py
│   │   │   ├── test_phase22_unified_integration.py
│   │   │   └── test_phase24_mind_matrix.py
│   │   ├── benchmark.js
│   │   ├── load-test.js
│   │   ├── test_ai_decision_engine.py
│   │   ├── test_deep_execution_system.py
│   │   ├── test_enhanced_integration.py
│   │   ├── test_executive_auto.py
│   │   └── vectors-manifest.yaml
│   ├── vectors
│   │   ├── auto-fix-bot
│   │   │   ├── invalid_bad_threshold.json
│   │   │   └── valid_minimal.json
│   │   ├── cloud-agent-delegation
│   │   │   ├── invalid_bad_weights.json
│   │   │   ├── invalid_missing_provider.json
│   │   │   ├── valid_full.json
│   │   │   └── valid_minimal.json
│   │   ├── osv-advisory
│   │   │   ├── invalid-schema.json
│   │   │   ├── valid-full.json
│   │   │   └── valid-minimal.json
│   │   └── vectors-manifest.yaml
│   └── README.md
├── tools
│   ├── ci
│   │   ├── contract-checker.js
│   │   ├── language-checker.js
│   │   └── policy-simulate.yml
│   ├── cli
│   │   ├── bin
│   │   │   └── admin-copilot.js
│   │   ├── README.md
│   │   └── package.json
│   ├── docs
│   │   ├── generate_knowledge_graph.py
│   │   ├── generate_mndoc_from_readme.py
│   │   ├── pr_comment_summary.py
│   │   ├── project_to_superroot.py
│   │   ├── provenance_injector.py
│   │   ├── scan_repo_generate_index.py
│   │   └── validate_index.py
│   ├── scripts
│   │   ├── artifacts
│   │   │   └── build.sh
│   │   ├── backup
│   │   │   ├── backup.sh
│   │   │   └── restore.sh
│   │   ├── naming
│   │   │   ├── check-naming.sh
│   │   │   ├── language-checker.mjs
│   │   │   └── suggest-name.mjs
│   │   ├── README.md
│   │   ├── advanced-push-protection.sh
│   │   ├── analyze.sh
│   │   ├── automation-entry.sh
│   │   ├── build-matrix.sh
│   │   ├── check-env.sh
│   │   ├── check-sync-contracts.js
│   │   ├── conditional-deploy.sh
│   │   ├── generate-directory-tree.sh
│   │   ├── manage-secret-patterns.py
│   │   ├── repair.sh
│   │   ├── run-v2.sh
│   │   ├── setup.sh
│   │   ├── validate-config.js
│   │   ├── validate_auto_fix_bot_config.py
│   │   └── vulnerability-alert-handler.py
│   └── utilities
│       ├── validate_vectors.py
│       └── validate_yaml.py
├── .auto-fix-bot.yml -> config/auto-fix-bot.yml
├── .env.example
├── .eslintrc.yaml
├── .gitignore
├── .prettierrc
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── DOCUMENTATION_INDEX.md
├── Dockerfile
├── Makefile
├── README.en.md
├── README.md
├── SECURITY.md
├── auto-fix-bot-dashboard.html
├── auto-fix-bot.yml -> config/auto-fix-bot.yml
├── copilot-diagnosis-20251201-095830.txt
├── deploy.sh
├── docker-compose.dev.yml
├── docker-compose.yml
├── jest.config.js
├── nginx.conf
├── package-lock.json
├── package.json
├── pnpm-lock.yaml
├── pyproject.toml
├── synergymesh.yaml
└── tsconfig.json

306 directories, 1186 files
```

---

## 📁 主要目錄說明

| 目錄              | 圖示 | 說明                                                          |
| ----------------- | ---- | ------------------------------------------------------------- |
| `.devcontainer/`  | 🐳   | 開發容器配置                                                  |
| `.github/`        | 🔄   | GitHub Actions 工作流程和配置                                 |
| `.vscode/`        | 🆚   | VS Code 編輯器配置                                            |
| `apps/`           | 📱   | 應用程式 (Web 前端)                                           |
| `automation/`     | 🤖   | 自動化模組 (智能、自主、架構、超自動化)                       |
| `config/`         | ⚙️   | 配置中心                                                      |
| `core/`           | 🏛️   | 核心平台服務                                                  |
| `docs/`           | 📚   | 專案文件                                                      |
| `governance/`     | ⚖️   | 治理與策略 (Schema、策略、SBOM)                               |
| `infrastructure/` | 🏗️   | 基礎設施 (K8s、監控)                                          |
| `legacy/`         | 📜   | 舊版存檔                                                      |
| `mcp-servers/`    | 🔌   | MCP (Model Context Protocol) 伺服器 (符號連結至 services/mcp) |
| `ops/`            | 📋   | 運維資源                                                      |
| `scripts/`        | 📝   | 根目錄腳本                                                    |
| `services/`       | ⚙️   | 服務層                                                        |
| `shared/`         | 📦   | 共用資源                                                      |
| `tests/`          | 🧪   | 測試套件                                                      |
| `tools/`          | 🔧   | 工具腳本                                                      |

---

## 🔗 相關文件

- [📋 PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) - 專案結構解構圖（含評估）
- [🏗️ SYSTEM_ARCHITECTURE.md](./architecture/SYSTEM_ARCHITECTURE.md) - 系統架構文件
- [📖 README.md](../README.md) - 專案說明

---

<div align="center">

**📅 最後更新：2024 年 12 月**

**📝 此文件由 `tree` 命令自動生成**

**統計：306 個目錄，1,186 個檔案**

[返回頂部](#-unmanned-island---完整目錄樹狀結構)

</div>
