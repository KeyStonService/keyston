# 策略配置 (Policies)

> **版本**: 1.0.0  
> **最後更新**: 2025-12-02

本文件描述系統的策略配置與 OPA/Conftest 整合。

---

## 概述

系統使用 OPA (Open Policy Agent) 和 Conftest 進行策略檢查。

---

## 策略目錄結構

```
governance/
├── policies/
│   ├── conftest/           # Conftest 策略
│   │   └── matechat-integration/
│   ├── opa/                # OPA 策略
│   └── custom/             # 自定義策略
└── schemas/                # JSON Schema
```

---

## 策略類型

### 1. 安全策略

| 策略 | 說明 |
|------|------|
| `no-secrets` | 禁止硬編碼密鑰 |
| `secure-defaults` | 安全默認配置 |
| `vulnerability-check` | 漏洞檢查 |

### 2. 合規策略

| 策略 | 說明 |
|------|------|
| `gdpr-compliance` | GDPR 合規 |
| `soc2-compliance` | SOC2 合規 |
| `hipaa-compliance` | HIPAA 合規 |

### 3. 品質策略

| 策略 | 說明 |
|------|------|
| `test-coverage` | 測試覆蓋率 >= 80% |
| `lint-errors` | 零 lint 錯誤 |
| `schema-validation` | Schema 驗證通過 |

---

## 使用方式

### Conftest 檢查

```bash
# 執行策略檢查
conftest test --policy governance/policies/conftest/ config/

# 指定輸出格式
conftest test --policy governance/policies/ -o json config/
```

### OPA 查詢

```bash
# 評估策略
opa eval -d governance/policies/opa/ -i input.json "data.policy.allow"
```

---

## 品質閘配置

```yaml
quality_gates:
  test_coverage: ">= 80%"
  lint_errors: 0
  security_vulnerabilities: 0
  schema_validation: pass
  policy_check: pass
```

---

## AI 治理護欄

```yaml
guardrails:
  safety:
    - harmful_content_detection
    - pii_detection
    - dangerous_operation_detection
  compliance:
    - gdpr_check
    - soc2_check
    - hipaa_check
  ethics:
    - bias_detection
    - fairness_check
    - transparency_check
```

---

## 相關資源

- [治理概覽](./overview.md) - 治理系統總覽
- [Schema 定義](./schema.md) - Schema 規範
- [治理管道](../COMPONENTS/GOVERNANCE_PIPELINE.md) - 十階段管道
