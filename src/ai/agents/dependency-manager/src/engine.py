"""
依賴管理引擎 - Dependency Manager Engine
整合所有功能的主引擎類
"""

import logging
import yaml
import uuid
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field

from .models.dependency import DependencyAnalysis, Ecosystem
from .models.vulnerability import VulnerabilityScanResult
from .models.update import UpdateResult
from .analyzers import NpmAnalyzer, PipAnalyzer, GoAnalyzer, BaseAnalyzer
from .scanners import VulnerabilityScanner, LicenseScanner
from .scanners.vulnerability_scanner import ScanConfig
from .scanners.license_scanner import LicensePolicy, LicenseScanResult
from .updaters import AutoUpdater
from .updaters.auto_updater import UpdateConfig
from .utils import DependencyTree, AuditLogger, AuditEventType

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ManagerConfig:
    """
    管理器配置
    
    Attributes:
        enabled: 是否啟用
        parallel: 是否並行處理
        max_workers: 最大工作線程數
        ecosystems: 啟用的生態系統
    """
    enabled: bool = True
    parallel: bool = True
    max_workers: int = 8
    ecosystems: List[Ecosystem] = field(default_factory=lambda: [
        Ecosystem.NPM,
        Ecosystem.PIP,
        Ecosystem.GO
    ])


class DependencyManager:
    """
    依賴管理器主類
    
    整合依賴分析、漏洞掃描、許可證檢查和自動更新功能。
    
    使用方式:
        manager = DependencyManager(config_path="config/manager.yaml")
        analysis = await manager.analyze_project("path/to/project")
        vulnerabilities = await manager.scan_vulnerabilities(analysis)
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化依賴管理器
        
        Args:
            config_path: 配置文件路徑
        """
        self.config = self._load_config(config_path)
        
        # 初始化各個組件
        self._analyzers: Dict[Ecosystem, BaseAnalyzer] = {}
        self._init_analyzers()
        
        self._vulnerability_scanner = VulnerabilityScanner()
        self._license_scanner = LicenseScanner()
        self._auto_updater = AutoUpdater()
        
        logger.info("依賴管理器初始化完成")
    
    def _load_config(self, config_path: Optional[str]) -> ManagerConfig:
        """
        載入配置
        
        Args:
            config_path: 配置文件路徑
            
        Returns:
            管理器配置
        """
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    yaml_config = yaml.safe_load(f)
                
                return ManagerConfig(
                    enabled=yaml_config.get('enabled', True),
                    parallel=yaml_config.get('parallel', True),
                    max_workers=yaml_config.get('max_workers', 8),
                    ecosystems=[
                        Ecosystem(e) for e in yaml_config.get('ecosystems', ['npm'])
                    ]
                )
            except Exception as e:
                logger.warning(f"載入配置失敗: {e}，使用默認配置")
        
        return ManagerConfig()
    
    def _init_analyzers(self) -> None:
        """初始化各生態系統的分析器"""
        if Ecosystem.NPM in self.config.ecosystems:
            self._analyzers[Ecosystem.NPM] = NpmAnalyzer()
        
        if Ecosystem.PIP in self.config.ecosystems:
            self._analyzers[Ecosystem.PIP] = PipAnalyzer()
        
        if Ecosystem.GO in self.config.ecosystems:
            self._analyzers[Ecosystem.GO] = GoAnalyzer()
        
        logger.info(f"已初始化 {len(self._analyzers)} 個分析器")
    
    async def analyze_project(
        self, 
        project_path: str,
        scan_type: str = "full"
    ) -> Dict[Ecosystem, DependencyAnalysis]:
        """
        分析專案依賴
        
        Args:
            project_path: 專案路徑
            scan_type: 掃描類型 ("full" 或 "quick")
            
        Returns:
            各生態系統的依賴分析結果
        """
        path = Path(project_path)
        if not path.exists():
            raise FileNotFoundError(f"專案路徑不存在: {project_path}")
        
        logger.info(f"開始分析專案: {project_path}")
        
        results: Dict[Ecosystem, DependencyAnalysis] = {}
        analysis_id = f"analysis-{uuid.uuid4().hex[:8]}"
        
        for ecosystem, analyzer in self._analyzers.items():
            analysis = await analyzer.analyze(path, analysis_id)
            if analysis:
                results[ecosystem] = analysis
        
        if not results:
            logger.warning("未找到任何支援的依賴清單文件")
        
        return results
    
    async def scan_vulnerabilities(
        self, 
        analysis: DependencyAnalysis
    ) -> VulnerabilityScanResult:
        """
        掃描漏洞
        
        Args:
            analysis: 依賴分析結果
            
        Returns:
            漏洞掃描結果
        """
        logger.info(f"開始漏洞掃描: {analysis.analysis_id}")
        return await self._vulnerability_scanner.scan(analysis.dependencies)
    
    async def scan_licenses(
        self, 
        analysis: DependencyAnalysis
    ) -> LicenseScanResult:
        """
        掃描許可證
        
        Args:
            analysis: 依賴分析結果
            
        Returns:
            許可證掃描結果
        """
        logger.info(f"開始許可證掃描: {analysis.analysis_id}")
        return await self._license_scanner.scan(analysis.dependencies)
    
    async def update_dependencies(
        self,
        analysis: DependencyAnalysis,
        security_only: bool = False
    ) -> UpdateResult:
        """
        更新依賴項
        
        Args:
            analysis: 依賴分析結果
            security_only: 是否僅更新安全修復
            
        Returns:
            更新結果
        """
        logger.info(f"開始更新依賴: {analysis.analysis_id}")
        
        # 獲取需要安全修復的套件
        security_fixes = [
            d.name for d in analysis.dependencies 
            if d.has_vulnerability
        ]
        
        if security_only:
            # 僅更新有安全漏洞的依賴
            deps_to_update = analysis.get_vulnerable_dependencies()
        else:
            # 更新所有過時的依賴
            deps_to_update = analysis.get_outdated_dependencies()
        
        return await self._auto_updater.update(deps_to_update, security_fixes)
    
    async def full_scan(
        self, 
        project_path: str
    ) -> Dict[str, Any]:
        """
        執行完整掃描
        
        包括依賴分析、漏洞掃描和許可證檢查
        
        Args:
            project_path: 專案路徑
            
        Returns:
            完整掃描結果
        """
        logger.info(f"開始完整掃描: {project_path}")
        
        result = {
            "project": project_path,
            "analyses": {},
            "vulnerabilities": {},
            "licenses": {}
        }
        
        # 分析各生態系統
        analyses = await self.analyze_project(project_path)
        
        for ecosystem, analysis in analyses.items():
            eco_name = ecosystem.value
            
            # 儲存分析結果
            result["analyses"][eco_name] = analysis.to_dict()
            
            # 漏洞掃描
            vuln_result = await self.scan_vulnerabilities(analysis)
            result["vulnerabilities"][eco_name] = vuln_result.to_dict()
            
            # 許可證掃描
            license_result = await self.scan_licenses(analysis)
            result["licenses"][eco_name] = license_result.to_dict()
        
        logger.info("完整掃描完成")
        return result
    
    def get_summary(self, scan_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        獲取掃描摘要
        
        Args:
            scan_result: 完整掃描結果
            
        Returns:
            摘要資訊
        """
        summary = {
            "total_dependencies": 0,
            "outdated_dependencies": 0,
            "vulnerable_dependencies": 0,
            "license_issues": 0,
            "ecosystems": []
        }
        
        for eco_name, analysis in scan_result.get("analyses", {}).items():
            summary["ecosystems"].append(eco_name)
            
            if "summary" in analysis:
                summary["total_dependencies"] += analysis["summary"].get("total_dependencies", 0)
                summary["outdated_dependencies"] += analysis["summary"].get("outdated", 0)
                summary["vulnerable_dependencies"] += analysis["summary"].get("vulnerable", 0)
        
        for eco_name, licenses in scan_result.get("licenses", {}).items():
            if "summary" in licenses:
                summary["license_issues"] += licenses["summary"].get("blocked", 0)
        
        return summary


# 命令行入口
async def main():
    """命令行入口函數"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(
        description="依賴管理代理 - SynergyMesh"
    )
    parser.add_argument(
        "--project", "-p",
        required=True,
        help="專案路徑"
    )
    parser.add_argument(
        "--scan-type",
        choices=["full", "quick"],
        default="full",
        help="掃描類型"
    )
    parser.add_argument(
        "--output", "-o",
        help="輸出文件路徑"
    )
    parser.add_argument(
        "--config", "-c",
        help="配置文件路徑"
    )
    
    args = parser.parse_args()
    
    # 初始化管理器
    manager = DependencyManager(config_path=args.config)
    
    # 執行完整掃描
    result = await manager.full_scan(args.project)
    
    # 輸出結果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"結果已保存至: {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 輸出摘要
    summary = manager.get_summary(result)
    print("\n=== 掃描摘要 ===")
    print(f"總依賴數: {summary['total_dependencies']}")
    print(f"過時依賴: {summary['outdated_dependencies']}")
    print(f"有漏洞依賴: {summary['vulnerable_dependencies']}")
    print(f"許可證問題: {summary['license_issues']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
