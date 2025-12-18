# 系統架構概覽 / System Architecture Overview

## 範圍 Scope

- 微服務、事件驅動架構（EDA）、消息隊列、API Gateway。
- 與 SynergyMesh 三系統（Core / Governance / Autonomous）之間的介面定義。
- 架構決策紀錄（ADR）與評審流程。

## 架構原則 Principles
<<<<<<< HEAD
<<<<<<< HEAD

1. **Single Source Config**：所有拓撲來自 `synergymesh.yaml` +
   `config/system-module-map.yaml`。
=======
1. **Single Source Config**：所有拓撲來自 `synergymesh.yaml` + `config/system-module-map.yaml`。
>>>>>>> origin/alert-autofix-37
=======

1. **Single Source Config**：所有拓撲來自 `synergymesh.yaml` + `config/system-module-map.yaml`。
>>>>>>> origin/copilot/sub-pr-402
2. **Traceability**：每個設計決策需映射到 docs/architecture 或 governance/schemas。
3. **SLSA Ready**：架構圖需描述供應鏈證據流向（core/slsa_provenance）。
4. **Fail Fast**：以 automation/architect 提供的混沌腳本驗證關鍵假設。

## 導覽 Guide

- `playbook-architecture.md`：在本平台進行架構決策的步驟。
- `examples/`：現有 core/automation 模組拆解。
- `review-checklist.md`：審查會議標準表單。
