# Multi-Repository Integration Guide | 多倉庫整合指南

**問題**: 如何將近100個儲存庫集成到 keystone-ai？
**GitHub 限制**: 一個倉庫不能直接嵌入另一個環境（submodule 有諸多限制）

---

## 🎯 解決方案對比表

| 方案 | 優點 | 缺點 | 適用場景 | 難度 |
|------|------|------|----------|------|
| **1. Git Subtree** | ✅ 單一倉庫<br>✅ 無需額外依賴<br>✅ 保留歷史 | ⚠️ 初次設置複雜<br>⚠️ 更新需手動 | 將外部代碼永久集成 | ⭐⭐ |
| **2. 自動同步腳本** | ✅ 靈活控制<br>✅ 可選擇性同步<br>✅ 易於理解 | ⚠️ 不保留歷史<br>⚠️ 需要維護腳本 | 定期從其他 repo 拉取代碼 | ⭐ |
| **3. Monorepo 工具** | ✅ 專業工具支持<br>✅ 統一管理<br>✅ 構建優化 | ⚠️ 學習曲線<br>⚠️ 需要重構 | 從零開始的 monorepo | ⭐⭐⭐ |
| **4. Git Remote 多源** | ✅ 保留所有歷史<br>✅ 靈活合併 | ⚠️ 手動操作多<br>⚠️ 衝突處理 | 少量倉庫整合 | ⭐⭐ |
| **5. 包管理器** | ✅ 版本控制<br>✅ 依賴管理 | ⚠️ 需要發布流程<br>⚠️ 不適合源碼整合 | 作為依賴引用 | ⭐⭐⭐ |

---

## ✅ 方案 1: Git Subtree (最推薦)

**適合你的場景**: 將其他倉庫的代碼完全集成到 keystone-ai

### 原理
- 將外部倉庫的代碼複製到子目錄
- 保留完整的 git 歷史
- 不需要 `.gitmodules`（比 submodule 更簡單）

### 實現步驟

```bash
# 1. 添加遠程倉庫
git remote add repo1 https://github.com/your-org/repo1.git
git remote add repo2 https://github.com/your-org/repo2.git

# 2. 拉取並合併到子目錄
git subtree add --prefix=external/repo1 repo1 main --squash
git subtree add --prefix=external/repo2 repo2 main --squash

# 3. 後續更新（從源倉庫拉取最新代碼）
git subtree pull --prefix=external/repo1 repo1 main --squash

# 4. 推送回源倉庫（可選，如果需要反向同步）
git subtree push --prefix=external/repo1 repo1 main
```

### 目錄結構示例

```
keystone-ai/
├── core/                    # 核心代碼
├── external/                # 從其他倉庫集成的代碼
│   ├── repo1/              # 來自 repo1
│   ├── repo2/              # 來自 repo2
│   ├── legacy-system/      # 來自 legacy 倉庫
│   └── ...
├── services/
└── tools/
```

### 批量添加腳本

創建 `tools/integrate_repositories.sh`:

```bash
#!/bin/bash
# 批量集成多個倉庫

REPOS=(
    "repo1:https://github.com/your-org/repo1.git:main"
    "repo2:https://github.com/your-org/repo2.git:main"
    "repo3:https://github.com/your-org/repo3.git:main"
    # ... 添加所有100個倉庫
)

for repo_info in "${REPOS[@]}"; do
    IFS=':' read -r name url branch <<< "$repo_info"

    echo "🔄 Integrating $name..."

    # 添加遠程
    git remote add "$name" "$url" 2>/dev/null || echo "Remote $name already exists"

    # Fetch 遠程代碼
    git fetch "$name"

    # Subtree 添加
    git subtree add --prefix="external/$name" "$name" "$branch" --squash

    echo "✅ $name integrated"
done
```

---

## ✅ 方案 2: 自動同步腳本 (最簡單)

**適合你的場景**: 定期從其他倉庫拉取最新代碼，不需要保留歷史

### 實現工具

創建 `tools/sync_external_repos.py`:

```python
#!/usr/bin/env python3
"""
自動同步外部倉庫到 keystone-ai
"""

import subprocess
import shutil
from pathlib import Path
import yaml

def sync_repo(repo_config: dict):
    """同步單個倉庫"""
    name = repo_config['name']
    url = repo_config['url']
    branch = repo_config.get('branch', 'main')
    target_dir = Path('external') / name

    print(f"🔄 Syncing {name}...")

    # 臨時克隆目錄
    temp_dir = Path(f'/tmp/keystone_sync_{name}')

    try:
        # 克隆或更新
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

        subprocess.run([
            'git', 'clone', '--depth=1', '--branch', branch, url, str(temp_dir)
        ], check=True, capture_output=True)

        # 移除 .git 目錄
        shutil.rmtree(temp_dir / '.git')

        # 複製到目標目錄
        if target_dir.exists():
            shutil.rmtree(target_dir)

        shutil.copytree(temp_dir, target_dir)

        print(f"✅ {name} synced successfully")

        # 清理臨時目錄
        shutil.rmtree(temp_dir)

        return True
    except Exception as e:
        print(f"❌ Failed to sync {name}: {e}")
        return False

def main():
    """主函數"""
    # 從配置文件讀取倉庫列表
    config_file = Path('config/external_repos.yaml')

    if not config_file.exists():
        print("❌ Config file not found: config/external_repos.yaml")
        return

    with open(config_file) as f:
        config = yaml.safe_load(f)

    repos = config.get('repositories', [])

    print(f"📦 Found {len(repos)} repositories to sync")

    # 創建 external 目錄
    Path('external').mkdir(exist_ok=True)

    # 同步所有倉庫
    success_count = 0
    for repo in repos:
        if sync_repo(repo):
            success_count += 1

    print(f"\n✅ Synced {success_count}/{len(repos)} repositories")

if __name__ == '__main__':
    main()
```

### 配置文件

創建 `config/external_repos.yaml`:

```yaml
# 外部倉庫配置
repositories:
  - name: repo1
    url: https://github.com/your-org/repo1.git
    branch: main
    description: "Repo 1 description"

  - name: repo2
    url: https://github.com/your-org/repo2.git
    branch: main
    description: "Repo 2 description"

  - name: legacy-system
    url: https://github.com/your-org/legacy-system.git
    branch: master
    description: "Legacy system code"

  # ... 添加所有100個倉庫

# 同步選項
sync_options:
  preserve_git_history: false
  exclude_patterns:
    - "*.pyc"
    - "__pycache__"
    - "node_modules"
    - ".git"
```

### 使用方法

```bash
# 1. 首次同步所有倉庫
python tools/sync_external_repos.py

# 2. 定期更新（加入 crontab）
0 2 * * * cd /path/to/keystone-ai && python tools/sync_external_repos.py

# 3. Git 提交集成的代碼
git add external/
git commit -m "chore: sync external repositories"
git push
```

---

## ✅ 方案 3: Git Remote 多源合併

**適合你的場景**: 少量倉庫（<10個）需要保留完整歷史

### 實現步驟

```bash
# 1. 為每個外部倉庫添加 remote
git remote add external-repo1 https://github.com/your-org/repo1.git

# 2. Fetch 代碼
git fetch external-repo1

# 3. 創建新分支用於整合
git checkout -b integrate-repo1

# 4. 合併外部倉庫到子目錄
git merge -s ours --no-commit --allow-unrelated-histories external-repo1/main
git read-tree --prefix=external/repo1/ -u external-repo1/main
git commit -m "feat: integrate repo1 into external/repo1"

# 5. 合併回主分支
git checkout main
git merge integrate-repo1

# 6. 清理
git branch -d integrate-repo1
```

---

## ✅ 方案 4: Monorepo 工具整合

**適合你的場景**: 長期維護，需要專業工具支持

### 推薦工具

1. **Turborepo** (JavaScript/TypeScript)
2. **Nx** (多語言支持)
3. **Bazel** (大型項目)
4. **Lerna** (JavaScript)

### Nx 示例

```bash
# 1. 初始化 Nx workspace
npx create-nx-workspace@latest keystone-ai --preset=empty

# 2. 遷移現有倉庫
nx g @nrwl/workspace:move-project --project=old-repo1 --destination=apps/repo1

# 3. 配置
# nx.json, workspace.json 會自動管理依賴關係
```

---

## 🚀 推薦方案：混合策略

基於你的需求（100個倉庫），建議使用**分層整合策略**：

### 第一層：核心整合 (Git Subtree)
將**關鍵的10-20個倉庫**使用 Git Subtree 完全集成：

```bash
# 核心倉庫列表
CORE_REPOS=(
    "core-engine"
    "authentication-service"
    "data-pipeline"
    # ... 10-20個核心倉庫
)

# 使用 subtree 完全集成
for repo in "${CORE_REPOS[@]}"; do
    git subtree add --prefix="core/$repo" \
        "https://github.com/your-org/$repo.git" main --squash
done
```

### 第二層：服務集成 (自動同步)
將**剩餘80-90個倉庫**使用自動同步腳本：

```bash
# 定期同步
python tools/sync_external_repos.py
```

### 第三層：包引用 (可選)
將**穩定不變的倉庫**發布為 npm/pip 包：

```json
// package.json
{
  "dependencies": {
    "@your-org/stable-lib1": "^1.0.0",
    "@your-org/stable-lib2": "^2.3.0"
  }
}
```

---

## 🛠️ 完整實現：一鍵整合工具

創建 `tools/integrate_all_repos.sh`:

```bash
#!/bin/bash
#═══════════════════════════════════════════════════════════════
#  Multi-Repository Integration Tool
#  多倉庫一鍵整合工具
#═══════════════════════════════════════════════════════════════

set -euo pipefail

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
CONFIG_FILE="$REPO_ROOT/config/external_repos.yaml"

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}✅ $*${NC}"; }
log_warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }
log_error() { echo -e "${RED}❌ $*${NC}"; }

# 模式選擇
MODE=${1:-"sync"}  # sync | subtree | hybrid

case $MODE in
    sync)
        log_info "Using SYNC mode (simple copy)"
        python3 tools/sync_external_repos.py
        ;;

    subtree)
        log_info "Using SUBTREE mode (full git history)"

        # 讀取配置並執行 subtree add
        # （需要配合 Python 腳本解析 YAML）
        python3 tools/subtree_integrate.py
        ;;

    hybrid)
        log_info "Using HYBRID mode (core + sync)"

        # 1. 核心倉庫用 subtree
        log_info "Integrating core repositories with subtree..."
        python3 tools/subtree_integrate.py --core-only

        # 2. 其餘用 sync
        log_info "Syncing remaining repositories..."
        python3 tools/sync_external_repos.py --exclude-core
        ;;

    *)
        log_error "Unknown mode: $MODE"
        echo "Usage: $0 [sync|subtree|hybrid]"
        exit 1
        ;;
esac

log_info "Integration complete!"
log_info "Review changes with: git status"
log_info "Commit with: git add external/ && git commit -m 'chore: integrate external repos'"
```

---

## 📋 配置示例：100個倉庫

`config/external_repos.yaml`:

```yaml
# 核心倉庫 (使用 subtree 完全整合)
core_repositories:
  - name: authentication-service
    url: https://github.com/keystone-api/auth-service.git
    branch: main
    priority: high

  - name: data-pipeline
    url: https://github.com/keystone-api/data-pipeline.git
    branch: main
    priority: high

  # ... 10-20個核心倉庫

# 普通倉庫 (使用 sync 定期同步)
sync_repositories:
  - name: legacy-system-1
    url: https://github.com/keystone-api/legacy-1.git
    branch: master
    priority: medium

  - name: legacy-system-2
    url: https://github.com/keystone-api/legacy-2.git
    branch: master
    priority: medium

  # ... 80-90個倉庫

# 同步配置
sync_options:
  schedule: "0 2 * * *"  # 每天凌晨2點
  exclude_patterns:
    - "*.pyc"
    - "__pycache__"
    - "node_modules"
    - ".git"
    - ".env"

  # 選擇性同步（只同步特定目錄）
  include_paths:
    - "src/"
    - "lib/"
    - "config/"
```

---

## 🔄 CI/CD 自動化

`.github/workflows/sync-external-repos.yml`:

```yaml
name: Sync External Repositories

on:
  schedule:
    - cron: '0 2 * * *'  # 每天凌晨2點
  workflow_dispatch:      # 手動觸發

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install pyyaml

      - name: Sync repositories
        run: python tools/sync_external_repos.py

      - name: Commit changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add external/
          git commit -m "chore: auto-sync external repositories" || exit 0
          git push
```

---

## 📊 方案選擇決策樹

```
有近100個倉庫需要整合
    │
    ├─ 需要完整 git 歷史？
    │   ├─ 是 → Git Subtree (10-20個核心)
    │   └─ 否 → 自動同步腳本 (80-90個普通)
    │
    ├─ 代碼會頻繁更新？
    │   ├─ 是 → 自動同步 + CI/CD
    │   └─ 否 → 一次性 Subtree
    │
    └─ 需要雙向同步？
        ├─ 是 → Git Subtree (支持 push 回源)
        └─ 否 → 自動同步 (單向拉取)
```

---

## ✅ 最終推薦

### 針對你的場景（100個倉庫）：

**混合策略 = Git Subtree (核心) + 自動同步 (其他)**

1. **10-20個核心倉庫** → `git subtree` 完全集成
2. **80-90個普通倉庫** → `sync_external_repos.py` 定期同步
3. **穩定庫** → 發布為包，通過包管理器引用

### 立即行動

```bash
# 1. 創建配置
cp config/external_repos.yaml.example config/external_repos.yaml
# 編輯並填入你的100個倉庫

# 2. 首次整合
./tools/integrate_all_repos.sh hybrid

# 3. 審查並提交
git status
git add external/
git commit -m "feat: integrate 100 external repositories"
git push

# 4. 設置自動同步
# 配置 GitHub Actions (見上面的 workflow)
```

---

**下一步**: 我可以立即為你創建這些工具嗎？
