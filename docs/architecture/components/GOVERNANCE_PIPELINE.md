# 治理管道 (Governance Pipeline)

> **版本**: 1.0.0  
> **最後更新**: 2025-12-02

本文件描述結構治理系統的十階段管道實現。

---

## 十階段治理管道

```
┌─────────────────────────────────────────────────────────────────┐
│                    十階段治理管道                                │
├─────────────────────────────────────────────────────────────────┤
│  1. Lint    → 2. Format → 3. Schema → 4. Vector Test           │
│       ↓                                      ↓                  │
│  5. Policy Gate → 6. K8s Validation → 7. SBOM                  │
│                                          ↓                      │
│  8. Provenance → 9. Cosign Sign → 10. Audit                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 階段詳解

### 階段 1: Lint

**目的**: YAML/JSON 語法檢查

```bash
# 執行 lint 檢查
npm run lint
```

### 階段 2: Format

**目的**: 格式化規則驗證

```bash
# 格式化檢查
npm run format:check
```

### 階段 3: Schema

**目的**: JSON Schema 驗證

```bash
# Schema 驗證
python tools/docs/validate_index.py --verbose
```

### 階段 4: Vector Test

**目的**: 測試向量驗證

### 階段 5: Policy Gate

**目的**: OPA/Conftest 策略檢查

```bash
# 策略檢查
conftest test --policy governance/policies/
```

### 階段 6: K8s Validation

**目的**: Kubernetes 清單驗證

```bash
# K8s 清單驗證
kubectl apply --dry-run=client -f infrastructure/kubernetes/
```

### 階段 7: SBOM

**目的**: 軟體物料清單生成

```bash
# 生成 SBOM
python tools/docs/provenance_injector.py --generate-sbom
```

### 階段 8: Provenance

**目的**: SLSA 證據注入

```bash
# 生成溯源證明
python tools/docs/provenance_injector.py --generate-provenance
```

### 階段 9: Cosign Sign

**目的**: Sigstore 無密鑰簽名

### 階段 10: Audit

**目的**: 審計事件記錄

---

## 品質閘

```yaml
quality_gates:
  test_coverage: '>= 80%'
  lint_errors: 0
  security_vulnerabilities: 0
  schema_validation: pass
  policy_check: pass
```

---

## 工具位置

| 工具          | 路徑                                     |
| ------------- | ---------------------------------------- |
| Schema 驗證器 | `tools/docs/validate_index.py`           |
| 倉庫掃描器    | `tools/docs/scan_repo_generate_index.py` |
| 溯源注入器    | `tools/docs/provenance_injector.py`      |

---

## 相關資源

- [治理概覽](../GOVERNANCE/overview.md) - 治理系統總覽
- [SLSA 溯源](../GOVERNANCE/slsa.md) - 供應鏈安全
- [策略配置](../../governance/policies/) - OPA 策略
