# 架構審查清單 / Architecture Review Checklist

- [ ] 需求與範圍已於 DOCUMENTATION_INDEX.md 登記
- [ ] 系統拓撲與依賴關係貼於 docs/architecture
- [ ] 風險矩陣：延遲、容量、資料一致性、供應鏈
- [ ] 安全策略覆蓋 OAuth2 / RBAC / Secrets / Audit
- [ ] Observability 計畫（log/metrics/trace）與 infra 對齊
- [ ] 回滾策略與災難恢復（02-enterprise/07-ci-cd-devops/canary-rollback.md）
- [ ] 可驗證實驗（Chaos、負載、game day）
- [ ] Manifest 條目更新並通過 `make all-kg`
