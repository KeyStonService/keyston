# AGENTS 狀態標記規範

本文件記錄所有 AI 代理在專案中使用的狀態標記（Status Marker）的約定。

## 狀態標記

- ✅ (check mark): 表示任務或檢查項已完成。
- ⏸️ (double vertical bar): 表示任務被暫停、中斷或被阻止。
- 🔄 (arrows clockwise): 表示任務正在進行或循環中。
- ❌ (cross mark): 表示任務失敗、被拒絕或錯誤。
- ⏭️ (next track button): 表示任務已跳過。

## 使用原則

1. 每個任務或待辦事項前必須使用一個狀態標記。
2. 狀態標記應在任務描述的同一行，位於最開始位置。
3. 所有報告、清單和交付物必須遵循此規範。
4. 狀態標記與任務狀態必須保持邏輯一致性：
   - 若任務受阻，所有相關審核項都應標記為 ⏸️
   - 若任務進行中，相關審核項可標記為 🔄 或空白
   - 若任務完成，所有相關審核項都應標記為 ✅
   - 若任務失敗，所有相關審核項都應標記為 ❌

## PR 模板規範


- 使用標準化狀態標記：✅ (Complete), ⏸️ (Blocked), 🔄 (In Progress), ❌ (Failed), ⏭️ (Skipped)
- 確保狀態與清單進度一致：status ≡ checklist progress
- 所有變更必須先更新治理文件再實施

## 證據鏈要求
- CHANGELOG.md: 紀錄所有變更歷史
- RISK_ASSESSMENT.md: 評估變更風險
- AGENT_DELIVERY_CONTRACT.md: 遵循交付契約
- 所有 PR 必須提供四大核心證據：repo, branch, commit, PR

## 行動端友善性

- 重要設定檔必須可見且易於存取
- 目錄深度合理化，避免過深巢狀
- 提供長按複製連結快速驗證功能
