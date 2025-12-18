#!/bin/bash
# Dockerfile 標準驗證腳本
# 用途：檢查所有 Dockerfile 是否遵循 Node.js 使用者權限標準

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 檢查 Dockerfile 標準合規性..."
echo ""

# 查找所有 Dockerfile（排除 node_modules）
dockerfiles=$(find . -name "Dockerfile" -type f ! -path "*/node_modules/*" ! -path "*/.git/*")

issues_found=0
files_checked=0

for dockerfile in $dockerfiles; do
    files_checked=$((files_checked + 1))
    
    # 檢查是否有 USER nodejs
    if grep -q "USER nodejs" "$dockerfile"; then
        echo "📄 檢查: $dockerfile"
        
        has_npm_install=false
        # 檢查是否有 npm install 或 npm ci
        if grep -q "npm \(install\|ci\)" "$dockerfile"; then
            has_npm_install=true
        fi
        
        if [ "$has_npm_install" = true ]; then
            # 檢查是否在 USER nodejs 之前設置了 /home/nodejs/.npm
            if ! grep -B 10 "USER nodejs" "$dockerfile" | grep -q "/home/nodejs/.npm"; then
                echo -e "${RED}❌ 錯誤: 缺少 /home/nodejs/.npm 目錄設置${NC}"
                echo "   位置: $dockerfile"
                echo "   請參考: .docker-templates/NODEJS_USER_SETUP.md"
                echo ""
                issues_found=$((issues_found + 1))
                continue
            fi
            
            # 檢查是否設置了 NPM_CONFIG_CACHE
            if ! grep -A 5 "USER nodejs" "$dockerfile" | grep -q "NPM_CONFIG_CACHE"; then
                echo -e "${YELLOW}⚠️  警告: 建議設置 NPM_CONFIG_CACHE 環境變數${NC}"
                echo "   位置: $dockerfile"
                echo ""
            fi
        fi
        
        echo -e "${GREEN}✅ 通過${NC}"
        echo ""
    fi
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 檢查結果："
echo "   檢查檔案數: $files_checked"
echo "   發現問題數: $issues_found"

if [ $issues_found -eq 0 ]; then
    echo -e "${GREEN}✅ 所有 Dockerfile 符合標準${NC}"
    exit 0
else
    echo -e "${RED}❌ 發現 $issues_found 個不符合標準的 Dockerfile${NC}"
    echo ""
    echo "請執行以下命令查看修復指南："
    echo "  cat .docker-templates/NODEJS_USER_SETUP.md"
    exit 1
fi
