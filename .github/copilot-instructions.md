# GitHub Copilot Instructions

## 📋 AI Behavior Contract Compliance

**IMPORTANT:** All AI interactions must comply with the [AI Behavior Contract](AI-BEHAVIOR-CONTRACT.md). Key principles:

- ✅ Use concrete, specific language (no vague excuses)
- ✅ Provide binary responses: CAN_COMPLETE or CANNOT_COMPLETE with specifics
- ✅ Decompose large tasks proactively (2-3 subtasks with execution order)
- ✅ Default to draft mode for file modifications (unless explicitly authorized)

**Before responding, verify compliance with contract sections 1-4.**

---

## 🏗️ Technical Guidelines

1. **Grasp the three-systems view early.** Start with the repo-level overview in [README.md](../README.md): SynergyMesh Core (AI decision + registries under `core/`), Structural Governance (schema + policy loops in `governance/` and `config/`), and the Autonomous/Drone stack (`automation/autonomous/`, `config/drone-config.yml`). When touching a feature, note which subsystem owns it and route changes through that directory's README before editing code.
2. **Treat YAML configs as the source of truth.** `synergymesh.yaml`, `config/system-manifest.yaml`, and `config/unified-config-index.yaml` drive most orchestrations. When adding services, update the manifest + module map first, then wire code. Never edit generated docs (`docs/generated-mndoc.yaml`, `docs/knowledge-graph.yaml`, `docs/superroot-entities.yaml`) by hand—regenerate via `make all-kg` after README/config changes.
3. **Respect workspace boundaries.** The root `package.json` is an npm workspace hub; run `npm install` once, then `npm run lint|test|build --workspaces --if-present` for the whole fleet or target a package (`npm run test -w core/contract_service/contracts-L1/contracts`). Keep TypeScript output confined to `dist/` per workspace tsconfig.
4. **Follow service-specific stacks.**
   - `core/contract_service/contracts-L1/contracts`: Express + Zod + Sigstore; controllers + middleware live under `src/`. Mirror TypeScript strict rules from `.github/island-ai-instructions.md` (2-space indent, camelCase functions, explicit return types).
   - `mcp-servers/`: Node-based MCP endpoints; each folder has its own CLI entry—run `npm start -w mcp-servers/<server>`.
   - Python automation (e.g., `tools/docs/*.py`, `automation/intelligent/`): use Python 3.10+ and virtualenv/uv; invoke scripts via `python3 <script>` and keep outputs under `docs/`.
5. **Use the documented workflows.**
   - Knowledge base regeneration: `make all-kg` (depends on `python3`); CI drift check uses the same target, so run it locally before committing.
   - Core stack smoke test: `npm run dev:stack` (runs `scripts/start-synergymesh-dev.sh`, which boots the contract service + MCP adapters).
   - Docs lint: `npm run docs:lint` to validate Markdown.
   - Governance validation: `python tools/docs/validate_index.py --verbose` before touching schema or policy files.
6. **Understand cross-cutting safety hooks.** Any change in `core/safety_mechanisms/`, `core/slsa_provenance/`, or `governance/policies/` must keep SLSA level promises. If you add a new build artifact, ensure Sigstore signing + provenance entries are updated and referenced in `core/contract_service/contracts-L1/contracts/BUILD_PROVENANCE.md`.
7. **Drone/autonomy code has its own cadence.** ROS/C++ pieces live under `automation/autonomous/architecture-stability`, API governance glue is Python, observability agents are Go. Keep each skeleton isolated; share data through the YAML contracts in `automation/autonomous/docs-examples/` rather than direct imports.
8. **Documentation-first changes.** For new capabilities, update the relevant index (`DOCUMENTATION_INDEX.md` + subsystem README) before code so downstream knowledge-graph jobs stay consistent. Match the existing bilingual style: headings in Traditional Chinese + English explanations when already present.
9. **Generated artefacts & CI expectations.** GitHub Actions expect `docs/knowledge-health-report.yaml` and similar files to exist; if you change detection logic under `automation/self_awareness_report.py`, also adjust the dashboards referenced in `docs/KNOWLEDGE_HEALTH.md`. Never delete those files without updating workflows under `.github/workflows/`.
10. **Debugging tips.** Prefer workspace-level scripts over ad-hoc commands. For npm packages, run `npm exec --workspace <pkg> ts-node src/index.ts` instead of global binaries. For Python tooling, use `PYTHONPATH=.` so shared modules in `core/` resolve. When the devcontainer fails (common `/home/node` issue), ensure `.devcontainer` scripts create the `node` user before running workspace commands.

感謝協作。
