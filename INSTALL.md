# SynergyMesh 安裝指南 | Installation Guide

<div align="center">

**🚀 跨平台安裝說明 | Cross-Platform Installation Instructions**

支援 Windows, macOS, Linux 和 Docker | Supporting Windows, macOS, Linux, and
Docker

</div>

---

## 📋 目錄 | Table of Contents

- [系統需求](#系統需求--system-requirements)
- [Windows 安裝](#-windows-安裝)
- [macOS 安裝](#-macos-安裝)
- [Linux 安裝](#-linux-安裝)
- [Docker 安裝](#-docker-安裝)
- [從源碼安裝](#從源碼安裝--install-from-source)
- [驗證安裝](#驗證安裝--verify-installation)
- [故障排除](#故障排除--troubleshooting)

---

## 系統需求 | System Requirements

### 最低配置 | Minimum Requirements

| 組件         | 要求          | Component   | Requirement     |
| ------------ | ------------- | ----------- | --------------- |
| **CPU**      | 2 核心        | **CPU**     | 2 cores         |
| **記憶體**   | 4 GB RAM      | **Memory**  | 4 GB RAM        |
| **儲存空間** | 2 GB 可用空間 | **Storage** | 2 GB free space |
| **作業系統** | 見下方        | **OS**      | See below       |

### 支援的作業系統 | Supported Operating Systems

- **Windows**: Windows 10/11 (64-bit)
- **macOS**: macOS 11.0 (Big Sur) 或更新版本
- **Linux**: Ubuntu 20.04+, Debian 11+, RHEL 8+, CentOS 8+, Fedora 35+

### 軟體依賴 | Software Dependencies

- **Python**: 3.10 或更高版本
- **Node.js**: 18.0 或更高版本
- **npm**: 8.0 或更高版本

---

## 🪟 Windows 安裝

### 方式 1: 使用 EXE 安裝程式（推薦）

1. **下載安裝程式**

   ```
   下載: SynergyMesh-Governance-setup.exe
   ```

2. **執行安裝程式**
   - 雙擊下載的 `.exe` 檔案
   - 按照安裝精靈的指示操作
   - 選擇安裝目錄（預設：`C:\Program Files\SynergyMesh`）

3. **完成安裝**
   - 安裝程式會自動添加到 PATH
   - 桌面會創建快捷方式

### 方式 2: 使用 MSI 安裝程式（企業部署）

```powershell
# 使用管理員權限執行
msiexec /i SynergyMesh-Governance-1.0.0.msi /qn
```

### 方式 3: 手動安裝

```batch
# 1. 解壓縮安裝包
unzip SynergyMesh-Governance-windows.zip

# 2. 進入目錄
cd SynergyMesh-Governance-windows

# 3. 執行安裝腳本（需要管理員權限）
install.bat
```

### 卸載 | Uninstall

```batch
# 執行卸載腳本
"C:\Program Files\SynergyMesh\uninstall.bat"

# 或使用 Windows 設定 > 應用程式 > 解除安裝
```

---

## 🍎 macOS 安裝

### 方式 1: 使用 Homebrew（推薦）

```bash
# 添加 tap
brew tap synergymesh/tap

# 安裝
brew install synergymesh-governance

# 更新
brew upgrade synergymesh-governance
```

### 方式 2: 使用 DMG 安裝程式

1. **下載 DMG**

   ```bash
   # 下載: SynergyMesh-Governance-1.0.0.dmg
   ```

2. **安裝**
   - 雙擊 `.dmg` 檔案
   - 將 `SynergyMesh-Governance.app` 拖拽到 `Applications` 資料夾

3. **首次啟動**

   ```bash
   # 如遇到安全提示，請前往：
   # 系統偏好設定 > 安全性與隱私 > 點擊"仍要打開"
   ```

### 方式 3: 使用 PKG 安裝程式

```bash
# 安裝
sudo installer -pkg SynergyMesh-Governance-1.0.0.pkg -target /

# 驗證
synergymesh --version
```

### 方式 4: 手動安裝

```bash
# 1. 下載並解壓
curl -L https://github.com/SynergyMesh-admin/SynergyMesh/releases/download/v1.0.0/SynergyMesh-Governance-macos.tar.gz | tar xz

# 2. 進入目錄
cd SynergyMesh-Governance-macos

# 3. 執行安裝腳本
sudo ./install-macos.sh
```

### 卸載 | Uninstall

```bash
# 使用 Homebrew
brew uninstall synergymesh-governance

# 或執行卸載腳本
sudo /Applications/SynergyMesh-Governance.app/Contents/Resources/uninstall-macos.sh
```

---

## 🐧 Linux 安裝

### 方式 1: 使用 AppImage（通用，推薦）

```bash
# 1. 下載 AppImage
wget https://github.com/SynergyMesh-admin/SynergyMesh/releases/download/v1.0.0/SynergyMesh-Governance-x86_64.AppImage

# 2. 賦予執行權限
chmod +x SynergyMesh-Governance-x86_64.AppImage

# 3. 執行
./SynergyMesh-Governance-x86_64.AppImage

# 4. （可選）整合到系統
./SynergyMesh-Governance-x86_64.AppImage --appimage-extract
sudo mv squashfs-root /opt/synergymesh
sudo ln -s /opt/synergymesh/AppRun /usr/local/bin/synergymesh
```

### 方式 2: Debian/Ubuntu (DEB)

```bash
# 1. 下載 DEB 包
wget https://github.com/SynergyMesh-admin/SynergyMesh/releases/download/v1.0.0/synergymesh-governance_1.0.0_amd64.deb

# 2. 安裝
sudo apt install ./synergymesh-governance_1.0.0_amd64.deb

# 或使用 dpkg
sudo dpkg -i synergymesh-governance_1.0.0_amd64.deb
sudo apt-get install -f  # 修復依賴
```

### 方式 3: RHEL/CentOS/Fedora (RPM)

```bash
# 1. 下載 RPM 包
wget https://github.com/SynergyMesh-admin/SynergyMesh/releases/download/v1.0.0/synergymesh-governance-1.0.0-1.x86_64.rpm

# 2. 安裝
sudo rpm -i synergymesh-governance-1.0.0-1.x86_64.rpm

# 或使用 yum/dnf
sudo yum install ./synergymesh-governance-1.0.0-1.x86_64.rpm
```

### 方式 4: Snap Store

```bash
# 安裝
sudo snap install synergymesh-governance

# 授予權限
sudo snap connect synergymesh-governance:home
```

### 卸載 | Uninstall

```bash
# Debian/Ubuntu
sudo apt remove synergymesh-governance

# RHEL/CentOS/Fedora
sudo rpm -e synergymesh-governance

# AppImage
sudo rm /opt/synergymesh
sudo rm /usr/local/bin/synergymesh

# Snap
sudo snap remove synergymesh-governance
```

---

## 🐳 Docker 安裝

### 方式 1: Docker Run（快速開始）

```bash
# 拉取映像
docker pull synergymesh/governance:latest

# 運行容器
docker run -d \
  --name synergymesh-governance \
  -p 8000:8000 \
  -v synergymesh-data:/var/lib/synergymesh \
  synergymesh/governance:latest
```

### 方式 2: Docker Compose（完整堆疊，推薦）

```bash
# 1. 下載 docker-compose.yml
wget https://raw.githubusercontent.com/SynergyMesh-admin/SynergyMesh/main/build/docker/docker-compose.yml

# 2. 啟動服務
docker-compose up -d

# 3. 查看日誌
docker-compose logs -f governance

# 4. 停止服務
docker-compose down
```

### 方式 3: 從源碼構建

```bash
# 1. Clone 倉庫
git clone https://github.com/SynergyMesh-admin/SynergyMesh.git
cd SynergyMesh

# 2. 構建映像
docker build -f build/docker/Dockerfile -t synergymesh/governance:custom .

# 3. 運行
docker run -d --name synergymesh synergymesh/governance:custom
```

### Windows 容器

```powershell
# 使用 Windows Server Core
docker pull synergymesh/governance:windows-latest
docker run -d synergymesh/governance:windows-latest
```

---

## 從源碼安裝 | Install from Source

### 前置準備

```bash
# 安裝 Python 3.10+
python3 --version

# 安裝 Node.js 18+
node --version

# 安裝 Git
git --version
```

### 安裝步驟

```bash
# 1. Clone 倉庫
git clone https://github.com/SynergyMesh-admin/SynergyMesh.git
cd SynergyMesh

# 2. 安裝 Python 依賴
pip install -r requirements.txt
pip install -e .

# 3. 安裝 Node.js 依賴
npm install

# 4. 構建
npm run build

# 5. 驗證
synergymesh --version
```

### 開發模式安裝

```bash
# 安裝開發依賴
pip install -e ".[dev]"
npm install --dev

# 運行測試
pytest
npm test
```

---

## 驗證安裝 | Verify Installation

### 檢查版本

```bash
# 查看版本信息
synergymesh --version

# 預期輸出：
# SynergyMesh Governance v1.0.0
```

### 運行健康檢查

```bash
# 執行健康檢查
synergymesh health

# 預期輸出：
# ✓ System: OK
# ✓ Python: 3.11.0
# ✓ Node.js: 20.0.0
# ✓ Dependencies: OK
```

### 查看幫助

```bash
# 查看命令列表
synergymesh --help

# 查看特定命令幫助
synergymesh <command> --help
```

---

## 故障排除 | Troubleshooting

### Windows

**問題：安裝時提示「需要管理員權限」**

```
解決：右鍵點擊安裝程式，選擇「以系統管理員身分執行」
```

**問題：找不到 Python/Node.js**

```
解決：確保 Python 和 Node.js 已添加到 PATH 環境變數
控制台 > 系統 > 進階系統設定 > 環境變數
```

### macOS

**問題：無法打開應用程式（安全限制）**

```bash
# 解決：允許未識別的開發者
sudo spctl --master-disable

# 或為特定應用授權
xattr -d com.apple.quarantine /Applications/SynergyMesh-Governance.app
```

**問題：Homebrew 安裝失敗**

```bash
# 更新 Homebrew
brew update

# 清除快取
brew cleanup
```

### Linux

**問題：AppImage 無法執行**

```bash
# 安裝 FUSE
sudo apt install fuse libfuse2  # Debian/Ubuntu
sudo yum install fuse fuse-libs  # RHEL/CentOS

# 掛載 FUSE
sudo modprobe fuse
```

**問題：缺少依賴**

```bash
# Debian/Ubuntu
sudo apt update
sudo apt install python3 nodejs

# RHEL/CentOS
sudo yum install python3 nodejs
```

### Docker

**問題：容器無法啟動**

```bash
# 查看日誌
docker logs synergymesh-governance

# 檢查資源
docker stats

# 重新創建容器
docker-compose down -v
docker-compose up -d
```

---

## 📞 獲取幫助 | Get Help

- **文檔**: <https://github.com/SynergyMesh-admin/SynergyMesh/tree/main/docs>
- **Issues**: <https://github.com/SynergyMesh-admin/SynergyMesh/issues>
- **Discussions**:
  <https://github.com/SynergyMesh-admin/SynergyMesh/discussions>

---

<div align="center">

**感謝使用 SynergyMesh！**

**Thank you for using SynergyMesh!**

</div>
