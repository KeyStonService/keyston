# intelligent-hyperautomation (chatops monorepo)

This repository implements an enterprise-grade, production-ready (prod) GitOps + CI/CD + Governance + Supply Chain Security system with:
- Multi-agent ChatOps automation (detect → decide → fix → PR → verify → merge)
- Naming governance (observe/validate/repair/migrate/audit) end-to-end
- Policy-as-Code (OPA/Conftest + Kyverno + Gatekeeper)
- Supply-chain security (SBOM/Provenance/Attestation/Cosign-ready layout)
- Artifact-to-App pipeline (docx/pdf/md/txt → structured modules)

Directory anchors:
- .github/workflows/        CI/CD + auto-fix PR loop
- scripts/                 CLI + scanners + fixers + playbooks
- policies/                OPA Rego + Conftest tests
- deployments/              K8s manifests (PrometheusRule/Grafana/Kyverno/Gatekeeper)
- artifacts/                modules/reports/evidence/audit outputs (generated)
- services/                 application services (engine-python, gateway-ts)
- proto/                    shared contracts
- tests/                    integration/e2e suites
- var/                      local audit logs (dev)

License: Apache-2.0
