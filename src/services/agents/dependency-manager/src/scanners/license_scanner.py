"""
許可證掃描器 - License Scanner
檢查依賴項的許可證合規性
"""

import logging
from dataclasses import dataclass, field
from enum import Enum

from ..models.dependency import Dependency, Ecosystem

logger = logging.getLogger(__name__)


class LicenseCategory(Enum):
    """許可證類別"""
    PERMISSIVE = "permissive"       # 寬鬆許可證
    COPYLEFT = "copyleft"           # Copyleft 許可證
    WEAK_COPYLEFT = "weak_copyleft" # 弱 Copyleft
    PROPRIETARY = "proprietary"     # 專有許可證
    UNKNOWN = "unknown"             # 未知


class ComplianceStatus(Enum):
    """合規狀態"""
    ALLOWED = "allowed"     # 允許使用
    WARNING = "warning"     # 需要注意
    BLOCKED = "blocked"     # 禁止使用
    UNKNOWN = "unknown"     # 未知


@dataclass
class LicensePolicy:
    """
    許可證政策配置
    
    定義哪些許可證被允許、警告或禁止
    """
    allowed: set[str] = field(default_factory=lambda: {
        "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause",
        "ISC", "CC0-1.0", "Unlicense", "0BSD"
    })
    warning: set[str] = field(default_factory=lambda: {
        "LGPL-2.1", "LGPL-3.0", "MPL-2.0", "EPL-1.0", "EPL-2.0"
    })
    blocked: set[str] = field(default_factory=lambda: {
        "GPL-2.0", "GPL-3.0", "AGPL-3.0", "SSPL-1.0"
    })
    exceptions: dict[str, str] = field(default_factory=dict)


@dataclass
class LicenseInfo:
    """
    許可證資訊
    
    Attributes:
        package: 套件名稱
        license_id: SPDX 許可證 ID
        license_name: 許可證名稱
        category: 許可證類別
        status: 合規狀態
        url: 許可證連結
    """
    package: str
    license_id: str
    license_name: str = ""
    category: LicenseCategory = LicenseCategory.UNKNOWN
    status: ComplianceStatus = ComplianceStatus.UNKNOWN
    url: str | None = None

    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            "package": self.package,
            "license_id": self.license_id,
            "license_name": self.license_name,
            "category": self.category.value,
            "status": self.status.value,
            "url": self.url
        }


@dataclass
class LicenseScanResult:
    """
    許可證掃描結果
    
    Attributes:
        scan_id: 掃描 ID
        licenses: 許可證資訊列表
        allowed_count: 允許的數量
        warning_count: 警告的數量
        blocked_count: 禁止的數量
        unknown_count: 未知的數量
    """
    scan_id: str
    licenses: list[LicenseInfo] = field(default_factory=list)
    allowed_count: int = 0
    warning_count: int = 0
    blocked_count: int = 0
    unknown_count: int = 0

    def add_license(self, license_info: LicenseInfo) -> None:
        """添加許可證資訊"""
        self.licenses.append(license_info)

        if license_info.status == ComplianceStatus.ALLOWED:
            self.allowed_count += 1
        elif license_info.status == ComplianceStatus.WARNING:
            self.warning_count += 1
        elif license_info.status == ComplianceStatus.BLOCKED:
            self.blocked_count += 1
        else:
            self.unknown_count += 1

    def has_compliance_issues(self) -> bool:
        """檢查是否有合規問題"""
        return self.blocked_count > 0

    def get_blocked_packages(self) -> list[LicenseInfo]:
        """獲取被禁止的套件"""
        return [l for l in self.licenses if l.status == ComplianceStatus.BLOCKED]

    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            "scan_id": self.scan_id,
            "summary": {
                "total": len(self.licenses),
                "allowed": self.allowed_count,
                "warning": self.warning_count,
                "blocked": self.blocked_count,
                "unknown": self.unknown_count
            },
            "licenses": [l.to_dict() for l in self.licenses]
        }


class LicenseScanner:
    """
    許可證掃描器
    
    檢查依賴項的許可證合規性
    """

    # 許可證類別映射
    LICENSE_CATEGORIES = {
        # 寬鬆許可證
        "MIT": LicenseCategory.PERMISSIVE,
        "Apache-2.0": LicenseCategory.PERMISSIVE,
        "BSD-2-Clause": LicenseCategory.PERMISSIVE,
        "BSD-3-Clause": LicenseCategory.PERMISSIVE,
        "ISC": LicenseCategory.PERMISSIVE,
        "CC0-1.0": LicenseCategory.PERMISSIVE,
        "Unlicense": LicenseCategory.PERMISSIVE,
        "0BSD": LicenseCategory.PERMISSIVE,

        # 弱 Copyleft
        "LGPL-2.1": LicenseCategory.WEAK_COPYLEFT,
        "LGPL-3.0": LicenseCategory.WEAK_COPYLEFT,
        "MPL-2.0": LicenseCategory.WEAK_COPYLEFT,
        "EPL-1.0": LicenseCategory.WEAK_COPYLEFT,
        "EPL-2.0": LicenseCategory.WEAK_COPYLEFT,

        # 強 Copyleft
        "GPL-2.0": LicenseCategory.COPYLEFT,
        "GPL-3.0": LicenseCategory.COPYLEFT,
        "AGPL-3.0": LicenseCategory.COPYLEFT,

        # 專有
        "SSPL-1.0": LicenseCategory.PROPRIETARY,
    }

    def __init__(self, policy: LicensePolicy | None = None):
        """
        初始化許可證掃描器
        
        Args:
            policy: 許可證政策，如未提供則使用默認政策
        """
        self.policy = policy or LicensePolicy()
        logger.info("許可證掃描器初始化完成")

    async def scan(
        self,
        dependencies: list[Dependency]
    ) -> LicenseScanResult:
        """
        掃描依賴項列表的許可證
        
        Args:
            dependencies: 待掃描的依賴項列表
            
        Returns:
            許可證掃描結果
        """
        import uuid
        scan_id = f"license-{uuid.uuid4().hex[:8]}"
        result = LicenseScanResult(scan_id=scan_id)

        logger.info(f"開始許可證掃描 [{scan_id}]: {len(dependencies)} 個依賴項")

        for dep in dependencies:
            license_info = await self._check_license(dep)
            result.add_license(license_info)

            # 更新依賴項的許可證資訊
            dep.license = license_info.license_id

        logger.info(
            f"掃描完成 [{scan_id}]: "
            f"允許: {result.allowed_count}, "
            f"警告: {result.warning_count}, "
            f"禁止: {result.blocked_count}"
        )

        return result

    async def _check_license(self, dep: Dependency) -> LicenseInfo:
        """
        檢查單個依賴項的許可證
        
        Args:
            dep: 依賴項
            
        Returns:
            許可證資訊
        """
        # 獲取許可證 ID（實際需要從 registry 獲取）
        license_id = await self._get_license(dep.name, dep.ecosystem)

        if not license_id:
            return LicenseInfo(
                package=dep.name,
                license_id="UNKNOWN",
                status=ComplianceStatus.UNKNOWN
            )

        # 判斷許可證類別
        category = self.LICENSE_CATEGORIES.get(license_id, LicenseCategory.UNKNOWN)

        # 判斷合規狀態
        status = self._check_compliance(dep.name, license_id)

        return LicenseInfo(
            package=dep.name,
            license_id=license_id,
            category=category,
            status=status
        )

    async def _get_license(
        self,
        package_name: str,
        ecosystem: Ecosystem
    ) -> str | None:
        """
        獲取套件的許可證
        
        Args:
            package_name: 套件名稱
            ecosystem: 生態系統
            
        Returns:
            許可證 ID
        """
        # 框架實現，實際需要查詢各生態系統的 registry
        logger.debug(f"獲取 {package_name} 許可證")
        return None

    def _check_compliance(
        self,
        package_name: str,
        license_id: str
    ) -> ComplianceStatus:
        """
        檢查許可證合規狀態
        
        Args:
            package_name: 套件名稱
            license_id: 許可證 ID
            
        Returns:
            合規狀態
        """
        # 檢查是否有例外
        if package_name in self.policy.exceptions:
            logger.debug(f"{package_name} 有許可證例外配置")
            return ComplianceStatus.ALLOWED

        # 正規化許可證 ID
        normalized_id = self._normalize_license_id(license_id)

        if normalized_id in self.policy.blocked:
            return ComplianceStatus.BLOCKED
        elif normalized_id in self.policy.warning:
            return ComplianceStatus.WARNING
        elif normalized_id in self.policy.allowed:
            return ComplianceStatus.ALLOWED

        return ComplianceStatus.UNKNOWN

    def _normalize_license_id(self, license_id: str) -> str:
        """
        正規化許可證 ID
        
        處理常見的變體形式
        
        Args:
            license_id: 原始許可證 ID
            
        Returns:
            正規化後的許可證 ID
        """
        # 移除常見的後綴
        normalized = license_id.strip()

        # 處理 "+" 後綴（如 GPL-3.0+）
        if normalized.endswith('+'):
            normalized = normalized[:-1]

        # 處理 "-only" 和 "-or-later" 後綴
        for suffix in ['-only', '-or-later']:
            if normalized.endswith(suffix):
                normalized = normalized.replace(suffix, '')

        return normalized

    def add_exception(self, package: str, reason: str) -> None:
        """
        添加許可證例外
        
        Args:
            package: 套件名稱
            reason: 例外原因
        """
        self.policy.exceptions[package] = reason
        logger.info(f"添加許可證例外: {package} - {reason}")
