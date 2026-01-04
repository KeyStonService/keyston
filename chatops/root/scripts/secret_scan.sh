#!/bin/bash
# secret_scan.sh - Scan for secrets in the repository

set -e

echo "🔍 Scanning for secrets..."

# Check for common secret patterns
SECRETS_FOUND=false

# Scan for potential API keys
if grep -r -i "api[_-]?key\|secret\|token\|password" . --include="*.yaml" --include="*.yml" --include="*.json" --exclude-dir=".git" --exclude-dir="dist" | grep -v "example\|dummy\|placeholder\|xxx" > /tmp/secret_scan.txt; then
    echo "  ⚠️  Potential secrets found:"
    cat /tmp/secret_scan.txt | head -10
    SECRETS_FOUND=true
fi

# Scan for GitHub tokens
if grep -r "ghp_\|github_pat_\|gho_\|ghu_\|ghs_\|ghr_" . --exclude-dir=".git" --exclude-dir="dist" > /tmp/github_tokens.txt; then
    echo "  ⚠️  GitHub tokens found:"
    cat /tmp/github_tokens.txt
    SECRETS_FOUND=true
fi

# Scan for AWS keys
if grep -r "AKIA[0-9A-Z]{16}" . --exclude-dir=".git" --exclude-dir="dist" > /tmp/aws_keys.txt; then
    echo "  ⚠️  AWS access keys found:"
    cat /tmp/aws_keys.txt
    SECRETS_FOUND=true
fi

if [ "$SECRETS_FOUND" = true ]; then
    echo "  ❌ Secrets detected - please review and remove"
    rm -f /tmp/secret_scan.txt /tmp/github_tokens.txt /tmp/aws_keys.txt
    exit 1
else
    echo "  ✅ No secrets detected"
    rm -f /tmp/secret_scan.txt /tmp/github_tokens.txt /tmp/aws_keys.txt
    echo "✅ Secret scan complete"
fi