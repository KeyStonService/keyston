#!/bin/sh
# Island AI post-commit hook
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPT="$REPO_ROOT/scripts/sync/watch-and-sync.sh"

if [ -x "$SCRIPT" ]; then
  echo "[post-commit] syncing scaffold via manifest"
  "$SCRIPT" --once
else
  echo "[post-commit] sync script not found: $SCRIPT" >&2
fi
