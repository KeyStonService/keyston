"""
語言邊界模組 - Language Boundary Module
確保輸出始終維持繁體中文的一致性
"""

import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class OutputLanguage(Enum):
    """輸出語言"""
    ZH_TW = "zh-TW"     # 繁體中文
    ZH_CN = "zh-CN"     # 簡體中文
    EN = "en"           # 英文
    JA = "ja"           # 日文


@dataclass
class TranslationEntry:
    """翻譯條目"""
    key: str
    zh_tw: str
    en: str = ""
    zh_cn: str = ""
    
    def get(self, lang: OutputLanguage) -> str:
        """獲取指定語言的翻譯"""
        if lang == OutputLanguage.ZH_TW:
            return self.zh_tw
        elif lang == OutputLanguage.EN:
            return self.en or self.zh_tw
        elif lang == OutputLanguage.ZH_CN:
            return self.zh_cn or self.zh_tw
        return self.zh_tw


class LanguageRegistry:
    """
    語言註冊表
    
    管理所有可翻譯的文字內容
    """
    
    # 核心術語翻譯
    TERMS = {
        # 依賴相關
        "dependency": TranslationEntry("dependency", "依賴項", "Dependency", "依赖项"),
        "dependencies": TranslationEntry("dependencies", "依賴項", "Dependencies", "依赖项"),
        "direct_dependency": TranslationEntry("direct_dependency", "直接依賴", "Direct Dependency", "直接依赖"),
        "transitive_dependency": TranslationEntry("transitive_dependency", "傳遞依賴", "Transitive Dependency", "传递依赖"),
        "dev_dependency": TranslationEntry("dev_dependency", "開發依賴", "Dev Dependency", "开发依赖"),
        "outdated": TranslationEntry("outdated", "過時", "Outdated", "过时"),
        "up_to_date": TranslationEntry("up_to_date", "最新", "Up to Date", "最新"),
        
        # 版本相關
        "version": TranslationEntry("version", "版本", "Version", "版本"),
        "current_version": TranslationEntry("current_version", "當前版本", "Current Version", "当前版本"),
        "latest_version": TranslationEntry("latest_version", "最新版本", "Latest Version", "最新版本"),
        "major": TranslationEntry("major", "主版本", "Major", "主版本"),
        "minor": TranslationEntry("minor", "次版本", "Minor", "次版本"),
        "patch": TranslationEntry("patch", "修補版本", "Patch", "修补版本"),
        
        # 漏洞相關
        "vulnerability": TranslationEntry("vulnerability", "漏洞", "Vulnerability", "漏洞"),
        "vulnerabilities": TranslationEntry("vulnerabilities", "漏洞", "Vulnerabilities", "漏洞"),
        "critical": TranslationEntry("critical", "嚴重", "Critical", "严重"),
        "high": TranslationEntry("high", "高", "High", "高"),
        "medium": TranslationEntry("medium", "中", "Medium", "中"),
        "low": TranslationEntry("low", "低", "Low", "低"),
        "severity": TranslationEntry("severity", "嚴重程度", "Severity", "严重程度"),
        "cve": TranslationEntry("cve", "漏洞編號", "CVE", "漏洞编号"),
        "fixed_version": TranslationEntry("fixed_version", "修復版本", "Fixed Version", "修复版本"),
        
        # 許可證相關
        "license": TranslationEntry("license", "許可證", "License", "许可证"),
        "allowed": TranslationEntry("allowed", "允許", "Allowed", "允许"),
        "warning": TranslationEntry("warning", "警告", "Warning", "警告"),
        "blocked": TranslationEntry("blocked", "禁止", "Blocked", "禁止"),
        "compliance": TranslationEntry("compliance", "合規性", "Compliance", "合规性"),
        
        # 更新相關
        "update": TranslationEntry("update", "更新", "Update", "更新"),
        "updates": TranslationEntry("updates", "更新", "Updates", "更新"),
        "auto_update": TranslationEntry("auto_update", "自動更新", "Auto Update", "自动更新"),
        "manual_review": TranslationEntry("manual_review", "人工審查", "Manual Review", "人工审查"),
        "pull_request": TranslationEntry("pull_request", "拉取請求", "Pull Request", "拉取请求"),
        "rollback": TranslationEntry("rollback", "回滾", "Rollback", "回滚"),
        
        # 操作相關
        "analysis": TranslationEntry("analysis", "分析", "Analysis", "分析"),
        "scan": TranslationEntry("scan", "掃描", "Scan", "扫描"),
        "scanning": TranslationEntry("scanning", "掃描中", "Scanning", "扫描中"),
        "completed": TranslationEntry("completed", "完成", "Completed", "完成"),
        "failed": TranslationEntry("failed", "失敗", "Failed", "失败"),
        "success": TranslationEntry("success", "成功", "Success", "成功"),
        "skipped": TranslationEntry("skipped", "跳過", "Skipped", "跳过"),
        
        # 風險相關
        "risk": TranslationEntry("risk", "風險", "Risk", "风险"),
        "risk_level": TranslationEntry("risk_level", "風險等級", "Risk Level", "风险等级"),
        "breaking_change": TranslationEntry("breaking_change", "破壞性變更", "Breaking Change", "破坏性变更"),
        
        # 報告相關
        "report": TranslationEntry("report", "報告", "Report", "报告"),
        "summary": TranslationEntry("summary", "摘要", "Summary", "摘要"),
        "details": TranslationEntry("details", "詳情", "Details", "详情"),
        "total": TranslationEntry("total", "總計", "Total", "总计"),
        
        # 時間相關
        "timestamp": TranslationEntry("timestamp", "時間戳", "Timestamp", "时间戳"),
        "estimated_time": TranslationEntry("estimated_time", "預估時間", "Estimated Time", "预估时间"),
        "hours": TranslationEntry("hours", "小時", "Hours", "小时"),
        "minutes": TranslationEntry("minutes", "分鐘", "Minutes", "分钟"),
        
        # 策略相關
        "policy": TranslationEntry("policy", "策略", "Policy", "策略"),
        "conservative": TranslationEntry("conservative", "保守", "Conservative", "保守"),
        "balanced": TranslationEntry("balanced", "平衡", "Balanced", "平衡"),
        "aggressive": TranslationEntry("aggressive", "積極", "Aggressive", "积极"),
        "security_first": TranslationEntry("security_first", "安全優先", "Security First", "安全优先"),
        
        # 生態系統
        "ecosystem": TranslationEntry("ecosystem", "生態系統", "Ecosystem", "生态系统"),
        "npm": TranslationEntry("npm", "NPM", "NPM", "NPM"),
        "pip": TranslationEntry("pip", "pip", "pip", "pip"),
        "go": TranslationEntry("go", "Go", "Go", "Go"),
        "maven": TranslationEntry("maven", "Maven", "Maven", "Maven"),
        "cargo": TranslationEntry("cargo", "Cargo", "Cargo", "Cargo"),
    }
    
    # 消息模板
    MESSAGES = {
        "analysis_started": TranslationEntry(
            "analysis_started",
            "開始分析 {project} 的依賴項",
            "Starting analysis of dependencies for {project}",
            "开始分析 {project} 的依赖项"
        ),
        "analysis_completed": TranslationEntry(
            "analysis_completed",
            "分析完成：共 {total} 個依賴項，{outdated} 個過時，{vulnerable} 個有漏洞",
            "Analysis completed: {total} dependencies, {outdated} outdated, {vulnerable} vulnerable",
            "分析完成：共 {total} 个依赖项，{outdated} 个过时，{vulnerable} 个有漏洞"
        ),
        "vulnerability_found": TranslationEntry(
            "vulnerability_found",
            "發現漏洞：{package} ({severity})",
            "Vulnerability found: {package} ({severity})",
            "发现漏洞：{package} ({severity})"
        ),
        "update_started": TranslationEntry(
            "update_started",
            "開始更新 {package}: {from_ver} → {to_ver}",
            "Starting update for {package}: {from_ver} → {to_ver}",
            "开始更新 {package}: {from_ver} → {to_ver}"
        ),
        "update_completed": TranslationEntry(
            "update_completed",
            "更新完成：{package} 已更新至 {version}",
            "Update completed: {package} updated to {version}",
            "更新完成：{package} 已更新至 {version}"
        ),
        "update_failed": TranslationEntry(
            "update_failed",
            "更新失敗：{package} - {error}",
            "Update failed: {package} - {error}",
            "更新失败：{package} - {error}"
        ),
        "license_violation": TranslationEntry(
            "license_violation",
            "許可證違規：{package} 使用 {license}",
            "License violation: {package} uses {license}",
            "许可证违规：{package} 使用 {license}"
        ),
        "scan_completed": TranslationEntry(
            "scan_completed",
            "掃描完成：發現 {count} 個問題",
            "Scan completed: {count} issues found",
            "扫描完成：发现 {count} 个问题"
        ),
        "recommendation": TranslationEntry(
            "recommendation",
            "建議使用「{scenario}」策略",
            "Recommended strategy: {scenario}",
            "建议使用「{scenario}」策略"
        ),
    }


class LanguageBoundary:
    """
    語言邊界控制器
    
    確保所有輸出維持指定語言的一致性
    """
    
    def __init__(self, default_lang: OutputLanguage = OutputLanguage.ZH_TW):
        """
        初始化語言邊界控制器
        
        Args:
            default_lang: 預設輸出語言
        """
        self.default_lang = default_lang
        self._custom_terms: Dict[str, TranslationEntry] = {}
        
        logger.info(f"語言邊界控制器初始化: {default_lang.value}")
    
    def t(self, key: str, lang: Optional[OutputLanguage] = None) -> str:
        """
        翻譯術語
        
        Args:
            key: 術語鍵值
            lang: 目標語言（可選，預設使用 default_lang）
            
        Returns:
            翻譯後的文字
        """
        target_lang = lang or self.default_lang
        
        # 優先查找自定義術語
        if key in self._custom_terms:
            return self._custom_terms[key].get(target_lang)
        
        # 查找內建術語
        if key in LanguageRegistry.TERMS:
            return LanguageRegistry.TERMS[key].get(target_lang)
        
        # 未找到時返回原始鍵值
        logger.warning(f"未找到翻譯: {key}")
        return key
    
    def msg(
        self, 
        key: str, 
        lang: Optional[OutputLanguage] = None,
        **kwargs
    ) -> str:
        """
        獲取格式化消息
        
        Args:
            key: 消息鍵值
            lang: 目標語言
            **kwargs: 格式化參數
            
        Returns:
            格式化後的消息
        """
        target_lang = lang or self.default_lang
        
        if key in LanguageRegistry.MESSAGES:
            template = LanguageRegistry.MESSAGES[key].get(target_lang)
            try:
                return template.format(**kwargs)
            except KeyError as e:
                logger.warning(f"消息格式化失敗: {key} - {e}")
                return template
        
        return key
    
    def add_term(self, key: str, zh_tw: str, en: str = "", zh_cn: str = "") -> None:
        """
        添加自定義術語
        
        Args:
            key: 術語鍵值
            zh_tw: 繁體中文
            en: 英文
            zh_cn: 簡體中文
        """
        self._custom_terms[key] = TranslationEntry(key, zh_tw, en, zh_cn)
        logger.debug(f"已添加自定義術語: {key}")
    
    def set_language(self, lang: OutputLanguage) -> None:
        """
        設置預設語言
        
        Args:
            lang: 目標語言
        """
        self.default_lang = lang
        logger.info(f"已切換預設語言: {lang.value}")
    
    def format_severity(self, severity: str) -> str:
        """
        格式化嚴重程度
        
        Args:
            severity: 嚴重程度（英文）
            
        Returns:
            本地化的嚴重程度
        """
        severity_map = {
            "CRITICAL": self.t("critical"),
            "HIGH": self.t("high"),
            "MEDIUM": self.t("medium"),
            "LOW": self.t("low"),
        }
        return severity_map.get(severity.upper(), severity)
    
    def format_update_type(self, update_type: str) -> str:
        """
        格式化更新類型
        
        Args:
            update_type: 更新類型（英文）
            
        Returns:
            本地化的更新類型
        """
        type_map = {
            "MAJOR": self.t("major"),
            "MINOR": self.t("minor"),
            "PATCH": self.t("patch"),
        }
        return type_map.get(update_type.upper(), update_type)
    
    def format_policy(self, policy: str) -> str:
        """
        格式化策略
        
        Args:
            policy: 策略名稱（英文）
            
        Returns:
            本地化的策略名稱
        """
        policy_map = {
            "auto": self.t("auto_update"),
            "pr": self.t("pull_request"),
            "manual": self.t("manual_review"),
            "skip": self.t("skipped"),
        }
        return policy_map.get(policy.lower(), policy)
    
    def format_ecosystem(self, ecosystem: str) -> str:
        """
        格式化生態系統名稱
        
        Args:
            ecosystem: 生態系統（英文）
            
        Returns:
            本地化的名稱（生態系統名稱通常保持原樣）
        """
        return self.t(ecosystem.lower())
    
    def localize_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        本地化報告
        
        將報告中的英文鍵值轉換為本地化文字
        
        Args:
            report: 原始報告字典
            
        Returns:
            本地化後的報告
        """
        def localize_dict(d: Dict) -> Dict:
            result = {}
            for key, value in d.items():
                # 嘗試翻譯鍵值
                local_key = self.t(key)
                
                if isinstance(value, dict):
                    result[local_key] = localize_dict(value)
                elif isinstance(value, list):
                    result[local_key] = [
                        localize_dict(item) if isinstance(item, dict) else item
                        for item in value
                    ]
                else:
                    result[local_key] = value
            
            return result
        
        return localize_dict(report)
    
    def get_all_terms(self) -> Dict[str, str]:
        """
        獲取所有術語的當前語言翻譯
        
        Returns:
            術語字典
        """
        terms = {}
        for key, entry in LanguageRegistry.TERMS.items():
            terms[key] = entry.get(self.default_lang)
        for key, entry in self._custom_terms.items():
            terms[key] = entry.get(self.default_lang)
        return terms


# 全域語言邊界實例
_language_boundary: Optional[LanguageBoundary] = None


def get_language_boundary() -> LanguageBoundary:
    """
    獲取全域語言邊界實例
    
    Returns:
        語言邊界控制器
    """
    global _language_boundary
    if _language_boundary is None:
        _language_boundary = LanguageBoundary()
    return _language_boundary


def t(key: str) -> str:
    """
    快捷翻譯函數
    
    Args:
        key: 術語鍵值
        
    Returns:
        翻譯後的文字
    """
    return get_language_boundary().t(key)


def msg(key: str, **kwargs) -> str:
    """
    快捷消息函數
    
    Args:
        key: 消息鍵值
        **kwargs: 格式化參數
        
    Returns:
        格式化後的消息
    """
    return get_language_boundary().msg(key, **kwargs)
