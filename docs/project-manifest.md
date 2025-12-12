# SynergyMesh Project Manifest

This manifest gives the repository a clear voice. Any contributor or agent can
quickly learn what this system is, what it currently needs, and which changes
are explicitly out of bounds.

## Identity & Mission

- **Name**: SynergyMesh – Unmanned Island System
- **Role**: Multi-agent automation platform for intelligent business and
  security orchestration
- **Mission Statement**: Deliver trustworthy automation by combining human
  guardrails with AI-driven execution so that complex cloud operations run
  safely and predictably.

## Active Needs (What We Want)

- Harden CI/CD workflows (integration-deployment, phase1-integration, and any
  new delegations) to prevent costly reruns.
- Keep TypeScript/ESLint configs consistent across `island-ai`, MCP servers, and
  future workspaces.
- Document operational runbooks for non-CLI teammates (VS Code Tasks, UI
  walk-throughs).
- Maintain agent role definitions so every delegate knows responsibilities and
  limitations before touching the codebase.
- Keep [docs/troubleshooting/INDEX.md](docs/troubleshooting/INDEX.md) and
  [docs/issues/known-failures.md](docs/issues/known-failures.md) current so
  automation alerts map directly to a remediation playbook.

## Guardrails (What We Avoid)

- Changes that bypass documented governance or security policies.
- Direct edits to production infrastructure without matching runbook entries or
  approval signals.
- Introducing automation that lacks explainability or overrides human review
  gates.
- Tooling drift between workspaces (e.g., partially upgraded Node/TypeScript
  stacks) that would cause Copilot or CI to fail silently.

## Proof & Self-Check Signals

- ✅ `npm run lint --workspaces --if-present` and
  `npm test --workspaces --if-present` succeed after any tooling change.
- ✅ `.github/workflows/project-self-awareness.yml` posts an up-to-date summary
  on every pull request.
- ✅ Agents listed in `config/agents/team/virtual-experts.yaml` have matching
  docs under `docs/agents/` describing scope and anti-goals.
- ✅ `.github/workflows/project-self-awareness-nightly.yml` raises an issue when
  automation signals fail and links to the troubleshooting index for context.
- ✅ `docs/troubleshooting/INDEX.md` maps every self-awareness signal to the
  appropriate runbook or known-failure entry.

## How to Update This Manifest

1. Edit this file when the repository’s scope or needs change.
2. Re-run
   `automation/self_awareness_report.py --output self-awareness-report.md`
   (automatically handled in CI) so PR comments reflect the newest statements.
3. Mention notable changes in `CHANGELOG.md` when the mission or guardrails are
   updated.
