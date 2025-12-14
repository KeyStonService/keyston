# Refactor Playbook: services/

**Generated:** 2025-12-12T01:18:24.732646  
**Cluster Score:** 82  
**Status:** Draft (LLM generation required for complete playbook)

---

## 1. Cluster 概覽

**Cluster Path:** `services/`  
**Current Status:** 需要重構與語言治理改進

這個 cluster 在 Unmanned Island System 中的角色：
- 路徑位置：services/
- 違規數量：0
- Hotspot 檔案：2
- 安全問題：0

---

## 2. 問題盤點

### 語言治理違規 (0)

✅ 無語言治理違規

### Hotspot 檔案 (2)

- **services/gateway/router.lua** (score: 88)
- **services/api/handler.cpp** (score: 70)

### Semgrep 安全問題 (0)

✅ 無安全問題


---

## 3. 語言與結構重構策略

**注意：** 此部分需要使用 LLM 生成完整建議。

預期內容：
- 語言層級策略（保留/遷出語言）
- 目錄結構優化建議
- 語言遷移路徑

---

## 4. 分級重構計畫（P0 / P1 / P2）

**注意：** 此部分需要使用 LLM 生成具體行動計畫。

### P0（24–48 小時內必須處理）
- 待 LLM 生成

### P1（一週內）
- 待 LLM 生成

### P2（持續重構）
- 待 LLM 生成

---

## 5. 適合交給 Auto-Fix Bot 的項目

**可自動修復：**
- 待 LLM 分析

**需人工審查：**
- 待 LLM 分析

---

## 6. 驗收條件與成功指標

**語言治理目標：**
- 違規數 < 5
- 安全問題 HIGH severity = 0
- Cluster score < 20

**改善方向：**
- 待 LLM 生成具體建議

---

## 7. 檔案與目錄結構（交付視圖）

### 受影響目錄

- services/

### 結構示意（變更範圍）

```
services/
├── _scratch/
│   ├── .gitkeep
│   └── README.md
├── agents/
│   ├── architecture-reasoner/
│   │   └── README.md
│   ├── auto-repair/
│   │   └── README.md
│   ├── code-analyzer/
│   │   └── README.md
│   ├── dependency-manager/
│   │   ├── config/
│   │   ├── src/
│   │   ├── tests/
│   │   └── README.md
│   ├── orchestrator/
│   │   └── README.md
│   ├── recovery/
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── phoenix_agent.py
│   ├── vulnerability-detector/
│   │   └── README.md
│   ├── README.md
│   └── runbook-executor.sh
├── mcp/
│   ├── deploy/
│   │   ├── deployment.yaml
│   │   ├── hpa.yaml
│   │   ├── pdb.yaml
│   │   ├── rbac.yaml
│   │   └── service.yaml
│   ├── .eslintrc.json
│   ├── .gitignore
│   ├── Dockerfile
│   ├── README.md
│   ├── VALIDATION.md
│   ├── package-lock.json
│   ├── package.json
│   └── tsconfig.json
├── watchdog/
│   ├── README.md
│   ├── __init__.py
│   └── system_watchdog.py
├── README.md
└── __init__.py
```

### 檔案說明

- `services/README.md` — 說明文檔
- `services/__init__.py` — Python 套件初始化
- `services/mcp/README.md` — 說明文檔
- `services/mcp/package.json` — Node.js 專案配置
- `services/mcp/tsconfig.json` — TypeScript 編譯配置
- `services/_scratch/README.md` — 說明文檔
- `services/agents/README.md` — 說明文檔
- `services/agents/architecture-reasoner/README.md` — 說明文檔
- `services/agents/recovery/README.md` — 說明文檔
- `services/agents/recovery/__init__.py` — Python 套件初始化

---

## 如何使用本 Playbook

1. **立即執行 P0 項目**：處理高優先級問題
2. **規劃 P1 重構**：安排一週內執行
3. **持續改進**：納入 P2 到長期技術債計畫
4. **交給 Auto-Fix Bot**：自動化可修復項目
5. **人工審查**：關鍵架構調整需要工程師參與

