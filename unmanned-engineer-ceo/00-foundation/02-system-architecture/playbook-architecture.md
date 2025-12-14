# 架構決策手冊 / Architecture Playbook

## Step 1 — 問題定義
- 將需求映射到 config/system-manifest.yaml 的 domain。
- 建立即時指標：延遲、吞吐、SLO、合規。

## Step 2 — 地圖對齊
- 參考 `config/system-module-map.yaml` 取得現有模組。
- 建立 `context diagram`，標示 SynergyMesh Core / Governance / Autonomous 交界。

## Step 3 — 模式挑選
- 依事件特性選擇：微服務 + REST、EDA + Kafka、Command Bus、Actor。
- 引用 `examples/` 內的現成圖譜作為 baseline。

## Step 4 — 安全與供應鏈
- 針對新服務列出 SLSA 證據流、Cosign 簽名流程。
- 在 governance/policies 內新增/更新對應策略。

## Step 5 — 實作規劃
- 撰寫 ADR，儲存於 docs/architecture。
- 設定 `npm run dev:stack` smoke 測試腳本。

## Step 6 — 審查
- 以 `review-checklist.md` 進行評審。
- 決議後更新 manifest.yaml 的 module 條目。
