#!/usr/bin/env bash
set -euo pipefail

mkdir -p artifacts/{sbom,attestations,reports}
mkdir -p artifacts/reports/{naming,auto-fix/details}
mkdir -p var

echo "bootstrap: ok"
