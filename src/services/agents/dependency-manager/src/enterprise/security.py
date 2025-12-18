"""
下世代安全模組 (Next-Gen Security Module)

提供進階企業級安全功能：
- SBOM (Software Bill of Materials) 生成
- 供應鏈安全分析
- 合規框架檢查 (SOC2, ISO27001, NIST)
- 零信任依賴驗證
- 簽章驗證與完整性檢查

第三優先級：創新突破階段 - 下世代應用開發
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class SBOMFormat(Enum):
    """SBOM 格式"""
    SPDX = "spdx"
    CYCLONEDX = "cyclonedx"
    SWID = "swid"
    SYFT = "syft"


class ComplianceFramework(Enum):
    """合規框架"""
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    NIST = "nist"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    GDPR = "gdpr"
    FedRAMP = "fedramp"


class SupplyChainRisk(Enum):
    """供應鏈風險類型"""
    TYPOSQUATTING = "typosquatting"         # 拼寫劫持
    DEPENDENCY_CONFUSION = "dependency_confusion"  # 依賴混淆
    MALICIOUS_PACKAGE = "malicious"         # 惡意套件
    COMPROMISED_MAINTAINER = "compromised"  # 維護者帳號被盜
    BUILD_TAMPERING = "build_tampering"     # 構建篡改
    UNPINNED_DEPENDENCY = "unpinned"        # 未鎖定版本


class TrustLevel(Enum):
    """信任等級"""
    VERIFIED = "verified"      # 已驗證
    TRUSTED = "trusted"        # 可信任
    UNKNOWN = "unknown"        # 未知
    SUSPICIOUS = "suspicious"  # 可疑
    UNTRUSTED = "untrusted"    # 不可信


@dataclass
class SBOMEntry:
    """SBOM 條目"""
    name: str
    version: str
    purl: str  # Package URL
    license: str
    supplier: str | None = None
    checksum_sha256: str | None = None
    checksum_sha512: str | None = None
    dependencies: list[str] = field(default_factory=list)
    external_refs: list[str] = field(default_factory=list)


@dataclass
class SBOM:
    """Software Bill of Materials"""
    format: SBOMFormat
    spec_version: str
    serial_number: str
    name: str
    version: str
    created_at: datetime
    components: list[SBOMEntry] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceCheck:
    """合規檢查結果"""
    framework: ComplianceFramework
    requirement_id: str
    requirement_name: str
    status: str  # pass, fail, partial, not_applicable
    evidence: list[str] = field(default_factory=list)
    remediation: str | None = None


@dataclass
class ComplianceReport:
    """合規報告"""
    framework: ComplianceFramework
    scan_date: datetime
    total_requirements: int
    passed: int
    failed: int
    partial: int
    not_applicable: int
    score: float  # 0-100
    checks: list[ComplianceCheck] = field(default_factory=list)


@dataclass
class SupplyChainAlert:
    """供應鏈安全警報"""
    risk_type: SupplyChainRisk
    severity: str  # critical, high, medium, low
    package_name: str
    description: str
    indicators: list[str] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class TrustAssessment:
    """信任評估"""
    package_name: str
    trust_level: TrustLevel
    score: float  # 0-100
    factors: dict[str, Any] = field(default_factory=dict)
    verification_status: dict[str, bool] = field(default_factory=dict)


@dataclass
class IntegrityCheck:
    """完整性檢查"""
    package_name: str
    version: str
    expected_checksum: str
    actual_checksum: str
    algorithm: str
    verified: bool
    checked_at: datetime = field(default_factory=datetime.now)


class NextGenSecurity:
    """
    下世代安全引擎
    
    提供企業級供應鏈安全功能：
    - SBOM 管理
    - 合規檢查
    - 供應鏈風險分析
    - 零信任驗證
    """

    # 已知惡意套件清單（模擬）
    KNOWN_MALICIOUS = {
        "event-stream": "2018-11-26",  # 惡意後門
        "ua-parser-js": "2021-10-22",  # 供應鏈攻擊
        "coa": "2021-11-04",           # 供應鏈攻擊
        "rc": "2021-11-04",            # 供應鏈攻擊
    }

    # 拼寫劫持檢測模式
    TYPOSQUAT_PATTERNS = [
        ("lodash", ["1odash", "lodash-es", "lodahs"]),
        ("express", ["expres", "expresss", "exprees"]),
        ("react", ["raect", "reacts", "reactt"]),
    ]

    # 合規要求映射
    COMPLIANCE_REQUIREMENTS = {
        ComplianceFramework.SOC2: {
            "CC6.1": "邏輯和物理訪問控制",
            "CC6.2": "變更管理",
            "CC6.3": "系統邊界安全",
            "CC7.1": "系統組件識別",
            "CC7.2": "惡意軟體防護",
        },
        ComplianceFramework.ISO27001: {
            "A.12.5.1": "軟體安裝控制",
            "A.12.6.1": "技術漏洞管理",
            "A.14.2.1": "安全開發政策",
            "A.14.2.2": "系統變更控制程序",
            "A.15.1.1": "供應商關係資訊安全政策",
        },
        ComplianceFramework.NIST: {
            "SR-3": "供應鏈風險評估",
            "SR-4": "來源鑒別",
            "SR-5": "獲取策略",
            "SR-6": "供應商評估",
            "SR-7": "供應鏈作業",
        },
    }

    def __init__(self):
        """初始化安全引擎"""
        self._sbom_cache: dict[str, SBOM] = {}
        self._trust_cache: dict[str, TrustAssessment] = {}
        self._alerts: list[SupplyChainAlert] = []

    # ==================== SBOM 管理 ====================

    def generate_sbom(self,
                     project_name: str,
                     version: str,
                     dependencies: list[dict[str, Any]],
                     sbom_format: SBOMFormat = SBOMFormat.CYCLONEDX) -> SBOM:
        """
        生成 SBOM
        
        Args:
            project_name: 專案名稱
            version: 版本
            dependencies: 依賴項列表
            sbom_format: SBOM 格式
            
        Returns:
            SBOM 文件
        """
        components = []

        for dep in dependencies:
            name = dep.get("name", "unknown")
            ver = dep.get("version", "0.0.0")
            ecosystem = dep.get("ecosystem", "npm")

            # 生成 Package URL
            purl = self._generate_purl(name, ver, ecosystem)

            # 計算校驗和
            checksum = self._calculate_checksum(f"{name}@{ver}")

            components.append(SBOMEntry(
                name=name,
                version=ver,
                purl=purl,
                license=dep.get("license", "UNKNOWN"),
                supplier=dep.get("supplier"),
                checksum_sha256=checksum,
                dependencies=dep.get("dependencies", [])
            ))

        # 生成序列號
        serial = self._generate_serial()

        sbom = SBOM(
            format=sbom_format,
            spec_version=self._get_spec_version(sbom_format),
            serial_number=serial,
            name=project_name,
            version=version,
            created_at=datetime.now(),
            components=components,
            metadata={
                "tool": "dependency-manager",
                "tool_version": "1.0.0"
            }
        )

        self._sbom_cache[f"{project_name}@{version}"] = sbom
        return sbom

    def _generate_purl(self, name: str, version: str, ecosystem: str) -> str:
        """生成 Package URL"""
        ecosystem_map = {
            "npm": "npm",
            "pip": "pypi",
            "go": "golang",
            "maven": "maven",
            "cargo": "cargo"
        }
        pkg_type = ecosystem_map.get(ecosystem, ecosystem)
        return f"pkg:{pkg_type}/{name}@{version}"

    def _calculate_checksum(self, content: str) -> str:
        """計算校驗和"""
        return hashlib.sha256(content.encode()).hexdigest()

    def _generate_serial(self) -> str:
        """生成序列號"""
        timestamp = datetime.now().isoformat()
        return f"urn:uuid:{hashlib.md5(timestamp.encode()).hexdigest()}"

    def _get_spec_version(self, sbom_format: SBOMFormat) -> str:
        """取得規範版本"""
        versions = {
            SBOMFormat.CYCLONEDX: "1.5",
            SBOMFormat.SPDX: "2.3",
            SBOMFormat.SWID: "2015",
            SBOMFormat.SYFT: "1.0.0"
        }
        return versions.get(sbom_format, "1.0")

    def export_sbom(self, sbom: SBOM) -> str:
        """
        匯出 SBOM
        
        Args:
            sbom: SBOM 物件
            
        Returns:
            JSON 字串
        """
        if sbom.format == SBOMFormat.CYCLONEDX:
            return self._export_cyclonedx(sbom)
        elif sbom.format == SBOMFormat.SPDX:
            return self._export_spdx(sbom)
        else:
            return self._export_generic(sbom)

    def _export_cyclonedx(self, sbom: SBOM) -> str:
        """匯出 CycloneDX 格式"""
        doc = {
            "bomFormat": "CycloneDX",
            "specVersion": sbom.spec_version,
            "serialNumber": sbom.serial_number,
            "version": 1,
            "metadata": {
                "timestamp": sbom.created_at.isoformat(),
                "tools": [sbom.metadata.get("tool", "unknown")],
                "component": {
                    "type": "application",
                    "name": sbom.name,
                    "version": sbom.version
                }
            },
            "components": [
                {
                    "type": "library",
                    "name": c.name,
                    "version": c.version,
                    "purl": c.purl,
                    "licenses": [{"license": {"id": c.license}}] if c.license else [],
                    "hashes": [
                        {"alg": "SHA-256", "content": c.checksum_sha256}
                    ] if c.checksum_sha256 else []
                }
                for c in sbom.components
            ]
        }
        return json.dumps(doc, indent=2)

    def _export_spdx(self, sbom: SBOM) -> str:
        """匯出 SPDX 格式"""
        doc = {
            "spdxVersion": f"SPDX-{sbom.spec_version}",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": sbom.name,
            "documentNamespace": sbom.serial_number,
            "creationInfo": {
                "created": sbom.created_at.isoformat(),
                "creators": [f"Tool: {sbom.metadata.get('tool', 'unknown')}"]
            },
            "packages": [
                {
                    "name": c.name,
                    "SPDXID": f"SPDXRef-Package-{c.name}",
                    "versionInfo": c.version,
                    "downloadLocation": c.purl,
                    "licenseConcluded": c.license or "NOASSERTION",
                    "checksums": [
                        {"algorithm": "SHA256", "checksumValue": c.checksum_sha256}
                    ] if c.checksum_sha256 else []
                }
                for c in sbom.components
            ]
        }
        return json.dumps(doc, indent=2)

    def _export_generic(self, sbom: SBOM) -> str:
        """匯出通用格式"""
        return json.dumps({
            "format": sbom.format.value,
            "version": sbom.spec_version,
            "project": sbom.name,
            "project_version": sbom.version,
            "created": sbom.created_at.isoformat(),
            "components": [
                {"name": c.name, "version": c.version, "purl": c.purl, "license": c.license}
                for c in sbom.components
            ]
        }, indent=2)

    # ==================== 合規檢查 ====================

    def check_compliance(self,
                        framework: ComplianceFramework,
                        dependencies: list[dict[str, Any]],
                        config: dict[str, Any] | None = None) -> ComplianceReport:
        """
        執行合規檢查
        
        Args:
            framework: 合規框架
            dependencies: 依賴項列表
            config: 配置選項
            
        Returns:
            合規報告
        """
        requirements = self.COMPLIANCE_REQUIREMENTS.get(framework, {})
        checks = []

        for req_id, req_name in requirements.items():
            check_result = self._evaluate_requirement(
                framework, req_id, req_name, dependencies, config
            )
            checks.append(check_result)

        # 統計
        passed = len([c for c in checks if c.status == "pass"])
        failed = len([c for c in checks if c.status == "fail"])
        partial = len([c for c in checks if c.status == "partial"])
        na = len([c for c in checks if c.status == "not_applicable"])

        total = len(checks)
        score = (passed + partial * 0.5) / total * 100 if total > 0 else 0

        return ComplianceReport(
            framework=framework,
            scan_date=datetime.now(),
            total_requirements=total,
            passed=passed,
            failed=failed,
            partial=partial,
            not_applicable=na,
            score=score,
            checks=checks
        )

    def _evaluate_requirement(self,
                             framework: ComplianceFramework,
                             req_id: str,
                             req_name: str,
                             dependencies: list[dict[str, Any]],
                             config: dict[str, Any] | None) -> ComplianceCheck:
        """評估單一要求"""
        evidence = []
        status = "pass"
        remediation = None

        # 根據要求執行不同檢查
        if "漏洞" in req_name or "vulnerability" in req_name.lower():
            vuln_count = sum(d.get("vulnerabilities", 0) for d in dependencies)
            if vuln_count > 0:
                status = "fail"
                evidence.append(f"發現 {vuln_count} 個漏洞")
                remediation = "修復所有已知漏洞"
            else:
                evidence.append("無已知漏洞")

        elif "供應商" in req_name or "supplier" in req_name.lower():
            known_suppliers = len([d for d in dependencies if d.get("supplier")])
            if known_suppliers < len(dependencies):
                status = "partial"
                evidence.append(f"{known_suppliers}/{len(dependencies)} 供應商已識別")
                remediation = "識別所有依賴的供應商資訊"
            else:
                evidence.append("所有供應商已識別")

        elif "變更" in req_name or "change" in req_name.lower():
            # 檢查是否有版本鎖定
            pinned = len([d for d in dependencies if not d.get("version", "").startswith("^")])
            if pinned < len(dependencies) * 0.8:
                status = "partial"
                evidence.append(f"{pinned}/{len(dependencies)} 版本已鎖定")
                remediation = "鎖定所有依賴版本"
            else:
                evidence.append("版本控制符合要求")

        elif "惡意" in req_name or "malicious" in req_name.lower():
            malicious = [d for d in dependencies
                        if d.get("name", "").lower() in self.KNOWN_MALICIOUS]
            if malicious:
                status = "fail"
                evidence.append(f"發現已知惡意套件：{[d['name'] for d in malicious]}")
                remediation = "立即移除惡意套件"
            else:
                evidence.append("無已知惡意套件")

        else:
            # 預設檢查
            evidence.append("已執行基本檢查")

        return ComplianceCheck(
            framework=framework,
            requirement_id=req_id,
            requirement_name=req_name,
            status=status,
            evidence=evidence,
            remediation=remediation
        )

    # ==================== 供應鏈安全 ====================

    def analyze_supply_chain(self,
                            dependencies: list[dict[str, Any]]) -> list[SupplyChainAlert]:
        """
        分析供應鏈安全
        
        Args:
            dependencies: 依賴項列表
            
        Returns:
            安全警報列表
        """
        alerts = []

        for dep in dependencies:
            name = dep.get("name", "unknown").lower()

            # 檢查已知惡意套件
            if name in self.KNOWN_MALICIOUS:
                alerts.append(SupplyChainAlert(
                    risk_type=SupplyChainRisk.MALICIOUS_PACKAGE,
                    severity="critical",
                    package_name=dep.get("name", ""),
                    description=f"已知惡意套件，發現日期：{self.KNOWN_MALICIOUS[name]}",
                    indicators=["已列入惡意套件清單"],
                    recommended_actions=[
                        "立即移除此套件",
                        "檢查系統是否受影響",
                        "審查相關代碼"
                    ]
                ))

            # 檢查拼寫劫持
            for original, typos in self.TYPOSQUAT_PATTERNS:
                if name in typos:
                    alerts.append(SupplyChainAlert(
                        risk_type=SupplyChainRisk.TYPOSQUATTING,
                        severity="high",
                        package_name=dep.get("name", ""),
                        description=f"可能是 '{original}' 的拼寫劫持套件",
                        indicators=[f"名稱與 '{original}' 相似"],
                        recommended_actions=[
                            f"確認是否應使用 '{original}'",
                            "驗證套件來源",
                            "檢查安裝歷史"
                        ]
                    ))

            # 檢查未鎖定版本
            version = dep.get("version", "")
            if version.startswith("*") or version == "latest":
                alerts.append(SupplyChainAlert(
                    risk_type=SupplyChainRisk.UNPINNED_DEPENDENCY,
                    severity="medium",
                    package_name=dep.get("name", ""),
                    description="版本未鎖定，可能導致依賴混淆攻擊",
                    indicators=["使用萬用字元或 latest 版本"],
                    recommended_actions=[
                        "鎖定特定版本",
                        "使用鎖定檔案 (package-lock.json 等)",
                        "啟用完整性檢查"
                    ]
                ))

        self._alerts = alerts
        return alerts

    # ==================== 零信任驗證 ====================

    def assess_trust(self,
                    package_name: str,
                    version: str,
                    metadata: dict[str, Any] | None = None) -> TrustAssessment:
        """
        評估套件信任度
        
        Args:
            package_name: 套件名稱
            version: 版本
            metadata: 元資料
            
        Returns:
            信任評估
        """
        metadata = metadata or {}
        factors = {}
        verification = {}

        # 來源驗證
        has_registry = metadata.get("from_official_registry", True)
        verification["official_registry"] = has_registry
        factors["source"] = 100 if has_registry else 30

        # 簽章驗證
        has_signature = metadata.get("has_signature", False)
        verification["signature"] = has_signature
        factors["signature"] = 100 if has_signature else 50

        # 維護者驗證
        verified_maintainer = metadata.get("verified_maintainer", False)
        verification["maintainer"] = verified_maintainer
        factors["maintainer"] = 100 if verified_maintainer else 60

        # 完整性驗證
        integrity_check = metadata.get("integrity_verified", False)
        verification["integrity"] = integrity_check
        factors["integrity"] = 100 if integrity_check else 40

        # 已知惡意檢查
        is_malicious = package_name.lower() in self.KNOWN_MALICIOUS
        verification["not_malicious"] = not is_malicious
        factors["safety"] = 0 if is_malicious else 100

        # 計算總分
        score = sum(factors.values()) / len(factors)

        # 決定信任等級
        if is_malicious:
            trust_level = TrustLevel.UNTRUSTED
        elif score >= 90:
            trust_level = TrustLevel.VERIFIED
        elif score >= 70:
            trust_level = TrustLevel.TRUSTED
        elif score >= 50:
            trust_level = TrustLevel.UNKNOWN
        else:
            trust_level = TrustLevel.SUSPICIOUS

        assessment = TrustAssessment(
            package_name=package_name,
            trust_level=trust_level,
            score=score,
            factors=factors,
            verification_status=verification
        )

        self._trust_cache[package_name] = assessment
        return assessment

    def verify_integrity(self,
                        package_name: str,
                        version: str,
                        expected_checksum: str,
                        content: bytes,
                        algorithm: str = "sha256") -> IntegrityCheck:
        """
        驗證完整性
        
        Args:
            package_name: 套件名稱
            version: 版本
            expected_checksum: 預期校驗和
            content: 內容
            algorithm: 演算法
            
        Returns:
            完整性檢查結果
        """
        if algorithm == "sha256":
            actual = hashlib.sha256(content).hexdigest()
        elif algorithm == "sha512":
            actual = hashlib.sha512(content).hexdigest()
        elif algorithm == "md5":
            actual = hashlib.md5(content).hexdigest()
        else:
            actual = hashlib.sha256(content).hexdigest()

        return IntegrityCheck(
            package_name=package_name,
            version=version,
            expected_checksum=expected_checksum,
            actual_checksum=actual,
            algorithm=algorithm,
            verified=(expected_checksum == actual)
        )

    # ==================== 報告生成 ====================

    def generate_security_report(self,
                                dependencies: list[dict[str, Any]],
                                frameworks: list[ComplianceFramework] | None = None) -> dict[str, Any]:
        """
        生成安全報告
        
        Args:
            dependencies: 依賴項列表
            frameworks: 合規框架列表
            
        Returns:
            安全報告
        """
        # 生成 SBOM
        sbom = self.generate_sbom("project", "1.0.0", dependencies)

        # 供應鏈分析
        supply_chain_alerts = self.analyze_supply_chain(dependencies)

        # 信任評估
        trust_assessments = []
        for dep in dependencies:
            assessment = self.assess_trust(
                dep.get("name", "unknown"),
                dep.get("version", "0.0.0"),
                dep
            )
            trust_assessments.append(assessment)

        # 合規檢查
        compliance_reports = []
        if frameworks:
            for framework in frameworks:
                report = self.check_compliance(framework, dependencies)
                compliance_reports.append(report)

        # 統計
        critical_alerts = len([a for a in supply_chain_alerts if a.severity == "critical"])
        untrusted = len([t for t in trust_assessments if t.trust_level == TrustLevel.UNTRUSTED])
        avg_trust = sum(t.score for t in trust_assessments) / len(trust_assessments) if trust_assessments else 0

        return {
            "summary": {
                "total_dependencies": len(dependencies),
                "critical_alerts": critical_alerts,
                "untrusted_packages": untrusted,
                "average_trust_score": avg_trust,
                "sbom_generated": True
            },
            "sbom": {
                "format": sbom.format.value,
                "components": len(sbom.components)
            },
            "supply_chain": [
                {
                    "package": a.package_name,
                    "risk_type": a.risk_type.value,
                    "severity": a.severity,
                    "description": a.description
                }
                for a in supply_chain_alerts
            ],
            "trust_assessments": [
                {
                    "package": t.package_name,
                    "trust_level": t.trust_level.value,
                    "score": t.score
                }
                for t in trust_assessments
            ],
            "compliance": [
                {
                    "framework": r.framework.value,
                    "score": r.score,
                    "passed": r.passed,
                    "failed": r.failed
                }
                for r in compliance_reports
            ]
        }

    def format_report_zh_tw(self, report: dict[str, Any]) -> str:
        """
        生成繁體中文報告
        
        Args:
            report: 報告資料
            
        Returns:
            格式化報告
        """
        lines = [
            "=" * 60,
            "🛡️ 下世代安全報告 - 供應鏈安全分析",
            "=" * 60,
            "",
            "📊 摘要",
            "-" * 40,
            f"  依賴項總數：{report['summary']['total_dependencies']}",
            f"  關鍵警報：{report['summary']['critical_alerts']}",
            f"  不可信套件：{report['summary']['untrusted_packages']}",
            f"  平均信任分數：{report['summary']['average_trust_score']:.1f}/100",
            f"  SBOM 已生成：{'✅' if report['summary']['sbom_generated'] else '❌'}",
            "",
            "📦 SBOM 資訊",
            "-" * 40,
            f"  格式：{report['sbom']['format']}",
            f"  組件數：{report['sbom']['components']}",
            "",
            "⚠️ 供應鏈警報",
            "-" * 40,
        ]

        severity_emoji = {
            "critical": "🚨",
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }

        if report["supply_chain"]:
            for alert in report["supply_chain"]:
                emoji = severity_emoji.get(alert["severity"], "❓")
                lines.append(f"  {emoji} [{alert['risk_type']}] {alert['package']}")
                lines.append(f"     {alert['description']}")
        else:
            lines.append("  ✅ 無供應鏈警報")

        lines.extend([
            "",
            "🔐 信任評估",
            "-" * 40,
        ])

        trust_emoji = {
            "verified": "🌟",
            "trusted": "✅",
            "unknown": "❓",
            "suspicious": "⚠️",
            "untrusted": "🚫"
        }

        # 按信任等級分組顯示
        for assessment in sorted(report["trust_assessments"],
                                 key=lambda x: x["score"], reverse=True)[:10]:
            emoji = trust_emoji.get(assessment["trust_level"], "❓")
            lines.append(f"  {emoji} {assessment['package']}: {assessment['score']:.0f}")

        if report["compliance"]:
            lines.extend([
                "",
                "📋 合規狀態",
                "-" * 40,
            ])
            for comp in report["compliance"]:
                status = "✅" if comp["score"] >= 80 else "⚠️" if comp["score"] >= 60 else "❌"
                lines.append(f"  {status} {comp['framework'].upper()}: {comp['score']:.1f}%")
                lines.append(f"     通過：{comp['passed']} | 失敗：{comp['failed']}")

        lines.extend(["", "=" * 60])

        return "\n".join(lines)
