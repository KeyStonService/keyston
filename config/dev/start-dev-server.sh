#!/bin/bash

# Auto-start development server after codespace is ready
# This script runs automatically when the container starts

echo "🚀 自動啟動開發伺服器..."

# 等待一小段時間確保所有服務就緒
sleep 2

# 檢查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "⚠️  node_modules 不存在，正在安裝依賴..."
    npm install --prefer-offline --no-audit
fi

# 檢查是否已有開發伺服器在運行
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ 開發伺服器已在運行 (端口 3000)"
else
    echo "📦 啟動開發伺服器..."
    echo "🌐 應用將在 http://localhost:3000 可用"
    echo ""
    
    # 確保日誌目錄存在
    mkdir -p logs
    
    # 在背景啟動開發伺服器，並將輸出記錄到日誌文件
    npm run dev 2>&1 | tee logs/dev-server.log &
    
    echo "✅ 開發伺服器已啟動（進程 ID: $!）"
    echo "📋 查看日誌: tail -f logs/dev-server.log"
fi

echo ""
