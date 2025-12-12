# 🔒 安全治理 | Security Governance

> 威脅防禦、存取控制、資料保護、應變與稽核 Security posture, access control,
> data protection, incident readiness, and auditability

## 📋 概述 | Overview

安全治理確保系統以「防禦優先、持續監控、可稽核」為核心原則運作，涵蓋零信任、
身份與存取、資料保護、漏洞管理、事件應變與安全稽核。

This dimension drives a security-by-design posture with consistent controls for
identity and access, data protection, vulnerability/threat management,
incident response, and auditability.

## 📁 目錄結構 | Directory Structure

```
security-governance/
├── README.md
├── dimension.yaml
├── automation_engine.py
├── AUTOMATION_ENGINE_README.md
├── security-policy.yaml
├── access-control-policy.yaml
├── data-protection-policy.yaml
├── vulnerability-management.yaml
├── incident-response-plan.yaml
├── security-audit-framework.yaml
├── security-maturity-model.yaml
├── config/
│   ├── identity-policy.yaml             # 身份與存取治理
│   └── tenancy-policy.yaml              # 租戶隔離與資源邊界
└── schemas/
    ├── identity-schema.json             # 身份/令牌結構
    └── tenancy-schema.json              # 租戶模型與隔離約束
```

## 🎯 核心組件 | Key Components

### 1. 身份與存取控制 Identity & Access Control

- `access-control-policy.yaml` 定義 RBAC/ABAC、最小權限、審核週期
- `config/identity-policy.yaml`、`schemas/identity-schema.json` 規範 MFA、
  JWT/OIDC 標準與服務對服務存取
- `config/tenancy-policy.yaml`、`schemas/tenancy-schema.json` 確保租戶隔離
  與配額邊界

### 2. 資料保護 Data Protection

- `data-protection-policy.yaml` 規範分類、加密、保留與銷毀
- 與 `security-policy.yaml` 對齊的防禦深度與持續監控原則

### 3. 漏洞與威脅管理 Vulnerability & Threat Management

- `vulnerability-management.yaml` 規範掃描頻率、修補 SLA、例外審批
- 安全策略中的防禦深度、密鑰/憑證管理與日誌要求

### 4. 事件應變與稽核 Incident Response & Audit

- `incident-response-plan.yaml` 定義偵測、分級、通報與復原流程
- `security-audit-framework.yaml` 保障可追溯性、稽核證據與留存策略

### 5. 成熟度與治理 Maturity & Governance

- `security-maturity-model.yaml` 描述階段性成熟度與提升路線圖
- `automation_engine.py` 支援自動化安全檢查與治理執行

## 🔗 整合 | Integrations

- **04-risk**：風險識別與優先順序
- **05-compliance**：法規映射（ISO 27001 / NIST / CIS 等）
- **07-audit / 70-audit**：稽核證據與追蹤
- **38-sbom / 64-attestation**：供應鏈、簽章與來源驗證

---

**Status**: Core Governance Domain **Last Updated**: 2025-12-12
