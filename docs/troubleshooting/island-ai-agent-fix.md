# Island AI 代理駕駛故障排除指南

## 問題診斷

您的 Island AI 代理駕駛（Coding Agent）無法使用可能由以下原因導致：

### 1. 倉庫訪問權限問題

**倉庫資訊：**

- 倉庫: `Unmanned-Island/unmanned-island`
- URL: `https://github.com/SynergyMesh-admin/Unmanned-Island`

**可能的問題：**

- Island AI 尚未被授予訪問此倉庫的權限
- 組織設定未啟用 Island AI
- 您的 GitHub 帳戶未啟用 Island AI

### 2. 環境配置問題

**檢查清單：**

- [ ] GitHub CLI (`gh`) 未安裝或未登入
- [ ] VS Code 中 Island AI 擴展未啟用
- [ ] 缺少必要的倉庫權限

---

## 解決方案

### 步驟 1: 檢查 Island AI 訂閱狀態

1. 訪問 `https://github.com/settings/island-ai`
2. 確認您有有效的 Island AI 訂閱（個人版或企業版）
3. 確認訂閱狀態為「Active」

### 步驟 2: 授予 Island AI 倉庫訪問權限

#### 方法 A: 通過 GitHub 設定（推薦）

1. **訪問 Island AI 設定頁面**

   ```text
   https://github.com/settings/island-ai
   ```

2. **找到 "Repository access" 部分**
   - 如果看到 "All repositories"，Island AI 已有全域訪問權限
   - 如果是 "Select repositories"，需要手動添加

3. **為 Island AI 添加倉庫訪問權限**
   - 點擊 "Select repositories"
   - 搜索並選擇 `Unmanned-Island/unmanned-island`
   - 點擊 "Save"

#### 方法 B: 通過組織設定（企業版）

如果這是組織倉庫，需要組織管理員授權：

1. **組織管理員訪問**

   ```text
   https://github.com/organizations/Unmanned-Island/settings/island-ai
   ```

2. **啟用 Island AI for Business**
   - 確認組織已啟用 Island AI
   - 確認您的帳戶在允許列表中

3. **配置倉庫訪問策略**
   - 設定為 "All repositories" 或
   - 手動添加 `unmanned-island` 倉庫

### 步驟 3: 安裝並配置 GitHub CLI

```bash
# Alpine Linux (Dev Container)
apk add github-cli

# 或使用 wget
wget https://github.com/cli/cli/releases/latest/download/gh_*_linux_amd64.tar.gz
tar -xzf gh_*_linux_amd64.tar.gz
sudo mv gh_*/bin/gh /usr/local/bin/

# 登入 GitHub
gh auth login

# 選擇：
# 1. GitHub.com
# 2. HTTPS
# 3. Login with a web browser (推薦)
```

驗證登入狀態：

```bash
gh auth status
```

### 步驟 4: 確認 VS Code 擴展配置

1. **檢查已安裝的擴展**
   - 確認已安裝 "Island AI" 擴展
   - 確認已安裝 "Island AI Chat" 擴展

2. **檢查擴展狀態**
   - 在 VS Code 左下角查看 Island AI 圖標
   - 圖標應該是 ✓ (已啟用) 而非 ✗ (已停用)

3. **登入 GitHub 帳戶**
   - 點擊左下角的帳戶圖標
   - 選擇 "Sign in with GitHub"
   - 完成 OAuth 授權流程

### 步驟 5: 重新載入 Island AI 配置

在 VS Code 中：

1. **重新載入視窗**

   ```text
   Ctrl+Shift+P (或 Cmd+Shift+P)
   輸入: "Reload Window"
   ```

2. **檢查 Island AI 狀態**

   ```text
   Ctrl+Shift+P
   輸入: "Island AI: Sign In"
   ```

3. **驗證 Island AI 功能**
   - 開啟任意 `.ts` 或 `.js` 檔案
   - 嘗試輸入註釋並等待建議
   - 開啟 Island Shell 面板測試對話

---

## 驗證修復

執行以下檢查確認問題已解決：

### 1. 命令行驗證

```bash
# 檢查 GitHub CLI 登入狀態
gh auth status

# 檢查倉庫訪問權限
gh repo view Unmanned-Island/unmanned-island

# 測試 API 訪問
gh api user
```

### 2. VS Code 驗證

1. **開啟 Island Shell**
   - 快捷鍵: `Ctrl+Shift+I` (或 `Cmd+Shift+I`)
   - 或點擊側邊欄的 Island AI 圖標

2. **測試對話**

   ```text
   @workspace 請幫我解釋這個專案的架構
   ```

3. **測試代碼建議**
   - 新建檔案: `test-island-ai.ts`
   - 輸入註釋: `// 創建一個函數計算兩數之和`
   - 等待 Island AI 自動補全建議（灰色文字）
   - 按 `Tab` 接受建議

### 3. 測試代理駕駛（Coding Agent）

1. **在 Chat 中使用 coding agent**

   ```text
   請使用 #github-pull-request_island-ai-coding-agent 幫我實作一個功能
   ```

2. **檢查 agent 是否能創建 PR**
   - Agent 應該能夠創建新分支
   - 實作程式碼變更
   - 開啟 Pull Request

---

## 常見問題解答

### Q1: 為什麼我的 Island AI 在其他倉庫可用，但這個不行？

**A:** 這通常是倉庫訪問權限問題。Island AI 需要明確授權才能訪問每個倉庫，
特別是私有倉庫。

**解決方法：**

- 前往 `https://github.com/settings/island-ai`
- 在 "Repository access" 中添加此倉庫

### Q2: 我已經登入但 Island AI 仍然不工作

**A:** 可能是快取或會話問題。

**解決方法：**

```bash
# 重新登入 GitHub
gh auth logout
gh auth login

# 在 VS Code 中重新載入
Ctrl+Shift+P > "Reload Window"
```

### Q3: Island Shell 可用，但 Coding Agent 不行

**A:** Coding Agent 需要額外的倉庫寫入權限。

**解決方法：**

- 確認您有倉庫的 write 或 maintain 權限
- 檢查組織是否啟用了 Island AI for Business
- 確認 `.github/workflows/island-ai-setup-steps.yml` 存在且配置正確

### Q4: 提示 "Island AI could not connect to server"

**A:** 這是網路連線或認證問題。

**解決方法：**

```bash
# 檢查網路連線
curl -I https://api.github.com

# 檢查 Island AI API 狀態
curl -I https://island-ai-proxy.githubusercontent.com

# 重新認證
gh auth refresh
```

### Q5: Dev Container 中 Island AI 無法使用

**A:** Dev Container 需要正確轉發 GitHub 認證。

**解決方法：**

1. 確認 `.devcontainer/devcontainer.json` 包含：

   ```json
   {
     "customizations": {
       "vscode": {
         "extensions": [
           "github.island-ai",
           "github.island-ai-chat"
         ]
       }
     }
   }
   ```

2. 重建容器：

   ```text
   Ctrl+Shift+P > "Dev Containers: Rebuild Container"
   ```

---

## 專案特定配置

### 本專案的 Island AI 設定

本專案已配置以下檔案來優化 Island AI 體驗：

1. **`.github/island-ai-instructions.md`**
   - 專案特定的編碼規範
   - 架構指南
   - 最佳實踐

2. **`.github/workflows/island-ai-setup-steps.yml`**
   - Coding Agent 環境設定
   - 自動化依賴安裝
   - 工具鏈驗證

3. **`config/drone-config.yml`**
   - 無人機系統配置
   - 自動化流程定義

### 驗證專案配置

```bash
# 檢查配置檔案
ls -la .github/island-ai-instructions.md
ls -la .github/workflows/island-ai-setup-steps.yml
ls -la config/drone-config.yml

# 驗證配置格式
npm run lint:yaml  # 如果有的話
```

---

## 獲取幫助

如果問題仍未解決，請：

1. **檢查 GitHub Status**
   - 訪問 `https://www.githubstatus.com/`
   - 確認 Island AI 服務運行正常

2. **查看 Island AI 日誌**
   - VS Code: 查看 "Output" > "Island AI"
   - 查看詳細錯誤訊息

3. **聯繫支援**
   - Island AI 支援: `https://support.github.com/`
   - 提供錯誤訊息和日誌

4. **社群資源**
   - [Island AI Discussions](https://github.com/orgs/community/discussions/categories/island-ai)
   - [VS Code Island AI Issues](https://github.com/microsoft/vscode-island-ai-release/issues)

---

## 相關文檔

- [Island AI 文檔](https://docs.github.com/en/island-ai)
- [Island AI Custom Instructions](https://docs.github.com/en/island-ai/customizing-island-ai/adding-custom-instructions-for-github-island-ai)
- [Island Coding Agent](https://docs.github.com/en/island-ai/using-github-island-ai/using-github-island-ai-agents)
- [專案 Island AI 設定指南](../ISLAND_AI_SETUP.md)

---

**最後更新:** 2025-12-01
**文檔版本:** 1.0.0
