#!/bin/bash

# 執行與偵錯系統安裝腳本
# Run & Debug System Setup Script

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║     MachineNativeOps 執行與偵錯系統 - 安裝程式              ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 檢查 Python 版本
echo "🔍 檢查 Python 版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python 版本: $python_version"

if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
    echo "❌ 錯誤: 需要 Python 3.8 或更高版本"
    exit 1
fi
echo "✅ Python 版本符合要求"
echo ""

# 建立虛擬環境（可選）
read -p "要建立虛擬環境嗎？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 建立虛擬環境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ 虛擬環境已建立並啟動"
    echo ""
fi

# 安裝依賴
echo "📦 安裝依賴套件..."
pip install --upgrade pip
pip install -r requirements-debug.txt
echo "✅ 依賴套件安裝完成"
echo ""

# 建立必要的目錄
echo "📁 建立目錄結構..."
mkdir -p .vscode
mkdir -p examples/debug-examples
mkdir -p logs
echo "✅ 目錄結構建立完成"
echo ""

# 複製範例配置
echo "📝 設定範例配置..."
if [ ! -f .vscode/launch.json ]; then
    cp examples/debug-examples/launch.json .vscode/launch.json
    echo "✅ launch.json 已複製到 .vscode/"
else
    echo "ℹ️  launch.json 已存在，跳過"
fi
echo ""

# 執行測試
echo "🧪 執行測試..."
python3 examples/debug-examples/demo.py --test-mode 2>/dev/null || true
echo "✅ 測試完成"
echo ""

# 顯示完成訊息
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║     ✅ 安裝完成！                                            ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "下一步："
echo ""
echo "1. 查看文檔："
echo "   cat docs/RUN_DEBUG_QUICKSTART.md"
echo ""
echo "2. 執行示範："
echo "   python3 examples/debug-examples/demo.py"
echo ""
echo "3. 使用命令列工具："
echo "   python3 -m src.core.run-debug.cli --help"
echo ""
echo "4. 啟動互動式 REPL："
echo "   python3 -m src.core.run-debug.cli repl"
echo ""
echo "5. 使用聊天式偵錯："
echo "   python3 -m src.core.run-debug.chat_interface"
echo ""
echo "📚 完整文檔: docs/RUN_DEBUG_SYSTEM.md"
echo ""
echo "🎉 開始使用 MachineNativeOps 執行與偵錯系統！"