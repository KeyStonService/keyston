# HLP Executor Core Plugin - legacy_scratch 清理計畫

## 清理原則

- ✅ 只在所有整合完成後才刪除 legacy_scratch 內容
- ✅ 逐步清理，每次清理後驗證系統完整性
- ✅ 保留必要的暫存內容，直到不再需要
- ✅ 最終目標: `_legacy_scratch/` 只剩下 `.gitkeep` 或完全清空

---

## 一、清理時機與條件

### 清理前提條件
在刪除 `docs/refactor_playbooks/_legacy_scratch/README.md` 之前，必須確認以下所有條件滿足：

#### 1. P0 行動全部完成
- [ ] `governance/registry/plugins/hlp-executor-core.yaml` 已創建並驗證
- [ ] `config/system-module-map.yaml` 已更新
- [ ] `infrastructure/kubernetes/` 下所有 K8s 清單已創建並通過 `kubectl apply --dry-run`
- [ ] `core/slsa_provenance/plugins/hlp-executor-core/` 目錄結構已建立
- [ ] `config/dependencies.yaml` 已更新
- [ ] `docs/architecture/EXECUTION_MODEL.md` 已創建
- [ ] `core/safety_mechanisms/partial_rollback.py` 已實現並通過單元測試

#### 2. P1 行動至少完成 80%
- [ ] 核心架構文件已完成 (CHECKPOINT_STRATEGY.md, RECOVERY_MODE.md)
- [ ] 運維手冊已創建 (ERROR_HANDLING, EMERGENCY, MAINTENANCE)
- [ ] 安全機制模組已實現 (retry_policies.py, checkpoint_manager.py)
- [ ] 整合配置已創建 (quantum, knowledge-graph)
- [ ] 監控配置已部署 (Prometheus ServiceMonitor)

#### 3. 文件索引已更新
- [ ] `docs/DOCUMENTATION_INDEX.md` 包含所有新增文件的索引
- [ ] `CHANGELOG.md` 已記錄 HLP Executor Core 的新增

#### 4. CI/CD 驗證通過
- [ ] 所有新增的 YAML 檔案通過 YAML Lint
- [ ] 所有新增的 Python 模組通過 Pylint/Mypy
- [ ] 所有新增的 Markdown 檔案通過 Markdownlint
- [ ] 所有 JSON Schema 驗證通過

#### 5. 功能驗證通過
- [ ] 部分回滾模組單元測試通過
- [ ] 檢查點管理模組單元測試通過
- [ ] K8s 清單可成功部署到測試集群（或通過 dry-run）
- [ ] 整合測試（如有）通過

---

## 二、清理步驟（分階段執行）

### 階段一：創建備份（可選但推薦）

```bash
# 1. 創建備份目錄
mkdir -p /tmp/hlp-executor-backup

# 2. 備份 legacy_scratch README
cp docs/refactor_playbooks/_legacy_scratch/README.md \
   /tmp/hlp-executor-backup/README.md.$(date +%Y%m%d_%H%M%S)

# 3. 記錄備份資訊
echo "Backup created at $(date)" >> /tmp/hlp-executor-backup/BACKUP_LOG.txt
```

### 階段二：驗證整合完整性

```bash
# 1. 驗證所有 P0 檔案存在
bash tools/scripts/verify-hlp-integration-p0.sh

# 2. 驗證配置檔案有效性
python tools/docs/validate_index.py --verbose

# 3. 驗證 K8s 清單
kubectl apply --dry-run=client -f infrastructure/kubernetes/deployments/hlp-executor-core.yaml
kubectl apply --dry-run=client -f infrastructure/kubernetes/rbac/hlp-executor-rbac.yaml
kubectl apply --dry-run=client -f infrastructure/kubernetes/network-policies/hlp-executor-netpol.yaml
kubectl apply --dry-run=client -f infrastructure/kubernetes/storage/hlp-executor-storage.yaml

# 4. 運行單元測試
npm test -w tests/unit/hlp-executor

# 5. 檢查文件索引
grep -r "hlp-executor" docs/DOCUMENTATION_INDEX.md
grep -r "HLP Executor Core" CHANGELOG.md
```

### 階段三：標記為已整合

在 legacy_scratch README 同目錄下創建標記檔案：

```bash
cat > docs/refactor_playbooks/_legacy_scratch/README.md.INTEGRATED << EOF
# Integration Status: COMPLETED

**Original File**: README.md  
**Integration Date**: $(date +%Y-%m-%d)  
**Integration By**: Copilot Agent  

## Integration Summary
This file has been fully deconstructed and integrated into the Unmanned Island system.

## Target Locations
See the following documents for integration details:
- Deconstruction: docs/refactor_playbooks/01_deconstruction/HLP_EXECUTOR_CORE_DECONSTRUCTION.md
- Integration Mapping: docs/refactor_playbooks/02_integration/HLP_EXECUTOR_CORE_INTEGRATION_MAPPING.md
- Action Plan: docs/refactor_playbooks/03_refactor/HLP_EXECUTOR_CORE_ACTION_PLAN.md
- Cleanup Plan: docs/refactor_playbooks/03_refactor/HLP_EXECUTOR_CORE_LEGACY_CLEANUP.md

## Verification
- [x] All P0 actions completed
- [x] All P1 actions completed (>80%)
- [x] K8s manifests validated
- [x] Unit tests passing
- [x] Documentation index updated
- [x] CHANGELOG updated

## Cleanup Actions Taken
1. Archived original README.md to backup
2. Created integration status marker
3. Updated .gitignore to exclude backup files

## Next Steps
- P2 actions can be completed incrementally
- Consider removing this directory after 30 days if no issues found
EOF
```

### 階段四：移動到存檔目錄（可選）

如果不想立即刪除，可以移動到存檔目錄：

```bash
# 1. 創建存檔目錄
mkdir -p docs/refactor_playbooks/_archive/hlp-executor-core

# 2. 移動原始檔案
mv docs/refactor_playbooks/_legacy_scratch/README.md \
   docs/refactor_playbooks/_archive/hlp-executor-core/original-spec.$(date +%Y%m%d).yaml

# 3. 移動整合標記
mv docs/refactor_playbooks/_legacy_scratch/README.md.INTEGRATED \
   docs/refactor_playbooks/_archive/hlp-executor-core/INTEGRATION_STATUS.md

# 4. 更新 .gitignore
echo "docs/refactor_playbooks/_archive/" >> .gitignore
```

### 階段五：最終清理（30 天後）

如果在 30 天內沒有發現問題，可以執行最終清理：

```bash
# 1. 刪除存檔目錄（如果使用了階段四）
rm -rf docs/refactor_playbooks/_archive/hlp-executor-core

# 2. 確認 _legacy_scratch 目錄狀態
ls -la docs/refactor_playbooks/_legacy_scratch/

# 3. 如果目錄為空（只剩 .gitkeep），考慮完全移除
# 或保留作為未來暫存使用
```

---

## 三、清理檢查清單

### Pre-Cleanup Checklist（清理前檢查）

#### 核心檔案完整性
- [ ] `governance/registry/plugins/hlp-executor-core.yaml` 存在且有效
- [ ] `config/system-module-map.yaml` 包含 HLP Executor 條目
- [ ] `infrastructure/kubernetes/deployments/hlp-executor-core.yaml` 存在
- [ ] `infrastructure/kubernetes/rbac/hlp-executor-rbac.yaml` 存在
- [ ] `infrastructure/kubernetes/network-policies/hlp-executor-netpol.yaml` 存在
- [ ] `infrastructure/kubernetes/storage/hlp-executor-storage.yaml` 存在
- [ ] `core/slsa_provenance/plugins/hlp-executor-core/README.md` 存在

#### 架構文件完整性
- [ ] `docs/architecture/EXECUTION_MODEL.md` 存在且內容完整
- [ ] `docs/architecture/CHECKPOINT_STRATEGY.md` 存在
- [ ] `docs/architecture/RECOVERY_MODE.md` 存在

#### 安全機制完整性
- [ ] `core/safety_mechanisms/partial_rollback.py` 存在且通過測試
- [ ] `core/safety_mechanisms/checkpoint_manager.py` 存在且通過測試
- [ ] `core/safety_mechanisms/retry_policies.py` 包含 HLP 重試策略
- [ ] `config/safety-mechanisms.yaml` 包含 HLP 配置
- [ ] `governance/policies/security/hlp-executor-security-policy.yaml` 存在

#### 整合配置完整性
- [ ] `config/integrations/quantum-integration.yaml` 存在
- [ ] `config/integrations/knowledge-graph-integration.yaml` 存在
- [ ] `config/dependencies.yaml` 包含 HLP 依賴

#### 監控配置完整性
- [ ] `infrastructure/monitoring/prometheus/servicemonitors/hlp-executor-metrics.yaml` 存在
- [ ] `config/monitoring.yaml` 包含 HLP 日誌配置

#### 運維手冊完整性
- [ ] `docs/operations/runbooks/HLP_EXECUTOR_ERROR_HANDLING.md` 存在
- [ ] `docs/operations/runbooks/HLP_EXECUTOR_EMERGENCY.md` 存在
- [ ] `docs/operations/runbooks/HLP_EXECUTOR_MAINTENANCE.md` 存在
- [ ] `docs/operations/slo/HLP_EXECUTOR_SLO.md` 存在

#### 文件索引完整性
- [ ] `docs/DOCUMENTATION_INDEX.md` 包含所有新增文件
- [ ] `CHANGELOG.md` 包含 HLP Executor Core 條目

#### 驗證測試
- [ ] 所有 YAML 檔案通過 lint
- [ ] 所有 Python 模組通過 lint 和 type check
- [ ] K8s 清單通過 `kubectl apply --dry-run`
- [ ] 單元測試通過

### Post-Cleanup Checklist（清理後檢查）

- [ ] 備份已創建（如果需要）
- [ ] 整合標記檔案已創建
- [ ] 所有引用 legacy_scratch 的文件已更新
- [ ] CI/CD 流程仍然正常運行
- [ ] 文件構建（docs build）無錯誤
- [ ] 系統啟動（dev stack）無錯誤

---

## 四、回滾計畫（如果清理後發現問題）

### 如果需要恢復 legacy_scratch 內容

```bash
# 1. 從備份恢復（如果使用了階段一）
cp /tmp/hlp-executor-backup/README.md.* \
   docs/refactor_playbooks/_legacy_scratch/README.md

# 2. 從存檔恢復（如果使用了階段四）
cp docs/refactor_playbooks/_archive/hlp-executor-core/original-spec.*.yaml \
   docs/refactor_playbooks/_legacy_scratch/README.md

# 3. 從 Git 歷史恢復
git log --all --full-history -- docs/refactor_playbooks/_legacy_scratch/README.md
git checkout <commit-hash> -- docs/refactor_playbooks/_legacy_scratch/README.md

# 4. 驗證恢復
cat docs/refactor_playbooks/_legacy_scratch/README.md | head -20
```

### 如果某些整合有問題

1. **不要刪除整個 legacy_scratch 內容**
2. **標記問題區域**:
   ```bash
   echo "Issue found in: <specific component>" >> \
     docs/refactor_playbooks/_legacy_scratch/INTEGRATION_ISSUES.md
   ```
3. **修復問題後再次驗證**
4. **更新清理檢查清單**

---

## 五、清理時間表

### 推薦時間表

| 階段 | 時間點 | 條件 | 動作 |
|------|--------|------|------|
| **階段 0** | 整合開始前 | - | 創建備份 |
| **階段 1** | P0 完成後 | 所有 P0 檔案創建 | 標記 P0 完成，開始 P1 |
| **階段 2** | P1 完成 80% | 核心功能整合 | 創建整合標記檔案 |
| **階段 3** | P1 完成 100% | 所有必要檔案就緒 | 移動到存檔目錄 |
| **階段 4** | +7 天 | 系統運行穩定 | 驗證無問題 |
| **階段 5** | +30 天 | 持續穩定運行 | 刪除存檔（可選） |

### 保守時間表（推薦）

| 階段 | 時間點 | 條件 | 動作 |
|------|--------|------|------|
| **階段 0** | 整合開始前 | - | 創建備份 |
| **階段 1** | P0+P1 全部完成 | 所有必要檔案創建 | 創建整合標記 |
| **階段 2** | +14 天 | 系統穩定 + P2 完成 50% | 移動到存檔 |
| **階段 3** | +60 天 | 持續穩定運行 | 考慮刪除存檔 |
| **階段 4** | +90 天 | 完全穩定 | 最終清理 |

---

## 六、清理完成標準

### 最小清理標準（Must）
1. ✅ 原始 README.md 已備份或存檔
2. ✅ 整合標記檔案已創建
3. ✅ 所有 P0 檔案已創建並驗證
4. ✅ 文件索引已更新
5. ✅ CI/CD 驗證通過

### 推薦清理標準（Should）
1. ✅ 所有 P1 檔案已創建並驗證
2. ✅ 單元測試全部通過
3. ✅ K8s 清單已部署到測試環境
4. ✅ 運維手冊已審查
5. ✅ 存檔目錄已創建

### 完全清理標準（Nice）
1. ✅ 所有 P2 檔案已創建
2. ✅ 整合測試通過
3. ✅ 系統穩定運行 30+ 天
4. ✅ 無回滾需求
5. ✅ 所有團隊成員確認無問題

---

## 七、特殊情況處理

### 情況 1: 部分整合失敗
**症狀**: 某些 P0 檔案無法創建或驗證失敗  
**處理**:
1. 保留 legacy_scratch 內容
2. 在 `INTEGRATION_ISSUES.md` 中記錄問題
3. 修復問題後重新驗證
4. 只在所有問題解決後才清理

### 情況 2: 發現遺漏的內容
**症狀**: 整合後發現 legacy_scratch 中有內容未被提取  
**處理**:
1. 立即停止清理
2. 補充缺失的整合（創建新的 P0/P1 行動）
3. 更新整合文件
4. 重新驗證後再清理

### 情況 3: 需要重複使用規格
**症狀**: 其他插件需要參考相同的規格結構  
**處理**:
1. 不刪除 legacy_scratch
2. 改為創建插件模板（P2-13）
3. 將 legacy_scratch 內容轉換為模板
4. 在模板完成後再清理

### 情況 4: 合規審計需求
**症狀**: 合規部門要求保留原始規格文件  
**處理**:
1. 不刪除 legacy_scratch
2. 創建永久存檔目錄 `docs/compliance/archives/`
3. 移動到存檔目錄並添加合規標記
4. 更新 `.gitignore` 確保存檔被追蹤

---

## 八、監控與驗證腳本

### 創建驗證腳本

**檔案**: `tools/scripts/verify-hlp-integration-p0.sh`

```bash
#!/bin/bash
set -e

echo "=== Verifying HLP Executor Core Integration (P0) ==="

# P0-1: Plugin Registry
echo "Checking P0-1: Plugin Registry..."
test -f governance/registry/plugins/hlp-executor-core.yaml || exit 1

# P0-2: Module Map
echo "Checking P0-2: Module Map..."
grep -q "hlp-executor-core" config/system-module-map.yaml || exit 1

# P0-3: K8s Deployment
echo "Checking P0-3: K8s Deployment..."
test -f infrastructure/kubernetes/deployments/hlp-executor-core.yaml || exit 1

# P0-4: RBAC
echo "Checking P0-4: RBAC..."
test -f infrastructure/kubernetes/rbac/hlp-executor-rbac.yaml || exit 1

# P0-5: Network Policy
echo "Checking P0-5: Network Policy..."
test -f infrastructure/kubernetes/network-policies/hlp-executor-netpol.yaml || exit 1

# P0-6: Storage
echo "Checking P0-6: Storage..."
test -f infrastructure/kubernetes/storage/hlp-executor-storage.yaml || exit 1

# P0-7: SLSA Provenance
echo "Checking P0-7: SLSA Provenance..."
test -d core/slsa_provenance/plugins/hlp-executor-core || exit 1

# P0-8: Dependencies
echo "Checking P0-8: Dependencies..."
grep -q "hlp-executor-core" config/dependencies.yaml || exit 1

# P0-9: Architecture Doc
echo "Checking P0-9: Architecture Doc..."
test -f docs/architecture/EXECUTION_MODEL.md || exit 1

# P0-10: Partial Rollback Module
echo "Checking P0-10: Partial Rollback Module..."
test -f core/safety_mechanisms/partial_rollback.py || exit 1

echo "✅ All P0 checks passed!"
echo ""
echo "Safe to proceed with legacy_scratch cleanup."
```

### 創建清理腳本

**檔案**: `tools/scripts/cleanup-hlp-legacy-scratch.sh`

```bash
#!/bin/bash
set -e

echo "=== HLP Executor Core legacy_scratch Cleanup ==="

# Step 1: Verify integration
echo "Step 1: Verifying integration..."
bash tools/scripts/verify-hlp-integration-p0.sh

# Step 2: Create backup
echo "Step 2: Creating backup..."
mkdir -p /tmp/hlp-executor-backup
cp docs/refactor_playbooks/_legacy_scratch/README.md \
   /tmp/hlp-executor-backup/README.md.$(date +%Y%m%d_%H%M%S)

# Step 3: Create integration marker
echo "Step 3: Creating integration marker..."
cat > docs/refactor_playbooks/_legacy_scratch/README.md.INTEGRATED << EOF
# Integration Status: COMPLETED
# Integration Date: $(date +%Y-%m-%d)
# See docs/refactor_playbooks/03_refactor/HLP_EXECUTOR_CORE_LEGACY_CLEANUP.md
EOF

# Step 4: Move to archive
echo "Step 4: Moving to archive..."
mkdir -p docs/refactor_playbooks/_archive/hlp-executor-core
mv docs/refactor_playbooks/_legacy_scratch/README.md \
   docs/refactor_playbooks/_archive/hlp-executor-core/original-spec.$(date +%Y%m%d).yaml

echo "✅ Cleanup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Run tests: npm test"
echo "2. Verify CI/CD: git push && check workflows"
echo "3. Monitor for 7-14 days"
echo "4. Consider final removal after 30 days"
```

---

## 九、清理決策樹

```
開始
  ↓
所有 P0 完成？ ──否→ 繼續整合，暫不清理
  ↓ 是
P1 完成 80%？ ──否→ 完成 P1，暫不清理
  ↓ 是
驗證測試通過？ ──否→ 修復問題，暫不清理
  ↓ 是
創建備份
  ↓
創建整合標記
  ↓
移動到存檔目錄
  ↓
監控 7-14 天
  ↓
系統穩定？ ──否→ 回滾，保留存檔
  ↓ 是
監控 30+ 天
  ↓
仍然穩定？ ──否→ 保留存檔，繼續監控
  ↓ 是
最終清理（可選）
  ↓
完成
```

---

## 十、總結

### 清理原則重申
1. **安全第一**: 創建備份，逐步清理
2. **驗證優先**: 每個階段都要驗證
3. **保守估計**: 推薦時間表比最小時間表長
4. **可回滾**: 隨時可以恢復原始內容

### 最終狀態目標
- `docs/refactor_playbooks/_legacy_scratch/` 目錄:
  - 選項 A: 完全清空（最激進）
  - 選項 B: 只保留 `.gitkeep`（推薦）
  - 選項 C: 保留整合標記檔案（保守）

### 成功標準
- ✅ 所有功能正常運行
- ✅ 所有測試通過
- ✅ 文件索引完整
- ✅ 系統穩定運行
- ✅ 團隊成員確認無問題
- ✅ 無依賴 legacy_scratch 的引用

---

**注意**: 本清理計畫應與整合計畫配合使用，不應單獨執行。
