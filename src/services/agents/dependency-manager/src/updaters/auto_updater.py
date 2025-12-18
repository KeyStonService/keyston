"""
自動更新器 - Auto Updater
根據策略自動更新依賴項
"""

import logging
import re
import uuid
from dataclasses import dataclass

from ..models.dependency import Dependency, Ecosystem
from ..models.update import Update, UpdatePolicy, UpdateResult, UpdateStatus, UpdateType

logger = logging.getLogger(__name__)


@dataclass
class UpdateConfig:
    """
    更新配置
    
    Attributes:
        patch_policy: Patch 版本更新策略
        minor_policy: Minor 版本更新策略
        major_policy: Major 版本更新策略
        security_auto_update: 是否自動更新安全修復
        dry_run: 是否為演練模式（不實際執行更新）
    """
    patch_policy: UpdatePolicy = UpdatePolicy.AUTO
    minor_policy: UpdatePolicy = UpdatePolicy.PR
    major_policy: UpdatePolicy = UpdatePolicy.MANUAL
    security_auto_update: bool = True
    dry_run: bool = False


@dataclass
class VersionParts:
    """版本號組成部分"""
    major: int = 0
    minor: int = 0
    patch: int = 0
    prerelease: str | None = None

    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        return version


class AutoUpdater:
    """
    自動更新器
    
    根據配置的策略自動更新依賴項
    """

    def __init__(self, config: UpdateConfig | None = None):
        """
        初始化自動更新器
        
        Args:
            config: 更新配置
        """
        self.config = config or UpdateConfig()
        logger.info("自動更新器初始化完成")

    async def update(
        self,
        dependencies: list[Dependency],
        security_fixes: list[str] | None = None
    ) -> UpdateResult:
        """
        更新依賴項
        
        Args:
            dependencies: 待更新的依賴項列表
            security_fixes: 需要安全修復的套件名稱列表
            
        Returns:
            更新結果
        """
        result_id = f"update-{uuid.uuid4().hex[:8]}"
        result = UpdateResult(result_id=result_id)
        security_fixes = security_fixes or []

        logger.info(f"開始更新 [{result_id}]: {len(dependencies)} 個依賴項")

        # 篩選需要更新的依賴項
        outdated = [d for d in dependencies if d.is_outdated() and d.latest_version]

        for dep in outdated:
            update = self._create_update(dep, dep.name in security_fixes)

            # 根據策略決定是否執行更新
            if self._should_update(update):
                update = await self._execute_update(update, dep.ecosystem)
            else:
                update.status = UpdateStatus.SKIPPED

            result.add_update(update)

        logger.info(
            f"更新完成 [{result_id}]: "
            f"成功: {result.success_count}, "
            f"失敗: {result.failed_count}, "
            f"跳過: {result.skipped_count}"
        )

        return result

    def _create_update(
        self,
        dep: Dependency,
        is_security_fix: bool
    ) -> Update:
        """
        創建更新對象
        
        Args:
            dep: 依賴項
            is_security_fix: 是否為安全修復
            
        Returns:
            更新對象
        """
        update_type = self._classify_update(
            dep.current_version,
            dep.latest_version or dep.current_version
        )

        policy = self._get_policy(update_type, is_security_fix)

        return Update(
            package=dep.name,
            from_version=dep.current_version,
            to_version=dep.latest_version or dep.current_version,
            update_type=update_type,
            policy=policy,
            is_security_fix=is_security_fix,
            breaking_changes=(update_type == UpdateType.MAJOR)
        )

    def _classify_update(self, current: str, latest: str) -> UpdateType:
        """
        分類更新類型
        
        Args:
            current: 當前版本
            latest: 最新版本
            
        Returns:
            更新類型
        """
        current_parts = self._parse_version(current)
        latest_parts = self._parse_version(latest)

        if latest_parts.major > current_parts.major:
            return UpdateType.MAJOR
        elif latest_parts.minor > current_parts.minor:
            return UpdateType.MINOR
        elif latest_parts.patch > current_parts.patch:
            return UpdateType.PATCH

        return UpdateType.UNKNOWN

    def _parse_version(self, version: str) -> VersionParts:
        """
        解析版本號
        
        支援標準 SemVer 格式: major.minor.patch[-prerelease]
        
        Args:
            version: 版本字符串
            
        Returns:
            版本部分
        """
        # 移除 v 前綴
        if version.startswith('v'):
            version = version[1:]

        # 匹配 SemVer 格式
        match = re.match(
            r'^(\d+)\.(\d+)\.(\d+)(?:-(.+))?$',
            version
        )

        if match:
            return VersionParts(
                major=int(match.group(1)),
                minor=int(match.group(2)),
                patch=int(match.group(3)),
                prerelease=match.group(4)
            )

        # 嘗試簡化格式
        parts = version.split('.')
        try:
            return VersionParts(
                major=int(parts[0]) if len(parts) > 0 else 0,
                minor=int(parts[1]) if len(parts) > 1 else 0,
                patch=int(parts[2].split('-')[0]) if len(parts) > 2 else 0
            )
        except (ValueError, IndexError):
            return VersionParts()

    def _get_policy(
        self,
        update_type: UpdateType,
        is_security_fix: bool
    ) -> UpdatePolicy:
        """
        獲取更新策略
        
        Args:
            update_type: 更新類型
            is_security_fix: 是否為安全修復
            
        Returns:
            更新策略
        """
        # 安全修復優先自動更新
        if is_security_fix and self.config.security_auto_update:
            return UpdatePolicy.AUTO

        # 根據更新類型返回對應策略
        if update_type == UpdateType.PATCH:
            return self.config.patch_policy
        elif update_type == UpdateType.MINOR:
            return self.config.minor_policy
        elif update_type == UpdateType.MAJOR:
            return self.config.major_policy

        return UpdatePolicy.MANUAL

    def _should_update(self, update: Update) -> bool:
        """
        判斷是否應該執行更新
        
        Args:
            update: 更新對象
            
        Returns:
            是否應該更新
        """
        if self.config.dry_run:
            logger.info(f"[演練模式] 跳過更新: {update}")
            return False

        if update.policy == UpdatePolicy.SKIP:
            return False

        if update.policy == UpdatePolicy.MANUAL:
            logger.info(f"需要手動更新: {update}")
            return False

        return True

    async def _execute_update(
        self,
        update: Update,
        ecosystem: Ecosystem
    ) -> Update:
        """
        執行更新
        
        Args:
            update: 更新對象
            ecosystem: 生態系統
            
        Returns:
            更新後的對象
        """
        logger.info(f"執行更新: {update}")

        try:
            # 根據生態系統執行對應的更新命令
            # 框架實現，實際需要執行命令行工具

            if ecosystem == Ecosystem.NPM:
                success = await self._update_npm(update)
            elif ecosystem == Ecosystem.PIP:
                success = await self._update_pip(update)
            else:
                logger.warning(f"不支援的生態系統: {ecosystem}")
                success = False

            if success:
                update.status = UpdateStatus.SUCCESS
                logger.info(f"更新成功: {update}")
            else:
                update.status = UpdateStatus.FAILED
                update.error_message = "更新命令執行失敗"

        except Exception as e:
            update.status = UpdateStatus.FAILED
            update.error_message = str(e)
            logger.error(f"更新失敗: {update} - {e}")

        return update

    async def _update_npm(self, update: Update) -> bool:
        """
        執行 NPM 更新
        
        實際實現需要執行: npm install {package}@{version}
        
        Args:
            update: 更新對象
            
        Returns:
            是否成功
        """
        logger.debug(f"NPM 更新: {update.package}@{update.to_version}")
        # 框架實現
        return True

    async def _update_pip(self, update: Update) -> bool:
        """
        執行 pip 更新
        
        實際實現需要執行: pip install {package}=={version}
        
        Args:
            update: 更新對象
            
        Returns:
            是否成功
        """
        logger.debug(f"pip 更新: {update.package}=={update.to_version}")
        # 框架實現
        return True

    async def rollback(self, update: Update) -> bool:
        """
        回滾更新
        
        Args:
            update: 要回滾的更新
            
        Returns:
            是否成功
        """
        logger.info(f"回滾更新: {update}")

        try:
            # 執行回滾邏輯
            update.status = UpdateStatus.ROLLED_BACK
            return True
        except Exception as e:
            logger.error(f"回滾失敗: {e}")
            return False
