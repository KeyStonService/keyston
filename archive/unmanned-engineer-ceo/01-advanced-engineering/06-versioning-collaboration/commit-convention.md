# Commit Convention

## Semantic Commit Format

```
<type>(<scope>): <summary>
```

- **type**：feat, fix, chore, docs, refactor, perf, test, build, ci, revert
- **scope**：模組/資料夾（e.g., core-contract, governance-schemas）
- **summary**：不超過 72 字元

## Footer

- BREAKING CHANGE: 描述重大變更
- Issues: `Closes #123`

## Example

```
feat(contract): add raft snapshot support
```

> 所有 commit 需通過 commitlint（見 .github/island-ai-instructions.md）。
