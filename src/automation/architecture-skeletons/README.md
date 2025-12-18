# 統一架構骨架系統 / Unified Architecture Skeletons System

## 📋 概述 / Overview

本目錄作為 **統一架構骨架系統** 的入口點，整合了：

- **unmanned-engineer-ceo** 的完整架構指南（11個骨架）
- **automation/autonomous** 的實現代碼

<<<<<<< HEAD
<<<<<<< HEAD
This directory serves as the entry point for the **Unified Architecture
Skeletons System**, integrating:

=======
This directory serves as the entry point for the **Unified Architecture Skeletons System**, integrating:
>>>>>>> origin/alert-autofix-37
=======
This directory serves as the entry point for the **Unified Architecture Skeletons System**, integrating:

>>>>>>> origin/copilot/sub-pr-402
- **unmanned-engineer-ceo** complete architecture guides (11 skeletons)
- **automation/autonomous** implementation code

## 🎯 目的 / Purpose

提供統一的架構決策框架，讓 AI 和工程師能夠：

1. 快速找到相關的架構指南
2. 參考實際的實現代碼
3. 遵循標準化的設計流程
4. 確保架構決策的一致性

## 📚 核心文件 / Core Files

| 文件 | 用途 | 受眾 |
|------|------|------|
| [unified-index.yaml](./unified-index.yaml) | 完整的骨架索引和映射 | AI + 工程師 |
| [mapping.yaml](./mapping.yaml) | 指南與實現的雙向映射 | AI |
| [README.md](./README.md) | 本檔案 - 使用指南 | 工程師 |

## 🏗️ 11 個核心骨架 / 11 Core Skeletons

### 按優先級分類 / By Priority

#### 🔴 關鍵骨架 (Critical - 必須實現)

1. **architecture-stability** - 架構穩定性
   - 狀態: ✅ 生產就緒
   - 用途: 系統架構設計、服務邊界、模組依賴
   - [指南](../../unmanned-engineer-ceo/60-machine-guides/70-architecture-skeletons/architecture-stability/) | [實現](../autonomous/architecture-stability/)

2. **security-observability** - 安全與可觀測性
   - 狀態: ✅ 生產就緒
   - 用途: 安全機制、監控告警、分散式追蹤
   - [指南](../../unmanned-engineer-ceo/60-machine-guides/70-architecture-skeletons/security-observability/) | [實現](../autonomous/security-observability/)

3. **identity-tenancy** - 身份與多租戶
   - 狀態: 🟡 設計階段
   - 用途: 認證授權、RBAC/ABAC、租戶隔離
   - [指南](../../unmanned-engineer-ceo/60-machine-guides/70-architecture-skeletons/identity-tenancy/) | [實現](../autonomous/identity-tenancy/)

4. **data-governance** - 資料治理
   - 狀態: 🟡 設計階段
   - 用途: 資料模式、分類、流向、隱私合規
   - [指南](../../unmanned-engineer-ceo/60-machine-guides/70-architecture-skeletons/data-governance/) | [實現](../autonomous/data-governance/)

5. **knowledge-base** - 知識庫
   - 狀態: 🟡 設計階段
   - 用途: 知識組織、查詢介面、AI 上下文管理
   - [指南](../../unmanned-engineer-ceo/60-machine-guides/70-architecture-skeletons/knowledge-base/) | [實現](../autonomous/knowledge-base/)

6. **nucleus-orchestrator** - 核心編排
   - 狀態: 🟡 設計階段
   - 用途: 工作流編排、代理協調、任務分派
   - [指南](../../unmanned-engineer-ceo/60-machine-guides/70-architecture-skeletons/nucleus-orchestrator/) | [實現](../autonomous/nucleus-orchestrator/)

#### 🟡 高優先級骨架 (High - 應該實現)

1. **api-governance** - API 治理
   - 狀態: ✅ 生產就緒
   - 用途: API 設計、版本管理、合約驗證
   - [指南](../../unmanned-engineer-ceo/60-machine-guides/70-architecture-skeletons/api-governance/) | [實現](../autonomous/api-governance/)

2. **testing-governance** - 測試治理
   - 狀態: ✅ 生產就緒
   - 用途: 測試策略、覆蓋率標準、品質門檻
   - [指南](../../unmanned-engineer-ceo/60-machine-guides/70-architecture-skeletons/testing-governance/) | [實現](../autonomous/testing-compatibility/)

3. **performance-reliability** - 性能與可靠性
   - 狀態: 🟡 設計階段
   - 用途: SLA 目標、容量規劃、故障恢復
   - [指南](../../unmanned-engineer-ceo/60-machine-guides/70-architecture-skeletons/performance-reliability/) | [實現](../autonomous/performance-reliability/)

#### 🟢 中優先級骨架 (Medium - 可以實現)

<<<<<<< HEAD
<<<<<<< HEAD
1. **cost-management** - 成本管理
   - 狀態: 🟡 設計階段
   - 用途: 成本監控、預算規劃、資源優化
   - [指南](../../unmanned-engineer-ceo/60-machine-guides/70-architecture-skeletons/cost-management/)
     | [實現](../autonomous/cost-management/)

2. **docs-governance** - 文檔治理
   - 狀態: ✅ 生產就緒
   - 用途: 文檔標準、更新流程、機器可讀文檔
   - [指南](../../unmanned-engineer-ceo/60-machine-guides/70-architecture-skeletons/docs-governance/)
     | [實現](../autonomous/docs-examples/)
=======
10. **cost-management** - 成本管理
=======
1. **cost-management** - 成本管理
>>>>>>> origin/copilot/sub-pr-402
    - 狀態: 🟡 設計階段
    - 用途: 成本監控、預算規劃、資源優化
    - [指南](../../unmanned-engineer-ceo/60-machine-guides/70-architecture-skeletons/cost-management/) | [實現](../autonomous/cost-management/)

2. **docs-governance** - 文檔治理
    - 狀態: ✅ 生產就緒
    - 用途: 文檔標準、更新流程、機器可讀文檔
    - [指南](../../unmanned-engineer-ceo/60-machine-guides/70-architecture-skeletons/docs-governance/) | [實現](../autonomous/docs-examples/)
<<<<<<< HEAD
>>>>>>> origin/alert-autofix-37
=======
>>>>>>> origin/copilot/sub-pr-402

## 🚀 快速開始 / Quick Start

### 對於 AI 系統 / For AI Systems

```python
# 1. 載入統一索引
import yaml
with open('automation/architecture-skeletons/unified-index.yaml') as f:
    index = yaml.safe_load(f)

# 2. 根據任務類型查詢骨架
task_type = "設計新的 API"
relevant_skeletons = find_skeletons_for_task(task_type)
# 返回: ['api-governance', 'security-observability', 'testing-governance']

# 3. 讀取指南文件
guide_path = index['skeletons'][skeleton_id]['guide']['path']
read_guide_files(guide_path)

# 4. 參考實現代碼
impl_path = index['skeletons'][skeleton_id]['implementation']['path']
read_implementation(impl_path)

# 5. 使用 guardrails 和 checklists 驗證
validate_with_guardrails(guide_path + 'guardrails.md')
check_with_checklists(guide_path + 'checklists.md')
```

### 對於工程師 / For Engineers

#### 步驟 1: 識別需求

```bash
# 我需要設計一個多租戶系統
# → 查看 identity-tenancy 骨架
```

#### 步驟 2: 閱讀指南

```bash
# 1. 查看概述
cat unmanned-engineer-ceo/60-machine-guides/70-architecture-skeletons/identity-tenancy/overview.md

# 2. 理解 IO 契約
cat unmanned-engineer-ceo/60-machine-guides/70-architecture-skeletons/identity-tenancy/io-contract.yaml

# 3. 檢查 Guardrails
cat unmanned-engineer-ceo/60-machine-guides/70-architecture-skeletons/identity-tenancy/guardrails.md
```

#### 步驟 3: 參考實現

```bash
# 查看實現目錄
cd automation/autonomous/identity-tenancy/
cat README.md
```

#### 步驟 4: 自檢

```bash
# 使用 Checklist 驗證設計
cat unmanned-engineer-ceo/60-machine-guides/70-architecture-skeletons/identity-tenancy/checklists.md
```

## 📖 使用場景 / Use Cases

### 場景 1: 設計新微服務

```
任務: 設計一個用戶管理微服務

步驟:
1. architecture-stability → 確定服務邊界
2. api-governance → 設計 API 介面
3. identity-tenancy → 實現認證授權
4. security-observability → 添加監控和日誌
5. testing-governance → 規劃測試策略

使用骨架: 5 個
預計時間: 2-3 天
```

### 場景 2: 實現多租戶支持

```
任務: 為現有系統添加多租戶支持

步驟:
1. identity-tenancy → 設計隔離策略
2. data-governance → 規劃資料分離
3. security-observability → 監控租戶邊界
4. testing-governance → 租戶隔離測試

使用骨架: 4 個
預計時間: 1-2 週
```

### 場景 3: 系統性能優化

```
任務: 優化系統性能並降低成本

步驟:
1. performance-reliability → 定義 SLA 和瓶頸分析
2. architecture-stability → 識別架構問題
3. cost-management → 評估成本影響和優化
4. testing-governance → 性能測試計劃

使用骨架: 4 個
預計時間: 1 週
```

## 🔄 工作流程 / Workflow

### AI 決策流程 / AI Decision Flow

```
1. 接收任務
   ↓
2. 查詢 unified-index.yaml
   找到相關骨架
   ↓
3. 讀取指南文件
   - overview.md (理解用途)
   - io-contract.yaml (了解輸入輸出)
   - runtime-mapping.yaml (找到真實位置)
   ↓
4. 檢查 Guardrails
   確保不違反規則
   ↓
5. 參考實現代碼
   了解實際做法
   ↓
6. 執行任務
   ↓
7. 使用 Checklist 驗證
   確保質量
   ↓
8. 更新知識庫
```

### 工程師設計流程 / Engineer Design Flow

```
1. 定義需求
   ↓
2. 選擇相關骨架
   (參考 unified-index.yaml)
   ↓
3. 研讀架構指南
   (unmanned-engineer-ceo)
   ↓
4. 參考實現代碼
   (automation/autonomous)
   ↓
5. 設計方案
   ↓
6. 自檢 (Checklists)
   ↓
7. 實現代碼
   ↓
8. 測試驗證
```

## 📊 骨架狀態總覽 / Skeletons Status Overview

### 實現狀態 / Implementation Status

| 狀態 | 數量 | 骨架列表 |
|------|------|---------|
| ✅ 生產就緒 | 5 | architecture-stability, security-observability, api-governance, testing-governance, docs-governance |
| 🟡 設計階段 | 6 | identity-tenancy, data-governance, performance-reliability, cost-management, knowledge-base, nucleus-orchestrator |
| 🔴 規劃中 | 0 | - |

### 技術棧分布 / Tech Stack Distribution

| 技術 | 骨架數量 | 骨架列表 |
|------|---------|---------|
| Python | 8 | api-governance, identity-tenancy, data-governance, testing-governance, performance-reliability, cost-management, knowledge-base, nucleus-orchestrator |
| C++ + ROS 2 | 1 | architecture-stability |
| Go | 1 | security-observability |
| YAML + Markdown | 1 | docs-governance |

## 🔗 整合點 / Integration Points

### 與 SynergyMesh 平台 / With SynergyMesh Platform

```yaml
integrations:
  core_systems:
    - core/unified_integration/     # 統一整合層
    - core/mind_matrix/             # 心智矩陣
    - core/safety_mechanisms/       # 安全機制
    - core/slsa_provenance/         # SLSA 溯源
  
  governance:
    - governance/schemas/           # 治理模式
    - governance/policies/          # 策略定義
  
  services:
    - services/mcp/                 # MCP 伺服器
    - services/agents/              # 智能代理
  
  infrastructure:
    - infrastructure/monitoring/    # 監控系統
    - infrastructure/drift/         # 漂移檢測
  
  documentation:
    - docs/knowledge-graph.yaml     # 知識圖譜
    - docs/LIVING_KNOWLEDGE_BASE.md # 活體知識庫
    - DOCUMENTATION_INDEX.md        # 文檔索引
```

## 📝 維護指南 / Maintenance Guide

### 更新骨架 / Updating Skeletons

當您需要更新骨架時：

1. **更新指南文件** (unmanned-engineer-ceo)

   ```bash
   cd unmanned-engineer-ceo/60-machine-guides/70-architecture-skeletons/<skeleton-name>/
   # 更新相關的 .md 和 .yaml 文件
   ```

2. **更新實現代碼** (automation/autonomous)

   ```bash
   cd automation/autonomous/<skeleton-name>/
   # 更新代碼和 README.md
   ```

3. **更新統一索引**

   ```bash
   cd automation/architecture-skeletons/
   # 更新 unified-index.yaml
   # 更新本 README.md
   ```

4. **同步知識庫**

   ```bash
   make all-kg  # 重新生成知識圖譜
   ```

### 添加新骨架 / Adding New Skeletons

1. 在 unmanned-engineer-ceo 中創建指南
2. 在 automation/autonomous 中創建實現目錄
3. 更新 unified-index.yaml
4. 更新本 README.md
5. 運行 `make all-kg`

## 🧪 測試與驗證 / Testing and Validation

### 驗證骨架完整性 / Validate Skeleton Completeness

```bash
# 檢查所有骨架的文件是否完整
python tools/validate_skeletons.py --check-completeness

# 驗證指南與實現的一致性
python tools/validate_skeletons.py --check-consistency

# 檢查鏈接有效性
python tools/validate_skeletons.py --check-links
```

## 📈 指標與報告 / Metrics and Reports

### 骨架使用統計 / Skeleton Usage Statistics

系統會自動追蹤骨架使用情況：

```yaml
usage_stats:
  most_used:
    - architecture-stability: 45%
    - api-governance: 25%
    - security-observability: 15%
  
  by_agent:
    architect_agent:
      - architecture-stability
      - api-governance
    security_agent:
      - security-observability
      - identity-tenancy
```

報告位置: `docs/skeleton-usage-report.yaml`

## 🆘 常見問題 / FAQ

### Q: 如何選擇合適的骨架？

**A**: 根據任務類型：

- 架構設計 → architecture-stability
- API 開發 → api-governance
- 安全需求 → security-observability, identity-tenancy
- 資料處理 → data-governance
- 測試 → testing-governance
- 性能優化 → performance-reliability
- 成本優化 → cost-management
- 文檔 → docs-governance
- 知識管理 → knowledge-base
- 工作流 → nucleus-orchestrator

### Q: 指南和實現不一致怎麼辦？

**A**:

1. 以指南為準（設計標準）
2. 更新實現代碼以符合指南
3. 如果指南有誤，更新指南並提 PR

### Q: 如何貢獻新的骨架？

**A**:

1. 提出 Issue 說明需求
2. 創建指南文件（5 個標準文件）
3. 創建實現目錄和 README
4. 更新 unified-index.yaml
5. 提交 PR 並請求審查

## 📞 支援與聯繫 / Support and Contact

### 維護團隊 / Maintainers

- **Owner**: SynergyMesh Architecture Guild
- **Contact**: <governance@unmanned.island>

### 相關資源 / Related Resources

- [架構分析報告](../../docs/ARCHITECTURE_SKELETON_ANALYSIS.md)
- [整合總結](../autonomous/INTEGRATION_SUMMARY.md)
- [知識健康報告](../../docs/KNOWLEDGE_HEALTH.md)
- [文檔索引](../../DOCUMENTATION_INDEX.md)

---

**版本**: 1.0.0  
**最後更新**: 2025-12-05  
**狀態**: ✅ 生產就緒  
**授權**: MIT License
