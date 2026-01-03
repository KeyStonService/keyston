#!/usr/bin/env bash
set -euo pipefail
mkdir -p artifacts/sbom
cat > artifacts/sbom/sbom.spdx.json <<'EOF'
{"tool":"sbom-stub","format":"spdx-json","components":[]}
EOF
echo "sbom: wrote artifacts/sbom/sbom.spdx.json"
