# 🔄 MachineNativeOps 架構重構遷移指南

> **文件版本**: 1.0.0  
> **建立日期**: 2025-12-17  
> **目標受眾**: 所有開發者、貢獻者、CI/CD 維護者  
> **狀態**: 📝 DRAFT - 隨重構進度更新

---

## 📋 目錄

1. [遷移概述](#-遷移概述)
2. [影響範圍](#-影響範圍)
3. [開發者行動項](#-開發者行動項)
4. [路徑映射表](#-路徑映射表)
5. [常見問題](#-常見問題)
6. [支援資源](#-支援資源)

---

## 🎯 遷移概述

### 為什麼要遷移？

MachineNativeOps 專案當前面臨嚴重的架構混亂問題：

- **52+ 個頂層目錄** - 導航困難，認知負荷高
- **命名不一致** - PascalCase、kebab-case、同義詞混用
- **重複目錄** - infra/infrastructure, deployment/deploy, script/scripts
- **配置分散** - .config/, config/, .devcontainer/

本次遷移將建立清晰的 `src/` 主目錄結構，統一配置管理，標準化命名規範。

### 遷移目標

```
從：52+ 個頂層目錄，混亂的命名
到：清晰的 src/ + config/ + scripts/ 三層結構
```

### 時間表

| 階段 | 時間 | 狀態 |
|------|------|------|
| **Phase 0: 準備** | 2 天 | 🔄 In Progress |
| **Phase 1: 文檔更新** | 2-3 天 | 🔄 In Progress |
| **Phase 2: 目錄遷移** | 3-5 天 | ⏳ Pending |
| **Phase 3: 引用更新** | 2-3 天 | ⏳ Pending |
| **Phase 4: 測試驗證** | 2-3 天 | ⏳ Pending |
| **Phase 5: 發布** | 1-2 天 | ⏳ Pending |

**預計完成日期**: 2025-12-28

---

## 📍 影響範圍

### 會被移動的目錄

#### 核心子系統

| 當前位置 | 新位置 | 說明 |
|---------|--------|------|
| `core/` | `src/core/` | SynergyMesh 核心引擎 |
| `governance/` | `src/governance/` | 結構治理系統 |
| `autonomous/` | `src/autonomous/core/` | 自主系統核心 |

#### 需要合併的重複目錄

| 當前位置 | 新位置 | 說明 |
|---------|--------|------|
| `infra/` + `infrastructure/` | `src/autonomous/infrastructure/` | 基礎設施（合併） |
| `deployment/` + `deploy/` | `src/autonomous/deployment/` | 部署配置（合併） |
| `script/` + `scripts/` | `scripts/` | 腳本（合併） |
| `ai/` + `island-ai/` | `src/ai/` | AI 系統（合併） |
| `agent/` | `src/ai/agents/` | 智能代理 |
| `automation/` | `src/autonomous/automation/` | 自動化系統 |

#### 配置與腳本

| 當前位置 | 新位置 | 說明 |
|---------|--------|------|
| `.devcontainer/` | `config/dev/devcontainer/` | 開發容器配置 |
| `.config/` | `config/dev/` | 開發工具配置 |
| `.vscode/settings.json` | `config/dev/vscode-settings.json` | VSCode 配置 |
| 分散的腳本 | `scripts/{dev,ci,ops}/` | 腳本分類整理 |

### 不會被移動的目錄

以下目錄保持原位：

- ✅ `.github/` - GitHub 配置與 workflows
- ✅ `docs/` - 文檔（僅更新路徑引用）
- ✅ `tests/` - 測試套件（僅更新路徑引用）
- ✅ `examples/` - 範例代碼
- ✅ `tools/` - 開發工具
- ✅ `machinenativeops.yaml` - 主配置文件
- ✅ `package.json`, `tsconfig.json` 等根目錄配置文件

---

## 👨‍💻 開發者行動項

### ⚠️ 重要：在遷移完成前

1. **暫停合併新功能 PR**
   - 從 [日期 TBD] 起，只接受 bugfix 和文檔更新
   - 所有待審查的功能 PR 建議暫緩合併

2. **備份本地工作**

   ```bash
   # 提交所有未提交的更改
   git add .
   git commit -m "WIP: Backup before restructuring"
   
   # 推送到您的分支
   git push origin your-branch
   ```

3. **保持關注**
   - 加入 Slack 頻道: `#architecture-restructuring`
   - 關注 GitHub Issue: `#TBD`

### ✅ 遷移完成後需要做什麼

#### 步驟 1: 拉取最新代碼

```bash
# 切換到 main 分支
git checkout main

# 拉取最新代碼（包含重構後的結構）
git pull origin main

# 查看新的目錄結構
tree -L 2 -d
```

#### 步驟 2: 更新您的分支

如果您有正在進行中的分支：

```bash
# 切換到您的分支
git checkout your-feature-branch

# Rebase 到最新的 main
git rebase main

# 解決衝突（主要是路徑變更）
# 使用下方的路徑映射表更新引用
```

#### 步驟 3: 更新 Import 路徑

**TypeScript/JavaScript**:

```typescript
// ❌ 舊路徑
import { CoreEngine } from 'core/engine';
import { PolicyValidator } from 'governance/validator';

// ✅ 新路徑
import { CoreEngine } from 'src/core/engine';
import { PolicyValidator } from 'src/governance/validator';
```

**Python**:

```python
# ❌ 舊路徑
from core.engine import CoreEngine
from governance.validator import PolicyValidator

# ✅ 新路徑
from src.core.engine import CoreEngine
from src.governance.validator import PolicyValidator
```

**自動化工具**:

```bash
# 使用我們提供的遷移腳本
bash scripts/migration/update-my-branch.sh

# 或手動全局替換
find . -name "*.ts" -o -name "*.tsx" | xargs sed -i \
  -e 's|from ["'\'']\.\./\.\./core/|from "src/core/|g' \
  -e 's|from ["'\'']core/|from "src/core/|g'
```

#### 步驟 4: 更新配置文件路徑

如果您的代碼引用了配置文件路徑：

```typescript
// ❌ 舊路徑
const config = readConfig('.devcontainer/devcontainer.json');

// ✅ 新路徑
const config = readConfig('config/dev/devcontainer/devcontainer.json');
```

#### 步驟 5: 運行測試

```bash
# 安裝依賴（可能有 workspace 變更）
npm install

# 運行 linter
npm run lint

# 運行測試
npm test

# 構建專案
npm run build
```

#### 步驟 6: 提交更新

```bash
# 查看更改
git status
git diff

# 提交路徑更新
git add .
git commit -m "chore: Update paths after architecture restructuring"

# 推送
git push origin your-feature-branch
```

---

## 🗺️ 路徑映射表

### 完整映射表

| 舊路徑 | 新路徑 | 類型 | 說明 |
|--------|--------|------|------|
| `core/` | `src/core/` | Move | SynergyMesh 核心引擎 |
| `core/unified_integration/` | `src/core/unified-integration/` | Move + Rename | 統一整合層 |
| `core/mind_matrix/` | `src/core/mind-matrix/` | Move + Rename | 心智矩陣 |
| `core/safety_mechanisms/` | `src/core/safety-mechanisms/` | Move + Rename | 安全機制 |
| `core/slsa_provenance/` | `src/core/slsa-provenance/` | Move + Rename | SLSA 溯源 |
| `core/contract_service/` | `src/core/contract-service/` | Move + Rename | 合約服務 |
| `governance/` | `src/governance/` | Move | 結構治理系統 |
| `autonomous/` | `src/autonomous/core/` | Move | 自主系統核心 |
| `deployment/` | `src/autonomous/deployment/` | Move | 部署配置 |
| `deploy/` | `src/autonomous/deployment/k8s/` | Move + Merge | K8s 部署 |
| `infra/` | `src/autonomous/infrastructure/` | Move + Merge | 基礎設施 (1) |
| `infrastructure/` | `src/autonomous/infrastructure/` | Move + Merge | 基礎設施 (2) |
| `automation/` | `src/autonomous/automation/` | Move | 自動化系統 |
| `ai/` | `src/ai/` | Move + Merge | AI 系統 (1) |
| `island-ai/` | `src/ai/island-core/` | Move + Merge | Island AI 核心 (2) |
| `agent/` | `src/ai/agents/` | Move | 智能代理 |
| `mcp-servers/` | `src/services/mcp-servers/` | Move | MCP 伺服器 |
| `services/` | `src/services/` | Move | 其他服務 |
| `web/` | `src/apps/web/` | Move | Web 應用 |
| `frontend/` | `src/apps/web/` | Move + Merge | 前端（合併到 web） |
| `client/` | `src/apps/client/` | Move | 客戶端應用 |
| `server/` | `src/apps/server/` | Move | 伺服器應用 |
| `shared/` | `src/shared/` | Move | 共享代碼庫 |
| `.devcontainer/` | `config/dev/devcontainer/` | Move | 開發容器配置 |
| `.config/` | `config/dev/` | Move | 開發工具配置 |
| `.vscode/settings.json` | `config/dev/vscode-settings.json` | Move | VSCode 配置 |
| `script/` | `scripts/` | Move + Merge | 腳本（合併到 scripts/） |
| `NamespaceTutorial/` | `docs/tutorials/namespace/` | Move + Rename | 命名空間教程 |
| `v1-python-drones/` | `legacy/python-drones-v1/` | Move | 舊版 Python Drones |
| `v2-multi-islands/` | `legacy/multi-islands-v2/` | Move | 舊版 Multi-Islands |

### 配置文件引用更新

| 文件 | 需要更新的路徑 |
|------|---------------|
| `machinenativeops.yaml` | ✅ 已自動更新 |
| `package.json` | `workspaces` 欄位 |
| `tsconfig.json` | `paths` 欄位 |
| `.github/workflows/*.yml` | 腳本路徑、構建路徑 |
| `docker-compose.yml` | 卷掛載路徑 |
| `Dockerfile` | `COPY` 指令路徑 |

---

## ❓ 常見問題

### Q1: 我的 PR 還沒合併，怎麼辦？

**A**:

- 如果是功能 PR，建議等待重構完成後 rebase 到新結構
- 如果是 bugfix，可以照常合併，我們會處理路徑衝突
- 如果急需合併，請在 PR 中添加標籤 `pre-restructuring`

### Q2: 重構期間發現緊急 bug 怎麼辦？

**A**:

- 緊急 bugfix 不受功能凍結限制
- 在當前結構上修復並合併
- 我們會在遷移腳本中處理這些變更

### Q3: 我的本地分支有很多未提交的更改？

**A**:

```bash
# 選項 1: 提交到臨時分支
git checkout -b backup/my-work
git add .
git commit -m "WIP: Backup before restructuring"
git push origin backup/my-work

# 選項 2: 使用 stash
git stash push -m "Work before restructuring"
# 重構完成後
git stash pop
```

### Q4: TypeScript 編譯錯誤怎麼辦？

**A**:

```bash
# 清除舊的構建緩存
rm -rf dist/ build/ *.tsbuildinfo

# 重新安裝依賴
rm -rf node_modules/
npm install

# 重新構建
npm run build
```

### Q5: CI/CD 失敗怎麼辦？

**A**:

- 檢查 GitHub Actions workflow 是否已更新腳本路徑
- 參考 `.github/workflows/` 下的更新模板
- 如仍失敗，請在 `#architecture-restructuring` 頻道求助

### Q6: 我可以繼續使用舊路徑嗎？

**A**:

- ❌ 不可以。舊路徑在遷移後將不存在
- 所有代碼必須更新到新路徑
- 我們提供自動化腳本協助遷移

### Q7: 重構後性能會受影響嗎？

**A**:

- ✅ 不會。這是純粹的目錄重組，不影響運行時性能
- ✅ 反而可能提升構建速度（更好的 webpack/tsconfig 緩存）

### Q8: 如何驗證我的更改是否正確？

**A**:

```bash
# 運行完整驗證套件
npm run verify-structure  # 驗證目錄結構
npm run lint              # 代碼風格檢查
npm test                  # 單元測試
npm run build             # 構建測試
```

---

## 📞 支援資源

### 文檔

- 📖 [架構重構計劃](./ARCHITECTURE_RESTRUCTURING_PLAN.md) - 完整重構方案
- 📋 [貢獻指南](../CONTRIBUTING.md) - 新的目錄結構規範
- 🏗️ [README 專案結構章節](../README.md#-專案結構--project-structure) - 新結構概覽

### 自動化工具

```bash
# 更新您的分支路徑
scripts/migration/update-my-branch.sh

# 驗證路徑更新是否完整
scripts/migration/verify-refs.sh

# 驗證目錄結構是否正確
scripts/migration/verify-structure.sh
```

### 溝通頻道

- 💬 **Slack**: `#architecture-restructuring`
- 🐛 **GitHub Issue**: `#TBD` (重構追蹤 issue)
- 📧 **Email**: <team@machinenativeops.io>
- 📅 **團隊會議**: [日期 TBD] - 重構說明會

### 聯絡人

- **技術負責人**: [指定負責人]
- **遷移腳本支援**: [指定負責人]
- **CI/CD 支援**: [指定負責人]

---

## 🎯 檢查清單

在開始工作前，請確認：

- [ ] 我已閱讀本遷移指南
- [ ] 我已備份我的本地工作
- [ ] 我已加入 Slack `#architecture-restructuring` 頻道
- [ ] 我了解哪些目錄會被移動

遷移完成後，請確認：

- [ ] 我已拉取最新的 main 分支
- [ ] 我已更新我的分支到新結構
- [ ] 我已更新所有 import 路徑
- [ ] 我已更新配置文件路徑引用
- [ ] 我已運行 linter 並通過
- [ ] 我已運行測試並通過
- [ ] 我已成功構建專案

---

**文件維護**: 本文件將隨重構進度持續更新。  
**最後更新**: 2025-12-17  
**版本**: 1.0.0  
**狀態**: 📝 DRAFT - 隨重構進度更新
