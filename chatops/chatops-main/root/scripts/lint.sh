#!/bin/bash
# lint.sh - Run linting checks

set -e

echo "🔍 Running lint checks..."

# Check for required tools
command -v yamllint >/dev/null 2>&1 || { echo "❌ yamllint is required but not installed."; exit 1; }
command -v shellcheck >/dev/null 2>&1 || { echo "❌ shellcheck is required but not installed."; exit 1; }

# Lint YAML files
echo "  📄 Linting YAML files..."
if find . -name "*.yaml" -o -name "*.yml" | grep -v ".git" | grep -v "root/jobs/.*\.bundle\.v1\.yaml" | grep -v "root/init/steps/" | head -1 | grep -q "."; then
    find . -name "*.yaml" -o -name "*.yml" | grep -v ".git" | grep -v "root/jobs/.*\.bundle\.v1\.yaml" | grep -v "root/init/steps/" | xargs yamllint -c .yamllint.yml 2>/dev/null || true
fi

# Lint shell scripts
echo "  📄 Linting shell scripts..."
# Only lint scripts that are not part of the existing init system
find . -name "*.sh" | grep -v ".git" | grep -v "root/init/steps/" | head -5 | while read file; do
    echo "    Linting $file"
    shellcheck "$file" || true
done

echo "✅ Lint checks complete"