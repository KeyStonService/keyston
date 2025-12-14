# SynergyMesh 構建指南 | Build Guide

<div align="center">

**🔨 跨平台構建說明 | Cross-Platform Build Instructions**

</div>

---

## 📋 目錄 | Table of Contents

- [構建環境準備](#構建環境準備)
- [Windows 構建](#windows-構建)
- [macOS 構建](#macos-構建)
- [Linux 構建](#linux-構建)
- [Docker 構建](#docker-構建)
- [統一構建腳本](#統一構建腳本)
- [CI/CD 自動化](#cicd-自動化)
- [故障排除](#故障排除)

---

## 構建環境準備

### 通用依賴

```bash
# 克隆倉庫
git clone https://github.com/SynergyMesh-admin/SynergyMesh.git
cd SynergyMesh

# 安裝基礎工具
python3 --version  # 需要 3.10+
node --version     # 需要 18+
npm --version      # 需要 8+
```

---

## Windows 構建

### 環境準備

**必需工具**:
- Python 3.10+ ([下載](https://www.python.org/downloads/))
- Node.js 18+ ([下載](https://nodejs.org/))
- Visual Studio Build Tools ([下載](https://visualstudio.microsoft.com/downloads/))

**可選工具**（用於完整構建）:
- PyInstaller: `pip install pyinstaller`
- NSIS: [下載](https://nsis.sourceforge.io/Download)
- WiX Toolset: [下載](https://wixtoolset.org/releases/)
- Code Signing Certificate (EV 推薦)

### 構建步驟

```batch
:: 1. 進入 Windows 構建目錄
cd build\windows

:: 2. 設置環境變數
call windows-environment.bat

:: 3. 執行構建
call build-windows.bat

:: 構建產物：
:: - dist\SynergyMesh-Governance.exe (EXE 安裝程式)
:: - SynergyMesh-Governance-1.0.0.msi (MSI 安裝程式)
```

### 代碼簽名（可選）

```powershell
# 使用 PowerShell 執行簽名腳本
.\sign-windows.ps1 -CertificatePath "path\to\cert.pfx"

# 或設置環境變數
$env:CERT_PASSWORD = "your-password"
.\sign-windows.ps1
```

### 構建自定義配置

編輯 `build/windows/windows-config.yaml`:

```yaml
build:
  signing:
    enabled: true
    certificate: path/to/certificate.pfx
    timestamp_server: http://timestamp.digicert.com

installation:
  default_path: "%ProgramFiles%\\SynergyMesh"
  create_shortcuts: true
```

---

## macOS 構建

### 環境準備

**必需工具**:
```bash
# 安裝 Xcode Command Line Tools
xcode-select --install

# 安裝 Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安裝構建工具
brew install python@3.11 node@20 create-dmg
pip3 install pyinstaller dmgbuild
```

**可選工具**（用於完整構建）:
- Apple Developer ID Certificate
- 公證工具（macOS 10.15+）

### 構建步驟

```bash
# 1. 進入 macOS 構建目錄
cd build/macos

# 2. 執行構建
chmod +x build-macos.sh
./build-macos.sh

# 構建產物：
# - SynergyMesh-Governance-1.0.0.dmg (DMG 磁碟映像)
# - SynergyMesh-Governance-1.0.0.pkg (PKG 安裝程式)
```

### 代碼簽名

```bash
# 設置簽名身份
export SIGNING_IDENTITY="Developer ID Application: Your Name"

# 執行簽名
./sign-macos.sh

# 驗證簽名
codesign --verify --deep --strict SynergyMesh-Governance.app
spctl --assess --verbose SynergyMesh-Governance.app
```

### 公證（Notarization）

```bash
# 1. 壓縮應用程式
ditto -c -k --keepParent SynergyMesh-Governance.app SynergyMesh-Governance.zip

# 2. 提交公證
xcrun notarytool submit SynergyMesh-Governance.zip \
  --apple-id "your-email@example.com" \
  --password "app-specific-password" \
  --team-id "TEAM_ID" \
  --wait

# 3. 附加公證票據
xcrun stapler staple SynergyMesh-Governance.app

# 4. 驗證
spctl --assess -vv --type install SynergyMesh-Governance.app
```

### 構建 Homebrew Formula

```bash
# 1. 計算 SHA256
shasum -a 256 SynergyMesh-Governance-1.0.0.tar.gz

# 2. 更新 Formula
# 編輯 build/macos/synergymesh-governance.rb
# 替換 url 和 sha256

# 3. 測試 Formula
brew install --build-from-source ./synergymesh-governance.rb
brew audit synergymesh-governance
```

---

## Linux 構建

### 環境準備

**Debian/Ubuntu**:
```bash
sudo apt update
sudo apt install -y \
  python3 python3-pip python3-dev \
  nodejs npm \
  build-essential \
  fakeroot dpkg-dev \
  rpm \
  fuse libfuse2

pip3 install pyinstaller
```

**RHEL/CentOS/Fedora**:
```bash
sudo yum install -y \
  python3 python3-pip python3-devel \
  nodejs npm \
  gcc gcc-c++ make \
  rpm-build \
  fuse fuse-libs

pip3 install pyinstaller
```

### 構建步驟

```bash
# 1. 進入 Linux 構建目錄
cd build/linux

# 2. 執行完整構建
chmod +x build-linux.sh
./build-linux.sh

# 構建產物：
# - SynergyMesh-Governance-x86_64.AppImage
# - debian/synergymesh-governance_1.0.0_amd64.deb
# - redhat/synergymesh-governance-1.0.0-1.x86_64.rpm
```

### 單獨構建各格式

```bash
# 僅構建 AppImage
./build-appimage.sh

# 僅構建 DEB 包
./build-deb.sh

# 僅構建 RPM 包
./build-rpm.sh
```

### 簽名 Packages

```bash
# 生成 GPG 密鑰（如果沒有）
gpg --full-generate-key

# 簽名 DEB 包
dpkg-sig --sign builder synergymesh-governance_1.0.0_amd64.deb

# 簽名 RPM 包
rpm --addsign synergymesh-governance-1.0.0-1.x86_64.rpm

# 驗證簽名
dpkg-sig --verify synergymesh-governance_1.0.0_amd64.deb
rpm --checksig synergymesh-governance-1.0.0-1.x86_64.rpm
```

---

## Docker 構建

### 構建 Linux 容器

```bash
# 1. 構建映像
docker build \
  -f build/docker/Dockerfile \
  -t synergymesh/governance:1.0.0 \
  -t synergymesh/governance:latest \
  .

# 2. 測試映像
docker run --rm synergymesh/governance:latest synergymesh --version

# 3. 推送到 Docker Hub（需要登錄）
docker login
docker push synergymesh/governance:1.0.0
docker push synergymesh/governance:latest
```

### 構建 Windows 容器

```powershell
# 構建 Windows 容器映像
docker build `
  -f build/docker/Dockerfile.windows `
  -t synergymesh/governance:windows-1.0.0 `
  .

# 測試
docker run --rm synergymesh/governance:windows-1.0.0 synergymesh --version
```

### 使用 Docker Compose

```bash
# 構建所有服務
docker-compose -f build/docker/docker-compose.yml build

# 啟動服務堆疊
docker-compose -f build/docker/docker-compose.yml up -d

# 查看日誌
docker-compose logs -f

# 停止服務
docker-compose down
```

### 多平台構建（Buildx）

```bash
# 創建 builder
docker buildx create --name multiplatform --use

# 構建多平台映像
docker buildx build \
  --platform linux/amd64,linux/arm64,linux/arm/v7 \
  -f build/docker/Dockerfile \
  -t synergymesh/governance:latest \
  --push \
  .
```

---

## 統一構建腳本

### 使用 Python 構建腳本

```bash
# 構建當前平台
python3 build/build.py <platform>

# 平台選項：
# - windows
# - macos
# - linux
# - docker
# - all

# 範例：
python3 build/build.py linux
python3 build/build.py docker --windows-docker
python3 build/build.py all
```

### 使用 Makefile

```bash
# 查看可用目標
make help

# 構建當前平台
make build

# 構建所有格式
make build-all

# 構建 Docker 映像
make docker-build

# 清理構建產物
make clean

# 完整構建流程
make clean build test package
```

---

## CI/CD 自動化

### GitHub Actions

我們提供了完整的 CI/CD 工作流程：

```yaml
.github/workflows/
├── build-windows.yml    # Windows 自動構建
├── build-macos.yml      # macOS 自動構建
├── build-linux.yml      # Linux 自動構建
└── release.yml          # 自動發布
```

### 觸發構建

```bash
# 推送 tag 觸發發布構建
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 推送到主分支觸發 CI
git push origin main
```

### 本地測試 CI

```bash
# 使用 act 在本地運行 GitHub Actions
# 安裝: https://github.com/nektos/act

# 運行 Linux 構建
act -W .github/workflows/build-linux.yml

# 運行所有工作流
act -l
act
```

---

## 故障排除

### Windows

**PyInstaller 失敗**:
```batch
:: 清除快取
rmdir /s /q build dist
pyinstaller --clean build-windows.spec
```

**MSI 構建失敗**:
```
確保 WiX Toolset 已安裝且在 PATH 中
where candle.exe
where light.exe
```

### macOS

**簽名失敗**:
```bash
# 列出可用證書
security find-identity -v -p codesigning

# 刪除過期證書
security delete-identity -c "Your Certificate Name"
```

**公證失敗**:
```bash
# 檢查公證狀態
xcrun notarytool log <submission-id> --apple-id <email>
```

### Linux

**AppImage 構建失敗**:
```bash
# 手動下載 appimagetool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
```

**缺少依賴**:
```bash
# 安裝所有構建依賴
sudo apt build-dep synergymesh-governance
```

### Docker

**映像過大**:
```bash
# 使用 dive 分析映像層
dive synergymesh/governance:latest

# 優化 Dockerfile
# - 使用 multi-stage builds
# - 減少層數
# - 清理快取
```

---

## 📚 相關文檔

- [INSTALL.md](./INSTALL.md) - 安裝指南
- [RELEASE.md](./RELEASE.md) - 發布流程
- [CONTRIBUTING.md](./CONTRIBUTING.md) - 貢獻指南

---

<div align="center">

**構建愉快！Happy Building!**

</div>
