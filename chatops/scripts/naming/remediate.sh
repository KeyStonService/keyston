#!/usr/bin/env bash
set -euo pipefail
# Intentional conservative default: do NOT auto-rename manifests here.
# Real implementation should create a branch + PR, never mutate main directly.
echo "remediate: noop (safe by default)"
