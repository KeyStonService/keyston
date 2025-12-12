# Refactor Playbook Configuration Integration Guide

# 重構劇本配置整合指南

**Date:** 2025-12-06  
**Purpose:** 說明如何使用既有配置系統進行重構路徑決策  
**Status:** ✅ Active

---

## 📋 概述

重構劇本系統完全整合到既有的 `config/system-module-map.yaml` 和
`config/unified-config-index.yaml`
中，**不新增額外的配置檔案**。所有路徑決策和權限管理都通過現有配置系統進行。

---

## 🎯 核心原則

### 1. 路徑決策權集中管理

```
所有重構操作的路徑決策 → config/system-module-map.yaml
所有文檔索引和發現 → config/unified-config-index.yaml
```

**禁止**：

- ❌ 直接掃描整個專案寫檔案
- ❌ 在劇本中硬編碼路徑
- ❌ 創建新的根目錄
- ❌ 繞過 module map 定義的邊界

**允許**：

- ✅ 通過 cluster_id 查詢 module map
- ✅ 只在 target_roots 定義的目錄中操作
- ✅ 遵守 allow_new_subdirs 設定
- ✅ 使用 owners 定義的審查流程

### 2. 預設禁止新建目錄

除非 module 明確設置
`allow_new_subdirs: true`，否則所有重構都只能在現有目錄中進行。

---

## 🔧 使用方式

### For Auto-Fix Bots / CI Tools

**步驟 1：從劇本獲取 cluster_id**

```bash
# 從 refactor playbook 的 front-matter 讀取
cluster_id=$(grep "cluster_id:" core__architecture_refactor.md | cut -d'"' -f2)
# Output: core/architecture-stability
```

**步驟 2：查詢 module map 獲取合法路徑**

```python
import yaml

# 載入 module map
with open('config/system-module-map.yaml', 'r') as f:
    module_map = yaml.safe_load(f)

# 查詢 cluster_id 對應的 refactor 設定
def find_refactor_config(cluster_id, module_map):
    for category in module_map['directory_categories'].values():
        for module in category.get('modules', {}).values():
            if 'refactor' in module and module['refactor']['cluster_id'] == cluster_id:
                return module['refactor']
    return None

refactor_config = find_refactor_config('core/architecture-stability', module_map)
```

**步驟 3：驗證操作合法性**

```python
def validate_refactor_operation(file_path, refactor_config):
    """驗證重構操作是否在允許的路徑範圍內"""

    # 檢查是否在 target_roots 內
    in_target = any(
        file_path.startswith(root)
        for root in refactor_config['target_roots']
    )

    if not in_target:
        raise ValueError(f"File {file_path} not in target_roots")

    # 檢查是否被排除
    for exclude in refactor_config.get('exclude_globs', []):
        if fnmatch.fnmatch(file_path, exclude):
            raise ValueError(f"File {file_path} matches exclude pattern")

    # 如果是新目錄，檢查是否允許
    if is_new_directory(file_path):
        if not refactor_config.get('allow_new_subdirs', False):
            raise ValueError(f"New subdirectories not allowed in this module")

    return True
```

**步驟 4：執行操作並標記 owners**

```python
def create_refactor_pr(changes, refactor_config):
    """創建重構 PR 並自動分配審查者"""

    # 從 config 獲取 owners
    reviewers = refactor_config.get('owners', [])

    # 創建 PR
    pr = github.create_pull_request(
        title=f"Refactor: {refactor_config['cluster_id']}",
        body=f"Automated refactor following playbook for {refactor_config['cluster_id']}",
        reviewers=reviewers
    )

    return pr
```

### For LLM / AI Agents

**System Prompt 範例**：

```markdown
# 重構路徑決策規則

你是一個專業的重構工程師。在執行任何重構操作前，你必須遵守以下規則：

## 路徑查詢流程

1. 從重構劇本的 front-matter 讀取 `cluster_id`
2. 在 `config/system-module-map.yaml` 中查找對應的 `refactor` 配置
3. 只在 `target_roots` 定義的目錄中進行修改
4. 遵守 `allow_new_subdirs` 的設定
5. 不修改 `exclude_globs` 匹配的檔案

## 絕對禁止的操作

- 在未定義 refactor 配置的目錄中修改檔案
- 創建新的根目錄
- 繞過 module map 直接決定路徑
- 在 allow_new_subdirs: false 的模組中創建新子目錄

## 範例

假設你要重構 `core/architecture-stability` cluster：

1. 讀取劇本獲取 cluster_id: "core/architecture-stability"
2. 查詢 system-module-map.yaml 找到對應的 refactor 配置
3. 確認 target_roots 包含: ["core/unified_integration/", "core/mind_matrix/"]
4. 確認 allow_new_subdirs: false
5. 只在這兩個目錄中修改現有檔案，不創建新目錄
```

**User Prompt 範例**：

```markdown
請為 `core/architecture-stability` cluster 執行重構：

1. 從 `config/system-module-map.yaml` 讀取該 cluster 的 refactor 配置
2. 列出允許修改的目錄 (target_roots)
3. 確認是否可以創建新子目錄 (allow_new_subdirs)
4. 只在允許的路徑範圍內進行重構
5. 列出需要審查的團隊 (owners)
```

### For Human Engineers

**快速參考**：

```bash
# 查看某個 cluster 的重構配置
yq '.directory_categories.core_platform.modules.unified_integration.refactor' \
   config/system-module-map.yaml

# 查看所有 refactor playbooks
yq '.config_file_index.refactor_playbooks' \
   config/unified-config-index.yaml

# 驗證路徑是否在允許範圍內
python3 tools/validate-refactor-index.py
```

---

## 📖 配置結構說明

### system-module-map.yaml 中的 refactor 區塊

```yaml
module_name:
  path: 'path/to/module/'
  description: '模組說明'
  provides: ['Capability1', 'Capability2']

  refactor: # 重構治理設定
    cluster_id: 'domain/cluster-name' # 對應的 cluster ID (必填)
    target_roots: # 允許修改的目錄列表 (必填)
      - 'path/to/dir1/'
      - 'path/to/dir2/'
    allow_new_subdirs: false # 是否允許創建新子目錄 (預設: false)
    allowed_new_paths: # 如果 allow_new_subdirs: true，可指定模式
      - 'path/to/dir/new-*/'
    include_globs: # 包含的檔案模式
      - 'path/**/*.ts'
      - 'path/**/*.py'
    exclude_globs: # 排除的檔案模式
      - '**/tests/**'
      - '**/__pycache__/**'
      - '**/node_modules/**'
    owners: # 審查者團隊
      - '@team-name'

    # 架構約束 (從 architecture skeletons)
    architecture_constraints:
      allowed_dependencies: # 允許的依賴模式
        - 'core/*'
        - 'runtime/*'
      banned_dependencies: # 禁止的依賴模式
        - 'apps/**'
      dependency_direction: 'downstream_only'
      skeleton_rules: # 必須遵守的骨架規則
        - 'architecture-stability'
        - 'api-governance'

    # 語言策略
    preferred_languages: # 優先使用的語言
      - 'typescript'
      - 'python'
    banned_languages: # 禁止的語言
      - 'php'
      - 'perl'

    # 品質指標閾值
    quality_thresholds:
      language_violations_max: 5 # 最大語言違規數
      semgrep_high_max: 0 # 最大 HIGH severity 數
      semgrep_medium_max: 3 # 最大 MEDIUM severity 數
      cyclomatic_complexity_max: 15 # 最大複雜度
      test_coverage_min: 75 # 最小測試覆蓋率 (%)
```

### unified-config-index.yaml 中的 refactor_playbooks 區塊

```yaml
refactor_playbooks:
  - id: 'refactor-03-domain-name' # 唯一識別碼
    file: 'path/to/playbook.md' # 劇本檔案路徑
    domain: 'domain' # 系統領域
    cluster_id: 'domain/cluster' # Cluster ID
    module_id: 'module_name' # 對應的 module (在 module map 中)
    type: 'refactor-playbook' # 文件類型
    status: 'draft' # 狀態
    references: # 相關引用
      module_map: 'config/system-module-map.yaml#path.to.refactor'
```

---

## 🎯 實際範例

### 範例 1：Core Architecture 重構

**劇本**:
`docs/refactor_playbooks/03_refactor/core/core__architecture_refactor.md`

```yaml
---
cluster_id: 'core/architecture-stability'
module_id: 'unified_integration'
---
```

**Module Map 配置**:

```yaml
core_platform:
  modules:
    unified_integration:
      refactor:
        cluster_id: 'core/architecture-stability'
        target_roots:
          - 'core/unified_integration/'
          - 'core/mind_matrix/'
        allow_new_subdirs: false
        owners:
          - '@core-owners'
```

**結果**：

- ✅ 可以修改 `core/unified_integration/` 和 `core/mind_matrix/` 中的現有檔案
- ❌ 不能在這些目錄下創建新子目錄
- ✅ PR 會自動指派給 `@core-owners` 審查

### 範例 2：Automation Autonomous 重構

**劇本**:
`docs/refactor_playbooks/03_refactor/automation/automation__autonomous_refactor.md`

```yaml
---
cluster_id: 'automation/autonomous'
module_id: 'autonomous_system'
---
```

**Module Map 配置**:

```yaml
automation:
  modules:
    autonomous_system:
      refactor:
        cluster_id: 'automation/autonomous'
        target_roots:
          - 'automation/autonomous/'
        allow_new_subdirs: false
        owners:
          - '@automation-team'
```

**結果**：

- ✅ 可以修改 `automation/autonomous/` 中的現有檔案
- ❌ 不能創建新子目錄
- ✅ PR 會自動指派給 `@automation-team` 審查

---

## 🚀 工具整合建議

### CI Workflow 整合

```yaml
# .github/workflows/refactor-validation.yml
name: Validate Refactor Operations

on:
  pull_request:
    paths:
      - 'core/**'
      - 'automation/**'
      - 'services/**'

jobs:
  validate-refactor-paths:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: pip install pyyaml

      - name: Validate refactor paths
        run: |
          python3 tools/validate-refactor-paths.py \
            --changes ${{ github.event.pull_request.changed_files }} \
            --module-map config/system-module-map.yaml

      - name: Check new directories
        run: |
          python3 tools/check-new-directories.py \
            --module-map config/system-module-map.yaml
```

### Pre-commit Hook 整合

```bash
#!/bin/bash
# .git/hooks/pre-commit

# 檢查修改的檔案是否在允許的路徑範圍內
python3 tools/validate-refactor-paths.py \
  --staged \
  --module-map config/system-module-map.yaml

if [ $? -ne 0 ]; then
  echo "❌ 錯誤：某些修改不在允許的重構路徑範圍內"
  echo "請查看 config/system-module-map.yaml 中的 refactor 配置"
  exit 1
fi
```

---

## 📝 維護指南

### 新增 Module 的 Refactor 配置

1. 在 `config/system-module-map.yaml` 的對應 module 下新增 `refactor` 區塊
2. 定義必填欄位：
   - `cluster_id`、`target_roots`、`owners`
   - `architecture_constraints` (依賴規則)
   - `preferred_languages` / `banned_languages`
   - `quality_thresholds` (品質閾值)
3. 在 `config/unified-config-index.yaml` 的 `refactor_playbooks` 下新增條目
4. 運行驗證：
   - `python3 tools/validate-refactor-index.py`
   - `python3 tools/validate-architecture-constraints.py`

### 更新 Module 的重構範圍

1. 修改 `system-module-map.yaml` 中的 `target_roots` 或 `allow_new_subdirs`
2. 更新對應的 refactor playbook front-matter
3. 提交 PR 並請 module owners 審查

### 廢棄 Cluster

1. 將 refactor playbook 的 status 更新為 `completed` 或 `archived`
2. 可選：移除 module map 中的 `refactor` 區塊（如果不再需要）
3. 保留 playbook 檔案供歷史參考

---

## ✅ 驗證檢查清單

在提交重構相關的 PR 前，請確認：

- [ ] 所有修改都在 module map 定義的 `target_roots` 內
- [ ] 如果創建新子目錄，確認 `allow_new_subdirs: true`
- [ ] 沒有修改 `exclude_globs` 匹配的檔案
- [ ] PR 已指派給 `owners` 定義的團隊
- [ ] 運行 `python3 tools/validate-refactor-index.py` 無錯誤

---

## 🔗 相關文檔

- [LEGACY_ANALYSIS_REPORT.md](./LEGACY_ANALYSIS_REPORT.md) - 系統架構分析
- [INTEGRATION_REPORT.md](./INTEGRATION_REPORT.md) - 整合報告
- [PROPOSER_CRITIC_WORKFLOW.md](./03_refactor/meta/PROPOSER_CRITIC_WORKFLOW.md) - 雙層 AI 重構工作流程 ⭐
- [config/system-module-map.yaml](../../config/system-module-map.yaml) - 模組映射（包含架構約束）
- [config/unified-config-index.yaml](../../config/unified-config-index.yaml) - 統一配置索引
- [automation/architecture-skeletons/](../../automation/architecture-skeletons/) -
  11 個架構骨架規則

---

**Last Updated:** 2025-12-06  
**Maintainer:** Unmanned Island Architecture Team  
**Status:** ✅ Production Ready
