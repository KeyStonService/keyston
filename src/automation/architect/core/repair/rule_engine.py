"""
Rule Engine - 規則引擎
基於規則的自動代碼修復
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


@dataclass
class RepairRule:
    """修復規則數據類"""
    name: str
    pattern: str
    replacement: str
    description: str
    auto_apply: bool = False


@dataclass
class RepairResult:
    """修復結果數據類"""
    file_path: str
    rules_applied: List[str]
    changes_made: int
    success: bool
    message: str


class RuleEngine:
    """
    規則引擎
    
    基於預定義規則自動修復代碼問題：
    - 代碼風格修復
    - 簡單語法修復
    - 廢棄代碼替換
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化規則引擎"""
        self.config = config or {}
        self.rules: List[RepairRule] = []
        self._load_default_rules()
        logger.info('RuleEngine initialized')
    
    def _load_default_rules(self):
        """加載默認修復規則"""
        self.rules = [
            RepairRule(
                name='trailing-whitespace',
                pattern=r'\s+$',
                replacement='',
                description='Remove trailing whitespace',
                auto_apply=True
            ),
            RepairRule(
                name='var-to-const',
                pattern=r'\bvar\s+',
                replacement='const ',
                description='Replace var with const',
                auto_apply=False
            ),
            RepairRule(
                name='double-quotes-to-single',
                pattern=r'"([^"]*)"',
                replacement=r"'\1'",
                description='Use single quotes instead of double quotes',
                auto_apply=False
            ),
        ]
    
    def add_rule(self, rule: RepairRule):
        """
        添加自定義修復規則
        
        Args:
            rule: 修復規則
        """
        self.rules.append(rule)
        logger.info(f'Added repair rule: {rule.name}')
    
    async def apply_fixes(
        self,
        file_path: str,
        auto_only: bool = True
    ) -> RepairResult:
        """
        應用修復規則
        
        Args:
            file_path: 文件路徑
            auto_only: 僅應用自動修復規則
            
        Returns:
            RepairResult: 修復結果
        """
        logger.info(f'Applying fixes to: {file_path}')
        
        path = Path(file_path)
        if not path.exists():
            return RepairResult(
                file_path=file_path,
                rules_applied=[],
                changes_made=0,
                success=False,
                message='File not found'
            )
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            rules_applied = []
            
            for rule in self.rules:
                if auto_only and not rule.auto_apply:
                    continue
                
                import re
                new_content = re.sub(rule.pattern, rule.replacement, content)
                if new_content != content:
                    content = new_content
                    rules_applied.append(rule.name)
                    logger.debug(f'Applied rule: {rule.name}')
            
            changes_made = sum(1 for a, b in zip(original_content, content) if a != b)
            
            if changes_made > 0:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return RepairResult(
                file_path=file_path,
                rules_applied=rules_applied,
                changes_made=changes_made,
                success=True,
                message=f'Applied {len(rules_applied)} rules, {changes_made} changes'
            )
        
        except Exception as e:
            logger.error(f'Error applying fixes: {e}')
            return RepairResult(
                file_path=file_path,
                rules_applied=[],
                changes_made=0,
                success=False,
                message=str(e)
            )
