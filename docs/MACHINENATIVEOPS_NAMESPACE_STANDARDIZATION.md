# MachineNativeOps 命名空間標準化計劃（AAPS Profile）

## 📋 項目概述

本文檔說明將既有資產標準化為 MachineNativeOps 命名空間的完整計劃。所有配置、代碼、文檔將統一使用 MachineNativeOps 命名空間，確保系統的一致性和可維護性。

## 🎯 標準化目標

### 1. API Group 統一
- **標準**: `machinenativeops.io/v2`
- **應用範圍**: 所有 Kubernetes 資源、CRD、API 端點

### 2. 資源類型統一
- **標準**: `MachineNativeOpsGlobalBaseline`
- **應用範圍**: 所有 Kubernetes Custom Resources

### 3. URN 統一
- **標準**: `urn:machinenativeops:`
- **格式**: `urn:machinenativeops:{category}:{subcategory}:{name}:{version}`
- **範例**: `urn:machinenativeops:baseline:stage0:bootstrap:v1`

### 4. 標籤前綴統一
- **標準**: `machinenativeops.io/`
- **應用範圍**: 所有 Kubernetes labels 和 annotations

### 5. Namespace 統一
- **標準**: `machinenativeops`
- **應用範圍**: 所有 Kubernetes 資源的 namespace 欄位

## 🗂️ 標準化範圍

### Root Layer 配置文件
```
MachineNativeOps/
├── root.config.yaml              # 全域基本配置
├── root.governance.yaml          # 治理/權限/策略配置
├── root.modules.yaml             # 模組註冊管理與相依
├── root.super-execution.yaml     # 超級執行/流程定義
├── root.trust.yaml               # 信任/憑證/安全配置
├── root.provenance.yaml          # 來源追溯與元資料
├── root.integrity.yaml           # 整體性驗證規則
├── root.bootstrap.yaml           # 開機與初始化設定
├── root.devices.map              # 裝置檔案對應表
├── root.fs.map                   # 系統層級目錄映射
├── root.kernel.map               # 核心模組/函式庫對應
├── root.env.sh                   # Root 使用者殼層環境
└── root.naming-policy.yaml       # 命名規範政策
```

### AAPS 層配置
```
engine/
├── machinenativenops-auto-monitor/
├── config-manager/
└── ...

agents/
├── super-agent/
└── ...

opt/machinenativenops/
└── modules/
    └── config-manager/
```

## 🛠️ 標準化工具

### 自動化轉換工具
```bash
# 乾跑模式（預覽變更）
python scripts/migration/namespace-converter.py --dry-run .

# 執行轉換
python scripts/migration/namespace-converter.py .

# 驗證轉換結果
python scripts/migration/namespace-validator.py .
```

### 轉換工具功能
1. **自動識別**: 掃描所有 YAML、Python、Markdown 文件
2. **批量轉換**: 
   - `apiVersion` → `machinenativeops.io/v2`
   - `kind` → `MachineNativeOpsGlobalBaseline`
   - `namespace` → `machinenativeops`
   - URN 格式標準化
   - 標籤前綴統一
3. **驗證檢查**: 確保轉換完整性
4. **報告生成**: 生成轉換統計報告（僅顯示檔案數量和 hash 變化）

## 📝 命名規範

### metadata.name 格式
```yaml
# 格式: mno-{stage}-{component}-{profile}
metadata:
  name: mno-stage0-bootstrap-baseline
  name: mno-stage1-quantum-processor
  name: mno-stage2-enterprise-integration
```

### URN 格式
```yaml
# 格式: urn:machinenativeops:{category}:{subcategory}:{name}:{version}
annotations:
  machinenativeops.io/urn: "urn:machinenativeops:baseline:stage0:bootstrap:v1"
  machinenativeops.io/urn: "urn:machinenativeops:module:config:manager:v1"
  machinenativeops.io/urn: "urn:machinenativeops:agent:super:orchestrator:v2"
```

### 標籤規範
```yaml
labels:
  machinenativeops.io/platform: "AAPS"
  machinenativeops.io/stage: "0"
  machinenativeops.io/layer: "L0"
  machinenativeops.io/profile: "bootstrap-baseline"
  machinenativeops.io/component: "core"
  machinenativeops.io/managed-by: "aaps-controller"
```

## 🔒 治理與驗證

### CI/CD Gate 檢查
```yaml
# .github/workflows/namespace-validation.yml
name: Namespace Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Check Namespace Compliance
        run: |
          python scripts/migration/namespace-validator.py .
          
      - name: Verify No Legacy References
        run: |
          # 確保沒有舊命名空間殘留
          ! grep -r "舊前綴" . --exclude-dir=.git
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

# 檢查是否有舊命名空間
if git diff --cached | grep -E "舊前綴"; then
    echo "❌ 發現舊命名空間引用，請使用 MachineNativeOps"
    exit 1
fi

# 驗證 YAML 格式
python scripts/migration/namespace-validator.py --staged

echo "✅ 命名空間驗證通過"
```

## 📊 轉換進度追蹤

### 階段 1: Root Layer（已完成）
- ✅ root.*.yaml 文件標準化
- ✅ root/ 目錄結構標準化
- ✅ FHS 標準目錄對齊

### 階段 2: AAPS Engine Layer（進行中）
- ✅ config-manager 重新安置到 opt/machinenativenops/modules/
- ⏳ auto-monitor 命名空間標準化
- ⏳ 其他 engine 組件標準化

### 階段 3: Agents Layer（待開始）
- ⏳ super-agent 命名空間標準化
- ⏳ 其他 agents 標準化

### 階段 4: 文檔與工具（待開始）
- ⏳ 文檔更新
- ⏳ 工具腳本更新
- ⏳ CI/CD 配置更新

## 🎯 成功標準

### 技術標準
1. ✅ 所有 YAML 文件使用 `machinenativeops.io/v2`
2. ✅ 所有資源使用 `MachineNativeOpsGlobalBaseline`
3. ✅ 所有 URN 使用 `urn:machinenativeops:` 前綴
4. ✅ 所有標籤使用 `machinenativeops.io/` 前綴
5. ✅ 所有 namespace 使用 `machinenativeops`

### 驗證標準
1. ✅ CI/CD 管道全部通過
2. ✅ 無舊命名空間殘留
3. ✅ 所有測試通過
4. ✅ 文檔完整更新

## 📚 參考資源

### 模板文件
- `templates/aaps-mno-baseline-skeleton.yaml` - AAPS 標準骨架
- `root/spec/*.yaml` - Root Layer 規範
- `root/schemas/*.yaml` - Schema 定義

### 工具腳本
- `scripts/migration/namespace-converter.py` - 命名空間轉換工具
- `scripts/migration/namespace-validator.py` - 驗證工具
- `scripts/migration/generate-report.py` - 報告生成工具

### 文檔
- `ROOT_ARCHITECTURE.md` - Root Layer 架構
- `AAPS_INTEGRATION_SUMMARY.md` - AAPS 整合摘要
- `docs/AUTO_MONITOR_INTEGRATION.md` - Auto-Monitor 整合指南

## 🔄 持續改進

### 定期審查
- **每週**: 檢查新增文件的命名空間合規性
- **每月**: 審查整體標準化進度
- **每季**: 更新命名規範和最佳實踐

### 反饋機制
- GitHub Issues: 報告命名空間相關問題
- Pull Requests: 提交改進建議
- Discussions: 討論命名規範演進

---

**最後更新**: 2025-12-22  
**版本**: v1.0.0  
**狀態**: ✅ 活躍維護中