# 架構穩定性骨架 / Architecture Stability Skeleton

## 骨架簡介 / Skeleton Overview

### 用途 / Purpose
本骨架定義系統整體架構設計原則、服務邊界劃分標準、模組依賴管理規範。AI 在設計新系統或重構現有系統時應優先查詢此骨架，確保設計符合企業架構標準。

This skeleton defines system-wide architecture design principles, service boundary standards, and module dependency management rules. AI should consult this skeleton first when designing new systems or refactoring existing ones.

### 適用場景 / Applicable Scenarios
- 🏗️ **系統架構設計** - 新系統設計、架構演進
- 🔀 **服務邊界劃分** - 微服務邊界、責任分離
- 🔗 **模組依賴規劃** - 依賴圖構建、循環依賴檢查
- 📐 **整體拓撲設計** - 系統拓撲、資料流設計

### 責任矩陣 / Responsibility Matrix

| 項目 | 由本骨架負責 | 由其他骨架負責 |
|------|-----------|------------|
| 服務邊界定義 | ✅ | |
| 模組依賴管理 | ✅ | |
| API 合約定義 | | ✅ API Governance |
| 資料模式設計 | | ✅ Data Governance |
| 安全措施實現 | | ✅ Security & Observability |
| 監控告警配置 | | ✅ Security & Observability |

### 與其他骨架的關係 / Relationship with Other Skeletons

```
┌─────────────────────────────────┐
│  架構穩定性 (主骨架)              │
│  Architecture Stability (Master) │
└────────────┬────────────────────┘
             │
    ┌────────┼────────┐
    │        │        │
    ▼        ▼        ▼
┌───────┐ ┌─────┐ ┌──────────┐
│ API   │ │ Data│ │ Security │
│ Gover.│ │Gover│ │& Observ. │
└───────┘ └─────┘ └──────────┘
```

---

## 核心設計原則 / Core Design Principles

### 1. 單一責任原則 (SRP)
- 每個服務只應有一個修改的理由
- 清晰的服務邊界，避免跨越職責

### 2. 依賴反轉原則 (DIP)
- 依賴抽象而非具體實現
- 使用依賴注入降低耦合度

### 3. 開閉原則 (OCP)
- 對擴展開放，對修改閉合
- 使用外掛架構和策略模式

### 4. 可測試性 (Testability)
- 模組應易於單元測試
- 避免強耦合和全域狀態

### 5. 可觀測性 (Observability)
- 提供追蹤點和指標暴露
- 支援分散式追蹤

---

## 典型架構決策 / Typical Architecture Decisions

### 服務邊界劃分
```yaml
# 示例：按業務能力劃分
services:
  user_service:      # 使用者管理
  order_service:     # 訂單管理
  payment_service:   # 支付處理
  notification_srv:  # 通知服務
```

### 依賴規則
```
最外層 (表現層)
    ↓
中間層 (業務邏輯)
    ↓
最內層 (領域模型)

方向：外層可依賴內層，但內層不能依賴外層
```

---

## AI 使用指南 / AI Usage Guide

### ✅ 在以下情況下使用此骨架
- 設計新微服務時
- 規劃系統重構時
- 檢查模組依賴時
- 評估服務邊界合理性時

### ❌ 不應依賴此骨架
- API 細節設計 → 查詢 API Governance
- 資料庫schema → 查詢 Data Governance
- 安全機制實現 → 查詢 Security & Observability

---

## 下一步 / Next Steps

1. 📄 閱讀 `runtime-mapping.yaml` 了解實現位置
2. 📋 查看 `io-contract.yaml` 理解輸入/輸出格式
3. 🚫 檢查 `guardrails.md` 了解禁止事項
4. ✓ 使用 `checklists.md` 進行設計驗證
