#!/bin/bash

# SynergyMesh 自動化系統入口點
# 作者: SynergyMesh Team
# 版本: 2.0.0

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 取得腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Docker Compose 命令封裝 (解決 v1/v2 版本差異)
docker_compose() {
    if docker compose version &> /dev/null 2>&1; then
        docker compose "$@"
    else
        docker-compose "$@"
    fi
}

# ASCII Art Logo
show_logo() {
    echo -e "${CYAN}"
    cat << "EOF"
   ╔═══════════════════════════════════════╗
   ║           SynergyMesh v2.0            ║
   ║      自動化開發無人機系統             ║
   ╚═══════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# 檢查先決條件
check_prerequisites() {
    echo -e "${BLUE}🔍 檢查系統先決條件...${NC}"
    
    local missing_deps=()
    
    # 檢查 Docker
    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi
    
    # 檢查 Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
        missing_deps+=("docker-compose")
    fi
    
    # 檢查 Node.js
    if ! command -v node &> /dev/null; then
        missing_deps+=("node")
    fi
    
    # 檢查 Python
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        echo -e "${RED}❌ 缺少以下依賴項: ${missing_deps[*]}${NC}"
        echo -e "${YELLOW}請先安裝缺少的工具後再執行此腳本${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ 所有先決條件已滿足${NC}"
    echo ""
    return 0
}

# 主選單
show_menu() {
    echo -e "${BLUE}🚀 請選擇操作模式:${NC}"
    echo "1. 🤖 自動模式 (AI 智能判斷)"
    echo "2. 🎯 快速啟動 (預設環境)"
    echo "3. ⚙️  自訂配置 (手動選擇)"
    echo "4. 📊 系統診斷 (環境檢查)"
    echo "5. 🔄 版本遷移 (v1 ↔ v2)"
    echo "6. 🛠️  開發工具箱"
    echo "7. 🐍 v1-python-drones (Python 無人機)"
    echo "8. 🏝️  v2-multi-islands (多語言無人島)"
    echo "0. ❌ 退出"
    echo ""
    read -p "請輸入選項 (0-8): " choice
}

# 建立預設配置
create_default_config() {
    echo -e "${BLUE}📝 建立預設配置...${NC}"
    
    if [ ! -f "drone-config.yml" ]; then
        echo -e "${YELLOW}⚠️  drone-config.yml 不存在，請確認檔案已建立${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ 預設配置已就緒${NC}"
}

# 自動模式 - AI 智能判斷
auto_mode() {
    echo -e "${GREEN}🤖 啟動自動模式...${NC}"
    
    # 檢查協調器腳本是否存在
    if [ -f "config/dev/automation/drone-coordinator.py" ]; then
        # 嘗試使用 Python 3
        local python_cmd
        if command -v python3 &> /dev/null; then
            python_cmd="python3"
        else
            python_cmd="python"
        fi
        
        # 啟動智能分析
        $python_cmd config/dev/automation/drone-coordinator.py --mode=auto
        
        # 根據分析結果自動配置
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ 自動配置完成！${NC}"
            start_devcontainer
        else
            echo -e "${RED}❌ 自動配置失敗${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  協調器腳本不存在，執行快速啟動...${NC}"
        quick_start
    fi
}

# 快速啟動
quick_start() {
    echo -e "${YELLOW}🎯 快速啟動模式...${NC}"
    
    # 檢查是否已有配置
    if [ -f "drone-config.yml" ]; then
        echo "發現現有配置，使用現有設定..."
        start_devcontainer
    else
        echo "建立預設配置..."
        create_default_config
        start_devcontainer
    fi
}

# 啟動開發容器
start_devcontainer() {
    echo -e "${CYAN}🐳 啟動開發容器環境...${NC}"
    
    cd config/dev
    
    # 執行初始化腳本
    if [ -f "setup.sh" ]; then
        chmod +x setup.sh
        ./setup.sh
    fi
    
    # 啟動 Docker Compose
    docker_compose up -d
    
    cd ..
    
    echo -e "${GREEN}🎉 系統已就緒！${NC}"
    echo -e "${BLUE}📝 開發環境: http://localhost:8080${NC}"
    echo -e "${BLUE}📊 監控面板: http://localhost:9090${NC}"
}

# 自訂配置
custom_config() {
    echo -e "${PURPLE}⚙️  自訂配置模式${NC}"
    echo ""
    echo "請選擇環境:"
    echo "1. development (開發環境)"
    echo "2. staging (測試環境)"
    echo "3. production (生產環境)"
    echo ""
    read -p "請輸入選項 (1-3): " env_choice
    
    local env_file=""
    case $env_choice in
        1) env_file="config/dev/environments/development.env" ;;
        2) env_file="config/dev/environments/staging.env" ;;
        3) env_file="config/dev/environments/production.env" ;;
        *)
            echo -e "${RED}無效選項${NC}"
            return 1
            ;;
    esac
    
    if [ -f "$env_file" ]; then
        echo -e "${GREEN}載入環境配置: $env_file${NC}"
        # shellcheck source=/dev/null
        source "$env_file"
        start_devcontainer
    else
        echo -e "${RED}環境配置檔案不存在: $env_file${NC}"
        return 1
    fi
}

# 系統診斷
system_diagnosis() {
    echo -e "${BLUE}📊 系統診斷中...${NC}"
    echo ""
    
    echo -e "${CYAN}🔧 系統資訊:${NC}"
    echo "  作業系統: $(uname -s)"
    echo "  核心版本: $(uname -r)"
    echo "  架構: $(uname -m)"
    echo ""
    
    echo -e "${CYAN}🐳 Docker 資訊:${NC}"
    if command -v docker &> /dev/null; then
        echo "  Docker 版本: $(docker --version 2>/dev/null || echo '未安裝')"
        if docker compose version &> /dev/null 2>&1; then
            echo "  Docker Compose 版本: $(docker compose version 2>/dev/null || echo '未知')"
        elif command -v docker-compose &> /dev/null; then
            echo "  Docker Compose 版本: $(docker-compose --version 2>/dev/null || echo '未知')"
        fi
    else
        echo "  Docker: 未安裝"
    fi
    echo ""
    
    echo -e "${CYAN}📦 Node.js 資訊:${NC}"
    if command -v node &> /dev/null; then
        echo "  Node.js 版本: $(node --version 2>/dev/null || echo '未知')"
        echo "  npm 版本: $(npm --version 2>/dev/null || echo '未知')"
    else
        echo "  Node.js: 未安裝"
    fi
    echo ""
    
    echo -e "${CYAN}🐍 Python 資訊:${NC}"
    if command -v python3 &> /dev/null; then
        echo "  Python 版本: $(python3 --version 2>/dev/null || echo '未知')"
    elif command -v python &> /dev/null; then
        echo "  Python 版本: $(python --version 2>/dev/null || echo '未知')"
    else
        echo "  Python: 未安裝"
    fi
    echo ""
    
    echo -e "${CYAN}📁 專案結構:${NC}"
    echo "  config/dev: $([ -d 'config/dev' ] && echo '✅' || echo '❌')"
    echo "  drone-config.yml: $([ -f 'drone-config.yml' ] && echo '✅' || echo '❌')"
    echo "  auto-scaffold.json: $([ -f 'auto-scaffold.json' ] && echo '✅' || echo '❌')"
    echo ""
    
    echo -e "${GREEN}✅ 系統診斷完成${NC}"
}

# 版本遷移
version_migration() {
    echo -e "${PURPLE}🔄 版本遷移工具${NC}"
    echo ""
    echo "可用的遷移選項:"
    echo "1. v1 → v2 (Python 無人機 → 多語言島嶼)"
    echo "2. v2 → v1 (多語言島嶼 → Python 無人機)"
    echo "3. 檢查遷移狀態"
    echo "4. 乾跑模式 (不實際執行)"
    echo "5. 返回主選單"
    echo ""
    read -p "請輸入選項 (1-5): " migration_choice
    
    local python_cmd
    if command -v python3 &> /dev/null; then
        python_cmd="python3"
    else
        python_cmd="python"
    fi
    
    case $migration_choice in
        1)
            echo -e "${BLUE}執行 v1 → v2 遷移...${NC}"
            if [ -f "migration/scripts/v1_to_v2.py" ]; then
                $python_cmd migration/scripts/v1_to_v2.py
            elif [ -f "migration/migrator.py" ]; then
                $python_cmd -m migration.migrator --direction=v1-to-v2
            else
                echo -e "${YELLOW}遷移腳本不存在${NC}"
            fi
            ;;
        2)
            echo -e "${BLUE}執行 v2 → v1 遷移...${NC}"
            if [ -f "migration/scripts/v2_to_v1.py" ]; then
                $python_cmd migration/scripts/v2_to_v1.py
            elif [ -f "migration/migrator.py" ]; then
                $python_cmd -m migration.migrator --direction=v2-to-v1
            else
                echo -e "${YELLOW}遷移腳本不存在${NC}"
            fi
            ;;
        3)
            echo -e "${BLUE}檢查遷移狀態...${NC}"
            if [ -f "migration/migrator.py" ]; then
                $python_cmd -m migration.migrator --direction=v1-to-v2 --check-only
            else
                echo -e "${YELLOW}遷移工具不存在${NC}"
            fi
            ;;
        4)
            echo -e "${BLUE}乾跑模式 (v1 → v2)...${NC}"
            if [ -f "migration/migrator.py" ]; then
                $python_cmd -m migration.migrator --direction=v1-to-v2 --dry-run
            else
                echo -e "${YELLOW}遷移工具不存在${NC}"
            fi
            ;;
        5)
            return 0
            ;;
        *)
            echo -e "${RED}無效選項${NC}"
            ;;
    esac
}

# 開發工具箱
dev_toolkit() {
    echo -e "${CYAN}🛠️  開發工具箱${NC}"
    echo ""
    echo "可用的工具:"
    echo "1. 🧹 清理暫存檔案"
    echo "2. 📦 重新安裝依賴"
    echo "3. 🔨 重建 Docker 映像"
    echo "4. 📊 查看容器日誌"
    echo "5. 🔌 重啟所有服務"
    echo "6. 返回主選單"
    echo ""
    read -p "請輸入選項 (1-6): " tool_choice
    
    case $tool_choice in
        1)
            echo -e "${BLUE}清理暫存檔案...${NC}"
            rm -rf node_modules/.cache tmp/ dist/ coverage/ 2>/dev/null || true
            echo -e "${GREEN}✅ 清理完成${NC}"
            ;;
        2)
            echo -e "${BLUE}重新安裝依賴...${NC}"
            npm ci 2>/dev/null || npm install
            echo -e "${GREEN}✅ 依賴安裝完成${NC}"
            ;;
        3)
            echo -e "${BLUE}重建 Docker 映像...${NC}"
            cd config/dev
            docker_compose build --no-cache
            cd ..
            echo -e "${GREEN}✅ 重建完成${NC}"
            ;;
        4)
            echo -e "${BLUE}顯示容器日誌...${NC}"
            cd config/dev
            docker_compose logs --tail=100
            cd ..
            ;;
        5)
            echo -e "${BLUE}重啟所有服務...${NC}"
            cd config/dev
            docker_compose restart
            cd ..
            echo -e "${GREEN}✅ 重啟完成${NC}"
            ;;
        6)
            return 0
            ;;
        *)
            echo -e "${RED}無效選項${NC}"
            ;;
    esac
}

# v1-python-drones 模式
v1_python_drones_mode() {
    echo -e "${PURPLE}🐍 v1-python-drones - Python 無人機系統${NC}"
    echo ""
    echo "可用的選項:"
    echo "1. 🤖 自動模式 (執行所有無人機)"
    echo "2. 📡 協調器無人機"
    echo "3. ✈️  自動駕駛無人機"
    echo "4. 🚢 部署無人機"
    echo "5. 返回主選單"
    echo ""
    read -p "請輸入選項 (1-5): " v1_choice
    
    local python_cmd
    if command -v python3 &> /dev/null; then
        python_cmd="python3"
    else
        python_cmd="python"
    fi
    
    case $v1_choice in
        1)
            echo -e "${BLUE}執行 v1-python-drones 自動模式...${NC}"
            $python_cmd v1-python-drones/main.py --mode=auto
            ;;
        2)
            echo -e "${BLUE}執行協調器無人機...${NC}"
            $python_cmd v1-python-drones/main.py --drone=coordinator
            ;;
        3)
            echo -e "${BLUE}執行自動駕駛無人機...${NC}"
            $python_cmd v1-python-drones/main.py --drone=autopilot
            ;;
        4)
            echo -e "${BLUE}執行部署無人機...${NC}"
            $python_cmd v1-python-drones/main.py --drone=deployment
            ;;
        5)
            return 0
            ;;
        *)
            echo -e "${RED}無效選項${NC}"
            ;;
    esac
}

# v2-multi-islands 模式
v2_multi_islands_mode() {
    echo -e "${CYAN}🏝️  v2-multi-islands - 多語言自動化無人島系統${NC}"
    echo ""
    echo "可用的選項:"
    echo "1. 🌊 自動模式 (執行協調器和主要島嶼)"
    echo "2. 🦀 Rust 性能核心島"
    echo "3. 🌊 Go 雲原生服務島"
    echo "4. ⚡ TypeScript 全棧開發島"
    echo "5. 🐍 Python AI 數據島"
    echo "6. ☕ Java 企業服務島"
    echo "7. 🏝️  執行所有島嶼"
    echo "8. 返回主選單"
    echo ""
    read -p "請輸入選項 (1-8): " v2_choice
    
    local python_cmd
    if command -v python3 &> /dev/null; then
        python_cmd="python3"
    else
        python_cmd="python"
    fi
    
    case $v2_choice in
        1)
            echo -e "${BLUE}執行 v2-multi-islands 自動模式...${NC}"
            $python_cmd v2-multi-islands/main.py --mode=auto
            ;;
        2)
            echo -e "${BLUE}執行 Rust 性能核心島...${NC}"
            $python_cmd v2-multi-islands/main.py --island=rust
            ;;
        3)
            echo -e "${BLUE}執行 Go 雲原生服務島...${NC}"
            $python_cmd v2-multi-islands/main.py --island=go
            ;;
        4)
            echo -e "${BLUE}執行 TypeScript 全棧開發島...${NC}"
            $python_cmd v2-multi-islands/main.py --island=typescript
            ;;
        5)
            echo -e "${BLUE}執行 Python AI 數據島...${NC}"
            $python_cmd v2-multi-islands/main.py --island=python
            ;;
        6)
            echo -e "${BLUE}執行 Java 企業服務島...${NC}"
            $python_cmd v2-multi-islands/main.py --island=java
            ;;
        7)
            echo -e "${BLUE}執行所有島嶼...${NC}"
            $python_cmd v2-multi-islands/main.py --all
            ;;
        8)
            return 0
            ;;
        *)
            echo -e "${RED}無效選項${NC}"
            ;;
    esac
}

# 主程式邏輯
main() {
    show_logo
    
    # 環境檢查
    if ! check_prerequisites; then
        exit 1
    fi
    
    while true; do
        show_menu
        
        case $choice in
            1) auto_mode ;;
            2) quick_start ;;
            3) custom_config ;;
            4) system_diagnosis ;;
            5) version_migration ;;
            6) dev_toolkit ;;
            7) v1_python_drones_mode ;;
            8) v2_multi_islands_mode ;;
            0) 
                echo -e "${GREEN}感謝使用 SynergyMesh! 👋${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}無效選項，請重新選擇${NC}"
                ;;
        esac
        
        echo ""
        read -p "按 Enter 返回主選單..."
        clear
        show_logo
    done
}

# 執行主程式
main "$@"
