#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

SUMMARY_FILE="${GITHUB_STEP_SUMMARY:-}"
PR_BODY="${PR_BODY:-}"
GOV_SCAN_SCRIPT="governance/35-scripts/scan-governance-directory.py" # numeric prefix retained for governance conventions
PYTEST_VERSION="${PYTEST_VERSION:-7.4.4}"

log() {
  echo "[governed-build] $*"
}

install_minimal_governance_deps() {
  log "Installing minimal governance deps (pyyaml jsonschema)"
  pip install pyyaml jsonschema
}

NODE_PRESENT=false
RUST_PRESENT=false
GO_PRESENT=false
PY_PRESENT=false
JAVA_PRESENT=false

if [[ -f package.json ]]; then
  NODE_PRESENT=true
  log "Install Node dependencies"
  npm install

  log "Lint workspaces"
  npm run lint --workspaces --if-present

  log "Docs lint (if defined)"
  npm run docs:lint --if-present

  log "Workspace tests"
  npm run test --workspaces --if-present

  log "Workspace build"
  npm run build --workspaces --if-present
fi

if [[ -d core ]]; then
  RUST_PRESENT=true
  log "Rust formatting and linting"
  cargo fmt --all -- --check
  cargo clippy --workspace --all-targets -- -D warnings

  log "Rust tests"
  cargo test --workspace --all-features

  log "Rust build"
  cargo build --workspace --all-features
fi

if [[ -d services ]]; then
  GO_PRESENT=true
  log "Go formatting check"
  test -z "$(gofmt -l ./services)"

  log "Go tests"
  (cd services && go test ./...)

  log "Go build"
  (cd services && go build ./...)
fi

if [[ -f requirements.txt || -f pyproject.toml || -n "$(find . -maxdepth 3 -name '*.py' -type f -print -quit 2>/dev/null)" ]]; then
  PY_PRESENT=true
  log "Python dependencies and tests"
  if [[ -f requirements.txt ]]; then
    pip install -r requirements.txt
  else
    pip install "pytest==${PYTEST_VERSION}"
  fi
  pytest
fi

if [[ -f pom.xml ]]; then
  JAVA_PRESENT=true
  log "Java tests"
  mvn test

  log "Java build"
  mvn clean install -DskipTests
fi

log "Validate manifest bootstrap"
python3 tools/bootstrap_from_manifest.py island.bootstrap.stage0.yaml --steps scaffold.directories materialize.templates

log "Governance validation"
python -m pip install --upgrade pip
if [[ -f requirements-workflow.txt ]]; then
  pip install -r requirements-workflow.txt
else
  log "requirements-workflow.txt missing; installing minimal governance deps"
  install_minimal_governance_deps
fi
python governance/scripts/validate-governance-structure.py --verbose
make validate-governance-ci
if [[ -f "${GOV_SCAN_SCRIPT}" ]]; then
  python "${GOV_SCAN_SCRIPT}" --deep
else
  log "Governance scan script not found at ${GOV_SCAN_SCRIPT}; skipping deep scan"
fi

if [[ -n "${PR_BODY}" ]]; then
  log "Validate AI Behavior Contract response body"
  .github/scripts/validate-ai-response.sh "${PR_BODY}"
fi

if [[ -n "${SUMMARY_FILE}" ]]; then
  node_status=$([ "$NODE_PRESENT" = true ] && echo "executed" || echo "skipped")
  rust_status=$([ "$RUST_PRESENT" = true ] && echo "executed" || echo "skipped")
  go_status=$([ "$GO_PRESENT" = true ] && echo "executed" || echo "skipped")
  python_status=$([ "$PY_PRESENT" = true ] && echo "executed" || echo "skipped")
  java_status=$([ "$JAVA_PRESENT" = true ] && echo "executed" || echo "skipped")
  {
    echo "## Governed Build Summary"
    echo "- Node tasks: ${node_status}"
    echo "- Rust tasks: ${rust_status}"
    echo "- Go tasks: ${go_status}"
    echo "- Python tasks: ${python_status}"
    echo "- Java tasks: ${java_status}"
    echo "- Governance: executed"
  } >>"$SUMMARY_FILE"
fi
