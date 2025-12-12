# Schema 定義 (Schema Definitions)

> **版本**: 1.0.0  
> **最後更新**: 2025-12-02

本文件描述系統使用的 Schema 定義規範。

---

## Schema 命名空間

```yaml
$schema: 'https://schema.synergymesh.io/docs-index/v1'
namespace: 'synergymesh.docs'
```

---

## 文檔索引 Schema

每個文檔項目必須包含以下欄位：

### 必要欄位

| 欄位          | 類型   | 說明                    |
| ------------- | ------ | ----------------------- |
| `id`          | string | 唯一識別符 (snake_case) |
| `path`        | string | 文檔相對路徑            |
| `title`       | string | 文檔標題                |
| `domain`      | string | 領域分類                |
| `layer`       | string | 架構層級                |
| `type`        | string | 文檔類型                |
| `tags`        | array  | 標籤陣列                |
| `owner`       | string | 負責團隊                |
| `status`      | string | 文檔狀態                |
| `description` | string | 簡短描述                |

### 可選欄位

| 欄位         | 類型   | 說明       |
| ------------ | ------ | ---------- |
| `platforms`  | array  | 支援平台   |
| `languages`  | array  | 程式語言   |
| `provenance` | object | SLSA 溯源  |
| `sbom`       | string | SBOM 路徑  |
| `signature`  | string | 簽名信息   |
| `links`      | array  | 相關連結   |
| `meta`       | object | 額外元數據 |

---

## 有效值定義

### Domain 領域

- `architecture` - 架構設計
- `automation` - 自動化系統
- `governance` - 治理與策略
- `operations` - 運維指南
- `guides` - 入門與教程
- `security` - 安全相關
- `components` - 核心元件

### Layer 層級

- `experience-interfaces` - 前端、橋接、合約
- `platform-core` - 核心服務、運行時、共用
- `ai-automation` - 自動化、代理、MCP 伺服器
- `enablement` - 基礎設施、CI、測試、配置
- `governance-ops` - 治理、運維、文檔

### Type 類型

- `readme` - README 文件
- `guide` - 指南文檔
- `reference` - 參考文檔
- `design` - 設計文檔
- `api-reference` - API 文檔
- `index` - 索引文檔
- `tutorial` - 教程

### Status 狀態

- `stable` - 穩定，生產可用
- `experimental` - 實驗性
- `draft` - 草稿
- `deprecated` - 已廢棄

---

## 範例

```yaml
- id: 'product_overview'
  path: 'docs/PRODUCT_OVERVIEW.md'
  title: '產品概覽 Product Overview'
  domain: 'architecture'
  layer: 'platform-core'
  type: 'reference'
  tags: ['overview', 'vision', 'mvp']
  owner: 'docs-team'
  status: 'stable'
  last_reviewed: '2025-12-02'
  description: '系統價值、願景、定位'
```

---

## Schema 驗證

```bash
# 驗證 knowledge_index.yaml
python tools/docs/validate_index.py --verbose
```

---

## 相關資源

- [治理概覽](./overview.md) - 治理系統總覽
- [文檔契約](../CONTRACT.md) - 文檔規範
- [知識索引](../knowledge_index.yaml) - 機器可讀索引
