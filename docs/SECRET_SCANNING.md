# Secret Scanning 全方位防護實現

## 概述

Secret Scanning 是 GitHub Advanced
Security 的關鍵功能，用於檢測和防止敏感資訊（如 API 金鑰、密碼、令牌）洩露到代碼庫中。本文檔詳細說明如何在企業環境中實現全方位的 Secret
Scanning 保護。

## Push Protection 自動化配置

### 什麼是 Push Protection？

Push
Protection 是一種主動防禦機制，在開發者推送代碼時即時檢測並阻止秘密洩露。這是防止敏感資訊洩露的第一道防線。

### 基本 Push Protection 設定

Push Protection 工作流程已配置於
`.github/workflows/secret-protection.yml`，提供以下功能：

#### 主要特性

1. **即時掃描**: 在 push 和 pull request 時自動觸發
2. **多模式檢測**: 支援多種秘密類型的模式匹配
3. **PR 評論**: 自動在 PR 中添加掃描結果
4. **安全建議**: 提供如何處理洩露秘密的指引

#### 支援的秘密類型

- GitHub Personal Access Tokens (PAT)
- OpenAI API Keys
- AWS Access Keys
- Azure Client Secrets
- Generic API Keys
- Private Keys (RSA, SSH)
- JWT Tokens
- Database Passwords
- Connection Strings
- Third-party API Keys (Slack, Stripe, etc.)

### 高級推播保護實現

#### 安裝 Pre-push Hook

使用 `scripts/advanced-push-protection.sh` 腳本安裝本地保護：

```bash
# 安裝 pre-push hook
./scripts/advanced-push-protection.sh install

# 執行掃描
./scripts/advanced-push-protection.sh scan
```

#### 檢查模式

```bash
# 檢查暫存的變更
./scripts/advanced-push-protection.sh "" "" staged

# 檢查最近的 commits
./scripts/advanced-push-protection.sh "" "" commits

# 完整倉庫掃描
./scripts/advanced-push-protection.sh "" "" full

# 嚴格模式（預設）
./scripts/advanced-push-protection.sh "" "" strict
```

#### Hook 工作原理

1. 在推送前自動執行
2. 掃描暫存的文件和最近的 commits
3. 檢測潛在的秘密模式
4. 如果發現秘密，阻止推送
5. 提供詳細的檢測報告

## 自定義模式定義與管理

### 企業專用模式配置

自定義模式定義於 `.github/secret-scanning/custom-patterns.yml`，包含：

#### 模式類別

**Critical（關鍵）**:

- 加密主金鑰
- AES 加密金鑰
- RSA 私鑰
- SSH 私鑰
- 雲端服務憑證

**High（高）**:

- 企業資料庫連接字串
- 內部 API 令牌
- 服務帳戶金鑰
- JWT 簽名密鑰
- OAuth 客戶端密鑰

**Medium（中）**:

- 舊版 API 金鑰
- Session 密鑰
- Bearer 令牌
- Webhook 密鑰

### 動態模式管理

#### 使用 Python 管理腳本

```bash
# 列出所有自定義模式
./scripts/manage-secret-patterns.py list --org your-org

# 建立新模式
./scripts/manage-secret-patterns.py create \
  --org your-org \
  --name "My Custom Pattern" \
  --regex "custom_[0-9a-f]{32}" \
  --secret-type "custom_secret"

# 更新現有模式
./scripts/manage-secret-patterns.py update \
  --org your-org \
  --pattern-id 123 \
  --name "Updated Pattern Name"

# 刪除模式
./scripts/manage-secret-patterns.py delete \
  --org your-org \
  --pattern-id 123

# 部署企業級模式集
./scripts/manage-secret-patterns.py deploy --org your-org

# 導出模式到文件
./scripts/manage-secret-patterns.py export \
  --org your-org \
  --file patterns-backup.json

# 從文件導入模式
./scripts/manage-secret-patterns.py import \
  --org your-org \
  --file patterns-backup.json
```

#### 環境變數配置

```bash
# 設定 GitHub Token
export GITHUB_TOKEN="your_github_token"

# 執行操作（無需 --token 參數）
./scripts/manage-secret-patterns.py list --org your-org
```

### 模式設計最佳實踐

1. **特異性**: 模式應足夠具體以減少誤報
2. **覆蓋範圍**: 確保涵蓋所有可能的格式變體
3. **效能**: 避免過於複雜的正則表達式
4. **文檔化**: 為每個模式提供清晰的描述
5. **測試**: 使用測試案例驗證模式有效性

#### 範例：建立自定義模式

```yaml
patterns:
  - name: 'Custom Service Token'
    pattern: 'svc_[A-Za-z0-9]{40}'
    confidence: 'high'
    severity: 'high'
    description: 'Internal service authentication token'
```

## 委派旁路機制實現

### 什麼是旁路機制？

有時某些檢測到的「秘密」實際上是：

- 誤報（False Positives）
- 測試資料
- 公開可用的範例
- 已批准的例外情況

旁路機制允許授權人員在經過適當審查後豁免這些警報。

### 旁路請求工作流程

工作流程位於 `.github/workflows/secret-bypass-request.yml`。

#### 發起旁路請求

```bash
# 透過 GitHub UI
1. 前往 Actions 標籤
2. 選擇 "Secret Scanning Bypass Request" 工作流程
3. 點擊 "Run workflow"
4. 填寫必要資訊：
   - Alert ID（警報 ID）
   - Bypass Reason（旁路原因）
   - Approver（批准者）
   - Justification（詳細理由）
5. 點擊 "Run workflow"
```

#### 旁路原因選項

- **False positive**: 誤報，不是真正的秘密
- **Test data**: 測試用途的假資料
- **Legacy system migration**: 舊系統遷移過程
- **Approved exception**: 經批准的例外情況
- **Development environment only**: 僅用於開發環境

### 批准流程

1. **請求提交**: 開發者提交旁路請求
2. **Issue 建立**: 系統自動建立追蹤 Issue
3. **通知批准者**: 安全團隊成員收到通知
4. **審查**: 批准者檢查警報和理由
5. **決策**:
   - 批准：標記警報為 resolved
   - 拒絕：關閉 Issue 並說明原因
6. **審計**: 所有決策記錄在審計日誌中

#### 批准旁路請求

```bash
# 使用 GitHub CLI
gh api --method PATCH \
  /repos/{owner}/{repo}/secret-scanning/alerts/{alert_id} \
  -f state=resolved \
  -f resolution=false_positive
```

### 審計日誌

所有旁路請求自動記錄在 `.github/audit-logs/secret-bypass-requests.json`：

```json
[
  {
    "timestamp": "2024-11-22T10:30:00Z",
    "requester": "developer1",
    "alert_id": "123",
    "reason": "False positive",
    "approver": "security-lead",
    "issue_number": 456,
    "status": "pending"
  }
]
```

## 整合與自動化

### CI/CD 整合

#### 在 Pipeline 中執行掃描

```yaml
# 在您的 CI/CD 工作流程中
- name: Secret Scanning
  run: |
    ./scripts/advanced-push-protection.sh scan
```

#### Pull Request 自動檢查

Secret Protection 工作流程會自動：

1. 掃描 PR 中的變更
2. 添加掃描結果評論
3. 提供修復建議

### 與 SIEM 整合

```bash
# 將秘密掃描事件發送到 SIEM
curl -X POST https://siem.example.com/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "secret_detected",
    "severity": "critical",
    "repository": "org/repo",
    "alert_id": "123"
  }'
```

### 通知配置

配置多種通知渠道：

1. **GitHub Issues**: 自動建立追蹤 issue
2. **Email**: 發送給安全團隊
3. **Slack**: 即時通知到安全頻道
4. **Jira**: 建立安全任務

## 最佳實踐

### 預防秘密洩露

1. **使用環境變數**

   ```bash
   # 好的做法
   export DATABASE_URL="postgres://..."

   # 避免
   const dbUrl = "postgres://user:password@host/db"
   ```

2. **使用密鑰管理服務**
   - AWS Secrets Manager
   - Azure Key Vault
   - HashiCorp Vault
   - GitHub Secrets

3. **使用 .gitignore**

   ```gitignore
   # 忽略包含秘密的文件
   .env
   .env.local
   secrets.yml
   *.key
   *.pem
   ```

4. **代碼審查**
   - 在合併前仔細檢查所有變更
   - 使用 PR 模板提醒檢查秘密

### 處理已洩露的秘密

如果秘密已經被推送到倉庫：

1. **立即輪換/撤銷**

   ```bash
   # 立即撤銷被洩露的憑證
   # 生成新的憑證
   # 更新所有使用該憑證的系統
   ```

2. **清理 Git 歷史**

   ```bash
   # 使用 BFG Repo-Cleaner
   bfg --replace-text passwords.txt repo.git

   # 或使用 git filter-branch
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch path/to/secret' \
     --prune-empty --tag-name-filter cat -- --all
   ```

3. **強制推送**

   ```bash
   git push --force --all
   git push --force --tags
   ```

4. **通知相關團隊**
   - 告知安全團隊
   - 更新受影響的服務
   - 審查存取日誌

### 團隊培訓

1. **安全意識培訓**
   - 定期進行秘密管理培訓
   - 分享真實案例
   - 提供最佳實踐指南

2. **工具使用培訓**
   - 如何使用 pre-push hooks
   - 如何回應警報
   - 如何請求旁路

3. **事件響應演練**
   - 模擬秘密洩露場景
   - 練習應對流程
   - 改進響應時間

## 監控與報告

### 關鍵指標

追蹤以下指標：

- **秘密檢測數量**: 按類型和嚴重程度
- **平均修復時間**: 從檢測到修復
- **誤報率**: 被標記為誤報的百分比
- **旁路請求數量**: 及批准率
- **覆蓋範圍**: 啟用掃描的倉庫百分比

### 生成報告

```bash
# 獲取秘密掃描統計
gh api /orgs/{org}/secret-scanning/alerts \
  --jq '[group_by(.secret_type)[] | {type: .[0].secret_type, count: length}]'
```

### Dashboard 監控

建議配置 Dashboard 顯示：

1. 開放警報數量（按嚴重程度）
2. 最近 30 天的趨勢
3. 修復速度指標
4. 最常見的秘密類型
5. 最活躍的倉庫

## 疑難排解

### 常見問題

**Q: 掃描報告太多誤報怎麼辦？**

A:

1. 調整自定義模式以提高精確度
2. 使用排除規則過濾已知的誤報
3. 為測試文件添加排除路徑

**Q: 如何處理舊倉庫中的歷史秘密？**

A:

1. 執行完整的倉庫掃描
2. 優先處理高嚴重程度的警報
3. 輪換所有被檢測到的憑證
4. 考慮清理 Git 歷史

**Q: Push Protection 阻止了合法的推送？**

A:

1. 確認檢測到的是否真的是秘密
2. 如果是誤報，提交旁路請求
3. 如果是測試資料，將其移到配置文件中

### 獲取支援

- 查閱
  [GitHub Secret Scanning 文檔](https://docs.github.com/en/code-security/secret-scanning)
- 聯繫安全團隊
- 查看內部知識庫
- 參與安全社群討論

## 相關資源

- [Secret Scanning 官方文檔](https://docs.github.com/en/code-security/secret-scanning)
- [Push Protection 指南](https://docs.github.com/en/code-security/secret-scanning/protecting-pushes-with-push-protection)
- [自定義模式文檔](https://docs.github.com/en/code-security/secret-scanning/defining-custom-patterns-for-secret-scanning)
- [Git 安全最佳實踐](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure)

---

**最後更新**: 2025-11-22  
**維護者**: SynergyMesh Security Team
