# 99-naming-convention: 統一命名規範治理

[![URN](https://img.shields.io/badge/URN-urn%3Amachinenativeops%3Agovernance%3Anaming--convention%3Av1-blue)](.)
[![Layer](https://img.shields.io/badge/Layer-Meta--Specification%20(90--99)-purple)](.)
[![Status](https://img.shields.io/badge/Status-Active-green)](.)

## 概述

統一命名規範治理維度是 MachineNativeOps 治理框架的**元規範層頂點**。此維度定義了整個系統的命名標準，確保所有維度、檔案、鍵值、引用和依賴關係遵循一致的命名慣例。

## 九大子規範

| ID | 規範 | 描述 |
|----|------|------|
| 01 | [目錄命名](./specs/01-directory-naming.yaml) | kebab-case、標準根目錄、同義詞消除 |
| 02 | [檔案命名](./specs/02-file-naming.yaml) | 檔案名格式、特殊檔案 |
| 03 | [副檔名](./specs/03-extension-standards.yaml) | 內容類型映射、禁止副檔名 |
| 04 | [鍵名](./specs/04-key-naming.yaml) | YAML/JSON 鍵命名、命名空間前綴 |
| 05 | [值名](./specs/05-value-naming.yaml) | 枚舉值、布林值、版本號、環境縮寫 |
| 06 | [映射](./specs/06-mapping-standards.yaml) | 路徑別名、關聯表命名 |
| 07 | [引用](./specs/07-reference-standards.yaml) | 跨檔案引用、導入模式 |
| 08 | [依賴](./specs/08-dependency-standards.yaml) | 版本約束、循環預防 |
| 09 | [URI/URN](./specs/09-uri-urn-standards.yaml) | 標準 URN 格式、API URI 模式 |

## 核心規則

### 目錄命名（kebab-case 強制）

```yaml
# ✅ 正確
src/governance/dimensions/99-naming-convention/

# ❌ 錯誤
Src/Governance/Dimensions/99_naming_convention/
```

### URN 格式

```
urn:machinenativeops:{domain}:{resource}:{version}
```

**範例：**

- `urn:machinenativeops:governance:naming-convention:v1`
- `urn:machinenativeops:ai:cognitive-engine:v2`

**註冊域名：**

- `governance` - 治理框架資源
- `ai` - AI 相關資源
- `core` - 核心引擎資源
- `autonomous` - 自主系統資源
- `config` - 配置資源
- `dimension` - 維度資源

### 鍵名規範

| 上下文 | 格式 | 範例 |
|--------|------|------|
| YAML 配置 | snake_case | `api_version`, `max_retry_count` |
| JSON API | camelCase | `apiVersion`, `maxRetryCount` |
| 註解 | 命名空間 | `machinenativeops.io/canonical-urn` |

### 值名規範

| 類型 | 格式 | 範例 |
|------|------|------|
| 枚舉 | kebab-case | `active`, `in-progress` |
| 布林 | 標準 | `true`, `false` |
| 版本 | SemVer | `1.0.0`, `v2.1.3-alpha` |
| 環境 | 縮寫 | `dev`, `staging`, `prod` |

## 驗證

### OPA/Rego 驗證

```bash
conftest test . --policy src/governance/dimensions/99-naming-convention/policy.rego
```

### 快速檢查

```bash
# 檢查目錄命名
find . -type d | grep -v node_modules | grep -E '[A-Z_]'

# 檢查 URN 格式
grep -rh 'urn:' --include='*.yaml' | grep -v 'urn:machinenativeops:[a-z0-9-]*:[a-z0-9-]*'
```

## 依賴關係

```yaml
dependencies:
  required:
    - 01-architecture   # 架構設計原則
    - 25-principles     # 治理原則
    - 31-schemas        # 結構驗證
  optional:
    - 27-templates      # 命名模板
    - 34-config         # 配置標準
    - 60-contracts      # 契約標準
```

## 元規範約束

作為元規範層維度，99-naming-convention：

- ✅ 可被其他維度依賴
- ❌ 不可依賴下游模組（防止循環）
- ✅ 定義所有其他維度遵循的命名標準

## 檔案結構

```
99-naming-convention/
├── dimension.yaml          # 維度定義
├── schema.json             # JSON Schema
├── policy.rego             # OPA 策略
├── README.md               # 本文件
├── specs/                  # 子規範
│   ├── 01-directory-naming.yaml
│   ├── 02-file-naming.yaml
│   ├── 03-extension-standards.yaml
│   ├── 04-key-naming.yaml
│   ├── 05-value-naming.yaml
│   ├── 06-mapping-standards.yaml
│   ├── 07-reference-standards.yaml
│   ├── 08-dependency-standards.yaml
│   └── 09-uri-urn-standards.yaml
├── examples/               # 範例
│   └── complete-naming-example.yaml
├── tests/                  # 測試
│   └── naming-convention-test.rego
└── tools/                  # 驗證工具
```

## 版本

- **當前版本**：1.0.0
- **建立日期**：2025-12-18
- **URN**：`urn:machinenativeops:governance:naming-convention:v1`
