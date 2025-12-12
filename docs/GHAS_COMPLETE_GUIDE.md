# GitHub Advanced Security (GHAS) 完整實施指南

## 📋 目錄

1. [概述](#概述)
2. [環境準備](#環境準備)
3. [CodeQL 實施](#codeql-實施)
4. [Secret Scanning 實施](#secret-scanning-實施)
5. [監控與報告](#監控與報告)
6. [最佳實踐](#最佳實踐)
7. [疑難排解](#疑難排解)

## 概述

本指南提供 GitHub Advanced Security
(GHAS) 在企業環境中的完整實施方案，涵蓋從基礎架構配置到高級安全功能的所有方面。

### GHAS 核心功能

- **CodeQL**: 靜態應用安全測試 (SAST)
- **Secret Scanning**: 秘密檢測和防護
- **Dependency Review**: 依賴項安全審查
- **Security Advisories**: 安全公告管理

### 文檔結構

```
docs/
├── GHAS_COMPLETE_GUIDE.md      # 本文件 - 完整實施指南
├── GHAS_DEPLOYMENT.md          # 部署架構與環境準備
├── CODEQL_SETUP.md             # CodeQL 自動化掃描配置
└── SECRET_SCANNING.md          # Secret Scanning 全方位防護
```

## 環境準備

### 第一步：基礎架構配置

詳細內容請參考 [GHAS_DEPLOYMENT.md](./GHAS_DEPLOYMENT.md)

#### 快速開始檢查清單

- [ ] GitHub Enterprise Cloud 或 Server 3.1+
- [ ] 組織管理員權限
- [ ] GHAS 授權已啟用
- [ ] 網路配置完成
- [ ] 監控系統就緒

#### 關鍵配置文件

| 文件                                 | 用途                |
| ------------------------------------ | ------------------- |
| `.github/security-policy.yml`        | 組織安全策略        |
| `.github/workflows/setup-runner.yml` | Runner 設定工作流程 |
| `config/security-network-config.yml` | 網路安全配置        |
| `config/prometheus-config.yml`       | Prometheus 監控     |
| `config/elasticsearch-config.sh`     | Elasticsearch 整合  |

### 第二步：權限與團隊配置

```bash
# 建立安全團隊
gh api \
  --method POST \
  /orgs/{org}/teams \
  --field name="security-team" \
  --field description="Enterprise Security Team" \
  --field privacy="closed"

# 配置倉庫權限
# 參考 GHAS_DEPLOYMENT.md 中的詳細說明
```

### 第三步：監控系統設置

#### Elasticsearch 設置

```bash
# 執行 Elasticsearch 配置腳本
./config/elasticsearch-config.sh
```

#### Prometheus 設置

```yaml
# 使用提供的 Prometheus 配置
# config/prometheus-config.yml
# config/prometheus-rules.yml
```

## CodeQL 實施

詳細內容請參考 [CODEQL_SETUP.md](./CODEQL_SETUP.md)

### 快速開始

#### 1. 啟用 CodeQL 工作流程

工作流程已配置於 `.github/workflows/codeql-advanced.yml`，支援：

- JavaScript/TypeScript
- Python
- Java
- C#
- C/C++
- Go

#### 2. 自定義配置

```yaml
# .github/codeql/codeql-config.yml
name: 'Enterprise CodeQL Config'
disable-default-queries: false
queries:
  - name: security-extended
    uses: security-extended
  - name: custom-enterprise-queries
    uses: ./.github/codeql/custom-queries
```

#### 3. 添加自定義查詢

```bash
# 參考現有查詢
cat .github/codeql/custom-queries/enterprise-security.ql

# 添加您自己的查詢規則
# 遵循 CodeQL 查詢語法
```

#### 4. 配置 PR 安全閘門

工作流程 `.github/workflows/pr-security-gate.yml` 提供：

- 自動 CodeQL 掃描
- 嚴重程度評估
- 自動 PR 評論
- 合併阻擋（Critical 級別）

### 多語言建置支援

```bash
# 使用建置腳本
./scripts/build-matrix.sh javascript
./scripts/build-matrix.sh python
./scripts/build-matrix.sh java
# ... 等
```

## Secret Scanning 實施

詳細內容請參考 [SECRET_SCANNING.md](./SECRET_SCANNING.md)

### 快速開始

#### 1. 啟用 Secret Protection

工作流程已配置於 `.github/workflows/secret-protection.yml`

#### 2. 安裝本地保護

```bash
# 安裝 pre-push hook
./scripts/advanced-push-protection.sh install

# 測試掃描
./scripts/advanced-push-protection.sh scan
```

#### 3. 配置自定義模式

```bash
# 部署企業級模式
./scripts/manage-secret-patterns.py deploy --org your-org

# 列出現有模式
./scripts/manage-secret-patterns.py list --org your-org

# 添加自定義模式
./scripts/manage-secret-patterns.py create \
  --org your-org \
  --name "My Pattern" \
  --regex "pattern_[0-9a-f]{32}" \
  --secret-type "custom_secret"
```

#### 4. 處理旁路請求

使用工作流程 `.github/workflows/secret-bypass-request.yml`：

1. 前往 Actions 標籤
2. 選擇 "Secret Scanning Bypass Request"
3. 填寫請求詳情
4. 提交審核

### 秘密類型支援

- GitHub Tokens
- API Keys (AWS, Azure, GCP)
- Database Credentials
- Private Keys
- OAuth Secrets
- JWT Tokens
- Third-party Service Keys

## 監控與報告

### Prometheus 指標

關鍵指標已在 `config/prometheus-rules.yml` 中定義：

- 安全警報數量（按嚴重程度）
- API 速率限制使用
- Runner 健康狀態
- 修復時間指標

### Elasticsearch 日誌

日誌收集配置於 `config/elasticsearch-config.sh`：

- 結構化日誌存儲
- 快速查詢和分析
- 長期保留（90 天）
- Kibana 視覺化

### Dashboard 建議

建議監控的 Dashboard：

1. **安全概覽**
   - 開放警報總數
   - 按嚴重程度分類
   - 趨勢圖表

2. **CodeQL 指標**
   - 掃描執行次數
   - 發現的漏洞
   - 修復狀態

3. **Secret Scanning 指標**
   - 檢測到的秘密
   - 旁路請求
   - 修復時間

4. **系統健康**
   - Runner 狀態
   - API 配額
   - 工作流程執行時間

## 最佳實踐

### 安全開發生命週期

1. **開發階段**
   - 使用 pre-push hooks
   - 本地運行安全掃描
   - 遵循安全編碼指南

2. **代碼審查**
   - 檢查安全警報
   - 驗證修復方案
   - 使用 PR 模板

3. **部署前**
   - 確保所有 Critical 警報已修復
   - 運行完整掃描
   - 更新安全文檔

4. **生產環境**
   - 持續監控
   - 定期審查警報
   - 保持工具更新

### 團隊協作

#### 角色與職責

| 角色        | 職責                         |
| ----------- | ---------------------------- |
| 安全團隊    | 政策制定、工具管理、事件響應 |
| 開發團隊    | 修復漏洞、遵循最佳實踐       |
| DevOps 團隊 | 基礎設施維護、監控配置       |
| 管理層      | 資源分配、風險決策           |

#### 溝通渠道

- Slack: #security-alerts
- Email: <security-team@example.com>
- Issues: GitHub Security 標籤
- Wiki: 內部安全知識庫

### 培訓計劃

1. **新員工入職**
   - 安全意識培訓
   - GHAS 工具使用
   - 最佳實踐指南

2. **定期培訓**
   - 每季度安全更新
   - 新威脅介紹
   - 案例學習

3. **實戰演練**
   - 安全事件模擬
   - 修復演練
   - 工具效能測試

## 疑難排解

### CodeQL 問題

#### 掃描失敗

**症狀**: CodeQL 分析失敗

**解決方案**:

```bash
# 檢查建置步驟
./scripts/build-matrix.sh <language>

# 增加 timeout
# 在工作流程中設定 timeout-minutes

# 啟用 debug 模式
# 在 init 步驟中添加 debug: true
```

#### 記憶體不足

**解決方案**:

```yaml
env:
  CODEQL_RAM: 8192
```

### Secret Scanning 問題

#### 太多誤報

**解決方案**:

1. 調整自定義模式
2. 添加排除規則
3. 使用更精確的正則表達式

#### Push 被阻擋

**解決方案**:

```bash
# 確認是否真的是秘密
# 如果是誤報，提交旁路請求

# 緊急情況下（不建議）
git push --no-verify
```

### 監控問題

#### Prometheus 無法收集指標

**檢查清單**:

- [ ] Exporter 是否運行
- [ ] 網路連接是否正常
- [ ] 認證配置是否正確
- [ ] 防火牆規則是否允許

#### Elasticsearch 連接失敗

**解決方案**:

```bash
# 測試連接
curl -X GET "http://elasticsearch:9200/_cluster/health"

# 檢查憑證
# 驗證 ELASTICSEARCH_PASSWORD

# 重新運行配置腳本
./config/elasticsearch-config.sh
```

## 進階主題

### 自動化修復

考慮整合自動修復工具：

- Dependabot 自動更新
- CodeQL 自動修復建議
- 自定義修復腳本

### 合規性

確保符合以下標準：

- SOC 2
- ISO 27001
- GDPR
- HIPAA（如適用）

### 擴展整合

可整合的其他工具：

- SIEM 系統
- Jira / 任務管理
- Slack / 通訊工具
- PagerDuty / 告警系統

## 資源連結

### 官方文檔

- [GitHub Advanced Security](https://docs.github.com/en/enterprise-cloud@latest/get-started/learning-about-github/about-github-advanced-security)
- [CodeQL 文檔](https://codeql.github.com/docs/)
- [Secret Scanning 文檔](https://docs.github.com/en/code-security/secret-scanning)

### 內部文檔

- [GHAS 部署指南](./GHAS_DEPLOYMENT.md)
- [CodeQL 設定指南](./CODEQL_SETUP.md)
- [Secret Scanning 指南](./SECRET_SCANNING.md)

### 社群資源

- GitHub Community Forum
- Security Best Practices
- OWASP Resources

## 支援

### 獲取幫助

1. **內部支援**
   - 聯繫安全團隊
   - 查看內部知識庫
   - 參加每週 Q&A

2. **外部支援**
   - GitHub Support
   - 社群論壇
   - 專業諮詢服務

### 回饋與改進

我們歡迎您的回饋！請通過以下方式提供建議：

- 提交 GitHub Issue
- 參與團隊會議
- 填寫回饋表單

---

## 附錄

### 快速參考

#### 常用命令

```bash
# CodeQL
./scripts/build-matrix.sh <language>

# Secret Scanning
./scripts/advanced-push-protection.sh scan
./scripts/manage-secret-patterns.py list --org <org>

# 監控
curl http://prometheus:9090/metrics
curl http://elasticsearch:9200/_cat/indices
```

#### 重要路徑

```
.github/
├── workflows/              # GitHub Actions 工作流程
├── codeql/                # CodeQL 配置和查詢
└── secret-scanning/       # Secret Scanning 配置

config/                    # 監控和基礎設施配置
scripts/                   # 自動化腳本
docs/                      # 文檔
```

### 更新日誌

- **2025-11-22**: 初始版本發布
  - 完整 GHAS 配置
  - CodeQL 和 Secret Scanning 實施
  - 監控和報告系統

---

**維護者**: SynergyMesh Security Team  
**最後更新**: 2025-11-22  
**版本**: 1.0.0
