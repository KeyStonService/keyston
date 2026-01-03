#!/usr/bin/env bash
set -euo pipefail
mkdir -p artifacts/attestations
cat > artifacts/attestations/provenance.intoto.json <<'EOF'
{"tool":"provenance-stub","slsa":"v1","level":"L3-target","notes":"replace with official generator + cosign attest"}
EOF
echo "provenance: wrote artifacts/attestations/provenance.intoto.json"
