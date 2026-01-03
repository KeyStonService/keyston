# Code Review Guide / 稽核指南

## 評審目標

- 保障 SynergyMesh 安全承諾（SLSA, 零信任）。
- 達成可觀測性 + 維護性基線。

## 評分規則

| 等級       | 描述                                      |
| ---------- | ----------------------------------------- |
=======

| 等級 | 描述 |
| ---- | ---- |

>>>>>>> origin/copilot/sub-pr-402
| ✅ Approve | 符合所有檢查條目，附上必要指標/測試結果。 |
| ⚠️ Comment | 需調整但可快速修復；提供具體建議。 |
| ❌ Reject | 核心風險或缺失測試/安全設計。 |

## 清單 Checklist

- [ ] CI/CD pipeline 綠燈（GitHub Actions + Makefile）
- [ ] 靜態分析無錯誤
- [ ] 測試覆蓋率 > team baseline
- [ ] Logging/Tracing 符合 08-observability 標準
- [ ] 秘密/憑證未洩露，遵循 security-checklist
- [ ] Documentation 更新（DOCUMENTATION_INDEX.md + relevant README）
