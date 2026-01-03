# 重組計劃：將目錄移至 Workspace

## 目標

將所有不應該在 `/workspace` 根目錄的內容移動到 `workspace/` 子目錄中的適當位置。

## 當前狀態

所有目錄已經移動到：`workspace/archive/workspace-root-cleanup-20251223-054304/`

## 重組映射

### 1. 開發工具和配置 → workspace/dev-tools/

- `.vscode/` → `workspace/dev-tools/.vscode/`
- `axm-tools/` → `workspace/dev-tools/axm-tools/`
- `engine/` → `workspace/dev-tools/engine/`
- `tools/` → `workspace/dev-tools/tools/`

### 2. 源代碼和腳本 → workspace/src/

- `src/` → `workspace/src/`
- `scripts/` → `workspace/src/scripts/`
- `bin/` → `workspace/src/bin/`

### 3. 配置文件 → workspace/config/ (已存在)

- `config/` 內容合併到 → `workspace/config/`
- `etc/` → `workspace/config/etc/`

### 4. 文檔 → workspace/docs/ (已存在)

- `docs/` 內容合併到 → `workspace/docs/`
- `examples/` → `workspace/docs/examples/`
- `templates/` → `workspace/docs/templates/`

### 5. 部署相關 → workspace/deploy/

- `deploy/` → `workspace/deploy/`
- `cloudflare/` → `workspace/deploy/cloudflare/`

### 6. 測試 → workspace/tests/

- `tests/` → `workspace/tests/`

### 7. 運維和治理 → workspace/ops/

- `ops/` → `workspace/ops/`
- `governance/` → `workspace/ops/governance/`
- `schemas/` → `workspace/ops/schemas/`

### 8. 歷史和參考 → workspace/archive/legacy/

- `archive/` → `workspace/archive/legacy/archive/`
- `current-repo/` → `workspace/archive/legacy/current-repo/`
- `reference-repo/` → `workspace/archive/legacy/reference-repo/`
- `machine-native-ops/` → `workspace/archive/legacy/machine-native-ops/`
- `machine-native-ops-fresh/` → `workspace/archive/legacy/machine-native-ops-fresh/`
- `machine-native-ops-new/` → `workspace/archive/legacy/machine-native-ops-new/`
- `MachineNativeOps/` → `workspace/archive/legacy/MachineNativeOps/`

### 9. 團隊和對話 → workspace/archive/conversations/

- `teams/` → `workspace/archive/conversations/teams/`
- `summarized_conversations/` → `workspace/archive/conversations/summarized/`

### 10. 私有配置 → workspace/private/

- `.github-private/` → `workspace/private/.github-private/`
- `.local/` → `workspace/private/.local/`

### 11. FHS 模擬目錄 → workspace/archive/fhs-simulation/

這些是模擬 FHS 結構的目錄，不是真正的系統目錄：

- `home/` → `workspace/archive/fhs-simulation/home/`
- `root/` → `workspace/archive/fhs-simulation/root/`
- `opt/` → `workspace/archive/fhs-simulation/opt/`
- `srv/` → `workspace/archive/fhs-simulation/srv/`
- `usr/` → `workspace/archive/fhs-simulation/usr/`
- `var/` → `workspace/archive/fhs-simulation/var/`
- `lib/` → `workspace/archive/fhs-simulation/lib/`
- `sbin/` → `workspace/archive/fhs-simulation/sbin/`
- `init.d/` → `workspace/archive/fhs-simulation/init.d/`

## 執行順序

1. 創建目標目錄結構
2. 移動文件到對應位置
3. 驗證移動結果
4. 清理空目錄
5. 更新文檔
6. Git 提交
