# Cloudflare + GitHub 整合部署指南

## 概述

本文檔說明如何設置 MachineNativeOps 的 Cloudflare Edge 服務與 GitHub 的完整整合環境。

## 架構圖

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MachineNativeOps Edge Architecture                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐     ┌──────────────────────────────────────────────────┐ │
│  │   GitHub     │     │              Cloudflare Edge                      │ │
│  │  Repository  │────▶│  ┌────────────┐  ┌─────────────┐  ┌───────────┐ │ │
│  │              │     │  │  Workers   │  │    Pages    │  │  Zero     │ │ │
│  │  - Push      │     │  │  (API)     │  │  (Frontend) │  │  Trust    │ │ │
│  │  - PR        │     │  └─────┬──────┘  └──────┬──────┘  └───────────┘ │ │
│  │  - Issues    │     │        │                │                        │ │
│  │  - Actions   │     │        ▼                ▼                        │ │
│  └──────┬───────┘     │  ┌─────────────────────────────────────────────┐ │ │
│         │             │  │              Cloudflare Services             │ │ │
│         │             │  │  ┌────┐  ┌────┐  ┌────┐  ┌──────────────┐   │ │ │
│         ▼             │  │  │ KV │  │ D1 │  │ R2 │  │Durable Objects│   │ │ │
│  ┌──────────────┐     │  │  └────┘  └────┘  └────┘  └──────────────┘   │ │ │
│  │   Webhooks   │────▶│  └─────────────────────────────────────────────┘ │ │
│  │   Handler    │     │                                                    │ │
│  └──────────────┘     └──────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 目錄結構

```
cloudflare/
├── workers/
│   ├── src/
│   │   ├── index.ts              # Worker 主入口
│   │   └── durable-objects/
│   │       └── rate-limiter.ts   # Rate Limiter DO
│   ├── package.json
│   └── tsconfig.json
├── pages/
│   ├── _headers                   # 自訂 HTTP 標頭
│   └── _redirects                 # URL 重定向規則
├── .env.example                   # 環境變數範本
└── wrangler.toml                  # Cloudflare 配置
```

## 設置步驟

### 1. Cloudflare 帳戶設置

#### 1.1 獲取帳戶資訊

1. 登入 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 點擊右上角帳戶名稱 > **Account ID** (複製保存)
3. 前往 **My Profile** > **API Tokens**

#### 1.2 建立 API Token

1. 點擊 **Create Token**
2. 選擇 **Custom token** > **Get started**
3. 設定權限：

| 權限類型 | 資源 | 權限等級 |
|---------|------|---------|
| Account | Cloudflare Workers Scripts | Edit |
| Account | Workers KV Storage | Edit |
| Account | Workers R2 Storage | Edit |
| Account | D1 | Edit |
| Zone | Cloudflare Pages | Edit |
| Zone | DNS | Edit |

4. 點擊 **Continue to summary** > **Create Token**
5. **立即複製 Token** (只顯示一次)

### 2. GitHub Repository 設置

#### 2.1 添加 Repository Secrets

前往 Repository > **Settings** > **Secrets and variables** > **Actions**

添加以下 Secrets：

| Secret 名稱 | 描述 |
|------------|------|
| `CLOUDFLARE_API_TOKEN` | Cloudflare API Token |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare Account ID |
| `CLOUDFLARE_ZONE_ID` | (可選) Zone ID |
| `WORKER_GITHUB_TOKEN` | 用於 Worker 的 GitHub PAT |
| `GITHUB_WEBHOOK_SECRET` | Webhook 驗證密鑰 |

#### 2.2 生成 Webhook Secret

```bash
openssl rand -hex 32
```

### 3. Cloudflare 資源創建

#### 3.1 安裝 Wrangler CLI

```bash
npm install -g wrangler

# 登入 Cloudflare
wrangler login
```

#### 3.2 創建 KV Namespaces

```bash
# 建立快取 namespace
wrangler kv:namespace create "CACHE"
wrangler kv:namespace create "CACHE" --preview

# 建立 session namespace
wrangler kv:namespace create "SESSIONS"
wrangler kv:namespace create "SESSIONS" --preview
```

將輸出的 ID 更新到 `wrangler.toml`。

#### 3.3 創建 D1 Database

```bash
# 建立資料庫
wrangler d1 create machinenativeops-prod
wrangler d1 create machinenativeops-staging
wrangler d1 create machinenativeops-dev
```

#### 3.4 創建 R2 Bucket

```bash
# 建立儲存桶
wrangler r2 bucket create machinenativeops-assets-prod
wrangler r2 bucket create machinenativeops-assets-staging
wrangler r2 bucket create machinenativeops-assets-dev
```

### 4. 部署 Worker

#### 4.1 本地開發

```bash
# 安裝依賴
cd cloudflare/workers
npm install

# 啟動開發伺服器
npm run dev
```

#### 4.2 手動部署

```bash
# 部署到開發環境
wrangler deploy --env development

# 部署到 staging
wrangler deploy --env staging

# 部署到 production
wrangler deploy --env production
```

#### 4.3 設置 Worker Secrets

```bash
# 設置 GitHub Token
echo "ghp_xxxx" | wrangler secret put GITHUB_TOKEN --env production

# 設置 Webhook Secret
echo "your_secret" | wrangler secret put GITHUB_WEBHOOK_SECRET --env production
```

### 5. GitHub Webhook 設置

#### 5.1 創建 Webhook

1. 前往 Repository > **Settings** > **Webhooks**
2. 點擊 **Add webhook**
3. 配置：

| 設定 | 值 |
|-----|-----|
| Payload URL | `https://api.machinenativeops.com/webhooks/github` |
| Content type | `application/json` |
| Secret | 您生成的 webhook secret |
| SSL verification | Enable |

4. 選擇事件：
   - Push events
   - Pull requests
   - Issues
   - Workflow runs
   - Releases

### 6. 自動部署

GitHub Actions 會在以下情況自動觸發部署：

- Push 到 `main` 分支 → Production
- Push 到 `staging` 分支 → Staging
- Pull Request 到 `main` → Preview 部署

### 7. 驗證部署

#### 7.1 健康檢查

```bash
# Production
curl https://api.machinenativeops.com/health

# Staging
curl https://staging-api.machinenativeops.com/health
```

#### 7.2 測試 Webhook

```bash
# 發送測試 webhook
curl -X POST https://api.machinenativeops.com/webhooks/github \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: ping" \
  -d '{"zen": "test"}'
```

## API 端點

### Worker API 端點

| 端點 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康檢查 |
| `/webhooks/github` | POST | GitHub Webhook 處理 |
| `/api/github/*` | ALL | GitHub API 代理 |
| `/assets/*` | GET | R2 資產服務 |
| `/api/*` | ALL | 後端 API 代理 |

### GitHub 事件處理

支援的 GitHub 事件：

| 事件類型 | 處理動作 |
|---------|---------|
| `push` | 觸發 CI/CD，更新快取 |
| `pull_request` | PR 預覽部署 |
| `issues` | Issue 通知處理 |
| `workflow_run` | 工作流狀態同步 |
| `release` | 版本發布自動化 |

## 環境配置

### 環境變數對照表

| 環境變數 | Development | Staging | Production |
|---------|-------------|---------|------------|
| `ENVIRONMENT` | development | staging | production |
| `API_BACKEND_URL` | localhost:8000 | staging-api.* | api.* |
| Worker URL | *.workers.dev | staging-api.* | api.* |

## 監控與日誌

### Cloudflare Dashboard

- **Workers** > **Analytics**: 請求統計、錯誤率
- **Workers** > **Logs**: 即時日誌
- **R2** > **Metrics**: 儲存使用量
- **D1** > **Metrics**: 資料庫查詢統計

### 使用 Wrangler 查看日誌

```bash
# 即時日誌
wrangler tail --env production

# 過濾特定路徑
wrangler tail --env production --search "webhooks"
```

## 故障排除

### 常見問題

#### 1. Webhook 驗證失敗

```
Error: Invalid signature
```

**解決方案**：確認 `GITHUB_WEBHOOK_SECRET` 與 GitHub 設定一致。

#### 2. KV/D1/R2 綁定錯誤

```
Error: Cannot read property 'get' of undefined
```

**解決方案**：確認 `wrangler.toml` 中的 ID 正確，並已創建資源。

#### 3. 部署失敗

```
Error: Authentication error
```

**解決方案**：檢查 `CLOUDFLARE_API_TOKEN` 權限是否正確。

## 安全建議

1. **API Token 權限最小化**：只授予必要權限
2. **Webhook Secret 定期輪換**：建議每 90 天更換
3. **啟用 Cloudflare Zero Trust**：保護管理端點
4. **使用環境變數**：不要硬編碼敏感資訊
5. **啟用 HTTPS**：確保 SSL 模式為 `strict`

## 相關資源

- [Cloudflare Workers 文檔](https://developers.cloudflare.com/workers/)
- [Wrangler CLI 參考](https://developers.cloudflare.com/workers/wrangler/)
- [GitHub Webhooks 文檔](https://docs.github.com/en/webhooks)
- [Cloudflare Zero Trust](https://developers.cloudflare.com/cloudflare-one/)
