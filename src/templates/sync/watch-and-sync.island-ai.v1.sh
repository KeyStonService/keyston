#!/bin/sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MANIFEST="${MANIFEST:-${REPO_ROOT}/island.bootstrap.stage0.yaml}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
MODE="once"
INTERVAL=5

usage() {
  cat <<'EOF'
Usage: watch-and-sync.sh [options]

Options:
  --once           Run a single sync (default)
  --watch          Watch templates/ and manifest for changes
  --interval <sec> Polling interval when --watch without observers (default: 5)
  --help           Show this help message
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --once)
      MODE="once"
      shift
      ;;
    --watch)
      MODE="watch"
      shift
      ;;
    --interval)
      INTERVAL="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

run_sync() {
  if [ ! -f "$MANIFEST" ]; then
    echo "[sync] manifest not found: $MANIFEST" >&2
    return 1
  fi

  echo "[sync] materializing scaffold via $MANIFEST"
  "$PYTHON_BIN" "$REPO_ROOT/tools/bootstrap_from_manifest.py" "$MANIFEST" --apply --steps scaffold.directories materialize.templates
}

if [ "$MODE" = "once" ]; then
  run_sync
  exit $?
fi

watch_with_tool() {
  WATCH_CMD="$1"
  shift
  $WATCH_CMD "$@" -- run_sync
}

# Prefer watchexec, fall back to fswatch or entr.
if command -v watchexec >/dev/null 2>&1; then
  watch_with_tool watchexec --watch "$REPO_ROOT/templates" --watch "$MANIFEST"
elif command -v fswatch >/dev/null 2>&1; then
  fswatch -o "$REPO_ROOT/templates" "$MANIFEST" | while read -r _; do
    run_sync
  done
elif command -v entr >/dev/null 2>&1; then
  find "$REPO_ROOT/templates" -type f >"$REPO_ROOT/.watch-and-sync.lst"
  printf '%s\n' "$MANIFEST" >>"$REPO_ROOT/.watch-and-sync.lst"
  entr -r sh -c run_sync <"$REPO_ROOT/.watch-and-sync.lst"
else
  echo "[sync] no watch utility found; falling back to polling every ${INTERVAL}s" >&2
  while true; do
    run_sync
    sleep "$INTERVAL"
  done
fi
