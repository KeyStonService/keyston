#!/bin/bash
set -e

# ═══════════════════════════════════════════════════════════════════════════════
# MachineNativeOps Project Name Standardization Script
# ═══════════════════════════════════════════════════════════════════════════════
#
# Purpose: Replace all name variants (SynergyMesh, synergymesh, Unmanned Island)
#          with standardized MachineNativeOps naming according to context
#
# Usage: bash scripts/naming/standardize-project-name.sh [--dry-run]
#
# Reference: Comment #3667258286 - Project Name Standardization Guide
# ═══════════════════════════════════════════════════════════════════════════════

DRY_RUN=false
if [ "$1" = "--dry-run" ]; then
  DRY_RUN=true
  echo "🔍 DRY RUN MODE - No files will be modified"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "MachineNativeOps Project Name Standardization"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

# Backup timestamp
BACKUP_TAG="backup-before-name-standardization-$(date +%Y%m%d-%H%M%S)"

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 1: Analysis
# ═══════════════════════════════════════════════════════════════════════════════

echo "📊 Phase 1: Analyzing current state..."
echo ""

echo "Current name variant counts:"
echo "  SynergyMesh:           $(grep -r "SynergyMesh" --include="*.md" --include="*.yaml" --include="*.yml" --include="*.json" --include="*.ts" --include="*.py" . 2>/dev/null | wc -l)"
echo "  synergymesh:           $(grep -r "synergymesh" --include="*.md" --include="*.yaml" --include="*.yml" --include="*.json" --include="*.ts" --include="*.py" . 2>/dev/null | wc -l)"
echo "  @synergymesh/*:        $(grep -r "@synergymesh/" --include="*.json" --include="*.ts" --include="*.tsx" . 2>/dev/null | wc -l)"
echo "  Unmanned Island System: $(grep -r "Unmanned Island System" --include="*.md" --include="*.yaml" --include="*.yml" . 2>/dev/null | wc -l)"
echo ""

if [ "$DRY_RUN" = true ]; then
  echo "ℹ️  Dry run complete. Run without --dry-run to execute replacements."
  exit 0
fi

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 2: Replacements
# ═══════════════════════════════════════════════════════════════════════════════

echo "🔄 Phase 2: Executing replacements..."
echo ""

# Function to replace in files
replace_in_files() {
  local pattern="$1"
  local replacement="$2"
  local file_patterns="$3"
  local description="$4"
  
  echo "  → $description"
  find . -type f \( $file_patterns \) -not -path "./node_modules/*" -not -path "./.git/*" -not -path "./dist/*" -not -path "./build/*" -exec sed -i.bak "s|$pattern|$replacement|g" {} \;
  find . -name "*.bak" -delete
}

# 2.1: Update machinenativeops.yaml (most critical)
echo "Step 2.1: Update machinenativeops.yaml..."
sed -i.bak 's|name: "SynergyMesh"|name: "MachineNativeOps"|g' machinenativeops.yaml
sed -i.bak 's|SynergyMesh Master Configuration|MachineNativeOps Master Configuration|g' machinenativeops.yaml
rm -f machinenativeops.yaml.bak
echo "  ✅ machinenativeops.yaml updated"
echo ""

# 2.2: Replace in Markdown files (Documentation)
echo "Step 2.2: Updating Markdown documentation..."
replace_in_files "SynergyMesh" "MachineNativeOps" "-name '*.md'" "Display name: SynergyMesh → MachineNativeOps"
replace_in_files "synergymesh\.io" "machinenativeops.io" "-name '*.md'" "Email domains"
replace_in_files "github\.com/SynergyMesh" "github.com/MachineNativeOps" "-name '*.md'" "GitHub org URLs"
replace_in_files "github\.com/synergymesh" "github.com/MachineNativeOps" "-name '*.md'" "GitHub org URLs (lowercase)"

# Handle "Unmanned Island System" - keep as descriptive name with clarification
replace_in_files "Unmanned Island System" "MachineNativeOps (Unmanned Island System)" "-name '*.md'" "Unmanned Island System → with clarification"
# Fix double replacements
replace_in_files "MachineNativeOps \(Unmanned Island System\) \(Unmanned Island System\)" "MachineNativeOps (Unmanned Island System)" "-name '*.md'" "Fix double replacements"

echo "  ✅ Markdown files updated"
echo ""

# 2.3: Replace in YAML/YML files
echo "Step 2.3: Updating YAML configuration files..."
replace_in_files "SynergyMesh" "MachineNativeOps" "-name '*.yaml' -o -name '*.yml'" "YAML: SynergyMesh → MachineNativeOps"
replace_in_files "synergymesh" "machinenativeops" "-name '*.yaml' -o -name '*.yml'" "YAML: synergymesh → machinenativeops"
replace_in_files "synergymesh\.io" "machinenativeops.io" "-name '*.yaml' -o -name '*.yml'" "YAML: email domains"
echo "  ✅ YAML files updated"
echo ""

# 2.4: Replace in JSON files (package.json, etc.)
echo "Step 2.4: Updating JSON files..."
replace_in_files "@synergymesh/" "@machinenativeops/" "-name '*.json'" "NPM scope: @synergymesh/* → @machinenativeops/*"
replace_in_files '"synergymesh"' '"machinenativeops"' "-name '*.json'" "Package keyword"
replace_in_files "github\.com/SynergyMesh" "github.com/MachineNativeOps" "-name '*.json'" "Repository URLs"
echo "  ✅ JSON files updated"
echo ""

# 2.5: Replace in TypeScript/JavaScript files
echo "Step 2.5: Updating TypeScript/JavaScript code..."
replace_in_files "@synergymesh/" "@machinenativeops/" "-name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx'" "Import paths: @synergymesh/* → @machinenativeops/*"
replace_in_files "'synergymesh'" "'machinenativeops'" "-name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx'" "String literals"
replace_in_files '"synergymesh"' '"machinenativeops"' "-name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx'" "String literals"
echo "  ✅ TypeScript/JavaScript files updated"
echo ""

# 2.6: Replace in Python files
echo "Step 2.6: Updating Python code..."
replace_in_files "synergymesh" "machinenativeops" "-name '*.py'" "Package name: synergymesh → machinenativeops"
replace_in_files "SynergyMesh" "MachineNativeOps" "-name '*.py'" "Class/display names"
echo "  ✅ Python files updated"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 3: Verification
# ═══════════════════════════════════════════════════════════════════════════════

echo "✅ Phase 3: Verification..."
echo ""

echo "Remaining occurrences (should be minimal/contextual):"
echo "  SynergyMesh:           $(grep -r "SynergyMesh" --include="*.md" --include="*.yaml" --include="*.yml" --include="*.json" --include="*.ts" --include="*.py" . 2>/dev/null | grep -v "node_modules" | grep -v ".git" | wc -l)"
echo "  synergymesh:           $(grep -r "synergymesh" --include="*.md" --include="*.yaml" --include="*.yml" --include="*.json" --include="*.ts" --include="*.py" . 2>/dev/null | grep -v "node_modules" | grep -v ".git" | wc -l)"
echo "  @synergymesh/*:        $(grep -r "@synergymesh/" --include="*.json" --include="*.ts" --include="*.tsx" . 2>/dev/null | grep -v "node_modules" | grep -v ".git" | wc -l)"
echo ""

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "✅ Project name standardization complete!"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Test the build: npm install && npm run build"
echo "  3. Run tests: npm test"
echo "  4. Commit changes: git add . && git commit -m 'refactor: Standardize project name to MachineNativeOps'"
echo ""
