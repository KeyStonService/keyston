# Canonical Naming Governance - Version History

All notable changes to the Canonical Naming Governance specification will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.0.0] - 2025-01-15

### 🎉 Initial Release

#### Added

- **Single Source of Truth**: `machine-spec.yaml` 作為所有命名規則的唯一權威來源
- **三種 Canonical 命名模式**:
  - `team-domain-env`: 團隊級命名空間（例：team-frontend-prod）
  - `tenant-workload-env-region`: 多租戶跨區域部署（例：tenant-payment-prod-uswest）
  - `env-app-version`: 多版本共存部署（例：prod-api-v2）

- **基礎命名規則**:
  - 字符限制: `[a-z0-9-]` (RFC-1123 DNS_LABEL)
  - 大小寫: 僅小寫
  - 最大長度: 63 字符
  - Canonical Regex: `^(team|tenant|dev|test|staging|prod|learn)-[a-z0-9-]{1,56}[a-z0-9]$`

- **標準環境定義**:
  - `dev` (開發環境)
  - `test` (測試環境)
  - `staging` (預生產環境)
  - `prod` (生產環境)
  - `learn` (學習/沙箱環境)

- **必需標籤規範**:
  - `environment`: 部署環境標識
  - `tenant`: 租戶標識
  - `app.kubernetes.io/name`: 應用名稱
  - `app.kubernetes.io/managed-by`: 管理工具標識

- **URN/URI 映射機制**:
  - URN 格式: `urn:machinenativeops:{domain}:{component}:env:{environment}:{version}`
  - Annotation Key: `machinenativeops.io/canonical-urn`
  - 所有 Namespace 必須包含 URN annotation

- **驗證規則**:
  - RULE-001: Namespace 命名格式驗證
  - RULE-002: 必需標籤驗證
  - RULE-003: URN annotation 驗證
  - RULE-004: 保留關鍵字檢查
  - RULE-005: 環境標籤值驗證

- **保留關鍵字列表**:
  - `core`, `internal`, `system`, `legacy`, `experimental`
  - `kube`, `kubernetes`, `default`

- **工具集成配置**:
  - Gatekeeper: Admission control enforcement
  - Conftest: OPA Rego 策略驗證
  - GitHub Actions: CI/CD 自動驗證
  - Prometheus: 合規性監控指標
  - Grafana: 可視化儀表板

- **遷移支持**:
  - 衝突檢測機制
  - 自動建議生成算法
  - 批量迁移配置
  - 回滾支持

- **豁免管理**:
  - Kubernetes 系統命名空間豁免 (kube-system, kube-public, etc.)
  - 歷史遺留系統豁免（有過期時間）
  - 豁免審批流程

- **SLA 目標定義**:
  - Naming Compliance Rate (NCR): 99.9%
  - Validation Failure Rate (VFR): < 1%
  - Migration Success Rate (MSR): > 95%

- **審計追蹤**:
  - 詳細日誌記錄
  - 1 年數據保留
  - 完整字段追蹤

#### Documentation

- `canonical/README.md`: 單頁治理摘要（Platform Engineer 快速參考）
- `canonical/machine-spec.yaml`: 完整機器可讀規範
- RFC 編號: RFC-2025-10-25

#### Governance

- 批准機構: Governance Board
- 負責團隊: Platform Engineering Team
- 生效日期: 2025-01-15

---

## [Unreleased]

### Planned for v1.1.0

- [ ] 增加更多命名模式支持（feature-branch-名稱模式）
- [ ] 支持多集群命名衝突檢測
- [ ] 增強 URN 映射到 Service Mesh 資源
- [ ] 集成 ArgoCD ApplicationSet 自動生成
- [ ] 支持 Terraform Provider 直接讀取 machine-spec

### Under Consideration

- [ ] 命名規則 A/B 測試機制
- [ ] 自動命名建議 AI 模型
- [ ] 跨雲平台命名統一（AWS/GCP/Azure）
- [ ] 命名合規性評分系統
- [ ] GitLab CI 集成模板

---

## Version History Summary

| Version | Release Date | RFC | Key Changes | Breaking Changes |
|---------|--------------|-----|-------------|------------------|
| v1.0.0 | 2025-01-15 | RFC-2025-10-25 | Initial release with 3 naming modes, URN mapping, and tool integrations | N/A (Initial) |

---

## Migration Guide

### Upgrading to v1.0.0 (Initial Release)

**For New Implementations:**

1. 部署 Gatekeeper ConstraintTemplates
2. 配置 CI/CD 驗證流程
3. 啟用 Prometheus 監控指標
4. 創建符合規範的新資源

**For Existing Resources:**

1. 使用 `naming-migration.py` 掃描現有資源
2. 檢測命名衝突和不合規資源
3. 生成遷移計劃
4. 分批執行遷移（參考 `policies/migration/naming-migration-policy.yaml`）
5. 驗證遷移結果
6. 更新監控指標

**Rollback Plan:**
如需回滾遷移，請參考:

- `templates/playbooks/migration-rollback.template.yaml`
- `tools/governance/bash/rollback_migration.sh`

---

## Contribution Guidelines

### 如何提議規範變更

1. **創建 RFC**:

   ```bash
   # 複製 RFC 模板
   cp docs/governance/rfc-template.md docs/governance/rfc-YYYY-MM-DD-your-proposal.md
   ```

2. **提交 Pull Request**:
   - 包含完整的影響分析
   - 提供向後兼容性說明
   - 包含遷移指南（如有破壞性變更）

3. **治理委員會審批**:
   - 技術審查: Platform Engineering Team
   - 業務審查: Product Team
   - 最終批准: Governance Board

4. **版本發布**:
   - 更新 `machine-spec.yaml` version
   - 更新 `CHANGELOG.md`
   - 更新相關文檔和工具
   - 發布 Release Notes

### 版本號規則

遵循 [Semantic Versioning](https://semver.org/):

- **Major (x.0.0)**: 破壞性變更（例：改變 canonical regex）
- **Minor (1.x.0)**: 新增功能，向後兼容（例：新增命名模式）
- **Patch (1.0.x)**: Bug 修復和文檔更新

---

## References

- **RFC-2025-10-25**: [Canonical Naming Governance Proposal](docs/governance/rfc-2025-10-25-canonical-naming.md)
- **Implementation Guide**: [docs/governance/04-canonical-naming-governance.md](docs/governance/04-canonical-naming-governance.md)
- **Migration Policy**: [policies/migration/naming-migration-policy.yaml](policies/migration/naming-migration-policy.yaml)
- **Validation Policy**: [policies/validation/ci-validation-policy.yaml](policies/validation/ci-validation-policy.yaml)

---

## Acknowledgments

本規範基於以下研究和最佳實踐：

- Kubernetes Naming Conventions (RFC-1123 DNS_LABEL)
- Google SRE Book - Naming Standards
- AWS Well-Architected Framework - Tagging Strategy
- CNCF Best Practices - Resource Naming
- RFC-8141 - Uniform Resource Names (URNs)
- OpenTelemetry Semantic Conventions

特別感謝:

- Platform Engineering Team 的設計和實施
- Governance Board 的審批和指導
- SRE Team 的運維反饋
- 所有參與 RFC 討論的團隊成員

---

**文檔維護**: Platform Engineering Team
**最後更新**: 2025-01-15
**下次審查**: 2025-04-15 (每季度審查)
