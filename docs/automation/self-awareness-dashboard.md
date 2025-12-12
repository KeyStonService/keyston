# Self-Awareness Dashboard

Use this guide to keep every automation run (CLI sampling, pull-request gates,
nightly checks) producing the same Markdown + JSON evidence. The JSON snapshots
feed dashboards, while the Markdown stays human-friendly for PR comments.

## Data Sources

| Source                                                  | Trigger                  | Output                                                      | Location                                                |
| ------------------------------------------------------- | ------------------------ | ----------------------------------------------------------- | ------------------------------------------------------- |
| CLI sampling (`npm run dev -- automation:run --sample`) | Developer before handoff | `reports/self-awareness-sample.md/json`                     | Local workspace (tracked in `.gitignore`)               |
| CLI full run (`npm run dev -- automation:run`)          | Pre-deploy self-check    | `reports/self-awareness-full.md/json`                       | Local workspace                                         |
| Pull-request workflow (`project-self-awareness.yml`)    | PR open/sync             | `reports/self-awareness.md/json` artifact, PR comment       | GitHub Actions artifacts named `self-awareness-report`  |
| Nightly workflow (`project-self-awareness-nightly.yml`) | 06:00 UTC daily          | `reports/self-awareness.md/json` artifact, issue on failure | GitHub Actions artifacts named `self-awareness-nightly` |

Each JSON document contains:

- `sections`: parsed copy of
  [docs/project-manifest.md](docs/project-manifest.md).
- `automation`: exit codes, output tails, and commands that were executed.
- `automation_summary`: total/success/failure counts so dashboards can color
  cards without parsing Markdown.

## Local Workflow

1. Initialize operations once per clone:

   ```bash
   cd tools/cli
   npm run dev -- automation:setup
   ```

2. Run the sampling flow (fast lint/tests) before sharing work:

   ```bash
   npm run dev -- automation:run --sample
   ```

   Inspect the results:

   ```bash
   less reports/self-awareness-sample.md
   jq '.automation_summary' reports/self-awareness-sample.json
   ```

3. Run the full suite before deployments:

   ```bash
   npm run dev -- automation:run
   ```

   This generates `reports/self-awareness-full.md/json` and exits non-zero if
   any command fails.

## Artifact-Driven Dashboards

To display results in a dashboard (Grafana, Notion, etc.), pull the JSON from
workflows:

```bash
# Latest PR run (replace RUN_ID)
gh run download RUN_ID -n self-awareness-report -D artifacts/pr-report
jq '.automation_summary' artifacts/pr-report/reports/self-awareness.json

# Nightly run
gh run list --workflow project-self-awareness-nightly.yml --limit 1 --json databaseId,status
```

Each JSON blob is already normalized, so dashboards only need a thin parser to
plot success/failure counts or show the last `n` output lines per signal.

## Failure Triage

- If automation exits non-zero locally, follow the mapping in
  [docs/troubleshooting/INDEX.md](docs/troubleshooting/INDEX.md).
- Nightly workflow failures automatically open an issue linking to the run and
  the troubleshooting index; close the issue only after re-running the failing
  signal and attaching the refreshed JSON.

Keeping these artifacts consistent ensures the entire repo "knows" what failed,
how it was remediated, and where to look next.
