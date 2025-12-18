"""
隱私優先框架 (Privacy-First Framework)

功能：
- 隱私設計：從設計階段考慮隱私
- 數據主權：確保數據控制權
- 同意管理：管理用戶同意
- 合規檢查：GDPR、CCPA 等法規合規

Features:
- Privacy by Design: Consider privacy from the design phase
- Data Sovereignty: Ensure data control
- Consent Management: Manage user consent
- Compliance Check: GDPR, CCPA regulatory compliance
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, cast


class DataSensitivity(Enum):
    """數據敏感度等級"""

    PUBLIC = "public"  # 公開
    INTERNAL = "internal"  # 內部
    CONFIDENTIAL = "confidential"  # 機密
    RESTRICTED = "restricted"  # 受限
    TOP_SECRET = "top_secret"  # 絕密


class ConsentType(Enum):
    """同意類型"""

    EXPLICIT = "explicit"  # 明確同意
    IMPLIED = "implied"  # 隱含同意
    OPT_IN = "opt_in"  # 選擇加入
    OPT_OUT = "opt_out"  # 選擇退出


class DataCategory(Enum):
    """數據類別"""

    PERSONAL = "personal"  # 個人數據
    SENSITIVE = "sensitive"  # 敏感數據
    FINANCIAL = "financial"  # 財務數據
    HEALTH = "health"  # 健康數據
    BIOMETRIC = "biometric"  # 生物識別
    BEHAVIORAL = "behavioral"  # 行為數據
    LOCATION = "location"  # 位置數據
    TECHNICAL = "technical"  # 技術數據


class ComplianceFramework(Enum):
    """合規框架"""

    GDPR = "gdpr"  # 歐盟通用數據保護條例
    CCPA = "ccpa"  # 加州消費者隱私法
    HIPAA = "hipaa"  # 健康保險便攜性和責任法案
    PIPEDA = "pipeda"  # 個人信息保護和電子文檔法案
    LGPD = "lgpd"  # 巴西通用數據保護法
    PDPA = "pdpa"  # 個人數據保護法（新加坡/台灣）


@dataclass
class DataField:
    """數據欄位定義"""

    field_name: str
    field_type: str
    sensitivity: DataSensitivity = DataSensitivity.INTERNAL
    category: DataCategory = DataCategory.TECHNICAL

    # 隱私屬性
    is_pii: bool = False  # 是否為個人識別資訊
    is_encrypted: bool = False  # 是否加密
    is_anonymized: bool = False  # 是否匿名化
    is_pseudonymized: bool = False  # 是否假名化

    # 保留策略
    retention_days: int = 365  # 保留天數
    deletion_policy: str = "soft"  # 刪除策略 (soft, hard)

    # 存取控制
    access_roles: list[str] = field(default_factory=list)
    requires_consent: bool = False


@dataclass
class PrivacyByDesign:
    """隱私設計原則實現"""

    project_name: str

    # 數據欄位映射
    data_fields: dict[str, DataField] = field(default_factory=dict)

    # 設計原則評分
    proactive_score: float = 0.0  # 預防性
    default_privacy_score: float = 0.0  # 默認隱私
    embedded_score: float = 0.0  # 嵌入式設計
    positive_sum_score: float = 0.0  # 正和博弈
    e2e_security_score: float = 0.0  # 端到端安全
    visibility_score: float = 0.0  # 可見性透明度
    user_centric_score: float = 0.0  # 以用戶為中心

    # 總分
    overall_score: float = 0.0

    # 評估日期
    assessment_date: datetime | None = None

    def __post_init__(self) -> None:
        if self.assessment_date is None:
            self.assessment_date = datetime.now()

    def add_data_field(self, field: DataField) -> None:
        """添加數據欄位"""
        self.data_fields[field.field_name] = field

    def assess(self) -> dict[str, float]:
        """評估隱私設計"""
        if not self.data_fields:
            return {"overall": 0.0}

        # 計算各項指標
        pii_count = sum(1 for f in self.data_fields.values() if f.is_pii)
        encrypted_count = sum(1 for f in self.data_fields.values() if f.is_encrypted)
        anonymized_count = sum(1 for f in self.data_fields.values() if f.is_anonymized)
        consent_required = sum(1 for f in self.data_fields.values() if f.requires_consent)

        total_fields = len(self.data_fields)

        # 預防性分數（PII 保護比例）
        self.proactive_score = (1 - pii_count / total_fields) * 100 if total_fields > 0 else 100

        # 默認隱私分數（加密和匿名化比例）
        protected = encrypted_count + anonymized_count
        self.default_privacy_score = (protected / total_fields) * 100 if total_fields > 0 else 0

        # 嵌入式設計分數
        self.embedded_score = 70  # 基礎分數，可根據架構評估調整

        # 正和博弈分數
        self.positive_sum_score = 75  # 基礎分數

        # 端到端安全分數
        self.e2e_security_score = (encrypted_count / total_fields) * 100 if total_fields > 0 else 0

        # 可見性分數（同意需求覆蓋率）
        self.visibility_score = (consent_required / pii_count) * 100 if pii_count > 0 else 100

        # 以用戶為中心分數
        self.user_centric_score = (
            min(100, (consent_required / total_fields) * 200) if total_fields > 0 else 0
        )

        # 計算總分（加權平均）
        self.overall_score = (
            self.proactive_score * 0.15
            + self.default_privacy_score * 0.20
            + self.embedded_score * 0.10
            + self.positive_sum_score * 0.10
            + self.e2e_security_score * 0.20
            + self.visibility_score * 0.15
            + self.user_centric_score * 0.10
        )

        return {
            "proactive": self.proactive_score,
            "default_privacy": self.default_privacy_score,
            "embedded": self.embedded_score,
            "positive_sum": self.positive_sum_score,
            "e2e_security": self.e2e_security_score,
            "visibility": self.visibility_score,
            "user_centric": self.user_centric_score,
            "overall": self.overall_score,
        }

    def get_recommendations(self) -> list[str]:
        """獲取改進建議"""
        recommendations = []

        if self.proactive_score < 70:
            recommendations.append("🔒 減少 PII 數據收集，考慮數據最小化原則")

        if self.default_privacy_score < 70:
            recommendations.append("🔐 增加數據加密和匿名化覆蓋率")

        if self.e2e_security_score < 70:
            recommendations.append("🛡️ 實施端到端加密，保護傳輸中的數據")

        if self.visibility_score < 70:
            recommendations.append("👁️ 對所有 PII 數據實施同意管理機制")

        if self.user_centric_score < 70:
            recommendations.append("👤 增強用戶對數據的控制權")

        if not recommendations:
            recommendations.append("✅ 隱私設計表現良好！繼續保持。")

        return recommendations


@dataclass
class DataSovereignty:
    """數據主權管理"""

    organization_id: str

    # 數據位置
    data_locations: dict[str, str] = field(default_factory=dict)  # data_type -> location

    # 管轄權映射
    jurisdiction_mapping: dict[str, list[str]] = field(default_factory=dict)

    # 跨境傳輸規則
    cross_border_rules: dict[str, dict[str, Any]] = field(default_factory=dict)

    # 本地化要求
    localization_requirements: list[dict[str, Any]] = field(default_factory=list)

    def register_data_location(self, data_type: str, location: str, jurisdiction: str) -> None:
        """註冊數據位置"""
        self.data_locations[data_type] = location

        if jurisdiction not in self.jurisdiction_mapping:
            self.jurisdiction_mapping[jurisdiction] = []
        self.jurisdiction_mapping[jurisdiction].append(data_type)

    def check_transfer_allowed(
        self, data_type: str, source_jurisdiction: str, target_jurisdiction: str
    ) -> dict[str, Any]:
        """檢查跨境傳輸是否允許"""
        # 檢查是否有特定規則
        rule_key = f"{source_jurisdiction}->{target_jurisdiction}"

        if rule_key in self.cross_border_rules:
            rule = self.cross_border_rules[rule_key]
            return {
                "allowed": rule.get("allowed", False),
                "conditions": rule.get("conditions", []),
                "documentation_required": rule.get("documentation", []),
            }

        # 默認規則：同一管轄區允許，不同管轄區需要審查
        if source_jurisdiction == target_jurisdiction:
            return {"allowed": True, "conditions": [], "documentation_required": []}

        return {
            "allowed": False,
            "conditions": ["需要數據傳輸協議", "需要合規審查"],
            "documentation_required": ["傳輸影響評估", "用戶同意書"],
        }

    def add_cross_border_rule(
        self,
        source: str,
        target: str,
        allowed: bool,
        conditions: list[str] | None = None,
        documentation: list[str] | None = None,
    ) -> None:
        """添加跨境傳輸規則"""
        rule_key = f"{source}->{target}"
        self.cross_border_rules[rule_key] = {
            "allowed": allowed,
            "conditions": conditions or [],
            "documentation": documentation or [],
        }

    def get_compliance_report(self) -> dict[str, Any]:
        """生成合規報告"""
        return {
            "organization_id": self.organization_id,
            "data_locations": self.data_locations,
            "jurisdictions": list(self.jurisdiction_mapping.keys()),
            "data_types_by_jurisdiction": self.jurisdiction_mapping,
            "cross_border_rules_count": len(self.cross_border_rules),
            "localization_requirements": len(self.localization_requirements),
            "report_date": datetime.now().isoformat(),
        }


@dataclass
class ConsentRecord:
    """同意記錄"""

    consent_id: str
    user_id: str
    purpose: str
    consent_type: ConsentType

    # 時間戳
    granted_at: datetime | None = None
    expires_at: datetime | None = None
    revoked_at: datetime | None = None

    # 狀態
    is_active: bool = True

    # 數據範圍
    data_categories: list[DataCategory] = field(default_factory=list)

    # 元數據
    source: str = ""  # 同意來源（網站、App、紙本）
    ip_address: str = ""  # IP 地址（已哈希）
    user_agent: str = ""  # 用戶代理

    def __post_init__(self) -> None:
        if self.granted_at is None:
            self.granted_at = datetime.now()

    def revoke(self) -> None:
        """撤銷同意"""
        self.is_active = False
        self.revoked_at = datetime.now()

    def is_valid(self) -> bool:
        """檢查同意是否有效"""
        if not self.is_active:
            return False

        if self.revoked_at is not None:
            return False

        return not (self.expires_at and datetime.now() > self.expires_at)


class ConsentManager:
    """
    同意管理器

    功能：
    - 收集和管理用戶同意
    - 追蹤同意歷史
    - 處理同意撤銷
    - 生成同意報告
    """

    def __init__(self) -> None:
        self.consents: dict[str, ConsentRecord] = {}
        self.user_consents: dict[str, list[str]] = {}  # user_id -> [consent_ids]
        self.purpose_consents: dict[str, list[str]] = {}  # purpose -> [consent_ids]

    def _generate_consent_id(self, user_id: str, purpose: str) -> str:
        """生成同意 ID"""
        data = f"{user_id}:{purpose}:{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def record_consent(
        self,
        user_id: str,
        purpose: str,
        consent_type: ConsentType,
        data_categories: list[DataCategory],
        expires_days: int = 365,
        source: str = "web",
        ip_address: str = "",
        user_agent: str = "",
    ) -> ConsentRecord:
        """
        記錄用戶同意

        Args:
            user_id: 用戶 ID
            purpose: 同意目的
            consent_type: 同意類型
            data_categories: 數據類別
            expires_days: 過期天數
            source: 同意來源
            ip_address: IP 地址
            user_agent: 用戶代理

        Returns:
            ConsentRecord: 同意記錄
        """
        consent_id = self._generate_consent_id(user_id, purpose)

        # 哈希 IP 地址以保護隱私
        hashed_ip = hashlib.sha256(ip_address.encode()).hexdigest()[:12] if ip_address else ""

        consent = ConsentRecord(
            consent_id=consent_id,
            user_id=user_id,
            purpose=purpose,
            consent_type=consent_type,
            expires_at=datetime.now() + timedelta(days=expires_days),
            data_categories=data_categories,
            source=source,
            ip_address=hashed_ip,
            user_agent=user_agent,
        )

        self.consents[consent_id] = consent

        # 更新索引
        if user_id not in self.user_consents:
            self.user_consents[user_id] = []
        self.user_consents[user_id].append(consent_id)

        if purpose not in self.purpose_consents:
            self.purpose_consents[purpose] = []
        self.purpose_consents[purpose].append(consent_id)

        return consent

    def revoke_consent(self, consent_id: str) -> bool:
        """撤銷同意"""
        if consent_id not in self.consents:
            return False

        self.consents[consent_id].revoke()
        return True

    def revoke_all_user_consents(self, user_id: str) -> int:
        """撤銷用戶所有同意"""
        if user_id not in self.user_consents:
            return 0

        count = 0
        for consent_id in self.user_consents[user_id]:
            if self.revoke_consent(consent_id):
                count += 1

        return count

    def check_consent(self, user_id: str, purpose: str, data_category: DataCategory) -> bool:
        """
        檢查用戶是否已同意特定目的和數據類別

        Args:
            user_id: 用戶 ID
            purpose: 目的
            data_category: 數據類別

        Returns:
            bool: 是否有有效同意
        """
        if user_id not in self.user_consents:
            return False

        for consent_id in self.user_consents[user_id]:
            consent = self.consents.get(consent_id)
            if consent and consent.is_valid():
                if consent.purpose == purpose and data_category in consent.data_categories:
                    return True

        return False

    def get_user_consents(self, user_id: str) -> list[ConsentRecord]:
        """獲取用戶所有同意記錄"""
        if user_id not in self.user_consents:
            return []

        return [self.consents[cid] for cid in self.user_consents[user_id] if cid in self.consents]

    def generate_consent_report(self, user_id: str) -> dict[str, Any]:
        """生成用戶同意報告"""
        consents = self.get_user_consents(user_id)

        active_consents = [c for c in consents if c.is_valid()]
        revoked_consents = [c for c in consents if not c.is_valid()]

        return {
            "user_id": user_id,
            "total_consents": len(consents),
            "active_consents": len(active_consents),
            "revoked_consents": len(revoked_consents),
            "consent_details": [
                {
                    "consent_id": c.consent_id,
                    "purpose": c.purpose,
                    "type": c.consent_type.value,
                    "granted_at": c.granted_at.isoformat() if c.granted_at else None,
                    "expires_at": c.expires_at.isoformat() if c.expires_at else None,
                    "is_valid": c.is_valid(),
                    "data_categories": [cat.value for cat in c.data_categories],
                }
                for c in consents
            ],
            "report_generated_at": datetime.now().isoformat(),
        }


class PrivacyFramework:
    """
    隱私優先框架

    功能：
    - 整合隱私設計、數據主權、同意管理
    - 合規性檢查
    - 隱私影響評估
    - 生成合規報告

    Usage:
        framework = PrivacyFramework("my_project")

        # 隱私設計評估
        framework.add_data_field(DataField(...))
        design_score = framework.assess_privacy_design()

        # 同意管理
        framework.record_consent(user_id, purpose, ...)
        has_consent = framework.check_consent(user_id, purpose, category)

        # 合規檢查
        compliance = framework.check_compliance(ComplianceFramework.GDPR)
    """

    # 合規框架要求
    COMPLIANCE_REQUIREMENTS = {
        ComplianceFramework.GDPR: {
            "consent_required": True,
            "data_minimization": True,
            "right_to_erasure": True,
            "data_portability": True,
            "breach_notification_hours": 72,
            "dpo_required": True,
            "impact_assessment": True,
        },
        ComplianceFramework.CCPA: {
            "consent_required": False,  # CCPA 使用 opt-out
            "right_to_know": True,
            "right_to_delete": True,
            "right_to_opt_out": True,
            "non_discrimination": True,
        },
        ComplianceFramework.HIPAA: {
            "phi_protection": True,
            "access_controls": True,
            "audit_trails": True,
            "encryption_required": True,
            "business_associate_agreements": True,
        },
        ComplianceFramework.PDPA: {
            "consent_required": True,
            "purpose_limitation": True,
            "access_correction": True,
            "data_protection_officer": True,
            "cross_border_restrictions": True,
        },
    }

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.privacy_design = PrivacyByDesign(project_name=project_name)
        self.data_sovereignty = DataSovereignty(organization_id=project_name)
        self.consent_manager = ConsentManager()

        # 合規狀態
        self.compliance_status: dict[ComplianceFramework, dict[str, Any]] = {}

    def add_data_field(self, field: DataField) -> None:
        """添加數據欄位"""
        self.privacy_design.add_data_field(field)

    def assess_privacy_design(self) -> dict[str, float]:
        """評估隱私設計"""
        return self.privacy_design.assess()

    def record_consent(
        self,
        user_id: str,
        purpose: str,
        consent_type: ConsentType,
        data_categories: list[DataCategory],
        **kwargs: Any,
    ) -> ConsentRecord:
        """記錄用戶同意"""
        return self.consent_manager.record_consent(
            user_id=user_id,
            purpose=purpose,
            consent_type=consent_type,
            data_categories=data_categories,
            **kwargs,
        )

    def check_consent(self, user_id: str, purpose: str, data_category: DataCategory) -> bool:
        """檢查同意"""
        return self.consent_manager.check_consent(user_id, purpose, data_category)

    def check_compliance(self, framework: ComplianceFramework) -> dict[str, Any]:
        """
        檢查特定合規框架的合規性

        Args:
            framework: 合規框架

        Returns:
            Dict: 合規檢查結果
        """
        requirements: dict[str, Any] = cast(
            dict[str, Any], self.COMPLIANCE_REQUIREMENTS.get(framework, {})
        )
        results: dict[str, bool | float] = {}
        issues: list[str] = []

        # 評估隱私設計
        self.privacy_design.assess()

        # 檢查各項要求
        if requirements.get("consent_required"):
            # 檢查是否有同意管理機制
            has_consent_mechanism = len(self.consent_manager.consents) > 0 or any(
                f.requires_consent for f in self.privacy_design.data_fields.values()
            )
            results["consent_management"] = has_consent_mechanism
            if not has_consent_mechanism:
                issues.append("缺少同意管理機制")

        if requirements.get("data_minimization"):
            # 檢查數據最小化
            pii_ratio = sum(1 for f in self.privacy_design.data_fields.values() if f.is_pii)
            total = len(self.privacy_design.data_fields)
            minimization_score = (1 - pii_ratio / total) * 100 if total > 0 else 100
            results["data_minimization"] = minimization_score >= 70
            if minimization_score < 70:
                issues.append("PII 數據比例過高，建議減少收集")

        if requirements.get("encryption_required"):
            # 檢查加密
            encrypted = sum(1 for f in self.privacy_design.data_fields.values() if f.is_encrypted)
            total = len(self.privacy_design.data_fields)
            encryption_rate = (encrypted / total) * 100 if total > 0 else 0
            results["encryption"] = encryption_rate >= 80
            if encryption_rate < 80:
                issues.append(f"加密覆蓋率不足 ({encryption_rate:.1f}%)")

        if requirements.get("right_to_erasure") or requirements.get("right_to_delete"):
            # 檢查刪除權
            has_deletion = any(f.deletion_policy for f in self.privacy_design.data_fields.values())
            results["right_to_deletion"] = has_deletion
            if not has_deletion:
                issues.append("缺少數據刪除政策")

        # 計算合規分數
        passed = sum(1 for v in results.values() if v is True)
        total_checks = len(results)
        compliance_score = (passed / total_checks) * 100 if total_checks > 0 else 0

        compliance_result = {
            "framework": framework.value,
            "compliance_score": compliance_score,
            "is_compliant": compliance_score >= 80,
            "checks": results,
            "issues": issues,
            "recommendations": self.privacy_design.get_recommendations(),
            "assessed_at": datetime.now().isoformat(),
        }

        self.compliance_status[framework] = compliance_result
        return compliance_result

    def perform_privacy_impact_assessment(self) -> dict[str, Any]:
        """
        執行隱私影響評估 (PIA)

        Returns:
            Dict: PIA 結果
        """
        # 收集數據類型統計
        data_categories = {}
        for data_field in self.privacy_design.data_fields.values():
            cat = data_field.category.value
            if cat not in data_categories:
                data_categories[cat] = {"count": 0, "pii": 0, "encrypted": 0}
            data_categories[cat]["count"] += 1
            if data_field.is_pii:
                data_categories[cat]["pii"] += 1
            if data_field.is_encrypted:
                data_categories[cat]["encrypted"] += 1

        # 評估風險等級
        risk_factors = []
        risk_score = 0

        # 高敏感度數據風險
        high_sensitivity = sum(
            1
            for f in self.privacy_design.data_fields.values()
            if f.sensitivity
            in [
                DataSensitivity.CONFIDENTIAL,
                DataSensitivity.RESTRICTED,
                DataSensitivity.TOP_SECRET,
            ]
        )
        if high_sensitivity > 0:
            risk_factors.append(f"存在 {high_sensitivity} 個高敏感度數據欄位")
            risk_score += high_sensitivity * 10

        # 未加密 PII 風險
        unencrypted_pii = sum(
            1 for f in self.privacy_design.data_fields.values() if f.is_pii and not f.is_encrypted
        )
        if unencrypted_pii > 0:
            risk_factors.append(f"{unencrypted_pii} 個 PII 欄位未加密")
            risk_score += unencrypted_pii * 15

        # 無同意要求風險
        no_consent = sum(
            1
            for f in self.privacy_design.data_fields.values()
            if f.is_pii and not f.requires_consent
        )
        if no_consent > 0:
            risk_factors.append(f"{no_consent} 個 PII 欄位未要求同意")
            risk_score += no_consent * 5

        # 確定風險等級
        if risk_score >= 50:
            risk_level = "HIGH"
        elif risk_score >= 25:
            risk_level = "MEDIUM"
        elif risk_score >= 10:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"

        return {
            "project_name": self.project_name,
            "assessment_date": datetime.now().isoformat(),
            "data_inventory": {
                "total_fields": len(self.privacy_design.data_fields),
                "by_category": data_categories,
            },
            "risk_assessment": {
                "risk_level": risk_level,
                "risk_score": risk_score,
                "risk_factors": risk_factors,
            },
            "design_scores": self.privacy_design.assess(),
            "recommendations": self.privacy_design.get_recommendations(),
            "mitigation_measures": self._generate_mitigation_measures(risk_factors),
        }

    def _generate_mitigation_measures(self, risk_factors: list[str]) -> list[dict[str, str]]:
        """生成風險緩解措施"""
        measures = []

        if any("高敏感度" in rf for rf in risk_factors):
            measures.append(
                {
                    "risk": "高敏感度數據",
                    "measure": "實施分層存取控制和審計日誌",
                    "priority": "HIGH",
                }
            )

        if any("未加密" in rf for rf in risk_factors):
            measures.append(
                {
                    "risk": "未加密 PII",
                    "measure": "對所有 PII 數據實施 AES-256 加密",
                    "priority": "HIGH",
                }
            )

        if any("未要求同意" in rf for rf in risk_factors):
            measures.append(
                {
                    "risk": "缺少同意機制",
                    "measure": "實施同意管理平台，確保用戶明確同意",
                    "priority": "MEDIUM",
                }
            )

        if not measures:
            measures.append(
                {"risk": "無重大風險", "measure": "繼續維持現有隱私保護措施", "priority": "LOW"}
            )

        return measures

    def generate_full_report(self) -> str:
        """生成完整隱私報告"""
        design_scores = self.privacy_design.assess()
        pia = self.perform_privacy_impact_assessment()

        report_lines = [
            "=" * 70,
            "🔒 隱私優先框架 - 完整報告",
            "=" * 70,
            f"專案名稱: {self.project_name}",
            f"報告日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "📊 隱私設計評分",
            "-" * 50,
            f"  總分: {design_scores['overall']:.1f}/100",
            f"  預防性: {design_scores['proactive']:.1f}",
            f"  默認隱私: {design_scores['default_privacy']:.1f}",
            f"  端到端安全: {design_scores['e2e_security']:.1f}",
            f"  透明度: {design_scores['visibility']:.1f}",
            f"  用戶中心: {design_scores['user_centric']:.1f}",
            "",
            "⚠️ 風險評估",
            "-" * 50,
            f"  風險等級: {pia['risk_assessment']['risk_level']}",
            f"  風險分數: {pia['risk_assessment']['risk_score']}",
        ]

        if pia["risk_assessment"]["risk_factors"]:
            report_lines.append("  風險因素:")
            for factor in pia["risk_assessment"]["risk_factors"]:
                report_lines.append(f"    - {factor}")

        report_lines.extend(
            [
                "",
                "💡 建議",
                "-" * 50,
            ]
        )
        for rec in self.privacy_design.get_recommendations():
            report_lines.append(f"  {rec}")

        if self.compliance_status:
            report_lines.extend(
                [
                    "",
                    "📋 合規狀態",
                    "-" * 50,
                ]
            )
            for framework, status in self.compliance_status.items():
                emoji = "✅" if status["is_compliant"] else "❌"
                report_lines.append(
                    f"  {emoji} {framework.value.upper()}: {status['compliance_score']:.1f}%"
                )

        report_lines.extend(
            [
                "",
                "=" * 70,
            ]
        )

        return "\n".join(report_lines)
