# 📌 MachineNativeOps 版本管理策略

> **文件版本**: 1.0.0  
> **建立日期**: 2025-12-17  
> **維護者**: SynergyMesh Development Team  
> **狀態**: ✅ APPROVED - Production Standard

---

## 📋 目錄

1. [版本管理原則](#-版本管理原則)
2. [單一真實來源](#-單一真實來源-single-source-of-truth)
3. [語意化版本控制](#-語意化版本控制-semantic-versioning)
4. [發布流程](#-發布流程)
5. [版本號規則](#-版本號規則)
6. [Git Tags 管理](#-git-tags-管理)
7. [子模組版本管理](#-子模組版本管理)
8. [FAQ](#-常見問題)

---

## 🎯 版本管理原則

### 核心原則

1. **單一真實來源** (Single Source of Truth)
   - `machinenativeops.yaml` 的 `version` 欄位是版本號的唯一來源
   - 所有其他地方的版本號必須從此文件讀取或同步

2. **語意化版本控制** (Semantic Versioning)
   - 嚴格遵守 [SemVer 2.0.0](https://semver.org/) 規範
   - 格式：`MAJOR.MINOR.PATCH`（例如：`4.0.0`）

3. **Git Tags 整合**
   - 每次發布必須創建對應的 Git tag
   - Tag 格式：`vMAJOR.MINOR.PATCH`（例如：`v4.0.0`）

4. **自動化優先**
   - 版本號更新應由 CI/CD 自動化處理
   - 減少人為錯誤

---

## 📍 單一真實來源 (Single Source of Truth)

### 主配置文件

**文件位置**: `/machinenativeops.yaml`

```yaml
# ═══════════════════════════════════════════════════════════════════════════════
#                    SynergyMesh Master Configuration
#                    主系統配置 - 統一入口點
# ═══════════════════════════════════════════════════════════════════════════════

version: "4.0.0"              # 🎯 版本號單一真實來源
vision_version: "1.0.0"        # 願景框架版本
name: "SynergyMesh"
description: |
  次世代雲原生智能自動化平台
```

### 為什麼選擇 `machinenativeops.yaml`？

✅ **優勢**:
1. **機器可讀** - YAML 格式易於自動化處理
2. **統一入口** - 符合專案「單一配置檔作為真實來源」的設計理念
3. **易於維護** - 集中管理所有系統級配置
4. **版本控制** - Git 追蹤變更歷史
5. **跨語言支援** - YAML 解析器在所有主流語言中可用

❌ **不使用 `package.json` 的原因**:
- 只覆蓋 Node.js 生態系統
- 專案使用多語言（TypeScript、Python、Go、Rust）
- `package.json` 應從 `machinenativeops.yaml` 同步版本

### 版本號讀取範例

**TypeScript**:
```typescript
import { readFileSync } from 'fs';
import { parse } from 'yaml';

function getProjectVersion(): string {
  const config = parse(readFileSync('machinenativeops.yaml', 'utf8'));
  return config.version;
}

console.log(`Version: ${getProjectVersion()}`); // Version: 4.0.0
```

**Python**:
```python
import yaml

def get_project_version() -> str:
    with open('machinenativeops.yaml', 'r') as f:
        config = yaml.safe_load(f)
    return config['version']

print(f"Version: {get_project_version()}")  # Version: 4.0.0
```

**Bash**:
```bash
# 使用 yq (YAML processor)
VERSION=$(yq eval '.version' machinenativeops.yaml)
echo "Version: $VERSION"  # Version: 4.0.0
```

---

## 🔢 語意化版本控制 (Semantic Versioning)

### SemVer 格式

```
MAJOR.MINOR.PATCH

例如: 4.2.1
     │ │ │
     │ │ └─ PATCH: 向後兼容的錯誤修正
     │ └─── MINOR: 向後兼容的新功能
     └───── MAJOR: 不向後兼容的 API 變更
```

### 版本號遞增規則

| 變更類型 | 範例 | 遞增規則 | 新版本 |
|---------|------|---------|-------|
| **重大變更** (Breaking Changes) | API 簽名變更、目錄結構重構 | `MAJOR += 1`, `MINOR = 0`, `PATCH = 0` | `4.0.0` → `5.0.0` |
| **新功能** (New Features) | 新增 API endpoint、新模組 | `MINOR += 1`, `PATCH = 0` | `4.2.0` → `4.3.0` |
| **錯誤修正** (Bug Fixes) | 修復 bug、性能優化 | `PATCH += 1` | `4.2.1` → `4.2.2` |

### 變更類型定義

#### MAJOR（主版本號）遞增條件

當進行**不向後兼容的變更**時遞增 MAJOR：

```yaml
breaking_changes:
  - API 簽名變更（移除參數、更改參數順序）
  - 移除公開的類別、函數、模組
  - 更改配置文件格式（如 YAML 結構變更）
  - 目錄結構重大重組（如本次架構重構）
  - 依賴項主版本升級（導致 API 變更）
```

**範例**:
```typescript
// v4.x.x
function createUser(name: string): User { ... }

// v5.0.0 - BREAKING CHANGE
function createUser(data: UserCreateInput): User { ... }
```

#### MINOR（次版本號）遞增條件

當進行**向後兼容的新功能**時遞增 MINOR：

```yaml
new_features:
  - 新增 API endpoint（不影響現有 API）
  - 新增配置選項（可選，有預設值）
  - 新增類別、函數、模組
  - 新增子命令（CLI）
  - 功能增強（不破壞現有行為）
```

**範例**:
```typescript
// v4.2.0
interface UserConfig {
  name: string;
  email: string;
}

// v4.3.0 - NEW FEATURE (向後兼容)
interface UserConfig {
  name: string;
  email: string;
  avatar?: string;  // 新增可選欄位
}
```

#### PATCH（修訂號）遞增條件

當進行**向後兼容的錯誤修正**時遞增 PATCH：

```yaml
bug_fixes:
  - 修復 bug
  - 性能優化（不改變 API）
  - 安全漏洞修補
  - 文檔更新（不涉及代碼變更）
  - 依賴項 PATCH 升級
```

**範例**:
```typescript
// v4.2.1 - 修復前
function calculateSum(a: number, b: number): number {
  return a - b;  // BUG: 應該是加法
}

// v4.2.2 - 修復後
function calculateSum(a: number, b: number): number {
  return a + b;  // FIXED
}
```

---

## 🚀 發布流程

### 標準發布流程 (Standard Release)

#### 步驟 1: 確定版本號

根據變更類型確定新版本號：

```bash
# 查看當前版本
CURRENT_VERSION=$(yq eval '.version' machinenativeops.yaml)
echo "Current version: $CURRENT_VERSION"

# 根據變更類型決定新版本
# - 重大變更 → MAJOR
# - 新功能 → MINOR
# - 錯誤修正 → PATCH
```

#### 步驟 2: 更新版本號

**手動更新**:
```bash
# 編輯 machinenativeops.yaml
vim machinenativeops.yaml

# 修改 version 欄位
version: "5.0.0"  # 從 4.x.x 升級到 5.0.0
```

**自動化更新** (推薦):
```bash
# 使用自動化腳本
npm run version:bump -- --type major
# 或
npm run version:bump -- --type minor
# 或
npm run version:bump -- --type patch
```

#### 步驟 3: 同步其他文件

更新其他需要版本號的文件：

```bash
# 同步 package.json
npm run version:sync

# 手動更新（如果自動化未覆蓋）
# - README.md 的版本徽章
# - CHANGELOG.md
```

#### 步驟 4: 更新 CHANGELOG

```bash
# 編輯 CHANGELOG.md
vim CHANGELOG.md
```

```markdown
## [5.0.0] - 2025-12-20

### 💥 Breaking Changes
- 重構目錄結構，建立 `src/` 主目錄
- 合併重複目錄（infra/infrastructure, deployment/deploy）
- 標準化命名為 kebab-case

### ✨ New Features
- 新增架構重構計劃文檔
- 新增遷移指南

### 🐛 Bug Fixes
- 無

### 📚 Documentation
- 更新 README.md 專案結構章節
- 更新 CONTRIBUTING.md 目錄結構規範
```

#### 步驟 5: 提交變更

```bash
# 暫存所有版本相關變更
git add machinenativeops.yaml package.json CHANGELOG.md README.md

# 提交（使用 Conventional Commits 格式）
git commit -m "chore: bump version to v5.0.0"
```

#### 步驟 6: 創建 Git Tag

```bash
# 創建帶註解的 tag
git tag -a v5.0.0 -m "Release v5.0.0 - Architecture Restructuring

Major Changes:
- Restructured project to use src/ main directory
- Merged duplicate directories
- Standardized naming to kebab-case
- Established version management strategy

See CHANGELOG.md for full details."

# 驗證 tag
git tag -l -n9 v5.0.0
```

#### 步驟 7: 推送到遠端

```bash
# 推送提交
git push origin main

# 推送 tag
git push origin v5.0.0

# 或一次推送所有 tags
git push origin --tags
```

#### 步驟 8: GitHub Release

創建 GitHub Release（自動或手動）：

**自動化** (透過 CI/CD):
```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags:
      - 'v*'
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          body_path: CHANGELOG.md
          draft: false
          prerelease: false
```

**手動**:
1. 前往 GitHub Repository → Releases
2. 點擊 "Draft a new release"
3. 選擇 tag: `v5.0.0`
4. 標題: `v5.0.0 - Architecture Restructuring`
5. 描述: 複製 CHANGELOG.md 對應版本內容
6. 點擊 "Publish release"

---

## 🏷️ Git Tags 管理

### Tag 命名規範

```bash
# 標準版本
v4.0.0, v4.1.0, v4.1.1

# 預發布版本
v5.0.0-alpha.1, v5.0.0-beta.2, v5.0.0-rc.1

# 特殊標籤
v4.0.0-pre-refactor  # 備份 tag
v4.0.0-hotfix        # 緊急修復 tag
```

### Tag 類型

| Tag 類型 | 格式 | 範例 | 用途 |
|---------|------|------|------|
| **正式發布** | `vX.Y.Z` | `v4.0.0` | 正式版本發布 |
| **Alpha** | `vX.Y.Z-alpha.N` | `v5.0.0-alpha.1` | 內部測試版本 |
| **Beta** | `vX.Y.Z-beta.N` | `v5.0.0-beta.2` | 公開測試版本 |
| **RC** | `vX.Y.Z-rc.N` | `v5.0.0-rc.1` | 發布候選版本 |
| **備份** | `vX.Y.Z-pre-<action>` | `v4.0.0-pre-refactor` | 重大變更前備份 |

### Tag 操作命令

```bash
# 創建 annotated tag（推薦）
git tag -a v5.0.0 -m "Release v5.0.0"

# 創建 lightweight tag（不推薦）
git tag v5.0.0

# 列出所有 tags
git tag -l

# 查看 tag 詳細資訊
git show v5.0.0

# 刪除本地 tag
git tag -d v5.0.0

# 刪除遠端 tag
git push origin :refs/tags/v5.0.0

# 推送所有 tags
git push origin --tags

# Checkout 到特定 tag
git checkout v5.0.0
```

---

## 📦 子模組版本管理

### Monorepo 版本策略

MachineNativeOps 使用 **統一版本號** 策略（Fixed/Locked Versioning）：

```yaml
# machinenativeops.yaml
version: "5.0.0"  # 所有子模組共用此版本號

# 所有子模組的 package.json 同步版本
packages:
  - src/core/package.json → version: "5.0.0"
  - src/governance/package.json → version: "5.0.0"
  - src/autonomous/package.json → version: "5.0.0"
```

### 為什麼使用統一版本？

✅ **優勢**:
1. **簡化管理** - 只需維護一個版本號
2. **一致性** - 所有模組版本同步
3. **易於追蹤** - 版本號對應明確的系統狀態
4. **發布簡單** - 一次發布所有模組

❌ **獨立版本的問題**:
- 版本管理複雜度高（需追蹤數十個版本號）
- 模組間依賴關係難以管理
- 發布流程繁瑣

### 版本同步腳本

```bash
# scripts/version/sync-all.sh
#!/bin/bash
set -e

# 從 machinenativeops.yaml 讀取版本號
VERSION=$(yq eval '.version' machinenativeops.yaml)
echo "Syncing all packages to version: $VERSION"

# 同步所有 package.json
find src/ -name "package.json" | while read pkg; do
  echo "Updating $pkg"
  jq --arg ver "$VERSION" '.version = $ver' "$pkg" > "$pkg.tmp"
  mv "$pkg.tmp" "$pkg"
done

echo "✅ All packages synced to v$VERSION"
```

**使用方法**:
```bash
# 自動同步所有子模組版本
npm run version:sync
```

---

## ❓ 常見問題

### Q1: 如何查看當前版本號？

```bash
# 方法 1: 讀取 machinenativeops.yaml
yq eval '.version' machinenativeops.yaml

# 方法 2: 使用 npm 腳本
npm run version:show

# 方法 3: 查看最新 Git tag
git describe --tags --abbrev=0
```

### Q2: 如何決定是 MAJOR、MINOR 還是 PATCH？

參考上方 [版本號遞增規則](#版本號遞增規則)。簡單判斷：

- **會破壞現有代碼嗎？** → MAJOR
- **增加新功能但不破壞現有代碼？** → MINOR
- **只是修復 bug？** → PATCH

### Q3: 預發布版本如何管理？

```bash
# Alpha 版本（內部測試）
git tag -a v5.0.0-alpha.1 -m "Alpha release for internal testing"

# Beta 版本（公開測試）
git tag -a v5.0.0-beta.1 -m "Beta release for public testing"

# RC 版本（發布候選）
git tag -a v5.0.0-rc.1 -m "Release candidate 1"

# 正式版本
git tag -a v5.0.0 -m "Official release"
```

### Q4: 如何回退版本？

```bash
# 回退到上一個 tag
git checkout v4.2.5

# 創建修復分支
git checkout -b hotfix/v4.2.6

# 修復後創建新 tag
git tag -a v4.2.6 -m "Hotfix: ..."
```

### Q5: CI/CD 如何自動讀取版本號？

**GitHub Actions 範例**:
```yaml
# .github/workflows/build.yml
name: Build
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Get version
        id: version
        run: |
          VERSION=$(yq eval '.version' machinenativeops.yaml)
          echo "version=$VERSION" >> $GITHUB_OUTPUT
      
      - name: Build
        run: |
          echo "Building version ${{ steps.version.outputs.version }}"
          npm run build
```

### Q6: 忘記創建 Git tag 怎麼辦？

```bash
# 找到對應的提交 SHA
git log --oneline

# 為舊提交創建 tag
git tag -a v5.0.0 <commit-sha> -m "Release v5.0.0 (retroactive)"

# 推送 tag
git push origin v5.0.0
```

---

## 🔗 相關資源

### 內部文檔

- [架構重構計劃](./ARCHITECTURE_RESTRUCTURING_PLAN.md)
- [遷移指南](./MIGRATION_GUIDE.md)
- [貢獻指南](../CONTRIBUTING.md)
- [變更日誌](../CHANGELOG.md)

### 外部標準

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Git Tagging](https://git-scm.com/book/en/v2/Git-Basics-Tagging)

### 自動化工具

- [yq](https://github.com/mikefarah/yq) - YAML processor
- [jq](https://stedolan.github.io/jq/) - JSON processor
- [npm version](https://docs.npmjs.com/cli/v9/commands/npm-version) - NPM 版本管理
- [standard-version](https://github.com/conventional-changelog/standard-version) - 自動化版本與 CHANGELOG

---

**文件維護**: 本文件為長期有效的版本管理標準。  
**最後更新**: 2025-12-17  
**版本**: 1.0.0  
**狀態**: ✅ APPROVED - Production Standard
