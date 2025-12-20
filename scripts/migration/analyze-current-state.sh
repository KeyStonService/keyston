#!/bin/bash
set -e

echo "=== MachineNativeOps 現狀分析工具 ==="
echo "分析時間: $(date)"
echo "分支: $(git branch --show-current)"
echo ""

# 1. 頂層目錄統計
echo "📊 頂層目錄統計"
echo "=================="
TOP_LEVEL_COUNT=$(find . -maxdepth 1 -type d -not -path '.' -not -path './.git' | wc -l)
echo "頂層目錄數量: $TOP_LEVEL_COUNT"

echo ""
echo "所有頂層目錄:"
find . -maxdepth 1 -type d -not -path '.' -not -path './.git' | sort

# 2. 重複目錄檢測
echo ""
echo "🔍 重複目錄檢測"
echo "=============="

# 檢測同義詞目錄
if [ -d "infra" ] && [ -d "infrastructure" ]; then
    echo "⚠️  發現重複: infra/ ←→ infrastructure/"
fi

if [ -d "deployment" ] && [ -d "deploy" ]; then
    echo "⚠️  發現重複: deployment/ ←→ deploy/"
fi

if [ -d "script" ] && [ -d "scripts" ]; then
    echo "⚠️  發現重複: script/ ←→ scripts/"
fi

if [ -d "ai" ] && [ -d "island-ai" ]; then
    echo "⚠️  發現重複: ai/ ←→ island-ai/"
fi

# 3. 命名規範檢測
echo ""
echo "📝 命名規範檢測"
echo "=============="

# 檢測 PascalCase 目錄
PASCAL_CASE_DIRS=$(find . -maxdepth 1 -type d -not -path '.' -not -path './.git' | grep -E '[A-Z][a-z]+[A-Z]')
if [ -n "$PASCAL_CASE_DIRS" ]; then
    echo "⚠️  PascalCase 目錄 (應改為 kebab-case):"
    echo "$PASCAL_CASE_DIRS"
fi

# 檢測過短目錄
SHORT_DIRS=$(find . -maxdepth 1 -type d -not -path '.' -not -path './.git' | grep -E '^./[a-z]{1,2}$')
if [ -n "$SHORT_DIRS" ]; then
    echo "⚠️  過短目錄 (語義不明):"
    echo "$SHORT_DIRS"
fi

# 4. 配置文件分散情況
echo ""
echo "⚙️  配置文件分散情況"
echo "=================="

echo "配置相關目錄:"
for dir in .config config .devcontainer .vscode; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir/"
        find "$dir" -type f | head -5 | sed 's/^/    /'
        echo "    ... ($(find "$dir" -type f | wc -l) 個文件)"
    fi
done

# 5. 治理目錄分散情況
echo ""
echo "⚖️  治理目錄分散情況"
echo "=================="

GOVERNANCE_DIRS=$(find . -type d -name "*govern*" | head -10)
if [ -n "$GOVERNANCE_DIRS" ]; then
    echo "治理相關目錄:"
    echo "$GOVERNANCE_DIRS"
fi

# 6. 核心模組現況
echo ""
echo "🔷 核心模組現況"
echo "=============="

for module in core governance autonomous; do
    if [ -d "$module" ]; then
        echo "  ✓ $module/ 存在"
        echo "    文件數: $(find "$module" -type f | wc -l)"
        echo "    子目錄: $(find "$module" -type d | wc -l)"
    else
        echo "  ✗ $module/ 不存在"
    fi
done

# 7. 依賴關係簡單分析
echo ""
echo "🔗 依賴關係分析"
echo "=============="

if [ -f "package.json" ]; then
    echo "Node.js 依賴:"
    echo "  dependencies: $(cat package.json | jq '.dependencies | keys | length' 2>/dev/null || echo "N/A")"
    echo "  devDependencies: $(cat package.json | jq '.devDependencies | keys | length' 2>/dev/null || echo "N/A")"
fi

if [ -f "machinenativeops.yaml" ]; then
    echo "✓ 主配置文件存在: machinenativeops.yaml"
    VERSION=$(grep "version:" machinenativeops.yaml | head -1 | cut -d: -f2 | tr -d ' "')
    echo "  當前版本: $VERSION"
fi

# 8. 問題總結
echo ""
echo "🚨 問題總結"
echo "=========="

ISSUES_COUNT=0

if [ $TOP_LEVEL_COUNT -gt 15 ]; then
    echo "❌ 頂層目錄過多 ($TOP_LEVEL_COUNT > 15)"
    ((ISSUES_COUNT++))
fi

if [ -d "infra" ] && [ -d "infrastructure" ]; then
    echo "❌ 存在重複目錄 (infra/infrastructure)"
    ((ISSUES_COUNT++))
fi

if [ -d "deployment" ] && [ -d "deploy" ]; then
    echo "❌ 存在重複目錄 (deployment/deploy)"
    ((ISSUES_COUNT++))
fi

if [ -n "$PASCAL_CASE_DIRS" ]; then
    echo "❌ 存在 PascalCase 命名"
    ((ISSUES_COUNT++))
fi

echo ""
echo "總計發現 $ISSUES_COUNT 個主要問題"

# 9. 建議行動
echo ""
echo "💡 建議行動"
echo "=========="

echo "1. 立即合併重複目錄"
echo "2. 統一命名規範為 kebab-case"
echo "3. 建立 src/ 主目錄結構"
echo "4. 整合分散的配置文件"
echo "5. 統一治理目錄"

echo ""
echo "=== 分析完成 ==="
