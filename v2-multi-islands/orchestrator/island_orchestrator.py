#!/usr/bin/env python3
"""
MachineNativeOps 島嶼協調器 (Island Orchestrator)

負責協調所有無人島的運作，管理島嶼間的通信和資源分配。
對應 .devcontainer/automation/drone-coordinator.py
"""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import sys
_current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(_current_dir.parent))

from utils import Colors, print_info, print_success, print_warn, print_error

# Governance integration
try:
    from governance_integration import GovernanceIntegration
    GOVERNANCE_AVAILABLE = True
except ImportError:
    GOVERNANCE_AVAILABLE = False
    print_warn("Governance integration not available")


class IslandStatus:
    """島嶼狀態"""
    DORMANT = "dormant"       # 休眠
    ACTIVATING = "activating"  # 啟動中
    ACTIVE = "active"         # 活躍
    SUSPENDED = "suspended"   # 暫停
    ERROR = "error"          # 錯誤


class IslandOrchestrator:
    """
    島嶼協調器
    
    作為無人島群的主控制器，負責：
    - 島嶼生命週期管理
    - 跨島嶼通信協調
    - 資源分配與負載均衡
    - 健康監控與故障恢復
    """
    
    def __init__(self) -> None:
        self.status = IslandStatus.DORMANT
        self.start_time: Optional[datetime] = None
        self.islands: dict[str, Any] = {}
        self.active_bridges: list[str] = []
        self._project_root = self._find_project_root()
        self.config: dict[str, Any] = {}
        
        # Governance integration
        self.governance: Optional[Any] = None
        if GOVERNANCE_AVAILABLE:
            try:
                self.governance = GovernanceIntegration("unmanned-island-agent")
                print_success("✅ Governance integration enabled")
            except Exception as e:
                print_warn(f"Governance integration failed: {e}")
    
    def _find_project_root(self) -> Path:
        """尋找專案根目錄"""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            if (current / 'island-control.yml').exists():
                return current
            if (current / 'drone-config.yml').exists():
                return current
            if (current / 'package.json').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    @property
    def project_root(self) -> Path:
        """取得專案根目錄"""
        return self._project_root
    
    def load_config(self) -> bool:
        """載入配置"""
        try:
            from config import IslandConfig
            island_config = IslandConfig.load()
            self.config = {
                'islands': island_config.islands,
                'orchestrator': island_config.orchestrator,
                'bridges': island_config.bridges,
            }
            print_success("配置已載入")
            return True
        except Exception as e:
            print_error(f"載入配置失敗: {e}")
            return False
    
    def start(self) -> bool:
        """啟動協調器"""
        print_info("🏝️ 啟動島嶼協調器...")
        
        self.load_config()
        
        self.status = IslandStatus.ACTIVATING
        self.start_time = datetime.now()
        
        # Governance: Validate compliance
        if self.governance:
            compliance_result = self.governance.validate_governance_compliance()
            if compliance_result["overall_status"] != "compliant":
                print_warn(f"⚠️ Governance compliance: {compliance_result['compliance_score']:.1f}%")
            else:
                print_success(f"✅ Governance compliance: {compliance_result['compliance_score']:.1f}%")
        
        # 初始化島嶼
        self._initialize_islands()
        
        # Governance: Health check
        if self.governance:
            health_result = self.governance.perform_health_check()
            print_info(f"🏥 Health status: {health_result['health_status']}")
            
            # Log audit event
            self.governance.log_audit_event("orchestrator_started", {
                "timestamp": datetime.now().isoformat(),
                "islands_count": len(self.islands)
            })
        
        self.status = IslandStatus.ACTIVE
        print_success("島嶼協調器已啟動")
        return True
    
    def stop(self) -> bool:
        """停止協調器"""
        print_info("停止島嶼協調器...")
        
        # 停止所有島嶼
        for island_id in list(self.islands.keys()):
            self._deactivate_island(island_id)
        
        self.status = IslandStatus.DORMANT
        print_success("島嶼協調器已停止")
        return True
    
    def _initialize_islands(self) -> None:
        """初始化所有島嶼"""
        print_info("🌊 初始化無人島群...")
        
        island_configs = self.config.get('islands', {})
        
        for island_id, island_config in island_configs.items():
            if island_config.get('enabled', True):
                self.islands[island_id] = {
                    'name': island_config.get('name', island_id),
                    'status': IslandStatus.DORMANT,
                    'priority': island_config.get('priority', 99),
                    'capabilities': island_config.get('capabilities', []),
                    'activated_at': None,
                }
                print_info(f"  🏝️ {island_config.get('name', island_id)}")
        
        print_success(f"已初始化 {len(self.islands)} 個島嶼")
    
    def activate_island(self, island_id: str) -> bool:
        """啟動指定島嶼"""
        if island_id not in self.islands:
            print_error(f"島嶼 {island_id} 不存在")
            return False
        
        island = self.islands[island_id]
        print_info(f"🏝️ 啟動島嶼: {island['name']}")
        
        island['status'] = IslandStatus.ACTIVATING
        island['activated_at'] = datetime.now()
        island['status'] = IslandStatus.ACTIVE
        
        print_success(f"島嶼 {island['name']} 已啟動")
        return True
    
    def _deactivate_island(self, island_id: str) -> bool:
        """停止指定島嶼"""
        if island_id not in self.islands:
            return False
        
        island = self.islands[island_id]
        island['status'] = IslandStatus.DORMANT
        island['activated_at'] = None
        return True
    
    def analyze_archipelago(self) -> dict[str, Any]:
        """
        分析整個島嶼群的狀態
        
        Returns:
            分析結果
        """
        print_info("🔍 分析島嶼群狀態...")
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'orchestrator_status': self.status,
            'total_islands': len(self.islands),
            'active_islands': 0,
            'islands': {},
            'tools': {},
            'recommendations': [],
        }
        
        # 統計島嶼狀態
        for island_id, island in self.islands.items():
            analysis['islands'][island_id] = {
                'name': island['name'],
                'status': island['status'],
                'capabilities': island['capabilities'],
            }
            if island['status'] == IslandStatus.ACTIVE:
                analysis['active_islands'] += 1
        
        # 檢查各語言工具
        language_tools = {
            'rust': ('rustc', '--version'),
            'go': ('go', 'version'),
            'typescript': ('tsc', '--version'),
            'python': ('python3', '--version'),
            'java': ('java', '--version'),
            'node': ('node', '--version'),
            'docker': ('docker', '--version'),
        }
        
        for lang, (cmd, arg) in language_tools.items():
            try:
                result = subprocess.run(
                    [cmd, arg],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                analysis['tools'][lang] = {
                    'installed': result.returncode == 0,
                    'version': result.stdout.strip().split('\n')[0] if result.returncode == 0 else None
                }
            except (FileNotFoundError, subprocess.TimeoutExpired):
                analysis['tools'][lang] = {'installed': False, 'version': None}
        
        # 生成建議
        if not analysis['tools'].get('docker', {}).get('installed'):
            analysis['recommendations'].append("建議安裝 Docker 以支援容器化部署")
        
        if not analysis['tools'].get('rust', {}).get('installed'):
            analysis['recommendations'].append("安裝 Rust 以啟用性能核心島")
        
        if not analysis['tools'].get('go', {}).get('installed'):
            analysis['recommendations'].append("安裝 Go 以啟用雲原生服務島")
        
        # 顯示分析結果
        self._display_analysis(analysis)
        
        return analysis
    
    def _display_analysis(self, analysis: dict[str, Any]) -> None:
        """顯示分析結果"""
        print_info("📊 島嶼群分析報告:")
        
        print("\n  🏝️ 島嶼狀態:")
        for island_id, island_info in analysis['islands'].items():
            status_icon = '🟢' if island_info['status'] == IslandStatus.ACTIVE else '⚪'
            print(f"    {status_icon} {island_info['name']}")
            print(f"       能力: {', '.join(island_info['capabilities'][:3])}...")
        
        print("\n  🔧 語言工具檢查:")
        for tool, info in analysis['tools'].items():
            status = '✅' if info.get('installed') else '❌'
            version = info.get('version', '未安裝')
            if version and len(version) > 50:
                version = version[:50] + '...'
            print(f"    {status} {tool}: {version}")
        
        if analysis['recommendations']:
            print("\n  💡 建議:")
            for rec in analysis['recommendations']:
                print(f"    • {rec}")
        
        print()
    
    def execute(self) -> dict[str, Any]:
        """執行協調任務"""
        return self.analyze_archipelago()
    
    def get_status(self) -> dict[str, Any]:
        """取得協調器狀態"""
        status_dict = {
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'total_islands': len(self.islands),
            'active_islands': sum(
                1 for i in self.islands.values() 
                if i['status'] == IslandStatus.ACTIVE
            ),
        }
        
        # Add governance info if available
        if self.governance:
            status_dict['governance'] = self.governance.get_agent_info()
        
        return status_dict
