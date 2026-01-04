#!/bin/bash
# fmt.sh - Format all YAML/JSON/Markdown files

set -e

echo "🔧 Formatting files..."

# Check for required tools
command -v yq >/dev/null 2>&1 || { echo "❌ yq is required but not installed."; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "❌ jq is required but not installed."; exit 1; }

# Format YAML files
echo "  📄 Formatting YAML files..."
find . -name "*.yaml" -o -name "*.yml" | while read file; do
    if [[ "$file" != "./.git"* ]]; then
        echo "    Formatting $file"
        yq eval --prettyPrint -i "$file"
    fi
done

# Format JSON files
echo "  📄 Formatting JSON files..."
find . -name "*.json" | while read file; do
    if [[ "$file" != "./.git"* ]]; then
        echo "    Formatting $file"
        jq '.' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
    fi
done

echo "✅ Formatting complete"