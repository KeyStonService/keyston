# SLSA 供應鏈安全

## 目標

- 達成 SLSA Level 3 認證
- 建立可追溯軟體物料鏈

## 關鍵實作

1. **來源控制**：受保護分支、必須通過 Code Review
2. **構建系統**：Hermetic Build、重現性驗證
3. **簽章**：使用 Sigstore/cosign 對產物簽章
4. **證據**：產出 provenance（`core/slsa_provenance/`）

## Pipeline

```
Commit → CI Build → Artifact Registry → Release → Runtime Checker
```

## 工具

- `scripts/generate-provenance.sh`
- GitHub OIDC + Sigstore Fulcio
- in-toto 驗證

## 驗證

```bash
./scripts/verify-provenance.sh artifact.tgz
```

## 治理整合

- SLSA 報告連結至決策系統
- 若 provenance 缺失→阻擋部署
