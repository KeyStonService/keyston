# schemas

## 目錄職責

此目錄為 MachineNativeOps 的 **Schema 定義層**，包含各種 YAML Schema 定義，用於驗證配置文件和資料結構。

## Schema 檔案說明

### 治理相關

| 檔案 | 職責 |
|------|------|
| `audit-report.schema.yaml` | 審計報告格式定義 |
| `change-request.schema.yaml` | 變更請求格式定義 |
| `exception-request.schema.yaml` | 例外請求格式定義 |
| `review-meeting.schema.yaml` | 審查會議格式定義 |
| `validation-policy.schema.yaml` | 驗證策略格式定義 |

### 命名與資源

| 檔案 | 職責 |
|------|------|
| `naming-spec.schema.yaml` | 命名規範定義 |
| `naming-policy.schema.yaml` | 命名策略定義 |
| `naming-observability.schema.yaml` | 命名可觀測性定義 |
| `resource-name.schema.yaml` | 資源名稱格式定義 |

### 營運相關

| 檔案 | 職責 |
|------|------|
| `metric-definition.schema.yaml` | 指標定義格式 |
| `migration-plan.schema.yaml` | 遷移計畫格式定義 |
| `remediation-playbook.schema.yaml` | 修復劇本格式定義 |

## 設計原則

1. **嚴格驗證**：所有配置必須符合 Schema
2. **版本控制**：Schema 變更需版本管理
3. **向後相容**：新版本 Schema 需相容舊資料
4. **文檔完整**：每個 Schema 需包含說明和範例

## 依賴規則

**可被依賴於**：
- `config/` - 驗證配置文件
- `src/governance/` - 治理相關驗證
- CI/CD pipelines - 自動化驗證

**不應依賴**：
- 任何實作代碼 - Schema 應獨立於實作

## 與其他目錄的關係

- **config/**：配置文件使用這些 Schema 驗證
- **src/governance/**：治理相關 Schema 與治理框架整合

