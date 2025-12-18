# Supply Chain Security / 軟體供應鏈安全

## 流程

1. **SBOM 生成**：使用 `syft`/`cyclonedx`，儲存於 governance/sbom。
2. **簽名**：cosign + Sigstore，自動寫入 core/slsa_provenance。
3. **Provenance**：遵循 SLSA Level 3，`BUILD_PROVENANCE.md` 為依據。
4. **驗證**：部署前使用 `cosign verify` + OPA Policy Gate。

## Integration Points

- `.github/workflows/ci-comprehensive-solution.yaml`
- `config/auto-fix-bot.yml` 觸發自動修復
- `docs/KNOWLEDGE_HEALTH.md` 記錄供應鏈風險指標
