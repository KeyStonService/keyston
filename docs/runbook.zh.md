# SynergyMesh 運維手冊

## 🚨 故障排查指南

### 常見問題與解決方案

#### 1. CI Pipeline 失敗

**症狀**: GitHub Actions workflow 失敗

**診斷步驟**:

```bash
# 檢查最近的 workflow 運行
gh run list --limit 5

# 查看特定 workflow 的日誌
gh run view <run-id> --log-failed
```

**可能原因與修復**:

1. **依賴安裝失敗**

   ```bash
   # 本地重現
   cd <sub-project>
   rm -rf node_modules
   npm ci
   ```

2. **Lint 錯誤**

   ```bash
   npm run lint
   npm run lint -- --fix  # 自動修復
   ```

3. **測試失敗**

   ```bash
   npm test
   npm test -- --verbose  # 詳細輸出
   ```

#### 2. Conftest 政策驗證失敗

**症狀**: PR 中 Conftest 檢查不通過

**診斷步驟**:

```bash
# 本地安裝 Conftest
brew install conftest  # macOS
# 或
wget https://github.com/open-policy-agent/conftest/releases/download/v0.49.1/conftest_0.49.1_Linux_x86_64.tar.gz

# 測試特定文件
conftest test deploy/deployment.yaml -p governance/policies/conftest/
```

**常見違規**:

1. **Namespace 命名不符合規範**

   ```yaml
   # ❌ 錯誤
   metadata:
     name: MyNamespace

   # ✅ 正確
   metadata:
     name: team-platform-prod
     labels:
       namespace.io/team: platform
       namespace.io/environment: production
       namespace.io/lifecycle: active
   ```

2. **Service port 缺少名稱**

   ```yaml
   # ❌ 錯誤
   ports:
     - port: 80
       targetPort: 8080

   # ✅ 正確
   ports:
     - name: http
       port: 80
       targetPort: 8080
   ```

#### 3. PR 無法合併

**症狀**: "Merging is blocked" 或 "Waiting for Code Scanning results"

**診斷步驟**:

```bash
# 檢查 PR 狀態
gh pr view <pr-number> --json statusCheckRollup,mergeStateStatus

# 檢查分支保護規則
# 前往: https://github.com/we-can-fix/synergymesh/settings/branches
```

**解決方案**:

1. **確保所有 CI 檢查通過**

   ```bash
   # 查看失敗的檢查
   gh pr checks <pr-number>
   ```

2. **調整 Repository Rules**（需要 Admin 權限）
   - 前往 Settings > Rules
   - 編輯應用於 main 分支的 Ruleset
   - 調整 Code Scanning 要求

3. **使用管理員權限合併**

   ```bash
   gh pr merge <pr-number> --squash --admin
   ```

#### 4. Monorepo Dispatcher 未觸發

**症狀**: 修改了子專案代碼但 CI 未執行

**診斷步驟**:

```bash
# 檢查最近的 workflow 運行
gh run list --workflow="monorepo-dispatch.yml" --limit 3

# 查看 paths-filter 輸出
gh run view <run-id> --log
```

**可能原因**:

1. **paths-filter 配置不正確**
   - 檢查 `.github/workflows/monorepo-dispatch.yml` 中的 `filters` 配置
   - 確保路徑匹配正確

2. **變更的文件不在監控範圍內**

   ```yaml
   # 擴展監控路徑
   filters: |
     mcp-servers:
       - 'mcp-servers/**'
       - '.github/workflows/reusable-ci.yml'  # 添加依賴
   ```

### 5. SBOM 生成失敗

**症狀**: `npm run sbom` 或 CI 中 SBOM 步驟失敗

**診斷步驟**:

```bash
# 本地測試
cd <sub-project>
npx @cyclonedx/cyclonedx-npm --output-file sbom.json

# 檢查輸出
cat sbom.json | jq .
```

**修復方案**:

```bash
# 確保依賴完整安裝
npm ci

# 清除快取重試
npm cache clean --force
npm ci
npx @cyclonedx/cyclonedx-npm --output-file sbom.json
```

## 🔧 維護操作

### 添加新的子專案

1. **創建專案目錄結構**

   ```bash
   mkdir -p apps/new-service
   cd apps/new-service
   npm init -y
   ```

2. **更新根目錄 package.json**

   ```json
   {
     "workspaces": [
       "mcp-servers",
       "core/contract_service/contracts-L1/contracts",
       "advanced-system-src",
       "apps/new-service"
     ]
   }
   ```

3. **更新 Monorepo Dispatcher**

   ```yaml
   # .github/workflows/monorepo-dispatch.yml
   filters: |
     new-service:
       - 'apps/new-service/**'

   ci-new-service:
     needs: detect-changes
     if: needs.detect-changes.outputs.new-service == 'true'
     uses: ./.github/workflows/reusable-ci.yml
     with:
       working-directory: apps/new-service
       service-name: new-service
   ```

4. **更新治理註冊表**

   ```yaml
   # governance/registry.yaml
   new-service:
     id: new-service
     type: service
     language: typescript
     owner: your-team
     ...
   ```

### 更新政策規則

1. **編輯 Conftest 政策**

   ```bash
   vim governance/policies/conftest/naming_policy.rego
   ```

2. **本地測試**

   ```bash
   conftest test <test-file> -p governance/policies/conftest/
   ```

3. **提交並創建 PR**

   ```bash
   git add governance/policies/conftest/
   git commit -m "chore: update conftest policies"
   git push
   ```

### 升級依賴

1. **檢查過期依賴**

   ```bash
   # 在根目錄
   npm outdated --workspaces

   # 在特定子專案
   cd <sub-project>
   npm outdated
   ```

2. **更新依賴**

   ```bash
   # 更新特定包
   npm update <package-name> --workspace=<workspace-name>

   # 或在子專案中
   cd <sub-project>
   npm update <package-name>
   ```

3. **安全更新**

   ```bash
   npm audit fix --workspaces
   ```

## 📊 監控與告警

### 關鍵指標

1. **CI/CD 指標**
   - 建置成功率
   - 平均建置時間
   - 測試覆蓋率

2. **政策合規指標**
   - 命名規範違規數
   - 安全漏洞數量
   - SBOM 覆蓋率

3. **部署指標**（規劃中）
   - 部署頻率
   - 變更失敗率
   - 平均恢復時間

### 日誌查看

```bash
# GitHub Actions 日誌
gh run view <run-id> --log

# 特定 job 的日誌
gh run view <run-id> --log --job=<job-name>

# 下載日誌
gh run download <run-id>
```

## 🔄 回滾策略

### Git 回滾

```bash
# 回滾到上一個 commit
git revert HEAD
git push

# 回滾到特定 commit
git revert <commit-hash>
git push
```

### PR 回滾

```bash
# 創建 revert PR
gh pr create --title "Revert: <original-pr-title>" \
             --body "Reverts #<pr-number>"
```

## 📝 定期維護任務

### 每週

- [ ] 檢查依賴安全更新
- [ ] 檢閱 PR 積壓
- [ ] 檢查 CI 失敗趨勢

### 每月

- [ ] 更新依賴版本
- [ ] 檢閱並更新政策
- [ ] 審查治理註冊表
- [ ] 檢查測試覆蓋率趨勢

### 每季

- [ ] 架構檢閱
- [ ] 性能基準測試
- [ ] 災難恢復演練
- [ ] 文檔更新

## 🆘 緊急聯絡

- **Platform Team**: <platform-team@example.com>
- **Security Team**: <security@example.com>
- **On-call**: [PagerDuty / Slack Channel]

## 📚 相關資源

- [架構文檔](architecture.zh.md)
- [貢獻指南](../CONTRIBUTING.md)
- [安全政策](../SECURITY.md)
- [GitHub Actions 文檔](https://docs.github.com/actions)
- [Conftest 文檔](https://www.conftest.dev/)
