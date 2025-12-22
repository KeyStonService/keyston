# Cloudflare + GitHub 整合部署指南

## ⚠️ 重要安全提醒

在部署到生產環境之前，請務必確認以下安全設置：

### 必要的安全配置

1. **GitHub Webhook Secret (必須)**
   - 生產和預備環境**必須**配置 `GITHUB_WEBHOOK_SECRET`
   - 使用強隨機密鑰（至少 32 字節）
   - 所有 webhook 請求必須通過簽名驗證
   - 開發環境可以暫時關閉此驗證，但會記錄警告

2. **CORS 配置**
   - 預設僅允許 `https://machinenativeops.com`
   - 如需其他域名，請在 `index.ts` 的 `CORS_HEADERS` 中明確列出
   - **禁止**在生產環境使用 `Access-Control-Allow-Origin: *`

3. **CSP 標頭**
   - Cloudflare Pages 已設置嚴格的 Content Security Policy
   - 禁止 `unsafe-inline` 和 `unsafe-eval`
   - 如需內聯腳本，請使用 nonce 或 hash

4. **KV Namespace IDs**
   - 部署前必須填寫 `wrangler.toml` 中的所有 namespace IDs
   - CI/CD 會驗證這些值是否已設置
   - 空的 ID 將導致部署失敗

5. **Rate Limiting**
   - 預設：每個 IP 每分鐘 100 次請求
   - 開發環境自動處理未知 IP（使用 User-Agent 做替代識別）
   - 生產環境依賴 Cloudflare 的 `CF-Connecting-IP`

### 環境變數安全檢查清單

- [ ] `CLOUDFLARE_API_TOKEN` 已添加到 GitHub Secrets
- [ ] `CLOUDFLARE_ACCOUNT_ID` 已添加到 GitHub Secrets
- [ ] `GITHUB_WEBHOOK_SECRET` 已設置（生產/預備環境必須）
- [ ] `WORKER_GITHUB_TOKEN` 已設置（如需 GitHub API 存取）
- [ ] 所有 Secrets 使用加密存儲，未在日誌中暴露
- [ ] wrangler.toml 中的 KV/D1/R2 IDs 已填寫

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

### 環境特定配置範例

#### Development 環境

**特點**：
- 允許未簽名的 webhooks（會記錄警告）
- 使用 `*.workers.dev` 子域名
- 較寬鬆的錯誤處理（顯示詳細錯誤訊息）
- 本地 wrangler dev 支援

**配置**：
```toml
[env.development]
name = "machinenativeops-worker-dev"
vars = { ENVIRONMENT = "development" }

[[env.development.kv_namespaces]]
binding = "CACHE"
id = "your-dev-cache-id"

[[env.development.kv_namespaces]]
binding = "SESSIONS"
id = "your-dev-sessions-id"
```

**部署命令**：
```bash
wrangler deploy --env development
```

#### Staging 環境

**特點**：
- **必須**配置 webhook secret（與生產環境相同的安全要求）
- 使用自訂域名 `staging-api.machinenativeops.com`
- 完整的錯誤日誌記錄
- 用於 QA 和整合測試

**配置**：
```toml
[env.staging]
name = "machinenativeops-worker-staging"
routes = [
  { pattern = "staging-api.machinenativeops.com/*", zone_name = "machinenativeops.com" }
]
vars = { ENVIRONMENT = "staging" }

[[env.staging.kv_namespaces]]
binding = "CACHE"
id = "your-staging-cache-id"

[[env.staging.d1_databases]]
binding = "DB"
database_name = "machinenativeops-staging"
database_id = "your-staging-db-id"
```

**必要 Secrets**：
```bash
echo "$GITHUB_WEBHOOK_SECRET" | wrangler secret put GITHUB_WEBHOOK_SECRET --env staging
echo "$GITHUB_TOKEN" | wrangler secret put GITHUB_TOKEN --env staging
```

#### Production 環境

**特點**：
- **強制** webhook 簽名驗證
- 嚴格的 CORS 策略（僅允許 machinenativeops.com）
- 完整的 CSP 防護（無 unsafe-inline）
- Rate limiting 全面啟用
- 完整的日誌和監控

**配置**：
```toml
[env.production]
name = "machinenativeops-worker-prod"
routes = [
  { pattern = "api.machinenativeops.com/*", zone_name = "machinenativeops.com" }
]
vars = { ENVIRONMENT = "production" }

[[env.production.kv_namespaces]]
binding = "CACHE"
id = "production-cache-id"  # ⚠️ 必須填寫

[[env.production.kv_namespaces]]
binding = "SESSIONS"
id = "production-sessions-id"  # ⚠️ 必須填寫

[[env.production.d1_databases]]
binding = "DB"
database_name = "machinenativeops-prod"
database_id = "production-db-id"  # ⚠️ 必須填寫

[[env.production.r2_buckets]]
binding = "ASSETS"
bucket_name = "machinenativeops-assets-prod"
```

**部署前檢查**：
```bash
# 1. 驗證所有 namespace IDs 已填寫
grep 'id = ""' wrangler.toml && echo "❌ 發現空的 ID！" || echo "✅ 所有 IDs 已填寫"

# 2. 確認 secrets 已設置
wrangler secret list --env production

# 3. 部署
wrangler deploy --env production
```

### 環境切換最佳實踐

1. **使用不同的資源**：每個環境使用獨立的 KV/D1/R2 實例
2. **獨立的 GitHub Webhooks**：為每個環境設置不同的 webhook URL
3. **Secrets 隔離**：不要在環境間共享 secrets
4. **分支策略**：
   - `main` → Production
   - `staging` → Staging
   - `develop` → Development
5. **漸進式部署**：Development → Staging → Production

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

## 測試與品質保證

### 當前測試狀態

⚠️ **重要提醒**：目前 Cloudflare Workers 專案**尚未實作完整的測試套件**。

#### 已配置但未實作的測試

`cloudflare/workers/package.json` 中已定義測試腳本：

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest"
  }
}
```

但是：
- ❌ 沒有測試檔案存在於 `cloudflare/workers` 目錄
- ❌ 沒有單元測試覆蓋率
- ❌ 沒有整合測試
- ❌ 沒有 E2E 測試

#### 建議的測試實作優先順序

**高優先級（關鍵安全功能）**：

1. Webhook 簽名驗證測試
2. Rate Limiter Durable Object 測試
3. GitHub API 代理測試
4. KV 錯誤處理測試

**中優先級（功能完整性）**：
5. CORS 標頭測試
6. 路由處理測試
7. 快取行為測試
8. 環境變數配置測試

**低優先級（邊緣情況）**：
9. 錯誤響應格式測試
10. 效能基準測試

#### 臨時驗證方法

在正式測試套件實作之前，請使用：

1. **型別檢查**：
   ```bash
   npm run typecheck
   ```

2. **手動 API 測試**：
   ```bash
   # 健康檢查
   curl https://api.machinenativeops.com/health
   
   # Webhook 測試
   curl -X POST https://api.machinenativeops.com/webhooks/github \
     -H "Content-Type: application/json" \
     -H "X-GitHub-Event: ping" \
     -H "X-Hub-Signature-256: sha256=<計算的簽名>" \
     -d '{"zen": "test"}'
   ```

3. **Wrangler 本地開發**：
   ```bash
   wrangler dev
   ```

4. **CI/CD 煙霧測試**：
   - GitHub Actions 會在部署後執行健康檢查
   - 檢查 workflow run 日誌確認部署成功

### 生產前檢查清單

在部署到生產環境前，請確認：

- [ ] TypeScript 編譯無錯誤 (`npm run typecheck`)
- [ ] 所有環境變數已正確設置
- [ ] Webhook secret 已配置且通過手動驗證
- [ ] Rate limiting 在開發環境測試正常
- [ ] CORS 標頭符合安全要求
- [ ] KV/D1/R2 資源 IDs 已填入 wrangler.toml
- [ ] 手動測試主要 API 端點（health, webhook, proxy）
- [ ] 檢查 Cloudflare Dashboard 中的 Worker 日誌無異常

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
