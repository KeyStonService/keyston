# Permission Simplification Guide

## 概述 (Overview)

本文檔說明專案中權限配置的簡化策略，以支持開發階段的順暢工作流程。

## 核心原則 (Core Principles)

### 開發階段：權限應該是幫助而非阻礙
**Development Stage: Permissions Should Help, Not Hinder**

- ✅ 使用 GitHub 自動提供的 `github.token`
- ✅ 無需配置額外的 secrets 或 permissions
- ✅ 開箱即用的工作流程
- ❌ 不需要手動配置自定義 tokens
- ❌ 不需要組織級別權限設置

### 生產環境：可選的增強安全性
**Production: Optional Enhanced Security**

- 生產環境可以選擇性覆蓋環境變數
- 通過環境保護規則添加額外審查
- 但不是必需的

## 變更摘要 (Changes Summary)

### 1. 移除硬編碼 Repository URL

**Before**:
```python
url='https://github.com/SynergyMesh-admin/SynergyMesh',
```

**After**:
```python
url=os.environ.get('REPOSITORY_URL', ''),
```

**理由**: 支持多組織部署，避免硬編碼特定 GitHub URL。

### 2. 簡化 Token 管理策略

**Before** (`.github/workflows/env-setup.yml`):
```yaml
# Token 優先順序：
#   1. vars.WE_TONKE (Repository Variable)
#   2. secrets.WE_TONKE (Repository Secret)
#   3. secrets.GITHUB_TOKEN (默認 Token)
```

**After**:
```yaml
# Token 策略 (Development-Friendly):
#   - 開發階段: 使用 GitHub 自動提供的 token (github.token)
#   - 無需配置額外的 secrets 或 permissions
```

### 3. 更新 Workflow Token 引用

所有工作流程現在使用 `github.token` 而非自定義 secrets：

- ✅ `.github/workflows/04-deploy-staging.yml`
- ✅ `.github/workflows/05-deploy-production.yml`
- ✅ `.github/workflows/07-dependency-update.yml`
- ✅ `.github/workflows/08-sync-subdirs.yml`
- ✅ `.github/workflows/self-healing-ci.yml`

**Before**:
```yaml
env:
  GITHUB_TOKEN: ${{ secrets.WE_TONKE || secrets.GITHUB_TOKEN }}
```

**After**:
```yaml
env:
  GITHUB_TOKEN: ${{ github.token }}
```

## 受益 (Benefits)

### 開發人員體驗
- 🚀 **即開即用**: 無需配置任何 secrets
- 🔄 **自動權限**: GitHub 自動提供適當的權限
- 🛠️ **簡化設置**: Fork 專案後立即可用

### 維護性
- 📝 **減少配置**: 不需要管理多個自定義 tokens
- 🔒 **安全**: 減少 secret 洩漏風險
- 🌍 **可移植**: 易於遷移到不同的 GitHub 組織

### CI/CD 穩定性
- ✅ **減少失敗**: 不再因為 token 配置錯誤導致失敗
- 🔧 **易於除錯**: 權限問題更容易識別和解決
- 📊 **一致性**: 所有環境使用相同的權限模式

## 遷移指南 (Migration Guide)

### 對於開發者

無需任何操作！所有變更對開發者透明：

1. Fork 或 Clone 專案
2. GitHub Actions 自動使用 `github.token`
3. 所有工作流程正常運行

### 對於維護者

如果你之前配置了自定義 secrets：

1. **WE_TONKE**: 可以安全移除
2. **DEPLOYMENT_TOKEN**: 可以安全移除
3. **DEPENDENCY_BOT_TOKEN**: 可以安全移除

這些 secrets 不再被使用，但保留它們也不會造成問題。

### 對於組織管理員

#### 開發/測試環境
- ✅ 使用預設的 `github.token`
- ✅ 無需額外配置

#### 生產環境（可選）
如果需要增強安全性，可以：

1. 在 GitHub Environments 中設置環境保護規則
2. 要求手動批准部署
3. 限制可以部署的分支

但這些都是**可選的**，不是必需的。

## 權限範圍 (Permission Scopes)

`github.token` 自動提供的權限：

- ✅ `contents: read/write` - 讀寫倉庫內容
- ✅ `pull-requests: read/write` - 管理 PR
- ✅ `issues: read/write` - 管理 Issues
- ✅ `actions: read` - 讀取 Actions 狀態
- ✅ `deployments: write` - 創建部署

這些權限足以支持大多數 CI/CD 工作流程。

## 常見問題 (FAQ)

### Q: 為什麼移除自定義 tokens？

**A**: 自定義 tokens 在開發階段是阻礙而非幫助：
- 需要手動配置
- 容易配置錯誤
- 增加維護負擔
- `github.token` 提供足夠的權限

### Q: 這會影響安全性嗎？

**A**: 不會，反而更安全：
- 減少 secret 數量 = 減少洩漏風險
- `github.token` 自動輪換
- 權限範圍由 GitHub 自動管理

### Q: 如果需要更高權限怎麼辦？

**A**: 
1. 在工作流程中明確聲明所需權限
2. 使用 GitHub Environments 添加保護規則
3. 只在絕對必要時使用 Personal Access Token

### Q: 這適用於所有工作流程嗎？

**A**: 是的，除非：
- 需要訪問其他 repository
- 需要特殊的組織級權限
- 需要長期有效的 token

在這些情況下，仍然可以使用自定義 secrets，但應該是例外而非常規。

## 最佳實踐 (Best Practices)

### ✅ 推薦做法

1. **優先使用 `github.token`**
   ```yaml
   env:
     GITHUB_TOKEN: ${{ github.token }}
   ```

2. **明確聲明所需權限**
   ```yaml
   permissions:
     contents: write
     pull-requests: write
   ```

3. **使用環境保護規則而非自定義 tokens**
   ```yaml
   environment:
     name: production
     url: https://example.com
   ```

### ❌ 避免做法

1. **不要硬編碼 repository URLs**
   ```python
   # ❌ Bad
   url='https://github.com/org/repo'
   
   # ✅ Good
   url=os.environ.get('REPOSITORY_URL', '')
   ```

2. **不要創建不必要的自定義 tokens**
   ```yaml
   # ❌ Bad
   token: ${{ secrets.CUSTOM_TOKEN }}
   
   # ✅ Good
   token: ${{ github.token }}
   ```

3. **不要在開發階段要求過度權限**
   ```yaml
   # ❌ Bad - 開發階段不需要這些
   permissions:
     id-token: write
     packages: write
     security-events: write
   
   # ✅ Good - 只聲明實際需要的
   permissions:
     contents: read
   ```

## 總結 (Conclusion)

通過簡化權限配置：
- ✅ 開發更順暢
- ✅ 配置更簡單
- ✅ 安全性更高
- ✅ 維護更容易

**記住**: 在開發階段，權限應該是幫助而非阻礙。

---

**相關文檔**:
- [GitHub Actions Permissions](https://docs.github.com/en/actions/security-guides/automatic-token-authentication)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Environment Protection Rules](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
