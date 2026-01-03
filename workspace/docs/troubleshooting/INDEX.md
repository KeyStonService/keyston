# Troubleshooting Index

Use this index whenever a self-awareness report, workflow log, or Copilot alert
mentions a failing signal. Each entry explains what the alert means, the
expected remediation steps, and which tasks/commands to run from VS Code Tasks
if you cannot use the terminal.

## Signal → Runbook Map

| Signal or Alert                    | Where It Comes From                                               | Runbook                                                                                                                                                                            |
| ---------------------------------- | ----------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Lint` / `Island AI Lint` failures | `project-self-awareness` workflows, VS Code **🔍 NPM: Lint** task | See [docs/troubleshooting/github-copilot-agent-fix.md](github-copilot-agent-fix.md) for environment fixes, then rerun `npm run lint --workspaces --if-present` or the VS Code task |
| `Tests` failures                   | `project-self-awareness` workflows, **🧪 NPM: 測試** task         | Investigate the reported suite inside the affected workspace and rerun the workspace-specific `npm test`                                                                           |
| `TypeScript Build` failure         | `project-self-awareness` workflows (`npx tsc -b tsconfig.json`)   | Run `npx tsc -b tsconfig.json`, fix type errors in the referenced project(s), and rerun                                                                                            |
| `Security Audit` failure           | `npm audit --workspaces --include-workspace-root`                 | Update dependencies or add advisories to the exceptions list per security policy, then rerun `npm audit`                                                                           |
| `Workspace Cleanliness` failure    | nightly self-awareness workflow (git status)                      | Commit or discard generated files so CI has a clean tree, then rerun lint/tests                                                                                                    |

## Execution Shortcuts

1. Open the VS Code Command Palette → **Run Task**.
2. Choose the task that matches the failing signal:
   - **🔍 NPM: Lint** – runs `npm run lint --workspaces --if-present`.
   - **🧪 NPM: 測試** – runs `npm test --workspaces --if-present`.
   - **🔨 NPM: 建置** – runs `npm run build --workspaces --if-present` (also
     exercises TypeScript build).
3. For audits, run **📦 NPM: 安裝依賴** first to ensure the lockfile is in sync,
   then execute `npm audit --workspaces --include-workspace-root` inside a
   terminal.

## Automation Sampling Flow

Use the CLI in `tools/cli` when you need a reproducible automation trail (for
example, before handing the repo to another agent):

1. Seed the operation catalog once per repo clone:

  ```bash
  cd tools/cli
  npm run dev -- automation:setup
  ```

1. Run the sample-friendly subset (safe for quick spot checks):

  ```bash
  npm run dev -- automation:run --sample
  ```

  This updates `tools/cli/island.automation.json`, records the mode as
  `sample`, and automatically writes `reports/self-awareness-sample.md` plus
  `reports/self-awareness-sample.json`.


1. Need to re-run the reporter manually (for ad-hoc debugging)? Execute:

  ```bash
  python automation/self_awareness_report.py \
    --lint-cmd "npm run lint --workspaces --if-present" \
    --test-cmd "npm test --workspaces --if-present" \
    --automation-cmd "Audit=npm audit --workspaces --include-workspace-root" \
    --output reports/self-awareness-manual.md \
    --json-output reports/self-awareness-manual.json \
    --fail-on-errors
  ```

The `--json-output` flag emits a machine-readable report for dashboards, while
`--fail-on-errors` keeps automation signals red whenever a command exits non-0.

## Reporting Gaps

If you find a repeated failure that is missing from this index, append a new row
with:

1. The exact signal text (copy/paste from the workflow comment or log).
2. The command or VS Code task that produces it.
3. The canonical runbook, ideally linking to a doc under `docs/issues/`.

This keeps the repository self-aware of new regression classes without waiting
for humans to rediscover the fix each time.
