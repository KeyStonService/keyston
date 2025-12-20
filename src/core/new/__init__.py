"""
MachineNativeOps Core Integration
核心集成模組 - 統一所有組件
"""

from .runtime.engine import engine as runtime_engine
from .governance.policy_engine import governance_engine
from .security.auth import security_manager
from .automation.workflow_engine import automation_engine
import logging

logger = logging.getLogger(__name__)

class MachineNativeOpsCore:
    """MachineNativeOps 核心類"""
    
    def __init__(self):
        self.runtime = runtime_engine
        self.governance = governance_engine
        self.security = security_manager
        self.automation = automation_engine
        self.is_initialized = False
    
    async def initialize(self):
        """初始化所有核心組件"""
        if self.is_initialized:
            return
        
        logger.info("🚀 初始化 MachineNativeOps 核心...")
        
        await self.runtime.start()
        await self.governance.initialize()
        await self.security.initialize()
        await self.automation.initialize()
        
        self.is_initialized = True
        logger.info("✅ MachineNativeOps 核心初始化完成")
    
    async def shutdown(self):
        """關閉所有核心組件"""
        logger.info("🛑 關閉 MachineNativeOps 核心...")
        
        await self.runtime.stop()
        
        logger.info("✅ MachineNativeOps 核心已關閉")
    
    async def submit_task(self, name: str, handler, parameters: dict = None):
        """提交任務到運行時"""
        return await self.runtime.submit_task(name, handler, parameters)
    
    async def authenticate(self, username: str, password: str):
        """用戶認證"""
        return await self.security.authenticate_user(username, password)
    
    async def create_workflow(self, name: str, description: str, tasks: list):
        """創建工作流"""
        return await self.automation.create_workflow(name, description, tasks)

# 全局核心實例
core = MachineNativeOpsCore()