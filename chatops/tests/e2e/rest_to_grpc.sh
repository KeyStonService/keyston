#!/usr/bin/env bash
# tests/e2e/rest_to_grpc.sh
set -euo pipefail
GATEWAY=${GATEWAY:-http://localhost:8081}
ENGINE=${ENGINE:-http://localhost:8080}
echo "=== E2E REST→gRPC stub ==="
curl -sf "$GATEWAY/healthz" && echo " gateway ok"
curl -sf "$ENGINE/healthz" && echo " engine ok"
curl -sf "$GATEWAY/api/passthrough?target=engine" | jq .
echo "=== done ==="
