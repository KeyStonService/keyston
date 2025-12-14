# Refactoring Playbook

## 觸發條件 Triggers
- 技術債記錄於 GLOBAL_TECH_REVIEW.txt 或 docs/KNOWLEDGE_HEALTH.md。
- 觀測到循環依賴、巨型函式、複雜度 > 15。

## 流程 Flow
1. **Assess**：使用 `npm run lint --workspaces`、`pytest`、`go test ./...`。
2. **Isolate**：建立 characterization tests，確保現狀被鎖定。
3. **Refactor**：應用 strangler fig、branch by abstraction。
4. **Prove**：更新自動測試 + observability 檢查。
5. **Document**：在 docs/ADVANCED_ESCALATION_SYSTEM.md 記錄。

## 工具 Tooling
- TypeScript: ts-morph + ESLint codemods
- Python: Rope, Bowler
- Go: gopls refactorings
- Rust: rust-analyzer assists
