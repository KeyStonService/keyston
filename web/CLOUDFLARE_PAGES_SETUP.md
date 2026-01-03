# Cloudflare Pages 部署指南

## 概述

本文檔說明如何為 MachineNativeOps 設置和部署 Cloudflare Pages。

## 📁 專案結構

```
machine-native-ops/
├── web/                          # Cloudflare Pages 根目錄
│   ├── dist/                     # 建置輸出 (自動生成)
│   ├── public/                   # 靜態資源
│   │   ├── _headers              # 自訂 HTTP 標頭
│   │   └── _redirects            # URL 重定向規則
│   ├── src/                      # 源代碼
│   │   ├── main.js              # JavaScript 入口點
│   │   └── style.css            # 樣式表
│   ├── index.html               # HTML 入口點
│   ├── package.json             # 專案依賴
│   ├── vite.config.js           # Vite 配置
│   ├── wrangler.toml            # Cloudflare Pages 配置
│   ├── .gitignore               # Git 忽略規則
│   └── README.md                # 專案說明
```

## 🚀 部署配置

### Git 存放庫設定

1. **存放庫**: `MachineNativeOps/machine-native-ops`
2. **生產分支**: `main`
3. **自動部署**: 已啟用

### 組建配置

| 設定項目 | 值 |
|---------|-----|
| 組建命令 | `npm run build` |
| 組建輸出目錄 | `dist` |
| 根目錄 | `web` |
| Node.js 版本 | 18.x 或更高 |

### 組建設定

- **組建註解**: 已啟用
- **組建快取**: 已啟用
- **組建系統版本**: Version 3
- **組建監看式路徑**: `*` (包含所有檔案)

### 分支控制

- **生產分支**: `main`
- **自動部署**: 所有分支推送時自動部署
  - `main` 分支 → 生產環境
  - 其他分支 → 預覽環境

## ⚙️ 執行階段配置

### Placement
- **模式**: 預設 (Smart Placement)

### 相容性設定
- **相容性日期**: 2025-12-24
- **相容性旗標**: 未定義

## 🔧 環境變數和祕密

在 Cloudflare Pages 控制台中設定:

1. 前往專案設定 → **Environment variables**
2. 新增變數:
   - 一般變數: 用於配置設定
   - 祕密變數: 用於敏感資料 (API 金鑰等)

範例:
```
API_URL=https://api.machinenativeops.com
ENVIRONMENT=production
```

## 🔗 繫結 (Bindings)

在 Cloudflare Pages 控制台中配置繫結以存取資源:

### 可用的繫結類型

1. **KV Namespaces**: 鍵值儲存
2. **D1 Databases**: SQL 資料庫
3. **R2 Buckets**: 物件儲存
4. **Durable Objects**: 狀態協調
5. **Workers AI**: AI/ML 功能

### 配置範例

在專案設定 → **Bindings** 中新增:
```
KV Namespace: CACHE
D1 Database: DB
R2 Bucket: ASSETS
```

## 📊 部署流程

### 自動部署

1. **推送程式碼到 GitHub**
   ```bash
   git add .
   git commit -m "Update web application"
   git push origin main
   ```

2. **Cloudflare Pages 自動觸發**
   - 檢測到推送事件
   - 執行組建命令
   - 部署到對應環境

3. **查看部署狀態**
   - 登入 Cloudflare Dashboard
   - 前往 Pages 專案
   - 查看部署日誌和狀態

### 手動部署

使用 Wrangler CLI:

```bash
cd web
npm run build
wrangler pages deploy dist --project-name=machine-native-ops
```

## 🛠️ 本地開發

### 安裝依賴

```bash
cd web
npm install
```

### 開發伺服器

```bash
npm run dev
```

訪問 `http://localhost:3000` 查看應用。

### 建置專案

```bash
npm run build
```

輸出目錄: `dist/`

### 預覽建置

```bash
npm run preview
```

## 📝 部署勾點 (Deployment Hooks)

目前未定義部署勾點。若需要在部署時執行自訂操作，可在 Cloudflare Pages 控制台中配置。

## 🔐 存取原則

在 Cloudflare Pages 控制台中配置存取原則:

1. 前往專案設定 → **Access policies**
2. 設定存取規則:
   - 公開存取
   - 需要驗證
   - IP 白名單

## 📋 Pages Functions

### 新增伺服器端邏輯

1. 建立 `functions/` 目錄:
   ```bash
   mkdir -p web/functions/api
   ```

2. 新增函數檔案:
   ```javascript
   // web/functions/api/hello.js
   export async function onRequest(context) {
     return new Response(JSON.stringify({
       message: 'Hello from Cloudflare Pages Functions!'
     }), {
       headers: { 'Content-Type': 'application/json' }
     });
   }
   ```

3. 訪問: `https://your-domain.pages.dev/api/hello`

### CPU 時間限制

- **預設**: 無限制 (Pages Functions 計費方案)
- 可在控制台中配置限制

## 🔄 通知設定

在 Cloudflare Pages 控制台中新增通知:

1. 前往專案設定 → **Notifications**
2. 選擇通知類型:
   - 部署成功/失敗
   - 建置錯誤
   - 效能警告

3. 配置通知管道:
   - Email
   - Webhook
   - Slack

## 🗑️ 專案管理

### 永久刪除專案

⚠️ **警告**: 此操作不可逆！

刪除將移除:
- 所有部署
- 所有資產
- 所有 Functions
- 所有配置

在 Cloudflare Pages 控制台中:
1. 前往專案設定
2. 滾動到底部
3. 點擊 "Delete project"
4. 確認刪除

## 📚 相關資源

- [Cloudflare Pages 官方文檔](https://developers.cloudflare.com/pages/)
- [Vite 官方文檔](https://vitejs.dev/)
- [Wrangler CLI 文檔](https://developers.cloudflare.com/workers/wrangler/)
- [專案 README](../README.md)

## 🐛 疑難排解

### 建置失敗

1. 檢查 `package.json` 中的依賴版本
2. 確認 Node.js 版本相容性
3. 查看建置日誌中的錯誤訊息

### 部署失敗

1. 驗證 Git 存放庫權限
2. 檢查建置輸出目錄是否正確
3. 確認分支配置

### 執行階段錯誤

1. 檢查環境變數是否正確設定
2. 驗證繫結配置
3. 查看 Functions 日誌

## 📞 支援

如有問題或需要協助，請在主存放庫中開啟 Issue。
