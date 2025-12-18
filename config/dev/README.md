# Devcontainer 開發環境配置

## 概述

此目錄包含 GitHub Codespaces 和 VS Code Remote Containers 的開發環境配置。配置已經過優化，以防止在 93% 處卡住的問題。

## 快速開始

### 使用 GitHub Codespaces

1. 在 GitHub 上點擊 "Code" > "Create codespace on main"
2. 等待環境初始化（約 2-3 分鐘）
   - ✅ 自動安裝所有項目依賴
   - ✅ 自動配置開發環境
   - ✅ 自動啟動開發伺服器
3. 開發服務器會自動啟動在 `http://localhost:3000`
4. 🎉 **完全自動化！登入後即可開始開發**

### 使用 VS Code Remote Containers

1. 安裝 VS Code 和 "Remote - Containers" 擴展
2. 打開項目文件夾
3. 點擊左下角綠色按鈕，選擇 "Reopen in Container"
4. 等待容器構建和初始化

## 🤖 完全自動化流程

```
登入程式碼空間
    ↓
[1] 容器創建 (postCreateCommand)
    ├── 執行 setup.sh
    ├── ✅ 自動驗證工具鏈
    ├── ✅ 自動創建目錄結構
    ├── ✅ 自動配置環境變數
    ├── ✅ 自動安裝 npm 依賴
    └── ⏱️  約 1-2 分鐘
    ↓
[2] 容器啟動 (postStartCommand)
    ├── 執行 start-dev-server.sh
    ├── ✅ 檢查依賴完整性
    ├── ✅ 自動啟動開發伺服器
    └── ⏱️  約 5-10 秒
    ↓
[3] 🎉 環境就緒！
    ├── 開發伺服器運行在 http://localhost:3000
    ├── 可以立即開始編碼
    └── 所有工具已配置完成
```

**關鍵特性：**

- ✅ **零手動配置** - 所有步驟自動執行
- ✅ **容錯機制** - 自動重試和降級
- ✅ **進度可見** - 每個步驟都有清晰的輸出
- ✅ **快速啟動** - 優化後僅需 2-3 分鐘

## 優化說明

### 為什麼會卡在 93%？

之前的配置在初始化時執行了過多的操作：

- 安裝過多的安全工具（Trivy, Cosign, Syft, OPA, Conftest）
- 在 setup.sh 中執行 `npm run build`
- 全局安裝多個 npm 包
- 配置 Git hooks 和其他非必需設置

### 我們做了什麼？

**1. 簡化 setup.sh**

- 只驗證核心工具（node, npm）
- 優化的 npm 安裝流程：
  ```bash
  npm ci --prefer-offline --no-audit --loglevel=error
  ```
- 移除了構建步驟（用戶可以手動運行 `npm run build`）
- 移除了全局 npm 包安裝

**2. 精簡 Dockerfile**

- 只安裝核心工具：kubectl, helm, Python 依賴
- 移除了 5 個安全工具的自動安裝
- 減少了鏡像構建時間約 50%

**3. 可選工具安裝**

- 創建了 `install-optional-tools.sh` 腳本
- 用戶可以按需安裝額外的工具

## 核心工具 vs 可選工具

### 自動安裝的核心工具

這些工具會在初始化時自動安裝：

- ✅ Node.js 18
- ✅ npm
- ✅ kubectl
- ✅ Helm
- ✅ Python 3 + pip
- ✅ 基礎系統工具（jq, curl, wget, git）

### 可選工具（按需安裝）

這些工具可以通過運行 `bash .devcontainer/install-optional-tools.sh` 來安裝：

- ⚙️ Trivy - 容器安全掃描
- ⚙️ Cosign - 容器簽名和驗證
- ⚙️ Syft - SBOM 生成工具
- ⚙️ OPA - 策略引擎
- ⚙️ Conftest - 策略測試工具

### 如何安裝可選工具

```bash
# 在 codespace 或容器內執行
bash .devcontainer/install-optional-tools.sh
```

這將安裝所有可選的安全和治理工具。

## 常見問題

### Q: 為什麼 npm 安裝速度變快了？

A: 我們使用了以下優化：

- `--prefer-offline`: 優先使用本地緩存
- `--no-audit`: 跳過安全審計（開發環境）
- `--loglevel=error`: 減少日誌輸出
- 配置了更長的超時和重試次數

### Q: 我需要所有的安全工具嗎？

A: 不一定。大多數日常開發不需要這些工具。只有在以下情況下需要：

- 執行安全掃描（Trivy）
- 生成 SBOM（Syft）
- 驗證容器簽名（Cosign）
- 測試策略（OPA, Conftest）

### Q: 自動化流程是如何工作的？

A: 當你登入程式碼空間時，會自動執行以下步驟：

1. **postCreateCommand** (容器創建時)
   - 執行 `setup.sh` 安裝所有依賴
   - 配置環境變數
   - 創建必要的目錄

2. **postStartCommand** (容器啟動時)
   - 執行 `start-dev-server.sh` 自動啟動開發伺服器
   - 檢查並確保依賴已安裝
   - 在背景運行開發伺服器

3. **完全自動化**
   - 無需手動執行任何命令
   - 登入後環境已就緒
   - 開發伺服器自動運行

### Q: 如何手動構建項目？

A: 運行以下命令：

```bash
npm run build
```

### Q: 初始化需要多長時間？

A:

- **之前**: 5-8 分鐘（常常卡在 93%）
- **現在**: 2-3 分鐘（順利完成）

## 端口映射

開發環境會轉發以下端口：

| 端口 | 服務            | 說明                    |
| ---- | --------------- | ----------------------- |
| 3000 | Web Application | 主應用程序（自動預覽）  |
| 8080 | API Gateway     | API 網關（通知）        |
| 9090 | Monitoring      | Prometheus 監控（通知） |

## 開發工作流

### 1. 啟動開發

容器啟動後，開發服務器會自動運行：

```bash
# 自動執行：npm run dev
```

### 2. 構建項目

```bash
npm run build
```

### 3. 運行測試

```bash
npm run test
```

### 4. 檢查代碼質量

```bash
npm run lint
npm run type-check
```

## 文件結構

```
.devcontainer/
├── devcontainer.json           # VS Code 配置
├── Dockerfile                  # 開發環境鏡像（已優化）
├── docker-compose.dev.yml      # 多容器編排
├── setup.sh                    # 初始化腳本（已優化）
├── install-optional-tools.sh   # 可選工具安裝
├── requirements.txt            # Python 依賴
├── prometheus.yml              # 監控配置
├── KB.md                       # 詳細知識庫文檔
└── README.md                   # 本文件
```

## 故障排除

### 問題：仍然在初始化時卡住

**解決方案:**

1. 檢查網絡連接
2. 嘗試重新創建 codespace
3. 查看 VS Code 的輸出面板獲取詳細錯誤

### 問題：npm install 失敗

**解決方案:**

```bash
# 清理並重新安裝
rm -rf node_modules package-lock.json
npm install
```

### 問題：需要安裝額外工具

**解決方案:**

```bash
# 安裝所有可選工具
bash .devcontainer/install-optional-tools.sh

# 或單獨安裝特定工具
sudo apt-get install <tool-name>
```

## 進一步閱讀

- [KB.md](./KB.md) - 詳細的技術文檔和配置說明
- [VS Code Remote Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [GitHub Codespaces 文檔](https://docs.github.com/en/codespaces)

## 貢獻

如果你發現可以進一步優化配置，歡迎提交 PR！請確保：

1. 測試你的更改不會導致初始化超時
2. 更新相關文檔（README.md 和 KB.md）
3. 說明優化的原因和效果

---

**注意**: 這些優化專門針對解決 93% 卡住的問題。如果你遇到其他問題，請查看 [KB.md](./KB.md) 或提交 issue。
