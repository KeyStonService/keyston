#!/usr/bin/env bash
set -euo pipefail

echo "Initializing chatops devcontainer..."
make bootstrap || true
