# Integration Scripts / 整合腳本

本目錄包含與第三方服務整合的腳本，用於擴展 GHAS 的通知和工單管理功能。

## 可用整合

### 1. Slack Webhook Integration

**文件**: `slack-webhook.sh`

**用途**: 發送安全告警到 Slack 頻道

**環境變數**:
- `SLACK_WEBHOOK_URL` (必需): Slack incoming webhook URL

**使用方式**:
```bash
# 設定 webhook URL
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# 發送告警
./slack-webhook.sh critical "Critical vulnerability detected" "CVE-2024-1234 in package xyz" "org/repo"
```

**參數**:
1. Severity: critical, high, medium, low
2. Message: 告警訊息
3. Details: 詳細資訊
4. Repository: 倉庫名稱

**特性**:
- 根據嚴重度使用不同顏色
- 包含時間戳和倉庫信息
- 標準化的消息格式

---

### 2. Jira Integration

**文件**: `jira-integration.py`

**用途**: 自動將安全告警建立為 Jira Issues

**環境變數**:
- `JIRA_URL` (必需): Jira 實例 URL
- `JIRA_USERNAME` (必需): Jira 用戶名
- `JIRA_API_TOKEN` (必需): Jira API Token
- `JIRA_PROJECT` (可選): 專案 Key，預設為 "SEC"
- `ALERT_SEVERITY`: 告警嚴重度
- `ALERT_SUMMARY`: 告警摘要
- `ALERT_DESCRIPTION`: 告警描述
- `ALERT_TYPE`: 告警類型
- `GITHUB_REPOSITORY`: GitHub 倉庫
- `ALERT_URL`: 告警 URL

**使用方式**:
```bash
# 設定環境變數
export JIRA_URL="https://your-company.atlassian.net"
export JIRA_USERNAME="your-email@company.com"
export JIRA_API_TOKEN="your-api-token"
export JIRA_PROJECT="SEC"

# 建立 Issue
./jira-integration.py critical "SQL Injection vulnerability" "Detected SQL injection in auth module"
```

**參數** (命令行或環境變數):
1. Severity: critical, high, medium, low
2. Summary: Issue 標題
3. Description: Issue 描述

**特性**:
- 自動映射嚴重度到 Jira 優先級
- 包含 SLA 目標
- 添加相關標籤
- 格式化的描述內容
- 支援添加評論和轉換狀態

---

## 在 GitHub Actions 中使用

### Slack 通知範例

```yaml
- name: Send Slack Notification
  if: failure()
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
  run: |
    ./config/integrations/slack-webhook.sh \
      critical \
      "CI Pipeline Failed" \
      "Build failed in ${{ github.workflow }}" \
      "${{ github.repository }}"
```

### Jira 整合範例

```yaml
- name: Create Jira Issue
  if: steps.scan.outputs.critical_count > 0
  env:
    JIRA_URL: ${{ secrets.JIRA_URL }}
    JIRA_USERNAME: ${{ secrets.JIRA_USERNAME }}
    JIRA_API_TOKEN: ${{ secrets.JIRA_API_TOKEN }}
    ALERT_SEVERITY: critical
    ALERT_SUMMARY: "Critical security vulnerabilities detected"
    ALERT_DESCRIPTION: "Found ${{ steps.scan.outputs.critical_count }} critical issues"
  run: |
    python3 ./config/integrations/jira-integration.py
```

---

## 設定指南

### Slack Webhook 設定

1. 前往 Slack 工作區設定
2. 搜尋 "Incoming Webhooks"
3. 點擊 "Add to Slack"
4. 選擇頻道（例如：#security-alerts）
5. 複製 Webhook URL
6. 添加到 GitHub Secrets: `SLACK_WEBHOOK_URL`

### Jira API Token 設定

1. 登入 Jira
2. 前往 Account Settings > Security
3. 點擊 "Create and manage API tokens"
4. 建立新的 API token
5. 複製 token
6. 添加到 GitHub Secrets:
   - `JIRA_URL`: 您的 Jira URL
   - `JIRA_USERNAME`: 您的 email
   - `JIRA_API_TOKEN`: API token

---

## 擴展整合

### 添加新整合

要添加新的整合服務，請遵循以下步驟：

1. **建立腳本文件**
   ```bash
   touch config/integrations/new-service.sh
   chmod +x config/integrations/new-service.sh
   ```

2. **實現整合邏輯**
   - 讀取環境變數配置
   - 驗證必需參數
   - 構建 API 請求
   - 處理錯誤
   - 返回適當的退出碼

3. **添加文檔**
   - 更新此 README
   - 說明用途和參數
   - 提供使用範例

4. **測試整合**
   - 本地測試
   - CI/CD 測試
   - 錯誤處理測試

### 整合模板

```bash
#!/bin/bash
# New Service Integration

set -e

# Configuration
SERVICE_URL="${SERVICE_URL:-}"
SERVICE_TOKEN="${SERVICE_TOKEN:-}"

# Validate configuration
if [ -z "$SERVICE_URL" ]; then
    echo "Error: SERVICE_URL not set"
    exit 1
fi

# Build payload
PAYLOAD=$(cat <<EOF
{
    "message": "$1",
    "severity": "$2"
}
EOF
)

# Send request
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "$SERVICE_URL" \
    -H "Authorization: Bearer $SERVICE_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

# Check result
if [ "$HTTP_CODE" -eq 200 ]; then
    echo "✅ Success"
    exit 0
else
    echo "❌ Failed (HTTP $HTTP_CODE)"
    exit 1
fi
```

---

## 疑難排解

### Slack 整合問題

**問題**: 消息未出現在 Slack

**解決方案**:
1. 驗證 webhook URL 正確
2. 檢查頻道權限
3. 測試 webhook:
   ```bash
   curl -X POST $SLACK_WEBHOOK_URL \
     -H 'Content-Type: application/json' \
     -d '{"text":"Test message"}'
   ```

### Jira 整合問題

**問題**: 認證失敗

**解決方案**:
1. 確認 API token 有效
2. 驗證 username 正確（應為 email）
3. 檢查專案權限
4. 測試連接:
   ```bash
   curl -u "email@example.com:api-token" \
     https://your-company.atlassian.net/rest/api/2/myself
   ```

---

## 安全考量

### 保護憑證

- ✅ 使用 GitHub Secrets 存儲憑證
- ✅ 不要在日誌中記錄敏感信息
- ✅ 定期輪換 API tokens
- ✅ 使用最小權限原則

### 網路安全

- ✅ 使用 HTTPS
- ✅ 驗證 SSL 證書
- ✅ 設定合適的超時時間
- ✅ 實施重試邏輯

---

## 相關資源

- [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)
- [Jira REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v2/)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

**維護者**: Security Team  
**最後更新**: 2025-11-22
