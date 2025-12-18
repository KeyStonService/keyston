#!/bin/bash
# Island AI 代理駕駛快速修復腳本
# 版本: 1.0.0

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 日誌函數
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# 標題
echo -e "${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║   Island AI 代理駕駛修復工具 v1.0                   ║
║   SynergyMesh - Unmanned Island System                    ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# 檢查是否在專案根目錄
if [ ! -f "package.json" ] && [ ! -f "drone-config.yml" ]; then
    log_error "請在專案根目錄執行此腳本"
    exit 1
fi

log_info "開始診斷 Island AI 配置..."
echo ""

# 步驟 1: 檢查 Git 配置
log_step "1/6 檢查 Git 配置"
if command -v git &> /dev/null; then
    GIT_REMOTE=$(git remote get-url origin 2>/dev/null || echo "未設定")
    log_info "Git 遠端: $GIT_REMOTE"
    
    if [[ $GIT_REMOTE == *"github.com"* ]]; then
        REPO_PATH=$(echo "$GIT_REMOTE" | sed -e 's/.*github.com[:/]\(.*\)\.git/\1/' -e 's/.*github.com[:/]\(.*\)/\1/')
        log_success "偵測到 GitHub 倉庫: $REPO_PATH"
    else
        log_warn "這不是 GitHub 倉庫"
    fi
else
    log_error "Git 未安裝"
fi
echo ""

# 步驟 2: 檢查 GitHub CLI
log_step "2/6 檢查 GitHub CLI"
if command -v gh &> /dev/null; then
    log_success "GitHub CLI 已安裝: $(gh --version | head -n1)"
    
    # 檢查登入狀態
    if gh auth status &> /dev/null; then
        log_success "GitHub CLI 已登入"
        GITHUB_USER=$(gh api user -q .login 2>/dev/null || echo "unknown")
        log_info "登入帳戶: $GITHUB_USER"
    else
        log_warn "GitHub CLI 未登入"
        log_info "請執行: gh auth login"
    fi
else
    log_warn "GitHub CLI 未安裝"
    log_info ""
    log_info "安裝方式:"
    
    if command -v apk &> /dev/null; then
        log_info "  Alpine: apk add github-cli"
    elif command -v apt-get &> /dev/null; then
        log_info "  Ubuntu/Debian: sudo apt-get install gh"
    elif command -v brew &> /dev/null; then
        log_info "  macOS: brew install gh"
    else
        log_info "  其他: https://github.com/cli/cli#installation"
    fi
fi
echo ""

# 步驟 3: 檢查配置檔案
log_step "3/6 檢查 Island AI 配置檔案"
CONFIG_FILES=(
    ".github/island-ai-instructions.md"
    ".github/workflows/island-ai-setup-steps.yml"
    "config/drone-config.yml"
)

for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        log_success "✓ $file"
    else
        log_warn "✗ $file 不存在"
    fi
done
echo ""

# 步驟 4: 檢查 Node.js 環境
log_step "4/6 檢查 Node.js 環境"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    log_success "Node.js: $NODE_VERSION"
    
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        log_success "npm: v$NPM_VERSION"
    fi
else
    log_error "Node.js 未安裝"
fi
echo ""

# 步驟 5: 檢查 Python 環境
log_step "5/6 檢查 Python 環境"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    log_success "$PYTHON_VERSION"
else
    log_warn "Python 3 未安裝"
fi
echo ""

# 步驟 6: 檢查無人機腳本
log_step "6/6 檢查無人機系統"
DRONE_SCRIPTS=(
    "config/dev/automation/auto-pilot.js"
    "config/dev/automation/drone-coordinator.py"
)

for script in "${DRONE_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        log_success "✓ $(basename $script)"
    else
        log_warn "✗ $(basename $script) 不存在"
    fi
done
echo ""

# 生成診斷報告
log_info "生成診斷報告..."
REPORT_FILE="island-ai-diagnosis-$(date +%Y%m%d-%H%M%S).txt"

cat > "$REPORT_FILE" << EOF
Island AI 代理駕駛診斷報告
生成時間: $(date)
==========================================

1. 系統資訊
   - 主機名稱: $(hostname)
   - 作業系統: $(uname -s)
   - 核心版本: $(uname -r)

2. Git 配置
   - Git 版本: $(git --version 2>/dev/null || echo "未安裝")
   - 遠端倉庫: $GIT_REMOTE
   - 倉庫路徑: ${REPO_PATH:-未偵測}

3. GitHub CLI
   - 安裝狀態: $(command -v gh &> /dev/null && echo "已安裝" || echo "未安裝")
   - 登入狀態: $(gh auth status &> /dev/null && echo "已登入" || echo "未登入")
   - 登入帳戶: ${GITHUB_USER:-未知}

4. 開發環境
   - Node.js: ${NODE_VERSION:-未安裝}
   - npm: ${NPM_VERSION:-未安裝}
   - Python: ${PYTHON_VERSION:-未安裝}

5. 配置檔案
EOF

for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file" >> "$REPORT_FILE"
    else
        echo "   ✗ $file" >> "$REPORT_FILE"
    fi
done

cat >> "$REPORT_FILE" << EOF

6. 無人機腳本
EOF

for script in "${DRONE_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        echo "   ✓ $script" >> "$REPORT_FILE"
    else
        echo "   ✗ $script" >> "$REPORT_FILE"
    fi
done

log_success "診斷報告已保存: $REPORT_FILE"
echo ""

# 提供修復建議
echo -e "${PURPLE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                    修復建議                               ║${NC}"
echo -e "${PURPLE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}⚠${NC} GitHub CLI 未安裝"
    echo "   修復: 安裝 GitHub CLI"
    echo ""
fi

if ! gh auth status &> /dev/null 2>&1; then
    echo -e "${YELLOW}⚠${NC} GitHub CLI 未登入"
    echo "   修復: 執行 'gh auth login'"
    echo ""
fi

echo -e "${CYAN}📋 接下來的步驟:${NC}"
echo ""
echo "1. 確認 Island AI 訂閱狀態"
echo "   → 訪問 https://github.com/settings/island-ai"
echo ""
echo "2. 授予 Island AI 倉庫訪問權限"
echo "   → 在上述頁面的 'Repository access' 中添加此倉庫"
echo ""
echo "3. 如果未安裝 GitHub CLI，請先安裝並登入"
echo "   → gh auth login"
echo ""
echo "4. 在 VS Code 中重新載入視窗"
echo "   → Ctrl+Shift+P > 'Reload Window'"
echo ""
echo "5. 測試 Island AI 功能"
echo "   → 開啟 Island Shell 並測試對話"
echo ""
echo -e "${GREEN}✅ 完整修復指南請參考:${NC}"
echo "   docs/troubleshooting/github-island-ai-agent-fix.md"
echo ""

# 詢問是否要打開 GitHub CLI 登入
if command -v gh &> /dev/null && ! gh auth status &> /dev/null 2>&1; then
    echo -n "是否現在執行 GitHub CLI 登入? (y/N): "
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        log_info "啟動 GitHub CLI 登入..."
        gh auth login
    fi
fi

echo ""
log_success "診斷完成！"
