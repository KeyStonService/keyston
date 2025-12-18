#!/bin/bash

# 安裝可選的安全和治理工具
# 這些工具不會在初始化時自動安裝，以加快 codespace 啟動速度
# 用戶可以根據需要手動運行此腳本
#
# 安全說明: 此腳本從官方源下載工具
# 建議在生產環境中使用包管理器或驗證校驗和

set -e

echo "🔧 安裝可選的安全和治理工具..."
echo "⚠️  注意: 將從官方 GitHub releases 和官方網站下載工具"
echo ""

# 安裝 GitHub CLI (含 Codespaces CLI)
echo "📦 安裝 GitHub CLI (含 Codespaces CLI)..."
if ! command -v gh &> /dev/null; then
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
    sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
    sudo apt update
    sudo apt install gh -y
    echo "✅ GitHub CLI 安裝完成"
else
    echo "✅ GitHub CLI 已安裝"
fi

# 顯示 Codespaces CLI 可用命令
echo "📦 驗證 Codespaces CLI..."
if gh codespace --help > /dev/null 2>&1; then
    echo "✅ Codespaces CLI 可用"
    echo "   版本: $(gh --version | head -1)"
else
    echo "⚠️ Codespaces CLI 驗證失敗，可能需要 GitHub CLI 認證"
    echo "   請執行 'gh auth login' 進行認證"
fi

# 安裝 Trivy 安全掃描工具
echo "📦 安裝 Trivy..."
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
echo "✅ Trivy 安裝完成"

# 安裝 Cosign 簽名工具
echo "📦 安裝 Cosign..."
curl -LO https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64
sudo mv cosign-linux-amd64 /usr/local/bin/cosign
sudo chmod +x /usr/local/bin/cosign
echo "✅ Cosign 安裝完成"

# 安裝 Syft SBOM 生成工具
echo "📦 安裝 Syft..."
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
echo "✅ Syft 安裝完成"

# 安裝 OPA 策略引擎
echo "📦 安裝 OPA..."
curl -L -o /tmp/opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
sudo mv /tmp/opa /usr/local/bin/opa
sudo chmod 755 /usr/local/bin/opa
echo "✅ OPA 安裝完成"

# 安裝 Conftest 策略測試工具
echo "📦 安裝 Conftest..."
curl -L https://github.com/open-policy-agent/conftest/releases/latest/download/conftest_linux_amd64.tar.gz | \
    sudo tar xz -C /usr/local/bin
echo "✅ Conftest 安裝完成"

echo ""
echo "🎉 所有可選工具安裝完成！"
echo ""
echo "已安裝的工具："
echo "  - GitHub CLI: 含 Codespaces CLI (gh codespace)"
echo "  - Trivy: 容器安全掃描"
echo "  - Cosign: 容器簽名和驗證"
echo "  - Syft: SBOM 生成"
echo "  - OPA: 策略引擎"
echo "  - Conftest: 策略測試"
echo ""
echo "🚀 Codespaces CLI 使用方式："
echo "  gh codespace create     # 建立新的 Codespace"
echo "  gh codespace list       # 列出所有 Codespaces"
echo "  gh codespace ssh        # SSH 連線到 Codespace"
echo "  gh codespace code       # 在 VS Code 中開啟 Codespace"
echo "  gh codespace stop       # 停止 Codespace"
echo "  gh codespace delete     # 刪除 Codespace"
